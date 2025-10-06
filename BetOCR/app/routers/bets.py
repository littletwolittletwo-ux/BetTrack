from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import os, json, uuid
from pathlib import Path
from typing import Any
from app.deps import current_user, require_admin
from app.db.session import get_db
from app.config import settings
from app.crud.bets import create_bet, get_or_create_bookmaker, recent_bets
from app.services.ocr.engine import ocr_image
from app.services.ocr.parsers import ladbrokes, pointsbet, sportsbet, tab, bet365, betfair
from app.services.ocr.parsers.multi_bet_parser import parse_multiple_bets
from app.services.profit import compute_profit
from app.schemas.bets import BetOut, BetUpdate

router = APIRouter(prefix="/bets", tags=["bets"])

PARSERS = {
 "ladbrokes": ladbrokes,
 "pointsbet": pointsbet,
 "sportsbet": sportsbet,
 "tab": tab,
 "bet365": bet365,
 "betfair": betfair
}

def generate_secure_filename(original_filename: str) -> str:
    """Generate a secure filename using UUID while preserving file extension.
    
    Args:
        original_filename: The user-provided filename
        
    Returns:
        A secure filename with UUID and preserved extension
    """
    # Extract file extension safely
    file_extension = Path(original_filename).suffix.lower() if original_filename else ""
    
    # Validate extension is safe (alphanumeric + dot only)
    if file_extension and not file_extension.replace(".", "").isalnum():
        file_extension = ""
    
    # Generate UUID-based filename with timestamp
    secure_name = f"{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex}"
    
    return f"{secure_name}{file_extension}"

@router.post("/upload", response_model=BetOut)
async def upload_bet(
 set_id: int = Form(...),
 bookmaker_name: str = Form(...),
 stake_manual: float = Form(...),
 image: UploadFile = File(...),
 user = Depends(current_user),
 db: Session = Depends(get_db)
):
 os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
 fname = generate_secure_filename(image.filename or "unknown.png")
 fpath = os.path.join(settings.UPLOAD_DIR, fname)
 with open(fpath, "wb") as f: f.write(await image.read())

 text, raw = ocr_image(fpath)
 # Type hint for clarity: raw is a dictionary from OCR engine
 raw: dict[str, Any] = raw
 
 # Use multi-bet parser for accurate net profit calculation
 multi_parsed = parse_multiple_bets(text)
 
 # Also try single bet parser for backward compatibility
 parser = PARSERS.get(bookmaker_name.strip().lower())
 single_parsed = parser.parse(text) if parser else {}

 # Use multi-bet results if multiple bets detected, otherwise use single bet
 if multi_parsed.get("total_bets", 0) > 1:
     # Multiple bets detected - use net profit calculation
     odds = multi_parsed.get("odds")
     result_status = multi_parsed.get("result_status") 
     cashout = None  # Multi-bet slips typically don't show cashout
     profit = multi_parsed.get("net_profit", 0.0)
     # Store detailed bet info in raw_ocr_json
     raw["multi_bet_details"] = multi_parsed
 else:
     # Single bet - use traditional calculation
     odds_value = single_parsed.get("odds")
     odds = float(odds_value) if odds_value and str(odds_value).strip() != '' else None
     result_status = single_parsed.get("result_status")
     cashout_value = single_parsed.get("cashout_amount")
     cashout = float(cashout_value) if cashout_value and str(cashout_value).strip() != '' else None
     commission_value = single_parsed.get("commission")
     comm = float(commission_value)/100.0 if commission_value and str(commission_value).strip() != '' else (settings.BETFAIR_DEFAULT_COMMISSION if bookmaker_name.lower()=="betfair" else 0.0)
     side = single_parsed.get("side")
     profit = compute_profit(bookmaker_name, side, odds, stake_manual, result_status, cashout, comm)

 bookmaker_id = get_or_create_bookmaker(db, bookmaker_name)
 bet = create_bet(
     db,
     set_id=set_id,
     bookmaker_id=bookmaker_id,
     uploaded_by=user.id,
     uploaded_at=datetime.utcnow(),
     image_path=fname,
     event_text=text[:5000],
     bet_type=single_parsed.get("side") or "back",
     odds_numeric=odds,
     stake_manual=stake_manual,
     potential_return=None,
     cashout_amount=cashout if 'cashout' in locals() else None,
     commission_rate=single_parsed.get("commission", 0) if 'single_parsed' in locals() else 0,
     result_status=result_status,
     settled_at=None,
     profit=profit,
     raw_ocr_json=raw,
     parse_version=2,  # Updated to version 2 for multi-bet support
     last_edited_by=None,
     last_edited_at=None
 )
 return bet

