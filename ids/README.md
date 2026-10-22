Tamanna AI — Intrusion Detection System (IDS)

Owner: HM INSAN ALI

1. Overview

Tamanna AI IDS is a security monitoring component designed to detect suspicious activity and report potential threats.

It complements the Tamanna AI Firewall. The Firewall controls access according to its configured policy, while the IDS analyzes available security events for suspicious patterns.

2. Core Features

* Monitor security logs and application events.
* Detect repeated failed login attempts.
* Identify suspicious request patterns.
* Detect unusual request frequency.
* Identify repeated access to sensitive paths.
* Generate structured security alerts.
* Maintain timestamped detection records.
* Produce JSON security reports.
* Integrate with the Firewall audit log.
* Support future dashboard integration.

3. Security Principles

* Start in monitor-only mode.
* Never modify operating-system firewall rules.
* Never automatically block an IP address.
* Do not collect passwords, authentication tokens, or unnecessary personal data.
* Validate and limit the size of incoming events.
* Record detection reasons for later review.
* Require explicit authorization before any future enforcement feature.

4. Planned Architecture

1. Event Collector
2. Event Normalizer
3. Detection Engine
4. Threat Rule Registry
5. Alert Manager
6. Security Event Store
7. JSON Report Generator
8. Unit Tests

5. Integration

The IDS should integrate with the existing Tamanna AI Firewall through documented interfaces.

The IDS must not assume that every event indicates an attack. Alerts require review and may include false positives.

6. Testing

Tests should cover:

* Normal events
* Repeated failed logins
* Suspicious request paths
* Malformed event data
* Oversized events
* Event storage and report generation
* False-positive handling
* Read-only operation

7. Project Identity

Project: Tamanna AI
Owner: HM INSAN ALI

This component is intended to improve visibility into security events. It does not guarantee that every attack will be detected.