import 'dotenv/config'
import { startAI } from './ai/ai.js'
import { githubSync } from './github/sync.js'
import { generateProject } from './generator/generator.js'
import { startWeb } from './web/server.js'
import { startBot } from './telegram/bot.js'

async function main(){
console.log("🌸 Tamanna AI Dev System v3 Starting...")

await githubSync()
await generateProject("create REST API with Node.js")
await startAI()
startWeb()
startBot()

console.log("✅ System Ready")
}

main()