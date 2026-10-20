# Website integration

The AIPE website (<https://aipel.co.uk/academy/>, repository
`FulongLi/Spirit-Connect-AIPE-Labs`) is a presentation layer. AIPE Academy is
the single source of truth for lessons, topics, prerequisites and academic
references; nothing educational is maintained twice.

## What the website consumes

| Academy file | Website use |
| --- | --- |
| `generated/lessons.json` | one page per lesson at `/academy/<domain>/<slug>/`, with status, type, time, prerequisite and next links, module, canonical GitHub source, lab links, translations and cited reference ids |
| `generated/knowledge-graph.json` | the interactive knowledge graph (`_data/knowledge_graph.yml` is generated from it; website-owned links per topic come from `_data/knowledge_graph_resources.yml`) and `_data/academy_graph.json` for learning paths |
| `generated/academic-references.json` | `_data/academic_references.json`, rendered as an external "Academic references" panel on every lesson that cites a course |
| lesson Markdown sources and `assets/` | page bodies and teaching assets, hash-checked against the catalogue |

The four website subjects are the four Academy domains (`foundations`,
`power-electronics`, `power-systems`, `renewable-energy`). The website's
former `renewables` key and URLs redirect to `renewable-energy`.

## How a refresh works

1. Merge the Academy change (or push it to a fork) so it exists at an
   immutable commit with a clean tree.
2. In the website checkout:
   ```sh
   python -m pip install -r requirements-dev.txt
   python tools/sync_ecosystem.py --registry ../AIPE-Registry --academy ../AIPE-Academy
   python tools/hub_data.py --write
   python tools/sync_ecosystem.py --check
   python tools/hub_data.py --check
   python tools/content_data.py --check
   python -m unittest discover -s tests -v
   ```
3. Place any new lesson URL in `_data/academy.yml` (the ordered lesson list of
   its subject) and, for a lab, in `_data/hub.yml`; the knowledge graph needs
   no edit because its topics and lesson attachments are generated.
4. Review the diff: `_data/ecosystem-lock.json` records the Academy repository,
   checkout repository, commit, catalogue/graph/reference hashes and every
   generated artifact hash.
5. Open the website pull request. Its CI checks out the pinned Academy
   revision, regenerates the pages, builds Jekyll and verifies every lesson
   URL, the four subject pages in both languages, the redirects, the canonical
   source links and the academic references panels.

Builds never follow an unpinned branch, and retiring a generated URL requires
a reviewed redirect; the sync refuses to drop one silently.

## URL contract

- Lesson pages: `/academy/<domain>/<slug>/` (English or Chinese, single-language
  pages; the language switch leads to the recorded translation or to the other
  language's Academy entry point).
- Subject pages: `/academy/<domain>/` and `/zh/academy/<domain>/`.
- Entry points: `/academy/` and `/zh/academy/`.
- Preserved: all eleven v0.1 lesson URLs, the migrated tutorial's blog URL
  `/resources/blog/buck-converter-from-zero-to-everything/`, and
  `/academy/renewables/` (redirect).

## Cross-repository dependency

A website refresh depends on a specific Academy commit, and the Academy's
generated files must be current (`python scripts/build_catalogue.py --check`).
Document the Academy commit and pull request in the website pull request, and
vice versa.
