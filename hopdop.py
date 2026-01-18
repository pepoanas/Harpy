import discord
from discord.ext import commands, tasks
from discord.ui import Select, View, Modal, Button
import aiohttp
import sys
import asyncio
import json
import os
import aiofiles
from discord.ui import Button, View, Modal, TextInput
import random
from datetime import datetime, timedelta
import datetime
import time
from datetime import datetime, timezone
from fuzzywuzzy import process
import subprocess
from discord import app_commands
import re
import psutil  # لجلب معلومات استهلاك الموارد
import platform
import datetime 
from discord.ui import Modal, TextInput
from discord import File
import pytz
from datetime import datetime
import io
import difflib

sys.stdout.reconfigure(encoding='utf-8')  # لضبط الترميز وحل مشكلة Unicode



# تفعيل كل الـ Intents المطلوبة
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="/", intents=intents)



@bot.event
async def on_ready():
    print(f'✅ تم تسجيل الدخول باسم {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'✅ تم مزامنة {len(synced)} أمر')
    except Exception as e:
        print(f'❌ حدث خطأ: {e}')



tree = bot.tree  








@bot.tree.command(name="انفو", description="عرض معلومات متقدمة عن المستخدم")
async def user_info(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer()  # تجنب انتهاء المهلة
    
    if member is None:
        member = interaction.user

    # 🟢 الاسم والصورة الرمزية
    name = member.name
    avatar = member.display_avatar.url

    # 🟢 البانر (إن وجد)
    user_data = await bot.fetch_user(member.id)
    banner = user_data.banner.url if user_data.banner else None

    # 🟢 اللقب (Nick)
    nick = member.nick if member.nick else "لا يوجد"

    # 🟢 الحالة (Online, DoNotDisturb, Idle, Offline)
    status = str(member.status).title()

    if status == "Online":
        status_display = "🟢 أونلاين"
    elif status == "DoNotDisturb":
        status_display = "⛔ مشغول"
    elif status == "Idle":
        status_display = "🟡 غائب"
    elif status == "Offline":
        status_display = "⚫ غير متصل"
    else:
        status_display = "❓ حالة غير معروفة"

    # 🟢 النشاط
    activity = member.activity.name if member.activity else "لا يوجد نشاط"

    # 🟢 حساب العمر ومدة الانضمام
    now = datetime.now(member.created_at.tzinfo)  # الحصول على الوقت الحالي بنفس المنطقة الزمنية
    account_age = (now - member.created_at).days
    joined_age = (now - member.joined_at).days if member.joined_at else "غير معروف"

    # 🟢 البحث عن آخر رسالة للمستخدم
    last_message_time = "غير متوفر"
    for channel in interaction.guild.text_channels:
        if channel.permissions_for(interaction.guild.me).read_message_history:  # التحقق من الصلاحيات
            try:
                async for message in channel.history(limit=100):
                    if message.author == member:
                        last_message_time = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                        break
            except:
                continue  # تجاهل الأخطاء الناتجة عن القنوات الخاصة

    # 🟢 الرتب الخاصة بالمستخدم
    roles = [role.mention for role in member.roles if role.name != "@everyone"]

    # 🟢 عدد الرسائل التي كتبها في السيرفر (باستخدام history)
    total_messages = 0
    for channel in interaction.guild.text_channels:
        if channel.permissions_for(interaction.guild.me).read_message_history:
            try:
                async for message in channel.history(limit=1000):
                    if message.author == member:
                        total_messages += 1
            except:
                continue

    # 🔹 إنشاء Embed متطور جدًا
    embed = discord.Embed(title=f"👤 معلومات {name}  𝓟𝓼 • ク", color=discord.Color.blue())
    embed.set_thumbnail(url=avatar)
    
    # 🟢 إضافة الحقول في التنسيق المطلوب
    embed.add_field(name="🔹 الاسم:", value=name, inline=False)
    embed.add_field(name="🎭 اللقب:", value=nick, inline=False)
    embed.add_field(name="📅 عمر الحساب:", value=f"{account_age} يومًا" if account_age > 0 else "غير معروف", inline=False)
    embed.add_field(name="🏠 مدة الانضمام:", value=f"{joined_age} يومًا" if isinstance(joined_age, int) else "غير معروف", inline=False)
    embed.add_field(name="💬 عدد الرسائل:", value=f"{total_messages} رسالة", inline=False)
    embed.add_field(name="📌 آخر تفاعل:", value=last_message_time if last_message_time != "غير متوفر" else "غير متوفر", inline=False)
    embed.add_field(name="🟢 الحالة:", value=status_display, inline=False)
    embed.add_field(name="🎮 النشاط:", value=activity, inline=False)

    # 🔹 إذا كان لديه بانر، أضفه
    if banner:
        embed.set_image(url=banner)

    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    
    await interaction.followup.send(embed=embed)  # إرسال الـ Embed بعد defer()





start_time = time.time()  # وقت بدء تشغيل البوت

@bot.tree.command(name="بوت", description="عرض معلومات عن البوت")
async def bot_info(interaction: discord.Interaction):
    await interaction.response.defer()  # تجنب انتهاء المهلة

    # 🟢 معلومات عامة عن البوت
    bot_name = bot.user.name
    bot_avatar = bot.user.display_avatar.url
    bot_owner = "5.h.5"  # ضع اسمك هنا أو اجلبه تلقائيًا
    bot_creation_date = bot.user.created_at.strftime("%Y-%m-%d %H:%M:%S")
    bot_commands = len(bot.tree.get_commands())  # عدد الأوامر المسجلة

    # 🟢 عدد السيرفرات والأعضاء
    total_guilds = len(bot.guilds)
    total_users = sum(guild.member_count for guild in bot.guilds if guild.member_count)

    # 🟢 مدة تشغيل البوت
    uptime_seconds = int(time.time() - start_time)
    uptime = str(datetime.utcfromtimestamp(uptime_seconds).strftime("%H:%M:%S"))

    # 🟢 سرعة استجابة البوت (Ping)
    latency = round(bot.latency * 1000, 2)

    # 🟢 استهلاك الموارد (RAM & CPU)
    process = psutil.Process()
    ram_usage = round(process.memory_info().rss / 1024 ** 2, 2)  # تحويل لـ MB
    cpu_usage = psutil.cpu_percent()

    # 🟢 نظام التشغيل والمكتبة
    python_version = platform.python_version()
    discord_version = discord.__version__
    os_name = platform.system()

    # 🔹 إنشاء Embed احترافي
    embed = discord.Embed(title="🤖 معلومات البوت", color=discord.Color.blue())
    embed.set_thumbnail(url=bot_avatar)
    embed.add_field(name="📛 الاسم", value=bot_name, inline=True)
    embed.add_field(name="👤 المالك", value=bot_owner, inline=True)
    embed.add_field(name="📅 تم الإنشاء", value=bot_creation_date, inline=True)
    embed.add_field(name="📜 عدد الأوامر", value=str(bot_commands), inline=True)
    embed.add_field(name="🌍 عدد السيرفرات", value=str(total_guilds), inline=True)
    embed.add_field(name="👥 عدد الأعضاء", value=str(total_users), inline=True)
    embed.add_field(name="⏳ وقت التشغيل", value=uptime, inline=True)
    embed.add_field(name="⚡ سرعة الاستجابة", value=f"{latency} مللي ثانية", inline=True)
    embed.add_field(name="💾 استهلاك RAM", value=f"{ram_usage} MB", inline=True)
    embed.add_field(name="🔥 استهلاك CPU", value=f"{cpu_usage}%", inline=True)
    embed.add_field(name="🖥️ نظام التشغيل", value=os_name, inline=True)
    embed.add_field(name="🐍 إصدار Python", value=python_version, inline=True)
    embed.add_field(name="📚 مكتبة Discord.py", value=discord_version, inline=True)

    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

    await interaction.followup.send(embed=embed)  # إرسال الـ Embed بعد defer()








@tree.command(name="afk", description="وضعك في حالة الخمول مع ذكر السبب")
async def afk(interaction: discord.Interaction, reason: str = "لم يتم تحديد سبب"):
    embed = discord.Embed(title="🚀 وضع الخمول", description=f"✅ {interaction.user.mention} الآن في وضع AFK: **{reason}**", color=discord.Color.orange())
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="banner", description="عرض البنر الخاص بك أو لشخص آخر")
async def banner(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    user = await bot.fetch_user(member.id)
    
    if user.banner:
        embed = discord.Embed(title=f"🎨 بانر {member.name}", color=discord.Color.blue())
        embed.set_image(url=user.banner.url)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ {member.mention} لا يملك بانر!", ephemeral=True)

@tree.command(name="link", description="إنشاء رابط دعوة للسيرفر وإرساله لك في الخاص")
async def link(interaction: discord.Interaction):
    try:
        invite = await interaction.channel.create_invite(max_age=86400, max_uses=5)
        await interaction.user.send(f"🔗 رابط الدعوة للسيرفر: {invite.url}")
        await interaction.response.send_message("✅ تم إرسال رابط الدعوة إلى رسائلك الخاصة!", ephemeral=True)
    
    except discord.Forbidden:
        await interaction.response.send_message("❌ لا يمكنني إرسال الرسائل الخاصة! تأكد أنك لم تحظر الرسائل من السيرفر.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ حدث خطأ: {e}", ephemeral=True)


@tree.command(name="server", description="عرض معلومات الخادم")
async def server(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"🔍 معلومات {guild.name}", color=discord.Color.blue())
    embed.add_field(name="👑 المالك", value=guild.owner, inline=True)
    embed.add_field(name="👥 الأعضاء", value=guild.member_count, inline=True)
    embed.add_field(name="📅 تم الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    await interaction.response.send_message(embed=embed)


@tree.command(name="channel", description="عرض معلومات عن روم معين")
async def channel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    channel = channel or interaction.channel
    embed = discord.Embed(title=f"📢 معلومات {channel.name}", color=discord.Color.purple())
    embed.add_field(name="📅 تم الإنشاء", value=channel.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="📝 الموضوع", value=channel.topic or "لا يوجد", inline=True)
    embed.set_footer(text=f"ID: {channel.id}")
    await interaction.response.send_message(embed=embed)

@tree.command(name="avatar", description="عرض صورة الأفاتار الخاصة بك أو لشخص آخر")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(title=f"🖼 صورة {member.name}", color=discord.Color.orange())
    embed.set_image(url=member.avatar.url)
    await interaction.response.send_message(embed=embed)







if not os.path.exists("levels.json"):
    with open("levels.json", "w") as f:
        json.dump({}, f)

def load_levels():
    with open("levels.json", "r") as f:
        return json.load(f)

def save_levels(data):
    with open("levels.json", "w") as f:
        json.dump(data, f, indent=4)

levels = load_levels()

# 🔹 حساب XP المطلوب لكل مستوى
def xp_required(level):
    return 5 * (level ** 2) + 50 * level + 100

# 📌 تحديث XP عند إرسال رسالة
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    user_id = str(message.author.id)
    
    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}
    
    # 🔹 إضافة XP عشوائي بين 5 و 15 لكل رسالة
    xp_gain = random.randint(5, 15)
    levels[user_id]["xp"] += xp_gain

    # 🔹 التحقق من الترقية إلى مستوى جديد
    current_level = levels[user_id]["level"]
    next_level_xp = xp_required(current_level)

    if levels[user_id]["xp"] >= next_level_xp:
        levels[user_id]["level"] += 1
        levels[user_id]["xp"] = 0  # إعادة تعيين XP عند الترقية
        
        embed = discord.Embed(
            title="🎉 تهانينا!",
            description=f"{message.author.mention} ارتقى إلى **المستوى {levels[user_id]['level']}** 🚀",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=message.author.avatar.url)
        embed.set_footer(text="واصل التفاعل للوصول إلى مستويات أعلى!")
        await message.channel.send(embed=embed)
    
    save_levels(levels)
    await bot.process_commands(message)

# 📌 أمر عرض المستوى الحالي (الملف الشخصي)
@tree.command(name="rank", description="عرض مستواك الحالي في السيرفر")
async def rank(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id not in levels:
        levels[user_id] = {"xp": 0, "level": 1}
    
    user_level = levels[user_id]["level"]
    user_xp = levels[user_id]["xp"]
    next_level_xp = xp_required(user_level)
    
    embed = discord.Embed(
        title=f"📊 مستواك الحالي - {interaction.user.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="🔹 المستوى:", value=f"**{user_level}**", inline=True)
    embed.add_field(name="🔸 نقاط الخبرة (XP):", value=f"**{user_xp}/{next_level_xp}**", inline=True)
    embed.set_thumbnail(url=interaction.user.avatar.url)
    embed.set_footer(text="🎯 تفاعل أكثر لزيادة مستواك!")

    await interaction.response.send_message(embed=embed)

# 📌 أمر قائمة الترتيب
@tree.command(name="leaderboard", description="عرض أفضل الأعضاء في السيرفر حسب المستويات")
async def leaderboard(interaction: discord.Interaction):
    sorted_levels = sorted(levels.items(), key=lambda x: x[1]["xp"], reverse=True)
    top_users = sorted_levels[:10]

    embed = discord.Embed(
        title="🏆 قائمة أفضل الأعضاء",
        color=discord.Color.purple()
    )

    for index, (user_id, data) in enumerate(top_users, start=1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(
            name=f"#{index} {user.name}",
            value=f"🔹 المستوى: **{data['level']}** | XP: **{data['xp']}**",
            inline=False
        )

    embed.set_footer(text="🎖 هل يمكنك الوصول إلى المركز الأول؟")
    await interaction.response.send_message(embed=embed)


#اوامر عامه

































@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ تم تسجيل الدخول باسم {bot.user} وتمت مزامنة الأوامر")


@bot.event
async def on_guild_join(guild):
    owner = guild.owner

    if owner:
        embed = discord.Embed(
            title="🤖 شكراً لإضافة البوت!",
            description=(
                f"👋 مرحبًا {owner.mention}، شكرًا لإضافة البوت إلى **{guild.name}**! 🎉\n\n"
                "🔹 سيتم إبلاغك بأي تحديثات جديدة تخص البوت.\n"
                "🔹   لا تنسي ان ترف رول البوت اعلي شي حته يتمكن من اجاء كل الاوامر  .\n"
                "🔹 البوت في تطور مستمر وسيدعم قريبًا العملات، الألعاب، والمتاجر! 🛒🎮💰\n\n"
                "إذا كنت بحاجة إلى مساعدة، لا تتردد في التواصل معي! 😊"
            ),
            color=discord.Color.green()
        )
        embed.set_footer(text="🔔 تأكد من متابعة تحديثات البوت باستمرار!")
        
        try:
            await owner.send(embed=embed)
        except discord.Forbidden:
            print(f"❌ لا يمكن إرسال رسالة إلى {owner} في {guild.name}")


































































#اوامر اداريه سسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسس

@tree.command(name="role", description="إضافة أو إزالة رتبة من عضو")
@app_commands.checks.has_permissions(manage_roles=True)
async def role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if role in member.roles:
        await member.remove_roles(role)
        await interaction.response.send_message(f"✅ تم إزالة الرتبة {role.name} من {member.mention}")
    else:
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ تم إعطاء الرتبة {role.name} إلى {member.mention}")

# أمر /show لإظهار قناة
@tree.command(name="show", description="إظهار قناة محددة")
@app_commands.checks.has_permissions(manage_channels=True)
async def show(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.set_permissions(interaction.guild.default_role, read_messages=True)
    await interaction.response.send_message(f"✅ تم إظهار القناة {channel.mention}")

# أمر /hide لإخفاء قناة
@tree.command(name="hide", description="إخفاء قناة محددة")
@app_commands.checks.has_permissions(manage_channels=True)
async def hide(interaction: discord.Interaction, channel: discord.TextChannel):
    await channel.set_permissions(interaction.guild.default_role, read_messages=False)
    await interaction.response.send_message(f"✅ تم إخفاء القناة {channel.mention}")

# أمر /hide-all لإخفاء جميع القنوات
@tree.command(name="hide-all", description="إخفاء جميع القنوات")
@app_commands.checks.has_permissions(manage_channels=True)
async def hide_all(interaction: discord.Interaction):
    for channel in interaction.guild.text_channels:
        await channel.set_permissions(interaction.guild.default_role, read_messages=False)
    await interaction.response.send_message("✅ تم إخفاء جميع القنوات")

# أمر /show-all لإظهار جميع القنوات
@tree.command(name="show-all", description="إظهار جميع القنوات")
@app_commands.checks.has_permissions(manage_channels=True)
async def show_all(interaction: discord.Interaction):
    for channel in interaction.guild.text_channels:
        await channel.set_permissions(interaction.guild.default_role, read_messages=True)
    await interaction.response.send_message("✅ تم إظهار جميع القنوات")

# أمر /clear لمسح عدد معين من الرسائل
@tree.command(name="clear", description="مسح عدد معين من الرسائل")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"✅ تم مسح {amount} رسالة!", ephemeral=True)

# أمر /inrole لمعرفة عدد الأعضاء الذين لديهم رتبة معينة
@tree.command(name="inrole", description="عرض عدد الأعضاء في رتبة معينة")
async def inrole(interaction: discord.Interaction, role: discord.Role):
    members_in_role = len(role.members)
    await interaction.response.send_message(f"👥 عدد الأعضاء في {role.name}: {members_in_role}")

# أمر /say ليكتب البوت رسالة بصيغة Embed
@tree.command(name="say", description="📢 كتابة رسالة بواسطة البوت")
async def say(interaction: discord.Interaction, message: str):
    """أي شخص يمكنه استخدام هذا الأمر"""
    embed = discord.Embed(description=message, color=discord.Color.blue())
    embed.set_footer(text=f"تم الإرسال بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)





tree = bot.tree  

@tree.command(name="ban", description="حظر عضو من السيرفر")
@commands.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    await member.ban(reason=reason)
    await interaction.response.send_message(f'✅ {member.mention} تم حظره بنجاح!')

# أمر إلغاء البان
@tree.command(name="unban", description="إلغاء حظر عضو")
@commands.has_permissions(ban_members=True)
async def unban(interaction: discord.Interaction, user_id: int):
    user = await bot.fetch_user(user_id)
    await interaction.guild.unban(user)
    await interaction.response.send_message(f'✅ {user.mention} تم إلغاء حظره!')

# أمر الكيك
@tree.command(name="kick", description="طرد عضو من السيرفر")
@commands.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    await member.kick(reason=reason)
    await interaction.response.send_message(f'✅ {member.mention} تم طرده بنجاح!')

# أمر الميوت
@tree.command(name="mute", description="إسكات عضو")
@commands.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد السبب"):
    await member.timeout(discord.utils.utcnow() + timedelta(days=1), reason=reason)
    await interaction.response.send_message(f'🔇 {member.mention} تم إسكاتُه!')

# أمر إزالة الميوت
@tree.command(name="unmute", description="إزالة الميوت عن عضو")
@commands.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f'✅ {member.mention} تم إزالة الميوت عنه!')

# أمر التايم أوت
@bot.tree.command(name="timeout", description="إعطاء عضو تايم أوت")
@commands.has_permissions(moderate_members=True)
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: str = "لم يتم تحديد السبب"):
    # استخدم datetime.timedelta بشكل صحيح
    await member.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=minutes), reason=reason)
    await interaction.response.send_message(f'⏳ {member.mention} تم إعطاؤه تايم أوت لمدة {minutes} دقيقة!')

# أمر إزالة التايم أوت
@tree.command(name="untimeout", description="إزالة التايم أوت عن عضو")
@commands.has_permissions(moderate_members=True)
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    await member.timeout(None)
    await interaction.response.send_message(f'✅ {member.mention} تم إزالة التايم أوت عنه!')

# أمر قفل الشات
@tree.command(name="lock", description="🔒 إغلاق الشات")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    """يجب أن يكون لدى المستخدم صلاحية 'إدارة القنوات' لاستخدام الأمر"""
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 تم إغلاق الشات!", ephemeral=True)

# أمر فتح الشات
@tree.command(name="unlock", description="فتح الشات")
@commands.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    await interaction.response.send_message("🔓 تم فتح الشات!")

#قسم البان / و فتح / وكيكسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسس






warnings = {}

# أمر التحذير
@bot.tree.command(name="تحذير", description="تحذير عضو معين بسبب معين")
@app_commands.checks.has_permissions(moderate_members=True)  # صلاحية الإشراف
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if member.id == interaction.user.id:
        return await interaction.response.send_message("❌ لا يمكنك تحذير نفسك!", ephemeral=True)

    if member.id == bot.user.id:
        return await interaction.response.send_message("❌ لا يمكنك تحذير البوت!", ephemeral=True)

    if member not in warnings:
        warnings[member] = []
    
    warnings[member].append(reason)

    await interaction.response.send_message(f"✅ تم تحذير {member.mention} بسبب: {reason}")

# أمر عرض التحذيرات
@bot.tree.command(name="التحذيرات", description="عرض التحذيرات الخاصة بعضو معين")
async def show_warnings(interaction: discord.Interaction, member: discord.Member):
    if member not in warnings or len(warnings[member]) == 0:
        return await interaction.response.send_message(f"✅ {member.mention} ليس لديه أي تحذيرات!", ephemeral=True)

    warn_list = "\n".join([f"- {r}" for r in warnings[member]])
    await interaction.response.send_message(f"📋 تحذيرات {member.mention}:\n{warn_list}")

# أمر مسح التحذيرات
@bot.tree.command(name="مسح_التحذيرات", description="مسح جميع تحذيرات عضو معين")
@app_commands.checks.has_permissions(moderate_members=True)
async def clear_warnings(interaction: discord.Interaction, member: discord.Member):
    if member not in warnings or len(warnings[member]) == 0:
        return await interaction.response.send_message(f"✅ {member.mention} ليس لديه أي تحذيرات لمسحها!", ephemeral=True)

    warnings[member] = []
    await interaction.response.send_message(f"✅ تم مسح جميع تحذيرات {member.mention}!")







emoji_limits = {}


@bot.tree.command(name="اضافة_ايموجي", description="إضافة إيموجي من سيرفر آخر أو صورة (الحد 3)")
@app_commands.checks.has_permissions(manage_emojis=True)  # التحقق من الصلاحيات
async def add_emoji(
    interaction: discord.Interaction, 
    name: str, 
    emoji: str = None, 
    attachment: discord.Attachment = None
):
    guild = interaction.guild

    # التأكد من وجود السيرفر في القاموس
    if guild.id not in emoji_limits:
        emoji_limits[guild.id] = 0

    if emoji_limits[guild.id] >= 3:
        return await interaction.response.send_message("❌ لقد وصلت إلى الحد الأقصى لإضافة الإيموجيات (3)!", ephemeral=True)

    img_data = None  # سيتم تخزين بيانات الصورة هنا

    # **إستخراج الإيموجي من سيرفر آخر**
    emoji_url = None
    if emoji:
        match = re.search(r"<a?:\w+:(\d+)>", emoji)  # استخراج ID الإيموجي
        if match:
            emoji_id = match.group(1)
            emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        else:
            return await interaction.response.send_message("❌ الرجاء إرسال إيموجي خارجي صحيح!", ephemeral=True)

    # **إذا أرسل مرفق، استخدمه كصورة للإيموجي**
    elif attachment:
        emoji_url = attachment.url

    else:
        return await interaction.response.send_message("❌ الرجاء إرسال إيموجي خارجي أو صورة مرفقة!", ephemeral=True)

    try:
        # جلب الصورة من الرابط
        async with aiohttp.ClientSession() as session:
            async with session.get(emoji_url) as response:
                if response.status != 200:
                    return await interaction.response.send_message("❌ فشل تحميل الصورة!", ephemeral=True)
                img_data = await response.read()

        # إضافة الإيموجي للسيرفر
        new_emoji = await guild.create_custom_emoji(name=name, image=img_data)
        emoji_limits[guild.id] += 1  # زيادة العداد

        await interaction.response.send_message(f"✅ تم إضافة الإيموجي بنجاح: {new_emoji}")

    except Exception as e:
        await interaction.response.send_message(f"❌ حدث خطأ أثناء إضافة الإيموجي: {e}", ephemeral=True)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"✅ تمت مزامنة {len(synced)} من الأوامر بنجاح!")
    except Exception as e:
        print(f"❌ خطأ أثناء المزامنة: {e}")



























@bot.tree.command(name="control", description="🔧 لوحة تحكم لإنشاء القنوات والرتب")
@app_commands.checks.has_permissions(administrator=True)
async def control(interaction: discord.Interaction, action: str, name: str, type: str = None):
    guild = interaction.guild

    # إنشاء قناة نصية أو صوتية
    if action.lower() == "create-channel":
        if type and type.lower() == "text":
            await guild.create_text_channel(name)
            await interaction.response.send_message(f"✅ تم إنشاء القناة النصية: **{name}**")
        elif type and type.lower() == "voice":
            await guild.create_voice_channel(name)
            await interaction.response.send_message(f"✅ تم إنشاء القناة الصوتية: **{name}**")
        else:
            await interaction.response.send_message("❌ نوع القناة غير صحيح! استخدم `text` أو `voice`.")

    # إنشاء رتبة جديدة
    elif action.lower() == "create-role":
        role = await guild.create_role(name=name, color=discord.Color.blue())
        await interaction.response.send_message(f"✅ تم إنشاء الرتبة: **{role.name}**")

    else:
        await interaction.response.send_message("❌ الأمر غير صحيح! استخدم `create-channel` أو `create-role`.")

 



temp_channels = {}  # تخزين القنوات المؤقتة
main_voice_channel_id = None  # تخزين معرف القناة الرئيسية

class VoiceControlView(discord.ui.View):
    def __init__(self, voice_channel, owner_id):
        super().__init__(timeout=None)
        self.voice_channel = voice_channel
        self.owner_id = owner_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """تأكد أن المستخدم هو صاحب الغرفة أو لديه صلاحية الأدمن"""
        if interaction.user.id == self.owner_id or interaction.user.guild_permissions.administrator:
            return True
        await interaction.response.send_message("❌ لا يمكنك التحكم في هذه الغرفة!", ephemeral=True)
        return False

    @discord.ui.button(label="🔒 قفل الغرفة", style=discord.ButtonStyle.danger)
    async def lock_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.voice_channel.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.response.send_message("🔒 تم قفل الغرفة!")

    @discord.ui.button(label="🔓 فتح الغرفة", style=discord.ButtonStyle.success)
    async def unlock_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.voice_channel.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.response.send_message("🔓 تم فتح الغرفة!")

    @discord.ui.button(label="✏️ تغيير اسم الغرفة", style=discord.ButtonStyle.primary)
    async def rename_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = discord.ui.Modal(title="تغيير اسم الغرفة")
        input_field = discord.ui.TextInput(label="الاسم الجديد", placeholder="أدخل الاسم الجديد")
        modal.add_item(input_field)

        async def modal_callback(modal_interaction: discord.Interaction):
            new_name = input_field.value
            await self.voice_channel.edit(name=new_name)
            await modal_interaction.response.send_message(f"✅ تم تغيير الاسم إلى `{new_name}`!")

        modal.on_submit = modal_callback
        await interaction.response.send_modal(modal)

@bot.tree.command(name="voice-setup", description="إنشاء نظام الغرف الصوتية التلقائية")
@app_commands.checks.has_permissions(administrator=True)
async def voice_setup(interaction: discord.Interaction, main_channel: discord.VoiceChannel):
    global main_voice_channel_id
    main_voice_channel_id = main_channel.id
    await interaction.response.send_message(
        f"✅ تم تعيين `{main_channel.name}` كقناة رئيسية لإنشاء الغرف الصوتية الخاصة!", ephemeral=True
    )

@bot.event
async def on_voice_state_update(member, before, after):
    global main_voice_channel_id

    guild = member.guild
    category_name = "🌀 قنوات خاصة"
    category = discord.utils.get(guild.categories, name=category_name)

    # إذا دخل العضو إلى القناة الرئيسية، يتم إنشاء غرفة خاصة وغرفة تحكم
    if after.channel and after.channel.id == main_voice_channel_id:
        voice_channel = await guild.create_voice_channel(
            name=f"🔊 {member.display_name}'s Room",
            category=category
        )
        control_channel = await guild.create_text_channel(
            name=f"🛠️ تحكم {member.display_name}",
            category=category
        )

        # ضبط صلاحيات غرفة التحكم بحيث يراها فقط صاحب الغرفة والإداريين
        await control_channel.set_permissions(member, read_messages=True, send_messages=True)
        await control_channel.set_permissions(guild.default_role, read_messages=False)

        # إرسال رسالة التحكم مع الأزرار
        view = VoiceControlView(voice_channel, member.id)
        await control_channel.send(
            f"🔧 **غرفة التحكم في الغرفة الصوتية الخاصة بـ {member.mention}**",
            view=view
        )

        # نقل العضو للغرفة الجديدة
        await member.move_to(voice_channel)

        # تخزين الغرف
        temp_channels[voice_channel.id] = (member.id, control_channel.id)

    # حذف الغرفة الصوتية وغرفة التحكم عند خروج صاحب الغرفة
    if before.channel and before.channel.id in temp_channels:
        owner_id, control_channel_id = temp_channels[before.channel.id]
        if member.id == owner_id and len(before.channel.members) == 0:
            control_channel = discord.utils.get(guild.text_channels, id=control_channel_id)
            await before.channel.delete()
            if control_channel:
                await control_channel.delete()
            del temp_channels[before.channel.id]










#جيف اواي سسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسس




















class Giveaway:
    def __init__(self, bot, channel, prize, duration, winners):
        self.bot = bot
        self.channel = channel
        self.prize = prize
        self.duration = duration
        self.winners = winners
        self.participants = set()
        self.message_id = None  # ✅ تعريف المتغير

    async def start(self):
        embed = discord.Embed(
            title="🎉 **جيف أواي جديد!** 🎉",
            description=f"🔹 **الجائزة:** {self.prize}\n🔹 **المدة:** {self.duration} دقيقة\n🔹 **عدد الفائزين:** {self.winners}\n\n🎈 **اضغط على 🎉 للمشاركة!**",
            color=discord.Color.gold(),
        )
        embed.set_footer(text="🎯 سيتم اختيار الفائز تلقائيًا عند انتهاء المدة!")

        msg = await self.channel.send(embed=embed)
        self.message_id = msg.id  # ✅ تخزين ID الرسالة
        await msg.add_reaction("🎉")

        await asyncio.sleep(self.duration * 60)  
        await self.end()

    async def end(self):
        if not self.participants:
            await self.channel.send("❌ **تم إلغاء الجيف أواي بسبب عدم وجود مشاركين!**")
            return

        winners = random.sample(list(self.participants), min(len(self.participants), self.winners))

        embed = discord.Embed(
            title="🏆 **انتهى الجيف أواي!** 🏆",
            description=f"🎁 **الجائزة:** {self.prize}\n🎊 **الفائزون:** {', '.join([f'<@{winner}>' for winner in winners])}",
            color=discord.Color.green(),
        )
        await self.channel.send(embed=embed)

giveaways = {}

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    for giveaway in giveaways.values():
        if hasattr(giveaway, "message_id") and reaction.message.id == giveaway.message_id:
            giveaway.participants.add(user.id)
            return

@bot.tree.command(name="start_giveaway", description="بدء جيف أواي جديد")
@app_commands.checks.has_permissions(administrator=True)
async def start_giveaway(interaction: discord.Interaction, channel: discord.TextChannel, prize: str, duration: int, winners: int):
    giveaway = Giveaway(bot, channel, prize, duration, winners)
    giveaways[channel.id] = giveaway

    await interaction.response.send_message(f"🎉 **تم بدء الجيف أواي في {channel.mention}!**", ephemeral=True)
    await giveaway.start()


















































































class HelpDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="الرئيسية", description="عرض الصفحة الرئيسية", emoji="🏠"),
            discord.SelectOption(label="الأوامر العامة", description="عرض قائمة الأوامر العامة", emoji="🌍"),
            discord.SelectOption(label="الأوامر الإدارية", description="عرض قائمة الأوامر الإدارية", emoji="🛠️"),
            discord.SelectOption(label="الأوامر البريميوم", description="عرض قائمة الأوامر البريميوم", emoji="💎"),
            discord.SelectOption(label="الألعاب", description="عرض أوامر الألعاب", emoji="🎮"),  # إضافة خيار الألعاب
        ]
        super().__init__(placeholder="🔍 اختر فئة الأوامر", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "الرئيسية":
            embed = discord.Embed(
                title="🌟 | الصفحة الرئيسية",
                description=(
                    "مرحبًا بك في **Hop Arab Bot**!\n\n"
                    "هنا يمكنك العثور على جميع الأوامر والموارد التي تحتاجها.\n\n"
                    "**👑 مميزاتنا:**\n"
                    "- دعم 24/7\n"
                    "- تحديثات مستمرة\n"
                    "- أوامر بريميوم حصرية\n\n"
                    "**💡 هل تحتاج المساعدة؟**\n"
                    "تواصل معنا عبر الروابط أدناه!"
                ),
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url="https://i.postimg.cc/W3FJckrf/image.png")  # صورة البوت
            embed.set_image(url="https://i.postimg.cc/BQfnpSpP/1.png")  # GIF متحرك كخلفية
            embed.add_field(
                name="🔗 الروابط المهمة",
                value=(
                    "[🌐 سيرفر الدعم](https://discord.gg/hum6H72TeT)\n"
                    "[🤖 إضافة البوت](https://discord.com/oauth2/authorize?client_id=1343580040775995402&permissions=8&integration_type=0&scope=bot)\n"
                    #"[❤️ دعمنا](https://www.patreon.com/example)"  # رابط دعم
                ),
                inline=False
            )
            embed.set_footer(text="Verson Bot | Powered by YourBotName")
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == "الأوامر العامة":
            embed = discord.Embed(title="🌍 | الأوامر العامة", color=discord.Color.green())
            embed.add_field(name="🔹 `info`", value="معلومات عن البوت", inline=False)
            embed.add_field(name="🔹 `afk`", value="تحديد حالتك كـ AFK", inline=False)
            embed.add_field(name="🔹 `banner`", value="عرض بانر السيرفر", inline=False)
            embed.add_field(name="🔹 `link`", value="رابط دعوة السيرفر", inline=False)
            embed.add_field(name="🔹 `server`", value="معلومات عن السيرفر", inline=False)
            embed.add_field(name="🔹 `channel`", value="معلومات القناة", inline=False)
            embed.add_field(name="🔹 `avatar`", value="عرض صورة الحساب", inline=False)
            embed.add_field(name="🔹 `rank`", value="عرض الرتبة الخاصة بك", inline=False)
            embed.add_field(name="🔹 `leaderboard`", value="عرض قائمة المتصدرين", inline=False)
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == "الأوامر الإدارية":
            embed = discord.Embed(title="🛠️ | الأوامر الإدارية", color=discord.Color.red())
            embed.add_field(name="🔸 `role`", value="إدارة الرتب", inline=False)
            embed.add_field(name="🔸 `show` / `hide`", value="إظهار / إخفاء القناة", inline=False)
            embed.add_field(name="🔸 `hide-all` / `show-all`", value="إخفاء / إظهار جميع القنوات", inline=False)
            embed.add_field(name="🔸 `clear`", value="مسح الرسائل", inline=False)
            embed.add_field(name="🔸 `inrole`", value="عرض من في رتبة معينة", inline=False)
            embed.add_field(name="🔸 `say`", value="إرسال رسالة عبر البوت", inline=False)
            embed.add_field(name="🔸 `ban` / `unban` / `kick`", value="حظر وإلغاء حظر وطرد الأعضاء", inline=False)
            embed.add_field(name="🔸 `mute` / `unmute`", value="كتم وإلغاء كتم الأعضاء", inline=False)
            embed.add_field(name="🔸 `timeout` / `untimeout`", value="إعطاء وإلغاء التايم آوت", inline=False)
            embed.add_field(name="🔸 `lock` / `unlock`", value="إغلاق وفتح القناة", inline=False)
            embed.add_field(name="🔸 `تحذير` / `التحذيرات` / `مسح_التحذيرات`", value="إدارة التحذيرات", inline=False)
            embed.add_field(name="🔸 `إضافة_ايموجي`", value="إضافة إيموجي جديد للسيرفر", inline=False)
            embed.add_field(name="🔸 `control`", value="لوحة التحكم المتطورة", inline=False)
            embed.add_field(name="🔸 `voice-setup`", value="إعداد نظام الصوت التلقائي", inline=False)
            embed.add_field(name="🔸 `start_giveaway`", value="بدء جيف أواي", inline=False)
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == "الأوامر البريميوم":
            embed = discord.Embed(title="💎 | الأوامر البريميوم", color=discord.Color.gold())
            embed.add_field(name="🔹 `premium`", value="تفعيل أو إدارة ميزات البريميوم", inline=False)
            embed.add_field(name="🔹 `subscribe`", value="اشتراك في خطة البريميوم", inline=False)
            embed.add_field(name="🔹 `change_avatar`", value="تغيير صورة البوت (بريميوم)", inline=False)
            embed.add_field(name="🔹 `setup_channel`", value="إعداد قناة خاصة (بريميوم)", inline=False)
            embed.add_field(name="🔹 `change_bot_nickname`", value="تغيير اسم البوت في السيرفر (بريميوم)", inline=False)
            embed.add_field(name="🔹 `broadcast_dm`", value="إرسال رسائل بث خاصة للأعضاء (بريميوم)", inline=False)
            embed.add_field(name="🔹 `set_welcome_channel`", value="إعداد قناة الترحيب (بريميوم)", inline=False)
            embed.add_field(name="🔹 `enable_prayer_times`", value="تفعيل إشعارات أوقات الصلاة (بريميوم)", inline=False)
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == "الألعاب":  # قسم الألعاب الجديد
            embed = discord.Embed(title="🎮 | الألعاب", color=discord.Color.blue())
            embed.add_field(name="🔹 `/guess`", value="🎭 لعبة تخمين الممثلين الفخمة!", inline=False)
            embed.add_field(name="🔹 `/wallet`", value="اعرض عدد البيتكوين التي تمتلكها ورتبتك!", inline=False)
            embed.add_field(name="🔹 `/add_bitcoins`", value="أضف بيتكوين لمستخدم (Admins Only)", inline=False)
            await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpDropdown())

class HelpCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

@bot.tree.command(name="help_me", description="عرض قائمة المساعدة")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌟 | الصفحة الرئيسية",
        description=(
            "مرحبًا بك في **Hop Arab Bot**!\n\n"
            "هنا يمكنك العثور على جميع الأوامر والموارد التي تحتاجها.\n\n"
            "**👑 مميزاتنا:**\n"
            "- دعم 24/7\n"
            "- تحديثات مستمرة\n"
            "- أوامر بريميوم حصرية\n\n"
            "**💡 هل تحتاج المساعدة؟**\n"
            "تواصل معنا عبر الروابط أدناه!"
        ),
        color=discord.Color.purple()
    )
    embed.set_thumbnail(url="https://i.postimg.cc/W3FJckrf/image.png")  # صورة البوت
    embed.set_image(url="https://i.postimg.cc/BQfnpSpP/1.png")  # GIF متحرك كخلفية
    embed.add_field(
        name="🔗 الروابط المهمة",
        value=(
            "[🌐 سيرفر الدعم](https://discord.gg/hum6H72TeT)\n"
            "[🤖 إضافة البوت](https://discord.com/oauth2/authorize?client_id=1343580040775995402&permissions=8&integration_type=0&scope=bot)\n"
            #"[❤️ دعمنا](https://www.patreon.com/example)"  # رابط دعم
        ),
        inline=False
    )
    embed.set_footer(text="تمني ان يعجبك خدمتنا و البوت تحت التطور و التحديث و اضاف خدمات اسهل و اضافت جديده ")

    # إرسال الرسالة للجميع (بدون استخدام ephemeral=True)
    await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=False)

