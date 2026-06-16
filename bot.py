# ==================================================
# ЧАСТЬ 1: Импорт библиотек
# ==================================================
import discord
from discord.ext import commands
import os

# ==================================================
# КРАСИВЫЙ БАННЕР ПРИ ЗАПУСКЕ
# ==================================================

def print_banner():
    """Печатает красивый баннер при запуске бота"""
    
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║    ██████╗ ███████╗██╗   ██╗                           ║
    ║    ██╔══██╗██╔════╝██║   ██║                           ║
    ║    ██║  ██║█████╗  ██║   ██║                           ║
    ║    ██║  ██║██╔══╝  ╚██╗ ██╔╝                           ║
    ║    ██████╔╝███████╗ ╚████╔╝                            ║
    ║    ╚═════╝ ╚══════╝  ╚═══╝                             ║
    ║                                                          ║
    ║               ██████╗  ██████╗ ████████╗                ║
    ║               ██╔══██╗██╔═══██╗╚══██╔══╝                ║
    ║               ██████╔╝██║   ██║   ██║                   ║
    ║               ██╔══██╗██║   ██║   ██║                   ║
    ║               ██████╔╝╚██████╔╝   ██║                   ║
    ║               ╚═════╝  ╚═════╝    ╚═╝                   ║
    ║                                                          ║
    ║              ╔══════════════════════════════╗            ║
    ║              ║  🚀 DEV - Nikichz1337 🚀     ║            ║
    ║              ╚══════════════════════════════╝            ║
    ║                                                          ║
    ║           🔥 Бот успешно запущен! 🔥                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    
    # Цветной текст в консоли (ANSI коды)
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
        'bold': '\033[1m'
    }
    
    print(f"{colors['cyan']}{colors['bold']}")
    print(banner)
    print(f"{colors['reset']}")

# ==================================================
# ЧАСТЬ 2: НАСТРОЙКИ (ЗАМЕНИ ЭТИ ЗНАЧЕНИЯ!)
# ==================================================

TOKEN = os.getenv('TOKEN', "Токен Бота")
VERIFIED_ROLE_ID = 1516513960415989902
SECOND_ROLE_ID = 1516514134601109555
CHANNEL_ID = 1516496993118322899

CATEGORY_ID = 1516522170493440135
CREATE_CHANNEL_ID = 1516522802407276674

channel_pairs = {}
channel_owners = {}

# ==================================================
# ЧАСТЬ 3: НАСТРОЙКА ПРАВ БОТА
# ==================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ==================================================
# СОБЫТИЕ ГОТОВНОСТИ БОТА
# ==================================================

@bot.event
async def on_ready():
    """Срабатывает, когда бот готов к работе"""
    print(f"\033[92m✅ Бот {bot.user} успешно запущен!\033[0m")
    print(f"\033[93m📊 На серверах: {len(bot.guilds)}\033[0m")
    print(f"\033[94m🔗 Пригласительная ссылка: https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot\033[0m")
    print(f"\033[96m{'='*50}\033[0m")

# ==================================================
# ЧАСТЬ 4: КОМАНДА /verify
# ==================================================

@bot.command()
@commands.has_permissions(administrator=True)
async def verify(ctx):
    button = discord.ui.Button(
        label='✅ Верифицироваться',
        style=discord.ButtonStyle.green,
        custom_id='verify_button'
    )
    view = discord.ui.View()
    view.add_item(button)
    await ctx.send('Нажми на кнопку ниже, чтобы получить доступ к серверу!', view=view)
    await ctx.message.delete()

# ==================================================
# ЧАСТЬ 5: ОБРАБОТЧИК ВЕРИФИКАЦИИ
# ==================================================

@bot.event
async def on_interaction(interaction):
    # === ВЕРИФИКАЦИЯ ===
    if interaction.data and interaction.data.get('custom_id') == 'verify_button':
        try:
            member = interaction.user
            guild = interaction.guild
            
            role1 = guild.get_role(VERIFIED_ROLE_ID)
            role2 = guild.get_role(SECOND_ROLE_ID)
            
            if role1 in member.roles:
                await interaction.response.send_message('❌ Вы уже верифицированы!', ephemeral=True)
                return
            
            if role1 is None:
                await interaction.response.send_message('❌ Ошибка: роль не найдена!', ephemeral=True)
                return
            
            await member.add_roles(role1, role2)
            await interaction.response.send_message('✅ Верификация пройдена!', ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f'❌ Ошибка', ephemeral=True)
    
    # === УПРАВЛЕНИЕ ПРИВАТНЫМ КАНАЛОМ ===
    await handle_management_buttons(interaction)

