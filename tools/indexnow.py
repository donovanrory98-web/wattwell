"""Tell Bing (and the search tools built on it) which pages changed in the last push.
Runs from GitHub Actions. Reads changed file paths on stdin. Google does not use IndexNow;
it re-reads sitemap.xml on its own."""
import json, os, sys, urllib.request
host = os.environ.get("SITE_HOST", "").strip()
key = open(os.path.join(os.path.dirname(__file__), "indexnow_key")).read().strip()
if not host:
    print("SITE_HOST not set; skipping IndexNow."); sys.exit(0)
urls = []
for line in sys.stdin:
    p = line.strip()
    if not p.startswith("site/") or not p.endswith(".html"):
        continue
    path = p[len("site/"):]
    if path.endswith("index.html"):
        path = path[: -len("index.html")]
    elif path.endswith(".html"):
        path = path[: -len(".html")]
    urls.append(f"https://{host}/{path}")
if not urls:
    print("No changed pages."); sys.exit(0)
body = json.dumps({"host": host, "key": key, "keyLocation": f"https://{host}/{key}.txt", "urlList": urls[:10000]}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, len(urls), "URLs")
except Exception as e:  # never fail the workflow over a ping
    print("IndexNow ping failed:", e)
