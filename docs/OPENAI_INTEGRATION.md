# OpenAI integration for Tamanna AI

Tamanna AI can select either its local Ollama provider or the hosted OpenAI Responses API. The authenticated chat orchestration continues to build the same user-scoped prompt, including permitted conversation history and retrieved knowledge, before calling the selected provider.

## Enable GPT on the backend

1. Create an OpenAI API key in the OpenAI Platform. ChatGPT subscriptions and API billing are separate.
2. Store the key in the backend host's private secret manager or an untracked server-side `.env` file. Never put it in HTML, JavaScript, mobile app bundles, GitHub commits, or chat messages.
3. Set these server environment values:

   ```dotenv
   TAMANNA_MODEL_PROVIDER=openai
   OPENAI_API_KEY=<server-side-secret>
   TAMANNA_OPENAI_MODEL=gpt-5.5
   TAMANNA_OPENAI_BASE_URL=https://api.openai.com/v1
   ```

4. Restart the FastAPI service and run `python scripts/validate_env.py --strict`.
5. Send an authenticated chat request and inspect the backend's normal health/logging facilities. Do not log the API key or full authorization headers.

## Keep local inference

To use the existing local Ollama integration instead, set:

```dotenv
TAMANNA_MODEL_PROVIDER=ollama
TAMANNA_OLLAMA_URL=http://127.0.0.1:11434
TAMANNA_OLLAMA_MODEL=qwen2.5:7b
```

Provider selection is explicit. Tamanna does not silently send private prompts to a hosted provider or silently fall back between providers. This avoids unexpected data transfer and API charges. A future fallback policy should be an explicit administrator setting with clear privacy and cost behavior.

## Security and limitations

- OpenAI requests originate from the backend, not the browser.
- The provider requires HTTPS, disables environment proxy inheritance, and does not follow redirects.
- Provider error response bodies are not exposed to chat users.
- API key values are never included in validation output.
- OpenAI API usage can incur separate charges and is subject to the selected project's model access, rate limits, and quotas.
- The code addition does not establish a live connection until a valid API key is configured on the deployed backend.
- Model names and availability can change; choose a model enabled for the API project.

## Verification

Run:

```sh
python -m pytest -q tests/test_openai_provider.py tests/test_ollama_provider.py
python scripts/validate_env.py
```

The tests use mocked HTTP responses; they verify request construction and error handling, not live API credentials or production connectivity.
