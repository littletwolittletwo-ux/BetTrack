import httpx, pytest, os, json

@pytest.mark.asyncio
async def test_employee_can_upload_and_parse(base_url, employee_token, sample_path):
    async with httpx.AsyncClient(base_url=base_url, timeout=60) as c:
        # First, fetch active sets and choose one
        rs = await c.get("/admin/sets?active=true", headers={"Authorization": f"Bearer {employee_token}"})
        # If employee is blocked from /admin/sets, fall back to admin token flow in other tests.
        if rs.status_code not in (200, 401, 403):
            rs.raise_for_status()
        set_id = None
        if rs.status_code == 200:
            sets = rs.json()
            assert sets, "No active sets available"
            set_id = sets[0]["id"]

        if not set_id:
            # fallback: hardcode known seeded set id = 1
            set_id = 1

        # Prepare multipart with sample image
        files = {
            "image": ("sportsbet_sample.png", open(sample_path, "rb"), "image/png")
        }
        data = {
            "set_id": str(set_id),
            "bookmaker_name": "Sportsbet",
            "stake_manual": "25.00"
        }
        r = await c.post("/bets/upload", headers={"Authorization": f"Bearer {employee_token}"}, files=files, data=data)
        r.raise_for_status()
        bet = r.json()

        # Basic assertions
        assert bet["set_id"] == set_id
        assert float(bet["stake_manual"]) == 25.00
        assert bet["bookmaker_id"] > 0
        # odds may or may not be detected; profit should be computed (0, positive for win, or -stake if lost)
        assert "profit" in bet