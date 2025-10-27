"""
Discord Self-bot - Kieran V0.3
Python 3.13 Compatible (CGI Fix Included)
Works on Pydroid3

IMPORTANT - Installation:
Self-bots require discord.py-self (not regular discord.py)

pip uninstall discord.py
pip install discord.py-self aiohttp colorama

WARNING: Self-bots violate Discord ToS = PERMANENT BAN RISK
Educational purposes only!
"""

# ========================================
# FIX FOR PYTHON 3.13 CGI MODULE REMOVAL
# ========================================
import sys
from html import escape as html_escape

class cgi:
    """Polyfill for removed cgi module in Python 3.13"""
    
    @staticmethod
    def escape(s, quote=True):
        return html_escape(s, quote=quote)
    
    def parse_header(line):
        parts = line.split(';')
        main = parts[0].strip()
        pdict = {}
        for p in parts[1:]:
            if '=' in p:
                name, val = p.split('=', 1)
                name = name.strip().lower()
                val = val.strip()
                if val[0] == val[-1] == '"':
                    val = val[1:-1]
                pdict[name] = val
        return main, pdict

sys.modules['cgi'] = cgi

# ========================================
# NOW IMPORT DISCORD (AFTER CGI FIX)
# ========================================
import discord
import asyncio
import os
from datetime import datetime, timedelta
from collections import defaultdict

