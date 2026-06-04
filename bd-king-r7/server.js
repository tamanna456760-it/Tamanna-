import express from "express"
import dotenv from "dotenv"
import { askAI } from "./ai/ai.js"
import { githubSync } from "./github/sync.js"

dotenv.config()

const app = express()

app.use(express.json())
app.use(express.static("public"))

// Health check
app.get("/", (req, res) => {
  res.json({ status: "Tamanna AI Server Running", time: new Date() })
})

// AI Route
app.post("/ai", async (req, res) => {
  try {
    const message = req.body.message
    if (!message) {
      return res.status(400).json({ error: "Message is required" })
    }

    const reply = await askAI(message)
    res.json({ reply })
  } catch (err) {
    console.error("AI Error:", err)
    res.status(500).json({ error: "AI processing failed" })
  }
})

// GitHub Sync Route
app.get("/sync", async (req, res) => {
  try {
    await githubSync({
      repoPath: "./project",
      remoteUrl: "https://github.com/tamanna456760-it/tamanna-.git",
      branch: "main",
      autoPull: true
    })

    res.json({ status: "GitHub synced successfully" })
  } catch (err) {
    console.error("Sync Error:", err)
    res.status(500).json({ error: "GitHub sync failed" })
  }
})

// Start Server
app.listen(process.env.PORT || 3000, () => {
  console.log(`🚀 Tamanna AI Server Running on port ${process.env.PORT}`)
})