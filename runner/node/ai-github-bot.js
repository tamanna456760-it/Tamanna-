require("dotenv").config();
const fs = require("fs");
const simpleGit = require("simple-git");
const { OpenAI } = require("openai");

const git = simpleGit();
const openai = new OpenAI({
  apiKey: process.env.OPENAI_KEY
});

async function aiEdit(prompt) {

  console.log("📥 Pulling latest repo...");
  await git.pull();

  const code = fs.readFileSync("index.js", "utf8"); // change target file

  console.log("🧠 Sending to AI...");

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [
      { role: "system", content: "You are a coding assistant. Modify the code safely." },
      { role: "user", content: `Instruction: ${prompt}\n\nCode:\n${code}` }
    ]
  });

  const newCode = response.choices[0].message.content;

  fs.writeFileSync("index.js", newCode);

  console.log("📤 Committing changes...");
  await git.add(".");
  await git.commit("AI Updated Code");
  await git.push();

  console.log("✅ Done!");
}

const userPrompt = process.argv[2];
aiEdit(userPrompt);