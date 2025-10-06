from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import math
from typing import List, Dict, Any
from app.db.session import get_db
from app.deps import current_user
from app.models.bet import Bet
from app.models.bet_set import BetSet
from app.models.bookmaker import Bookmaker

router = APIRouter(prefix="/stats", tags=["risk"])

def _utcnow():
    return datetime.utcnow()

@router.get("/risk")
def risk_stats(
    hours: int = Query(720, ge=1, le=365*24, description="Lookback window in hours"),
    db: Session = Depends(get_db),
    user = Depends(current_user),
):
    # Time range
    since = _utcnow() - timedelta(hours=hours)

    # Pull settled/recorded bets in window (exclude pending bets with NULL profit)
    q = (
        db.query(
            Bet.id,
            Bet.set_id,
            Bet.bookmaker_id,
            Bet.uploaded_at,
            Bet.profit,
            Bet.stake_manual,
        )
        .filter(Bet.uploaded_at >= since)
        .filter(Bet.profit.isnot(None))
    )
    rows = q.all()
    if not rows:
        return {
            "hours": hours,
            "summary": {"sharpe": None, "max_drawdown": None, "var95": None, "n": 0},
            "daily_pl": [],
            "exposure_by_set": [],
            "exposure_by_bookmaker": []
        }

    # Convert to Python lists
    profits = []
    daily_map = {}  # date -> profit sum
    expo_set = {}   # set_id -> total stake
    expo_bm = {}    # bookmaker_id -> total stake
    cum = 0.0
    equity_curve = []  # (timestamp, cum_profit)

    # Build aggregates
    for r in rows:
        p = float(r.profit or 0.0)
        s = float(r.stake_manual or 0.0)
        profits.append(p)

        d = (r.uploaded_at or _utcnow()).date()
        daily_map[d] = daily_map.get(d, 0.0) + p

        if r.set_id:
            expo_set[r.set_id] = expo_set.get(r.set_id, 0.0) + s
        if r.bookmaker_id:
            expo_bm[r.bookmaker_id] = expo_bm.get(r.bookmaker_id, 0.0) + s

    # Daily P/L series
    daily_pl = [{"date": d.isoformat(), "pl": round(v, 2)} for d, v in sorted(daily_map.items())]

    # Equity curve (cumulative over time using daily series)
    for point in daily_pl:
        cum += point["pl"]
        equity_curve.append(cum)

    # Max Drawdown
    max_drawdown = None
    if equity_curve:
        peak = equity_curve[0]
        mdd = 0.0
        for v in equity_curve:
            if v > peak:
                peak = v
            drawdown = peak - v
            if drawdown > mdd:
                mdd = drawdown
        max_drawdown = round(mdd, 2)

    # VaR 95% (historical, on per-bet profits)
    var95 = None
    if profits:
        sorted_p = sorted(profits)
        idx = int(0.05 * (len(sorted_p) - 1))
        var95 = round(sorted_p[idx], 2)  # 5th percentile of profit distribution (can be negative)

    # Sharpe Ratio (per-bet), risk-free assumed 0 in this context
    sharpe = None
    if profits and len(profits) > 1:
        mean_p = sum(profits) / len(profits)
        var_p = sum((x - mean_p) ** 2 for x in profits) / (len(profits) - 1)
        std_p = math.sqrt(var_p) if var_p > 0 else 0.0
        if std_p > 0:
            sharpe = round(mean_p / std_p, 3)

    # Human-friendly exposures (join names)
    set_names = {s.id: s.name for s in db.query(BetSet).all()}
    bm_names = {b.id: b.name for b in db.query(Bookmaker).all()}

    exposure_by_set = [{"name": set_names.get(k, str(k)), "stake": round(v, 2)} for k, v in sorted(expo_set.items(), key=lambda x: x[0])]
    exposure_by_bookmaker = [{"name": bm_names.get(k, str(k)), "stake": round(v, 2)} for k, v in sorted(expo_bm.items(), key=lambda x: x[0])]

    return {
        "hours": hours,
        "summary": {
            "sharpe": sharpe,
            "max_drawdown": max_drawdown,
            "var95": var95,
            "n": len(profits)
        },
        "daily_pl": daily_pl,
        "exposure_by_set": exposure_by_set,
        "exposure_by_bookmaker": exposure_by_bookmaker
    }