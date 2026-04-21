from datetime import datetime
from models import User,Transaction
from file_manager import FileManager

class ExpenseTracker:
    def __init__(self, user : User,fm:FileManager):
        self.user=user
        self._fm=fm
        self._transactions:list[Transaction]=fm.load_transactions()


#----------------------------Add / Delete --------------------------
    def add_transaction(self, amount:float,category:str,note:str,transaction_type:str)-> Transaction:
        t=Transaction(amount,category,note,transaction_type)
        self._transactions.append(t)
        self._fm.save_transactions(self._transactions)
        return t
    
    def delete_transaction(self,transaction_id: str)-> bool:
        original =len(self._transactions)
        self._transactions=[t for t in self._transactions if t.id !=transaction_id]
        if len(self._transactions)<original:
            self._fm.save_transactions(self._transactions)
            return True
        return False

    #------------------------ Getters --------------------------------
    def get_all(self)->list[Transaction]:
        return sorted(self._transactions,key=lambda t:(t.date,t.time),reverse=True)
    
    def get_by_month(self, year: int = None, month: int = None) -> list[Transaction]:
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        short_year = str(year)[2:]  # 2025 → 25
        return [t for t in self._transactions if t.date.endswith(f"{month:02d}-{short_year}")]
    

  #---------------------------- Calculations --------------------------------------

    def total_expense_this_month(self)-> float:
        return sum(t.amount for t in self.get_by_month() if t.transaction_type=="expense")
    
    def total_income_this_month(self)-> float:
        return sum(t.amount for t in self.get_by_month() if t.transaction_type=="income")
    def balance_this_month(self)-> float:
        return self.total_income_this_month()-self.total_expense_this_month()
    def budget_used_percent(self)-> float:
        budget=self.user.monthly_budget
        if budget<= 0:
            return 0.0
        return (self.total_expense_this_month()/budget)*100
    def category_breakdown(self,transactions: list[Transaction]= None)-> dict:
        txns=transactions if transactions is not None else self.get_by_month()
        breakdown={}
        for t in txns:
            if t.transaction_type=="expense":
                breakdown[t.category]=breakdown.get(t.category,0)+t.amount
        return dict(sorted(breakdown.items(), key=lambda x: x[1],reverse=True))