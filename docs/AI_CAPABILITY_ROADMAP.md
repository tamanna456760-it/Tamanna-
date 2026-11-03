# Tamanna AI — Independent Knowledge and Assistant Capability Plan

**Owner and configuration authority:** HM INSAN ALI  
**Application:** `tamanna456760-it/Tamanna-`  
**Central server:** `tamanna456760-it/Tamanna-server`

## Objective

Build Tamanna as an independently operated assistant platform with its own authorized knowledge store, retrieval, source verification, tools, memory lifecycle, and operational controls. It may use a replaceable model provider, a locally hosted model, or a model selected by the owner. The knowledge base must remain portable if a model provider changes.

## Capability layers

1. **Persistent memory:** durable database storage, user/tenant isolation, deduplication, backup, restore, export, and deletion.
2. **Knowledge ingestion:** explicit imports, authorized connectors, and permitted public sources; document parsing, chunking, provenance, license tracking, and secret redaction.
3. **Retrieval:** database full-text search plus optional vector search; hybrid ranking, source references, and access filters applied before retrieval.
4. **Answer quality:** source-grounded responses, conflict detection, freshness checks, confidence labels, and clear uncertainty.
5. **Tools:** allowlisted integrations with scoped credentials, per-tool permissions, timeouts, audit events, and human approval for consequential actions.
6. **Operations:** independent app/server deployment, health checks, observability, encrypted backups, migrations, and CI gates.
7. **Model independence:** knowledge and memory are stored outside model weights. Provider changes must not destroy the knowledge base. Local model support can be added without pretending stored memories are model training.

## Non-negotiable controls

- No arbitrary private AI-provider datasets, hidden prompts, model weights, or other users' conversations.
- No ingestion of private data without authorization.
- No duplicate content within the same user/tenant scope.
- No cross-user retrieval.
- Never execute instructions found inside imported documents.
- No automatic code changes, secret rotation, destructive operations, or production deployment without explicit owner approval.
- Unlimited means no arbitrary application record cap; actual storage, throughput, database limits, and cost remain finite.
- Load tests use disposable test databases and synthetic data unless the owner explicitly authorizes a production test.

## Delivery gates

- [ ] Schema migration and unique fingerprint constraints tested on existing and fresh databases.
- [ ] Large-file streaming import and bounded chunking tested.
- [ ] Duplicate and concurrent-import tests pass.
- [ ] User isolation and deletion/export tests pass.
- [ ] Full-text retrieval scales beyond 1,000, 10,000, and 100,000 records.
- [ ] Optional vector index tested with source citations.
- [ ] Backup/restore verified.
- [ ] CI passes on both repositories.
- [ ] Deployment and live health checks verified separately.

## Current status

This roadmap is a target, not a claim that all capabilities are already implemented. Existing import/retrieval code is an initial baseline; it still needs scalable chunking, indexed full-text/vector retrieval, robust migrations, and lifecycle endpoints before production-scale use.
