import discord
from discord.ext import commands
from discord import app_commands
import requests
from datetime import datetime
import asyncio
import typing
import datetime



# --- Bot Setup ---
intents = discord.Intents.default()
intents.members = True # ⚠️ ISKE BINA OWNER NONE RAHEGA
intents.message_content = True  # Message content intent zaroori hai ! commands ke liye

bot = commands.Bot(command_prefix="!", intents=intents)
TOKEN = 'MTQzNDE3OTM1OTYzOTQ3MDE0Mg.GnMEJ2.mSRXrT4u_5t9OIotKbI6V2SdbUv7FNJhNnf-XE'
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
                if "profile" in info_data:
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
    embed.set_thumbnail(url="https://images-ext-1.discordapp.net/external/E05QxTWwvq0iRyp13KQ39SCcHVg-5dnGfCI_Sh15ynU/%3Fsize%3D128/https/cdn.discordapp.com/avatars/1321807619274575872/d67b7c57283b267c9dd42f8a94561910.webp")
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

#delete msg command

@bot.hybrid_command(
    name="sdelete",
    description="Slowly delete messages with 1s gap.",
    help="""
    Usage:
    /sdelete limit:10
    /sdelete member:@User limit:20
    /sdelete msg_id:123456789
    """
)
@discord.app_commands.describe(
    limit="(Default: 10)",
    member="witch member's msg",
    msg_id="provid any message id to start deleteing after that msg"
)
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True, read_message_history=True)
async def slow_delete(
    ctx: commands.Context, 
    limit: int = 10, 
    member: discord.Member = None, 
    msg_id: str = None  # msg_id ko string rakha hai taaki bada number crash na kare
):
    # Defer response to avoid timeout
    await ctx.defer()

    # Prefix command message delete logic
    if ctx.prefix != "/":
        try:
            await ctx.message.delete()
        except:
            pass

    # Logic to handle arguments
    after_msg_obj = None
    
    if msg_id:
        try:
            # Convert string ID to Object
            after_msg_obj = discord.Object(id=int(msg_id))
        except ValueError:
            await ctx.send("❌ Invalid Message ID provided.", ephemeral=True)
            return

    # Status Message
    status_text = f"🗑️ **Deletion started...**\nLimit: `{limit}`"
    if member:
        status_text += f"\nFilter: {member.mention}"
    
    status_msg = await ctx.send(status_text)
    
    # Fetch Messages
    # Agar 'after' (msg_id) diya hai to wahan se history lo
    if after_msg_obj:
        history = ctx.channel.history(limit=limit, after=after_msg_obj)
    else:
        history = ctx.channel.history(limit=limit)

    deleted_count = 0

    # Deletion Loop
    async for msg in history:
        # Skip status msg and pinned msgs
        if msg.id == status_msg.id or msg.pinned:
            continue

        # Filter by Member if provided
        if member and msg.author != member:
            continue
            
        try:
            await msg.delete()
            deleted_count += 1
            await asyncio.sleep(1) # 1s Gap (Rate Limit Safe)
        except discord.Forbidden:
            await ctx.send("❌ Permission Denied!", ephemeral=True)
            return
        except discord.HTTPException:
            continue # Skip failed deletes

    # Completion
    await status_msg.edit(content=f"✅ **Done!** Deleted `{deleted_count}` messages.")
    await asyncio.sleep(3)
    try:
        await status_msg.delete()
    except:
        pass

@slow_delete.error
async def slow_delete_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You need `Manage Messages` permission.", ephemeral=True)
    else:
        await ctx.send(f"Error: {error}", ephemeral=True)


#user info cmd 

