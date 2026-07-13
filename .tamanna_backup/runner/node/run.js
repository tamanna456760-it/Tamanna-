import 'dotenv/config'
import { startAI } from './ai/ai.js'
import { githubSync } from './github/sync.js'
import { generateProject } from './generator/generator.js'
import { startWeb } from './web/server.js'
import { startBot } from './telegram/bot.js'
import { monitorSystem } from './monitor/monitor.js'
import { securityScan } from './security/security.js'
import { backupSystem } from './backup/backup.js'

async function main(){
  console.log("🌸 Tamanna AI Full OS v5 Starting...")

  await securityScan()
  await backupSystem()
  await githubSync()
  await generateProject("Create full stack AI project with Node.js and Express")
  await startAI()
  monitorSystem()
  startWeb()
  startBot()

  console.log("✅ Tamanna AI Full OS v5 Ready")
}

main()