import discord
from discord import app_commands
from datetime import datetime
import os

# ===== CONFIG =====
import os
TOKEN = os.getenv("TOKEN")


GUILD_ID = 1462959158763585693
LOG_CHANNEL_ID = 1465798160323444897
PULIZIA_ROLE_ID = 1465798254263406858
# ==================

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Bot online come {client.user}")

@tree.command(
    name="pulizia",
    description="Registra una pulizia completata",
    guild=discord.Object(id=GUILD_ID)
)
@app_commands.describe(
    bottiglie="Numero bottiglie",
    prezzo="Prezzo per bottiglia",
    famiglia="Nome famiglia"
)
async def pulizia(
    interaction: discord.Interaction,
    bottiglie: int,
    prezzo: int,
    famiglia: str
):
    ruolo = interaction.guild.get_role(PULIZIA_ROLE_ID)
    if ruolo not in interaction.user.roles:
        await interaction.response.send_message(
            "❌ Non hai il ruolo necessario.",
            ephemeral=True
        )
        return

    totale = bottiglie * prezzo
    data = datetime.now().strftime("%d/%m/%Y • %H:%M")

    embed = discord.Embed(
        title="🧹 PULIZIA COMPLETATA",
        color=discord.Color.green()
    )
    embed.add_field(name="👤 Utente", value=interaction.user.mention)
    embed.add_field(name="👨‍👩‍👧 Famiglia", value=famiglia)
    embed.add_field(name="🍾 Bottiglie", value=bottiglie)
    embed.add_field(name="💰 Totale", value=f"{totale}$")
    embed.add_field(name="📅 Data", value=data, inline=False)

    await interaction.response.send_message(embed=embed)

    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)

client.run(TOKEN)
