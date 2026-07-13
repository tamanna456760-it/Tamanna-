import simpleGit from "simple-git"

const git = simpleGit()

export async function githubSync(){

await git.add(".")
await git.commit("Telegram AI update")
await git.push()

}