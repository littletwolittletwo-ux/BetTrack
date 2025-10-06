from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import csv, io, os, uuid
from datetime import datetime
from typing import Optional
from app.deps import current_user              # employees & admins
from app.db.session import get_db
from app.models.user import User
from app.models.bet_set import BetSet
from app.models.csv_upload import CsvUpload
from app.crud.bets import create_bet, get_or_create_bookmaker

router = APIRouter(prefix="/import", tags=["csv-import"])

def _resolve_set_id(db: Session, set_val: Optional[str]) -> Optional[int]:
    if not set_val:
        return None
    s = set_val.strip()
    if not s:
        return None
    if s.isdigit():
        obj = db.get(BetSet, int(s))
        return obj.id if obj else None
    obj = db.query(BetSet).filter(BetSet.name == s).first()
    return obj.id if obj else None

@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="Validate only; do not write rows"),
    default_set: Optional[str] = Query(None, description="Fallback set (name or id) for new schema if CSV has no 'set' column"),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    raw = await file.read()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    
    # Save file to disk if not dry run
    file_path = None
    csv_upload_record = None
    if not dry_run:
        # Create unique filename with sanitized original name
        # Sanitize filename to prevent path traversal
        original_filename = os.path.basename(file.filename) if file.filename else "unknown.csv"
        # Remove any remaining path separators and keep only safe characters
        safe_original = "".join(c for c in original_filename if c.isalnum() or c in "._-")
        if not safe_original:
            safe_original = "upload.csv"
        
        timestamp = int(datetime.utcnow().timestamp())
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = f"{timestamp}_{unique_id}_{safe_original}"
        file_path = os.path.join("csv_uploads", safe_filename)
        
        # Ensure directory exists
        os.makedirs("csv_uploads", exist_ok=True)
        
        # Write file to disk
        with open(file_path, "wb") as f:
            f.write(raw)
        
        # Create database record
        csv_upload_record = CsvUpload(
            uploaded_by=user.id,
            original_filename=file.filename or "unknown.csv",
            file_path=file_path,
            file_size=len(raw),
            records_imported=0,  # Will update later
            records_skipped=0    # Will update later
        )
        db.add(csv_upload_record)
        db.flush()  # Get the ID without committing

    # Parse once, normalize headers
    sio = io.StringIO(text)
    rdr = csv.DictReader(sio)
    if not rdr.fieldnames:
        raise HTTPException(400, "CSV has no header row")
    headers = [h.strip().lower() for h in rdr.fieldnames]

    has_legacy = {"set", "profit"}.issubset(set(headers)) and not {"stake", "odds"}.issubset(set(headers))
    has_new = {"stake", "odds", "profit"}.issubset(set(headers))

    if not has_legacy and not has_new:
        raise HTTPException(
            400,
            "CSV must match one of:\n"
            "  - legacy: set,profit\n"
            "  - new: stake,odds,profit (optional set)  "
            "If using new format without a 'set' column, pass ?default_set=<name|id>."
        )

    # Re-read with normalized keys
    sio2 = io.StringIO(text)
    rdr2 = csv.DictReader(sio2)
    rows = []
    for r in rdr2:
        rows.append({(k or '').strip().lower(): (v or '').strip() for k, v in r.items()})

    # Prepare response
    result = {
        "filename": file.filename,
        "mode": "legacy" if has_legacy else "new",
        "dry_run": dry_run,
        "total_rows": 0,
        "inserted": 0,
        "skipped": 0,
        "errors": [],
    }

    # Only create bookmaker if we're actually inserting
    csv_bookmaker_id = None
    if not dry_run:
        csv_bookmaker_id = get_or_create_bookmaker(db, "CSV Import")

    # Resolve default set if provided
    default_set_id = _resolve_set_id(db, default_set) if default_set else None

    for i, row in enumerate(rows, start=2):  # header == 1
        # Skip blank line
        if not any(row.values()):
            continue

        result["total_rows"] += 1

        try:
            if has_legacy:
                # ----- Legacy: set,profit -----
                set_id = _resolve_set_id(db, row.get("set"))
                if not set_id:
                    result["skipped"] += 1
                    result["errors"].append({"row": i, "error": f"Unknown set '{row.get('set')}'"})
                    continue
                profit = float(row.get("profit", "").replace(",", ""))
                if not dry_run:
                    if csv_bookmaker_id is None:
                        csv_bookmaker_id = get_or_create_bookmaker(db, "CSV Import")
                    create_bet(
                        db,
                        set_id=set_id,
                        bookmaker_id=csv_bookmaker_id,
                        uploaded_by=user.id,
                        uploaded_at=datetime.utcnow(),
                        image_path="csv_import",
                        event_text=f"CSV legacy import: {file.filename}",
                        bet_type="manual",
                        odds_numeric=None,
                        stake_manual=0.0,
                        potential_return=None,
                        cashout_amount=None,
                        commission_rate=None,
                        result_status="manual",
                        settled_at=None,
                        profit=round(profit, 2),
                        raw_ocr_json=None,
                        parse_version=2,
                        last_edited_by=user.id,
                        last_edited_at=datetime.utcnow(),
                    )
                    result["inserted"] += 1
                continue

            # ----- New: stake,odds,profit (+ optional set) -----
            # set resolution (row set OR default_set query)
            set_id = _resolve_set_id(db, row.get("set")) or default_set_id
            if not set_id:
                result["skipped"] += 1
                result["errors"].append({"row": i, "error": "Missing set; supply a 'set' column or ?default_set=<name|id>."})
                continue

            # required numerics
            stake = float(row.get("stake", "").replace(",", ""))
            odds = float(row.get("odds", "").replace(",", ""))
            profit = float(row.get("profit", "").replace(",", ""))

            if not dry_run:
                if csv_bookmaker_id is None:
                    csv_bookmaker_id = get_or_create_bookmaker(db, "CSV Import")
                create_bet(
                    db,
                    set_id=set_id,
                    bookmaker_id=csv_bookmaker_id,
                    uploaded_by=user.id,
                    uploaded_at=datetime.utcnow(),
                    image_path="csv_import",
                    event_text=f"CSV new-format import: {file.filename}",
                    bet_type="manual",
                    odds_numeric=odds,
                    stake_manual=stake,
                    potential_return=None,
                    cashout_amount=None,
                    commission_rate=None,
                    result_status="manual",
                    settled_at=None,
                    profit=round(profit, 2),
                    raw_ocr_json=None,
                    parse_version=2,
                    last_edited_by=user.id,
                    last_edited_at=datetime.utcnow(),
                )
                result["inserted"] += 1

        except ValueError as ve:
            result["skipped"] += 1
            result["errors"].append({"row": i, "error": f"Invalid numeric value: {ve}"})
        except Exception as e:
            result["skipped"] += 1
            result["errors"].append({"row": i, "error": f"{type(e).__name__}: {e}"})

    # Update CSV upload record with final counts if not dry run
    if not dry_run and csv_upload_record:
        csv_upload_record.records_imported = result["inserted"]
        csv_upload_record.records_skipped = result["skipped"]
        db.commit()
        
        # Add upload information to result
        result["csv_upload_id"] = csv_upload_record.id
        result["file_saved"] = file_path
    
    return result