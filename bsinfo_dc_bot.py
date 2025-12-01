import discord
from discord.ext import commands
from discord import app_commands
import requests
from datetime import datetime

# --- Bot Setup ---
intents = discord.Intents.default()
intents.message_content = True  # Message content intent zaroori hai ! commands ke liye

bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = 'MTQzNDE3OTM1OTYzOTQ3MDE0Mg.G9sXA4.wZeBwXUuZrTKGjhyK_wIz73yq1vG7XoGX1PVYg'
@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    try:
        # Ye line hybrid commands (Slash commands) ko Discord pe register karti hai
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Sync Error: {e}")

# --- Main Command ---
@bot.hybrid_command(name="bsinfo", description="Get BombSquad account age & profile info")
@app_commands.describe(pb_id="Enter BombSquad PB ID (e.g., pb-IF4TV...)")
async def bsinfo(ctx, pb_id: str):
    # Bot ko 'Thinking...' state me daalo taaki timeout na ho
    await ctx.defer()

    # --- URLs ---
    # URL 1: Age/Created (Iska use hum Validation ke liye bhi karenge)
    age_url = f"https://bombsquadgame.com/accountquery?id={pb_id}"
    # URL 2: Profile Info
    info_url = f"http://bombsquadgame.com/bsAccountInfo?buildNumber=20258&accountID={pb_id}"

    # --- PART 1: Validate ID & Get Age ---
    created_str = "Unknown"
    age_str = "Unknown"

    try:
        response_age = requests.get(age_url)
        age_data = response_age.json()

        # Sabse pehle check: Kya ID galat hai?
        if "error" in age_data:
            # Agar error aaya to user ko batao aur yahi rok do
            error_msg = age_data["error"]
            await ctx.send(f"❌ **Error:** {error_msg} -> `{pb_id}`")
            return

        # Agar ID sahi hai, to Age calculate karo
        if "created" in age_data:
            c_list = age_data["created"]
            creation_time = datetime(*c_list) # List unpack kiya
            now = datetime.now()
            age = now - creation_time

            created_str = creation_time.strftime('%Y-%m-%d %H:%M:%S')
            age_str = f"{age.days} days ({round(age.days/365, 1)} years)"

    except Exception as e:
        await ctx.send(f"⚠️ **API Error (Age):** {e}")
        return

    # --- PART 2: Get Profile Details ---
    # Default variables taaki agar data na mile to code fate nahi
    account_names = "Unknown"
    profile_name = "Unknown"
    achievements = "0"
    char_name = "Unknown"
    is_global = "No"
    rank = "Unranked"
    trophies = "N/A"

    try:
        response_info = requests.get(info_url)
        if response_info.status_code == 200:
            info_data = response_info.json()

            # Kabhi kabhi valid ID par bhi info empty hoti hai, isliye check zaruri hai
            if info_data:
                # 1. Names
                if "accountDisplayStrings" in info_data:
                    # List ko comma string me badla
                    account_names = ', '.join(info_data["accountDisplayStrings"])
                    account_names = account_names.replace("", "<:cr:1271120318861283399>")
                    account_names = account_names.replace("", "<:bs_pheonix:1252440405115408517>")
                    account_names = account_names.replace("", "<:skull_bs:1252440222319247452>")
                    account_names = account_names.replace("", "<:bs_v2account:1251940770378682429>")
                    account_names = account_names.replace("", "<:de:1271120315056918579>")
                    account_names = account_names.replace("", "<:bs_pheonix:1252440405115408517>")

                if "profileDisplayString" in info_data:
                    profile_name = info_data["profileDisplayString"]
                    profile_name = profile_name.replace("", "<:cr:1271120318861283399>")
                    profile_name = profile_name.replace("", "<:bs_pheonix:1252440405115408517>")
                    profile_name = profile_name.replace("", "<:skull_bs:1252440222319247452>")
                    profile_name = profile_name.replace("", "<:bs_v2account:1251940770378682429>")
                    profile_name = profile_name.replace("", "<:de:1271120315056918579>")
                    profile_name = profile_name.replace("", "<:bs_pheonix:1252440405115408517>")

                # 2. Stats
                if "achievementsCompleted" in info_data:
                    achievements = str(info_data["achievementsCompleted"])

                # Rank null ho sakta hai, isliye safe check
                r_val = info_data.get("rank")
                if r_val is not None:
                    rank = f"#{r_val}"

                t_val = info_data.get("trophies")
                if t_val:
                    trophies = str(t_val)

                # 3. Character Profile
                if "profile" in info_:
                    p_data = info_data["profile"]
                    char_name = p_data.get("character", "Unknown")
                    if p_data.get("global", False):
                        is_global = "Yes"

    except Exception as e:
        print(f"Info API Error: {e}") 
        # Yahan hum return nahi karenge, kyunki Age data mil chuka hai, 
        # to hum partial info dikha sakte hain.

    # --- PART 3: Send Result (Embed) ---
    embed = discord.Embed(
        title="💣 BombSquad Account Details",
        description=f"Valid ID: `{pb_id}`",
        color=0xFFA500 # Orange color (BombSquad theme)
    )

    # Field 1: Identity
    embed.add_field(name="🆔 Identity", value=f"**Profile:** {profile_name}\n**Account:** {account_names}", inline=False)

    # Field 2: Stats (Rank & Trophies side-by-side)
    embed.add_field(name="🏆 Rank", value=rank, inline=True)
    embed.add_field(name="🎖️ Trophies", value=trophies, inline=True)
    embed.add_field(name="🎯 Achievements", value=achievements, inline=True)

    # Field 3: Character Info
    embed.add_field(name="👾 Character", value=f"{char_name} (Global: {is_global})", inline=False)

    # Field 4: Timeline (Age logic from your code)
    embed.add_field(name="📅 Timeline", value=f"**Created:** {created_str}\n**Age:** {age_str}", inline=False)

    # Footer
    embed.set_footer(text=f"Checked by {ctx.author.display_name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)

# Bot Run
bot.run(TOKEN)