async def cog_load(self):
    # تأكد من مزامنة الأوامر مع Discord عند بدء البوت
    await self.bot.tree.sync()




# إضافة الكود لمزامنة الأوامر بعد بدء البوت
@bot.event
async def on_ready():
    # مزامنة الأوامر مع Discord عند بدء البوت
    await bot.tree.sync()
    print("Commands synchronized with Discord!")

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCommand(bot))

@bot.event
async def on_ready():
    # مزامنة الأوامر مع Discord عند بدء البوت
    await bot.tree.sync()
    print("نورت يا انس")


#صاحب البوتسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسس


@bot.tree.command(name="toggle_status", description="تغيير حالة البوت بين متصل ومشغول (خاص بصاحب البوت)")
async def toggle_status(interaction: discord.Interaction):
    # التحقق من أن المستخدم هو صاحب البوت
    if interaction.user.id != bot_owner_id:
        await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب البوت.", ephemeral=True)
        return

    # الحصول على الحالة الحالية للبوت
    current_status = bot.status

    # تغيير الحالة بناءً على الحالة الحالية
    if current_status == discord.Status.online:  # إذا كان البوت متصلًا
        await bot.change_presence(status=discord.Status.dnd)  # تغيير الحالة إلى مشغول
        new_status = "مشغول"
    else:  # إذا كان البوت في أي حالة أخرى (مثل مشغول)
        await bot.change_presence(status=discord.Status.online)  # تغيير الحالة إلى متصل
        new_status = "متصل"

    # إرسال رسالة تأكيد
    await interaction.response.send_message(f"✅ تم تغيير حالة البوت إلى: **{new_status}**", ephemeral=True)





