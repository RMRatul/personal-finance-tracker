from typing import Optional
from tracker import ExpenseTracker

class Alert:
    WARNING_THRESHOLD = 80  # % OF BUDGET
    DANGER_THRESHOLD=100   # % OF BUDGET

    def __init__(self,tracker :ExpenseTracker):
        self._tracker=tracker
    
    def check_budget(self)-> list[str]:
        msg=[]
        used=self._tracker.budget_used_percent()
        budget=self._tracker.user.monthly_budget
        spent=self._tracker.total_expense_this_month()
        remaining=budget-spent

        if used >= self.DANGER_THRESHOLD:
            msg.append(f"🚨 BUDGET EXCEEDED! You've spent ৳ {spent:.2f} "f"({used:.1f}% of ৳ {budget:.2f} budget)!")
        elif used >= self.WARNING_THRESHOLD:
            msg.append(f"⚠️  WARNING! {used:.1f}% budget used. "f"Only ৳ {remaining:.2f} remaining this month.")
 
        return msg
        
    def check_large_expense(self,amount:float, threshold:float=1000)-> Optional[str]:
            if amount >= threshold:
                return f"💸 Large expense detected: ৳ {amount:.2f}"
            return None
        
    def get_savings_tip(self) -> str:
            breakdown = self._tracker.category_breakdown()
            if not breakdown:
                return "✅ No expenses yet this month. Great start!"
 
            top_category = max(breakdown, key=breakdown.get)
            top_amount = breakdown[top_category]
            tips = {
            "food": f"🍔 You spent ৳ {top_amount:.2f} on food. Try cooking at home more!",
            "entertainment": f"🎮 ৳ {top_amount:.2f} on entertainment. Consider free alternatives!",
            "shopping": f"🛍️ ৳ {top_amount:.2f} on shopping. Make a list before buying!",
            "transport": f"🚗 ৳ {top_amount:.2f} on transport. Try carpooling or public transit!",
            }

            return tips.get(top_category,f"📊 Top spending: {top_category} (৳ {top_amount:.2f}). Keep an eye on it!")