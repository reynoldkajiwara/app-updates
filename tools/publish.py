#!/usr/bin/env python3
"""Adds a release made by an app's Scripts/release.sh to this site.

Usage: tools/publish.py <folder with release.txt and the zip> "<note 1>" "<note 2>" ...

Copies the zip into <app>/ and puts a new item at the top of <app>/appcast.xml, after checking the
zip's length and EdDSA signature against the app's public key (keys.txt).
"""
import base64, email.utils, html, pathlib, re, shutil, sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

SITE = pathlib.Path(__file__).resolve().parent.parent
BASE_URL = "https://reynoldkajiwara.github.io/app-updates"


def main() -> None:
    folder = pathlib.Path(sys.argv[1])
    notes = sys.argv[2:]
    info = dict(line.split("=", 1) for line in (folder / "release.txt").read_text().splitlines() if "=" in line)
    app, version, build = info["app"], info["version"], info["build"]
    slug = app.lower()
    zip_path = folder / info["zip"]
    data = zip_path.read_bytes()
    signature = re.search(r'edSignature="([^"]+)"', info["signature"]).group(1)
    length = int(re.search(r'length="(\d+)"', info["signature"]).group(1))
    if len(data) != length:
        sys.exit(f"Length mismatch: zip is {len(data)} bytes, signature says {length}")

    keys = dict(line.split("=", 1) for line in (SITE / "keys.txt").read_text().splitlines() if "=" in line)
    Ed25519PublicKey.from_public_bytes(base64.b64decode(keys[slug])).verify(base64.b64decode(signature), data)

    appcast = SITE / slug / "appcast.xml"
    text = appcast.read_text()
    if f"<sparkle:version>{build}</sparkle:version>" in text:
        sys.exit(f"Build {build} is already published; every release needs a higher build number")

    shutil.copyfile(zip_path, SITE / slug / zip_path.name)
    notes_html = "".join(f"<li>{html.escape(n)}</li>" for n in notes) or "<li>Improvements and fixes</li>"
    item = f"""    <item>
      <title>{app} {version}</title>
      <pubDate>{email.utils.formatdate(usegmt=True)}</pubDate>
      <sparkle:version>{build}</sparkle:version>
      <sparkle:shortVersionString>{version}</sparkle:shortVersionString>
      <sparkle:minimumSystemVersion>{info["minimumSystemVersion"]}</sparkle:minimumSystemVersion>
      <description><![CDATA[<ul>{notes_html}</ul>]]></description>
      <enclosure url="{BASE_URL}/{slug}/{zip_path.name}" type="application/octet-stream" sparkle:edSignature="{signature}" length="{length}"/>
    </item>
"""
    marker = "    <language>en</language>\n"
    appcast.write_text(text.replace(marker, marker + item, 1))
    print(f"Published {app} {version} (build {build}), signature checked")


if __name__ == "__main__":
    main()
