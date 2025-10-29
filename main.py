def get_nickname_command():
    """Extracted nickname changer command only - ALL STATUSES INCLUDING OFFLINE"""
    
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
    
    # Get token and server ID
    print("Enter your Discord token:")
    token = input("Token: ").strip()
    
    print("\nEnter Server ID:")
    server_id = int(input("Server ID: ").strip())
    
    # ALL statuses including offline
    target_statuses = [
        discord.Status.online,
        discord.Status.idle, 
        discord.Status.dnd,
        discord.Status.offline  # ADDED OFFLINE
    ]
    
    client = discord.Client()
    
    @client.event
    async def on_ready():
        print(f'Logged in as {client.user.name}')
        target_guild = discord.utils.get(client.guilds, id=server_id)
        
        if not target_guild:
            print(f"Server with ID {server_id} not found!")
            await client.close()
            return
            
        print(f"Found server: {target_guild.name}")
        print("Starting nickname changes for ALL members (including offline)...\n")
        
        batch_count = 0
        total_changed = 0
        
        while True:
            batch_count += 1
            changes_this_batch = 0
            
            print(f"Batch #{batch_count} starting...")
            
            for member in target_guild.members:
                if (member.status in target_statuses and  # This now includes offline
                    not member.bot and 
                    member != client.user):
                    
                    try:
                        await member.edit(nick="ht | discord.gg/NGjgMVqp6w - Kieran Runs You")
                        changes_this_batch += 1
                        total_changed += 1
                        
                        status_text = {
                            discord.Status.online: "ONLINE",
                            discord.Status.idle: "IDLE", 
                            discord.Status.dnd: "DND",
                            discord.Status.offline: "OFFLINE"  # ADDED OFFLINE
                        }
                        
                        status_label = status_text.get(member.status, "UNKNOWN")
                        print(f"[{status_label}] Changed {member.name} -> ht | discord.gg/NGjgMVqp6w - Kieran Runs You")
                        
                    except discord.Forbidden:
                        print(f"No permission: {member.name}")
                    except discord.HTTPException as e:
                        if e.status == 429:
                            print("Rate limited! Waiting 5s...")
                            await asyncio.sleep(5)
                        else:
                            print(f"Error on {member.name}: {e}")
                    
                    await asyncio.sleep(1.8)
                    
                    if changes_this_batch >= 10:
                        break
            
            print(f"Batch #{batch_count} complete: {changes_this_batch} changes")
            print(f"Total changed: {total_changed}")
            
            if changes_this_batch > 0:
                print("Waiting 3 seconds...\n")
                await asyncio.sleep(3)
            else:
                print("No more members to change. Waiting 10 seconds...\n")
                await asyncio.sleep(10)
    
    try:
        client.run(token, bot=False)
    except KeyboardInterrupt:
        print("\nStopping...")
    except discord.LoginFailure:
        print("Invalid token!")

# Run the nickname command
if __name__ == "__main__":
    get_nickname_command()