@router.get("/recent", response_model=list[BetOut])
def recent(hours: int = 72, set_id: int | None = None, db: Session = Depends(get_db), user = Depends(current_user)):
 bets = recent_bets(db, hours=hours, set_id=set_id)
 return bets

@router.get("/all", response_model=list[BetOut])
def get_all_bets(limit: int = 100, offset: int = 0, db: Session = Depends(get_db), user = Depends(current_user)):
 """Get all uploaded bets with comprehensive details for the uploads panel."""
 from app.models.bet import Bet
 
 bets = (
     db.query(Bet)
     .order_by(Bet.uploaded_at.desc())
     .offset(offset)
     .limit(limit)
     .all()
 )
 return bets

@router.patch("/{bet_id}", response_model=BetOut)
def update_bet(bet_id: int, bet_update: BetUpdate, db: Session = Depends(get_db), user = Depends(current_user)):
    """Update a bet record with manual corrections from confirmation popup."""
    from app.models.bet import Bet
    
    # Find the bet
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    
    # Check if user can edit (own bet or admin)
    if bet.uploaded_by != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Can only edit your own bets")
    
    # Update fields that were provided
    update_data = bet_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(bet, field):
            setattr(bet, field, value)
    
    # Recalculate profit if key fields changed
    if any(field in update_data for field in ['stake_manual', 'odds_numeric', 'result_status']):
        from app.services.profit import compute_profit
        # Get bookmaker name for profit calculation using the relationship
        bet_with_bookmaker = db.query(Bet).join(Bet.bookmaker).filter(Bet.id == bet_id).first()
        if bet_with_bookmaker and bet_with_bookmaker.bookmaker:
            bet.profit = compute_profit(
                bet_with_bookmaker.bookmaker.name,
                bet.bet_type or "back",
                bet.odds_numeric,
                bet.stake_manual,
                bet.result_status,
                bet.cashout_amount,
                bet.commission_rate or 0.0
            )
    
    # Track edit metadata
    bet.last_edited_by = user.id
    bet.last_edited_at = datetime.utcnow()
    
    db.commit()
    db.refresh(bet)
    
    return bet

@router.delete("/{bet_id}")
def delete_bet(bet_id: int, db: Session = Depends(get_db), user = Depends(current_user)):
    """Delete a bet record - can be used to cancel uploads from confirmation popup."""
    from app.models.bet import Bet
    import os
    
    # Find the bet
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    
    # Check permissions (own bet, admin, or fresh upload within 5 minutes)
    is_recent = (datetime.utcnow() - bet.uploaded_at).total_seconds() < 300  # 5 minutes
    can_delete = (bet.uploaded_by == user.id) or (user.role == "admin") or is_recent
    
    if not can_delete:
        raise HTTPException(status_code=403, detail="Cannot delete this bet")
    
    # Remove the image file if it exists
    if bet.image_path:
        image_file = os.path.join(settings.UPLOAD_DIR, bet.image_path)
        if os.path.exists(image_file):
            try:
                os.remove(image_file)
            except OSError:
                pass  # File removal failed, but continue with DB deletion
    
    # Delete the bet
    db.delete(bet)
    db.commit()
    
    return {"message": "Bet deleted successfully", "id": bet_id}