# ==================================================
# ЧАСТЬ 6: ПРИВАТНЫЕ КАНАЛЫ
# ==================================================

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return
    
    if after.channel and after.channel.id == CREATE_CHANNEL_ID:
        await create_private_channel(member, after.channel)
    
    if before.channel and before.channel.id != CREATE_CHANNEL_ID:
        if before.channel.id in channel_pairs:
            await update_control_panel(before.channel)
            if len(before.channel.members) == 0:
                await delete_private_channel(before.channel)

async def create_private_channel(member, source_channel):
    guild = member.guild
    category = guild.get_channel(CATEGORY_ID)
    
    if not category:
        print(f"❌ Категория не найдена! ID: {CATEGORY_ID}")
        return
    
    channel_name = f"🔊 {member.display_name}"
    text_name = f"📝 {member.display_name}"
    verified_role = guild.get_role(VERIFIED_ROLE_ID)
    
    voice_overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=False, view_channel=False),
        member: discord.PermissionOverwrite(connect=True, manage_channels=True, view_channel=True),
        guild.me: discord.PermissionOverwrite(connect=True, manage_channels=True, view_channel=True),
    }
    
    if verified_role:
        voice_overwrites[verified_role] = discord.PermissionOverwrite(connect=True, view_channel=True)
    
    voice_channel = await guild.create_voice_channel(
        name=channel_name,
        category=category,
        overwrites=voice_overwrites,
        bitrate=source_channel.bitrate,
        user_limit=0
    )
    
    text_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, manage_channels=True, view_channel=True),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, manage_channels=True, view_channel=True),
    }
    
    text_channel = await guild.create_text_channel(
        name=text_name,
        category=category,
        overwrites=text_overwrites,
        position=voice_channel.position + 1
    )
    
    channel_pairs[voice_channel.id] = text_channel.id
    channel_owners[voice_channel.id] = member.id
    
    await member.move_to(voice_channel)
    
    embed, view = create_control_panel(voice_channel, member)
    await text_channel.send(f"👋 Привет, {member.mention}!", embed=embed, view=view)

async def update_control_panel(voice_channel):
    guild = voice_channel.guild
    
    if voice_channel.id not in channel_pairs:
        return
    
    text_id = channel_pairs[voice_channel.id]
    text_channel = guild.get_channel(text_id)
    if not text_channel:
        return
    
    try:
        owner_id = channel_owners.get(voice_channel.id)
        owner = guild.get_member(owner_id) if owner_id else None
        
        if not owner and voice_channel.members:
            owner = voice_channel.members[0]
        
        if not owner:
            await text_channel.delete()
            del channel_pairs[voice_channel.id]
            del channel_owners[voice_channel.id]
            return
        
        async for msg in text_channel.history(limit=10):
            if msg.author == bot.user and msg.embeds:
                embed, view = create_control_panel(voice_channel, owner)
                await msg.edit(embed=embed, view=view)
                break
        
    except Exception as e:
        print(f"Ошибка обновления панели: {e}")

