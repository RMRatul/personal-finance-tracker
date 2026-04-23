from datetime import datetime
from tracker import ExpenseTracker
from models import Category

class Report:
    def __init__(self, tracker: ExpenseTracker):
        self._tracker=tracker
    
    def monthly_summary(self,year:int=None ,month:int =None)-> str:
        now=datetime.now()
        year=year or now.year
        month=month or now.month

        txns=self._tracker.get_by_month(year,month)
        expenses=[t for t in txns if t.transaction_type=="expense"]
        incomes=[t for t in txns if t.transaction_type=="income"]

        total_expense= sum(t.amount for t in expenses)
        total_income=sum(t. amount for t in incomes)
        balance=total_income-total_expense
        budget=self._tracker.user.monthly_budget
        used_pct=(total_expense/budget *100) if budget > 0 else 0

        month_name = datetime(year, month, 1).strftime("%B %Y")
 
        lines = [
            "",
            "=" * 50,
            f"  📊 MONTHLY REPORT — {month_name}",
            "=" * 50,
            f"  👤 User        : {self._tracker.user.name}",
            f"  💰 Budget      : ৳ {budget:.2f}",
            f"  📤 Total Spent : ৳ {total_expense:.2f} ({used_pct:.1f}%)",
            f"  📥 Total Income: ৳ {total_income:.2f}",
            f"  {'🟢' if balance >= 0 else '🔴'} Balance    : ৳ {balance:.2f}",
            "-" * 50,
            "  📂 CATEGORY BREAKDOWN:",
        ]

        breakdown = self._tracker.category_breakdown(txns)
        if breakdown:
            for cat, amount in breakdown.items():
                pct = (amount / total_expense * 100) if total_expense > 0 else 0
                bar = "█" * int(pct / 5)
                lines.append(
                    f"  {Category.display_name(cat):<22} ৳{amount:>8.2f}  {bar} {pct:.1f}%"
                )
        else:
            lines.append("  No expenses recorded.")
 
        lines += [
            "-" * 50,
            f"  Total transactions: {len(txns)} "
            f"({len(expenses)} expenses, {len(incomes)} incomes)",
            "=" * 50,
            "",
        ]
        return "\n".join(lines)

    def generate_chart(self, year: int = None, month: int = None) -> bool:
        """Generate a pie chart using matplotlib."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("  ⚠️  matplotlib not installed. Run: pip install matplotlib")
            return False
 
        now = datetime.now()
        year = year or now.year
        month = month or now.month
 
        txns = self._tracker.get_by_month(year, month)
        breakdown = self._tracker.category_breakdown(txns)
 
        if not breakdown:
            print("  No data to chart.")
            return False
 
        labels = [Category.display_name(c) for c in breakdown.keys()]
        values = list(breakdown.values())
        colors = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
            "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"
        ]
 
        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            autopct="%1.1f%%",
            colors=colors[:len(values)],
            startangle=140,
            textprops={"fontsize": 10}
        )
        month_name = datetime(year, month, 1).strftime("%B %Y")
        ax.set_title(
            f"Expense Breakdown — {month_name}\n"
            f"Total: ৳{sum(values):.2f}",
            fontsize=13,
            fontweight="bold"
        )
        plt.tight_layout()
 
        filename = f"report_{year}_{month:02d}.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        plt.show()
        print(f"  ✅ Chart saved as '{filename}'")
        return True
 
    def last_n_transactions(self, n: int = 10) -> str:
        txns = self._tracker.get_all()[:n]
        if not txns:
            return "  No transactions found."
        lines = [f"\n  Last {n} Transactions:", "-" * 50]
        for t in txns:
            lines.append(f"  {t}")
        lines.append("")
        return "\n".join(lines)



        
