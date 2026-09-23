# BD-KING-R7 Powerhub — Tamanna AI Website

**ASP.NET 8 Razor Pages • .NET 8 • Docker • PostgreSQL-ready**

**Owner:** HM INSAN ALI

---

## 1. Overview

**BD-KING-R7 Powerhub** is the web control, documentation, project-status and system-information interface for **Tamanna AI**.

The website is designed to provide a clean web layer that can later connect with the Tamanna AI backend, automation services, project intelligence, memory, language systems and other approved project modules.

### Core technologies

- ASP.NET Core 8
- Razor Pages
- C#
- .NET 8
- JSON-based project content
- PostgreSQL-ready architecture
- Docker
- Docker Compose
- Health monitoring
- Environment-based configuration

---

# 2. Main Architecture

```text
                         BROWSER
                            │
                            ▼
                ┌──────────────────────┐
                │   BD-KING-R7         │
                │   POWERHUB WEBSITE   │
                │   ASP.NET 8          │
                │   Razor Pages        │
                └──────────┬───────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
        ProjectStore    Health API    System API
             │
             ▼
      Data/projects.json


                 Future Integration
                         │
                         ▼
              ┌─────────────────────┐
              │     Tamanna AI      │
              │     FastAPI         │
              │     main.py         │
              └──────────┬──────────┘
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
   Language          Understanding       Memory
     System             System            System
       │                 │                  │
       └─────────────────┼──────────────────┘
                         ▼
                  Reply Generator
                         │
                         ▼
                   Module Router