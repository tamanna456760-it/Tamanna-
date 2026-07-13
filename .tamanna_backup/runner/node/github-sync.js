import simpleGit from 'simple-git'

const git = simpleGit()

export async function githubSync(){

console.log("GitHub Sync Running")

await git.add('.')
await git.commit("Tamanna AI Auto Update")
await git.push()

console.log("GitHub Sync Complete")

}