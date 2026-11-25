"""Quality check on every push: titles, descriptions and internal links.
Prints problems; exits 1 if any page breaks a hard rule so the commit shows a red cross."""
import html as H, os, posixpath, re, sys
root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "site"))
pages, files = {}, set()
for d, _, fs in os.walk(root):
    for f in fs:
        rel = os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
        files.add(rel)
        if f.endswith(".html"):
            pages[rel] = open(os.path.join(d, f), encoding="utf-8", errors="ignore").read()
def exists(page, href):
    h = href.split("#")[0].split("?")[0]
    if "'+" in h or "+'" in h: return True
    if not h or h.startswith(("http:", "https:", "//", "mailto:", "tel:", "data:", "javascript:", "/api/", "/.netlify/")):
        return True
    p = h.lstrip("/") if h.startswith("/") else posixpath.normpath(posixpath.join(posixpath.dirname(page), h))
    if p in (".", ""): p = "index.html"
    p = p.rstrip("/")
    return any(c in files for c in (p, p + ".html", p + "/index.html")) or p == ""
def attr(tag, name):
    m = re.search(name + r'="([^"]*)"', tag)
    return m.group(1) if m else None
errs, warns = [], []
for rel, html in pages.items():
    if rel.startswith("404") or re.match(r"google[0-9a-f]+\.html$", rel): continue
    if re.search(r'<meta[^>]*name="robots"[^>]*noindex', html): continue
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    desc = None
    for tag in re.findall(r"<meta[^>]+>", html):
        if attr(tag, "name") == "description": desc = attr(tag, "content") or ""
    if not t: errs.append(f"{rel}: no <title>")
    elif len(H.unescape(t.group(1).strip())) > 62: warns.append(f"{rel}: title {len(H.unescape(t.group(1).strip()))} chars")
    if desc is None: errs.append(f"{rel}: no meta description")
    elif len(H.unescape(desc)) > 160: warns.append(f"{rel}: description {len(H.unescape(desc))} chars")
    for href in re.findall(r'(?:href|src)="([^"]+)"', html):
        if not exists(rel, href): errs.append(f"{rel}: broken link {href}")
print(f"{len(pages)} pages checked, {len(errs)} errors, {len(warns)} warnings")
for w in warns[:50]: print("WARN", w)
for e in errs[:200]: print("ERROR", e)
sys.exit(1 if errs else 0)
