import { Router, type IRouter, type Request, type Response, type NextFunction } from "express";
import helmet from "helmet";
import cors from "cors";
import compression from "compression";
import rateLimit from "express-rate-limit";
import morgan from "morgan";
import { v4 as uuidv4 } from "uuid";

import healthRouter from "./health";
import openaiRouter from "./openai/conversations";

// ----------------------------------------------
// 1. কাস্টম রেসপন্স ফরম্যাট (structure)
// ----------------------------------------------
export interface ApiResponse<T = any> {
  success: boolean;
  message?: string;
  data?: T;
  error?: string;
  requestId: string;
  timestamp: string;
}

// রেসপন্স হেলপার (router level এ ব্যবহারের জন্য)
declare global {
  namespace Express {
    interface Response {
      success<T>(data?: T, message?: string, status?: number): void;
      error(message: string, status?: number, details?: any): void;
    }
  }
}

// ----------------------------------------------
// 2. Async হ্যান্ডলার (try-catch মুক্ত)
// ----------------------------------------------
const asyncHandler = (fn: Function) => (req: Request, res: Response, next: NextFunction) =>
  Promise.resolve(fn(req, res, next)).catch(next);

// ----------------------------------------------
// 3. রেট লিমিটিং (প্রতি IP ১০ মিনিটে ১০০ রিকোয়েস্ট)
// ----------------------------------------------
const limiter = rateLimit({
  windowMs: 10 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    success: false,
    error: "Too many requests, please try again later.",
    requestId: "rate-limit",
    timestamp: new Date().toISOString(),
  },
});

// ----------------------------------------------
// 4. মেইন রাউটার ক্লাস (অ্যাডভান্সড আর্কিটেকচার)
// ----------------------------------------------
class AdvancedRouter {
  public router: IRouter;

  constructor() {
    this.router = Router();

    this.initializeMiddlewares();
    this.initializeResponseMethods();
    this.initializeRoutes();
    this.initializeErrorHandler();
  }

  private initializeMiddlewares() {
    // সিকিউরিটি + পারফরম্যান্স
    this.router.use(helmet());
    this.router.use(cors({ origin: process.env.CORS_ORIGIN?.split(",") || "*" }));
    this.router.use(compression());
    this.router.use(limiter);

    // রিকোয়েস্ট আইডি জেনারেট
    this.router.use((req: Request, res: Response, next: NextFunction) => {
      req.headers["x-request-id"] = req.headers["x-request-id"] || uuidv4();
      next();
    });

    // লগিং (request id সহ)
    morgan.token("request-id", (req: Request) => (req.headers["x-request-id"] as string) || "-");
    this.router.use(morgan("combined :request-id"));

    // JSON পার্স + বডি লিমিট
    this.router.use(express.json({ limit: "10mb" }));
    this.router.use(express.urlencoded({ extended: true, limit: "10mb" }));
  }

  private initializeResponseMethods() {
    // success method
    this.router.use((req: Request, res: Response, next: NextFunction) => {
      res.success = function <T>(data?: T, message = "Success", status = 200) {
        const response: ApiResponse<T> = {
          success: true,
          message,
          data,
          requestId: req.headers["x-request-id"] as string,
          timestamp: new Date().toISOString(),
        };
        this.status(status).json(response);
      };

      res.error = function (message: string, status = 500, details?: any) {
        const response: ApiResponse = {
          success: false,
          error: message,
          ...(details && { data: details }),
          requestId: req.headers["x-request-id"] as string,
          timestamp: new Date().toISOString(),
        };
        this.status(status).json(response);
      };
      next();
    });
  }

  private initializeRoutes() {
    // হেলথ চেক (অ্যাডভান্সড ভার্সন)
    this.router.get("/health", asyncHandler(async (req: Request, res: Response) => {
      const healthInfo = {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        timestamp: new Date().toISOString(),
      };
      res.success(healthInfo, "Server is healthy");
    }));

    // ওপেনএআই রাউট (প্রয়োজনে কাস্টম মিডলওয়্যার যোগ করা যাবে)
    this.router.use("/api/v1/openai", openaiRouter); // ভার্সনিং যোগ হলো

    // ৪০৪ হ্যান্ডলার
    this.router.use("*", (req: Request, res: Response) => {
      res.error(`Cannot ${req.method} ${req.originalUrl}`, 404);
    });
  }

  private initializeErrorHandler() {
    // গ্লোবাল এরর হ্যান্ডলার (সব async error ধরে)
    this.router.use((err: any, req: Request, res: Response, next: NextFunction) => {
      console.error("Global error:", err);

      const status = err.status || err.statusCode || 500;
      const message = err.message || "Internal Server Error";

      // প্রোডাকশনে বিস্তারিত ত্রুটি লুকান
      const errorResponse = process.env.NODE_ENV === "development"
        ? { stack: err.stack, details: err.details }
        : undefined;

      res.error(message, status, errorResponse);
    });
  }
}

// ----------------------------------------------
// 5. এক্সপোর্ট রেডি-টু-ইউজ রাউটার
// ----------------------------------------------
const { router } = new AdvancedRouter();
export default router;