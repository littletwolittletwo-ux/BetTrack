from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
from typing import List

from app.deps import AdminUser  # Only admins can access these endpoints
from app.db.session import get_db
from app.models.csv_upload import CsvUpload
from app.models.user import User

router = APIRouter(prefix="/admin/csv", tags=["csv-management"])

@router.get("/uploads")
async def list_csv_uploads(
    days: int = Query(7, ge=1, le=7, description="Number of days to look back (max 7 due to retention policy)"),
    admin: User = Depends(AdminUser),
    db: Session = Depends(get_db),
):
    """List CSV uploads from the last N days (capped at 7 days due to retention policy)"""
    # Automatically clean up files older than 7 days to enforce retention policy
    cleanup_cutoff = datetime.utcnow() - timedelta(days=7)
    old_uploads = db.query(CsvUpload).filter(CsvUpload.uploaded_at < cleanup_cutoff).all()
    
    for old_upload in old_uploads:
        # Delete file from disk if it exists
        if old_upload.file_path and os.path.exists(old_upload.file_path):
            try:
                os.remove(old_upload.file_path)
            except OSError:
                pass  # Continue even if file deletion fails
        # Delete database record
        db.delete(old_upload)
    
    db.commit()
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    uploads = db.query(CsvUpload).filter(
        CsvUpload.uploaded_at >= cutoff_date
    ).order_by(CsvUpload.uploaded_at.desc()).all()
    
    result = []
    for upload in uploads:
        # Get uploader username
        uploader = db.get(User, upload.uploaded_by)
        
        # Check if file still exists
        file_exists = os.path.exists(upload.file_path) if upload.file_path else False
        
        result.append({
            "id": upload.id,
            "original_filename": upload.original_filename,
            "uploaded_by": uploader.username if uploader else "Unknown",
            "uploaded_at": upload.uploaded_at.isoformat(),
            "file_size": upload.file_size,
            "records_imported": upload.records_imported,
            "records_skipped": upload.records_skipped,
            "file_exists": file_exists,
            "days_old": (datetime.utcnow() - upload.uploaded_at).days
        })
    
    return {
        "uploads": result,
        "total_count": len(result),
        "days_requested": days
    }

@router.get("/uploads/{upload_id}/download")
async def download_csv_file(
    upload_id: int,
    admin: User = Depends(AdminUser),
    db: Session = Depends(get_db),
):
    """Download a specific CSV file (only files uploaded within last 7 days)"""
    upload = db.get(CsvUpload, upload_id)
    if not upload:
        raise HTTPException(404, "CSV upload not found")
    
    # Enforce 7-day retention policy
    age_days = (datetime.utcnow() - upload.uploaded_at).days
    if age_days >= 7:
        raise HTTPException(410, "CSV file is no longer available (files are retained for 7 days only)")
    
    if not upload.file_path or not os.path.exists(upload.file_path):
        raise HTTPException(404, "CSV file not found on disk")
    
    return FileResponse(
        path=upload.file_path,
        filename=upload.original_filename,
        media_type="text/csv"
    )

@router.delete("/uploads/{upload_id}")
async def delete_csv_upload(
    upload_id: int,
    admin: User = Depends(AdminUser),
    db: Session = Depends(get_db),
):
    """Delete a CSV upload record and file"""
    upload = db.get(CsvUpload, upload_id)
    if not upload:
        raise HTTPException(404, "CSV upload not found")
    
    # Delete file from disk if it exists
    if upload.file_path and os.path.exists(upload.file_path):
        try:
            os.remove(upload.file_path)
        except OSError:
            pass  # Continue even if file deletion fails
    
    # Delete database record
    db.delete(upload)
    db.commit()
    
    return {"message": "CSV upload deleted successfully"}

@router.post("/cleanup")
async def cleanup_old_csv_files(
    days: int = Query(7, ge=7, le=7, description="Delete files older than 7 days (fixed for retention policy)"),
    admin: User = Depends(AdminUser),
    db: Session = Depends(get_db),
):
    """Clean up CSV files older than 7 days (enforced by retention policy)"""
    # Force days to 7 to enforce retention policy
    days = 7
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Find old uploads
    old_uploads = db.query(CsvUpload).filter(
        CsvUpload.uploaded_at < cutoff_date
    ).all()
    
    deleted_files = 0
    deleted_records = 0
    
    for upload in old_uploads:
        # Delete file from disk if it exists
        if upload.file_path and os.path.exists(upload.file_path):
            try:
                os.remove(upload.file_path)
                deleted_files += 1
            except OSError:
                pass  # Continue even if file deletion fails
        
        # Delete database record
        db.delete(upload)
        deleted_records += 1
    
    db.commit()
    
    return {
        "message": f"Cleanup complete",
        "deleted_files": deleted_files,
        "deleted_records": deleted_records,
        "cutoff_days": days
    }
