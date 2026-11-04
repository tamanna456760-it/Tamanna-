# Tamanna AI: Modular AI Projects and Knowledge Catalogue

## What changed

The nine unresolved Git submodule gitlinks are represented as a first-party,
read-only capability and knowledge catalogue in
`tamanna_ai/integrations/project_catalog.py`.

The catalogue maps each reference to a potential Tamanna feature and searchable
knowledge topics. It preserves the exact commit IDs found in the parent
repository so the references are not lost.

## Feature mapping

| Upstream reference | Tamanna capability | Knowledge topics |
| --- | --- | --- |
| AutoGen | Multi-agent coordination | Roles, routing, approvals, termination |
| CLI | Safe CLI interface | Help, allow-list, permissions, audit |
| CrewAI | Agent task planning | Roles, tasks, delegation, review |
| Dify | Workflow orchestration | Workflows, triggers, approvals, webhooks |
| LangChain | LLM and retrieval pipelines | Retrievers, loaders, templates, citations |
| n8n | Workflow automation | Workflows, webhooks, status, retries |
| Open WebUI | Chat UI interoperability reference | UX, provider settings, accessibility |
| Power Systems CLI | Safe system operations | Health, diagnostics, service status |
| Tamanna project reference | Internal project knowledge | Architecture, module map, decisions, history |

## Important implementation boundary

This catalogue is a real, testable Tamanna feature, but it is not a claim that
the upstream projects' source code has been imported or that their capabilities
are operational. The parent repository contained Git submodule entries but no
`.gitmodules` file, so the upstream repository URLs could not be recovered from
the checkout metadata. A Git commit ID alone does not identify its source
repository.

Every entry therefore remains `source_unverified`. Before importing or adapting
upstream code, recover the canonical repository URL, inspect the exact pinned
revision, review its license and dependencies, and perform a security review.
Then implement a narrow adapter behind Tamanna's existing permission and
tool-execution boundaries. Do not copy entire projects into chat memory.

## Memory model

The catalogue's `memory_topics` are searchable reference metadata. They are not
personal chat memories and do not contain credentials or private user data.
Actual documents can be imported through Tamanna's existing authorized
knowledge-import pipeline, with provenance, user isolation, and source labels.

Imported documents must be treated as untrusted reference material, never as
instructions to execute. Secrets, private prompts, model weights, and private
third-party data must not be ingested.

## Checkout repair

The broken gitlink entries are removed from the parent tree because their
submodule URLs are missing. Their pinned commit IDs remain recorded in the
catalogue. This makes a normal checkout independent of those unavailable
submodule definitions while preserving the recovery information.

## Verification

Run:

```bash
python -m pytest tests/test_project_catalog.py -q
python -m compileall -q tamanna_ai/integrations/project_catalog.py
git submodule status
```

A successful catalogue test does not verify the upstream integrations. Those
remain blocked until source repositories are identified and separately tested.
