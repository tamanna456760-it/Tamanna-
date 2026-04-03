require("dotenv").config();

if (!process.env.OPENAI_KEY) {
  console.error("OPENAI_KEY not found");
  process.exit(1);
}

console.log("OPENAI KEY LOADED");