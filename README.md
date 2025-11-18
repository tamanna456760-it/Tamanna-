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
    <-->bd-king-r7<-->tamanna code language 
 <---->bd-king-r7 program>---> All 
     File System Monitor → Sync Engine → Build Engine