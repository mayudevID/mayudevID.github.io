#!/usr/bin/env python3
"""Archive the GOT Agency, KTADBRNR and EMCare Google Play screenshots locally."""
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = (
    "_data/got_agency_screenshots.json",
    "_data/ktadbrnr_screenshots.json",
    "_data/emcare_screenshots.json",
)
IMAGE_TYPES = {
    "image/jpeg": (".jpg", b"\xff\xd8\xff"),
    "image/png": (".png", b"\x89PNG\r\n\x1a\n"),
    "image/webp": (".webp", b"RIFF"),
}


def main():
    for data_file in DATA_FILES:
        metadata_path = ROOT / data_file
        shots = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata_changed = False
        for shot in shots:
            destination = ROOT / shot["local_path"].lstrip("/")
            if destination.is_file():
                print(f"Already present: {destination.relative_to(ROOT)}")
                continue
            request = Request(shot["url"], headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=30) as response:
                content_type = response.headers.get_content_type()
                data = response.read(10_000_001)
            if len(data) > 10_000_000:
                raise ValueError(f"Screenshot exceeds size limit: {shot['url']}")
            image_type = IMAGE_TYPES.get(content_type)
            if image_type is None or not data.startswith(image_type[1]):
                raise ValueError(f"Unsupported screenshot format ({content_type}): {shot['url']}")
            if content_type == "image/webp" and data[8:12] != b"WEBP":
                raise ValueError(f"Invalid WebP screenshot: {shot['url']}")
            destination = destination.with_suffix(image_type[0])
            local_path = "/" + destination.relative_to(ROOT).as_posix()
            if shot["local_path"] != local_path:
                shot["local_path"] = local_path
                metadata_changed = True
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary = destination.with_suffix(".tmp")
            temporary.write_bytes(data)
            temporary.replace(destination)
            print(f"Archived: {destination.relative_to(ROOT)}")
        if metadata_changed:
            metadata_path.write_text(json.dumps(shots, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
