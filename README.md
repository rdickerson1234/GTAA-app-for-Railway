# GTAA Momentum App — Deploy Guide

## What this is
A mobile web app that shows the top 15 ETFs ranked by momentum (20d + 60d + 120d returns),
with an OLS slope filter and a TIP regime signal. Opens on iPhone Safari like a native app.

---

## Files
```
gtaa-app/
  app.py              ← Flask backend + momentum logic
  requirements.txt    ← Python dependencies
  Procfile            ← tells Railway how to start the app
  templates/
    index.html        ← iPhone-optimized frontend
```

---

## Deploy to Railway (free, ~10 minutes)

### Step 1 — Put the files on GitHub
1. Go to github.com → New repository → name it `gtaa-momentum` → Create
2. Upload all files (drag and drop works): `app.py`, `requirements.txt`, `Procfile`, and the `templates/` folder with `index.html` inside it

### Step 2 — Deploy on Railway
1. Go to railway.app → Sign up with your GitHub account
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `gtaa-momentum`
4. Railway auto-detects Python and deploys. Takes ~2 minutes.
5. Click **Settings** → **Networking** → **Generate Domain**
6. You'll get a URL like: `https://gtaa-momentum-production.up.railway.app`

### Step 3 — Add to iPhone Home Screen
1. Open that URL in Safari on your iPhone
2. Tap the **Share** button (box with arrow)
3. Tap **Add to Home Screen**
4. Name it "GTAA" → Add
5. It now opens like a native app, full screen, no browser chrome

---

## How the app works
- Hit the URL → it fetches live data from Yahoo Finance and ranks ETFs
- First load takes ~20–30 seconds (downloading ~700 days of price data for 75 ETFs)
- The **TIP signal** tells you if the strategy is in "market on" or "go to cash" mode
- **Trend OK** = OLS slope is positive over the last 30 days
- **Weak Slope** = momentum score is good but recent trend line is declining (use caution)

---

## Free tier limits (Railway)
- $5/month free credit — more than enough for personal use
- App sleeps after 30 min of inactivity; first visit after sleep takes ~5 seconds to wake

---

## Notes
- Data comes from Yahoo Finance (free, no API key needed)
- The ETF list is hardcoded in `app.py` — edit the `ETF_LIST` variable to add/remove tickers
- The momentum formula matches Russell's original: ret20 + ret60 + ret120
- The timeout is set to 120 seconds to handle Yahoo Finance's slower responses
