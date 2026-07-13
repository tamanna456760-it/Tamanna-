import express, { type Express, type Request, type Response, type NextFunction } from "express";
import cors from "cors";
import pinoHttp from "pino-http";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import compression from "compression";
import hpp from "hpp";
import cookieParser from "cookie-parser";
import router from "./routes";
import { logger } from "./lib/logger";

const app: Express = express();

// ---------- Security ----------
app.use(helmet()); // Sets various HTTP headers for security
app.use(hpp());   // Protects against HTTP Parameter Pollution

// Rate limiting (adjust windowMs / max per your needs)
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,                 // limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Too many requests, please try again later." },
});
app.use("/api", limiter); // Apply to API routes

// ---------- Performance ----------
app.use(compression()); // gzip compression

// ---------- Logging (advanced pino-http) ----------
app.use(
  pinoHttp({
    logger,
    autoLogging: {
      ignore: (req) => req.url === "/health", // don't log health checks
    },
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
          ip: req.ip,
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
      err: pinoHttp.stdSerializers.err,
    },
    customSuccessMessage: (req, res) =>
      `${req.method} ${req.url} completed with ${res.statusCode}`,
    customErrorMessage: (req, res, err) =>
      `${req.method} ${req.url} failed: ${err.message}`,
  })
);

// ---------- Standard middleware ----------
app.use(cors({
  origin: process.env.CORS_ORIGIN?.split(",") || "*",
  credentials: true,
}));
app.use(express.json({ limit: "10kb" })); // limit body size
app.use(express.urlencoded({ extended: true, limit: "10kb" }));
app.use(cookieParser());

// ---------- Health check endpoint ----------
app.get("/health", (req, res) => {
  res.status(200).json({
    status: "ok",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
  });
});

// ---------- API routes ----------
app.use("/api", router);

// ---------- 404 handler ----------
app.use((req: Request, res: Response) => {
  res.status(404).json({ error: "Route not found" });
});

// ---------- Global error handler ----------
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error({ err, req }, "Unhandled error");
  const status = (err as any).status || 500;
  const message = status === 500 ? "Internal Server Error" : err.message;
  res.status(status).json({ error: message });
});

// ---------- Graceful shutdown ----------
const server = app.listen(process.env.PORT || 3000, () => {
  logger.info(`Server running on port ${process.env.PORT || 3000}`);
});

const shutdown = async () => {
  logger.info("Shutting down gracefully...");
  server.close(() => {
    logger.info("Server closed");
    process.exit(0);
  });
  // Force close after 10 seconds
  setTimeout(() => {
    logger.error("Forced shutdown due to timeout");
    process.exit(1);
  }, 10000);
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);

export default app;