@bot.tree.command(name="change_bot_name", description="تغيير اسم البوت الحقيقي (خاص بصاحب البوت)")
async def change_bot_name(interaction: discord.Interaction, new_name: str):
    # التحقق من أن المستخدم هو صاحب البوت
    if interaction.user.id != bot_owner_id:
        await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب البوت.", ephemeral=True)
        return

    try:
        # تغيير اسم البوت عالميًا
        await bot.user.edit(username=new_name)

        # إرسال رسالة تأكيد
        await interaction.response.send_message(f"✅ تم تغيير اسم البوت إلى: **{new_name}**", ephemeral=True)
    except Exception as e:
        # في حالة حدوث خطأ أثناء تغيير الاسم
        await interaction.response.send_message(f"❌ حدث خطأ أثناء تغيير اسم البوت: {str(e)}", ephemeral=True)










@bot.tree.command(name="broadcast", description="إرسال رسالة إلى جميع السيرفرات (خاص بصاحب البوت)")
async def broadcast(interaction: discord.Interaction, message: str):
    # التحقق من أن المستخدم هو صاحب البوت
    if interaction.user.id != bot_owner_id:
        await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب البوت.", ephemeral=True)
        return

    # جمع القنوات العامة في جميع السيرفرات
    successful_servers = []
    failed_servers = []

    for guild in bot.guilds:
        try:
            # اختيار أول قناة نصية متاحة في السيرفر
            channel = next(
                (ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages),
                None
            )

            if channel:
                await channel.send(message)
                successful_servers.append(guild.name)
            else:
                failed_servers.append(guild.name)
        except Exception as e:
            failed_servers.append(guild.name)

    # إنشاء رسالة تأكيد
    embed = discord.Embed(
        title="📢 تقرير البث",
        description="تم إرسال الرسالة إلى السيرفرات التالية:",
        color=discord.Color.green()
    )

    if successful_servers:
        embed.add_field(name="✅ السيرفرات الناجحة", value="\n".join(successful_servers), inline=False)

    if failed_servers:
        embed.add_field(name="❌ السيرفرات الفاشلة", value="\n".join(failed_servers), inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)










