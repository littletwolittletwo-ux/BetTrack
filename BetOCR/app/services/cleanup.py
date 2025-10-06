import os
import datetime
import logging
from pathlib import Path
from app.config import settings

logger = logging.getLogger(__name__)

def cleanup_old_images(retention_days: int = 7):
    """
    Clean up image files older than retention_days from the upload directory.
    Only removes image files, leaves database records intact.
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    
    if not upload_dir.exists():
        logger.info(f"Upload directory {upload_dir} does not exist, skipping cleanup")
        return
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=retention_days)
    cutoff_timestamp = cutoff_date.timestamp()
    
    deleted_count = 0
    total_size_freed = 0
    
    # Common image file extensions
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'}
    
    logger.info(f"Starting cleanup of images older than {retention_days} days from {upload_dir}")
    
    try:
        for file_path in upload_dir.iterdir():
            if file_path.is_file():
                # Check if it's an image file
                if file_path.suffix.lower() in image_extensions:
                    file_stat = file_path.stat()
                    file_modified_time = file_stat.st_mtime
                    
                    if file_modified_time < cutoff_timestamp:
                        try:
                            file_size = file_stat.st_size
                            file_path.unlink()  # Delete the file
                            deleted_count += 1
                            total_size_freed += file_size
                            logger.info(f"Deleted old image: {file_path.name}")
                        except Exception as e:
                            logger.error(f"Failed to delete {file_path.name}: {e}")
                    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
    
    if deleted_count > 0:
        size_mb = total_size_freed / (1024 * 1024)
        logger.info(f"Cleanup completed: Deleted {deleted_count} old images, freed {size_mb:.2f} MB")
    else:
        logger.info("Cleanup completed: No old images found to delete")
    
    return {
        "deleted_count": deleted_count,
        "size_freed_mb": total_size_freed / (1024 * 1024),
        "retention_days": retention_days
    }

def cleanup_orphaned_images():
    """
    Clean up image files that exist in the filesystem but no longer 
    have corresponding database records.
    """
    from sqlalchemy.orm import Session
    from app.db.session import get_db
    from app.models.bet import Bet
    
    upload_dir = Path(settings.UPLOAD_DIR)
    
    if not upload_dir.exists():
        logger.info(f"Upload directory {upload_dir} does not exist, skipping orphan cleanup")
        return
    
    db = next(get_db())
    
    try:
        # Get all image paths from database
        db_image_paths = set()
        bets = db.query(Bet).filter(Bet.image_path.isnot(None)).all()
        for bet in bets:
            if bet.image_path:
                db_image_paths.add(bet.image_path)
        
        # Find files in upload directory that aren't referenced in database
        orphaned_count = 0
        total_size_freed = 0
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff'}
        
        for file_path in upload_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                if file_path.name not in db_image_paths:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        orphaned_count += 1
                        total_size_freed += file_size
                        logger.info(f"Deleted orphaned image: {file_path.name}")
                    except Exception as e:
                        logger.error(f"Failed to delete orphaned image {file_path.name}: {e}")
        
        if orphaned_count > 0:
            size_mb = total_size_freed / (1024 * 1024)
            logger.info(f"Orphan cleanup completed: Deleted {orphaned_count} orphaned images, freed {size_mb:.2f} MB")
        else:
            logger.info("Orphan cleanup completed: No orphaned images found")
            
        return {
            "deleted_count": orphaned_count,
            "size_freed_mb": total_size_freed / (1024 * 1024)
        }
            
    except Exception as e:
        logger.error(f"Error during orphan cleanup: {e}")
        return {"error": str(e)}
    finally:
        db.close()