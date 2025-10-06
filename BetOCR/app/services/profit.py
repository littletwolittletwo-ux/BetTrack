def compute_profit(bookmaker: str, side: str | None, odds: float | None, stake: float,
                result_status: str | None, cashout_amount: float | None, commission: float | None) -> float:
 commission = commission or 0.0
 if result_status and result_status.lower().startswith("cashout") and cashout_amount is not None:
     return round(float(cashout_amount) - float(stake), 2)
 if bookmaker.lower() == "betfair" and (side or "").lower() == "lay":
     if result_status == "won":
         return round(float(stake) * (1 - commission), 2)
     if result_status == "lost" and odds:
         return round(- float(stake) * (float(odds) - 1), 2)
     return 0.0
 # back logic
 if result_status == "won" and odds:
     return round(float(stake) * (float(odds) - 1) * (1 - commission), 2)
 if result_status == "lost":
     return round(-float(stake), 2)
 return 0.0