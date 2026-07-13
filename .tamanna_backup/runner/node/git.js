import simpleGit from "simple-git"

const git = simpleGit("./project")

export async function gitPush(){

await git.init()
await git.add(".")
await git.commit("AI generated project")
await git.push()

console.log("GitHub updated")

}