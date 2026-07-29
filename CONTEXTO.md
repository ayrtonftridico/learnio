# CONTEXTO — learn.io (método e operação)

Documento de handoff para agentes e humanos. Objetivo: continuar o projeto sem redescobrir decisões.

**Live:** https://ayrtonftridico.github.io/learnio/  
**Repo:** https://github.com/ayrtonftridico/learnio (público)  
**Pasta local típica:** `c:\Users\ayrto\Downloads\learn.io`  
**Idioma do produto:** default **EN**; PT-BR disponível via switch. UI e docs de trabalho em **PT-BR**.

---

## 1. O que é

Site **estático** (HTML/JS/JSON) para treinar certificações de Data Engineering:

- Modo **Practice** (banco completo, progresso no `localStorage`)
- Modo **Mock exam** (amostra do tamanho da prova real + timer)
- Bancos paralelos **EN** (`questions/`) e **PT** (`questions-pt/`)
- Sem backend, sem login, sem analytics obrigatório
- Apoio financeiro (Buy Me a Coffee / PIX) **removido por enquanto**

Não é um LMS. É um hub de quizzes + catálogo.

---

## 2. Arquitetura do site

### Arquivos raiz (publicados)

| Arquivo | Função |
|---------|--------|
| `index.html` | Home: lista provas, filtro por **vendor**, switch EN/PT |
| `quiz.html` | Player do quiz / mock |
| `exams.json` | Catálogo das provas |
| `site-config.js` | Brand, tagline, author |
| `favicon.svg` | Ícone |

### Pasta por exame `{id}/`

```
{id}/
  manifest.json      # lista de arquivos + count
  temario.json       # programa da prova: seções / subtemas / pesos (quando houver)
  questions/         # EN
  questions-pt/      # PT-BR
```

Runtime do quiz:

1. Lê `exams.json` pelo `?exam=`
2. Lê `manifest.json` → lista de arquivos
3. Carrega `{path}/questions/` ou `questions-pt/` conforme idioma
4. Progresso: `localStorage` key `learnioQuiz_{examId}_{en|pt}`
5. Histórico de mocks: `learnioHistory`
6. Idioma UI: `learnioLang` (`en` default)

### Schema de questão (chaves legadas; texto EN ou PT)

Os **nomes dos campos** no JSON vieram de um schema antigo em espanhol e **não devem ser renomeados** (o `quiz.html` depende deles). O **conteúdo** do texto é EN ou PT-BR.

| Campo (fixo) | Significado |
|---------------|-------------|
| `pregunta` | enunciado |
| `opciones` | alternativas |
| `texto_opcion` | texto da alternativa |
| `es_correcta` | se a alternativa é a correta |
| `explicacion` | explicação da alternativa |
| `tags` | `[id do subtema, rótulo curto]` |

Arquivo de programa/syllabus por exame: `temario.json` (nome de arquivo legado; = programa da prova).

Cada arquivo `1.1.json` etc. é um **array**:

```json
{
  "pregunta": "...",
  "opciones": [
    {
      "texto_opcion": "...",
      "es_correcta": true,
      "explicacion": "..."
    }
  ],
  "tags": ["1.1", "Rótulo curto"]
}
```

Regras:

- Sempre **4** alternativas (Associate seção 1 histórica pode ter 5)
- Exatamente **uma** `es_correcta: true`
- Toda alternativa tem `explicacion`
- `tags[0]` = id do subtema (= nome do arquivo sem `.json`)
- UI **embaralha** a ordem das alternativas na exibição

### `exams.json` (campos importantes)

- `id`, `title`, `short`, `vendor`, `path`
- `level` (beginner/intermediate/advanced) — metadado; **filtro de level foi removido da UI**
- `durationMinutes`, `realExamQuestions`, `bankCount`
- `languages`: `["en","pt"]`
- `blurb` / `blurbPt` — copy curta, **sem datas** tipo “Nov 2025”, sem “blueprint oficial…”

### Catálogo atual (volumes aproximados)

| id | Vendor | bankCount | Mock Q / min |
|----|--------|-----------|--------------|
| `DE_associate_databricks` | Databricks | 1226 (+ mocks reais) | 45 / 90 |
| `DE_professional_databricks` | Databricks | 1198 (+ mocks reais) | 59 / 120 |
| `DP203_azure` | Microsoft | 900 | 50 / 120 |
| `DEA_C01_aws` | AWS | 850 | 65 / 130 |
| `PDE_google` | Google Cloud | 900 | 50 / 120 |
| `SnowPro_Core_snowflake` | Snowflake | 900 | 100 / 115 |
| `dbt_Analytics_Engineering` | dbt Labs | 850 | 65 / 120 |

