File System Monitor → Sync Engine → Build Engine --> tamanna code language 

┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   File System   │───▶│   Sync Engine    │───▶│   Build Engine  │
│    Monitor      │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Change Detection│    │  Conflict Resolver │  │ Dependency Manager│
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │   Deployment    │
                        │     Engine      │
                        └─────────────────┘
     