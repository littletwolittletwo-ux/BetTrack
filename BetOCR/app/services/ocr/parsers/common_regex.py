import re
from typing import Any, Dict

# Enhanced patterns to capture various betting slip formats
STAKE_RE = r"(stake|wager|bet|amount|win\s*â€¢\s*stake)\s*[:\-â€¢]?\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)"
ODDS_RE  = r"(odds|price|@|multi\s*@|game.*@)\s*[:\-â€¢]?\s*([0-9]+(?:\.[0-9]{1,3})?)"
RET_RE   = r"(potential\s*return|payout|return|bet\s*return|winnings)\s*[:\-â€¢]?\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)"
RESULT_RE = r"(result|status|outcome|state)\s*[:\-â€¢]?\s*(won|lost|void|cash.?out|pending|resulted|winning)"
CASHOUT_RE = r"(cash.?out|early\s*payout)\s*[:\-â€¢]?\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)"
COMM_RE = r"(commission|comm|fee)\s*[:\-â€¢]?\s*([0-9]+(?:\.[0-9]+)?)\s*%?"
SIDE_RE = r"\b(back|lay|for|against)\b"

# Enhanced patterns for detecting win/loss amounts  
WIN_AMOUNT_RE = r"(win\s+)?\+\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)"  # Win +$115.00, +$300.00, +$1.25
LOSS_AMOUNT_RE = r"-\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)"  # -$50.00, - $50.00, -50.00
PROFIT_INDICATOR_RE = r"(profit|win|winning|won|loss|lost|losing)"  # Result indicators

# Additional patterns for specific betting slip elements  
LEGS_RE = r"([0-9]+)\s*(legs?|leg)\b"  # "3 Legs", "2 Legs", "4 Legs"
EVENT_RE = r"(v|vs|versus|\s-\s)"
BONUS_RE = r"(bonus|promo|boost)\s*[:\-â€¢]?\s*\$?\s*([0-9]+(?:\.[0-9]{1,2})?)"

def grab(rx, text_lower):
 m = re.search(rx, text_lower, re.I)
 if not m:
     return None
 # Handle patterns with different numbers of groups safely
 try:
     return m.group(2)  # Try group 2 first (most patterns)
 except IndexError:
     return m.group(1)  # Fallback to group 1 for single-group patterns

def parse_common(text: str) -> Dict[str, Any]:
 t = text.lower()
 
 # Try multiple approaches for better extraction
 result = {
     "stake_ocr": grab(STAKE_RE, t),
     "odds": grab(ODDS_RE, t),
     "potential_return": grab(RET_RE, t),
     "result_status": grab(RESULT_RE, t),
     "cashout_amount": grab(CASHOUT_RE, t),
     "commission": grab(COMM_RE, t),
     "side": grab(SIDE_RE, t),
 }
 
 # Additional extractions for enhanced parsing
 legs = grab(LEGS_RE, t)
 bonus = grab(BONUS_RE, t)
 
 # If no standard odds found, try alternative patterns
 if not result["odds"]:
     # Look for pattern like "4.00" after multi, game, or similar
     alt_odds = re.search(r"(multi|same\s*game).*?([0-9]+\.[0-9]{1,3})", t, re.I)
     if alt_odds:
         result["odds"] = alt_odds.group(2)
 
 # Enhanced result status detection with better win/loss amount parsing
 win_amount_match = re.search(WIN_AMOUNT_RE, t, re.I)
 loss_amount_match = re.search(LOSS_AMOUNT_RE, t, re.I)
 
 if win_amount_match:
     result["actual_return"] = float(win_amount_match.group(2))  # Updated to use group(2) for enhanced pattern
     result["result_status"] = "won"
 elif loss_amount_match:
     result["loss_amount"] = float(loss_amount_match.group(1))
     result["result_status"] = "lost"
 
 # If no result status found yet, try other detection methods
 if not result["result_status"]:
     # Look for explicit win/loss indicators
     if re.search(r"(âœ“|tick|win|won|winning)", t, re.I):
         result["result_status"] = "won" 
     elif re.search(r"(âœ—|x|cross|lose|lost|losing)", t, re.I):
         result["result_status"] = "lost"
     elif re.search(r"pending|waiting", t, re.I):
         result["result_status"] = "pending"
 
 # Add metadata
 if legs:
     result["legs"] = legs
 if bonus:
     result["bonus"] = bonus
     
 return result

# New patterns for enhanced result detection from training data
NO_RETURN_RE = r"(no\s*return|n/a|not\s*applicable|return\s*n/a)"
COLLECTED_ZERO_RE = r"collected\s*\$?\s*0\.00"
LOSS_INDICATORS_RE = r"\b(lost|lose|losing)\b"
WIN_INDICATORS_RE = r"(win\s*\+\s*\$?([0-9]+(?:\.[0-9]{1,2})?))"

def parse_enhanced(text: str) -> Dict[str, Any]:
    """Enhanced parsing function that handles the new betting slip formats from training data"""
    t = text.lower()
    result: Dict[str, Any] = parse_common(text) or {}
    
    # Use local raw dict to avoid nested subscripting on potentially None objects
    raw: Dict[str, Any] = result.get("raw_ocr_json") or {}
    result["raw_ocr_json"] = raw
    
    # Use deterministic result precedence to avoid false classifications
    # Priority: Explicit loss indicators > Cashout/Void > Win amounts > Checkmarks > Pending
    
    # HIGHEST PRIORITY: Explicit loss indicators (No Return, Lost, Collected $0.00)
    if re.search(NO_RETURN_RE, t, re.I) or re.search(COLLECTED_ZERO_RE, t, re.I):
        result["result_status"] = "lost"
        raw["actual_return"] = 0.0
    elif re.search(LOSS_INDICATORS_RE, t, re.I):
        result["result_status"] = "lost"
    
    # SECOND PRIORITY: Keep existing cashout/void status from base parsing
    elif result.get("result_status") in ["void", "cash_out", "cashout"]:
        pass  # Don't override these important statuses
    
    # THIRD PRIORITY: Win amount detection for formats like "Win +$115.00"  
    elif not result.get("result_status") or result.get("result_status") == "pending":
        win_match = re.search(WIN_INDICATORS_RE, t, re.I)
        if win_match:
            raw["actual_return"] = float(win_match.group(2))
            result["result_status"] = "won"
        
        # LOWEST PRIORITY: Checkmark indicators (only if no other status determined)
        elif not result.get("result_status") and ("âœ“" in text or "tick" in t):
            result["result_status"] = "won"
    
    # Enhanced leg detection for multi-bets
    legs_match = re.search(LEGS_RE, t, re.I)
    if legs_match:
        raw["legs"] = legs_match.group(1)  # Number of legs
        result["bet_type"] = "multi"  # This column exists in schema
    
    # Bonus bet detection
    if "bonus bet" in t or "get a $" in t:
        bonus_match = re.search(r"\$([0-9]+(?:\.[0-9]{1,2})?)", t)
        if bonus_match:
            raw["bonus"] = bonus_match.group(1)
    
    return result
