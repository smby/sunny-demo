# Deployment Notes

## Recommended setup for external testing
- Frontend: GitHub Pages (public static site)
- Backend: Render / Railway / Fly.io (private API with env keys)

This keeps API keys off the frontend while letting Sunny test from browser.

## Frontend (GitHub Pages)
1. Build frontend:
```bash
cd frontend
npm install
npm run build
```
2. Deploy `frontend/dist` to GitHub Pages.
3. Set `VITE_API_BASE` to your hosted backend URL before build.

## Backend (hosted)
1. Deploy `backend` app with Python runtime.
2. Start command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
3. Configure env vars:
- `CORS_ORIGINS=<github-pages-origin>`
- `OPENAI_API_KEY=...` (optional)
- `OPENAI_MODEL=gpt-4o-mini`

## Security reminders
- Never put API keys in frontend `.env` for public deploy.
- Restrict CORS to your deployed frontend domain.
