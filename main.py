"""
💰 Personal Finance Tracker Bot
================================
A real-world CLI bot to track your income & expenses.
"""
 
import os
import sys
from datetime import datetime
 
from models import User, Category
from file_manager import FileManager
from tracker import ExpenseTracker
from alert import Alert
from report import Report
from email_sender import EmailSender, EmailConfig
 
 
# -------------------------- Helpers ---------------------------

def clear():
    os.system("cls" if os.name=='nt' else 'clear')
def banner():
    print("""
╔══════════════════════════════════════════════════╗
║        💰 Personal Finance Tracker Bot           ║
║           Your Money, Your Control!              ║
╚══════════════════════════════════════════════════╝
""")
    
def divider(char="─", width=50):
    print(char * width)

def prompt(text:str) -> str:
    return input(f" {text}: ").strip()

def show_alerts(alert: Alert):
    messages = alert.check_budget()
    if messages:
        print()
        for msg in messages:
            print(f"  {msg}")
        print()

# -------------------- Setup ---------------------
def setup_user(fm: FileManager) -> User:
    clear()
    banner()
    print("  👋 Welcome! Let's set up your profile first.\n")
    name = prompt("Your name")
    while True:
        try:
            budget = float(prompt("Monthly budget (৳)"))
            if budget <= 0:
                print("  ❌ Budget must be positive!")
                continue
            break
        except ValueError:
            print("  ❌ Please enter a valid number.")
 
    user = User(name, budget)
    fm.save_user(user)
    print(f"\n  ✅ Profile created! Welcome, {name}! 🎉\n")
    input("  Press Enter to continue...")
    return user

# ------------------------ Menus --------------------------
def main_menu(tracker: ExpenseTracker, alert: Alert):
    clear()
    banner()
 
    # Quick stats
    spent = tracker.total_expense_this_month()
    income = tracker.total_income_this_month()
    budget = tracker.user.monthly_budget
    pct = tracker.budget_used_percent()
    bar_filled = int(pct / 10)
    bar = "█" * bar_filled + "░" * (10 - bar_filled)
 
    print(f"  Hello, {tracker.user.name}! 👋   {datetime.now().strftime('%d %b %Y')}")
    divider()
    print(f"  Budget  : [{bar}] {pct:.1f}%")
    print(f"  Spent   : ৳ {spent:.2f}  /  ৳{budget:.2f}")
    print(f"  Income  : ৳ {income:.2f}")
    print(f"  Balance : ৳ {tracker.balance_this_month():.2f}")
    divider()
 
    show_alerts(alert)
 
    print("  MENU")
    print("  1. ➕ Add Expense")
    print("  2. 💚 Add Income")
    print("  3. 📋 View Transactions")
    print("  4. 🗑️  Delete Transaction")
    print("  5. 📊 Monthly Report")
    print("  6. 📈 Show Chart")
    print("  7. 📧 Email Report")
    print("  8. ⚙️  Settings")
    print("  9. 🚪 Exit")
    divider()
 
def add_transaction_menu(tracker: ExpenseTracker, alert: Alert,
                         transaction_type: str = "expense"):
    clear()
    banner()
    type_label = "💸 Add Expense" if transaction_type == "expense" else "💚 Add Income"
    print(f"  {type_label}\n")
 
    # Amount
    while True:
        try:
            amount = float(prompt("Amount (৳)"))
            if amount <= 0:
                print("  ❌ Amount must be positive!")
                continue
            break
        except ValueError:
            print("  ❌ Invalid amount.")
 
    # Category
    if transaction_type == "expense":
        print("\n  Categories:")
        cats = Category.all_categories()
        for i, c in enumerate(cats, 1):
            print(f"    {i}. {Category.display_name(c)}")
        while True:
            try:
                choice = int(prompt("Choose category (number)"))
                if 1 <= choice <= len(cats):
                    category = cats[choice - 1]
                    break
                print(f"  ❌ Enter 1–{len(cats)}")
            except ValueError:
                print("  ❌ Invalid choice.")
    else:
        category = "other"
 
    note = prompt("Note (optional)") or "—"
 
    t = tracker.add_transaction(amount, category, note, transaction_type)
    print(f"\n  ✅ Added: {t}")
 
    # Check for large expense
    if transaction_type == "expense":
        large = alert.check_large_expense(amount)
        if large:
            print(f"  {large}")
        show_alerts(alert)
        tip = alert.get_savings_tip()
        print(f"  💡 Tip: {tip}")
 
    print()
    input("  Press Enter to continue...")
 
def view_transactions_menu(tracker: ExpenseTracker, report: Report):
    clear()
    banner()
    print("  📋 VIEW TRANSACTIONS\n")
    print("  1. Last 10 transactions")
    print("  2. This month's expenses")
    print("  3. This month's income")
    print("  4. All transactions")
    print("  5. ← Back")
    divider()
 
    choice = prompt("Choice")
 
    if choice == "1":
        print(report.last_n_transactions(10))
    elif choice == "2":
        txns = [t for t in tracker.get_by_month() if t.transaction_type == "expense"]
        print(f"\n  This month's expenses ({len(txns)} records):")
        divider()
        for t in txns:
            print(f"  {t}")
        print()
    elif choice == "3":
        txns = [t for t in tracker.get_by_month() if t.transaction_type == "income"]
        print(f"\n  This month's income ({len(txns)} records):")
        divider()
        for t in txns:
            print(f"  {t}")
        print()
    elif choice == "4":
        all_txns = tracker.get_all()
        print(f"\n  All transactions ({len(all_txns)} records):")
        divider()
        for t in all_txns:
            print(f"  [{t.id[-6:]}] {t}")
        print()
    elif choice == "5":
        return
 
    input("  Press Enter to continue...")

