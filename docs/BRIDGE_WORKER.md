# Running the Tamanna bridge worker

The bridge worker is a separate process. It uses the same model provider configuration as the existing `Main.py` chat application.

1. Configure these values in the private `.env` used by the Tamanna AI process:

```env
TAMANNA_BRIDGE_URL=https://YOUR-CENTRAL-SERVER
TAMANNA_BRIDGE_SERVICE_TOKEN=<same-private-service-token-configured-on-central-server>
TAMANNA_BRIDGE_POLL_SECONDS=3
```

2. Install the normal Tamanna server dependencies and start the worker from the repository root:

```bash
python -m tamanna_ai.integrations.run_bridge_worker
```

3. Run the chat server and worker as separate supervised services (for example, separate Docker Compose services or systemd units). Restart the worker automatically on failure and keep logs private.

The worker calls the existing configured model provider; it does not create a new model. It does not execute shell commands. Use HTTPS for remote connections and never commit the service token.

Note: deploy the matching Central Server bridge endpoints first. Until both processes are running and ChatGPT is authorized to the `/mcp` endpoint, the bridge is not live.