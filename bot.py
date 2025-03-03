import logging
import os
import subprocess
import random
import discord
from discord.ext import commands
from discord import app_commands
import asyncio

TOKEN = "YOUR_BOT_TOKEN"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# In-memory storage
user_tokens = {}  
database_file = "database.txt"
log_file = "vps_logs.txt"
SERVER_LIMIT = 100
whitelist_ids = {"853279989586853908"}  

# Utility Functions
def log_vps_event(event):
    with open(log_file, "a") as log:
        log.write(f"{event}\n")

# VPS Creation Command (Admin Only, No Docker)
@bot.tree.command(name="create", description="Creates a custom VPS instance (Admin Only).")
@app_commands.describe(member_name="Member name", cpu="CPU cores", ram="RAM (GB)", disk="Disk size (GB)")
async def create(interaction: discord.Interaction, member_name: str, cpu: int, ram: int, disk: int):
    userid = str(interaction.user.id)

    if userid not in whitelist_ids:
        await interaction.response.send_message("❌ You don't have permission to create a VPS!", ephemeral=True)
        return

    await interaction.response.send_message(f"Creating VPS for {member_name}...", ephemeral=True)

    try:
        # Install required packages
        subprocess.run("sudo apt update && sudo apt install -y tmate", shell=True, check=True)

        # Start tmate session
        session_name = f"vps-{random.randint(1000, 9999)}"
        subprocess.run(f"tmate -S /tmp/{session_name}.sock new-session -d", shell=True, check=True)
        subprocess.run(f"tmate -S /tmp/{session_name}.sock wait tmate-ready", shell=True, check=True)

        # Get SSH connection details
        ssh_command = subprocess.check_output(f"tmate -S /tmp/{session_name}.sock display -p '#{tmate_ssh}'", shell=True).decode().strip()

        log_vps_event(f"VPS {member_name} created by {interaction.user.name} (ID: {userid})")

        # Save VPS info to database
        with open(database_file, "a") as f:
            f.write(f"{userid}|{member_name}|{session_name}|{ssh_command}\n")

        await interaction.followup.send(f"✅ VPS `{member_name}` created!\n🔗 SSH Command: `{ssh_command}`", ephemeral=True)

    except subprocess.CalledProcessError as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

# List Active VPS Instances
@bot.tree.command(name="listvps", description="Lists all active VPS instances.")
async def list_vps(interaction: discord.Interaction):
    userid = str(interaction.user.id)

    if userid not in whitelist_ids:
        await interaction.response.send_message("❌ You do not have permission to list VPS instances!", ephemeral=True)
        return

    if not os.path.exists(database_file) or os.stat(database_file).st_size == 0:
        await interaction.response.send_message("⚠️ No active VPS instances found.", ephemeral=True)
        return

    embed = discord.Embed(title="🖥️ Active VPS Instances", color=0x00ff00)
    
    with open(database_file, "r") as f:
        for line in f:
            user_id, vps_name, session_name, ssh_command = line.strip().split("|")
            embed.add_field(name=f"🔹 {vps_name}", value=f"👤 Owner: <@{user_id}>\n🔗 SSH: `{ssh_command}`", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# Kill All VPS Command (Admin Only, No Docker)
@bot.tree.command(name="killvps", description="Kill all user VPS instances. (Admin Only)")
async def kill_vps(interaction: discord.Interaction):
    userid = str(interaction.user.id)

    if userid not in whitelist_ids:
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    await interaction.response.send_message("⚠️ **Stopping all VPS instances...**", ephemeral=True)

    subprocess.run("pkill -f tmate", shell=True, check=True)

    # Clear database
    open(database_file, "w").close()

    log_vps_event(f"⚠️ ALL VPS INSTANCES WERE REMOVED BY {interaction.user.name} (ID: {userid})")

    await interaction.followup.send("✅ **All VPS instances have been stopped.**", ephemeral=True)

@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    await bot.tree.sync()

bot.run(TOKEN)
