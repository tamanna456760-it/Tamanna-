import { gitPush } from "./git.js";

// Compatibility wrapper: no implicit staging, commit, or push.
export async function githubSync() {
  console.log("GitHub sync check started");
  const result = await gitPush();
  console.log(result.pushed ? "GitHub sync completed" : result.reason);
  return result;
}
