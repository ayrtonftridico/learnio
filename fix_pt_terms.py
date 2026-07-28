"""
Normaliza a terminologia dos bancos PT-BR (`*/questions-pt/*.json`).

Objetivo: texto corrido em PT-BR, mas termos oficiais de produto e jargão de
prova em inglês (job cluster, workspace, shuffle, checkpoint, bundle...).
Traduzir esses termos atrapalha o estudo, porque a prova e a UI usam o inglês.

Uso:
    python fix_pt_terms.py            # aplica nos bancos
    python fix_pt_terms.py --dry-run  # só relata o que mudaria
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Expressões em que "trabalho" NÃO é "job" e precisam sobreviver às regras gerais.
KEEP = [
    "cargas de trabalho",
    "carga de trabalho",
    "trabalho colaborativo",
    "trabalho interativo",
    "trabalho útil",
    "trabalho em equipe",
    "trabalho manual",
    "trabalho pesado",
    "ambiente de trabalho",
    "ordem aleatória",
    "amostra aleatória",
    "amostragem aleatória",
    "pasta de lixo",
    "diretório de lixo",
]

# Substituições literais, das frases mais longas para as mais curtas.
REPLACEMENTS: list[tuple[str, str]] = [
    # --- compute ---
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
    ("SKU de jobs serverless", "Jobs serverless SKU"),
    ("tempos de execução mais antigos", "runtimes mais antigos"),
    ("tempos de execução", "runtimes"),
    # --- workspace / UI ---
    ("Espaços de trabalho", "Workspaces"),
    ("espaços de trabalho", "workspaces"),
    ("Espaço de trabalho", "Workspace"),
    ("espaço de trabalho", "workspace"),
    ("Fluxos de trabalho", "Workflows"),
    ("fluxos de trabalho", "workflows"),
    ("Fluxo de trabalho", "Workflow"),
    ("fluxo de trabalho", "workflow"),
    ("IU de empregos", "Jobs UI"),
    ("IU de trabalhos", "Jobs UI"),
    ("IU de tarefas", "Jobs UI"),
    ("UI de tarefas", "Jobs UI"),
    ("lista de empregos", "lista de jobs"),
    ("tipo de tarefa Executar Trabalho", "tipo de tarefa Run Job"),
    ("tarefa Executar Trabalho", "tarefa Run Job"),
    # abas da UI ("guia" no sentido de tab). O sentido de "guia do exame" fica intacto.
    ("Guia Estágios", "aba Stages"),
    ("guia Estágios", "aba Stages"),
    ("Guia Estágio", "aba Stage"),
    ("guia Estágio", "aba Stage"),
    ("Guia Executores", "aba Executors"),
    ("guia Executores", "aba Executors"),
    ("Guia Executor", "aba Executors"),
    ("guia Executor", "aba Executors"),
    ("Guia Execuções", "aba Runs"),
    ("guia Execuções", "aba Runs"),
    ("Guia Lakeflow Runs", "aba Lakeflow Runs"),
    ("guia Lakeflow Runs", "aba Lakeflow Runs"),
    ("Guia Métricas", "aba Metrics"),
    ("guia Métricas", "aba Metrics"),
    ("Guia Qualidade de dados", "aba Data quality"),
    ("guia Qualidade de dados", "aba Data quality"),
    ("Guia Qualidade", "aba Quality"),
    ("guia Qualidade", "aba Quality"),
    ("Guia Jobs", "aba Jobs"),
    ("guia Jobs", "aba Jobs"),
    ("Guia SQL", "aba SQL"),
    ("guia SQL", "aba SQL"),
    ("Guia Spark", "aba Spark"),
    ("guia Spark", "aba Spark"),
    ("Guia Storage", "aba Storage"),
    ("guia Storage", "aba Storage"),
    ("guia Armazenamento", "aba Storage"),
    ("Qual guia", "Qual aba"),
    ("qual guia", "qual aba"),
    ("guia do estágio", "aba do estágio"),
    # --- Spark ---
    ("partições aleatórias", "shuffle partitions"),
    ("Partições aleatórias", "Shuffle partitions"),
    ("gravação aleatória", "shuffle write"),
    ("Gravação aleatória", "Shuffle write"),
    ("leitura aleatória", "shuffle read"),
    ("Leitura aleatória", "Shuffle read"),
    ("dados aleatórios", "dados de shuffle"),
    ("dado aleatório", "dado de shuffle"),
    ("saída aleatória", "saída de shuffle"),
    ("arquivos aleatórios", "arquivos de shuffle"),
    ("arquivo aleatório", "arquivo de shuffle"),
    ("operações aleatórias", "operações de shuffle"),
    ("operação aleatória", "operação de shuffle"),
    ("junções aleatórias", "shuffle joins"),
    ("junção aleatória", "shuffle join"),
    ("Junção aleatória", "Shuffle join"),
    ("limite aleatório", "shuffle boundary"),
    ("buffers aleatórios", "buffers de shuffle"),
    ("estágio aleatório", "estágio de shuffle"),
    ("spill aleatório", "spill de shuffle"),
    ("vazamento aleatório", "spill de shuffle"),
    ("contagem aleatória", "contagem de shuffle"),
    ("distribuição aleatória", "distribuição do shuffle"),
    ("embaralhamento", "shuffle"),
    ("derramamento", "spill"),
    ("Derramamento", "Spill"),
    ("coletor de lixo", "garbage collector"),
    ("coleta de lixo", "garbage collection"),
    ("Coleta de lixo", "Garbage collection"),
    ("pontos de verificação", "checkpoints"),
    ("ponto de verificação", "checkpoint"),
    ("Pontos de verificação", "Checkpoints"),
    ("Ponto de verificação", "Checkpoint"),
    ("distorção de dados", "data skew"),
    ("Distorção de dados", "Data skew"),
    ("motorista", "driver"),
    ("Motorista", "Driver"),
    # --- DABs ---
    ("pacotes configuráveis", "bundles"),
    ("pacote configurável", "bundle"),
    ("Pacotes configuráveis", "Bundles"),
    ("Pacote configurável", "Bundle"),
    ("requisitos.txt", "requirements.txt"),
    # --- chaves YAML que o tradutor quebra ---
    ("espaço de trabalho:", "workspace:"),
    ("anfitrião:", "host:"),
    ("Anfitrião:", "host:"),
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
    # --- erros de tradução ---
    ("usuárioes", "usuários"),
    ("Usuárioes", "Usuários"),
    ("asalvar", "aguardar"),
]

# Regras finais: "trabalho(s)" isolado quase sempre é "job(s)" nesses bancos.
REGEX_RULES: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\btrabalhos\b"), "jobs"),
    (re.compile(r"\btrabalho\b"), "job"),
    (re.compile(r"\bTrabalhos\b"), "Jobs"),
    (re.compile(r"\bTrabalho\b"), "Job"),
    (re.compile(r"\bempregos\b"), "jobs"),
    (re.compile(r"\bIU\b"), "UI"),
]


def fix_text(text: str) -> str:
    held: list[str] = []

    def hold(match: re.Match[str]) -> str:
        held.append(match.group(0))
        return f"\x00{len(held) - 1}\x00"

    keep_pattern = re.compile("|".join(re.escape(k) for k in sorted(KEEP, key=len, reverse=True)), re.I)
    out = keep_pattern.sub(hold, text)

    for old, new in REPLACEMENTS:
        out = out.replace(old, new)
    for pattern, new in REGEX_RULES:
        out = pattern.sub(new, out)

    for i, original in enumerate(held):
        out = out.replace(f"\x00{i}\x00", original)
    return out


def fix_obj(obj):
    if isinstance(obj, str):
        return fix_text(obj)
    if isinstance(obj, list):
        return [fix_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: fix_obj(v) for k, v in obj.items()}
    return obj


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    files = sorted(ROOT.glob("*/questions-pt/*.json"))
    changed = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        new_text = json.dumps(fix_obj(json.loads(original)), ensure_ascii=False, indent=2) + "\n"
        if new_text == original:
            continue
        changed += 1
        print(f"{'(dry) ' if dry_run else 'OK '}{path.relative_to(ROOT)}")
        if not dry_run:
            path.write_text(new_text, encoding="utf-8")
    print(f"\nArquivos {'a alterar' if dry_run else 'alterados'}: {changed}/{len(files)}")


if __name__ == "__main__":
    main()
