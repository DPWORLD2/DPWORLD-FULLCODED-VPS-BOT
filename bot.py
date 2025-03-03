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
user_tokens = {}  # Stores tokens for each user
database_file = "database.txt"
SERVER_LIMIT = 100
whitelist_ids = {"ADMIN_USER_ID"}  # Replace with actual admin IDs

# Utility Functions
def generate_random_port():
    return random.randint(20000, 30000)

def add_to_database(userid, container_name, ssh_command):
    with open(database_file, 'a') as f:
        f.write(f"{userid}|{container_name}|{ssh_command}\n")

def get_user_servers(userid):
    if not os.path.exists(database_file):
        return []
    with open(database_file, "r") as f:
        return [line.strip() for line in f if line.startswith(userid)]

def get_container_id_from_database(userid, container_name):
    servers = get_user_servers(userid)
    for server in servers:
        parts = server.split("|")
        if container_name in parts:
            return parts[1]
    return None

# VPS Creation Command
@bot.tree.command(name="create", description="Creates a custom VPS instance.")
@app_commands.describe(member_name="Member name", cpu="CPU cores", ram="RAM (GB)", disk="Disk size (GB)")
async def create(interaction: discord.Interaction, member_name: str, cpu: int, ram: int, disk: int):
    userid = str(interaction.user.id)

    # Check tokens
    if user_tokens.get(userid, 0) <= 0:
        await interaction.response.send_message("❌ You don't have enough tokens to create a VPS!", ephemeral=True)
        return

    if len(get_user_servers(userid)) >= SERVER_LIMIT:
        await interaction.response.send_message("❌ Instance limit reached.", ephemeral=True)
        return

    await interaction.response.send_message(f"Creating VPS for {member_name}...", ephemeral=True)

    image_name = "my-vps-image"
    ssh_port = generate_random_port()

    # Build Docker image if it doesn’t exist
    subprocess.run(f"docker build -t {image_name} .", shell=True, check=True)

    try:
        container_id = subprocess.check_output([
            "docker", "run", "-itd", "--privileged", "--cap-add=ALL",
            "--memory", f"{ram}g", "--cpus", str(cpu), "--name", member_name, "-p", f"{ssh_port}:22", image_name
        ]).strip().decode("utf-8")

        ssh_command = f"ssh root@<VPS_IP> -p {ssh_port}"  # Replace <VPS_IP> with actual IP

        add_to_database(userid, container_id, ssh_command)

        await interaction.followup.send(f"✅ VPS `{member_name}` created!\n🔗 SSH Command: `{ssh_command}`", ephemeral=True)

    except subprocess.CalledProcessError as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

# Give Tokens Command
@bot.tree.command(name="givetokens", description="Gives tokens to a user (Admin only).")
@app_commands.describe(user="User to give tokens", amount="Number of tokens to give")
async def givetokens(interaction: discord.Interaction, user: discord.Member, amount: int):
    if str(interaction.user.id) not in whitelist_ids:
        await interaction.response.send_message("❌ You don’t have permission to give tokens!", ephemeral=True)
        return

    user_tokens[str(user.id)] = user_tokens.get(str(user.id), 0) + amount
    await interaction.response.send_message(f"✅ Gave `{amount}` tokens to {user.mention}!", ephemeral=True)

# VPS Suspension Task (Every Hour)
async def deduct_tokens():
    while True:
        await asyncio.sleep(3600)  # Runs every hour
        for userid, tokens in list(user_tokens.items()):
            if tokens > 0:
                user_tokens[userid] -= 1  # Deduct 1 token per hour

            if user_tokens[userid] == 0:
                servers = get_user_servers(userid)
                for server in servers:
                    container_id = server.split("|")[1]
                    subprocess.run(["docker", "stop", container_id], check=True)  # Suspend VPS

                user = await bot.fetch_user(int(userid))
                if user:
                    await user.send("⚠️ Your VPS has been **suspended** due to insufficient tokens!")

# Start Task on Bot Startup
@bot.event
async def on_ready():
    print(f'✅ Bot is online as {bot.user}')
    await bot.tree.sync()
    bot.loop.create_task(deduct_tokens())

bot.run(TOKEN)
          
