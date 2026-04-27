import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

from report import Report
from models import Category


CONFIG_FILE = "data/email_config.json"


class EmailConfig:
    def __init__(self, sender_email: str, app_password: str, receiver_email: str):
        self.sender_email = sender_email
        self.app_password = app_password      # Gmail App Password (16 chars)
        self.receiver_email = receiver_email

    def to_dict(self) -> dict:
        return {
            "sender_email": self.sender_email,
            "app_password": self.app_password,
            "receiver_email": self.receiver_email,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EmailConfig":
        return cls(
            sender_email=data["sender_email"],
            app_password=data["app_password"],
            receiver_email=data["receiver_email"],
        )

    def save(self):
        os.makedirs("data", exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls) -> Optional["EmailConfig"]:
        if not os.path.exists(CONFIG_FILE):
            return None
        try:
            with open(CONFIG_FILE) as f:
                return cls.from_dict(json.load(f))
        except Exception:
            return None

    @classmethod
    def exists(cls) -> bool:
        return os.path.exists(CONFIG_FILE)


class EmailSender:
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587

    def __init__(self, config: EmailConfig, report: Report):
        self._config = config
        self._report = report

    def _build_html(self, year: int, month: int) -> str:
        tracker = self._report._tracker
        txns = tracker.get_by_month(year, month)
        breakdown = tracker.category_breakdown(txns)

        total_expense = sum(t.amount for t in txns if t.transaction_type == "expense")
        total_income = sum(t.amount for t in txns if t.transaction_type == "income")
        balance = total_income - total_expense
        budget = tracker.user.monthly_budget
        used_pct = (total_expense / budget * 100) if budget > 0 else 0
        month_name = datetime(year, month, 1).strftime("%B %Y")

        bar_filled = min(int(used_pct), 100)
        bar_color = (
            "#e74c3c" if used_pct >= 100
            else "#f39c12" if used_pct >= 80
            else "#2ecc71"
        )

        # Category rows
        cat_rows = ""
        for cat, amount in breakdown.items():
            pct = (amount / total_expense * 100) if total_expense > 0 else 0
            cat_rows += f"""
            <tr>
              <td style="padding:8px 12px;">{Category.display_name(cat)}</td>
              <td style="padding:8px 12px; text-align:right;">৳{amount:,.2f}</td>
              <td style="padding:8px 12px; text-align:right; color:#888;">{pct:.1f}%</td>
            </tr>"""

        # Recent transactions (last 5)
        recent = sorted(txns, key=lambda t: (t.date, t.time), reverse=True)[:5]
        txn_rows = ""
        for t in recent:
            color = "#e74c3c" if t.transaction_type == "expense" else "#2ecc71"
            sign = "-" if t.transaction_type == "expense" else "+"
            txn_rows += f"""
            <tr>
              <td style="padding:8px 12px; color:#888;">{t.date}</td>
              <td style="padding:8px 12px;">{Category.display_name(t.category)}</td>
              <td style="padding:8px 12px;">{t.note}</td>
              <td style="padding:8px 12px; text-align:right; color:{color}; font-weight:500;">
                {sign}৳{t.amount:,.2f}
              </td>
            </tr>"""

        balance_color = "#2ecc71" if balance >= 0 else "#e74c3c"
        balance_sign = "+" if balance >= 0 else ""

        return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:30px auto;background:#fff;border-radius:10px;
              overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:#2c3e50;padding:28px 32px;">
      <h1 style="color:#fff;margin:0;font-size:22px;">💰 Monthly Finance Report</h1>
      <p style="color:#aab4c0;margin:6px 0 0;font-size:14px;">
        {month_name} · {tracker.user.name}
      </p>
    </div>

    <!-- Summary Cards -->
    <div style="display:flex;gap:0;border-bottom:1px solid #eee;">
      <div style="flex:1;padding:20px 24px;border-right:1px solid #eee;text-align:center;">
        <p style="margin:0;font-size:12px;color:#888;text-transform:uppercase;">Spent</p>
        <p style="margin:6px 0 0;font-size:24px;font-weight:700;color:#e74c3c;">
          ৳ {total_expense:,.2f}
        </p>
      </div>
      <div style="flex:1;padding:20px 24px;border-right:1px solid #eee;text-align:center;">
        <p style="margin:0;font-size:12px;color:#888;text-transform:uppercase;">Income</p>
        <p style="margin:6px 0 0;font-size:24px;font-weight:700;color:#2ecc71;">
          ৳ {total_income:,.2f}
        </p>
      </div>
      <div style="flex:1;padding:20px 24px;text-align:center;">
        <p style="margin:0;font-size:12px;color:#888;text-transform:uppercase;">Balance</p>
        <p style="margin:6px 0 0;font-size:24px;font-weight:700;color:{balance_color};">
          {balance_sign} ৳ {balance:,.2f}
        </p>
      </div>
    </div>

    <!-- Budget Bar -->
    <div style="padding:24px 32px;border-bottom:1px solid #eee;">
      <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
        <span style="font-size:13px;color:#555;">Budget used</span>
        <span style="font-size:13px;font-weight:600;color:{bar_color};">
          {used_pct:.1f}% of ৳ {budget:,.2f}
        </span>
      </div>
      <div style="background:#eee;border-radius:6px;height:10px;overflow:hidden;">
        <div style="width:{bar_filled}%;background:{bar_color};height:100%;border-radius:6px;">
        </div>
      </div>
    </div>

    <!-- Category Breakdown -->
    <div style="padding:24px 32px;border-bottom:1px solid #eee;">
      <h2 style="font-size:15px;font-weight:600;color:#2c3e50;margin:0 0 14px;">
        Category Breakdown
      </h2>
      <table style="width:100%;border-collapse:collapse;font-size:14px;">
        <thead>
          <tr style="background:#f8f8f8;">
            <th style="padding:8px 12px;text-align:left;color:#888;font-weight:500;">Category</th>
            <th style="padding:8px 12px;text-align:right;color:#888;font-weight:500;">Amount</th>
            <th style="padding:8px 12px;text-align:right;color:#888;font-weight:500;">%</th>
          </tr>
        </thead>
        <tbody>
          {cat_rows if cat_rows else
           '<tr><td colspan="3" style="padding:12px;color:#aaa;text-align:center;">'
           'No expenses this month</td></tr>'}
        </tbody>
      </table>
    </div>

    <!-- Recent Transactions -->
    <div style="padding:24px 32px;border-bottom:1px solid #eee;">
      <h2 style="font-size:15px;font-weight:600;color:#2c3e50;margin:0 0 14px;">
        Recent Transactions
      </h2>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead>
          <tr style="background:#f8f8f8;">
            <th style="padding:8px 12px;text-align:left;color:#888;font-weight:500;">Date</th>
            <th style="padding:8px 12px;text-align:left;color:#888;font-weight:500;">Category</th>
            <th style="padding:8px 12px;text-align:left;color:#888;font-weight:500;">Note</th>
            <th style="padding:8px 12px;text-align:right;color:#888;font-weight:500;">Amount</th>
          </tr>
        </thead>
        <tbody>
          {txn_rows if txn_rows else
           '<tr><td colspan="4" style="padding:12px;color:#aaa;text-align:center;">'
           'No transactions</td></tr>'}
        </tbody>
      </table>
    </div>

    <!-- Footer -->
    <div style="padding:20px 32px;background:#f8f8f8;text-align:center;">
      <p style="margin:0;font-size:12px;color:#aaa;">
        Sent by 💰 Personal Finance Tracker Bot ·
        {datetime.now().strftime("%d %b %Y %H:%M")}
      </p>
    </div>

  </div>
</body>
</html>"""

    def send_report(self, year: int = None, month: int = None) -> tuple[bool, str]:
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        month_name = datetime(year, month, 1).strftime("%B %Y")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"💰 Finance Report — {month_name}"
        msg["From"] = self._config.sender_email
        msg["To"] = self._config.receiver_email

        # Plain text fallback
        plain = self._report.monthly_summary(year, month)
        msg.attach(MIMEText(plain, "plain"))

        # HTML version
        html = self._build_html(year, month)
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP(self.SMTP_HOST, self.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(self._config.sender_email, self._config.app_password)
                server.sendmail(
                    self._config.sender_email,
                    self._config.receiver_email,
                    msg.as_string()
                )
            return True, f"✅ Report sent to {self._config.receiver_email}"
        except smtplib.SMTPAuthenticationError:
            return False, "❌ Authentication failed! Check your Gmail App Password."
        except smtplib.SMTPException as e:
            return False, f"❌ SMTP error: {e}"
        except Exception as e:
            return False, f"❌ Error: {e}"