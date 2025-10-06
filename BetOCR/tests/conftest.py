import os, anyio, httpx, pytest

BASE = os.getenv("E2E_BASE", "http://localhost:5000")

@pytest.fixture(scope="session")
def base_url():
    return BASE

@pytest.fixture(scope="session")
def sample_path():
    p = os.path.join("tests", "samples", "sportsbet_sample.png")
    assert os.path.exists(p), f"Missing sample image at {p}. Upload it first."
    return p

@pytest.fixture(scope="session")
async def admin_token(base_url):
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as c:
        r = await c.post("/auth/login", json={"username":"admin","password":"dwang1237"})
        r.raise_for_status()
        data = r.json()
    return data["access_token"]

@pytest.fixture(scope="session")
async def employee_token(base_url):
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as c:
        r = await c.post("/auth/login", json={"username":"slave","password":"admin"})
        r.raise_for_status()
        data = r.json()
    return data["access_token"]

def auth_headers(tok): return {"Authorization": f"Bearer {tok}"}