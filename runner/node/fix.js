import fs from "fs-extra"
import { askAI } from "./ai.js"

export async function fixCode(filePath){
  const code = await fs.readFile(filePath, "utf-8")
  const prompt = `
Fix this code automatically, remove duplicates, fix syntax errors:
${code}
`
  const fixedCode = await askAI(prompt)
  await fs.writeFile(filePath, fixedCode)
  console.log(`✅ Code fixed: ${filePath}`)
}