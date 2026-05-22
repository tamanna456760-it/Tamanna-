import simpleGit from "simple-git"
import fs from "fs-extra"
import path from "path"

export async function syncFiles({
  repoPath = "./project",
  remoteUrl = null,
  branch = "main",
  autoPull = true,
} = {}) {
  try {
    await fs.ensureDir(repoPath)

    const repo = simpleGit(repoPath)

    // Initialize repo if missing
    const isRepo = await repo.checkIsRepo()
    if (!isRepo) {
      console.log("📁 Initializing new Git repository...")
      await repo.init()
    }

    // Add remote if provided
    const remotes = await repo.getRemotes(true)
    const hasOrigin = remotes.some(r => r.name === "origin")

    if (remoteUrl && !hasOrigin) {
      console.log("🔗 Adding remote origin...")
      await repo.addRemote("origin", remoteUrl)
    }

    // Ensure branch exists
    const currentBranch = (await repo.branch()).current
    if (currentBranch !== branch) {
      console.log(`🌿 Switching to branch: ${branch}`)
      try {
        await repo.checkout(branch)
      } catch {
        console.log(`🌱 Creating branch: ${branch}`)
        await repo.checkoutLocalBranch(branch)
      }
    }

    // Pull latest changes
    if (autoPull && hasOrigin) {
      console.log("⬇️ Pulling latest changes...")
      await repo.pull("origin", branch)
    }

    // Stage & commit
    const status = await repo.status()
    if (status.files.length === 0) {
      console.log("✔️ No changes to commit")
    } else {
      console.log("📝 Committing changes...")
      await repo.add(".")
      await repo.commit(`Auto sync commit - ${new Date().toISOString()}`)
    }

    // Push
    if (hasOrigin) {
      console.log("⬆️ Pushing to GitHub...")
      await repo.push("origin", branch)
    }

    console.log("🌐 Sync complete")
  } catch (err) {
    console.error("❌ Sync failed:", err.message)
  }
}