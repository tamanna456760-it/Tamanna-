import simpleGit from "simple-git"

const git=simpleGit()

export async function githubSync(){

await git.add(".")
await git.commit("AI auto update")
await git.push()

}