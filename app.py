from flask import Flask, render_template, redirect, url_for, flash,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from forms import RegisterForm, LoginForm,ApplyOutpassForm,EditProfileForm
from werkzeug.utils import secure_filename
from zoneinfo import ZoneInfo

from models import db, User,Outpass
import os
from datetime import datetime


# -------------------- Flask App Setup --------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///outpass.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# -------------------- Extensions --------------------
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# -------------------- Predefined Admin Roles --------------------
predefined = {
    "admin@gmail.com": {"password": "admin", "role": "admin"},
    "warden1@hostel.com": {"password": "warden@123", "role": "warden"},
    "caretaker1@hostel.com": {"password": "caretaker@123", "role": "caretaker"},
    "security1@hostel.com": {"password": "security@123", "role": "security"},
}

# -------------------- User Loader --------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------- Routes --------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(email=email).first():
            flash("Email already registered", "warning")
            return redirect(url_for("register"))

        new_user = User(name=name, email=email, role="student")
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # ✅ Predefined user login
        if email in predefined and password == predefined[email]["password"]:
            user = User.query.filter_by(email=email).first()

            # 🔹 If user doesn't exist in DB, create them
            if not user:
                user = User(name=email.split('@')[0], email=email, role=predefined[email]["role"])
                user.set_password(password)  # Save hashed password to match schema
                db.session.add(user)
                db.session.commit()

            login_user(user)  # ✅ Login is required
            flash("Login successful!", "success")
            return redirect(url_for(f"{user.role}_dashboard"))

        # ✅ Student login
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("student_dashboard"))

        flash("Invalid login credentials", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("home"))

# -------------------- Dashboards (Role-Based Access) --------------------

@app.route("/student/dashboard")
@login_required
def student_dashboard():
    if current_user.role != "student":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    edit_form = EditProfileForm(obj=current_user)
    apply_form = ApplyOutpassForm()
    outpasses = Outpass.query.filter_by(student_id=current_user.id).order_by(Outpass.submitted_at.desc()).all()

    return render_template("student/dashboard.html",user=current_user,edit_form=edit_form,outpass_form=apply_form,outpasses=outpasses)

@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    from forms import EditProfileForm

    form = EditProfileForm(obj=current_user)  # pre-fill with current data

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.gender = form.gender.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.sidno = form.sidno.data
        current_user.branch = form.branch.data
        current_user.batch = form.batch.data
        current_user.p_email = form.p_email.data
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("student/edit_profile.html", form=form)

@app.route("/apply-outpass", methods=["GET", "POST"])
@login_required
def apply_outpass():
    if current_user.role != "student":
        flash("Unauthorized", "danger")
        return redirect(url_for("login"))

    form = ApplyOutpassForm()
    if form.validate_on_submit():

        # Conditionally set warden_approval
        warden_status = "Pending" if form.warden_required.data else "Not Requested"

        # Create Outpass object
        outpass = Outpass(
            student_id=current_user.id,
            reason=form.reason.data,
            from_date=form.from_date.data,
            to_date=form.to_date.data,
            warden_required=form.warden_required.data,
            warden_approval=warden_status
        )

        db.session.add(outpass)
        db.session.commit()
        flash("Outpass application submitted!", "success")
        return redirect(url_for("student_dashboard"))

    return render_template("student/apply_outpass.html", form=form)






@app.route('/caretaker/dashboard')
@login_required
def caretaker_dashboard():
    if not current_user.is_authenticated or current_user.role != 'caretaker':
        flash("Unauthorized", "danger")
        return redirect(url_for('login'))

    pending = Outpass.query.filter_by(status='Pending').all()
    history = Outpass.query.order_by(Outpass.submitted_at.desc()).all()
    return render_template("caretaker/dashboard.html",
                           user=current_user,
                           pending_outpasses=pending,
                           all_outpasses=history)
@app.route('/update-outpass/<int:outpass_id>/<action>')
@login_required
def update_outpass_status(outpass_id, action):
    if current_user.role not in ['caretaker', 'warden']:
        flash("Unauthorized", "danger")
        return redirect(url_for('login'))

    outpass = Outpass.query.get_or_404(outpass_id)

    if action == 'approve':
        outpass.status = "Approved"
        flash("Outpass approved!", "success")
    elif action == 'reject':
        outpass.status = "Rejected"
        flash("Outpass rejected.", "warning")
    else:
        flash("Invalid action!", "danger")
        return redirect(url_for('login'))

    db.session.commit()

    # Redirect based on role
    if current_user.role == 'caretaker':
        return redirect(url_for('caretaker_dashboard'))
    else:
        return redirect(url_for('warden_dashboard'))

