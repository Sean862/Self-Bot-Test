"""
Discord Self-bot - Kieran V0.2
Python 3.13 Compatible (CGI Fix Included)
Works on Pydroid3

Installation:
pip install discord.py aiohttp colorama

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
    print("║         KIERAN SELF-BOT V0.2          ║")
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
    print("║         KIERAN SELF-BOT V0.2          ║")
    print("╚═══════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[ 1 ]{Style.RESET_ALL} - Nickname Changer")
    print(f"{Fore.RED}[ 2 ]{Style.RESET_ALL} - Exit")
    print(f"{Fore.CYAN}{'━' * 50}{Style.RESET_ALL}")
    
    while True:
        choice = input(f"{Fore.YELLOW}Select option: {Style.RESET_ALL}").strip()
        if choice in ['1', '2']:
            return choice
        else:
            print(f"{Fore.RED}Invalid choice. Enter 1 or 2{Style.RESET_ALL}\n")

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
                    
                    print(f"{status_color}  [{status_label}]{Style.RESET_ALL} {Fore.CYAN}[{changes_this_batch}/10]{Style.RESET_ALL} {Fore.WHITE}{member.name}{Style.RESET_ALL} → {Fore.GREEN}Kieran{Style.RESET_ALL}")
                    
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
    async def on_error(event, *args, **kwargs):
        print(f"{Fore.RED}Error in {event}{Style.RESET_ALL}")
    
    try:
        await client.start(TOKEN)
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Stopping bot...{Style.RESET_ALL}")
        await client.close()

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
                        
            elif choice == '2':  # Exit
                print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
                break
                
    except ModuleNotFoundError as e:
        if 'discord' in str(e):
            print(f"\n{Fore.RED}discord.py not installed!{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Install with:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   pip install discord.py aiohttp colorama{Style.RESET_ALL}")
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