@bot.hybrid_command(name="userinfo", description="Get detailed information about a user.")
@app_commands.describe(member="Select a member to view info (Leave empty for yourself)")
async def userinfo(ctx, member: discord.Member = None):
    # Agar member select nahi kiya to khud ka info dikhao
    if member is None:
        member = ctx.author

    # Embed Setup
    embed = discord.Embed(
        title=f"👤 User Info: {member.display_name}",
        color=member.color if member.color != discord.Color.default() else discord.Color.blue(),
        timestamp=datetime.datetime.now()
    )

    # Thumbnail (Avatar)
    embed.set_thumbnail(url=member.display_avatar.url)

    # --- Basic Info ---
    embed.add_field(name="🆔 User ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="📛 Username", value=f"{member.name}", inline=True)
    embed.add_field(name="🏷️ Nickname", value=f"{member.nick if member.nick else 'None'}", inline=True)

    # --- Dates (Dynamic Timestamps) ---
    # Created At
    created_ts = int(member.created_at.timestamp())
    embed.add_field(
        name="📅 Account Created", 
        value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)", 
        inline=False
    )
    
    # Joined At
    if member.joined_at:
        joined_ts = int(member.joined_at.timestamp())
        embed.add_field(
            name="📥 Joined Server", 
            value=f"<t:{joined_ts}:D> (<t:{joined_ts}:R>)", 
            inline=False
        )

    # --- Roles Info ---
    # @everyone role ko list se hata rahe hain aur reverse kar rahe hain (Highest role first)
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    roles.reverse()
    
    # Agar roles zyada hain to truncate karo
    role_str = ", ".join(roles) if roles else "No Roles"
    if len(role_str) > 1024:
        role_str = role_str[:1020] + "..."

    embed.add_field(name=f"🎭 Roles [{len(roles)}]", value=role_str, inline=False)
    
    # --- Top Role & Permissions ---
    embed.add_field(name="🔝 Top Role", value=member.top_role.mention, inline=True)
    embed.add_field(name="🤖 Bot?", value="Yes" if member.bot else "No", inline=True)

    # Footer
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)



#server info cmd

@bot.hybrid_command(name="serverinfo", description="Get detailed information about this server.")
async def serverinfo(ctx):
    guild = ctx.guild
    
    # Embed Setup
    embed = discord.Embed(
        title=f"ℹ️ Server Info: {guild.name}",
        description=f"{guild.description if guild.description else 'No description set.'}",
        color=discord.Color.gold(),
        timestamp=datetime.datetime.now()
    )

    # Icon & Banner
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    if guild.banner:
        embed.set_image(url=guild.banner.url)

    # --- General Info ---
    embed.add_field(name="👑 Owner", value=f"{guild.owner.mention}", inline=True)
    embed.add_field(name="🆔 Server ID", value=f"`{guild.id}`", inline=True)
    
    # Creation Date
    created_ts = int(guild.created_at.timestamp())
    embed.add_field(name="📅 Created On", value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)", inline=True)

    # --- Member Stats ---
    # Note: Accurate counts ke liye 'intents.members = True' zaruri hai
    total_members = guild.member_count
    # Simple count logic
    bots = sum(1 for m in guild.members if m.bot)
    humans = total_members - bots
    
    embed.add_field(
        name="👥 Members", 
        value=f"**Total:** {total_members}\n👨 **Humans:** {humans}\n🤖 **Bots:** {bots}", 
        inline=True
    )

    # --- Channel Stats ---
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    
    embed.add_field(
        name="💬 Channels", 
        value=f"**Text:** {text_channels}\n**Voice:** {voice_channels}\n**Categories:** {categories}", 
        inline=True
    )

    # --- Other Stats ---
    embed.add_field(name="🎭 Roles", value=f"{len(guild.roles)}", inline=True)
    embed.add_field(name="😀 Emojis", value=f"{len(guild.emojis)}", inline=True)
    embed.add_field(
        name="🚀 Boost Status", 
        value=f"Level {guild.premium_tier} ({guild.premium_subscription_count} Boosts)", 
        inline=True
    )

    # Footer
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

#avatar cmd

@bot.hybrid_command(name="av", aliases=["avatar"], description="View a user's large avatar.")
@app_commands.describe(member="Select user (Empty for your own)")
async def avatar(ctx, member: discord.Member = None):
    # Agar member select nahi kiya, to khud ka avatar dikhao
    if member is None:
        member = ctx.author

    # Embed Setup
    embed = discord.Embed(
        title=f"🖼️ Avatar: {member.display_name}",
        color=member.color if member.color != discord.Color.default() else discord.Color.purple(),
        timestamp=datetime.datetime.now()
    )

    # Avatar URL (High Quality)
    # display_avatar automatically handles server-specific avatars vs global avatars
    main_url = member.display_avatar.url
    
    embed.set_image(url=main_url)

    # Download Links Generation
    formats = []
    formats.append(f"[PNG]({member.display_avatar.with_format('png').url})")
    formats.append(f"[JPG]({member.display_avatar.with_format('jpg').url})")
    formats.append(f"[WEBP]({member.display_avatar.with_format('webp').url})")
    
    # Agar avatar animated (GIF) hai, to GIF link add karo
    if member.display_avatar.is_animated():
        formats.append(f"[GIF]({member.display_avatar.with_format('gif').url})")

    embed.description = f"**Download:** {' | '.join(formats)}"

    # Footer
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)

    await ctx.send(embed=embed)

