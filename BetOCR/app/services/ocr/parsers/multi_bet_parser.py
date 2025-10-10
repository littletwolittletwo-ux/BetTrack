import re
from typing import List, Dict, Any
from .common_regex import parse_common

def parse_multiple_bets(text: str) -> Dict[str, Any]:
    """Parse multiple bets from a single betting slip and calculate net profit."""
    
    # Split text into individual bet sections
    # Look for patterns that indicate new bets: "Same Game Multi @", "Multi @", etc.
    bet_sections = re.split(r'(?=Same\s+Game\s+Multi\s*@|Multi\s*@|Bet\s*[0-9])', text, flags=re.IGNORECASE)
    
    individual_bets = []
    total_stakes = 0.0
    total_returns = 0.0
    net_profit = 0.0
    
    for i, section in enumerate(bet_sections):
        if not section.strip():
            continue
            
        # Parse each section as an individual bet
        parsed = parse_common(section)
        
        if not parsed.get("odds"):
            continue
            
        stake = float(parsed.get("stake_ocr") or 0) if parsed.get("stake_ocr") and str(parsed.get("stake_ocr")).strip() else 0.0
        odds = float(parsed.get("odds") or 0) if parsed.get("odds") and str(parsed.get("odds")).strip() else 0.0
        result_status = parsed.get("result_status")
        
        # Look for return amounts in this section (e.g., "+$56.25")
        return_match = re.search(r'\+\s*\$([0-9]+(?:\.[0-9]{1,2})?)', section, re.IGNORECASE)
        actual_return = float(return_match.group(1)) if return_match else 0.0
        
        # Extract number of legs for this bet
        legs_match = re.search(r'([0-9]+)\s*leg[s]?', section, re.IGNORECASE)
        total_legs = int(legs_match.group(1)) if legs_match else 1
        
        # Return-first profit calculation (architect's recommendation)
        if actual_return > 0:
            # Use actual return as source of truth for profit calculation
            bet_profit = actual_return - stake
            
            # Classify outcome by comparing to expected amounts (with 2% tolerance)
            expected_full_win = stake * odds if odds else 0
            expected_partial = 0.7 * stake
            
            tolerance = 0.02 * stake  # 2% tolerance
            
            if odds and abs(actual_return - expected_full_win) <= tolerance:
                failed_legs = 0  # All legs hit
            elif abs(actual_return - expected_partial) <= tolerance:
                failed_legs = 1  # 1 leg failed 
            elif abs(actual_return - stake) <= tolerance:
                failed_legs = 0  # Break-even/push (treat as no legs failed for simplicity)
            else:
                # Partial return that doesn't match standard patterns
                failed_legs = 1 if total_legs > 1 else 0
                
        else:
            # No return parsed - fall back to user's leg failure rules
            if result_status == "lost" or actual_return == 0:
                failed_legs = 2 if total_legs > 1 else 1
                bet_profit = -stake
            elif result_status == "won" and odds and odds > 0:
                # Assume all legs hit if marked as won but no return data
                failed_legs = 0
                bet_profit = stake * (odds - 1)
            else:
                # Conservative assumption
                failed_legs = 2 if total_legs > 1 else 1
                bet_profit = -stake
            
        individual_bets.append({
            "bet_number": i + 1,
            "odds": odds,
            "stake": stake,
            "total_legs": total_legs,
            "failed_legs": failed_legs,
            "result_status": result_status or "unknown",
            "actual_return": actual_return,
            "profit": round(bet_profit, 2)
        })
        
        total_stakes += stake
        total_returns += actual_return
        net_profit += bet_profit
    
    # Return summary with individual bet details
    return {
        "total_bets": len(individual_bets),
        "individual_bets": individual_bets,
        "total_stakes": total_stakes,
        "total_returns": total_returns, 
        "net_profit": round(net_profit, 2),
        "overall_result": "won" if net_profit > 0 else ("lost" if net_profit < 0 else "break_even"),
        # For backward compatibility with single bet parsing
        "odds": individual_bets[0]["odds"] if individual_bets else None,
        "stake_ocr": str(total_stakes) if total_stakes > 0 else None,
        "result_status": "won" if net_profit > 0 else ("lost" if net_profit < 0 else "break_even")
    }
