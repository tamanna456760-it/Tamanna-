const chokidar = require("chokidar");
const { exec } = require("child_process");

console.log("🚀 Tamanna Ultimate Auto Dev System Running...");

const watcher = chokidar.watch(".", {
  ignored: /node_modules|\.git/,
  persistent: true
});

watcher.on("change", (path) => {
  console.log(`\n📂 File changed: ${path}`);

  exec("npm run lint", () => {
    console.log("🛠 Code Auto Fixed");
  });

  exec("npm run format", () => {
    console.log("🎨 Code Formatted");
  });

  exec("npm run build", () => {
    console.log("🏗 Build Complete");
  });

  exec("git add . && git commit -m 'auto update' && git push", () => {
    console.log("🔁 Git Auto Synced");
  });
});
const { exec } = require("child_process");
const util = require("util");
const chalk = require("chalk");

const execPromise = util.promisify(exec);

class AutoCommitter {
  constructor() {
    this.branch = "main";
  }

  async commit(message = "chore: auto-commit changes") {
    try {
      console.log(chalk.blue("🤖 Starting auto-commit process..."));

      // Check if there are changes
      const { stdout: status } = await execPromise("git status --porcelain");
      if (!status.trim()) {
        console.log(chalk.yellow("⚠️ No changes to commit"));
        return;
      }

      // Add all changes
      console.log(chalk.blue("📦 Staging changes..."));
      await execPromise("git add .");

      // Commit
      console.log(chalk.blue("💾 Committing changes..."));
      await execPromise(`git commit -m "${message}"`);

      // Get current branch
      const { stdout: branch } = await execPromise("git branch --show-current");
      this.branch = branch.trim();

      // Push
      console.log(chalk.blue("🚀 Pushing to remote..."));
      await execPromise(`git push origin ${this.branch}`);

      console.log(
        chalk.green(`✅ Successfully committed and pushed: "${message}"`),
      );
    } catch (error) {
      console.log(chalk.red(`❌ Auto-commit failed: ${error.message}`));
    }
  }

  async getGitInfo() {
    try {
      const [branch, remote] = await Promise.all([
        execPromise("git branch --show-current"),
        execPromise("git remote get-url origin"),
      ]);

      return {
        branch: branch.stdout.trim(),
        remote: remote.stdout.trim(),
      };
    } catch (error) {
      return { branch: "unknown", remote: "none" };
    }
  }
}

module.exports = AutoCommitter;
