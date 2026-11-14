# Observability package boundary

The target observability boundary owns structured application logs, health metrics, tracing, audit events, and exporters.

Current code is distributed across `tamanna_ai/reports/`, `tamanna_ai/runtime/`, security audit modules, and the root `logs/` archive. This README records the intended package boundary; it does not claim that a unified telemetry implementation exists.

Do not create duplicate loggers or audit stores here. Consolidate only after mapping current imports, event schemas, retention rules, and tests. Runtime logs belong outside source control; archived historical logs must not be imported as live application state.
