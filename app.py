"""
GTAA Momentum Strategy - Flask Backend
Author: adapted from Russell Dickerson's GTAA momentum script
"""

from flask import Flask, jsonify, render_template
import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import datetime as dt
import os

app = Flask(__name__)

# ── ETF Universe ──────────────────────────────────────────────────────────────
ETF_LIST = [
    "DIA","SPY","QQQ","MTUM","IWM","ARKK","VNQ","FFTY","IEF","IGOV",
    "IGV","IPO","ITB","IBB","IYT","JETS","KBE","SMH","TAN","VBK",
    "VBR","VCIT","VEA","VWO","VGIT","TLT","VGLT","VT","VTV",
    "FCOM","XLC","FNCL","XLF","FDIS","XLY","FUTY","XLU",
    "XAR","XLB","XLE","XLI","XLK","XLP","XLRE","XLV","XRT","XT",
    "TIP","SCZ","MDY","RSP","FBTC","GLD","SLV","URNM","COPX","REMX",
    "GSG","GCC","XME","USO","FAN","URA","NLR",
    "GREK","EWY","VNM","EPOL","EWJ","EWZ","EZU","MCHI","EWQ","EWG","EWD"
]

def fetch_and_rank(top_n=15):
    now = dt.datetime.now() + dt.timedelta(days=1)
    start = (dt.datetime.now() - dt.timedelta(days=700)).strftime('%Y-%m-%d')

    # Download prices
    prices = yf.download(ETF_LIST, start=start, end=now, auto_adjust=True, progress=False)["Close"]
    prices = prices.bfill().ffill()
    prices.index = pd.to_datetime(prices.index).strftime('%Y-%m-%d')

    # Drop ETFs with too much missing data
    prices = prices.dropna(axis=1, thresh=int(len(prices) * 0.7))

    # Momentum score: 20d + 60d + 120d returns
    ret20  = prices.pct_change(20,  fill_method=None)
    ret60  = prices.pct_change(60,  fill_method=None)
    ret120 = prices.pct_change(120, fill_method=None)
    score  = ret20 + ret60 + ret120

    last_date = prices.index[-1]

    # TIP regime filter
    tip_score = score["TIP"].iloc[-1] if "TIP" in score.columns else 1
    market_on = bool(tip_score >= 0)

    # Top N by momentum score
    today_scores = score.iloc[-1].dropna()
    ranked = today_scores.sort_values(ascending=False)
    top_tickers = ranked.head(top_n).index.tolist()

    # OLS slope filter (30-day linear regression on normalised prices)
    recent = prices[-30:].copy()
    recent = recent / recent.iloc[0]
    dflen  = len(recent)
    x      = np.array(range(dflen))
    x1     = sm.add_constant(x)

    results_list = []
    for ticker in top_tickers:
        if ticker not in recent.columns:
            continue
        y = recent[ticker].interpolate()
        try:
            model   = sm.OLS(y, x1).fit()
            slope   = float(model.params.iloc[1])
        except Exception:
            slope = 0.0

        mom_score = float(ranked[ticker])
        results_list.append({
            "rank":       len(results_list) + 1,
            "ticker":     ticker,
            "momentum":   round(mom_score * 100, 2),   # as %
            "slope":      round(slope, 4),
            "trend_ok":   bool(slope > 0),
        })

    return {
        "as_of":      last_date,
        "market_on":  market_on,
        "tip_signal": round(float(tip_score) * 100, 2),
        "rankings":   results_list,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/rankings")
def rankings():
    try:
        data = fetch_and_rank(top_n=15)
        return jsonify({"status": "ok", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
