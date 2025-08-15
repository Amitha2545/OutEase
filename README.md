# 📝 Outpass Management System

A web-based Outpass Management System built with **Flask** that streamlines the process of applying for and approving student outpasses within a campus. It supports role-based authentication and dashboards for Students, Caretakers, Wardens, Security, and Admins.

---

## 🚀 Features

- 🔒 Secure registration and login for students
- 🎯 Role-based dashboards:
  - **Student**: Apply outpass, view status/history, profile edit
  - **Caretaker**: View pending outpasses, approve/reject
  - **Warden**: Approve/reject caretaker-approved outpasses
  - **Security**: Mark student exits
  - **Admin**: View all users, manage accounts
- ⏰ Indian Standard Time (IST)-based timestamps
- 🗂️ Clean UI using Bootstrap + Jinja templates

---

## 🛠️ Tech Stack

- **Backend**: Flask, Flask-Login, Flask-Migrate, SQLAlchemy
- **Frontend**: HTML5, CSS3, Bootstrap
- **Database**: SQLite
- **Deployment**: Render (or any platform supporting Flask apps)

---


## 📦 Installation

1. **Clone the repo:**

```bash
git clone https://github.com/your-username/outpass-management-system.git
cd outpass-management-system
```

2. **Create virtual environment:**

```bash
python3 -m venv outpass_env
source outpass_env/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Setup database:**

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. **Run the app:**

```bash
flask run
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 🔒 Default Credentials

| Role       | Email               | Password     |
|------------|---------------------|--------------|
| Admin      | admin@gmail.com     | admin        |
| Warden     | [predefined list]   | warden@123   |
| Security   | security@email.com  | security@123 |
| Student    | Self register       | -            |

---

## 🌐 Deployment

1. Push to GitHub
2. Use [Render](https://render.com) to deploy:
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn app:app`

---



## 🙋‍♀️ Author

**Amitha Gollapudi**  
Email: [amithagollapudi@gmail.com]  
Project for: RGUKT Ongole 💻
