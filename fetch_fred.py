#!/usr/bin/env python3
"""
Credit Watch — FRED data fetcher (runs in GitHub Actions, server-side).
No CORS, no external libs (stdlib only). Writes ./data.json for the dashboard.
Requires env var FRED_API_KEY (set as a GitHub Actions secret).
"""
import json, os, sys, datetime, urllib.request, urllib.parse

FRED_KEY = os.environ.get("FRED_API_KEY", "").strip()
if not FRED_KEY:
    print("ERROR: FRED_API_KEY not set", file=sys.stderr)
    sys.exit(1)

# dashboard key -> (FRED series id, momentum window in observations)
SERIES = {
    "hy":    ("BAMLH0A0HYM2", 21),   # HY OAS            (daily)
    "ig":    ("BAMLC0A0CM",   21),   # IG OAS            (daily)
    "bbb":   ("BAMLC0A4CBBB", 21),   # BBB OAS           (daily)
    "ccc":   ("BAMLH0A3HYC",  21),   # CCC & lower OAS   (daily)
    "baa":   ("BAA10Y",       21),   # Baa - 10Y         (daily)
    "nfci":  ("NFCI",          4),   # Chicago Fed NFCI  (weekly)
    "stl":   ("STLFSI4",       4),   # StL stress index  (weekly)
    "vix":   ("VIXCLS",       21),   # VIX               (daily)
    "curve": ("T10Y2Y",       21),   # 10Y - 2Y          (daily)
    "spx":   ("SP500",        21),   # S&P 500           (daily) -> divergence
}

START = (datetime.date.today() - datetime.timedelta(days=5 * 365 + 30)).isoformat()


def fetch_fred(series_id):
    q = urllib.parse.urlencode({
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json",
        "observation_start": START,
        "sort_order": "asc",
    })
    url = f"https://api.stlouisfed.org/fred/series/observations?{q}"
    req = urllib.request.Request(url, headers={"User-Agent": "credit-watch/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    points = []
    for o in payload.get("observations", []):
        v = o.get("value", ".")
        if v in (".", "", None):
            continue
        try:
            points.append({"d": o["date"], "v": float(v)})
        except ValueError:
            continue
    return points


def fetch_move():
    """MOVE bond-vol index via Yahoo (unofficial). Optional; fails gracefully."""
    try:
        url = ("https://query1.finance.yahoo.com/v8/finance/chart/"
               "%5EMOVE?range=5y&interval=1d")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            d = json.load(r)
        res = d["chart"]["result"][0]
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
        if len(closes) >= 1:
            return round(closes[-1], 1)
    except Exception as e:
        print(f"MOVE fetch skipped: {e}", file=sys.stderr)
    return None


out = {
    "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    "series": {},
    "move": None,
}

ok = 0
for key, (sid, win) in SERIES.items():
    try:
        pts = fetch_fred(sid)
        if len(pts) < 2:
            print(f"WARN {key} ({sid}): only {len(pts)} points", file=sys.stderr)
            continue
        last = pts[-1]["v"]
        idx = max(0, len(pts) - 1 - win)
        prev = pts[idx]["v"]
        out["series"][key] = {"last": last, "prev": prev, "points": pts}
        ok += 1
    except Exception as e:
        print(f"ERROR {key} ({sid}): {e}", file=sys.stderr)

out["move"] = fetch_move()

if ok < 5:
    print(f"ERROR: only {ok} series fetched, aborting (data.json not written)", file=sys.stderr)
    sys.exit(1)

with open("data.json", "w") as f:
    json.dump(out, f, separators=(",", ":"))

print(f"Wrote data.json: {ok} series, move={out['move']}, generated={out['generated']}")
