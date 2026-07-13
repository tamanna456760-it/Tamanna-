import express from "express";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import cors from "cors";
import xssClean from "xss-clean";
import mongoSanitize from "express-mongo-sanitize";
import cookieParser from "cookie-parser";

const app = express();

// Basic security headers
app.use(helmet());

// Body parsing
app.use(express.json());
app.use(cookieParser());

// CORS control
app.use(cors({
  origin: ["https://your-frontend.com"],
  credentials: true
}));

// XSS protection
app.use(xssClean());

// NoSQL injection / query sanitize
app.use(mongoSanitize());

// Rate limit (login / auth routes এর জন্য আলাদা করে আরও strict করা যায়)
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 300,
  standardHeaders: true,
  legacyHeaders: false
});
app.use(globalLimiter);

// Simple auth middleware skeleton
function requireAuth(req, res, next) {
  const token = req.headers.authorization?.split(" ")[1] || req.cookies.token;
  if (!token) return res.status(401).json({ message: "Unauthorized" });

  try {
    // এখানে JWT verify করবে
    // const payload = jwt.verify(token, process.env.JWT_SECRET);
    // req.user = payload;
    next();
  } catch (err) {
    return res.status(401).json({ message: "Invalid token" });
  }
}

// Protected route example
app.get("/api/secure-data", requireAuth, (req, res) => {
  res.json({ secret: "Only authenticated users can see this" });
});

// Error handler (sensitive info leak না করার জন্য)
app.use((err, req, res, next) => {
  console.error("Error:", err.message);
  res.status(500).json({ message: "Something went wrong" });
});

app.listen(3000, () => {
  console.log("Secure-ish server running on port 3000");
});
