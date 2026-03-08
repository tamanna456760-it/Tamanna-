import fs from "fs-extra"
import { askAI } from "./ai.js"

export async function generateCode(idea){

const prompt = "Write production ready code for: " + idea

const code = await askAI(prompt)

return code

}

export async function saveCode(name,code){

await fs.ensureDir("./project")

await fs.writeFile("./project/"+name,code)

console.log("File saved:",name)

}