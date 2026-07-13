require("dotenv").config();
const fetch = require("node-fetch");
const simpleGit = require("simple-git");
const git = simpleGit();

async function syncRepo() {
  console.log("📥 Pulling latest code...");
  await git.pull();

  console.log("🧠 Sending code to AI...");

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${process.env.OPENAI_KEY}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      messages: [
        { role: "user", content: "Check my project for errors and suggest fixes." }
      ]
    })
  });

  const data = await response.json();
  console.log("AI Suggestion:\n", data.choices[0].message.content);

  console.log("📤 Auto Commit...");
  await git.add(".");
  await git.commit("AI Auto Sync Update");
  await git.push();

  console.log("✅ Sync Complete");
}

setInterval(syncRepo, 60000);