def delete_transaction_menu(tracker: ExpenseTracker):
    clear()
    banner()
    print("  🗑️  DELETE TRANSACTION\n")
    all_txns = tracker.get_all()[:15]
 
    if not all_txns:
        print("  No transactions to delete.")
        input("  Press Enter to continue...")
        return
 
    for i, t in enumerate(all_txns, 1):
        print(f"  {i:2}. [{t.id[-6:]}] {t}")
    divider()
 
    try:
        choice = int(prompt("Enter number to delete (0 to cancel)"))
        if choice == 0:
            return
        if 1 <= choice <= len(all_txns):
            t = all_txns[choice - 1]
            confirm = prompt(f"Delete '{t.note}' ৳ {t.amount:.2f}? (y/n)")
            if confirm.lower() == "y":
                if tracker.delete_transaction(t.id):
                    print("  ✅ Deleted successfully!")
                else:
                    print("  ❌ Could not delete.")
        else:
            print("  ❌ Invalid choice.")
    except ValueError:
        print("  ❌ Invalid input.")
 
    input("  Press Enter to continue...")

def settings_menu(tracker: ExpenseTracker, fm: FileManager):
    clear()
    banner()
    print("  ⚙️  SETTINGS\n")
    print(f"  Current profile: {tracker.user}")
    divider()
    print("  1. Change monthly budget")
    print("  2. Change name")
    print("  3. ← Back")
    divider()
 
    choice = prompt("Choice")
 
    if choice == "1":
        while True:
            try:
                new_budget = float(prompt("New monthly budget (৳)"))
                if new_budget <= 0:
                    print("  ❌ Must be positive!")
                    continue
                tracker.user.monthly_budget = new_budget
                fm.save_user(tracker.user)
                print(f"  ✅ Budget updated to ৳{new_budget:.2f}")
                break
            except ValueError:
                print("  ❌ Invalid amount.")
    elif choice == "2":
        new_name = prompt("New name")
        if new_name:
            tracker.user.name = new_name
            fm.save_user(tracker.user)
            print(f"  ✅ Name updated to {new_name}")
    elif choice == "3":       
        return          
 
    input("  Press Enter to continue...")

def email_menu(report: Report):
    clear()
    banner()
    print("  📧 EMAIL REPORT\n")
 
    config = EmailConfig.load()
 
    if not config:
        print("  No email configured yet. Let's set it up.\n")
        print("  ℹ️  You need a Gmail App Password (not your normal password).")
        print("  Get one at: myaccount.google.com/apppasswords\n")
        sender = prompt("Your Gmail address")
        app_pass = prompt("Gmail App Password (16 chars)")
        receiver = prompt("Send report to (email)")
        config = EmailConfig(sender, app_pass, receiver)
        config.save()
        print("\n  ✅ Email config saved!")
    else:
        print("  Current config:")
        print(f"  From : {config.sender_email}")
        print(f"  To   : {config.receiver_email}")
        divider()
        print("  1. Send report now")
        print("  2. Send specific month report")
        print("  3. Update email settings")
        print("  4. ← Back")
        divider()
        choice = prompt("Choice")
 
        if choice == "1":
            print("\n  📤 Sending report...")
            sender_obj = EmailSender(config, report)
            success, msg = sender_obj.send_report()
            print(f"  {msg}")
        elif choice == "2":
            try:
                year = int(prompt("Year (e.g. 2026)"))
                month = int(prompt("Month (1-12)"))
                if 1 <= month <= 12:
                    print("\n  📤 Sending report...")
                    sender_obj = EmailSender(config, report)
                    success, msg = sender_obj.send_report(year, month)
                    print(f"  {msg}")
                else:
                    print("  ❌ Invalid month!")
            except ValueError:
                print("  ❌ Invalid input!")
        elif choice == "3":
            sender = prompt("New Gmail address")
            app_pass = prompt("New App Password")
            receiver = prompt("Send to (email)")
            config = EmailConfig(sender, app_pass, receiver)
            config.save()
            print("\n  ✅ Email config updated!")
        elif choice == "4":
            return
 
    input("\n  Press Enter to continue...")


# ----------------------- Main ----------------------------------------
def main():
    fm = FileManager()
 
    # First time setup
    if not fm.user_exists():
        user = setup_user(fm)
    else:
        user = fm.load_user()
        if not user:
            print("  ❌ Error loading user data. Please restart.")
            sys.exit(1)
 
    tracker = ExpenseTracker(user, fm)
    alert = Alert(tracker)
    report = Report(tracker)
 
    while True:
        main_menu(tracker, alert)
        choice = prompt("Choice")
 
        if choice == "1":
            add_transaction_menu(tracker, alert, "expense")
        elif choice == "2":
            add_transaction_menu(tracker, alert, "income")
        elif choice == "3":
            view_transactions_menu(tracker, report)
        elif choice == "4":
            delete_transaction_menu(tracker)
        elif choice == "5":
            clear()
            banner()
            print(report.monthly_summary())
            input("  Press Enter to continue...")
        elif choice == "6":
            clear()
            banner()
            print("  📈 Generating chart...\n")
            report.generate_chart()
            input("  Press Enter to continue...")
        elif choice == "7":
            email_menu(report)
        elif choice == "8":
            settings_menu(tracker, fm)
        elif choice == "9":
            clear()
            print("\n  👋 Goodbye! Keep tracking your money! 💰\n")
            sys.exit(0)
        else:
            print("  ❌ Invalid choice. Try again.")
 
 
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  👋 Bye!\n")
        sys.exit(0)