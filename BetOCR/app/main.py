from fastapi import FastAPI, Request, Depends, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.db.session import get_db, SessionLocal, engine
from sqlalchemy.orm import Session
from app.db.init_data import init_core
from app.models import User, BetSet, Bookmaker, Bet, CsvUpload  # ensure models import
from app.auth.router import router as auth_router
from app.routers.bets import router as bets_router
from app.routers.stats import router as stats_router
# Removed files router - using StaticFiles instead
from app.routers.admin import router as admin_router
from app.routers.imports import router as import_router
from app.routers.csv_management import router as csv_management_router
from app.routers.risk import router as risk_router

app = FastAPI(title="bet-ocr-app")

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Mount static files first
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(bets_router)
app.include_router(stats_router)
# Mount uploads directory as static files (handles GET/HEAD properly)
app.mount("/files", StaticFiles(directory=settings.UPLOAD_DIR), name="files")
app.include_router(admin_router)
app.include_router(import_router)
app.include_router(csv_management_router)
app.include_router(risk_router)

@app.on_event("startup")
def startup_seed():
 # Seed sets & bookmakers
 with SessionLocal() as db:
     init_core(db)

@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "service": "bet-ocr-app"}

@app.get("/", response_class=RedirectResponse)
def root():
    return RedirectResponse(url="/admin/", status_code=302)

# Minimal HTML helpers (quick dev UI)
LOGIN_HTML = """
<h3>Login</h3>
<form method="post" action="/auth/login" onsubmit="doLogin(event)">
<label>Username</label><input id="u" /><br/>
<label>Password</label><input id="p" type="password" /><br/>
<button type="submit">Login</button>
</form>
<pre id="out"></pre>
<script>
async function doLogin(e){
e.preventDefault();
const r = await fetch('/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:document.getElementById('u').value,password:document.getElementById('p').value})});
const j = await r.json(); localStorage.setItem('token', j.access_token); localStorage.setItem('role', j.role); document.getElementById('out').textContent = JSON.stringify(j,null,2);
}
</script>
"""

UPLOAD_HTML = """
<h3>Upload Bet</h3>
<form onsubmit="uploadBet(event)">
<label>Set ID</label><input id="set_id" type="number" required/><br/>
<label>Bookmaker</label><input id="bk" value="Sportsbet"/><br/>
<label>Stake (manual)</label><input id="stake" type="number" step="0.01" required/><br/>
<label>Image</label><input id="img" type="file" accept="image/*" required/><br/>
<button>Upload</button>
</form>
<pre id="out"></pre>
<script>
async function uploadBet(e){
e.preventDefault();
const fd = new FormData();
fd.append('set_id', document.getElementById('set_id').value);
fd.append('bookmaker_name', document.getElementById('bk').value);
fd.append('stake_manual', document.getElementById('stake').value);
fd.append('image', document.getElementById('img').files[0]);
const r = await fetch('/bets/upload',{method:'POST', headers:{'Authorization':'Bearer '+localStorage.getItem('token')}, body: fd});
const j = await r.json(); document.getElementById('out').textContent = JSON.stringify(j,null,2);
}
</script>
"""

ADMIN_HTML = """
<h3>Admin</h3>
<p>Token in LS. Simple helpers:</p>
<button onclick="listUsers()">List Users</button>
<button onclick="listSets()">List Sets</button>
<button onclick="stats()">Stats (72h)</button>
<pre id="out"></pre>
<script>
async function listUsers(){
const r = await fetch('/admin/users',{headers:{'Authorization':'Bearer '+localStorage.getItem('token')}});
document.getElementById('out').textContent = JSON.stringify(await r.json(),null,2);
}
async function listSets(){
const r = await fetch('/admin/sets',{headers:{'Authorization':'Bearer '+localStorage.getItem('token')}});
document.getElementById('out').textContent = JSON.stringify(await r.json(),null,2);
}
async function stats(){
const r = await fetch('/stats/sets?hours=72',{headers:{'Authorization':'Bearer '+localStorage.getItem('token')}});
document.getElementById('out').textContent = JSON.stringify(await r.json(),null,2);
}
</script>
"""

@app.get("/login", response_class=RedirectResponse)
def login_redirect(): 
    return RedirectResponse(url="/admin/login", status_code=302)

@app.get("/upload", response_class=RedirectResponse)
def upload_redirect(): 
    return RedirectResponse(url="/admin/upload", status_code=302)

@app.get("/admin", response_class=RedirectResponse)
def admin_redirect(): 
    return RedirectResponse(url="/admin/", status_code=302)

@app.get("/admin/", response_class=FileResponse)
def admin_spa():
    return FileResponse("app/static/admin/index.html")

# Catch-all route for React SPA client-side routing
@app.get("/admin/{path:path}")
def admin_spa_catchall(path: str):
    return FileResponse("app/static/admin/index.html")