# 💰 Personal Finance Tracker Bot

> Your Money, Your Control! — A CLI-based personal finance tracker built with Python.

---

## 📸 Features

- ➕ Add **Expenses** with categories
- 💚 Add **Income** records
- 📋 View transactions (by month, type, or all)
- 🗑️ Delete transactions
- 📊 Monthly summary report
- 📈 Pie chart visualization (matplotlib)
- 📧 Email HTML report via Gmail
- ⚠️ Budget alerts & savings tips
- ⏰ Auto monthly report scheduler

---

## 📁 Project Structure

```
personal-finance-tracker/
│
├── main.py            # Entry point - CLI menus
├── models.py          # User, Transaction, Category classes
├── file_manager.py    # Save/load data (JSON)
├── tracker.py         # Core logic - add, delete, calculate
├── alert.py           # Budget warnings & savings tips
├── report.py          # Monthly summary & pie chart
├── email_sender.py    # Gmail HTML report sender
├── scheduler.py       # Auto monthly report scheduler
├── requirements.txt   # Dependencies
└── data/              # Auto-created (gitignored)
    ├── user.json
    ├── transactions.json
    └── email_config.json
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/personal-finance-tracker.git
cd personal-finance-tracker
```

### 2. Create virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python main.py
```

---

## 📧 Email Setup (Gmail)

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Generate a **16-character App Password**
3. In the app, go to **Email Report → Setup**
4. Enter your Gmail address and App Password

---

## 📊 Categories

| Icon | Category     |
|------|-------------|
| 🍔   | Food        |
| 🚗   | Transport   |
| 💡   | Bills       |
| 🎮   | Entertainment |
| 💊   | Health      |
| 🛍️   | Shopping    |
| 📚   | Education   |
| 📦   | Other       |

---

## ⚙️ Tech Stack

- **Language:** Python 3.10+
- **Libraries:** `matplotlib`, `schedule`
- **Storage:** JSON files
- **Email:** Gmail SMTP

---

## 👨‍💻 Author

Built with ❤️ by **RMRatul**