#kick cmd

@bot.hybrid_command(name="kick", description="Kick a member from the server.")
@app_commands.describe(member="The user you want to kick", reason="Reason for the kick (Optional)")
@commands.has_permissions(kick_members=True)
@commands.bot_has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    
    # 1. Prevent Self-Kick
    if member.id == ctx.author.id:
        await ctx.send("❌ You cannot kick yourself.", ephemeral=True)
        return

    # 2. Check Role Hierarchy (Mod vs Target)
    # The command user must have a higher top role than the target (unless user is Owner)
    if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("🚫 You cannot kick this user due to role hierarchy.", ephemeral=True)
        return

    # 3. Check Bot Hierarchy (Bot vs Target)
    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send("🚫 I cannot kick this user because their role is higher than or equal to mine.", ephemeral=True)
        return

    # 4. Attempt to DM the user before kicking
    try:
        dm_embed = discord.Embed(
            title=f"Kicked from {ctx.guild.name}",
            color=discord.Color.red(),
            timestamp=datetime.datetime.now()
        )
        dm_embed.add_field(name="Reason", value=reason)
        dm_embed.add_field(name="Moderator", value=ctx.author.name)
        await member.send(embed=dm_embed)
    except discord.Forbidden:
        pass # User has DMs closed, ignore and proceed

    # 5. Execute Kick
    try:
        await member.kick(reason=f"Kicked by {ctx.author} | Reason: {reason}")

        # 6. Success Embed (Public Log)
        embed = discord.Embed(
            title="👢 Member Kicked",
            color=discord.Color.brand_red(),
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        embed.add_field(name="User", value=f"{member.mention}\n(`{member.id}`)", inline=True)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Reason", value=f"``````", inline=False)
        
        embed.set_footer(text=f"Action taken by {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ An error occurred while kicking: {e}", ephemeral=True)

# Error Handler for this specific command
@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You do not have permission to use this command (`Kick Members`).", ephemeral=True)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("🚫 I do not have permission to kick members. Please check my role permissions.", ephemeral=True)
    else:
        await ctx.send(f"⚠️ An unexpected error occurred: {error}", ephemeral=True)


#spam msg cmd

@bot.hybrid_command(name="repeat", description="Repeat a message multiple times safely.")
@app_commands.describe(message="The message to send", amount="How many times (Max 50)")
@commands.has_permissions(manage_messages=True) # Sirf Mods use kar sakein
async def repeat(ctx, message: str, amount: int):
    
    # 1. Safety Limits
    if amount > 50:
        await ctx.send("⚠️ **Safety Limit:** You cannot send more than 50 messages at once to avoid a bot ban.", ephemeral=True)
        return
    
    if amount < 1:
        await ctx.send("⚠️ Amount must be at least 1.", ephemeral=True)
        return

    # 2. Confirmation Embed
    embed = discord.Embed(
        title="🔄 Broadcast Started",
        description=f"**Message:** {message}\n**Count:** {amount}\n**Delay:** 1.5s (Safe Mode)",
        color=discord.Color.green()
    )
    status_msg = await ctx.send(embed=embed)

    # 3. Execution Loop
    for i in range(amount):
        try:
            await ctx.channel.send(message)
            
            # ⚠️ VITAL: 1.5 Seconds delay to prevent API Ban
            await asyncio.sleep(1.5) 
            
        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to send messages here.", ephemeral=True)
            return
        except discord.HTTPException:
            await ctx.send("❌ API Error. Stopping broadcast.", ephemeral=True)
            return

    # 4. Completion
    try:
        completion_embed = discord.Embed(
            title="✅ Broadcast Complete",
            description=f"Sent {amount} messages successfully.",
            color=discord.Color.blue()
        )
        await status_msg.edit(embed=completion_embed)
        # Status message delete after 5 seconds
        await asyncio.sleep(5)
        await status_msg.delete()
    except:
        pass

@repeat.error
async def repeat_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You need `Manage Messages` permission to use this.", ephemeral=True)

#dm cmd 

@bot.hybrid_command(name="dm", description="Send a direct message to a user.")
@app_commands.describe(
    member="The user to DM",
    message="The content of the message",
    use_embed="Send as an Embed? (Default: False)",
    show_server="Show server name in footer/text? (Default: False)",
    mention="Mention the user in the DM? (Default: False)"
)
@commands.has_permissions(manage_messages=True) # Restricted to Mods
async def dm(
    ctx, 
    member: discord.Member, 
    message: str, 
    use_embed: bool = False, 
    show_server: bool = False, 
    mention: bool = False
):
    
    # 1. Prevent DMing Bots
    if member.bot:
        await ctx.send("❌ I cannot DM bots.", ephemeral=True)
        return

    # 2. Defer (Processing might take a moment)
    await ctx.defer(ephemeral=True)

    # 3. Construct the Payload
    try:
        # A. IF EMBED IS TRUE
        if use_embed:
            embed = discord.Embed(
                description=message,
                color=discord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            # Optional: Show Server Name in Footer
            if show_server:
                embed.set_footer(text=f"Sent from: {ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
            
            # Optional: Mention (We put the mention outside the embed usually, or inside description)
            content_str = member.mention if mention else None
            
            await member.send(content=content_str, embed=embed)

        # B. IF EMBED IS FALSE (Text Mode)
        else:
            final_msg = message
            
            # Optional: Mention
            if mention:
                final_msg = f"{member.mention}\n{final_msg}"
            
            # Optional: Show Server Name
            if show_server:
                final_msg += f"\n\n**From Server:** {ctx.guild.name}"
                
            await member.send(final_msg)

        # 4. Success Confirmation
        await ctx.send(f"✅ Message sent to **{member}** successfully.", ephemeral=True)

    except discord.Forbidden:
        # 5. Error: DMs Closed
        await ctx.send(f"❌ Failed to DM **{member}**. Their DMs are likely closed or privacy settings block me.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}", ephemeral=True)

@dm.error
async def dm_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You need `Manage Messages` permission to use this.", ephemeral=True)

#say cmd 


@bot.hybrid_command(name="say", description="Make the bot send a message or an embed.")
@app_commands.describe(
    message="Plain text content (Ignored if Use Embed is True)",
    use_embed="Send as an Embed? (Default: False)",
    title="Embed Title (Optional)",
    description="Embed Description (Optional)"
)
@commands.has_permissions(manage_messages=True) # Restricted to Mods/Admins
async def say(
    ctx, 
    message: str = None, 
    use_embed: bool = False, 
    title: str = None, 
    description: str = None
):
    # 1. Clean up the trigger command (If using prefix like !say)
    if ctx.prefix != "/":
        try:
            await ctx.message.delete()
        except:
            pass

    # 2. LOGIC FOR EMBED MODE
    if use_embed:
        # Validation: Ensure at least a title or description is provided
        if not title and not description:
            await ctx.send("❌ **Error:** You must provide a `title` or `description` when using Embed mode.", ephemeral=True)
            return

        # Create the Embed (No Timestamp, clean footer)
        embed = discord.Embed(
            title=title if title else None,
            description=description if description else None,
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)

    # 3. LOGIC FOR TEXT MODE
    else:
        # Validation: Ensure a message is provided
        if not message:
            await ctx.send("❌ **Error:** Please provide a `message` argument.", ephemeral=True)
            return

        # Send Plain Text
        await ctx.send(message)

# Error Handler
@say.error
async def say_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You do not have permission (`Manage Messages`) to use this command.", ephemeral=True)
    else:
        await ctx.send(f"⚠️ An unexpected error occurred: {error}", ephemeral=True)

# addrole/removerole cmd 
# --- ADD ROLE COMMAND ---
@bot.hybrid_command(name="addrole", description="Assign a role to a member.")
@app_commands.describe(
    member="Select the member",
    role="Select the role from the list"
)
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def add_role(ctx, member: discord.Member, role: discord.Role):
    
    # 1. Hierarchy Check (User vs Role)
    # Prevent user from adding a role higher than their own
    if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("🚫 You cannot assign a role that is higher than or equal to your own top role.", ephemeral=True)
        return

    # 2. Hierarchy Check (Bot vs Role)
    # Prevent bot from trying to add a role higher than itself
    if role >= ctx.guild.me.top_role:
        await ctx.send("🚫 I cannot assign this role because it is higher than my own role.", ephemeral=True)
        return

    # 3. Check if Managed (Integration roles like Server Booster / Bot roles)
    if role.is_default() or role.managed:
        await ctx.send("🚫 Cannot assign default or integration roles manually.", ephemeral=True)
        return

    # 4. Check if user already has the role
    if role in member.roles:
        await ctx.send(f"⚠️ **{member.display_name}** already has the **{role.name}** role.", ephemeral=True)
        return

    # 5. Execution
    try:
        await member.add_roles(role, reason=f"Added by {ctx.author}")
        
        # Success Embed
        embed = discord.Embed(
            description=f"✅ **Role Added**\n\n👤 **User:** {member.mention}\n🛡️ **Role:** {role.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Failed to add role: {e}", ephemeral=True)


# --- REMOVE ROLE COMMAND ---
@bot.hybrid_command(name="removerole", description="Remove a role from a member.")
@app_commands.describe(
    member="Select the member",
    role="Select the role from the list"
)
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def remove_role(ctx, member: discord.Member, role: discord.Role):

    # 1. Hierarchy Check (User vs Role)
    if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("🚫 You cannot remove a role that is higher than or equal to your own top role.", ephemeral=True)
        return

    # 2. Hierarchy Check (Bot vs Role)
    if role >= ctx.guild.me.top_role:
        await ctx.send("🚫 I cannot remove this role because it is higher than my own role.", ephemeral=True)
        return

    # 3. Check if user actually has the role
    if role not in member.roles:
        await ctx.send(f"⚠️ **{member.display_name}** does not have the **{role.name}** role.", ephemeral=True)
        return

    # 4. Execution
    try:
        await member.remove_roles(role, reason=f"Removed by {ctx.author}")
        
        # Success Embed
        embed = discord.Embed(
            description=f"✅ **Role Removed**\n\n👤 **User:** {member.mention}\n🛡️ **Role:** {role.mention}",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Failed to remove role: {e}", ephemeral=True)

# Shared Error Handler
@add_role.error
@remove_role.error
async def role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You need `Manage Roles` permission to use this command.", ephemeral=True)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("🚫 I do not have `Manage Roles` permission. Please check my server settings.", ephemeral=True)

#createrole cmd 
# Permission Presets (Selection List ke liye)
class RolePermissions(discord.app_commands.Choice[int]):
    pass

@bot.hybrid_command(name="createrole", description="Create a new role with specific permissions.")
@app_commands.describe(
    name="Name of the new role",
    color="Hex Color Code (e.g. #FF0000) or Type 'Red', 'Blue'",
    permission_level="Select permission level from the list"
)
@app_commands.choices(permission_level=[
    discord.app_commands.Choice(name="Default (No Perms)", value=0),
    discord.app_commands.Choice(name="Moderator (Kick/Ban/Manage Msg)", value=1),
    discord.app_commands.Choice(name="Administrator (Full Access)", value=2)
])
@commands.has_permissions(manage_roles=True)
async def create_role(ctx, name: str, color: str = None, permission_level: discord.app_commands.Choice[int] = 0):
    
    # 1. Color Parser
    role_color = discord.Color.default()
    if color:
        try:
            if color.startswith("#"):
                color = color.replace("#", "")
                role_color = discord.Color(int(color, 16))
            elif color.lower() == "red": role_color = discord.Color.red()
            elif color.lower() == "blue": role_color = discord.Color.blue()
            elif color.lower() == "green": role_color = discord.Color.green()
            elif color.lower() == "yellow": role_color = discord.Color.gold()
            elif color.lower() == "orange": role_color = discord.Color.orange()
            else:
                role_color = discord.Color.default()
        except:
            pass

    # 2. Permission Setup (FIXED HERE)
    # Pehle blank permissions object banaya
    perms = discord.Permissions.none() 
    perm_desc = "Default (No Special Perms)"

    # Value extract karna zaruri hai
    selected_value = permission_level.value if isinstance(permission_level, discord.app_commands.Choice) else permission_level

    if selected_value == 1: # Moderator
        perms.kick_members = True
        perms.ban_members = True
        perms.manage_messages = True
        perms.mute_members = True
        perms.read_messages = True
        perms.send_messages = True
        perm_desc = "Moderator"
        
    elif selected_value == 2: # Admin
        perms.administrator = True
        perm_desc = "Administrator"
    
    else: # Default (Basic Member)
        # Basic permissions (Send msg, Read history etc.)
        perms.read_messages = True
        perms.send_messages = True
        perms.read_message_history = True
        perms.connect = True
        perms.speak = True

    # 3. Execution
    try:
        new_role = await ctx.guild.create_role(
            name=name, 
            permissions=perms, 
            color=role_color, 
            reason=f"Created by {ctx.author}"
        )

        # Success Embed
        embed = discord.Embed(
            title="✨ Role Created Successfully",
            color=new_role.color if new_role.color.value != 0 else discord.Color.green()
        )
        embed.add_field(name="Name", value=new_role.mention, inline=True)
        embed.add_field(name="Level", value=perm_desc, inline=True)
        embed.add_field(name="Color", value=str(new_role.color), inline=True)
        
        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ I do not have permission to create roles.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)

#delete role cmd
@bot.hybrid_command(name="deleterole", description="Delete an existing role from the server.")
@app_commands.describe(role="Select the role to delete from the list")
@commands.has_permissions(manage_roles=True)
@commands.bot_has_permissions(manage_roles=True)
async def delete_role(ctx, role: discord.Role):
    
    # 1. Safety Check: Managed Roles
    # Integration roles (Bot roles, Booster roles) delete nahi hone chahiye
    if role.managed:
        await ctx.send("🚫 Cannot delete managed integration roles (like Bot roles or Booster roles).", ephemeral=True)
        return

    # 2. Safety Check: Default Role
    # @everyone role delete nahi ho sakta
    if role.is_default():
        await ctx.send("🚫 Cannot delete the default @everyone role.", ephemeral=True)
        return

    # 3. Hierarchy Check (User vs Role)
    # User apne se upar ka role delete nahi kar sakta
    if role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
        await ctx.send("🚫 You cannot delete a role that is higher than or equal to your own top role.", ephemeral=True)
        return

    # 4. Hierarchy Check (Bot vs Role)
    # Bot apne se upar ka role delete nahi kar sakta
    if role >= ctx.guild.me.top_role:
        await ctx.send("🚫 I cannot delete this role because it is higher than my own role.", ephemeral=True)
        return

    # 5. Execution
    try:
        role_name = role.name # Delete hone ke baad role.name gayab ho sakta hai, pehle save kar lo
        await role.delete(reason=f"Deleted by {ctx.author}")

        # Success Embed
        embed = discord.Embed(
            description=f"🗑️ **Role Deleted**\n\nThe role **{role_name}** has been permanently removed.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ I do not have permission to delete this role.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ Error occurred: {e}", ephemeral=True)

# Error Handler
@delete_role.error
async def delete_role_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You need `Manage Roles` permission to use this.", ephemeral=True)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("🚫 I need `Manage Roles` permission to do this.", ephemeral=True)

#mute/unmute cmd 


# --- HELPER FUNCTION (MUST BE AT THE TOP) ---
def parse_time(time_str: str):
    """Converts time strings like '2m', '1h' to seconds."""
    if not time_str: return None
    time_str = time_str.lower()
    try:
        if time_str.endswith("s"): return int(time_str[:-1])
        if time_str.endswith("m"): return int(time_str[:-1]) * 60
        if time_str.endswith("h"): return int(time_str[:-1]) * 3600
        if time_str.endswith("d"): return int(time_str[:-1]) * 86400
        if time_str.isdigit(): return int(time_str) * 60 # Default to minutes
    except ValueError:
        return None
    return None


# --- MUTE COMMAND (Corrected) ---
@bot.hybrid_command(name="mute", description="Mute a member using a role.")
@app_commands.describe(
    member="The member to mute",
    duration="Duration (e.g. 10m, 1h). Default: 2m",
    reason="Reason for mute"
)
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str = "2m", reason: str = "No reason provided"):

    # 1. SETUP MUTED ROLE
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if not muted_role:
        try:
            msg = await ctx.send("⚙️ 'Muted' role not found. Creating it now...")
            muted_role = await ctx.guild.create_role(name="Muted", reason="Auto-created by Bot")
            
            # Set Permissions for all channels
            for channel in ctx.guild.channels:
                try:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)
                except:
                    pass
            await msg.edit(content="✅ 'Muted' role created and configured.")
        except Exception as e:
            await ctx.send(f"❌ Failed to create Muted role: {e}")
            return

    # 2. ASSIGN ROLE
    try:
        if muted_role in member.roles:
            await ctx.send("⚠️ Member is already muted.", ephemeral=True)
            return
            
        await member.add_roles(muted_role, reason=reason)
        
        # 3. PARSE TIME (Ab ye function defined hai to error nahi aayega)
        seconds = parse_time(duration) 
        if not seconds: seconds = 120 # Fallback 2 mins if invalid
        
        embed = discord.Embed(
            description=f"🔇 **{member.mention} has been Muted.**\n⏱️ Duration: {duration}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

        # 4. SCHEDULE UNMUTE
        await asyncio.sleep(seconds)
        
        # Check if still muted before unmuting
        # Fetch member again to get updated roles
        member = ctx.guild.get_member(member.id)
        if member and muted_role in member.roles:
            await member.remove_roles(muted_role, reason="Mute duration expired")
            try:
                await ctx.channel.send(f"🔊 **{member.mention}** has been unmuted (Time expired).")
            except:
                pass

    except discord.Forbidden:
        await ctx.send("❌ Permission Error: Check bot hierarchy.", ephemeral=True)
    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)

# --- UNMUTE COMMAND ---
@bot.hybrid_command(name="unmute", description="Unmute a member.")
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role and muted_role in member.roles:
        await member.remove_roles(muted_role, reason=f"Unmuted by {ctx.author}")
        await ctx.send(f"🔊 **{member.mention}** has been unmuted.")
    else:
        await ctx.send("⚠️ User is not muted.", ephemeral=True)

# --- EVENT LISTENER (PING REPLY) ---
@bot.event
async def on_message(message):
    if message.author.bot: return

    if message.mentions:
        muted_role = discord.utils.get(message.guild.roles, name="Muted")
        if muted_role:
            for user in message.mentions:
                if muted_role in user.roles:
                    embed = discord.Embed(
                        description=f"🔇 **{user.display_name}** is currently muted and cannot reply.",
                        color=discord.Color.orange()
                    )
                    await message.reply(embed=embed, delete_after=5)
                    break 

    await bot.process_commands(message)


#lock/unlock channel cmd 
# --- SAFE LOCK COMMAND ---
@bot.hybrid_command(name="lock", description="Lock channel for all non-admin roles.")
@app_commands.describe(channel="Channel to lock (Optional)")
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
    target_channel = channel if channel else ctx.channel
    
    await ctx.send(f"🔒 Processing lock for {target_channel.mention}, please wait...", delete_after=3)

    # 1. Get Current Overwrites (Taaki purani settings delete na hon)
    overwrites = target_channel.overwrites

    # 2. Update Overwrites in Memory (No API Calls yet)
    # Pehle @everyone ko lock karo
    default_role = ctx.guild.default_role
    
    # Get existing permissions for @everyone or create new
    overwrite = overwrites.get(default_role, discord.PermissionOverwrite())
    overwrite.send_messages = False
    overwrites[default_role] = overwrite

    # Baaki roles ko bhi lock karo
    for role in ctx.guild.roles:
        # Skip Admins and Bots
        if role.permissions.administrator or role.managed:
            continue
            
        # Update existing overwrite or create new
        overwrite = overwrites.get(role, discord.PermissionOverwrite())
        overwrite.send_messages = False
        overwrites[role] = overwrite

    try:
        # 3. SINGLE API CALL (Rate Limit Safe)
        # Ek baar me sab apply hoga
        await target_channel.edit(overwrites=overwrites)
        
        # Simple Text Message (No Embed)
        await ctx.send(f"🔒 **{target_channel.name}** has been locked for all non-admin roles.\nOnly **Administrators** can send messages now.")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)


