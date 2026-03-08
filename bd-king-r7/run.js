import 'dotenv/config'
import { startAI } from './ai.js'
import { githubSync } from './github-sync.js'
import { systemMonitor } from './monitor.js'
import { securityScan } from './security.js'

console.log("🌸 Tamanna AI OS Starting...")

async function startSystem(){

await securityScan()

await githubSync()

systemMonitor()

await startAI()

}

startSystem()