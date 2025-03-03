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
whitelist_ids = {"ADMIN_USER_ID"}  # Replace with actual admin IDs

# Utility Functions
def generate_random_port():
    return random.randint(20000, 30000)

def add_to_database(userid, container_name, ssh_command):
    with open(database_file, 'a') as f:
        f.write(f"{userid}|{container_name}|{ssh_command}\n")

def remove_from_database(container_id):
    if not os.path.exists(database_file):
        return
    with open(database_file, "r") as f:
        lines = f.readlines()
    with open(database_file, "w") as f:
        for line in lines:
            if container_id not in line:
                f.write(line)

def get_user_servers(userid):
    if not os.path.exists(database_file):
        return []
    with open(database_file, "r") as f:
        return [line.strip() for line in f if line.startswith(userid)]

def log_vps_event(event):
    with open(log_file, "a") as log:
        log.write(f"{event}\n")

# VPS Creation Command (Admin Only)
@bot.tree.command(name="create", description="Creates a custom VPS instance (Admin Only).")
@app_commands.describe(member_name="Member name", cpu="CPU cores", ram="RAM (GB)", disk="Disk size (GB)")
async def create(interaction: discord.Interaction, member_name: str, cpu: int, ram: int, disk: int):
    userid = str(interaction.user.id)

    # Check if user is an admin
    if userid not in whitelist_ids:
        await interaction.response.send_message("❌ You don't have permission to create a VPS!", ephemeral=True)
        return

    if len(get_user_servers(userid)) >= SERVER_LIMIT:
        await interaction.response.send_message("❌ Instance limit reached.", ephemeral=True)
        return

    await interaction.response.send_message(f"Creating VPS for {member_name}...", ephemeral=True)

    image_name = "my-vps-image"
    ssh_port = generate_random_port()

    subprocess.run(f"docker build -t {image_name} .", shell=True, check=True)

    try:
        container_id = subprocess.check_output([
            "docker", "run", "-itd", "--privileged", "--cap-add=ALL",
            "--memory", f"{ram}g", "--cpus", str(cpu), "--name", member_name, "-p", f"{ssh_port}:22", image_name
        ]).strip().decode("utf-8")

        ssh_command = f"ssh root@<VPS_IP> -p {ssh_port}"  # Replace <VPS_IP> with actual IP

        add_to_database(userid, container_id, ssh_command)
        log_vps_event(f"VPS {member_name} created by {interaction.user.name} (ID: {userid})")

        await interaction.followup.send(f"✅ VPS `{member_name}` created!\n🔗 SSH Command: `{ssh_command}`", ephemeral=True)

    except subprocess.CalledProcessError as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

# Give Tokens Command (Admin Only)
@bot.tree.command(name="givetokens", description="Gives tokens to a user (Admin only).")
@app_commands.describe(user="User to give tokens", amount="Number of tokens to give")
async def givetokens(interaction: discord.Interaction, user: discord.Member, amount: int):
    if str(interaction.user.id) not in whitelist_ids:
        await interaction.response.send_message("❌ You don’t have permission to give tokens!", ephemeral=True)
        return

    user_tokens[str(user.id)] = user_tokens.get(str(user.id), 0) + amount
    await interaction.response.send_message(f"✅ Gave `{amount}` tokens to {user.mention}!", ephemeral=True)

# Kill All VPS Command (Admin Only)
@bot.tree.command(name="killvps", description="Kill all user VPS instances. (Admin Only)")
async def kill_vps(interaction: discord.Interaction):
    userid = str(interaction.user.id)

    if userid not in whitelist_ids:
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    await interaction.response.send_message("⚠️ **Stopping and removing all VPS instances...**", ephemeral=True)

    subprocess.run("docker rm -f $(docker ps -aq)", shell=True, check=True)

    with open(database_file, "w") as f:
        f.write("")

    log_vps_event(f"⚠️ ALL VPS INSTANCES WERE REMOVED BY {interaction.user.name} (ID: {userid})")

    await interaction.followup.send("✅ **All VPS instances have been stopped and deleted.**", ephemeral=True)

# Start Task on Bot Startup
@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    await bot.tree.sync()

bot.run(TOKEN)
