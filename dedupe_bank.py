"""
Remove questões repetidas dos bancos e sincroniza as contagens.

Repetição é medida pelo enunciado normalizado: é o que o usuário percebe como
"já vi essa questão". Mantém a primeira ocorrência (ordem do manifest) e
atualiza `manifest.json.count` e `exams.json.bankCount`.

Uso:
    python dedupe_bank.py --dry-run
    python dedupe_bank.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def norm(text: str) -> str:
    # ignora pontuação/caixa/espaços para pegar variações triviais do mesmo enunciado
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def dedupe_exam(exam_dir: Path, dry_run: bool) -> tuple[int, int]:
    manifest_path = exam_dir / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = manifest.get("files", [])

    seen: set[str] = set()
    removed_total = 0
    kept_total = 0

    for name in files:
        path = exam_dir / "questions-pt" / name
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        kept = []
        for q in data:
            key = norm(q.get("pregunta", ""))
            if key and key in seen:
                removed_total += 1
                continue
            seen.add(key)
            kept.append(q)
        kept_total += len(kept)
        if len(kept) != len(data):
            print(f"  {name}: {len(data)} -> {len(kept)}")
            if not dry_run:
                path.write_text(
                    json.dumps(kept, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
                )

    if not dry_run and manifest.get("count") != kept_total:
        manifest["count"] = kept_total
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return removed_total, kept_total


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    catalog_path = ROOT / "exams.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    for exam in catalog.get("exams", []):
        exam_dir = ROOT / exam["path"]
        print(f"\n=== {exam['short']} ===")
        removed, kept = dedupe_exam(exam_dir, dry_run)
        print(f"  removidas: {removed} | restantes: {kept}")
        if not dry_run:
            exam["bankCount"] = kept

    if not dry_run:
        catalog_path.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print("\nexams.json e manifests atualizados.")


if __name__ == "__main__":
    main()
