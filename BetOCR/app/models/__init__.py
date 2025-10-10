# Central model imports to ensure proper initialization order
# Import base models first (no relationships)
from app.models.user import User
from app.models.bet_set import BetSet

# Import models with relationships second
from app.models.bookmaker import Bookmaker
from app.models.bet import Bet
from app.models.csv_upload import CsvUpload

# Export all models for easy importing
__all__ = [
    "User",
    "BetSet", 
    "Bookmaker",
    "Bet",
    "CsvUpload"
]
