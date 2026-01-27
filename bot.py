import discord
from discord import app_commands
from datetime import datetime
import random
import os

# ========= CONFIG =========
TOKEN = os.getenv("TOKEN")  # Railway ENV
GUILD_ID = 1462959158763585693
ROLE_ID_AUTORIZZATO = 1465798254263406858
LOG_CHANNEL_ID = 1465798160323444897
# ==========================

# ===== INTENTS =====
intents = discord.Intents.default()
intents.guilds = True
intents.members = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
guild = discord.Object(id=GUILD_ID)

# ===== LOG FILE (temporaneo su Railway) =====
def salva_log(testo):
    with open("log_pulizie.txt", "a", encoding="utf-8") as f:
        f.write(testo + "\n")

@client.event
async def on_ready():
    await tree.sync(guild=guild)
    print(f"✅ Bot online come {client.user}")

# ===== /pulizia =====
@tree.command(
    name="pulizia",
    description="Registra una pulizia completata",
    guild=guild
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
    await interaction.response.defer()

    ruolo = interaction.guild.get_role(ROLE_ID_AUTORIZZATO)
    if ruolo not in interaction.user.roles:
        await interaction.followup.send(
            "❌ Non hai il ruolo necessario.",
            ephemeral=True
        )
        return

    totale = bottiglie * prezzo
    data_ora = datetime.now().strftime("%d/%m/%Y • %H:%M")
    fattura_id = f"PZ-{random.randint(10000,99999)}"

    embed = discord.Embed(
        title="🧹 PULIZIA COMPLETATA",
        color=discord.Color.green()
    )

    embed.add_field(name="🆔 ID Fattura", value=fattura_id, inline=False)
    embed.add_field(name="👤 Utente", value=interaction.user.mention, inline=True)
    embed.add_field(name="👨‍👩‍👧 Famiglia", value=famiglia, inline=True)
    embed.add_field(name="🍾 Bottiglie", value=bottiglie, inline=True)
    embed.add_field(name="💵 Prezzo", value=f"{prezzo}$", inline=True)
    embed.add_field(name="💰 Totale", value=f"{totale}$", inline=True)
    embed.add_field(name="📅 Data & Ora", value=data_ora, inline=False)

    await interaction.followup.send(embed=embed)

    log_testo = (
        f"[{data_ora}] ID:{fattura_id} | {interaction.user} | "
        f"Famiglia:{famiglia} | Bottiglie:{bottiglie} | "
        f"Prezzo:{prezzo}$ | Totale:{totale}$"
    )

    salva_log(log_testo)

    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"🧾 **LOG PULIZIA**\n```{log_testo}```"
        )

# ===== /annulla =====
@tree.command(
    name="annulla",
    description="Annulla una pulizia tramite ID",
    guild=guild
)
@app_commands.describe(
    id_fattura="ID fattura da annullare"
)
async def annulla(interaction: discord.Interaction, id_fattura: str):
    await interaction.response.defer(ephemeral=True)

    ruolo = interaction.guild.get_role(ROLE_ID_AUTORIZZATO)
    if ruolo not in interaction.user.roles:
        await interaction.followup.send(
            "❌ Non autorizzato.",
            ephemeral=True
        )
        return

    data_ora = datetime.now().strftime("%d/%m/%Y • %H:%M")
    testo = f"[{data_ora}] ❌ ANNULLATA fattura {id_fattura} da {interaction.user}"

    salva_log(testo)

    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"🚫 **PULIZIA ANNULLATA**\n```{testo}```"
        )

    await interaction.followup.send(
        f"🚫 Pulizia **{id_fattura}** annullata.",
        ephemeral=True
    )

client.run(TOKEN)
