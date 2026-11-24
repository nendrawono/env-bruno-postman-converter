#!/usr/bin/env python3
"""
WONO-COLLECTION Environment Converter
Konversi dua arah antara Bruno Environment (.bru) dan Postman Environment (.postman_environment.json).
Menggunakan Python Standard Library tanpa dependency eksternal.
"""

import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def parse_bru_environment(bru_path: Path) -> tuple[str, list[dict]]:
    """Membaca file .bru environment dan mengekstrak daftar variabel dari blok vars & vars:secret."""
    content = bru_path.read_text(encoding="utf-8-sig")
    env_name = bru_path.stem
    variables: list[dict] = []
    seen_keys: set[str] = set()

    vars_blocks = re.findall(r"(?m)^\s*vars\s*\{([\s\S]*?)^\s*\}", content)
    for block in vars_blocks:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            if len(val) >= 2 and ((val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")):
                val = val[1:-1]
            if key and key not in seen_keys:
                seen_keys.add(key)
                variables.append({
                    "key": key,
                    "value": val,
                    "type": "default",
                    "enabled": True,
                })

    secret_blocks = re.findall(r"(?m)^\s*vars:secret\s*\[([\s\S]*?)^\s*\]", content)
    for block in secret_blocks:
        for item in re.split(r"[,\n]", block):
            key = item.strip()
            if not key or key.startswith("//") or key.startswith("#"):
                continue
            if key not in seen_keys:
                seen_keys.add(key)
                variables.append({
                    "key": key,
                    "value": "",
                    "type": "secret",
                    "enabled": True,
                })

    return env_name, variables


def convert_bru_to_postman(input_file: Path) -> Path:
    """Konversi file .bru ke .postman_environment.json di direktori yang sama."""
    if input_file.suffix.lower() != ".bru":
        raise ValueError(f"File input harus berekstensi .bru (ditemukan: '{input_file.suffix}').")

    env_name, values = parse_bru_environment(input_file)

    postman_payload = {
        "id": str(uuid.uuid4()),
        "name": env_name,
        "values": values,
        "_postman_variable_scope": "environment",
        "_postman_exported_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "_postman_exported_using": "WONO-COLLECTION Python Converter",
    }

    output_file = input_file.parent / f"{env_name}-WONCONV.postman_environment.json"
    output_file.write_text(
        json.dumps(postman_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_file


def convert_postman_to_bru(input_file: Path) -> Path:
    """Konversi file .postman_environment.json (atau .json) ke .bru di direktori yang sama."""
    if input_file.suffix.lower() != ".json":
        raise ValueError(f"File input harus berekstensi .json (ditemukan: '{input_file.suffix}').")

    raw_text = input_file.read_text(encoding="utf-8-sig")
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Format JSON tidak valid: {exc}") from exc

    if not isinstance(data, dict) or "values" not in data or not isinstance(data["values"], list):
        raise ValueError(
            "File JSON bukan skema Postman Environment yang valid (tidak ditemukan array 'values')."
        )

    env_name = str(data.get("name") or "").strip()
    if not env_name:
        stem = input_file.stem
        env_name = stem[:-20] if stem.endswith(".postman_environment") else stem

    normal_vars: list[tuple[str, str]] = []
    secret_vars: list[str] = []

    for item in data["values"]:
        if not isinstance(item, dict):
            continue
        if item.get("enabled") is False:
            continue
        key = str(item.get("key") or "").strip()
        if not key:
            continue
        val = "" if item.get("value") is None else str(item.get("value"))
        var_type = str(item.get("type") or "default").lower()

        if var_type == "secret" and val == "":
            secret_vars.append(key)
        else:
            normal_vars.append((key, val))

    lines: list[str] = ["vars {"]
    for key, val in normal_vars:
        lines.append(f"  {key}: {val}" if val != "" else f"  {key}: ")
    lines.append("}")

    if secret_vars:
        lines.append("vars:secret [")
        for idx, skey in enumerate(secret_vars):
            comma = "," if idx < len(secret_vars) - 1 else ""
            lines.append(f"  {skey}{comma}")
        lines.append("]")

    # Pastikan nama file bersih dari karakter ilegal OS
    safe_name = re.sub(r'[<>:"/\\|?*]+', "_", env_name).strip() or "environment"
    output_file = input_file.parent / f"{safe_name}-WONCONV.bru"
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_file


def clean_user_path(raw_input: str) -> Path:
    """Membersihkan tanda kutip jika user drag-and-drop atau copy path file ke terminal."""
    cleaned = raw_input.strip()
    if len(cleaned) >= 2 and (
        (cleaned[0] == '"' and cleaned[-1] == '"')
        or (cleaned[0] == "'" and cleaned[-1] == "'")
    ):
        cleaned = cleaned[1:-1].strip()
    return Path(cleaned).expanduser()


def main() -> None:
    print("=" * 60)
    print("  WONO-COLLECTION Environment Converter (Bruno <-> Postman)")
    print("=" * 60)
    print("Pilih mode konversi:")
    print("  [1] Bruno Environment (.bru)  -->  Postman (.postman_environment.json)")
    print("  [2] Postman (.postman_environment.json)  -->  Bruno Environment (.bru)")
    print("  [0] Keluar")
    print("-" * 60)

    choice = input("Masukkan pilihan Anda (1/2/0): ").strip()
    if choice == "0":
        print("Keluar dari program.")
        sys.exit(0)

    if choice not in {"1", "2"}:
        print("[ERROR] Pilihan tidak valid. Jalankan ulang dan pilih 1 atau 2.")
        sys.exit(1)

    if choice == "1":
        prompt_text = "Masukkan full path file environment Bruno (.bru): "
    else:
        prompt_text = "Masukkan full path file Postman environment (.postman_environment.json): "

    raw_path = input(prompt_text)
    if not raw_path.strip():
        print("[ERROR] Path file tidak boleh kosong.")
        sys.exit(1)

    input_path = clean_user_path(raw_path)

    if not input_path.exists() or not input_path.is_file():
        print(f"[ERROR] File tidak ditemukan: {input_path}")
        sys.exit(1)

    try:
        if choice == "1":
            out_path = convert_bru_to_postman(input_path)
        else:
            out_path = convert_postman_to_bru(input_path)
    except Exception as exc:
        print(f"[ERROR] Gagal melakukan konversi: {exc}")
        sys.exit(1)

    print("-" * 60)
    print("[SUKSES] Konversi berhasil!")
    print(f"File Input  : {input_path.resolve()}")
    print(f"File Output : {out_path.resolve()}")
    print("-" * 60)


if __name__ == "__main__":
    main()
