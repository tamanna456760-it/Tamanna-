import fs from "fs-extra"
import { askAI } from "./ai.js" // তোমার AI engine

// 1️⃣ Read all code
const allCode = await fs.readFile("all_code.hm","utf-8")

// 2️⃣ AI decide করে কোন ফাইল কোথায় যাবে
const result = await askAI(`
আপনি এখন Code Organizer:
Input: এক ফাইলে সব কোড।
Output: JSON format:
{
  "ai/ai.js":"AI engine code ...",
  "web/server.js":"Web server code ...",
  "telegram/bot.js":"Telegram bot code ...",
  "github/sync.js":"GitHub sync code ...",
  "monitor/monitor.js":"System monitor code ...",
  "security/security.js":"Security system code ...",
  "backup/backup.js":"Backup code ...",
  "devops/deploy.js":"Deploy code ..."
}
`)

// 3️⃣ Parse AI JSON
const files = JSON.parse(result)

// 4️⃣ Write to proper folders
for(const path in files){
  await fs.ensureDir(path.split("/").slice(0,-1).join("/"))
  await fs.writeFile(path, files[path])
  console.log(`✅ File created: ${path}`)
}

console.log("🎉 All code organized automatically!")