def create_control_panel(voice_channel, owner):
    members_list = "\n".join([f"• {m.display_name}" for m in voice_channel.members]) or "Нет участников"
    owner_in_channel = owner in voice_channel.members if owner else False
    
    embed = discord.Embed(
        title=f"🎛️ Управление каналом",
        color=discord.Color.green()
    )
    
    status = "🟢 Открыт"
    if voice_channel.overwrites_for(voice_channel.guild.default_role).connect is False:
        status = "🔴 Закрыт"
    
    embed.add_field(name="📊 Статус", value=status, inline=True)
    
    if owner_in_channel and owner:
        embed.add_field(name="👑 Владелец", value=owner.mention, inline=True)
    else:
        embed.add_field(name="👑 Владелец", value="❌ Не в канале", inline=True)
    
    embed.add_field(name="👥 Участников", value=f"{len(voice_channel.members)}", inline=True)
    embed.add_field(name="👤 В канале", value=members_list, inline=False)
    
    limit = voice_channel.user_limit
    if limit == 0:
        limit_text = "♾️ Без лимита"
    else:
        limit_text = f"{limit} человек" if limit == 1 else f"{limit} человека"
    
    embed.add_field(name="📊 Лимит", value=limit_text, inline=True)
    embed.add_field(name="🔊 Канал", value=voice_channel.mention, inline=True)
    embed.set_footer(text="Нажимай на кнопки для управления")
    
    view = discord.ui.View()
    
    view.add_item(discord.ui.Button(
        label='🔒 Закрыть',
        style=discord.ButtonStyle.red,
        custom_id=f'lock_{voice_channel.id}'
    ))
    view.add_item(discord.ui.Button(
        label='🔓 Открыть',
        style=discord.ButtonStyle.green,
        custom_id=f'unlock_{voice_channel.id}'
    ))
    
    view.add_item(discord.ui.Button(
        label='👻 Скрыть',
        style=discord.ButtonStyle.secondary,
        custom_id=f'hide_{voice_channel.id}'
    ))
    view.add_item(discord.ui.Button(
        label='👀 Показать',
        style=discord.ButtonStyle.primary,
        custom_id=f'show_{voice_channel.id}'
    ))
    
    limit_options = [
        discord.SelectOption(label="♾️ Без лимита", value="0"),
        discord.SelectOption(label="1 человек", value="1"),
        discord.SelectOption(label="2 человека", value="2"),
        discord.SelectOption(label="3 человека", value="3"),
        discord.SelectOption(label="4 человека", value="4"),
        discord.SelectOption(label="5 человек", value="5"),
        discord.SelectOption(label="6 человек", value="6"),
        discord.SelectOption(label="7 человек", value="7"),
        discord.SelectOption(label="8 человек", value="8"),
        discord.SelectOption(label="9 человек", value="9"),
        discord.SelectOption(label="10 человек", value="10"),
    ]
    limit_select = discord.ui.Select(
        placeholder='👥 Выбрать лимит',
        options=limit_options,
        custom_id=f'limit_{voice_channel.id}'
    )
    view.add_item(limit_select)
    
    view.add_item(discord.ui.Button(
        label='✏️ Переименовать',
        style=discord.ButtonStyle.primary,
        custom_id=f'rename_{voice_channel.id}'
    ))
    
    view.add_item(discord.ui.Button(
        label='🗑️ Удалить канал',
        style=discord.ButtonStyle.danger,
        custom_id=f'delete_{voice_channel.id}'
    ))
    
    return embed, view

async def delete_private_channel(channel):
    guild = channel.guild
    
    if channel.id in channel_pairs:
        text_id = channel_pairs[channel.id]
        text_channel = guild.get_channel(text_id)
        if text_channel:
            await text_channel.delete()
        del channel_pairs[channel.id]
    
    if channel.id in channel_owners:
        del channel_owners[channel.id]
    
    await channel.delete()

# ==================================================
# ЧАСТЬ 7: ОБРАБОТЧИК КНОПОК УПРАВЛЕНИЯ
# ==================================================

