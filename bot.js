const { Client, GatewayIntentBits } = require("discord.js");

const client = new Client({
  intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent]
});

client.on("ready", () => {
  console.log(`Bot connected as ${client.user.tag}`);
});

client.on("messageCreate", (msg) => {
  if (msg.content === "!status") {
    msg.reply("System Online and Connected");
  }
});

client.login("YOUR_DISCORD_BOT_TOKEN");