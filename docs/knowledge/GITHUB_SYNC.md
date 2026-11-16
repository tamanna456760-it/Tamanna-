# GitHub Knowledge Sync (API-free)

Tamanna can use the public GitHub repository as a knowledge source without a
GitHub REST API token and without a hosted AI API. The sync process uses the
ordinary Git HTTPS protocol to clone/fetch a **public** repository, then uses
Tamanna's existing SQLite knowledge store and deterministic local feature
embeddings. Chat generation still requires the separately installed local
Ollama model.

## Run on the same machine as the FastAPI backend

```bash
python scripts/sync_github_knowledge.py
```

Optional configuration:

```bash
TAMANNA_KNOWLEDGE_GIT_URL=https://github.com/OWNER/REPOSITORY.git
TAMANNA_KNOWLEDGE_GIT_BRANCH=main
```

The default source is the public `tamanna456760-it/Tamanna-` repository.
Only Markdown, reStructuredText and text files are indexed. The sync excludes
runtime, build, private, secret, upload and trash directories, skips symbolic
links and files larger than 1 MB, and caps the corpus at 20,000 documents.
The SQLite index is written under `data/knowledge_vectors.sqlite3` and must
remain on persistent private backend storage.

## How chat uses it

The authenticated RAG route already searches the shared `tamanna-public`
corpus alongside the current user's private corpus. This sync script writes
GitHub documents under that shared owner so the existing retrieval path can
find them. Guest chat on the standalone Main.py application must be verified
against its actual route before claiming it uses this index.

## Important boundaries

- No GitHub API token or hosted AI API key is used.
- Public GitHub repository required for unauthenticated Git transport. A private
  source requires a separately secured deploy key or local checkout; never put
  credentials in the repository URL.
- GitHub is the knowledge source, not the language model. Ollama must be
  installed and running locally to generate natural-language answers.
- The backend must run this sync script after deployment and whenever new
  knowledge is added. This commit does not create a running VPS service or a
  scheduled job, and it does not make GitHub Pages execute Python.
- The index is additive by source path: changed files replace their prior
  chunks. Deleted/renamed files are not automatically pruned yet; inspect
  source metadata and perform a deliberate stale-source cleanup before
  enabling automated deletion.
- Retrieved documents are untrusted reference material. Do not follow
  instructions embedded in documents as system instructions.


## Account repository memory integration

The account inventory workflow is separate from the public source-code RAG sync:

1. `scripts/sync_github_repositories.py` uses a GitHub token to enumerate repositories visible to that token.
2. Because `memory/github_repositories.json` is committed to this repository, the workflow filters out every private repository before writing the file. Private names, URLs and descriptions must never be committed to a public repository.
3. `scripts/index_github_repository_memory.py --validate-only` validates the public inventory in CI without requiring a database.
4. To index an inventory into a backend database, run the indexer on the backend host with `TAMANNA_GITHUB_MEMORY_OWNER_ID` set to the authenticated administrator's internal owner ID and `TAMANNA_KNOWLEDGE_DB` pointing to the persistent knowledge database. The indexer requires an explicit owner ID and does not write to the shared `tamanna-public` corpus.

Example (backend host only):

```bash
TAMANNA_GITHUB_MEMORY_OWNER_ID="<internal-admin-owner-id>" \
TAMANNA_KNOWLEDGE_DB="/var/lib/tamanna/knowledge_vectors.sqlite3" \
python scripts/index_github_repository_memory.py
```

For private repositories, do not use the committed public inventory. Generate a separate inventory in a private backend-only location with a token that has only the required repository read access, then pass that private file using `--index-file /secure/path/repositories.json`. Keep the file outside the Git checkout, restrict filesystem permissions, and never upload it as a public artifact. The indexer still requires the explicit owner ID.

The scheduled GitHub workflow polls every six hours; it is not an instantaneous repository-created webhook. It only sees repositories visible to the configured token. Set `TAMANNA_GITHUB_TOKEN` as an Actions secret with the minimum read-only repository/account scope needed. The built-in workflow token may see only the current repository. The workflow's `GITHUB_TOKEN` permission to write is limited to committing the public inventory in this repository.

This integration indexes repository metadata, not all repository source code. Source-code indexing remains the separate public Git HTTPS workflow described above. A production backend schedule/service must invoke the metadata indexer after the inventory is refreshed; GitHub Actions does not directly write into the VPS database.