@bot.tree.command(name="leave_server", description="مغادرة سيرفر محدد باستخدام معرف السيرفر (خاص بصاحب البوت)")
async def leave_server(interaction: discord.Interaction, server_id: str, farewell_message: str = "شكراً لكم على استضافة البوت! 👋"):
    # التحقق من أن المستخدم هو صاحب البوت
    if interaction.user.id != bot_owner_id:
        await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب البوت.", ephemeral=True)
        return

    try:
        # تحويل المدخل إلى عدد صحيح (ID)
        server_id = int(server_id)

        # البحث عن السيرفر باستخدام المعرف
        guild = bot.get_guild(server_id)
        if guild is None:
            await interaction.response.send_message(f"❌ لم يتم العثور على السيرفر بمعرف: `{server_id}`.", ephemeral=True)
            return

        # إرسال رسالة وداعية
        channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
        if channel:
            await channel.send(farewell_message)

        # مغادرة السيرفر
        await guild.leave()
        await interaction.response.send_message(f"✅ تم مغادرة السيرفر: **{guild.name}** (`{server_id}`).", ephemeral=True)

    except ValueError:
        await interaction.response.send_message("❌ المعرف الذي أدخلته غير صالح. الرجاء إدخال معرف صحيح.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ حدث خطأ أثناء محاولة مغادرة السيرفر: {str(e)}", ephemeral=True)





@bot.tree.command(name="list_servers", description="عرض قائمة السيرفرات التي يتواجد فيها البوت (خاص بصاحب البوت)")
async def list_servers(interaction: discord.Interaction):
    # التحقق من أن المستخدم هو صاحب البوت
    if interaction.user.id != bot_owner_id:
        await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب البوت.", ephemeral=True)
        return

    # جمع بيانات السيرفرات
    servers_list = [f"**{guild.name}** (`{guild.id}`)" for guild in bot.guilds]

    if not servers_list:
        await interaction.response.send_message("❌ البوت لا يتواجد في أي سيرفر حاليًا.", ephemeral=True)
        return

    # إنشاء رسالة مضمنة
    embed = discord.Embed(
        title="📖 قائمة السيرفرات",
        description="\n".join(servers_list),
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)






#صاحب البوتسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسس


#قسم برميونم    سسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسس







pending_requests = {}

# دالة لتوليد كود عشوائي مكون من 4 أرقام
def generate_code():
    return random.randint(1000, 9999)

# دالة للتحقق إذا كان الشخص هو صاحب السيرفر
def is_owner(interaction: discord.Interaction):
    return interaction.user == interaction.guild.owner

# معرف صاحب البوت الذي سيقوم بتشغيل الأوامر الخاصة
bot_owner_id = 1304398871501340702  # استبدل بهذا المعرف الخاص بك

# قاعدة لتخزين الحالات الخاصة بالسبام
spam_warnings = {}

# قاعدة بيانات للمشتركين في البرميوم
premium_servers = {}

