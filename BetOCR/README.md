# bet-ocr-app

FastAPI app on Replit to OCR bookmaker betslip screenshots, compute profit, and track running stats per Set. Roles: **admin** & **employee**. Admin can manage users & sets, edit any bet, and view stats in a timeframe (default 72h). Employee uploads screenshots, picks a Set (active only), and enters stake manually.

## Quick start
1. Add secrets in Replit (copy .env.example to Secrets).
2. Shell:


pip install -r requirements.txt
alembic upgrade head
python scripts/create_defaults.py

3. Click **Run**. Visit the repl URL:
- API root: `/`
- Minimal HTML:
  - `/login` (basic form)
  - `/upload` (employee)
  - `/admin` (links to Users/Sets/Stats)
4. Default logins (dev only):
- Admin: `admin` / `dwang1237`
- Employee: `slave` / `admin`

## Notes
- Use Neon for a free Postgres `DATABASE_URL`.
- OCR = Tesseract by default; later you can add PaddleOCR.
- Sets seeded: `s, c, a, o, d, k`.