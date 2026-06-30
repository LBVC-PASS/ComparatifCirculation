# CLAUDE.md — ComparatifCirculation

Brief for any Claude session working on this repo. Read before editing.

## What this is

A zero-build, single-page web tool comparing Quebec municipal traffic bylaws
(*règlements de circulation*) against each other and the provincial **CSR**
(*Code de la sécurité routière*). It flags each article as redundant with the
CSR, divergent between towns, a lacuna (gap), or clean. Built for legal
codification review across towns served by the same police board (Régie —
RPLDM).

## Files

| File | Role |
|------|------|
| `taxonomie.json` | Config: `villes` (towns), `domaines` (8), `themes` (~48, each `{id, domaine, label}`). |
| `articles.json` | `{ "version", "articles": [...] }` — the bylaw articles. |
| `index.html` | CSS + HTML + vanilla JS. **No dependencies, no framework, no build step.** Also holds *embedded copies* of both JSON files in `<script id="emb-tax">` / `<script id="emb-art">` as a `file://` fallback. |
| `build.py` | Regenerates the embedded copies from the JSON. No dependencies (stdlib only). |

## Workflow (do this every time)

1. Edit `taxonomie.json` and/or `articles.json`.
2. Run `python3 build.py` — syncs the embedded fallback blocks in `index.html`.
3. Commit. (Editing JSON updates the app; nothing else to rebuild.)

**Never hand-edit the `emb-tax` / `emb-art` blocks** — `build.py` owns them.
Skipping step 2 makes the double-click (`file://`) view go stale.

## Data model — an article

```json
{ "id":"SM-7", "source":"SM", "numero":"7", "theme":"sig_arret",
  "objet":"…", "texte":"…", "statut":"redondant_csr",
  "recommandation":"reecrire", "renvoi_csr":"368", "amende":null,
  "parametres":{}, "note":null }
```

- `source` — a town id; **must** exist in `taxonomie.json → villes[].id`.
- `theme` — a theme id; **must** exist in `taxonomie.json → themes[].id`.
- `statut` ∈ `propre | redondant_csr | divergent | desuet | hybride | a_valider`.
- `recommandation` ∈ `conserver | retirer | harmoniser | reecrire | moderniser | valider`.
  **This per-article field is the source of truth in the UI** — it overrides
  the statut-derived default (`recoText()` in `index.html`). Set it deliberately.
- `amende` — `null` or `{min, max}` in dollars.
- **Write JSON text WITHOUT accents** (`reglement`, `desuet`, `reecrire`). The
  JS re-adds accents for display (`RECOS`, `STATUTS` label maps). Keep new data
  unaccented to match existing rows.

## Towns are data-driven (N-town model)

Towns are **not** hardcoded. To add a town (e.g. Pointe-Calumet,
Saint-Joseph-du-Lac): add an entry to `villes` and add its articles — **no code
changes needed.**

```json
{ "id":"PC", "label":"Pointe-Calumet", "reglement":"###", "court":"PC ####" }
```

- `villes[]` order = column display order in the Rapport view.
- The Rapport renders one dynamic column per town. Flags
  (`harmonise` / `divergent` / `lacune` / `redondant_csr` / `partiel`) and the
  "lacune" summary are computed across **all** towns — a theme covered by some
  but not all towns = lacune.
- Up to 6 town colors are predefined (CSS `.pill.v0`…`.pill.v5`).

## Conventions to preserve

- Keep the no-dependency, data-driven principle: editing JSON updates the app,
  no rebuild.
- Do **not** reintroduce hardcoded `DM` / `SM` logic — iterate over `VILLES`.
- Keep article `id`s stable.
- Every article's `source` and `theme` must resolve against `taxonomie.json`.

## Verifying a change

Headless render check works on both paths — `file://` (uses embedded fallback;
CORS-blocks the `fetch`, which is expected) and a local HTTP server (uses the
live JSON). Confirm no `pageerror`s, the summary stats populate, and the Rapport
columns match the town count.

## History

- PR #1 — refactor to data-driven N-town model + `build.py` sync script.
- PR #2 — per-article `recommandation` made the UI source of truth.

Roadmap (per `index.html` footer): ingest annexes (street lists); add
Pointe-Calumet and Saint-Joseph-du-Lac; a comparison-matrix tab.