async def handle_management_buttons(interaction):
    if not interaction.data:
        return
    
    custom_id = interaction.data.get('custom_id')
    if not custom_id:
        return
    
    parts = custom_id.split('_')
    if len(parts) < 2:
        return
    
    action = parts[0]
    voice_id = int(parts[1])
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        voice_channel = interaction.guild.get_channel(voice_id)
        if not voice_channel:
            await interaction.followup.send('❌ Канал не найден.', ephemeral=True)
            return
        
        owner_id = channel_owners.get(voice_channel.id)
        is_owner = interaction.user.id == owner_id
        is_admin = interaction.user.guild_permissions.administrator
        
        if not is_owner and not is_admin:
            await interaction.followup.send('❌ Ты не владелец этого канала!', ephemeral=True)
            return
        
        if action == 'lock':
            for role in interaction.guild.roles:
                if role.id != interaction.user.top_role.id and role.id != interaction.guild.me.top_role.id:
                    await voice_channel.set_permissions(role, overwrite=None)
            
            await voice_channel.set_permissions(interaction.guild.default_role, connect=False)
            await voice_channel.set_permissions(interaction.user, connect=True)
            await voice_channel.set_permissions(interaction.guild.me, connect=True)
            
            verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
            if verified_role:
                await voice_channel.set_permissions(verified_role, connect=False)
            
            await interaction.followup.send('🔒 Канал закрыт!', ephemeral=True)
            await update_control_panel(voice_channel)
        
        elif action == 'unlock':
            for role in interaction.guild.roles:
                if role.id != interaction.user.top_role.id and role.id != interaction.guild.me.top_role.id:
                    await voice_channel.set_permissions(role, overwrite=None)
            
            await voice_channel.set_permissions(interaction.guild.default_role, overwrite=None)
            
            verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
            if verified_role:
                await voice_channel.set_permissions(verified_role, connect=True)
            
            await voice_channel.set_permissions(interaction.user, connect=True)
            await voice_channel.set_permissions(interaction.guild.me, connect=True)
            
            await interaction.followup.send('🔓 Канал открыт!', ephemeral=True)
            await update_control_panel(voice_channel)
        
        elif action == 'hide':
            await voice_channel.edit(category=None)
            
            for role in interaction.guild.roles:
                if role.id != interaction.user.top_role.id and role.id != interaction.guild.me.top_role.id:
                    await voice_channel.set_permissions(role, connect=False, view_channel=False)
            
            await voice_channel.set_permissions(interaction.user, connect=True, view_channel=True)
            await voice_channel.set_permissions(interaction.guild.me, connect=True, view_channel=True)
            
            await interaction.followup.send('👻 Канал скрыт!', ephemeral=True)
            await update_control_panel(voice_channel)
        
        elif action == 'show':
            category = interaction.guild.get_channel(CATEGORY_ID)
            if category:
                await voice_channel.edit(category=category)
                
                for role in interaction.guild.roles:
                    if role.id != interaction.user.top_role.id and role.id != interaction.guild.me.top_role.id:
                        await voice_channel.set_permissions(role, overwrite=None)
                
                verified_role = interaction.guild.get_role(VERIFIED_ROLE_ID)
                if verified_role:
                    await voice_channel.set_permissions(verified_role, connect=True, view_channel=True)
                
                await voice_channel.set_permissions(interaction.user, connect=True, view_channel=True)
                await voice_channel.set_permissions(interaction.guild.me, connect=True, view_channel=True)
                
                await interaction.followup.send('👀 Канал показан!', ephemeral=True)
                await update_control_panel(voice_channel)
            else:
                await interaction.followup.send('❌ Категория не найдена.', ephemeral=True)
        
        elif action == 'limit':
            value = int(interaction.data.get('values', ['0'])[0])
            await voice_channel.edit(user_limit=value)
            
            if value == 0:
                limit_text = "♾️ Без лимита"
            else:
                limit_text = f"{value} человек" if value == 1 else f"{value} человека"
            
            await interaction.followup.send(f'✅ Лимит: **{limit_text}**', ephemeral=True)
            await update_control_panel(voice_channel)
        
        elif action == 'rename':
            await interaction.followup.send('✏️ Напиши новое имя канала в чат.', ephemeral=True)
            
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel
            
            try:
                msg = await bot.wait_for('message', timeout=30.0, check=check)
                new_name = msg.content[:100]
                
                await voice_channel.edit(name=f"🔊 {new_name}")
                await interaction.channel.edit(name=f"📝 {new_name}")
                
                await interaction.followup.send(f'✅ Канал переименован в **{new_name}**!', ephemeral=True)
                await msg.delete()
                await update_control_panel(voice_channel)
            except:
                await interaction.followup.send('❌ Время вышло!', ephemeral=True)
        
        elif action == 'delete':
            await interaction.followup.send('⚠️ Напиши `да` для подтверждения удаления.', ephemeral=True)
            
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel and m.content.lower() == 'да'
            
            try:
                await bot.wait_for('message', timeout=30.0, check=check)
                await delete_private_channel(voice_channel)
                await interaction.followup.send('🗑️ Канал удален!', ephemeral=True)
            except:
                await interaction.followup.send('❌ Отменено.', ephemeral=True)
    
    except Exception as e:
        await interaction.followup.send(f'❌ Ошибка: {str(e)}', ephemeral=True)

