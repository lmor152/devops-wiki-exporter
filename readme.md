# Wiki Exporter

Use this to export your DevOps wikis to a single HTML file

1. Clone this repo
1. Create virtual environment:
   - `python -m venv env`
   - `source env/bin/activate` (MacOS/Linux)  
       or   
   `env/scripts/activate` (windows)
1. `pip install -r requirements.txt`
1. Clone your DevOps wiki to a directory within this repo
2. Run `python wikiexporter.py wikiname.wiki`
3. Export will appear as export.html in the root folder by default

