"""Build a runnable Python distribution; static-only hosting cannot run the API."""
from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
out=root/'dist'
if out.exists():shutil.rmtree(out)
out.mkdir()
for name in ('index.html','ar.html','ksp.html','integrations','sw.js','manifest.webmanifest','src','public','docs','mars','server.py','README.md'):
    source=root/name
    if source.is_dir():shutil.copytree(source,out/name,ignore=shutil.ignore_patterns('__pycache__'))
    else:shutil.copy2(source,out/name)
print('Python application built in dist/. Run: cd dist && python3 server.py')
