import simpleGit from "simple-git"
import fs from "fs-extra"

const git = simpleGit()

export async function syncFiles(repoPath="./project"){
  await fs.ensureDir(repoPath)
  const repo = simpleGit(repoPath)
  await repo.init()
  await repo.add(".")
  await repo.commit("Auto sync commit")
  await repo.push()
  console.log("🌐 Files and code synced to GitHub")
}