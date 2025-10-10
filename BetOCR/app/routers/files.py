from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os
from app.deps import CurrentUser
from app.config import settings

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/{filename}")
def get_file(filename: str):
 path = os.path.join(settings.UPLOAD_DIR, filename)
 if not os.path.exists(path):
     raise HTTPException(404, "Not found")
 return FileResponse(path)
