"""Maintainer-only: vendor the pinned Swagger UI bundle; normal startup is offline."""
import hashlib
import io
import json
import tarfile
import urllib.request
from pathlib import Path

VERSION = "5.34.1"
ROOT = Path(__file__).resolve().parents[1]
url = f"https://registry.npmjs.org/swagger-ui-dist/-/swagger-ui-dist-{VERSION}.tgz"
archive = urllib.request.urlopen(url, timeout=30).read()
folder = ROOT / "backend" / "static"
folder.mkdir(exist_ok=True)
manifest = {"package": "swagger-ui-dist", "version": VERSION, "source": url, "files": {}}
with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
    for filename in ["swagger-ui-bundle.js", "swagger-ui.css", "LICENSE", "NOTICE"]:
        try:
            data = tar.extractfile("package/" + filename).read()
        except KeyError:
            continue
        (folder / filename).write_bytes(data)
        manifest["files"][filename] = hashlib.sha256(data).hexdigest()
(folder / "vendor-manifest.json").write_text(json.dumps(manifest, indent=2))
print(f"Vendored Swagger UI {VERSION}; {len(manifest['files'])} files.")
