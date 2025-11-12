const fs = require('fs-extra');
const chalk = require('chalk');

class SetupScript {
  async run() {
    console.log(chalk.blue('⚙️ Setting up tamangsaru522-it development environment...'));
    
    await this.createGitHooks();
    await this.createConfigFiles();
    await this.displayNextSteps();
  }

  async createGitHooks() {
    const hooksDir = '.git/hooks';
    
    if (!await fs.pathExists(hooksDir)) {
      console.log(chalk.yellow('⚠️ Git not initialized. Run git init first.'));
      return;
    }

    // Pre-commit hook
    const preCommitHook = `#!/bin/bash
echo "🔧 tamangsaru522-it auto-fix running..."
node src/main.js fix-json
git add *.json
echo "✅ Pre-commit checks completed"
`;

    await fs.writeFile(`${hooksDir}/pre-commit`, preCommitHook);
    await execPromise(`chmod +x ${hooksDir}/pre-commit`);
    
    console.log(chalk.green('✅ Git hooks installed'));
  }

  async createConfigFiles() {
    const configs = {
      '.auto-fix.json': JSON.stringify({
        name: "tamangsaru522-it",
        version: "1.0.0",
        settings: {
          autoFixJSON: true,
          autoCommit: true,
          skipDirs: ["node_modules", ".git", "dist"]
        }
      }, null, 2)
    };

    for (const [file, content] of Object.entries(configs)) {
      if (!await fs.pathExists(file)) {
        await fs.writeFile(file, content);
        console.log(chalk.green(`✅ Created ${file}`));
      }
    }
  }

  async displayNextSteps() {
    console.log(`
${chalk.green('🎉 Setup completed!')}

Next steps:
1. ${chalk.cyan('git add .')} - Stage all files
2. ${chalk.cyan('git commit -m "feat: initial commit"')} - First commit
3. ${chalk.cyan('git remote add origin <your-repo-url>')} - Add remote
4. ${chalk.cyan('git push -u origin main')} - Push to GitHub

Auto-fix commands:
• ${chalk.cyan('npm run fix')} - Run comprehensive auto-fix
• ${chalk.cyan('npm run commit')} - Auto commit changes
• ${chalk.cyan('npm run fix-json')} - Fix JSON files only
    `);
  }
}

module.exports = SetupScript;