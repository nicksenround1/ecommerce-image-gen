import os
import base64
from pathlib import Path


def save_image_bytes(image_bytes: bytes, output_path: str) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(image_bytes)
    return output_path


def image_to_base64(image_path: str) -> tuple[str, str]:
    """Returns (base64_data, media_type)"""
    with open(image_path, "rb") as f:
        data = base64.standard_b64encode(f.read()).decode("utf-8")
    ext = image_path.split(".")[-1].lower()
    media_type = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    return data, media_type


def confirm(prompt: str) -> bool:
    while True:
        answer = input(f"\n{prompt} [y/n]: ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
