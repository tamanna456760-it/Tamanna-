import express from "express";
import helmet from "helmet";
import dns from "dns";
import { URL } from "url";

const app = express();
app.use(express.json());
app.use(helmet());

// Allowed outbound hosts (only your own services)
const ALLOWED_HOSTS = [
  "api.my-internal-service.local",
  "internal-db.local"
];

// Helper: check if URL is allowed
function isAllowedUrl(targetUrl) {
  try {
    const url = new URL(targetUrl);
    return ALLOWED_HOSTS.includes(url.hostname);
  } catch {
    return false;
  }
}

// Example: safe fetch wrapper (pseudo)
async function safeFetch(url, options = {}) {
  if (!isAllowedUrl(url)) {
    throw new Error(`Blocked outbound request to: ${url}`);
  }

  // এখানে তুমি node-fetch / axios ইত্যাদি ব্যবহার করতে পারো
  // return fetch(url, options);
  return { ok: true, message: "Simulated internal call only" };
}

// Example route: কোনোভাবেই third‑party তে ডাটা যাবে না
app.post("/api/send-data", async (req, res) => {
  const { targetUrl, payload } = req.body;

  try {
    const response = await safeFetch(targetUrl, {
      method: "POST",
      body: JSON.stringify(payload),
      headers: { "Content-Type": "application/json" }
    });

    res.json({ status: "sent", response });
  } catch (err) {
    console.error("Blocked/Failed:", err.message);
    res.status(400).json({ error: "Outbound blocked or invalid" });
  }
});

app.listen(3000, () => {
  console.log("Data-protective server running on 3000");
});