# أمر الاشتراك لعرض المميزات
@bot.tree.command(name="premium")
async def premium(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب السيرفر.", ephemeral=True)
        return

    if interaction.guild.id in premium_servers:
        await interaction.response.send_message("❌ هذا السيرفر قد اشترك بالفعل في البرميوم.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎉 اشتراك بريميوم للبوت",
        description="احصل على مميزات حصرية مع اشتراك بريميوم للبوت!",
        color=discord.Color.gold()
    )
    
    embed.add_field(name="🛠️ المميزات:", value=( 
        "- تغيير اسم البوت\n"
        "- تغيير صورة البوت\n"
        "- حماية من السبام (مع 3 تحذيرات)\n"
        "- مميزات أخرى قادمة\n"
    ), inline=False)
    
    embed.add_field(name="💰 السعر:", value="100 جنيه أو 50 مليون كريدت", inline=False)
    embed.add_field(name="🔑 كيف تشترك؟", value="اكتب الأمر `/subscribe` لشراء الاشتراك", inline=False)

    code = generate_code()
    pending_requests[interaction.guild.id] = {
        "code": code,
        "guild": interaction.guild
    }

    await interaction.response.send_message(embed=embed)

# أمر الاشتراك لتحويل الطلب إلى صاحب البوت
@bot.tree.command(name="subscribe")
async def subscribe(interaction: discord.Interaction):
    if not is_owner(interaction):
        await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب السيرفر.", ephemeral=True)
        return
    
    if interaction.guild.id not in pending_requests:
        await interaction.response.send_message("❌ يجب عليك أولًا استخدام أمر `/premium` لطلب الاشتراك.", ephemeral=True)
        return
    
    invites = await interaction.guild.invites()
    if not invites:
        await interaction.response.send_message("❌ لا توجد دعوات للسيرفر.", ephemeral=True)
        return
    
    await bot.get_user(bot_owner_id).send(
        f"📬 شخص يريد الاشتراك في البرميوم! \n"
        f"اسم السيرفر: {interaction.guild.name}\n"
        f"اسم صاحب السيرفر: {interaction.guild.owner.name}\n"
        f"رابط السيرفر: {invites[0].url}\n"
        f"📝 لتفعيل الاشتراك، اكتب `!give {pending_requests[interaction.guild.id]['code']}`"
    )

    embed = discord.Embed(
        title="🔑 اشتراكك في البوت البرميوم",
        description="تم تأكيد طلب الاشتراك في البرميوم. انتظر حتى يقوم صاحب البوت بتفعيل الاشتراك.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

# أمر give لتفعيل الاشتراك باستخدام الكود فقط
@bot.tree.command(name="give")
async def give(interaction: discord.Interaction, code: int):
    if interaction.user.id != bot_owner_id:
        await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب البوت.", ephemeral=True)
        return

    if interaction.guild.id not in pending_requests:
        await interaction.response.send_message("❌ لا يوجد طلب اشتراك لهذا السيرفر.", ephemeral=True)
        return

    stored_code = pending_requests[interaction.guild.id]["code"]
    if code != stored_code:
        await interaction.response.send_message("❌ الكود المدخل غير صحيح. حاول مرة أخرى.", ephemeral=True)
        return

    guild = pending_requests.pop(interaction.guild.id)
    premium_servers[interaction.guild.id] = True

    embed = discord.Embed(
        title="🔑 تم تفعيل اشتراكك في البرميوم!",
        description="المميزات الآن متاحة لك.",
        color=discord.Color.green()
    )
    embed.add_field(name="✨ المزايا الحصرية متاحة الآن بين يديك! ✨", value=(
        "💎 **تغيير اسم البوت**: اختر لقبًا مميزًا يعكس شخصية البوت.\n"
        "🖼️ **تغيير صورة البوت**: زين البوت بصورة تعبر عن ذوقك الرفيع.\n"
        "🛠️ **إعداد قناة الإعدادات**: قم بإنشاء قناة مركزية لإدارة كافة إعدادات البوت.\n"
        "📢 **البث المباشر للرسائل**: أرسل رسائل مباشرة إلى جميع الأعضاء بلمسة واحدة.\n"
        "👋 **تعيين قناة الترحيب**: استقبل الأعضاء الجدد برسائل ترحيب دافئة في قناة مخصصة.\n"
        "🕋 **تفعيل مواقيت الصلاة**: أضف لمسة روحانية مع مواقيت الصلاة اليومية.\n"
        "🚀 **المزيد من المزايا**: ابقَ على تواصل لمعرفة الميزات القادمة قريبًا!\n"
    ), inline=False)

    # إضافة لون فخم للـ embed (أحمر غامق أو بنفسجي)
    embed.color = 0x8A2BE2  # لون بنفسجي ملكي

    # إضافة تذييل احترافي
    embed.set_footer(text="شكرًا لاستخدام بوت Hop Arab! ❇️", icon_url="https://i.postimg.cc/W3FJckrf/image.png")

    await guild["guild"].owner.send(embed=embed)
    await interaction.response.send_message(f"✅ تم تفعيل الاشتراك للبوت في السيرفر: {guild['guild'].name}", ephemeral=True)

# التحقق إذا كان المستخدم هو صاحب السيرفر
def is_owner(interaction: discord.Interaction):
    return interaction.user == interaction.guild.owner

class AvatarModal(Modal):
    def __init__(self):
        super().__init__(title="Change Avatar")

    avatar_url = TextInput(label="Enter Image URL")

    async def on_submit(self, interaction: discord.Interaction):
        if not is_owner(interaction):
            await interaction.response.send_message("🚫 هذا الأمر مخصص فقط لصاحب السيرفر.", ephemeral=True)
            return

        if interaction.guild.id not in premium_servers:
            await interaction.response.send_message("❌ يجب أن يكون لديك اشتراك بريميوم لاستخدام هذا الأمر.", ephemeral=True)
            return

        if self.avatar_url.value.startswith("http"):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.avatar_url.value) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            await interaction.guild.me.edit(avatar=data)
                            await interaction.response.send_message(f"✅ تم تغيير صورة البوت بنجاح بواسطة {interaction.user.name}.", ephemeral=True)
                            await interaction.channel.send(f"تم تغيير صورة البوت بواسطة {interaction.user.name}!", file=discord.File(io.BytesIO(data), filename="avatar.png"))
                        else:
                            await interaction.response.send_message("❌ حدث خطأ أثناء تحميل الصورة. تأكد من الرابط.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"❌ حدث خطأ أثناء تغيير الصورة: {str(e)}", ephemeral=True)
        else:
            await interaction.response.send_message("❌ يجب إدخال رابط صورة صالح.", ephemeral=True)


server_settings = {}

@bot.tree.command(name="setup_channel", description="اختيار قناة وإضافة إيموجيات ردود الفعل")
async def setup_channel(interaction: discord.Interaction):
    # التحقق إذا السيرفر بريميوم
    if not premium_servers.get(interaction.guild.id, False):
        await interaction.response.send_message("هذا الأمر متاح فقط للسيرفرات البريميوم!", ephemeral=True)
        return

    # التحقق من الصلاحيات
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("عذرًا، هذا الأمر متاح فقط للمشرفين!", ephemeral=True)
        return

    # جلب القنوات النصية في السيرفر
    text_channels = [channel for channel in interaction.guild.text_channels]

    # إنشاء قائمة بأسماء القنوات
    channel_names = "\n".join([f"{i+1}. {channel.name}" for i, channel in enumerate(text_channels)])

    # إرسال رسالة لاختيار القناة
    await interaction.response.send_message(
        f"اختر رقم القناة اللي تبغى تفعّل فيها النظام:\n{channel_names}",
        ephemeral=True
    )

    # تخزين القنوات مؤقتًا
    server_settings[interaction.guild.id] = {"channels": text_channels, "emojis": []}

    # استقبال الرد من المستخدم (اختيار القناة)
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        channel_choice = await bot.wait_for("message", check=check, timeout=30)
        channel_index = int(channel_choice.content) - 1

        if 0 <= channel_index < len(text_channels):
            selected_channel = text_channels[channel_index]
            server_settings[interaction.guild.id]["selected_channel"] = selected_channel

            # طلب الإيموجيات من المستخدم
            await interaction.followup.send(
                "اكتب الإيموجيات اللي تبغى تضيفها كردود فعل (مفصولة بمسافات):",
                ephemeral=True
            )

            emoji_choice = await bot.wait_for("message", check=check, timeout=30)
            emojis = emoji_choice.content.split()

            # تخزين الإيموجيات
            server_settings[interaction.guild.id]["emojis"] = emojis

            await interaction.followup.send(
                f"تم تفعيل النظام في القناة: {selected_channel.mention} مع الإيموجيات: {' '.join(emojis)}",
                ephemeral=True
            )
        else:
            await interaction.followup.send("اختيار غير صحيح! العملية ألغيت.", ephemeral=True)

    except ValueError:
        await interaction.followup.send("اختيار غير صحيح! العملية ألغيت.", ephemeral=True)
    except TimeoutError:
        await interaction.followup.send("انتهت المدة الزمنية! العملية ألغيت.", ephemeral=True)

@bot.event
async def on_message(message):
    # التحقق إذا كانت الرسالة قادمة من سيرفر
    if message.guild is None:
        return  # تجاهل الرسائل الخاصة

    guild_id = message.guild.id
    if guild_id in server_settings:
        settings = server_settings[guild_id]
        selected_channel = settings.get("selected_channel")

        if message.channel == selected_channel:
            # تجاهل الرسائل اللي من البوت نفسه
            if message.author.bot:
                return

            # إنشاء الـ Embed بناءً على الرسالة
            embed = discord.Embed(
                description=message.content,
                color=discord.Color.blue()
            )
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)

            # إرسال الرسالة الجديدة (Embed)
            await message.delete()  # حذف الرسالة الأصلية
            sent_message = await message.channel.send(embed=embed)

            # إضافة الإيموجيات اللي تم اختيارها
            for emoji in settings["emojis"]:
                await sent_message.add_reaction(emoji)

    # السماح للأوامر العادية بالعمل
    await bot.process_commands(message)




@bot.tree.command(name="change_bot_nickname", description="تغيير اسم البوت في هذا السيرفر فقط (بريميوم)")
async def change_bot_nickname(interaction: discord.Interaction, new_nickname: str):
    # التحقق إذا السيرفر بريميوم
    if not premium_servers.get(interaction.guild.id, False):
        await interaction.response.send_message("هذا الأمر متاح فقط للسيرفرات البريميوم!", ephemeral=True)
        return

    # التحقق من الصلاحيات
    if not interaction.user.guild_permissions.manage_nicknames:
        await interaction.response.send_message("عذرًا، هذا الأمر متاح فقط لمن عندهم صلاحية تغيير الأسماء!", ephemeral=True)
        return

    try:
        # تغيير الـ Nickname الخاص بالبوت في السيرفر ده
        await interaction.guild.me.edit(nick=new_nickname)

        # إرسال رسالة تأكيد
        await interaction.response.send_message(f"تم تغيير اسم البوت في هذا السيرفر إلى: `{new_nickname}` بنجاح!", ephemeral=True)

    except discord.Forbidden:
        await interaction.response.send_message("ليس لدي الصلاحيات اللازمة لتغيير الاسم في هذا السيرفر!", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.response.send_message(f"حدث خطأ أثناء تغيير الاسم: {e}", ephemeral=True)







class ConfirmationView(View):
    def __init__(self, interaction: discord.Interaction, message: str, filtered_members: list):
        super().__init__(timeout=30)  # الزر يبقى شغال لمدة 30 ثانية
        self.interaction = interaction
        self.message = message
        self.filtered_members = filtered_members
        self.confirmed = False

    @discord.ui.button(label="تأكيد", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        self.confirmed = True
        await interaction.response.send_message("جاري إرسال البرودكاست...", ephemeral=True)
        self.stop()

    @discord.ui.button(label="إلغاء", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("تم إلغاء البرودكاست.", ephemeral=True)
        self.stop()

@bot.tree.command(name="broadcast_dm", description="إرسال برودكاست خاص للأعضاء (متقدم)")
async def broadcast_dm(interaction: discord.Interaction, message: str, status: str = "all"):
    """
    الخيارات المتاحة لـ `status`:
    - all: يبعت للجميع.
    - online: يبعت للأعضاء اللي أونلاين فقط.
    - offline: يبعت للأعضاء اللي أوفلاين فقط.
    """
    # التحقق إذا السيرفر بريميوم
    if not premium_servers.get(interaction.guild.id, False):
        await interaction.response.send_message("هذا الأمر متاح فقط للسيرفرات البريميوم!", ephemeral=True)
        return

    # التحقق من الصلاحيات
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("عذرًا، هذا الأمر متاح فقط للمشرفين!", ephemeral=True)
        return

    try:
        # جلب كل الأعضاء في السيرفر
        members = interaction.guild.members

        # فلترة الأعضاء بناءً على الحالة (أونلاين، أوفلاين، الكل)
        filtered_members = []
        for member in members:
            if status == "all":
                filtered_members.append(member)
            elif status == "online" and member.status != discord.Status.offline:
                filtered_members.append(member)
            elif status == "offline" and member.status == discord.Status.offline:
                filtered_members.append(member)

        # رسالة تأكيد قبل الإرسال
        confirm_message = (
            f"سيتم إرسال البرودكاست إلى {len(filtered_members)} عضو.\n"
            f"هل تريد المتابعة؟"
        )

        # إنشاء الأزرار
        view = ConfirmationView(interaction, message, filtered_members)
        await interaction.response.send_message(confirm_message, view=view, ephemeral=True)

        # الانتظار حتى المستخدم يضغط على زر
        await view.wait()

        # لو المستخدم أكد
        if view.confirmed:
            success_count = 0
            failed_count = 0
            for member in filtered_members:
                try:
                    # التحقق إذا العضو يقبل الرسائل الخاصة
                    if member.dm_channel is None:
                        await member.create_dm()  # إنشاء قناة DM إذا كانت غير موجودة
                    await member.send(message)
                    success_count += 1
                except discord.Forbidden:
                    failed_count += 1
                    continue
                except Exception:
                    failed_count += 1
                    continue

            # رسالة تأكيد النجاح
            result_message = (
                f"تم إرسال البرودكاست بنجاح!\n"
                f"عدد الناجحين: {success_count}\n"
                f"عدد الفشل: {failed_count}"
            )
            await interaction.followup.send(result_message, ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"حدث خطأ أثناء إرسال البرودكاست: {e}", ephemeral=True)












welcome_channels = {}

class PollView(View):
    def __init__(self, options: list):
        super().__init__(timeout=None)
        self.options = options
        self.votes = {option: 0 for option in options}

        for option in options:
            button = Button(label=option, style=discord.ButtonStyle.blurple)
            button.callback = self.create_callback(option)
            self.add_item(button)

    def create_callback(self, option: str):
        async def callback(interaction: discord.Interaction):
            self.votes[option] += 1
            await interaction.response.send_message(f"تم تسجيل تصويتك على: {option}", ephemeral=True)
        return callback

@bot.tree.command(name="set_welcome_channel", description="اختيار قناة لإرسال رسائل الترحيب")
async def set_welcome_channel(interaction: discord.Interaction):
    # التحقق إذا السيرفر بريميوم
    if not premium_servers.get(interaction.guild.id, False):
        await interaction.response.send_message("هذا الأمر متاح فقط للسيرفرات البريميوم!", ephemeral=True)
        return

    # التحقق من الصلاحيات
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("عذرًا، هذا الأمر متاح فقط للمشرفين!", ephemeral=True)
        return

    # جلب القنوات النصية في السيرفر
    text_channels = [channel for channel in interaction.guild.text_channels]

    # إنشاء قائمة بأسماء القنوات
    channel_names = "\n".join([f"{i+1}. {channel.name}" for i, channel in enumerate(text_channels)])

    # إرسال رسالة لاختيار القناة
    await interaction.response.send_message(
        f"اختر رقم القناة اللي تبغى تعرض فيها رسائل الترحيب:\n{channel_names}",
        ephemeral=True
    )

    # تخزين القنوات مؤقتًا
    welcome_channels[interaction.guild.id] = text_channels

    # استقبال الرد من المستخدم (اختيار القناة)
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        channel_choice = await bot.wait_for("message", check=check, timeout=30)
        channel_index = int(channel_choice.content) - 1

        if 0 <= channel_index < len(text_channels):
            selected_channel = text_channels[channel_index]
            welcome_channels[interaction.guild.id] = selected_channel.id

            await interaction.followup.send(
                f"تم تفعيل رسائل الترحيب في القناة: {selected_channel.mention}",
                ephemeral=True
            )
        else:
            await interaction.followup.send("اختيار غير صحيح! العملية ألغيت.", ephemeral=True)

    except ValueError:
        await interaction.followup.send("اختيار غير صحيح! العملية ألغيت.", ephemeral=True)
    except TimeoutError:
        await interaction.followup.send("انتهت المدة الزمنية! العملية ألغيت.", ephemeral=True)

@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    if guild_id in welcome_channels:
        channel_id = welcome_channels[guild_id]
        channel = bot.get_channel(channel_id)

        if channel:
            welcome_message = (
                f"مرحبًا {member.mention}! 🎉\n"
                f"أهلاً بك في سيرفر **{member.guild.name}**.\n"
                f"نتمنى لك وقتًا ممتعًا معنا!"
            )
            await channel.send(welcome_message)











# قاموس لتخزين قنوات إشعارات الأذان لكل سيرفر
prayer_channels = {}

# API URL لأوقات الصلاة (Aladhan.com)
PRAYER_API_URL = "http://api.aladhan.com/v1/timingsByCity"

def get_prayer_times(city: str, country: str):
    params = {
        "city": city,
        "country": country,
        "method": 5,  # طريقة الحساب (5 = جامعة أم القرى)
    }
    response = requests.get(PRAYER_API_URL, params=params)
    if response.status_code == 200:
        data = response.json()["data"]["timings"]
        return data
    return None

@bot.tree.command(name="enable_prayer_times", description="تفعيل إشعارات أوقات الصلاة (بريميوم)")
async def enable_prayer_times(interaction: discord.Interaction):
    # التحقق إذا السيرفر بريميوم
    if not premium_servers.get(interaction.guild.id, False):
        await interaction.response.send_message("هذا الأمر متاح فقط للسيرفرات البريميوم!", ephemeral=True)
        return

    # التحقق من الصلاحيات
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("عذرًا، هذا الأمر متاح فقط للمشرفين!", ephemeral=True)
        return

    # جلب القنوات النصية في السيرفر
    text_channels = [channel for channel in interaction.guild.text_channels]

    # إنشاء قائمة بأسماء القنوات
    channel_names = "\n".join([f"{i+1}. {channel.name}" for i, channel in enumerate(text_channels)])

    # إرسال رسالة لاختيار القناة
    await interaction.response.send_message(
        f"اختر رقم القناة اللي تبغى تعرض فيها إشعارات أوقات الصلاة:\n{channel_names}",
        ephemeral=True
    )

    # تخزين القنوات مؤقتًا
    prayer_channels[interaction.guild.id] = text_channels

    # استقبال الرد من المستخدم (اختيار القناة)
    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        channel_choice = await bot.wait_for("message", check=check, timeout=30)
        channel_index = int(channel_choice.content) - 1

        if 0 <= channel_index < len(text_channels):
            selected_channel = text_channels[channel_index]
            prayer_channels[interaction.guild.id] = selected_channel.id

            await interaction.followup.send(
                f"تم تفعيل إشعارات أوقات الصلاة في القناة: {selected_channel.mention}",
                ephemeral=True
            )
        else:
            await interaction.followup.send("اختيار غير صحيح! العملية ألغيت.", ephemeral=True)

    except ValueError:
        await interaction.followup.send("اختيار غير صحيح! العملية ألغيت.", ephemeral=True)
    except TimeoutError:
        await interaction.followup.send("انتهت المدة الزمنية! العملية ألغيت.", ephemeral=True)

# وظيفة دورية للتحقق من أوقات الصلاة وإرسال الإشعارات
@tasks.loop(minutes=1)
async def check_prayer_times():
    for guild_id, channel_id in prayer_channels.items():
        channel = bot.get_channel(channel_id)
        if not channel:
            continue

        # تحديد المدينة والدولة (يمكنك تعديلها حسب الحاجة)
        city = "مكة"
        country = "السعودية"

        # جلب أوقات الصلاة
        prayer_times = get_prayer_times(city, country)
        if not prayer_times:
            continue

        # التحقق من الوقت الحالي
        now = datetime.now(pytz.timezone("Asia/Riyadh")).strftime("%H:%M")
        prayer_name = None

        if now == prayer_times["Dhuhr"]:
            prayer_name = "الظهر"
        elif now == prayer_times["Asr"]:
            prayer_name = "العصر"
        elif now == prayer_times["Maghrib"]:
            prayer_name = "المغرب"
        elif now == prayer_times["Isha"]:
            prayer_name = "العشاء"
        elif now == prayer_times["Fajr"]:
            prayer_name = "الفجر"

        # إرسال الإشعار إذا حان وقت الأذان
        if prayer_name:
            await channel.send(f"حان الآن وقت أذان **{prayer_name}** 🕌")

            
#قسم العاب و كوينزسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسسس






















































# تعريف القاموس الأساسي لتخزين البيتكوين
user_bitcoins = {}

# قائمة الممثلين
actors = {
    "Leonardo DiCaprio": ["ليوناردو ديكابريو", "Leonardo DiCaprio", "https://i.postimg.cc/sgSCXGgg/Leonardo-Di-Caprios.webp"],
    "Tom Hanks": ["توم هانكس", "Tom Hanks", "https://i.postimg.cc/QCyZBp7H/Tom-Hanks.webp"],
    "Brad Pitt": ["براد بيت", "Brad Pitt", "https://i.postimg.cc/VLhz5c9D/Brad-Pittea.webp"],
    "Angelina Jolie": ["أنجلينا جولي", "Angelina Jolie", "https://i.postimg.cc/fTqRXds7/Angelina-Jolie.jpg"],
    "Robert Downey Jr": ["روبرت داوني جونيور", "Robert Downey Jr", "https://i.postimg.cc/T1CYtLD6/Robert-Downey-Jr.jpg"],
    "Will Smith": ["ويل سميث", "Will Smith", "https://i.postimg.cc/dVXDMySQ/Will-Smith.webp"],
    "Johnny Depp": ["جوني ديب", "Johnny Depp", "https://i.postimg.cc/L5RnCFQz/Johnny-Depp.jpg"],
    "Dwayne Johnson": ["دواين جونسون", "Dwayne Johnson", "https://i.postimg.cc/9fK9BSjp/Dwayne-Johnson.jpg"],
    "Mohamed Ramadan": ["محمد رمضان", "Mohamed Ramadan", "https://i.postimg.cc/d01R6rZq/Mohamed-Ramadan.jpg"],
    "Ahmed Helmy": ["أحمد حلمي", "Ahmed Helmy", "https://i.postimg.cc/qqnxnrhy/Ahmed-Helmy.png"],
    "Amr Diab": ["عمرو دياب", "Amr Diab", "https://i.postimg.cc/5tNgrDTW/amr-deap.jpg"],
    "Eminem": ["ايمينيم", "Eminem", "https://i.postimg.cc/MX2j8jGj/Eminem.jpg"],
    "Drake": ["دريك", "Drake", "https://i.postimg.cc/VkXW5zQ8/Drake.jpg"]
}

# صور العملات
coin_images = {
    "Heads": "https://i.postimg.cc/DwFRyZdh/coin-hrad.jpg",
    "Tails": "https://i.postimg.cc/13j077zd/Tails.jpg"
}


# الأمر الأول: عرض المحفظة
@bot.tree.command(name="wallet", description="اعرض عدد البيتكوين التي تمتلكها ورتبتك!")
async def wallet(interaction: discord.Interaction):
    user_id = interaction.user.id
    bitcoins = user_bitcoins.get(user_id, 0)

    # تصنيفات الرتب
    ranks = {
        0: "🚶 مبتدئ",
        5: "🥉 لاعب محترف",
        10: "🥈 خبير",
        20: "🥇 أسطورة",
        50: "👑 ملك اللعبة",
        100: "🔥 إمبراطور العملات",
        500: "⚡ مليونير رقمي",
        1_000: "💎 قطب البيتكوين",
        5_000: "🏦 بارون الاقتصاد",
        10_000: "🦄 أسطورة الاقتصاد"
    }

    # البحث عن أعلى رتبة تناسب عدد البيتكوين
    rank = max((r for r in ranks if bitcoins >= r), default=0)
    rank_name = ranks[rank]

    embed = discord.Embed(title="💰 محفظتك", color=discord.Color.gold())
    embed.set_thumbnail(url="https://i.postimg.cc/yNwW1MYr/bitcoin-wallet.png")
    embed.add_field(name="👤 اللاعب:", value=interaction.user.mention, inline=True)
    embed.add_field(name="💎 بيتكوين:", value=f"**{bitcoins} BTC**", inline=True)
    embed.add_field(name="🏆 رتبتك:", value=rank_name, inline=False)

    await interaction.response.send_message(embed=embed)

# الأمر الثاني: إضافة بيتكوين (Admins Only)
@bot.tree.command(name="add_bitcoins", description="أضف بيتكوين لمستخدم (Admins Only)")
async def add_bitcoins(interaction: discord.Interaction, member: discord.Member, amount: int):
    # التحقق من صلاحيات الأدمن
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ ليس لديك صلاحية لاستخدام هذا الأمر!", ephemeral=True)
        return

    if amount <= 0:
        await interaction.response.send_message("❌ يجب أن يكون المبلغ أكبر من 0!", ephemeral=True)
        return

    user_bitcoins[member.id] = user_bitcoins.get(member.id, 0) + amount
    await interaction.response.send_message(f"✅ تم إضافة **{amount} بيتكوين** إلى {member.mention}!")

# الأمر الثالث: لعبة تخمين الممثلين
@bot.tree.command(name="guess", description="🎭 لعبة تخمين الممثلين الفخمة!")
async def guess(interaction: discord.Interaction):
    actor_name, actor_data = random.choice(list(actors.items()))
    actor_aliases, actor_image_url = actor_data[:-1], actor_data[-1]

    embed = discord.Embed(
        title="🎭 **لعبة الممثلين الفخمة**",
        description="👀 **من هو هذا الممثل؟**\n💬 *اكتب اسمه في الدردشة!*",
        color=discord.Color.gold()
    )
    embed.set_image(url=actor_image_url)
    embed.set_footer(text="⏳ لديك 30 ثانية للتخمين!")

    class HelpButtons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.used_help = set()

        @discord.ui.button(label="🔍 كشف أول وآخر حرف (-3 BTC)", style=discord.ButtonStyle.red, emoji="📖")
        async def reveal_letters(self, interaction: discord.Interaction, button: discord.ui.Button):
            user_id = interaction.user.id
            if user_id in self.used_help:
                await interaction.response.send_message("⚠️ **لقد استخدمت المساعدة بالفعل!**", ephemeral=True)
                return
            if user_bitcoins.get(user_id, 0) < 3:
                await interaction.response.send_message("❌ **ليس لديك بيتكوين كافٍ لهذه المساعدة!**", ephemeral=True)
                return
            user_bitcoins[user_id] -= 3
            self.used_help.add(user_id)
            hint = f"🔹 يبدأ اسمه بحرف **{actor_aliases[0][0]}** وينتهي بحرف **{actor_aliases[0][-1]}**."
            await interaction.response.send_message(f"💡 **تلميح:** {hint}", ephemeral=True)

        @discord.ui.button(label="📝 عدد الأحرف (-2 BTC)", style=discord.ButtonStyle.blurple, emoji="🔢")
        async def reveal_length(self, interaction: discord.Interaction, button: discord.ui.Button):
            user_id = interaction.user.id
            if user_id in self.used_help:
                await interaction.response.send_message("⚠️ **لقد استخدمت المساعدة بالفعل!**", ephemeral=True)
                return
            if user_bitcoins.get(user_id, 0) < 2:
                await interaction.response.send_message("❌ **ليس لديك بيتكوين كافٍ لهذه المساعدة!**", ephemeral=True)
                return
            user_bitcoins[user_id] -= 2
            self.used_help.add(user_id)
            hint = f"📏 اسم الممثل يحتوي على **{len(actor_aliases[0])}** أحرف."
            await interaction.response.send_message(f"💡 **تلميح:** {hint}", ephemeral=True)

    view = HelpButtons()
    await interaction.response.send_message(embed=embed, view=view)

    def check(message: discord.Message):
        return message.author == interaction.user and any(
            difflib.SequenceMatcher(None, message.content.lower(), alias.lower()).ratio() > 0.75
            for alias in actor_aliases
        )

    try:
        answer = await bot.wait_for('message', timeout=30.0, check=check)
        user_id = answer.author.id
        user_bitcoins[user_id] = user_bitcoins.get(user_id, 0) + 5
        win_embed = discord.Embed(
            title="🏆 **إجابة صحيحة!**",
            description=f"🎉 {answer.author.mention} **أحسنت! لقد ربحت 5 بيتكوين!**",
            color=discord.Color.green()
        )
        win_embed.set_footer(text="🔥 استمر في اللعب لتصبح ملك التحديات! 🏅")
        await interaction.channel.send(embed=win_embed)
    except asyncio.TimeoutError:
        lose_embed = discord.Embed(
            title="⏳ **انتهى الوقت!**",
            description=f"❌ لم يتمكن أحد من تخمين الاسم! الإجابة الصحيحة كانت: **{actor_name}**",
            color=discord.Color.red()
        )
        lose_embed.set_footer(text="🎭 حاول مرة أخرى في الجولة القادمة!")
        await interaction.channel.send(embed=lose_embed)

# الأمر الرابع: آلة الحظ
@bot.tree.command(name="slot", description="🎰 جرب حظك في آلة الحظ واربح البيتكوين!")
async def slot(interaction: discord.Interaction, bet: int):
    user_id = interaction.user.id

    # التحقق من صحة الرهان
    if bet <= 0 or user_bitcoins.get(user_id, 0) < bet:
        await interaction.response.send_message("❌ ليس لديك بيتكوين كافٍ!", ephemeral=True)
        return

    emojis = ["🍒", "🍋", "🔔", "⭐", "🍉", "🍇"]
    slot_result = [random.choice(emojis) for _ in range(3)]

    if slot_result[0] == slot_result[1] == slot_result[2]:
        winnings = bet * 3
        user_bitcoins[user_id] += winnings
        result_text = f"🎉 مبروك! ربحت **{winnings} بيتكوين**!"
    else:
        user_bitcoins[user_id] -= bet
        result_text = f"😢 لم تفز هذه المرة! خسرت **{bet} بيتكوين**."

    embed = discord.Embed(title="🎰 آلة الحظ", description=" ".join(slot_result), color=discord.Color.gold())
    embed.add_field(name="📜 النتيجة", value=result_text, inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="coinflip", description="🎯 لعبة قلب الجنيه المصري!")
async def coinflip(interaction: discord.Interaction, amount: int):
    user_id = interaction.user.id

    # التحقق من صحة الرهان
    if amount <= 0:
        await interaction.response.send_message("❌ **الرهان يجب أن يكون أكبر من 0 BTC!**", ephemeral=True)
        return
    if user_bitcoins.get(user_id, 0) < amount:
        await interaction.response.send_message(f"💰 **ليس لديك رصيد كافٍ! رصيدك الحالي: {user_bitcoins.get(user_id, 0)} BTC**", ephemeral=True)
        return

    # إنشاء رسالة Embed مع زرين للاختيار
    embed = discord.Embed(
        title="🎯 **لعبة قلب الجنيه المصري**",
        description=f"💰 **اختر وجه العملة الذي تراهن عليه!**\n🎲 **رهانك:** {amount} BTC",
        color=discord.Color.gold()
    )
    embed.set_thumbnail(url="https://i.postimg.cc/DwFRyZdh/coin-hrad.jpg")
    embed.set_footer(text=f"رصيدك الحالي: {user_bitcoins[user_id]} BTC")

    class CoinButtons(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=30)  # وقت انتهاء بعد 30 ثانية
            self.choice = None  # تخزين اختيار المستخدم

        @discord.ui.button(label="🪙 Heads", style=discord.ButtonStyle.primary)
        async def heads_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.choice = "Heads"
            await self.process_bet(interaction)

        @discord.ui.button(label="🪙 Tails", style=discord.ButtonStyle.danger)
        async def tails_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.choice = "Tails"
            await self.process_bet(interaction)

        async def process_bet(self, interaction: discord.Interaction):
            # إذا لم يختر المستخدم أي شيء
            if not self.choice:
                await interaction.response.send_message("⚠️ **يجب عليك اختيار وجه العملة أولاً!**", ephemeral=True)
                return

            # اختيار النتيجة العشوائية
            result = random.choice(["Heads", "Tails"])
            user_wins = (result == self.choice)

            # تحديث الرصيد بناءً على النتيجة
            if user_wins:
                user_bitcoins[user_id] += amount
                result_text = f"🎉 {interaction.user.mention} **لقد ربحت {amount} BTC!**"
                color = discord.Color.green()
            else:
                user_bitcoins[user_id] -= amount
                result_text = f"😢 {interaction.user.mention} **لقد خسرت {amount} BTC... حاول مرة أخرى!**"
                color = discord.Color.red()

            # إرسال النتيجة
            result_embed = discord.Embed(
                title="🎯 **نتيجة قلب الجنيه**",
                description=f"{result_text}\n💸 **وجه العملة:** {result}\n💰 **رصيدك الحالي:** {user_bitcoins[user_id]} BTC",
                color=color
            )
            result_embed.set_image(url=coin_images[result])
            result_embed.set_footer(text="🔥 العب بحكمة ولا تخاطر بكل شيء!")
            await interaction.response.edit_message(embed=result_embed, view=None)

    # إرسال الرسالة مع الأزرار
    view = CoinButtons()
    await interaction.response.send_message(embed=embed, view=view)
    










@bot.tree.command(name="sync", description="Sync commands with Discord")
async def sync(interaction: discord.Interaction):
    await bot.tree.sync()
    await interaction.response.send_message("Commands synced!", ephemeral=True)










# تشغيل البوت
bot.run("MTM0MzU4MDA0MDc3NTk5NTQwMg.Gga_XG.JdrICq3t2eIRPgDXz8gDgDuFCCv87kouIgcioI")
