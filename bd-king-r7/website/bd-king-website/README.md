```markdown
# bd-king-r7 Powerhub — Website (Razor Pages, .NET 8)

What this is

- A small documentation & status website for bd-king-r7 and Tamanna AI.
- Razor Pages (.NET 8) with a JSON data file (Data/projects.json) you can edit to add or update content.
- Includes Dockerfile for containerized deployment.

Files of interest

- Program.cs — app entrypoint
- Services/ProjectStore.cs — loads Data/projects.json
- Pages/\* — Razor pages for content and detail view
- Data/projects.json — content source (edit this to change website content)
- wwwroot/css/site.css — minimal styling
- Dockerfile — containerize the site

Build & run locally

1. Install .NET 8 SDK on your machine.
2. From the project directory:
   dotnet build
   dotnet run

   The site will run on http://localhost:5000 (or the URL printed by dotnet run).

Build & run with Docker

1. Build the image:
   docker build -t bd-king-website:latest .

2. Run:
   docker run -p 8080:80 bd-king-website:latest

   Visit http://localhost:8080

Editing content

- Open Data/projects.json and modify or add items. Fields:
  - Id (unique identifier used in URLs)
  - Title
  - Short (short summary)
  - Content (HTML string)
  - Languages (array)
  - Tags (array)
- After editing, restart the site (or rebuild image) to pick up changes.

How this integrates with the automation system

- The ProjectStore and pages are intentionally simple: the same orchestrator/agent system described previously can be linked from this site.
- You can extend the site to query the orchestrator API (if you built the .NET orchestrator) and show live run status for agents.

Next steps I recommend

1. Provide the bd-king-r7 repository URL and exact build/test commands — I will:
   - add a "Build status" section that can fetch and display the latest automated-run reports (if you run the orchestrator).
   - pre-fill agent fix/build commands for your codebase.
2. If you want me to push this into a Git repo I can produce a complete repo layout and optionally a GitHub Actions pipeline to build & publish the Docker image.
3. For production: put an HTTPS reverse proxy (nginx/Caddy), set environment variables, and run behind a process manager or container orchestrator.

Security note

- Keep any orchestrator tokens and secrets out of the Data/ JSON; use environment-backed config for secrets if you integrate dynamic reporting.
```