---

## 3. UX / produto (decisões já tomadas)

- Título da aba: **`LEARN.IO`**
- Fontes: **Bricolage Grotesque** (títulos), **Figtree** (corpo), **JetBrains Mono** (meta/atalhos)
- Evitar travessões (`—`) e pontuação “decorativa de IA” na copy
- Home: filtro **só Vendor** (All + vendors do catálogo)
- Sem bloco de café/doação na UI
- Quiz: atalhos `↑ ↓` (foco A–E), `→` confirma, `←`, `A–E`, `G` (ir para), `?`
- Mock: `?mode=sim` ou botão Mock; timer = `durationMinutes`; N = `realExamQuestions`
- Mock **balanceia domínios** (cotas pelo `peso` do `temario.json` quando existe; senão cotas iguais). Exclui pacotes “Real practice / study bank” (`90.x`, peso 0). Resultado mostra o mix por domínio.
- Mock: após cada resposta mostra **explicações** (correta + erradas) e trava a escolha. No mock, **esconde tags/tópico** (evita vazar o domínio). No fim: revisar missed, correct e all.
- Cache: home busca `exams.json?v=` + `CATALOG_VERSION`; quiz busca bancos com `BANK_VERSION` + `cache: 'no-store'`

---

## 4. Como o conteúdo foi / deve ser criado

### 4.1 Bancos “originais” (Databricks Associate / Professional / AWS)

- Conteúdo editorial (cenários + escolha de serviço/padrão)
- Tradução em lote com `deep_translator` (Google)
- Scripts locais (estão no `.gitignore` via `*.py`, existem na máquina):
  - `translate_to_en.py` — `questions-pt` → `questions`
  - `translate_to_pt.py` — `questions` → `questions-pt`
  - Protegem termos de produto (Unity Catalog, job cluster, BigQuery, etc.)
  - Cache: `{exam}/.translate_cache_{en|pt}.json` (ignorado no git)

### 4.2 Bancos novos (Azure DP-203, SnowPro, GCP PDE, dbt)

Gerados por agentes (Grok/Composer) + tooling local:

```
tools/bankgen/
  engine.py              # expand_cards, write_exam, wrappers de cenário
  azure_dp203.py         # (e similares por prova)
  snowflake_core.py
  gcp_pde.py
  dbt_analytics.py
  rebalance_options.py   # pós-processo de qualidade de alternativas
  generate_all.py        # legado / orquestração parcial
```

Padrão de geração:

1. `temario.json` com domínios oficiais + `alvo` por subtema (~850–900 Q)
2. Knowledge **cards** (stem, correct, why, wrong×3, tag)
3. `expand_cards` multiplica com indústrias/volumes/regiões até o alvo
4. Grava EN em `questions/`
5. Traduz para `questions-pt/` (`translate_to_pt.py`)
6. Registra em `exams.json`

**Atenção de qualidade:** geração em volume tende a:

- Distratores curtos / fracos
- **Viés “alternativa mais longa = correta”** (chegou a 85–99% em vários bancos)

Mitigação: `tools/bankgen/rebalance_options.py` **só engorda distratores** (nunca encurta a correta). Alvo: longest=correct ≲ ~10%. **Proibido** `compress()` na alternativa certa.

### 4.3 Import de provas / simulados “reais”

Script: `tools/bankgen/import_real_mocks.py`

Fontes usadas (só Databricks — qualidade editorial):

1. Markdown em `Dataside/09_referencias/estudos_certificacao/`
   - Associate: `prova_teste_…associate.md`, `simulado_2_…associate.md` → `90.1.json`, `90.2.json`
   - Professional: `simulado_…professional.md` → `11.1.json`
2. PassTest hand-written em `Dataside/07_projetos/passtest/core/script.js`
   - Estrutura: `EXAM_DATA.providers[].certs[]` (`de-associate`, `de-professional`)
   - Filtra `[Profundidade…]` e pads AWS/Azure; grava `90.3.json` / `11.2.json`

Comandos:

```bash
python tools/bankgen/import_real_mocks.py          # MD + PassTest
python tools/bankgen/import_real_mocks.py md       # só Markdown
python tools/bankgen/import_real_mocks.py passtest # só PassTest
```

Não importar bancos template PassTest de AWS/Azure (qualidade ruim). SnowPro / PDE / dbt / DEA ainda sem dumps locais “reais”.

