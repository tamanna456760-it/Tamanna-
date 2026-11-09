# Tamanna AI on GitHub Pages

## Published address

- User interface: https://tamanna456760-it.github.io/Tamanna-/
- Admin preview: https://tamanna456760-it.github.io/Tamanna-/admin/

The deployment is a **static project-site preview**. It includes the user chat interface, settings UI, static assets, and the Admin Control Center preview.

## What GitHub Pages can and cannot run

GitHub Pages serves static HTML, CSS, JavaScript, images, and other static files. It does not run Python, FastAPI, Docker, Ollama, background workers, or a database.

Therefore, on this GitHub Pages address:

- The interface and local browser preferences can be viewed.
- Sign-in, account creation, AI inference, chat history, server metrics, and privileged Admin actions are not active.
- The chat UI explicitly identifies preview mode and does not send prompts to a nonexistent backend.
- The Admin page remains in Preview Mode and must not show invented live data.

## Deployment

The workflow `.github/workflows/deploy-github-pages.yml` builds the static site into `dist/`, rewrites asset and navigation paths for the `/Tamanna-/` project URL, excludes the custom-domain `CNAME` file from the Pages artifact, and deploys with GitHub Pages Actions.

Every push to `main` triggers the deployment workflow.

## Enable full AI functionality later

To enable real chat and account features, deploy the existing FastAPI application to a separately managed backend host with persistent storage and a private local Ollama runtime. Then configure a secure same-origin API route or a carefully restricted HTTPS API origin. Do not put session secrets, model credentials, database credentials, or private keys in this static repository or browser JavaScript.

The VPS and domain are not assumed to be purchased or configured. Do not treat a successful static Pages deployment as proof that the AI backend is live.
