require("dotenv").config();

module.exports = () => {
  const apiKey = process.env.DEEP_API_KEY || "NO_KEY_FOUND";
  const rateLimit = process.env.DEEP_RATE_LIMIT || 100;
  const env = process.env.NODE_ENV || "development";

  return {
    status: "OK",
    engine: "Tamanna AI • Deep Core",
    power: "Deep Power Engaged",
    environment: env,
    rateLimit: `${rateLimit} req/min`,
    apiKeyStatus: apiKey.startsWith("http") ? "URL_MODE" : "KEY_MODE",
    timestamp: new Date().toISOString(),
    system: {
      name: process.env.SYSTEM_NAME || "BD-KING-R7",
      engine: process.env.ENGINE_NAME || "Tamanna-AI",
      mode: process.env.ENGINE_MODE || "production",
    },
  };
};
