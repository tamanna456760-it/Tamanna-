import { generateCode } from "./generator.js"
import { saveCode } from "./generator.js"
import { gitPush } from "./git.js"

async function run(){

console.log("Tamanna AI Coding Agent Started")

const idea = "create simple node api server"

const code = await generateCode(idea)

await saveCode("server.js",code)

await gitPush()

console.log("Project Generated")

}

run()