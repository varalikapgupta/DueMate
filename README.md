# DueMate – Student Assignment Deadline Tracker

**Stay organized. Never miss a deadline.**

DueMate is a web-based assignment management system developed using Python Flask and MySQL. It helps students organize academic tasks, track deadlines and monitor assignment progress.

## Features

- Student registration and login
- Secure password hashing
- Add, update and delete assignments
- Subject-wise assignment organization
- Dashboard with assignment statistics
- Search assignments by title
- Filter by subject and status
- Deadline alerts for:
  - Due in 2 days
  - Due tomorrow
  - Due today
  - Overdue assignments
- Sort by earliest deadline, latest deadline and title

## Technology Stack

| Technology | Usage |
|---|---|
| Python | Backend |
| Flask | Web framework |
| MySQL | Database |
| HTML | Frontend |
| CSS | Styling |
| Jinja2 | Dynamic templates |
| Git & GitHub | Version control |

## Database Structure

DueMate uses three relational tables:

1. **Students** – Student account details.
2. **Subjects** – Subjects associated with students.
3. **Assignments** – Assignment details, deadlines and status.

### Relationships

- Students to Subjects: One-to-Many
- Students to Assignments: One-to-Many
- Subjects to Assignments: One-to-Many

## Project Structure

```text
DueMate/
├── app.py
├── config.py
├── schema.sql
├── requirements.txt
├── test_db.py
├── templates/
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    └── style.css
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/varalikapgupta/DueMate.git
cd DueMate
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

- Start MySQL Server.
- Create a database named `duemate`.
- Execute the SQL statements in `schema.sql`.
- Create your local `config.py` with your own database credentials and Flask secret key.

**Security:** Never upload `config.py`, passwords or secret keys to GitHub.

### 5. Run the application

```bash
python app.py
```

Open:

http://127.0.0.1:5000

## Future Enhancements

- Email deadline notifications
- Calendar integration
- Assignment priority management
- Academic progress analytics

## Developer

**Varalika Gupta**

GitHub: https://github.com/varalikapgupta

---

*DueMate – Manage tasks. Track progress. Meet deadlines.*
