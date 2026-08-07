# CEOE Two-Phase UI Prototype — Fixed

Run:

```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Then open:

http://127.0.0.1:8050

The navigation callback has been corrected to use Dash's `ALL` pattern-matching wildcard.

## Deploying on Vercel

This app is a Dash (Flask) app exposed to Vercel as a Python serverless function via `api/index.py`, configured by `vercel.json`.

1. Push this repo to GitHub (see below).
2. In Vercel, "Add New Project" → import `ceoe-ui`.
3. Framework preset: **Other**. No build command / output directory needed — `vercel.json` handles routing.
4. Deploy.

