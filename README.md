<div align="center">
  <img src="assets/logo.png" width="128" height="128" alt="AGY Switcher Logo">
  <h1>♽ AGY Switcher</h1>
  <p><b>A native, lightweight macOS Menu Bar utility for Power Users to seamlessly hot-swap between multiple Antigravity AI accounts.</b></p>
  
  <p>
    <a href="https://github.com/yourusername/AGY-Switcher/releases"><img src="https://img.shields.io/badge/Platform-macOS-black?style=for-the-badge&logo=apple" alt="macOS"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python" alt="Python"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License"></a>
  </p>
</div>

<br>

**AGY Switcher** securely circumvents Electron token caching by forcefully isolating cookies and injecting OAuth Refresh Tokens directly into the macOS Keychain. This allows you to instantly swap active accounts and precisely track your 5-hour quota cooldowns from your Menu Bar.

---

## ✨ Features
* **🧠 Smart Auto-Switch**: Automatically calculates quota decay and swaps to the account that has been resting the longest.
* **⏳ 5-Hour Quota Timers**: Tracks to-the-minute usage and visually labels accounts that are `Ready ✅`.
* **🚨 Global Red Alert**: The menu bar icon dynamically turns **Red** to warn you when all 5 accounts are exhausted.
* **📱 Mobile Remote Control**: Trigger an account swap directly from your iPhone/iPad by giving a chat command to the Antigravity agent!
* **⚡ Singleton Engine**: A self-healing background process guarantees 0% CPU usage when idle and prevents duplicate apps.
* **➕ Add Accounts UI**: Instantly backup and save new active accounts with a single native popup click—no terminal required.

---

## 🚀 One-Click Installation

AGY Switcher builds itself dynamically on your machine to ensure complete security.

1. Clone or download this repository.
2. Open your terminal, navigate to the folder, and run:
   ```bash
   ./install.sh
   ```
3. That's it! The script will automatically build a native `.app` bundle, inject the high-res squircle icon, add it to your Mac's Login Items, and launch it into your Menu Bar!

---

## ⚙️ How To Add Accounts

1. Open the normal **Antigravity** app and log into any Google or Claude account.
2. Click the `AGY` icon in your Mac Menu Bar.
3. Click **"➕ Add Current Account"** at the bottom.
4. Type a name (e.g. *"Work"*, *"Personal"*) and hit Enter!
5. The widget will instantly extract the live OAuth token from your Keychain, save it locally, and add it to the dropdown menu!

---

## 🔐 Required macOS Permissions
Because AGY Switcher deeply integrates with the OS to hot-swap background processes, macOS will ask you for a few standard permissions during your first run:

1. **Keychain Access (Crucial)**: 
   When you trigger your first account switch, macOS will prompt you saying *"Python wants to access your keychain"*. **You must click "Always Allow"**. If you just click "Allow", macOS will annoyingly prompt you every single time you try to swap accounts!
2. **System Events / Automation**: 
   When you click "➕ Add Current Account", macOS might ask to allow the app to control System Events. This is strictly required to display the native Apple popup dialog on your screen.
3. **Notifications**: 
   Required to display the *"Warping to..."* alert in the top right corner of your screen when an account swaps.
4. **Accessibility (For Keyboard Shortcuts)**: 
   If you decide to bind the Python script to a global macOS keyboard shortcut, your Mac will require you to grant Accessibility permissions to whatever app you are currently typing in.

---

## 🗑️ Uninstallation
If you ever want to remove AGY Switcher, simply run:
```bash
./uninstall.sh
```
This will cleanly kill the background engine, remove the app from your Login Items, and securely shred the hidden `~/.gemini/auth_backups/` folder containing your tokens.

---

## 🔒 Security & Privacy
AGY Switcher is built for absolute privacy. All OAuth tokens are strictly stored locally on your machine in a hidden `~/.gemini/auth_backups/` directory. No data is ever transmitted, and the script operates 100% offline.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
