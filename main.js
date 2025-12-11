const { program } = require("./cli");
const JSONFixer = require("./json-fixer");
const AutoCommitter = require("./auto-committer");

class TamangsaruAutoFix {
  constructor() {
    this.name = "tamangsaru522-it Auto Fix";
    this.version = "1.0.0";
  }

  async run() {
    console.log(`🚀 ${this.name} v${this.version}`);

    const command = process.argv[2] || "help";

    switch (command) {
      case "fix":
        await this.fixAll();
        break;
      case "fix-json":
        await this.fixJSON();
        break;
      case "commit":
        await this.autoCommit();
        break;
      case "setup":
        await this.setup();
        break;
      default:
        this.showHelp();
    }
  }

  async fixAll() {
    console.log("🔧 Running comprehensive auto-fix...");

    const jsonFixer = new JSONFixer();
    const committer = new AutoCommitter();

    // Fix JSON files
    await jsonFixer.fixDirectory(".");

    // Auto commit changes
    await committer.commit("fix: auto-fix code and JSON formatting");

    console.log("✅ Auto-fix completed!");
  }

  async fixJSON() {
    console.log("📝 Fixing JSON files...");
    const fixer = new JSONFixer();
    await fixer.fixDirectory(".");
  }

  async autoCommit() {
    const message = process.argv[3] || "chore: auto-commit changes";
    const committer = new AutoCommitter();
    await committer.commit(message);
  }

  async setup() {
    console.log("⚙️ Setting up tamangsaru522-it auto-fix environment...");
    // Setup git hooks and configuration
    require("../scripts/setup").run();
  }

  showHelp() {
    console.log(`
Usage: node src/main.js [command]

Commands:
  fix        - Run comprehensive auto-fix
  fix-json   - Fix JSON files only
  commit [msg] - Auto commit with message
  setup     - Setup development environment
  help      - Show this help message

Examples:
  node src/main.js fix
  node src/main.js fix-json
  node src/main.js commit "feat: add new feature"
    `);
  }
}

// Run if called directly
if (require.main === module) {
  new TamangsaruAutoFix().run();
}

module.exports = TamangsaruAutoFix;