# --- SAFE UNLOCK COMMAND ---
@bot.hybrid_command(name="unlock", description="Unlock channel and reset role overrides.")
@app_commands.describe(channel="Channel to unlock (Optional)")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    target_channel = channel if channel else ctx.channel
    
    await ctx.send(f"🔓 Processing unlock for {target_channel.mention}, please wait...", delete_after=3)

    # 1. Get Current Overwrites
    overwrites = target_channel.overwrites

    # 2. Update Overwrites in Memory
    # @everyone ko unlock karo
    default_role = ctx.guild.default_role
    overwrite = overwrites.get(default_role, discord.PermissionOverwrite())
    overwrite.send_messages = True
    overwrites[default_role] = overwrite

    # Baaki roles ka restriction HATA DO (Reset to None/Default)
    for role in ctx.guild.roles:
        if role.permissions.administrator or role.managed:
            continue
        
        # Agar is role ka overwrite exist karta hai
        if role in overwrites:
            overwrite = overwrites[role]
            # 'None' ka matlab hai restriction hata do
            overwrite.send_messages = None 
            overwrites[role] = overwrite

    try:
        # 3. SINGLE API CALL
        await target_channel.edit(overwrites=overwrites)
        
        # Simple Text Message (No Embed)
        await ctx.send(f"🔓 **{target_channel.name}** has been unlocked.\nMembers can speak now.")

    except Exception as e:
        await ctx.send(f"❌ Error: {e}", ephemeral=True)

