import json
import os
from typing import Optional
from models import User,Transaction

class FileManager:
    DATA_DIR="Data"
    USER_FILE="Data/user.json"
    TRANSACTIONS_FILE="Data/transactions.json"
 # ---------------------- User----------------------
    def __init__(self):
        self._ensure_data_dir()
    def _ensure_data_dir(self):
        os.makedirs(self.DATA_DIR,exist_ok=True)

    def save_user(self,user:User) -> bool:
        try:
            with open(self.USER_FILE,"w") as f:
                json.dump(user.to_dict(),f,indent=2)
                return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False
    
    def load_user(self) -> Optional[User]:
        if not os.path.exists(self.USER_FILE):
            return None
        
        try:
            with open(self.USER_FILE,"r") as f:
                return User.from_dict(json.load(f))
        except Exception as e:
            print(f"Error loading user: {e}")
            return None
        def user_exists(self) -> bool:
         return os.path.exists(self.USER_FILE)
        
# ------------------------ Transactions -------------------------------
    def save_transactions(self, transactions: list[Transaction]) -> bool:
        try:
            with open(self.TRANSACTIONS_FILE, "w") as f:
                json.dump([t.to_dict() for t in transactions], f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving transactions: {e}")
            return False
    
    def load_transactions(self) -> list[Transaction]:
        if not os.path.exists(self.TRANSACTIONS_FILE):
            return []
        try:
            with open(self.TRANSACTIONS_FILE, "r") as f:
                return [Transaction.from_dict(d) for d in json.load(f)]
        except Exception as e:
            print(f"Error loading transactions: {e}")
            return []

    def clear_transactions(self) -> bool:
        """Wipe all transactions (used for testing / reset)."""
        try:
            with open(self.TRANSACTIONS_FILE, "w") as f:
                json.dump([], f)
            return True
        except Exception as e:
            print(f"Error clearing transactions: {e}")
            return False

            

