import { gitPush } from "./git.js";

// Compatibility wrapper: all push policy is enforced in one hardened module.
export async function githubSync() {
  return gitPush();
}
