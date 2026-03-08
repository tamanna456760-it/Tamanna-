import fs from "fs-extra"
import { askAI } from "./ai.js"

async function organizeCode(){

  // 1️⃣ Read all code from one file
  const allCode = await fs.readFile("all_code.hm","utf-8")

  // 2️⃣ Ask AI to split code into correct files
  const prompt = `
আপনি এখন Code Organizer:
Input: এক ফাইলে সব কোড:
${allCode}

Output JSON format:
{
  "ai/ai.js":"AI engine code ...",
  "web/server.js":"Web server code ...",
  "telegram/bot.js":"Telegram bot code ...",
  "github/sync.js":"GitHub sync code ...",
  "monitor/monitor.js":"System monitor code ...",
  "security/security.js":"Security code ...",
  "backup/backup.js":"Backup code ...",
  "devops/deploy.js":"Deploy code ..."
}
`
  const result = await askAI(prompt)

  // 3️⃣ Parse JSON
  let files
  try {
    files = JSON.parse(result)
  } catch (e){
    console.error("❌ AI JSON parsing error:", e)
    console.log("AI output:", result)
    return
  }

  // 4️⃣ Write to correct folders
  for(const path in files){
    await fs.ensureDir(path.split("/").slice(0,-1).join("/"))
    await fs.writeFile(path, files[path])
    console.log(`✅ File created: ${path}`)
  }

  console.log("🎉 All code organized automatically!")
}

organizeCode()