"""
Traduz questions/*.json (EN) -> questions-pt/*.json (PT-BR) em lotes.
Mantém o schema do quiz.html.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "questions"
DST = ROOT / "questions-pt"
CACHE_PATH = ROOT / ".translate_cache_pt.json"
SEP = "\n⟦§⟧\n"
MAX_CHARS = 3500  # margem sob o limite do Google

PROTECT = sorted(
    {
        "Databricks Asset Bundles",
        "Declarative Automation Bundles",
        "Lakeflow Connect",
        "Lakeflow Jobs",
        "Unity Catalog",
        "Delta Lake",
        "Delta Sharing",
        "Auto Loader",
        "COPY INTO",
        "MERGE INTO",
        "DESCRIBE HISTORY",
        "VACUUM",
        "OPTIMIZE",
        "Z-ORDER",
        "Liquid Clustering",
        "Predictive Optimization",
        "Photon",
        "Spark UI",
        "Databricks Runtime",
        "SQL warehouse",
        "SQL Warehouse",
        "Medallion Architecture",
        "materialized view",
        "Materialized View",
        "streaming table",
        "Streaming Table",
        "cloudFiles",
        "DynamicFrame",
        "DataFrame",
        "broadcast join",
        "shuffle.partitions",
        "autoBroadcastJoinThreshold",
        "approx_count_distinct",
        "dropDuplicates",
        "Catalog Explorer",
        "information_schema",
        "Lakehouse",
        "Git Folders",
        "Repos",
        "DABs",
        "JDBC",
        "ODBC",
        "ADLS",
        "ACID",
        "DAG",
        "CI/CD",
        "GRANT",
        "REVOKE",
        "DENY",
        "ABAC",
        # Termos oficiais — não traduzir (aparecem na prova em inglês)
        "all-purpose clusters",
        "all-purpose cluster",
        "job clusters",
        "job cluster",
        "Jobs clusters",
        "Jobs cluster",
        "Jobs compute",
        "serverless compute",
        "Serverless compute",
        "Serverless",
        "serverless",
        "workspace",
        "Workspace",
        "workspaces",
        "Workspaces",
        "init scripts",
        "cluster libraries",
        "requirements.txt",
    },
    key=len,
    reverse=True,
)

translator = GoogleTranslator(source="en", target="pt")


def load_cache() -> dict[str, str]:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


def protect_terms(text: str) -> tuple[str, list[str]]:
    held: list[str] = []

    def repl(match: re.Match[str]) -> str:
        held.append(match.group(0))
        return f"⟦T{len(held) - 1}⟧"

    pattern = "|".join(re.escape(t) for t in PROTECT)
    return re.sub(pattern, repl, text, flags=re.IGNORECASE), held


def restore_terms(text: str, held: list[str]) -> str:
    out = text
    for i, term in enumerate(held):
        for marker in (f"⟦T{i}⟧", f"[T{i}]", f"(T{i})"):
            if marker in out:
                out = out.replace(marker, term)
                break
    return out


def polish_ptbr(text: str) -> str:
    # PT-PT -> PT-BR + desfazer traduções literais de termos oficiais
    reps = [
        ("ficheiro", "arquivo"),
        ("Ficheiro", "Arquivo"),
        ("utilizador", "usuário"),
        ("Utilizador", "Usuário"),
        ("controlo", "controle"),
        ("Controlo", "Controle"),
        ("ecrã", "tela"),
        ("secção", "seção"),
        ("secções", "seções"),
        ("registo", "registro"),
        ("registos", "registros"),
        ("contacto", "contato"),
        ("equipa", "equipe"),
        ("clusters de computação de trabalhos", "job clusters"),
        ("cluster de computação de trabalhos", "job cluster"),
        ("computação de trabalhos", "Jobs compute"),
        ("clusters de tarefas", "job clusters"),
        ("cluster de tarefas", "job cluster"),
        ("Clusters de tarefas", "Job clusters"),
        ("Cluster de tarefas", "Job cluster"),
        ("clusters de empregos", "job clusters"),
        ("cluster de empregos", "job cluster"),
        ("Clusters de empregos", "Job clusters"),
        ("Cluster de empregos", "Job cluster"),
        ("clusters de trabalhos", "job clusters"),
        ("cluster de trabalhos", "job cluster"),
        ("Clusters de trabalhos", "Job clusters"),
        ("Cluster de trabalhos", "Job cluster"),
        ("clusters de jobs", "job clusters"),
        ("cluster de jobs", "job cluster"),
        ("cluster do trabalho", "job cluster"),
        ("Clusters multifuncionais", "All-purpose clusters"),
        ("Cluster multifuncional", "All-purpose cluster"),
        ("clusters multifuncionais", "all-purpose clusters"),
        ("cluster multifuncional", "all-purpose cluster"),
        ("clusters multiuso", "all-purpose clusters"),
        ("cluster multiuso", "all-purpose cluster"),
        ("clusters para todos os fins", "all-purpose clusters"),
        ("cluster para todos os fins", "all-purpose cluster"),
        ("Serverless computar", "Serverless compute"),
        ("serverless computar", "serverless compute"),
        ("computação Serverless", "serverless compute"),
        ("computação serverless", "serverless compute"),
        ("SKU de empregos serverless", "Jobs serverless SKU"),
        ("IU de empregos", "Jobs UI"),
        ("IU de trabalhos", "Jobs UI"),
        ("IU de tarefas", "Jobs UI"),
        ("lista de empregos", "lista de Jobs"),
        ("Espaços de trabalho", "Workspaces"),
        ("espaços de trabalho", "workspaces"),
        ("Espaço de trabalho", "Workspace"),
        ("espaço de trabalho", "workspace"),
        ("usuárioes", "usuários"),
        ("asalvar", "aguardar"),
        ("alvos:", "targets:"),
        ("padrão: verdadeiro", "default: true"),
        ("padrão: falso", "default: false"),
        ("modo: desenvolvimento", "mode: development"),
        ("modo: produção", "mode: production"),
        ("clusters_de_trabalho:", "job_clusters:"),
        ("novo_cluster:", "new_cluster:"),
        ("executar_as:", "run_as:"),
        ("nome_principal_serviço:", "service_principal_name:"),
        ("  desenvolvedor:\n", "  dev:\n"),
        ("  estímulo:\n", "  prod:\n"),
        ("recursos:\n  empregos:", "resources:\n  jobs:"),
    ]
    for a, b in reps:
        text = text.replace(a, b)
    # "guardar" sem quebrar "aguardar"
    text = re.sub(r"(?<![Aa])guardar", "salvar", text)
    text = re.sub(r"(?<![Aa])Guardar", "Salvar", text)
    return text


def translate_raw(text: str) -> str:
    for attempts in range(1, 8):
        try:
            return translator.translate(text) or text
        except Exception as exc:  # noqa: BLE001
            wait = min(2**attempts, 45)
            print(f"  retry {attempts}: {exc} (wait {wait}s)")
            time.sleep(wait)
    return text


def translate_one(text: str) -> str:
    protected, held = protect_terms(text)
    return polish_ptbr(restore_terms(translate_raw(protected), held))


def make_batches(items: list[str]) -> list[list[str]]:
    batches: list[list[str]] = []
    cur: list[str] = []
    size = 0
    for s in items:
        # strings longas sozinhas
        if len(s) > MAX_CHARS:
            if cur:
                batches.append(cur)
                cur, size = [], 0
            batches.append([s])
            continue
        add = len(s) + len(SEP)
        if cur and size + add > MAX_CHARS:
            batches.append(cur)
            cur, size = [], 0
        cur.append(s)
        size += add
    if cur:
        batches.append(cur)
    return batches


def collect_strings(files: list[Path]) -> set[str]:
    needed: set[str] = set()
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            data = [data]
        for q in data:
            needed.add(q.get("pregunta", ""))
            for op in q.get("opciones", []):
                needed.add(op.get("texto_opcion", ""))
                needed.add(op.get("explicacion", ""))
            for t in q.get("tags", []):
                s = str(t)
                if not re.fullmatch(r"\d+(\.\d+)?", s):
                    needed.add(s)
    needed.discard("")
    return needed


def apply_file(path: Path, cache: dict[str, str]) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        data = [data]
    out = []
    for q in data:
        tags = []
        for t in q.get("tags", []):
            s = str(t)
            if re.fullmatch(r"\d+(\.\d+)?", s):
                tags.append(s)
            else:
                tags.append(cache.get(s, s))
        out.append(
            {
                "pregunta": cache.get(q.get("pregunta", ""), q.get("pregunta", "")),
                "opciones": [
                    {
                        "texto_opcion": cache.get(
                            op.get("texto_opcion", ""), op.get("texto_opcion", "")
                        ),
                        "es_correcta": op.get("es_correcta", False),
                        "explicacion": cache.get(
                            op.get("explicacion", ""), op.get("explicacion", "")
                        ),
                    }
                    for op in q.get("opciones", [])
                ],
                "tags": tags,
            }
        )
    return out


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    files = sorted(SRC.glob("*.json"))
    cache = load_cache()

    print("Coletando strings únicas...")
    needed = collect_strings(files)
    missing = [s for s in needed if s not in cache]
    print(
        f"Únicas: {len(needed)} | cache: {len(needed) - len(missing)} | faltam: {len(missing)}"
    )

    batches = make_batches(missing)
    print(f"Lotes: {len(batches)}")

    for bi, batch in enumerate(batches, 1):
        if len(batch) == 1:
            cache[batch[0]] = translate_one(batch[0])
        else:
            # proteger cada item, juntar, traduzir, separar
            packed_parts = []
            helds = []
            for s in batch:
                p, h = protect_terms(s)
                packed_parts.append(p)
                helds.append(h)
            packed = SEP.join(packed_parts)
            translated_pack = translate_raw(packed)
            # restaurar separador se o Google alterou
            parts = translated_pack.split(SEP)
            if len(parts) != len(batch):
                # fallback: uma a uma
                print(f"  lote {bi}: split falhou ({len(parts)}!={len(batch)}); fallback")
                for s in batch:
                    cache[s] = translate_one(s)
                    time.sleep(0.05)
            else:
                for s, part, held in zip(batch, parts, helds):
                    cache[s] = polish_ptbr(restore_terms(part.strip(), held))

        if bi % 5 == 0 or bi == len(batches):
            save_cache(cache)
            print(f"  lotes {bi}/{len(batches)} | cache={len(cache)}")
        time.sleep(0.25)

    save_cache(cache)
    print("Gerando JSONs em questions-pt/...")
    total_q = 0
    for path in files:
        translated = apply_file(path, cache)
        (DST / path.name).write_text(
            json.dumps(translated, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        total_q += len(translated)
        print(f"  OK {path.name} ({len(translated)})")

    print(f"\nConcluído: {len(files)} arquivos, {total_q} questões -> {DST}")


if __name__ == "__main__":
    main()
