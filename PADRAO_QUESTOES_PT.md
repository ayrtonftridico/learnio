# Padrão de questões PT-BR (`questions-pt/`)

Schema compatível com o quiz central (`quiz.html`):

```json
[
  {
    "pregunta": "Enunciado em PT-BR",
    "opciones": [
      { "texto_opcion": "...", "es_correcta": true,  "explicacion": "..." },
      { "texto_opcion": "...", "es_correcta": false, "explicacion": "..." },
      { "texto_opcion": "...", "es_correcta": false, "explicacion": "..." },
      { "texto_opcion": "...", "es_correcta": false, "explicacion": "..." }
    ],
    "tags": ["1.1", "Rótulo curto"]
  }
]
```

- 4 alternativas, exatamente 1 correta, explicação em todas
- PT-BR no texto corrido; **termos oficiais do produto/prova em inglês**
- Um arquivo por subtema (`1.1.json`, …) listado em `manifest.json`
- Alternativa correta sem ser sistematicamente a mais longa

## Glossário — manter em inglês

Traduzir esses termos prejudica o estudo (a prova e a UI usam o inglês):

| Manter | Evitar |
|---|---|
| job cluster / job clusters | cluster de tarefas / empregos / trabalhos |
| all-purpose cluster(s) | cluster multifuncional / para todos os fins |
| Jobs compute | computação de trabalhos |
| serverless compute | Serverless computar / computação serverless (como nome do produto) |
| workspace / workspaces | espaço(s) de trabalho |
| Unity Catalog, Delta Lake, Auto Loader, Photon, … | traduções literais |
| chaves YAML (`targets`, `host`, `job_clusters`, `run_as`, …) | `alvos`, `anfitrião`, `clusters_de_trabalho`, … |

Nomes de APIs, privilégios (`SELECT`, `BROWSE`), paths e chaves YAML (`workspace:`, `host:`) também ficam em inglês.

## Correção em lote

Se o Google Translate vazar de novo:

```bash
python fix_pt_terms.py
```
