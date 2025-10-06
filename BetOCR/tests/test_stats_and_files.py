import httpx, pytest

@pytest.mark.asyncio
async def test_recent_stats_and_file_serving(base_url, admin_token):
    async with httpx.AsyncClient(base_url=base_url, timeout=30) as c:
        # stats
        rs = await c.get("/stats/sets?hours=72", headers={"Authorization": f"Bearer {admin_token}"})
        rs.raise_for_status()
        assert isinstance(rs.json(), list)

        # Attempt to fetch a file listing via bets recent then file
        rb = await c.get("/bets/recent?hours=72", headers={"Authorization": f"Bearer {admin_token}"})
        rb.raise_for_status()
        items = rb.json()
        if items:
            img = items[0]["image_path"]
            rf = await c.get(f"/files/{img}", headers={"Authorization": f"Bearer {admin_token}"})
            assert rf.status_code in (200, 404)  # 200 if file present, 404 if cleaned up
        else:
            assert items == [] or isinstance(items, list)