# ==================================================
# ЧАСТЬ 8: КОМАНДЫ
# ==================================================

@bot.command()
@commands.has_permissions(administrator=True)
async def cleanup(ctx):
    guild = ctx.guild
    deleted = 0
    
    for channel in guild.voice_channels:
        if channel.category_id == CATEGORY_ID and len(channel.members) == 0:
            if channel.id != CREATE_CHANNEL_ID:
                if channel.id in channel_pairs:
                    text_id = channel_pairs[channel.id]
                    text_channel = guild.get_channel(text_id)
                    if text_channel:
                        await text_channel.delete()
                    del channel_pairs[channel.id]
                
                if channel.id in channel_owners:
                    del channel_owners[channel.id]
                
                await channel.delete()
                deleted += 1
    
    await ctx.send(f"🗑️ Удалено {deleted} каналов.", ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def restore_panels(ctx):
    guild = ctx.guild
    category = guild.get_channel(CATEGORY_ID)
    
    if not category:
        await ctx.send(f"❌ Категория не найдена!", ephemeral=True)
        return
    
    restored = 0
    skipped = 0
    
    for channel in category.voice_channels:
        if channel.id == CREATE_CHANNEL_ID:
            continue
        
        if channel.id in channel_pairs:
            skipped += 1
            continue
        
        owner_id = channel_owners.get(channel.id)
        owner = guild.get_member(owner_id) if owner_id else None
        
        if not owner and channel.members:
            owner = channel.members[0]
        
        if not owner:
            skipped += 1
            continue
        
        text_name = f"📝 {owner.display_name}"
        text_overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False, send_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, manage_channels=True, view_channel=True),
            owner: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, manage_channels=True, view_channel=True),
        }
        
        text_channel = await guild.create_text_channel(
            name=text_name,
            category=category,
            overwrites=text_overwrites,
            position=channel.position + 1
        )
        
        channel_pairs[channel.id] = text_channel.id
        channel_owners[channel.id] = owner.id
        
        embed, view = create_control_panel(channel, owner)
        await text_channel.send(f"👋 Привет, {owner.mention}!", embed=embed, view=view)
        restored += 1
    
    embed = discord.Embed(
        title="✅ Панели восстановлены!",
        color=discord.Color.green()
    )
    embed.add_field(name="📊 Восстановлено", value=f"{restored}", inline=True)
    embed.add_field(name="⏭️ Пропущено", value=f"{skipped} (уже есть или пустые)", inline=True)
    
    await ctx.send(embed=embed, ephemeral=True)

@bot.command()
@commands.has_permissions(administrator=True)
async def check_channels(ctx):
    guild = ctx.guild
    
    embed = discord.Embed(
        title="🔍 Проверка каналов",
        color=discord.Color.blue()
    )
    
    category = guild.get_channel(CATEGORY_ID)
    embed.add_field(
        name="📁 Категория",
        value=f"{category.mention if category else '❌ НЕ НАЙДЕНА!'}",
        inline=False
    )
    
    create_channel = guild.get_channel(CREATE_CHANNEL_ID)
    embed.add_field(
        name="🎤 Канал для создания",
        value=f"{create_channel.mention if create_channel else '❌ НЕ НАЙДЕН!'}",
        inline=False
    )
    
    if channel_pairs:
        channels_list = "\n".join([f"<#{ch_id}> (📝)" for ch_id in channel_pairs.values()])
        embed.add_field(name="📝 Текстовые каналы управления", value=channels_list, inline=False)
    else:
        embed.add_field(name="📝 Текстовые каналы управления", value="Нет активных каналов", inline=False)
    
    await ctx.send(embed=embed, ephemeral=True)

# ==================================================
# ЧАСТЬ 9: ЗАПУСК БОТА
# ==================================================

if __name__ == "__main__":
    # Печатаем красивый баннер
    print_banner()
    
    # Запускаем бота
    bot.run(TOKEN)