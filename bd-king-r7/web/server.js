import express from 'express'
import { askAI } from '../ai/ai.js'
const app = express()
app.use(express.json())
app.use(express.static("public"))

app.post("/ai", async (req,res)=>{
const reply = await askAI(req.body.message)
res.json({reply})
})

app.listen(process.env.PORT, ()=>console.log(`🌐 Web Dashboard running on port ${process.env.PORT}`))