#ban/unbann cmd 

# --- BAN COMMAND ---
@bot.hybrid_command(name="ban", description="Ban a user from the server (Supports User ID).")
@app_commands.describe(user="Select user or enter User ID", reason="Reason for the ban")
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def ban(ctx, user: discord.User, reason: str = "No reason provided"):
    
    # 1. Check if User is Already Banned
    try:
        await ctx.guild.fetch_ban(user)
        # Agar fetch_ban success hua, iska matlab user pehle se banned hai
        await ctx.send(f"⚠️ **{user.name}** is already banned from this server.", ephemeral=True)
        return
    except discord.NotFound:
        pass # User banned nahi hai, proceed karein...

    # 2. Hierarchy Check (Agar user server ke andar hai)
    member = ctx.guild.get_member(user.id)
    if member:
        # Prevent self-ban
        if member.id == ctx.author.id:
            await ctx.send("❌ You cannot ban yourself.", ephemeral=True)
            return
        # User vs Target
        if member.top_role >= ctx.author.top_role and ctx.author.id != ctx.guild.owner_id:
            await ctx.send("🚫 You cannot ban this user due to role hierarchy.", ephemeral=True)
            return
        # Bot vs Target
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send("🚫 I cannot ban this user because their role is higher than mine.", ephemeral=True)
            return

    # 3. Execution
    try:
        # Try to DM the user before banning
        try:
            embed_dm = discord.Embed(
                title=f"🚫 Banned from {ctx.guild.name}",
                description=f"Reason: {reason}",
                color=discord.Color.red()
            )
            await user.send(embed=embed_dm)
        except:
            pass # DM fail hone par ignore karein

        # Perform Ban
        await ctx.guild.ban(user, reason=f"Banned by {ctx.author} | {reason}")

        # Success Embed
        embed = discord.Embed(
            title="🔨 Member Banned",
            description=f"**User:** {user.mention} (`{user.id}`)\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
            color=discord.Color.dark_red(),
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Failed to ban user: {e}", ephemeral=True)


# --- UNBAN COMMAND ---
@bot.hybrid_command(name="unban", description="Unban a user using their ID.")
@app_commands.describe(user="Select user or enter User ID", reason="Reason for the unban")
@commands.has_permissions(ban_members=True)
@commands.bot_has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, reason: str = "No reason provided"):
    
    # 1. Check if User is ACTUALLY Banned
    try:
        await ctx.guild.fetch_ban(user)
        # Agar yahan error nahi aaya, matlab user banned hai. Good to go.
    except discord.NotFound:
        # Agar NotFound error aaya, matlab user banned nahi hai
        await ctx.send(f"⚠️ **{user.name}** is already unbanned (or was never banned).", ephemeral=True)
        return

    # 2. Execution
    try:
        await ctx.guild.unban(user, reason=f"Unbanned by {ctx.author} | {reason}")

        # Success Embed
        embed = discord.Embed(
            title="🤝 Member Unbanned",
            description=f"**User:** {user.mention} (`{user.id}`)\n**Reason:** {reason}\n**Moderator:** {ctx.author.mention}",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Failed to unban user: {e}", ephemeral=True)

# Shared Error Handler
@ban.error
@unban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You need `Ban Members` permission to use this.", ephemeral=True)
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("🚫 I need `Ban Members` permission.", ephemeral=True)


# Bot Run
bot.run(TOKEN)
