from datetime import datetime
from dataclasses import dataclass,field

class Category:
     CATEGORIES = {
        "food": "🍔 Food",
        "transport": "🚗 Transport",
        "bills": "💡 Bills",
        "entertainment": "🎮 Entertainment",
        "health": "💊 Health",
        "shopping": "🛍️  Shopping",
        "education": "📚 Education",
        "other": "📦 Other",
    }
     
     @classmethod
     def is_valid(cls,category : str) -> bool:
          return category.lower() in cls.CATEGORIES
     
     @classmethod
     def display_name(cls, category : str) -> str:
          return cls.CATEGORIES.get(category.lower(),"📦 Other")
     
     @classmethod
     def all_categories(cls) -> list:
          return list(cls.CATEGORIES.keys())
     
@dataclass
class Transaction:
    amount: float
    category: str
    note: str
    transaction_type: str  # "expense" or "income"
    date: str = field(default_factory=lambda: datetime.now().strftime("%d-%m-%y"))
    time: str = field(default_factory=lambda: datetime.now().strftime("%H:%M"))
    id: str = field(default_factory=lambda: datetime.now().strftime("%d%m%y%H%M%S%f"))


    def to_dict(self) -> dict:
         return {
             "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "note": self.note,
            "type": self.transaction_type,
            "date": self.date,
            "time": self.time,

         }
    
    @classmethod
    def from_dict(cls,data: dict) -> "Transaction":
         t=cls(
            amount=data["amount"],
            category=data["category"],
            note=data["note"],
            transaction_type=data["type"],
            date=data["date"],
            time=data["time"],
         )

         t.id=data["id"]

         return t
    
    def __str__(self) -> str:
          icon = "🔴" if self.transaction_type == "expense" else "🟢"
          return(f"{icon} [{self.date}] {Category.display_name(self.category)}"
                  f"| ৳ {self.amount:.2f} | {self.note}")
    


class User:
    def __init__(self, name: str, monthly_budget: float):
        self.name = name
        self.monthly_budget = monthly_budget
        self._created_at = datetime.now().strftime("%d-%m-%y")
 
    @property
    def monthly_budget(self):
        return self._monthly_budget
 
    @monthly_budget.setter
    def monthly_budget(self, value: float):
        if value <= 0:
            raise ValueError("Budget must be positive!")
        self._monthly_budget = value
 
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "monthly_budget": self._monthly_budget,
            "created_at": self._created_at,
        }
 
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        user = cls(data["name"], data["monthly_budget"])
        user._created_at = data.get("created_at", datetime.now().strftime("%d-%m-%y"))
        return user
 
    def __str__(self) -> str:
        return f"👤 {self.name} | Monthly Budget: ৳ {self._monthly_budget:.2f}"
        
       
 
         