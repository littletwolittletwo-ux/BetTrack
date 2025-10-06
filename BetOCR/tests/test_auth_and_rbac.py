import httpx, pytest

@pytest.mark.asyncio
async def test_login_admin_and_employee(base_url):
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as c:
        ra = await c.post("/auth/login", json={"username":"admin","password":"dwang1237"})
        re = await c.post("/auth/login", json={"username":"slave","password":"admin"})
        assert ra.status_code == 200 and re.status_code == 200
        assert ra.json()["role"] == "admin"
        assert re.json()["role"] == "employee"

@pytest.mark.asyncio
async def test_admin_only_routes_access_control(base_url, admin_token, employee_token):
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as c:
        # Admin can list users
        r1 = await c.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert r1.status_code == 200

        # Employee should be forbidden
        r2 = await c.get("/admin/users", headers={"Authorization": f"Bearer {employee_token}"})
        assert r2.status_code in (401,403)