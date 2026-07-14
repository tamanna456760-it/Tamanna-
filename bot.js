#!/usr/bin/env node

const readline = require("readline");
const os = require("os");

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: "Tamanna> "
});

console.log("==================================");
console.log("🤖 Tamanna CLI Bot v1.0.0");
console.log("Type 'help' to see commands.");
console.log("==================================");

const commands = {
    help: () => {
        console.log(`
Available Commands:
-------------------
help      Show this help
status    Show bot status
time      Show current time
system    Show system information
clear     Clear the screen
exit      Exit the bot
`);
    },

    status: () => {
        console.log({
            name: "Tamanna Bot",
            version: "1.0.0",
            status: "Online"
        });
    },

    time: () => {
        console.log(new Date().toString());
    },

    system: () => {
        console.log({
            platform: os.platform(),
            hostname: os.hostname(),
            cpuCount: os.cpus().length,
            memoryGB: (os.totalmem() / 1024 / 1024 / 1024).toFixed(2)
        });
    },

    clear: () => {
        console.clear();
    }
};

rl.prompt();

rl.on("line", (line) => {
    const cmd = line.trim().toLowerCase();

    if (cmd === "exit") {
        console.log("Goodbye!");
        process.exit(0);
    }

    if (commands[cmd]) {
        commands[cmd]();
    } else {
        console.log(`Unknown command: ${cmd}`);
    }

    rl.prompt();
});
