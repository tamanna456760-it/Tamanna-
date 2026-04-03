import express from "express"
import dotenv from "dotenv"
import { askAI } from "./ai/ai.js"
import { githubSync } from "./github/sync.js"

dotenv.config()

const app = express()

app.use(express.json())
app.use(express.static("public"))

app.post("/ai", async (req,res)=>{

const message=req.body.message

const response=await askAI(message)

res.json({reply:response})

})

app.get("/sync",async(req,res)=>{

await githubSync()

res.json({status:"GitHub synced"})

})

app.listen(process.env.PORT,()=>{

console.log("Tamanna AI Server Running")

})