# learn.io

Free practice product for **Data Engineering** certifications.

Question banks in **PT-BR** (official terms kept in English) + **EN** for DE Associate. Progress in the browser. No login.

## Exams

| Exam | Questions | Practice | Mock |
|---|---|---|---|
| Databricks DE Associate | 1008 | [open](quiz.html?exam=DE_associate_databricks) | [mock](quiz.html?exam=DE_associate_databricks&mode=sim) |
| Databricks DE Professional | 1009 | [open](quiz.html?exam=DE_professional_databricks) | [mock](quiz.html?exam=DE_professional_databricks&mode=sim) |
| AWS DEA-C01 | ~850 | [open](quiz.html?exam=DEA_C01_aws) | [mock](quiz.html?exam=DEA_C01_aws&mode=sim) |

## Local

```bash
cd learn.io
python -m http.server 8765
```

Open [http://localhost:8765](http://localhost:8765).

## Publish (GitHub Pages / Netlify / Cloudflare Pages)

1. Edit `site-config.js` — especially `buyMeACoffee`.
2. Deploy the `learn.io` folder as a static site (no build step).
3. Keep `exams.json`, `quiz.html`, and `*/questions-pt/` together.

## Features

- **Practice** — full bank, filters (All / Pending / Wrong), jump (`G`), PT|EN
- **Mock exam** — random sample sized like the real test + countdown timer; graded at the end
- **Export history** — downloads JSON + CSV (practice answers + mock sessions)

## Config

`site-config.js`:

- `brand`, `tagline`, `author`
- `buyMeACoffee`
- `description`

## Structure

```
learn.io/
  index.html          ← English landing
  quiz.html
  exams.json
  site-config.js
  favicon.svg
  */questions-pt/
  DE_associate_databricks/questions/   ← EN
```

## Question format

See `PADRAO_QUESTOES_PT.md`. Schema: `pregunta`, `opciones[]`, `tags`.
