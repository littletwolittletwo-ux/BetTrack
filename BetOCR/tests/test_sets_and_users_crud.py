import httpx, pytest, random, string

def rnd_name(prefix="set"):
    return prefix + "_" + "".join(random.choice(string.ascii_lowercase) for _ in range(5))

@pytest.mark.asyncio
async def test_sets_crud(base_url, admin_token):
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as c:
        # list (should include s,c,a,o,d,k)
        r = await c.get("/admin/sets", headers={"Authorization": f"Bearer {admin_token}"})
        r.raise_for_status()
        base_sets = [s["name"] for s in r.json()]
        assert all(x in base_sets for x in ["s","c","a","o","d","k"])

        # create
        name = rnd_name()
        rc = await c.post("/admin/sets", json={"name": name}, headers={"Authorization": f"Bearer {admin_token}"})
        rc.raise_for_status()
        sid = rc.json()["id"]

        # rename
        rn = await c.put(f"/admin/sets/{sid}", json={"name": name+"_ren"}, headers={"Authorization": f"Bearer {admin_token}"})
        rn.raise_for_status()
        assert rn.json()["name"] == name+"_ren"

        # disable
        rd = await c.patch(f"/admin/sets/{sid}/status", json={"is_active": False}, headers={"Authorization": f"Bearer {admin_token}"})
        rd.raise_for_status()
        assert rd.json()["is_active"] is False

@pytest.mark.asyncio
async def test_users_crud(base_url, admin_token):
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as c:
        # create user
        uname = "emp_" + rnd_name("u")
        rc = await c.post("/admin/users", json={"username": uname, "password": "Pass1234", "role": "employee"},
                          headers={"Authorization": f"Bearer {admin_token}"})
        rc.raise_for_status()
        uid = rc.json()["id"]

        # promote to admin
        rp = await c.put(f"/admin/users/{uid}", json={"role":"admin"}, headers={"Authorization": f"Bearer {admin_token}"})
        rp.raise_for_status()
        assert rp.json()["role"] == "admin"

        # disable
        rd = await c.patch(f"/admin/users/{uid}/status", json={"is_active": False}, headers={"Authorization": f"Bearer {admin_token}"})
        rd.raise_for_status()
        assert rd.json()["is_active"] is False

        # reset password
        rr = await c.post(f"/admin/users/{uid}/password", json={"password":"NewPass!234"}, headers={"Authorization": f"Bearer {admin_token}"})
        rr.raise_for_status()
        assert rr.json()["ok"] is True