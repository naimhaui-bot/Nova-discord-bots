const {
  Client,
  GatewayIntentBits,
  PermissionsBitField
} = require("discord.js");

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// Utilisation des variables d'environnement pour Railway
const HONEYPOT_CHANNEL = process.env.HONEYPOT_CHANNEL;
const LOG_CHANNEL = process.env.LOG_CHANNEL;

client.once("ready", () => {
  console.log(`${client.user.tag} est connecté.`);
});

client.on("messageCreate", async (message) => {
  if (message.author.bot) return;
  if (message.channel.id !== HONEYPOT_CHANNEL) return;

  // Ignore les modérateurs
  if (
    message.member.permissions.has(
      PermissionsBitField.Flags.ManageMessages
    )
  ) {
    return;
  }

  try {
    await message.delete().catch(() => {});

    await message.member.ban({
      reason: "Détection Honeypot"
    });

    const log = message.guild.channels.cache.get(LOG_CHANNEL);
    if (log) {
      log.send(
        `🍯 ${message.author.tag} a été banni automatiquement après avoir parlé dans le salon Honeypot.`
      );
    }
  } catch (err) {
    console.error(err);
  }
});

client.login(process.env.DISCORD_TOKEN);
