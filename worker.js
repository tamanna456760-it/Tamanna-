const VERSION = "1.0.0";

const SECURITY_HEADERS = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
};

const ALLOWED_METHODS = "GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS";
const ALLOWED_HEADERS = "Authorization, Content-Type, X-Requested-With, X-CSRF-Token";

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      ...SECURITY_HEADERS,
      ...headers,
    },
  });
}

function configuredOrigins(env) {
  return String(env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean);
}

function originAllowed(request, env) {
  const origin = request.headers.get("Origin");
  if (!origin) return true;

  let requestOrigin;
  try {
    requestOrigin = new URL(request.url).origin;
  } catch {
    return false;
  }

  return origin === requestOrigin || configuredOrigins(env).includes(origin);
}

function corsHeaders(request, env) {
  const origin = request.headers.get("Origin");
  if (!origin) return {};

  let ownOrigin;
  try {
    ownOrigin = new URL(request.url).origin;
  } catch {
    return {};
  }

  if (origin !== ownOrigin && !configuredOrigins(env).includes(origin)) {
    return {};
  }

  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": ALLOWED_METHODS,
    "Access-Control-Allow-Headers": ALLOWED_HEADERS,
    "Access-Control-Max-Age": "600",
    Vary: "Origin",
  };
}

function withSecurityHeaders(response, extraHeaders = {}) {
  const headers = new Headers(response.headers);
  for (const [name, value] of Object.entries(SECURITY_HEADERS)) {
    headers.set(name, value);
  }
  for (const [name, value] of Object.entries(extraHeaders)) {
    headers.set(name, value);
  }
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

function parseApiOrigin(value) {
  if (!value) return null;

  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error("TAMANNA_API_ORIGIN must be a valid absolute URL.");
  }

  if (url.protocol !== "https:" || url.username || url.password || url.search || url.hash) {
    throw new Error("TAMANNA_API_ORIGIN must be HTTPS and must not contain credentials, query, or fragment.");
  }

  const host = url.hostname.toLowerCase();
  if (
    host === "localhost" ||
    host === "::1" ||
    host.endsWith(".localhost") ||
    /^127\./.test(host) ||
    /^10\./.test(host) ||
    /^192\.168\./.test(host) ||
    /^169\.254\./.test(host) ||
    /^172\.(1[6-9]|2\d|3[01])\./.test(host)
  ) {
    throw new Error("TAMANNA_API_ORIGIN cannot point to a loopback or private IPv4 address.");
  }

  return url;
}

async function proxyApi(request, env) {
  let backend;
  try {
    backend = parseApiOrigin(env.TAMANNA_API_ORIGIN);
  } catch (error) {
    return json(
      { success: false, error: error.message, code: "API_ORIGIN_INVALID" },
      503
    );
  }

  if (!backend) {
    return json(
      {
        success: false,
        error: "The FastAPI backend is not configured.",
        code: "API_BACKEND_NOT_CONFIGURED",
      },
      503
    );
  }

  const incoming = new URL(request.url);
  const prefix = backend.pathname.replace(/\/+$/, "");
  const target = new URL(
    `${prefix}${incoming.pathname}${incoming.search}`,
    backend.origin
  );

  const headers = new Headers(request.headers);
  for (const name of [
    "host",
    "content-length",
    "connection",
    "transfer-encoding",
    "cf-connecting-ip",
  ]) {
    headers.delete(name);
  }

  headers.set("X-Forwarded-Host", incoming.host);
  headers.set("X-Forwarded-Proto", "https");
  if (!headers.has("User-Agent")) {
    headers.set("User-Agent", `TamannaAI-Worker/${VERSION}`);
  }

  const init = {
    method: request.method,
    headers,
    redirect: "manual",
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
  }

  try {
    const upstream = await fetch(target.toString(), init);
    const responseHeaders = corsHeaders(request, env);
    responseHeaders["Cache-Control"] = "no-store";
    return withSecurityHeaders(upstream, responseHeaders);
  } catch {
    return json(
      {
        success: false,
        error: "The API backend could not be reached.",
        code: "API_BACKEND_UNAVAILABLE",
      },
      502,
      corsHeaders(request, env)
    );
  }
}

async function serveAssets(request, env) {
  if (!env.ASSETS || typeof env.ASSETS.fetch !== "function") {
    return json(
      { success: false, error: "Static assets binding ASSETS is missing." },
      500
    );
  }

  try {
    return withSecurityHeaders(await env.ASSETS.fetch(request));
  } catch {
    return json(
      { success: false, error: "Static website assets could not be loaded." },
      500
    );
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.protocol !== "https:") {
      return Response.redirect(
        `https://${url.host}${url.pathname}${url.search}`,
        301
      );
    }

    if (!["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"].includes(request.method)) {
      return json(
        { success: false, error: "Method not allowed." },
        405,
        { Allow: ALLOWED_METHODS }
      );
    }

    if (!originAllowed(request, env)) {
      return json(
        { success: false, error: "Origin is not allowed.", code: "ORIGIN_NOT_ALLOWED" },
        403
      );
    }

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: { ...SECURITY_HEADERS, ...corsHeaders(request, env) },
      });
    }

    if (url.pathname === "/health") {
      return json({
        success: true,
        service: "Tamanna AI Cloudflare Worker",
        status: "online",
        version: VERSION,
        backendConfigured: Boolean(env.TAMANNA_API_ORIGIN),
        timestamp: new Date().toISOString(),
      });
    }

    if (url.pathname === "/api" || url.pathname.startsWith("/api/")) {
      return proxyApi(request, env);
    }

    return serveAssets(request, env);
  },
};
