const { exec } = require('child_process');
const util = require('util');
const chalk = require('chalk');

const execPromise = util.promisify(exec);

class AutoCommitter {
  constructor() {
    this.branch = 'main';
  }

  async commit(message = 'chore: auto-commit changes') {
    try {
      console.log(chalk.blue('🤖 Starting auto-commit process...'));

      // Check if there are changes
      const { stdout: status } = await execPromise('git status --porcelain');
      if (!status.trim()) {
        console.log(chalk.yellow('⚠️ No changes to commit'));
        return;
      }

      // Add all changes
      console.log(chalk.blue('📦 Staging changes...'));
      await execPromise('git add .');

      // Commit
      console.log(chalk.blue('💾 Committing changes...'));
      await execPromise(`git commit -m "${message}"`);

      // Get current branch
      const { stdout: branch } = await execPromise('git branch --show-current');
      this.branch = branch.trim();

      // Push
      console.log(chalk.blue('🚀 Pushing to remote...'));
      await execPromise(`git push origin ${this.branch}`);

      console.log(chalk.green(`✅ Successfully committed and pushed: "${message}"`));
      
    } catch (error) {
      console.log(chalk.red(`❌ Auto-commit failed: ${error.message}`));
    }
  }

  async getGitInfo() {
    try {
      const [branch, remote] = await Promise.all([
        execPromise('git branch --show-current'),
        execPromise('git remote get-url origin')
      ]);

      return {
        branch: branch.stdout.trim(),
        remote: remote.stdout.trim()
      };
    } catch (error) {
      return { branch: 'unknown', remote: 'none' };
    }
  }
}

module.exports = AutoCommitter;