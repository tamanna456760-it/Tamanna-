require("dotenv").config();
const simpleGit = require("simple-git");
const fs = require("fs-extra");
const fetch = require("node-fetch");

const git = simpleGit();

const OPENAI_KEY = process.env.OPENAI_KEY;
const REPO_URL = process.env.REPO_URL;

async function aiSync() {
  console.log("📥 Pulling latest repo...");
  await git.pull();

  // Example: Read main file (index.js)
  const filePath = "index.js";
  if (!fs.existsSync(filePath)) {
    console.log("File not found:", filePath);
    return;
  }

  const code = fs.readFileSync(filePath, "utf8");

  console.log("🧠 Sending code to AI...");
  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${OPENAI_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [
        { role: "system", content: "You are a coding assistant. Fix any errors and optimize code." },
        { role: "user", content: `Code:\n${code}` }
      ]
    })
  });

  const data = await response.json();
  const newCode = data.choices[0].message.content;

  fs.writeFileSync(filePath, newCode);

  console.log("📤 Committing changes...");
  await git.add(".");
  await git.commit("AI auto sync update");
  await git.push();

  console.log("✅ AI Sync Complete!");
}

// Run every 1 minute (optional)
setInterval(aiSync, 60000);