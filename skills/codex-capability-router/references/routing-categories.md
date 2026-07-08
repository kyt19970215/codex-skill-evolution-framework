# Routing Categories

Use this table as a first-pass map. Prefer capabilities that are already installed and exposed in the current session.

| Category | Task signals | Preferred route |
| --- | --- | --- |
| product_design | product design, UX, UI, prototype, screenshot to app, design audit | Installed product-design workflow; start with its context or brief gate |
| creative_production | campaign assets, illustrations, covers, infographics, product imagery | Installed image-generation or specialist visual workflow |
| business_analysis | metrics, KPI, dashboard, variance analysis, report | Installed spreadsheet, data-analysis, document, or presentation workflow |
| documents | Word, DOCX, document editing, redline, comments | Installed document workflow |
| spreadsheets | XLSX, CSV, TSV, formulas, charts | Installed spreadsheet workflow |
| presentations | PPTX, slides, deck | Installed presentation workflow |
| pdf | PDF creation, extraction, rendering, forms | Installed PDF workflow |
| github | repository, issue, pull request, review, CI, publish | Installed GitHub workflow or app tools |
| web_browser | browser testing, page inspection, live URL interaction | Installed browser workflow |
| desktop_control | desktop app or operating-system UI interaction | Installed computer-use workflow |
| coding_debug | code edit, shell, build, test, dependency, path, encoding, quoting | `coding-debug-rules` |
| research_verification | public tool, current version, API behavior, exact public error | `research-verification` |
| project_rules | named repository, product, game, or domain | `project-rules-router`, then the narrow matching project skill |
| skill_evolution | create, update, split, merge, absorb, maintain, observe triggers, prune, or route skills and durable rules | `skill-evolution-core` plus `skill-evolution-router` |
| skill_discovery | no installed capability clearly matches | Discovery workflow; installation still requires explicit authorization |

## Ambiguous Tasks

- Map the requested outcome and artifact before choosing a tool.
- Prefer one narrow owner for each workflow.
- If a task needs both domain reasoning and artifact production, route domain work first and artifact production second.
- If the best match is not installed, present it as a candidate with trust level and side effects.
- Keep local capability names and precedence decisions in `external-skill-registry.md`, not in this public default map.
