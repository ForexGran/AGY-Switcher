import rumps
import json
import os
import subprocess
import sys
import base64
from datetime import datetime, timezone
import fcntl

# Singleton Lock
lock_file = open('/tmp/agy_widget.lock', 'w')
try:
    fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
except IOError:
    sys.exit(0)

sys.stdout = open(os.path.expanduser("~/.gemini/auth_backups/widget_debug.log"), "a")
sys.stderr = sys.stdout

class AntigravityWidget(rumps.App):
    def __init__(self):
        super(AntigravityWidget, self).__init__(" AGY", icon="/Applications/AGY Switcher.app/Contents/Resources/menubar.png", template=False)
        self.usage_file = os.path.expanduser('~/.gemini/auth_backups/usage.json')
        self.backup_dir = os.path.expanduser('~/.gemini/auth_backups')
        self.res_dir = "/Applications/AGY Switcher.app/Contents/Resources"
        self.accounts = []
        self.fingerprints = {}
        
        # Ensure backup dir exists
        os.makedirs(self.backup_dir, exist_ok=True)
        self.load_accounts()
        self.last_state_hash = ''
                
    def load_accounts(self):
        self.accounts = []
        self.fingerprints = {}
        try:
            for file in os.listdir(self.backup_dir):
                if file.startswith('token_'):
                    acc = file.replace('token_', '')
                    self.accounts.append(acc)
                    with open(os.path.join(self.backup_dir, file), 'r') as f:
                        self.fingerprints[acc] = self.get_rt_from_string(f.read())
        except Exception as e:
            print(f"Error loading accounts: {e}")
            
    def get_rt_from_string(self, token_str):
        out = token_str.strip()
        if out.startswith('go-keyring-base64:'): out = out.replace('go-keyring-base64:', '')
        pad = len(out) % 4
        if pad: out += '=' * (4 - pad)
        try:
            return json.loads(base64.b64decode(out).decode('utf-8')).get('token', {}).get('refresh_token')
        except: return None
        
    def get_live_account(self):
        try:
            keychain_str = subprocess.check_output(['security', 'find-generic-password', '-s', 'gemini', '-a', 'antigravity', '-w'], text=True)
            live_rt = self.get_rt_from_string(keychain_str)
            for acc, rt in self.fingerprints.items():
                if rt and rt == live_rt:
                    return acc
        except: pass
        return None

    def get_usage(self):
        try:
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        except:
            return {}
            
    def set_usage(self, acc):
        usage = self.get_usage()
        usage[acc] = datetime.now(timezone.utc).isoformat()
        with open(self.usage_file, 'w') as f:
            json.dump(usage, f)


    @rumps.timer(5)
    def update_ui(self, _):
        usage = self.get_usage()
        live_acc = self.get_live_account()
        
        if live_acc:
            self.set_usage(live_acc)
            usage = self.get_usage()
            self.title = f" {live_acc}"
        else:
            self.title = " AGY"
            
        # Create a state string to check if we actually need to rebuild the menu
        state_str = str(live_acc) + str(self.accounts) + str(usage)
        if state_str == getattr(self, 'last_state_hash', ''):
            return # Skip expensive UI rebuild if nothing changed!
        self.last_state_hash = state_str
            
        new_menu = []
        
        if len(self.accounts) > 1:
            new_menu.append(rumps.MenuItem("Smart Auto-Switch", icon=os.path.join(self.res_dir, "auto.png"), callback=self.auto_switch_callback))
            new_menu.append(rumps.separator)
        
        standby_items = []
        all_on_cooldown = True
        
        for acc in sorted(self.accounts):
            last_used = usage.get(acc)
            is_on_cooldown = False
            
            if acc == live_acc:
                item = rumps.MenuItem(f"{acc} (Online Now)", icon=os.path.join(self.res_dir, "active.png"))
                new_menu.append(item)
                new_menu.append(rumps.separator)
                is_on_cooldown = True 
            else:
                if not last_used:
                    status = "Available"
                    ico = os.path.join(self.res_dir, "idle.png")
                    all_on_cooldown = False
                else:
                    try:
                        dt = datetime.fromisoformat(last_used)
                        diff = datetime.now(timezone.utc) - dt
                        s = diff.total_seconds()
                        if s > 18000:
                            status = "Ready ✅"
                            ico = os.path.join(self.res_dir, "ready.png")
                            all_on_cooldown = False
                        else:
                            is_on_cooldown = True
                            if s < 60: status = "Just now"
                            elif s < 3600: status = f"{int(s//60)}m ago"
                            elif s < 86400: status = f"{int(s//3600)}h ago"
                            else: status = f"{int(s//86400)}d ago"
                            ico = os.path.join(self.res_dir, "recent.png")
                    except:
                        status = "Unknown"
                        ico = os.path.join(self.res_dir, "recent.png")
                        all_on_cooldown = False
                        
                item = rumps.MenuItem(f"{acc} ({status})", icon=ico, callback=self.make_switch_callback(acc))
                standby_items.append(item)
                
            if not is_on_cooldown:
                all_on_cooldown = False
                
        if len(self.accounts) > 0 and all_on_cooldown:
            self.icon = os.path.join(self.res_dir, "menubar_red.png")
        else:
            self.icon = os.path.join(self.res_dir, "menubar.png")
                
        new_menu.extend(standby_items)
        if len(self.accounts) == 0:
            new_menu.append(rumps.MenuItem("No accounts found. Log in first!"))
            
        new_menu.append(rumps.separator)
        new_menu.append(rumps.MenuItem("➕ Add Current Account", callback=self.add_account_callback))
        new_menu.append(rumps.separator)
        new_menu.append(rumps.MenuItem("Quit AGY Switcher", callback=rumps.quit_application))
        
        self.menu.clear()
        self.menu.update(new_menu)

    def auto_switch_callback(self, _):
        usage = self.get_usage()
        live_acc = self.get_live_account()
        
        def get_ts(a):
            iso = usage.get(a)
            if not iso: return 0
            try: return datetime.fromisoformat(iso).timestamp()
            except: return 0
            
        cands = [a for a in self.accounts if a != live_acc]
        if not cands: cands = self.accounts
            
        if cands:
            target_acc = min(cands, key=get_ts)
            self.make_switch_callback(target_acc)(None)

    def make_switch_callback(self, acc):
        def callback(_):
            try:
                subprocess.Popen(['afplay', '/System/Library/Sounds/Tink.aiff'])
                subprocess.Popen(['osascript', '-e', f'display notification "Warping to {acc}..." with title "AGY Switcher"'])
                self.set_usage(acc)
                token_path = os.path.join(self.backup_dir, f"token_{acc}")
                with open(token_path, 'r') as f:
                    token = f.read().strip()
                subprocess.run(['security', 'add-generic-password', '-a', 'antigravity', '-s', 'gemini', '-w', token, '-U'])
                subprocess.run(['killall', '-9', 'Antigravity'])
                cookie_path = os.path.expanduser('~/Library/Application Support/Antigravity/Cookies')
                cookie_journal_path = os.path.expanduser('~/Library/Application Support/Antigravity/Cookies-journal')
                subprocess.run(['rm', '-f', cookie_path, cookie_journal_path])
                import time
                time.sleep(1.5)
                subprocess.run(['open', '-a', '/Applications/Antigravity.app'])
            except Exception as e:
                print(f"CRITICAL ERROR: {e}", flush=True)
        return callback
        

    def add_account_callback(self, _):
        try:
            try:
                keychain_str = subprocess.check_output(['security', 'find-generic-password', '-s', 'gemini', '-a', 'antigravity', '-w'], text=True)
            except subprocess.CalledProcessError:
                subprocess.Popen(['osascript', '-e', 'display alert "No Token Found" message "Could not extract token from Keychain. Are you logged in to Antigravity?"'])
                return
                
            if not keychain_str.strip():
                return
                
            script = '''
            tell application "System Events"
                activate
                set theResponse to display dialog "A live session was detected!
What would you like to name this account? (e.g., Work, Personal)" default answer "" with title "AGY Switcher" buttons {"Cancel", "Save"} default button "Save"
                return text returned of theResponse
            end tell
            '''
            try:
                name = subprocess.check_output(['osascript', '-e', script], text=True).strip()
            except subprocess.CalledProcessError:
                return # User clicked Cancel
                
            if not name:
                return
                
            token_path = os.path.join(self.backup_dir, f"token_{name}")
            
            if os.path.exists(token_path):
                script_confirm = f'''
                tell application "System Events"
                    activate
                    display dialog "An account named '{name}' already exists. Overwrite it?" buttons {{"Cancel", "Overwrite"}} default button "Cancel" with icon caution
                end tell
                '''
                try:
                    subprocess.check_output(['osascript', '-e', script_confirm])
                except subprocess.CalledProcessError:
                    return # User clicked Cancel on overwrite
            
            with open(token_path, "w") as f:
                f.write(keychain_str.strip())
                
            self.load_accounts()
            self.last_state_hash = '' # Force UI rebuild
            subprocess.Popen(['afplay', '/System/Library/Sounds/Glass.aiff'])
            subprocess.Popen(['osascript', '-e', f'display notification "Account {name} saved successfully!" with title "AGY Switcher"'])
            
        except Exception as e:
            subprocess.Popen(['osascript', '-e', f'display alert "Error" message "{str(e)}"'])

if __name__ == "__main__":
    AntigravityWidget().run()
