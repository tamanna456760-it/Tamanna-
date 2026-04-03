import { askAI } from '../ai/ai.js'
import fs from 'fs-extra'

export async function generateProject(idea){
const code = await askAI("Write production ready code for: "+idea)
await fs.ensureDir("./project")
await fs.writeFile("./project/index.js", code)
console.log("📝 Project generated")
}