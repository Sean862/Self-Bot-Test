"""
Discord Self-bot - Kiera V0.1
Python 3.13 Compatible (CGI Fix Included)
Works on Pydroid3

Installation:
pip install discord.py aiohttp

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

def print_banner():
    banner = """
╔══════════════════════════════════════════════════╗
║                  Kiera V0.1                      ║
║           Discord Self-Bot Toolkit               ║
╚══════════════════════════════════════════════════╝
"""
    print(banner)
    print("WARNING: Self-bots violate Discord ToS!")
    print("Using this can result in PERMANENT ACCOUNT BAN")
    print("Use at your own risk - Educational purposes only\n")

def get_token():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Enter your Discord token:")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    while True:
        token = input("Token: ").strip()
        if len(token) > 50:
            return token
        else:
            print("Invalid token (too short). Try again.\n")

def show_menu():
    print("\n" + "━" * 50)
    print("[ 1 ] - Nickname Changer")
    print("[ 2 ] - Exit")
    print("━" * 50)
    
    while True:
        choice = input("Select option: ").strip()
        if choice in ['1', '2']:
            return choice
        else:
            print("Invalid choice. Enter 1 or 2\n")

def get_server_id():
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Enter Server ID")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    while True:
        server_id_str = input("Server ID: ").strip()
        try:
            server_id = int(server_id_str)
            if len(str(server_id)) >= 17:
                return server_id
            else:
                print("Invalid Server ID (too short). Try again.\n")
        except ValueError:
            print("Invalid Server ID (must be numbers only). Try again.\n")

def confirm_nickname_change():
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("NICKNAME CHANGER CONFIGURATION")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("This will:")
    print("• Change nicknames for Online/Idle/DND members")
    print("• Process 10 members at a time (1.8s delay each)")
    print("• 3 second cooldown after every 10 changes")
    print("• Run continuously until you stop it")
    print("\nDo you want to continue?")
    
    response = input("Type 'yes' to continue, anything else to cancel: ").strip().lower()
    return response == 'yes'

# Global variables
TOKEN = None
SERVER_ID = None
client = None

async def change_nicknames_loop():
    target_guild = discord.utils.get(client.guilds, id=SERVER_ID)
    
    if not target_guild:
        print(f"ERROR: Server with ID {SERVER_ID} not found!")
        print(f"\nAvailable servers you're in:")
        for g in client.guilds:
            print(f"   • {g.name} (ID: {g.id})")
        print(f"\nTip: Make sure you copied the correct Server ID")
        return
    
    print(f"Found server: {target_guild.name}")
    print(f"Total members: {len(target_guild.members)}")
    print(f"Your highest role: {target_guild.me.top_role.name}")
    print(f"\n" + "━" * 60 + "\n")
    
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
        
        print(f"Batch #{batch_count} starting (max 10 changes)...")
        
        for member in target_guild.members:
            # Only target: Online, Idle, or DND + not bot + not yourself
            if (member.status in target_statuses and 
                not member.bot and 
                member != client.user):
                
                try:
                    await member.edit(nick="Kieran")
                    changes_this_batch += 1
                    total_changed += 1
                    
                    status_text = {
                        discord.Status.online: "[ONLINE]",
                        discord.Status.idle: "[IDLE]", 
                        discord.Status.dnd: "[DND]"
                    }
                    status_label = status_text.get(member.status, "[UNKNOWN]")
                    
                    print(f"  {status_label} [{changes_this_batch}/10] {member.name} -> Kieran")
                    
                except discord.Forbidden:
                    print(f"  No permission: {member.name}")
                    
                except discord.HTTPException as e:
                    if e.status == 429:
                        print(f"  Rate limited! Waiting 5s...")
                        await asyncio.sleep(5)
                    else:
                        print(f"  Error on {member.name}: {e}")
                
                # 1.8 second delay between each change
                await asyncio.sleep(1.8)
                
                # Stop after 10 changes
                if changes_this_batch >= 10:
                    break
        
        print(f"\nBatch #{batch_count} Complete:")
        print(f"   • Changed this batch: {changes_this_batch}/10")
        print(f"   • Total changed: {total_changed}")
        
        if changes_this_batch > 0:
            print(f"\nCooldown: Waiting 3 seconds before next batch...")
            print("━" * 60 + "\n")
            await asyncio.sleep(3)
        else:
            print(f"\nNo eligible members found. Waiting 10 seconds...")
            print("━" * 60 + "\n")
            await asyncio.sleep(10)

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
                    
                    @client.event
                    async def on_ready():
                        print(f'\nSuccessfully logged in!')
                        print(f'Account: {client.user.name}')
                        print(f'User ID: {client.user.id}')
                        print(f'Target Server ID: {SERVER_ID}')
                        print(f'\nTarget Statuses: Online | Idle | DND')
                        print(f'Rate: 10 changes/batch, 1.8s delay, 3s cooldown')
                        print(f'Press Ctrl+C to stop\n')
                        asyncio.create_task(change_nicknames_loop())
                    
                    @client.event
                    async def on_error(event, *args, **kwargs):
                        print(f"Error in {event}")
                    
                    print("\nConnecting to Discord...")
                    print("━" * 60 + "\n")
                    
                    # Run the bot
                    try:
                        client.run(TOKEN, bot=False)
                    except KeyboardInterrupt:
                        print("\nReturning to main menu...")
                        continue
                        
            elif choice == '2':  # Exit
                print("\nGoodbye!")
                break
                
    except discord.LoginFailure:
        print("\nLOGIN FAILED!")
        print("   • Check your token is correct")
        print("   • Token might be expired")
        print("   • Make sure you copied the full token")
        
    except ModuleNotFoundError as e:
        if 'discord' in str(e):
            print("\ndiscord.py not installed!")
            print("\nInstall with:")
            print("   pip install discord.py aiohttp")
        else:
            print(f"\nMissing module: {e}")
            
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    main()
