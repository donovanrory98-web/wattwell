# Wattwell

The live website is everything in `site/`. Netlify publishes it automatically whenever `main` changes (settings in `netlify.toml`).

- `site/`: the published pages
- `tools/check_site.py`: quality check that runs on every push (titles, descriptions, broken links)
- `tools/indexnow.py`: tells Bing which pages changed