@app.route("/warden/dashboard")
@login_required
def warden_dashboard():
    if current_user.role != 'warden':
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    pending_outpasses = Outpass.query.filter_by(warden_required=True, warden_status=None).all()
    all_outpasses = Outpass.query.filter_by(warden_required=True).all()

    return render_template("warden/dashboard.html", 
        pending_outpasses=pending_outpasses,
        all_outpasses=all_outpasses
    )


@app.route('/warden/approve/<int:id>', methods=['POST'])
@login_required
def warden_approve(id):
    if current_user.role != 'warden':
        flash("Unauthorized", "danger")
        return redirect(url_for("login"))

    action = request.form.get('action')  # ✅ get from form

    outpass = Outpass.query.get_or_404(id)

    if action == "approve":
        outpass.warden_status = "approved"
        outpass.warden_approval = "Approved"
        flash("Outpass approved successfully.", "success")
    elif action == "reject":
        outpass.warden_status = "rejected"
        outpass.warden_approval = "Rejected"
        flash("Outpass rejected.", "danger")
    else:
        flash("Invalid action.", "warning")

    db.session.commit()
    return redirect(url_for('warden_dashboard'))


@app.route('/security/dashboard')
@login_required
def security_dashboard():
    if current_user.role != 'security':
        flash("Unauthorized access!", "danger")
        return redirect(url_for('login'))

    # Fetch approved outpasses pending exit
    pending_exit_outpasses = Outpass.query.filter(Outpass.status == 'Approved',Outpass.security_exit != 'Exited').all()


    # Fetch outpasses already exited
    exited_outpasses = Outpass.query.filter_by(security_exit='Exited').all()

    return render_template('security/dashboard.html',
                           pending_exit_outpasses=pending_exit_outpasses,
                           exited_outpasses=exited_outpasses)


@app.route('/mark-exit/<int:id>', methods=['POST'])
@login_required
def mark_exit(id):
    outpass = Outpass.query.get_or_404(id)
    outpass.security_exit = 'Exited'
    outpass.exited_at = datetime.now(ZoneInfo("Asia/Kolkata"))
    db.session.commit()
    flash('Exit marked successfully.', 'success')
    return redirect(url_for('security_dashboard'))


from collections import defaultdict
from datetime import timedelta

@app.route("/admin/dashboard", methods=["GET"])
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    total_users = User.query.count()
    total_outpasses = Outpass.query.count()
    all_users = User.query.all()
    all_outpasses = Outpass.query.order_by(Outpass.submitted_at.desc()).all()

    # Count roles
    role_counts = defaultdict(int)
    for user in all_users:
        role_counts[user.role] += 1

    # Chart data: last 7 days
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    last_week = today - timedelta(days=6)
    date_counts = defaultdict(int)

    for outpass in Outpass.query.filter(Outpass.submitted_at >= last_week).all():
        date_str = outpass.submitted_at.date().isoformat()
        date_counts[date_str] += 1

    # Fill missing dates with 0
    for i in range(7):
        day = (last_week + timedelta(days=i)).isoformat()
        if day not in date_counts:
            date_counts[day] = 0

    # Sort by date
    date_counts = dict(sorted(date_counts.items()))

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_outpasses=total_outpasses,
        all_users=all_users,
        all_outpasses=all_outpasses,
        role_counts=role_counts,
        date_counts=date_counts
    )

@app.route("/admin/create-user", methods=["POST"])
@login_required
def admin_create_user():
    if current_user.role != "admin":
        flash("Unauthorized access", "danger")
        return redirect(url_for("login"))

    name = request.form.get("name")
    email = request.form.get("email")
    role = request.form.get("role")

    if not all([name, email, role]):
        flash("Please fill all fields", "warning")
        return redirect(url_for("admin_dashboard"))

    if User.query.filter_by(email=email).first():
        flash("User with this email already exists", "warning")
        return redirect(url_for("admin_dashboard"))

    password = f"{role}@123"
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f"{role.capitalize()} created successfully with default password: {password}", "success")
    return redirect(url_for("admin_dashboard"))


# -------------------- Main Entry --------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
