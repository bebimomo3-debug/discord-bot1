import os
import discord
from discord import app_commands
from datetime import datetime
import random

# ========= CONFIG =========
TOKEN = os.getenv("TOKEN")
GUILD_ID = 1462959158763585693
ROLE_ID_AUTORIZZATO = 1465798254263406858
LOG_CHANNEL_ID = 1465798160323444897
# ==========================

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
guild = discord.Object(id=GUILD_ID)

# ===== LOG FILE =====
def salva_log(testo):
    with open("log_pulizie.txt", "a", encoding="utf-8") as f:
        f.write(testo + "\n\n")

@client.event
async def on_ready():
    await tree.sync(guild=guild)
    print(f"✅ Bot online come {client.user}")

# ======================
#        /PULIZIA
# ======================
@tree.command(
    name="pulizia",
    description="Registra una pulizia",
    guild=guild
)
@app_commands.describe(
    famiglia="Nome famiglia",
    bottiglie="Numero bottiglie",
    prezzo="Prezzo per bottiglia"
)
async def pulizia(
    interaction: discord.Interaction,
    famiglia: str,
    bottiglie: int,
    prezzo: int
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
    fattura_id = f"PZ-{random.randint(10000, 99999)}"
    utente = interaction.user.mention  # 👈 TAG AUTOMATICO

    embed = discord.Embed(
        title="🧾 LOG PULIZIA",
        color=discord.Color.green()
    )

    embed.add_field(name="👤 Utente", value=utente, inline=False)
    embed.add_field(name="👨‍👩‍👧 Famiglia", value=famiglia, inline=False)
    embed.add_field(name="🍾 Bottiglie", value=bottiglie, inline=True)
    embed.add_field(name="💵 Prezzo", value=f"{prezzo}$", inline=True)
    embed.add_field(name="💰 Totale", value=f"{totale}$", inline=True)
    embed.add_field(name="🆔 ID", value=fattura_id, inline=False)
    embed.set_footer(text=data_ora)

    await interaction.followup.send(embed=embed)

    log_testo = (
        f"[{data_ora}]\n"
        f"Utente: {utente}\n"
        f"Famiglia: {famiglia}\n"
        f"Bottiglie: {bottiglie}\n"
        f"Prezzo: {prezzo}$\n"
        f"Totale: {totale}$\n"
        f"ID: {fattura_id}"
    )

    salva_log(log_testo)

    try:
        log_channel = await client.fetch_channel(LOG_CHANNEL_ID)
        await log_channel.send(embed=embed)
    except Exception as e:
        print("Errore log:", e)

# ======================
#        /ANNULLA
# ======================
@tree.command(
    name="annulla",
    description="Annulla una pulizia",
    guild=guild
)
@app_commands.describe(
    id_fattura="ID fattura",
    motivo="Motivo annullamento"
)
async def annulla(
    interaction: discord.Interaction,
    id_fattura: str,
    motivo: str
):
    await interaction.response.defer(ephemeral=True)

    ruolo = interaction.guild.get_role(ROLE_ID_AUTORIZZATO)
    if ruolo not in interaction.user.roles:
        await interaction.followup.send("❌ Non autorizzato.", ephemeral=True)
        return

    data_ora = datetime.now().strftime("%d/%m/%Y • %H:%M")
    utente = interaction.user.mention

    testo = (
        f"[{data_ora}]\n"
        f"Utente: {utente}\n"
        f"ID: {id_fattura}\n"
        f"Motivo: {motivo}"
    )

    salva_log(testo)

    embed = discord.Embed(
        title="🚫 PULIZIA ANNULLATA",
        color=discord.Color.red()
    )
    embed.add_field(name="👤 Utente", value=utente, inline=False)
    embed.add_field(name="🆔 ID", value=id_fattura, inline=False)
    embed.add_field(name="📝 Motivo", value=motivo, inline=False)
    embed.set_footer(text=data_ora)

    log_channel = await client.fetch_channel(LOG_CHANNEL_ID)
    await log_channel.send(embed=embed)

    await interaction.followup.send("🚫 Pulizia annullata.", ephemeral=True)

# ===== AVVIO =====
client.run(TOKEN)