# ========================================
# COLOR SUPPORT
# ========================================
try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
    COLORS_ENABLED = True
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        RED = YELLOW = GREEN = CYAN = MAGENTA = BLUE = WHITE = LIGHTRED_EX = LIGHTGREEN_EX = LIGHTCYAN_EX = LIGHTMAGENTA_EX = ""
    class Back:
        BLACK = ""
    class Style:
        BRIGHT = RESET_ALL = ""
    COLORS_ENABLED = False

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔═══════════════════════════════════════╗")
    print("║         KIERAN SELF-BOT V0.3          ║")
    print("╚═══════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    print(f"{Fore.RED}{Style.BRIGHT}⚠️  WARNING: Self-bots violate Discord ToS!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Using this can result in PERMANENT ACCOUNT BAN{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Use at your own risk - Educational purposes only{Style.RESET_ALL}\n")

def get_token():
    print(f"{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{Style.BRIGHT}Enter your Discord token:{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    
    while True:
        token = input(f"{Fore.YELLOW}Token: {Style.RESET_ALL}").strip()
        if len(token) > 50:
            return token
        else:
            print(f"{Fore.RED}Invalid token (too short). Try again.{Style.RESET_ALL}\n")

def show_menu():
    clear_screen()
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔═══════════════════════════════════════╗")
    print("║         KIERAN SELF-BOT V0.3          ║")
    print("╚═══════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[ 1 ]{Style.RESET_ALL} - Nickname Changer")
    print(f"{Fore.MAGENTA}[ 2 ]{Style.RESET_ALL} - Anti-Nuke Protection (Monitor Server)")
    print(f"{Fore.CYAN}[ 3 ]{Style.RESET_ALL} - View Nuke Statistics & Graph")
    print(f"{Fore.RED}[ 4 ]{Style.RESET_ALL} - Exit")
    print(f"{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    
    while True:
        choice = input(f"{Fore.YELLOW}Select option: {Style.RESET_ALL}").strip()
        if choice in ['1', '2', '3', '4']:
            return choice
        else:
            print(f"{Fore.RED}Invalid choice. Enter 1-4{Style.RESET_ALL}\n")

def get_server_id():
    print(f"\n{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{Style.BRIGHT}Enter Server ID{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    
    while True:
        server_id_str = input(f"{Fore.YELLOW}Server ID: {Style.RESET_ALL}").strip()
        try:
            server_id = int(server_id_str)
            if len(str(server_id)) >= 17:
                return server_id
            else:
                print(f"{Fore.RED}Invalid Server ID (too short). Try again.{Style.RESET_ALL}\n")
        except ValueError:
            print(f"{Fore.RED}Invalid Server ID (must be numbers only). Try again.{Style.RESET_ALL}\n")

def confirm_nickname_change():
    print(f"\n{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}{Style.BRIGHT}NICKNAME CHANGER CONFIGURATION{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}This will:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Change nicknames for Online/Idle/DND members{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Process 10 members at a time (1.8s delay each){Style.RESET_ALL}")
    print(f"{Fore.WHITE}• 3 second cooldown after every 10 changes{Style.RESET_ALL}")
    print(f"{Fore.WHITE}• Run continuously until you stop it{Style.RESET_ALL}")
    print(f"\n{Fore.YELLOW}Do you want to continue?{Style.RESET_ALL}")
    
    response = input(f"{Fore.YELLOW}Type 'yes' to continue, anything else to cancel: {Style.RESET_ALL}").strip().lower()
    return response == 'yes'

# Global variables
TOKEN = None
SERVER_ID = None
client = None
NUKE_PROTECTION_ENABLED = False

# Anti-Nuke Detection Variables
ban_tracker = defaultdict(list)
kick_tracker = defaultdict(list)
channel_delete_tracker = defaultdict(list)
role_delete_tracker = defaultdict(list)

# Statistics tracking
nuke_statistics = {
    'total_nukes_detected': 0,
    'total_bans_detected': 0,
    'total_kicks_detected': 0,
    'total_channels_deleted': 0,
    'total_roles_deleted': 0,
    'nuke_events': [],  # List of (timestamp, type, count)
    'nukers': defaultdict(int)  # Track who did the nuking
}

# Thresholds for nuke detection
NUKE_THRESHOLDS = {
    'bans': 5,        # 5 bans in timeframe = nuke
    'kicks': 8,       # 8 kicks in timeframe = nuke
    'channels': 3,    # 3 channel deletes = nuke
    'roles': 4,       # 4 role deletes = nuke
    'timeframe': 30   # 30 seconds timeframe
}

def draw_bar_graph(data, max_width=40):
    """Draw a simple ASCII bar graph"""
    if not data:
        return "No data available"
    
    max_val = max(data.values()) if data else 1
    graph = ""
    
    for label, value in data.items():
        bar_length = int((value / max_val) * max_width) if max_val > 0 else 0
        bar = "█" * bar_length
        graph += f"{label:20} {bar} {value}\n"
    
    return graph

def show_nuke_statistics():
    """Display nuke statistics with graphs"""
    clear_screen()
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("╔════════════════════════════════════════════╗")
    print("║       NUKE DETECTION STATISTICS            ║")
    print("╚════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}\n")
    
    # Overall Statistics
    print(f"{Fore.YELLOW}{Style.BRIGHT}═══ OVERALL STATISTICS ═══{Style.RESET_ALL}")
    print(f"{Fore.RED}Total Nukes Detected: {nuke_statistics['total_nukes_detected']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Total Bans Detected: {nuke_statistics['total_bans_detected']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Total Kicks Detected: {nuke_statistics['total_kicks_detected']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Total Channels Deleted: {nuke_statistics['total_channels_deleted']}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Total Roles Deleted: {nuke_statistics['total_roles_deleted']}{Style.RESET_ALL}")
    
    # Graph: Actions by Type
    print(f"\n{Fore.CYAN}{Style.BRIGHT}═══ ACTIONS BY TYPE ═══{Style.RESET_ALL}")
    action_data = {
        'Bans': nuke_statistics['total_bans_detected'],
        'Kicks': nuke_statistics['total_kicks_detected'],
        'Channels': nuke_statistics['total_channels_deleted'],
        'Roles': nuke_statistics['total_roles_deleted']
    }
    print(draw_bar_graph(action_data))
    
    # Graph: Top Nukers
    if nuke_statistics['nukers']:
        print(f"{Fore.RED}{Style.BRIGHT}═══ TOP NUKERS ═══{Style.RESET_ALL}")
        top_nukers = dict(sorted(nuke_statistics['nukers'].items(), 
                                key=lambda x: x[1], reverse=True)[:5])
        print(draw_bar_graph(top_nukers))
    
    # Recent Nuke Events
    if nuke_statistics['nuke_events']:
        print(f"{Fore.MAGENTA}{Style.BRIGHT}═══ RECENT NUKE EVENTS ═══{Style.RESET_ALL}")
        recent = nuke_statistics['nuke_events'][-10:]  # Last 10 events
        for i, (timestamp, nuke_type, count, nuker) in enumerate(reversed(recent), 1):
            time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{Fore.YELLOW}{i}.{Style.RESET_ALL} {Fore.WHITE}{time_str}{Style.RESET_ALL} - "
                  f"{Fore.RED}{nuke_type.upper()}{Style.RESET_ALL} ({count} actions) - "
                  f"{Fore.CYAN}by {nuker}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}")
    input(f"\n{Fore.GREEN}Press Enter to return to menu...{Style.RESET_ALL}")

async def check_nuke_activity(guild_id, action_type, entry=None):
    """Check if recent activity indicates a nuke attempt"""
    now = datetime.now()
    cutoff = now - timedelta(seconds=NUKE_THRESHOLDS['timeframe'])
    
    # Get nuker info if available
    nuker = "Unknown"
    if entry and hasattr(entry, 'user'):
        nuker = f"{entry.user.name}#{entry.user.discriminator}"
    
    # Clean old entries and add new one
    if action_type == 'ban':
        ban_tracker[guild_id] = [t for t in ban_tracker[guild_id] if t > cutoff]
        ban_tracker[guild_id].append(now)
        count = len(ban_tracker[guild_id])
        threshold = NUKE_THRESHOLDS['bans']
        nuke_statistics['total_bans_detected'] += 1
    elif action_type == 'kick':
        kick_tracker[guild_id] = [t for t in kick_tracker[guild_id] if t > cutoff]
        kick_tracker[guild_id].append(now)
        count = len(kick_tracker[guild_id])
        threshold = NUKE_THRESHOLDS['kicks']
        nuke_statistics['total_kicks_detected'] += 1
    elif action_type == 'channel':
        channel_delete_tracker[guild_id] = [t for t in channel_delete_tracker[guild_id] if t > cutoff]
        channel_delete_tracker[guild_id].append(now)
        count = len(channel_delete_tracker[guild_id])
        threshold = NUKE_THRESHOLDS['channels']
        nuke_statistics['total_channels_deleted'] += 1
    elif action_type == 'role':
        role_delete_tracker[guild_id] = [t for t in role_delete_tracker[guild_id] if t > cutoff]
        role_delete_tracker[guild_id].append(now)
        count = len(role_delete_tracker[guild_id])
        threshold = NUKE_THRESHOLDS['roles']
        nuke_statistics['total_roles_deleted'] += 1
    else:
        return False, 0, nuker
    
    is_nuke = count >= threshold
    
    if is_nuke:
        nuke_statistics['total_nukes_detected'] += 1
        nuke_statistics['nuke_events'].append((now, action_type, count, nuker))
        nuke_statistics['nukers'][nuker] += 1
    
    return is_nuke, count, nuker

async def nuke_alert(guild, action_type, count, nuker):
    """Send alert when nuke is detected"""
    print(f"\n{Fore.RED}{Back.BLACK}{Style.BRIGHT}{'═' * 60}{Style.RESET_ALL}")
    print(f"{Fore.RED}{Back.BLACK}{Style.BRIGHT}  NUKE DETECTED! SERVER UNDER ATTACK!  {Style.RESET_ALL}")
    print(f"{Fore.RED}{Back.BLACK}{Style.BRIGHT}{'═' * 60}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Server: {Style.BRIGHT}{guild.name}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Attack Type: {Style.BRIGHT}{action_type.upper()}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Action Count: {Style.BRIGHT}{count} in {NUKE_THRESHOLDS['timeframe']} seconds{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Suspected Nuker: {Style.BRIGHT}{Fore.RED}{nuker}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Time: {Style.BRIGHT}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
    print(f"{Fore.RED}{Back.BLACK}{Style.BRIGHT}{'═' * 60}{Style.RESET_ALL}\n")
    
    # Send DM notification to yourself
    try:
        alert_msg = (
            f"**NUKE ALERT**\n"
            f"**Server:** {guild.name}\n"
            f"**Attack Type:** {action_type.upper()}\n"
            f"**Count:** {count} actions in {NUKE_THRESHOLDS['timeframe']}s\n"
            f"**Suspected Nuker:** {nuker}\n"
            f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await client.user.send(alert_msg)
    except Exception as e:
        print(f"{Fore.RED}Could not send DM: {e}{Style.RESET_ALL}")

async def start_anti_nuke_monitor():
    """Start monitoring for nuke attempts"""
    global NUKE_PROTECTION_ENABLED
    target_guild = discord.utils.get(client.guilds, id=SERVER_ID)
    
    if not target_guild:
        print(f"{Fore.RED}Server not found!{Style.RESET_ALL}")
        return
    
    NUKE_PROTECTION_ENABLED = True
    print(f"\n{Fore.GREEN}{Style.BRIGHT}╔════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}║  Anti-Nuke Protection Activated!      ║{Style.RESET_ALL}")
    print(f"{Fore.GREEN}{Style.BRIGHT}╚════════════════════════════════════════╝{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Monitoring: {target_guild.name}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Detection Thresholds:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Bans: {NUKE_THRESHOLDS['bans']} in {NUKE_THRESHOLDS['timeframe']}s{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Kicks: {NUKE_THRESHOLDS['kicks']} in {NUKE_THRESHOLDS['timeframe']}s{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Channel Deletes: {NUKE_THRESHOLDS['channels']} in {NUKE_THRESHOLDS['timeframe']}s{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  • Role Deletes: {NUKE_THRESHOLDS['roles']} in {NUKE_THRESHOLDS['timeframe']}s{Style.RESET_ALL}")
    print(f"\n{Fore.GREEN}Monitoring active... Press Ctrl+C to stop{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}\n")

async def change_nicknames_loop():
    target_guild = discord.utils.get(client.guilds, id=SERVER_ID)
    
    if not target_guild:
        print(f"{Fore.RED}{Style.BRIGHT}ERROR: Server with ID {SERVER_ID} not found!{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Available servers you're in:{Style.RESET_ALL}")
        for g in client.guilds:
            print(f"{Fore.WHITE}   • {g.name} (ID: {g.id}){Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Tip: Make sure you copied the correct Server ID{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}Found server: {target_guild.name}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Total members: {len(target_guild.members)}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}Your highest role: {target_guild.me.top_role.name}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}\n")
    
    batch_count = 0
    total_changed = 0
    
    # Target statuses: Online, Idle (moon/away), Do Not Disturb
    target_statuses = [
        discord.Status.online,
        discord.Status.idle,
        discord.Status.dnd
    ]
    
    while True:
        batch_count += 1
        changes_this_batch = 0
        
        print(f"{Fore.YELLOW}{Style.BRIGHT}Batch #{batch_count} starting (max 10 changes)...{Style.RESET_ALL}")
        
        for member in target_guild.members:
            # Only target: Online, Idle, or DND + not bot + not yourself
            if (member.status in target_statuses and 
                not member.bot and 
                member != client.user):
                
                try:
                    await member.edit(nick="Kieran")
                    changes_this_batch += 1
                    total_changed += 1
                    
                    status_colors = {
                        discord.Status.online: Fore.GREEN,
                        discord.Status.idle: Fore.YELLOW, 
                        discord.Status.dnd: Fore.RED
                    }
                    status_text = {
                        discord.Status.online: "ONLINE",
                        discord.Status.idle: "IDLE", 
                        discord.Status.dnd: "DND"
                    }
                    
                    status_color = status_colors.get(member.status, Fore.WHITE)
                    status_label = status_text.get(member.status, "UNKNOWN")
                    
                    print(f"{status_color}  [{status_label}]{Style.RESET_ALL} {Fore.CYAN}[{changes_this_batch}/10]{Style.RESET_ALL} {Fore.WHITE}{member.name}{Style.RESET_ALL} -> {Fore.GREEN}Kieran{Style.RESET_ALL}")
                    
                except discord.Forbidden:
                    print(f"{Fore.RED}  No permission: {member.name}{Style.RESET_ALL}")
                    
                except discord.HTTPException as e:
                    if e.status == 429:
                        print(f"{Fore.YELLOW}  Rate limited! Waiting 5s...{Style.RESET_ALL}")
                        await asyncio.sleep(5)
                    else:
                        print(f"{Fore.RED}  Error on {member.name}: {e}{Style.RESET_ALL}")
                
                # 1.8 second delay between each change
                await asyncio.sleep(1.8)
                
                # Stop after 10 changes
                if changes_this_batch >= 10:
                    break
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}Batch #{batch_count} Complete:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   • Changed this batch: {changes_this_batch}/10{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}   • Total changed: {total_changed}{Style.RESET_ALL}")
        
        if changes_this_batch > 0:
            print(f"\n{Fore.YELLOW}Cooldown: Waiting 3 seconds before next batch...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}\n")
            await asyncio.sleep(3)
        else:
            print(f"\n{Fore.YELLOW}No eligible members found. Waiting 10 seconds...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}\n")
            await asyncio.sleep(10)

async def run_bot():
    """Async function to run the bot properly"""
    global client
    
    @client.event
    async def on_ready():
        print(f'\n{Fore.GREEN}{Style.BRIGHT}Successfully logged in!{Style.RESET_ALL}')
        print(f'{Fore.CYAN}Account: {client.user.name}{Style.RESET_ALL}')
        print(f'{Fore.CYAN}User ID: {client.user.id}{Style.RESET_ALL}')
        print(f'{Fore.YELLOW}Target Server ID: {SERVER_ID}{Style.RESET_ALL}')
        print(f'\n{Fore.MAGENTA}Target Statuses: {Fore.GREEN}Online{Style.RESET_ALL} | {Fore.YELLOW}Idle{Style.RESET_ALL} | {Fore.RED}DND{Style.RESET_ALL}')
        print(f'{Fore.CYAN}Rate: 10 changes/batch, 1.8s delay, 3s cooldown{Style.RESET_ALL}')
        print(f'{Fore.RED}Press Ctrl+C to stop{Style.RESET_ALL}\n')
        asyncio.create_task(change_nicknames_loop())
    
    @client.event
    async def on_member_ban(guild, user):
        """Detect when members are banned"""
        if not NUKE_PROTECTION_ENABLED or guild.id != SERVER_ID:
            return
        
        # Try to get audit log entry
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    is_nuke, count, nuker = await check_nuke_activity(guild.id, 'ban', entry)
                    if is_nuke:
                        await nuke_alert(guild, 'ban', count, nuker)
                    else:
                        print(f"{Fore.YELLOW}[BAN] {user.name} banned by {nuker} ({count}/{NUKE_THRESHOLDS['bans']}){Style.RESET_ALL}")
                    break
        except:
            is_nuke, count, nuker = await check_nuke_activity(guild.id, 'ban', None)
            if is_nuke:
                await nuke_alert(guild, 'ban', count, nuker)
    
    @client.event
    async def on_member_remove(member):
        """Detect when members are kicked"""
        if not NUKE_PROTECTION_ENABLED or member.guild.id != SERVER_ID:
            return
        
        # Check if it was a kick (not a ban or leave)
        try:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
                if entry.target.id == member.id:
                    is_nuke, count, nuker = await check_nuke_activity(member.guild.id, 'kick', entry)
                    if is_nuke:
                        await nuke_alert(member.guild, 'kick', count, nuker)
                    else:
                        print(f"{Fore.YELLOW}[KICK] {member.name} kicked by {nuker} ({count}/{NUKE_THRESHOLDS['kicks']}){Style.RESET_ALL}")
                    break
        except:
            pass
    
    @client.event
    async def on_guild_channel_delete(channel):
        """Detect when channels are deleted"""
        if not NUKE_PROTECTION_ENABLED or channel.guild.id != SERVER_ID:
            return
        
        try:
            async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
                if entry.target.id == channel.id:
                    is_nuke, count, nuker = await check_nuke_activity(channel.guild.id, 'channel', entry)
                    if is_nuke:
                        await nuke_alert(channel.guild, 'channel', count, nuker)
                    else:
                        print(f"{Fore.YELLOW}[CHANNEL DELETE] #{channel.name} deleted by {nuker} ({count}/{NUKE_THRESHOLDS['channels']}){Style.RESET_ALL}")
                    break
        except:
            is_nuke, count, nuker = await check_nuke_activity(channel.guild.id, 'channel', None)
            if is_nuke:
                await nuke_alert(channel.guild, 'channel', count, nuker)
    
    @client.event
    async def on_guild_role_delete(role):
        """Detect when roles are deleted"""
        if not NUKE_PROTECTION_ENABLED or role.guild.id != SERVER_ID:
            return
        
        try:
            async for entry in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
                if entry.target.id == role.id:
                    is_nuke, count, nuker = await check_nuke_activity(role.guild.id, 'role', entry)
                    if is_nuke:
                        await nuke_alert(role.guild, 'role', count, nuker)
                    else:
                        print(f"{Fore.YELLOW}[ROLE DELETE] @{role.name} deleted by {nuker} ({count}/{NUKE_THRESHOLDS['roles']}){Style.RESET_ALL}")
                    break
        except:
            is_nuke, count, nuker = await check_nuke_activity(role.guild.id, 'role', None)
            if is_nuke:
                await nuke_alert(role.guild, 'role', count, nuker)
    
    @client.event
    async def on_error(event, *args, **kwargs):
        print(f"{Fore.RED}Error in {event}{Style.RESET_ALL}")
    
    try:
        # For self-bots with discord.py-self
        await client.start(TOKEN, bot=False)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Stopping bot...{Style.RESET_ALL}")
        await client.close()
    except TypeError:
        # Fallback for regular discord.py (won't work but gives better error)
        try:
            await client.start(TOKEN)
        except Exception:
            pass

def main():
    global TOKEN, SERVER_ID, client
    
    try:
        print_banner()
        
        # Get token first
        TOKEN = get_token()
        
        # Show menu
        while True:
            choice = show_menu()
            
            if choice == '1':  # Nickname Changer
                SERVER_ID = get_server_id()
                
                if confirm_nickname_change():
                    # Create Discord client
                    client = discord.Client()
                    
                    print(f"\n{Fore.CYAN}Connecting to Discord...{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}\n")
                    
                    try:
                        asyncio.run(run_bot())
                    except KeyboardInterrupt:
                        print(f"\n{Fore.YELLOW}Returning to main menu...{Style.RESET_ALL}")
                        client = None
                        continue
                    except discord.LoginFailure:
                        print(f"\n{Fore.RED}{Style.BRIGHT}LOGIN FAILED!{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}   • Check your token is correct{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}   • Token might be expired{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}   • Make sure you copied the full token{Style.RESET_ALL}")
                        input(f"\n{Fore.CYAN}Press Enter to return to menu...{Style.RESET_ALL}")
                        continue
                        
            elif choice == '2':  # Anti-Nuke Protection
                SERVER_ID = get_server_id()
                
                # Create Discord client
                client = discord.Client()
                
                print(f"\n{Fore.CYAN}Connecting to Discord...{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'━' * 60}{Style.RESET_ALL}\n")
                
                try:
                    asyncio.run(run_bot())
                    # After connection, start monitoring
                    await start_anti_nuke_monitor()
                except KeyboardInterrupt:
                    print(f"\n{Fore.YELLOW}Stopping anti-nuke monitor...{Style.RESET_ALL}")
                    NUKE_PROTECTION_ENABLED = False
                    client = None
                    continue
                except discord.LoginFailure:
                    print(f"\n{Fore.RED}{Style.BRIGHT}LOGIN FAILED!{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}   • Check your token is correct{Style.RESET_ALL}")
                    input(f"\n{Fore.CYAN}Press Enter to return to menu...{Style.RESET_ALL}")
                    continue
                    
            elif choice == '3':  # View Statistics
                show_nuke_statistics()
                
            elif choice == '4':  # Exit
                print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                break
                
    except ModuleNotFoundError as e:
        if 'discord' in str(e):
            print(f"\n{Fore.RED}{Style.BRIGHT}discord.py-self not installed!{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Self-bots require discord.py-self (not regular discord.py){Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Install with:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}   pip uninstall discord.py{Style.RESET_ALL}")
            print(f"{Fore.WHITE}   pip install discord.py-self aiohttp colorama{Style.RESET_ALL}")
        elif 'colorama' in str(e):
            print(f"\n{Fore.YELLOW}colorama not installed (colors disabled){Style.RESET_ALL}")
            print(f"\n{Fore.CYAN}Install with:{Style.RESET_ALL}")
            print(f"   pip install colorama")
        else:
            print(f"\n{Fore.RED}Missing module: {e}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"\n{Fore.RED}Unexpected error: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Error type: {type(e).__name__}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