### 4.4 Checklist para adicionar um exame novo

1. Criar pasta `{id}/` com `temario.json`, `manifest.json`, `questions/`, `questions-pt/`
2. Arquivos `{N.M}.json` alinhados ao temario; schema acima
3. Rodar medição de viés de comprimento; se > ~40% longest=correct, rodar `rebalance_options.py`
4. Entrada em `exams.json` (blurbs limpos EN/PT, vendor, bankCount)
5. Testar `quiz.html?exam={id}&lang=en` e `&lang=pt`
6. Commit + `git push origin main` (GitHub Pages em `/` da `main`)

---

## 5. Deploy

- Hosting: **GitHub Pages** no repo `ayrtonftridico/learnio`, branch `main`, path `/`
- Publicar só assets estáticos necessários (HTML/JS/JSON dos bancos)
- `*.py`, caches de tradução, docs internos do Associate, etc. ficam fora do site (gitignore)
- Após push: esperar 1–2 min; se a home parecer antiga → hard refresh / aba anônima / `?v=...`
- Sintoma clássico de cache: home com 3 provas + filtro Level + blurb “Nov 2025”

Comandos típicos:

```bash
cd c:\Users\ayrto\Downloads\learn.io
git add ...
git commit -m "..."
git push origin main
```

---

## 6. Comandos úteis (local)

```bash
# Traduzir EN → PT
python translate_to_pt.py DP203_azure SnowPro_Core_snowflake

# Traduzir PT → EN
python translate_to_en.py DE_professional_databricks

# Rebalancear comprimento das alternativas
python tools/bankgen/rebalance_options.py
python tools/bankgen/rebalance_options.py DP203_azure

# Medir viés "mais longa = correta"
python -c "..."  # ver histórico do chat / rebalance script stats
```

Dependência: `deep_translator` (e rede para Google Translate).

---

## 7. Convenções de copy e i18n

- Default idioma: **EN**
- Termos de produto oficiais preferencialmente **em inglês** mesmo no PT (job cluster, Unity Catalog, COPY INTO, etc.)
- SQL/Python em fences: sintaxe **sempre em inglês**; rodar `python fix_pt_terms.py` após traduzir (restaura fences a partir do EN + glossário)
- Blurbs: frases naturais, sem data de blueprint, sem lista telegráfica demais
- Não usar markdown com `**` em textos que o usuário cola em LinkedIn (regra do workspace Dataside; pouco relevante aqui)
- Preferir PT-BR em respostas do agente neste workspace

---

## 8. Problemas conhecidos / backlog

1. **Qualidade editorial dos bancos gerados** — distratores ainda fracos em vários exames; priorizar reescrita real (não só pad de tamanho)
2. **DP-203** — exame Microsoft aposentado (mar/2025); mantido como treino de skills Azure DE
3. **Cache Pages/browser** — sempre considerar ao validar deploy
4. **Apoio / PIX** — BMC removido; LivePix / link Pix são opções futuras melhores que Stripe chato
5. **Associate `1.json`** — exceção histórica (vários 1.x num arquivo só)
6. Tooling Python **não está no GitHub** (`*.py` no gitignore); quem clonar o repo público não leva os geradores — estão só na pasta local (ou precisam ser commitados de propósito depois)

---

## 9. O que um novo chat deve fazer primeiro

1. Ler este `CONTEXTO.md`
2. Abrir `exams.json` + `index.html` / `quiz.html` se a tarefa for UI
3. Se for conteúdo: olhar 1–2 JSON de `questions/` do exame alvo e o `temario.json`
4. Não inventar schema novo; não reintroduzir café/Level filter sem pedido
5. Antes de declarar “deploy ok”, validar URL live de `exams.json` e um `manifest.json` do exame novo (não só o HTML)
6. Após mudar bancos em massa, medir viés de comprimento das alternativas

---

## 10. Histórico resumido deste ciclo

- Productização do quiz estático + GitHub Pages
- Default EN + switch EN/PT na home e no quiz
- EN gerado para Professional e AWS (antes só PT)
- Quatro exames novos: Azure DP-203, SnowPro Core, GCP PDE, dbt AE (EN+PT)
- UI: filtros vendor, fontes novas, copy limpa, sem café
- Correção do atalho “resposta mais longa”
- Import de simulados reais (MD + PassTest Databricks) em seções `90.x` / `11.x`
- Este documento para continuidade de contexto

---

*Atualizado em 2026-07-29. Se divergir do repo, o código e o `exams.json` vencem.*
