import express from "express";
import cors from "cors";
import helmet from "helmet";
import morgan from "morgan";
import dotenv from "dotenv";
import { RateLimiterMemory } from "rate-limiter-flexible";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3002;
const rateLimiter = new RateLimiterMemory({
  keyGenerator: (req) => req.ip,
  points: 10,
  duration: 60,
});

app.use(helmet());
app.use(cors());
app.use(morgan("combined"));
app.use(express.json({ limit: "1mb" }));

function authenticateInternal(req, res, next) {
  const expectedKey = process.env.AI_SERVICE_API_KEY;
  if (!expectedKey) {
    return res.status(503).json({
      error: "Service not configured",
      message: "Set AI_SERVICE_API_KEY in the private environment before enabling internal access.",
    });
  }
  if (req.headers["x-api-key"] !== expectedKey) {
    return res.status(401).json({ error: "Unauthorized", message: "Invalid API key" });
  }
  return next();
}

app.post("/api/chat", authenticateInternal, async (req, res) => {
  try {
    await rateLimiter.consume(req.ip);
  } catch {
    return res.status(429).json({
      error: "Rate limit exceeded",
      message: "Too many requests. Please try again in a minute.",
    });
  }

  const { message } = req.body || {};
  if (typeof message !== "string" || !message.trim()) {
    return res.status(400).json({
      error: "Invalid message",
      message: "Message is required and must be a non-empty string.",
    });
  }

  // External model providers are deliberately disabled. Return an honest
  // unavailable response until a tested local inference/knowledge adapter exists.
  return res.status(503).json({
    error: "Local AI runtime unavailable",
    message: "No local model or knowledge database is configured. External model APIs are disabled.",
  });
});

app.get("/health", (_req, res) => {
  res.json({
    status: "degraded",
    service: "Tamanna local AI gateway",
    model: null,
    externalProviders: "disabled",
    localRuntime: "not_configured",
    timestamp: new Date().toISOString(),
  });
});

if (process.env.NODE_ENV !== "test") {
  app.listen(PORT, () => {
    console.log(`Tamanna local AI gateway listening on port ${PORT}; local runtime not configured`);
  });
}

export default app;
