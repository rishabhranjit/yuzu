import lime
from lime.util import *
import lime.widgets as widgets

from pathlib import Path
import os, json, threading
import time

#- Checklist Data -#

checklist = [
    ["Enable firewall", "sudo ufw enable"],
    ["Allow all services via UFW", "sudo ufw allow [port] (SSH is 22)"],
    ["Update package list", "sudo apt-get update"],
    ["Update packages", "sudo apt-get upgrade"],
    ["Distribution upgrade", "sudo apt-get dist-upgrade"],
    ["Remove unauthorized software", "sudo apt-get purge <package>"],
    ["Enable auto-updates", "Through the Software & Updates GUI (click the check buttons)"],
    ["Lock root account", "sudo passwd -l root"],
    ["Ensure all passwords are secured", "passwd [user]"],
    ["Check for users with UID 0", "nano /etc/passwd"],
    ["Remove unauthorized users", "Edit /etc/passwd using nano"],
    ["Remove unauthorized sudo privileges", "Edit /etc/group using nano"],
    ["Secure browser", "Go into browser settings and enable all security options"],
    ["Copy SSH config file", "Copy your SSH config file into /etc/ssh/sshd_config using nano"],
    ["Secure critical Linux file permissions", "sudo chmod -R 440 /etc/sudoers && sudo chmod -R 644 /etc/group && sudo chmod -R 644 /etc/passwd && sudo chmod -R 640 /etc/shadow"],
    ["Ensure users own their home directories", "ls -l"],
    ["Check crontabs", "/etc/crontab or /var/spool/cron/crontabs"],
    ["Check user bashrc & bashalias", "nano /home/[user]/.bashrc and .bash_aliases"],
    ["Check for malicious files in skel", "nano /etc/skel"],
    ["Check for malicious activity in init", "nano /etc/init.d/"],
    ["Check SUID binaries", "Refer to https://gtfobins.github.io/"],
    ["Check apt configuration", "nano /etc/apt"],
    ["Check LD_PRELOAD", "nano /etc/ld*"],
    ["Set minimum password age", "nano /etc/login.defs"],
    ["Set maximum password age", "nano /etc/login.defs"],
    ["Remove 'nullok' from PAM", "nano /etc/pam.d"],
    ["Set minimum password length", "nano /etc/pam.d/common-password (e.g., minlen=12)"],
    ["Remember previously used passwords", "nano /etc/pam.d/common-password (e.g., remember=5)"],
    ["Secure sysctl settings", "nano /etc/sysctl.conf"],
    ["Check for unnecessary services", "service --status-all"],
    ["Check for prohibited files", 'sudo find / -type f -name "*.mp3" -o -name "*.jpg" -o -name "*.mp4"'],
    ["Check for netcat backdoor", "sudo ss -ln (inspect ports connected to loopback)"],
    ["Disable guest login", "nano /etc/lightdm/lightdm.conf.d/ or /etc/gdm3/daemon.conf"],
    ["Check sources list & apt keys", "apt-cache policy and apt-key list"],
    ["Check sudoers", "nano /etc/sudoers or /etc/sudoers.d/ (ensure nothing is NOPASSWD)"],
    ["Check for suspicious entries", "nano /etc/hosts"],
    ["Prevent IP spoofing", 'echo "nospoof on" >> /etc/host.conf'],
    ["Uninstall netcat", "apt-get purge netcat*"],
    ["Uninstall Samba", "apt-get purge samba* and apt-get purge smb*"],
    ["Check /etc permissions manually", "ls -l /etc"]
]

#- Checklist read/write -#

checklist_path = Path.home() / ".checklist.json"




checklist_data = {
    "checked": [],
    "checklist": checklist
}

def checklist_sync():
    with open(checklist_path, "w") as f:
        json.dump(checklist_data, f)

checklist_window: lime.Window = None
def reload_preview():
    global checklist_window
    if not checklist_window: return
    checklist_window.widgets = []
    checklist_window.old_hash = []
    checklist_window._real_height = 0
    checklist_window._current_height = 0
    rerender_checklist()

if os.path.exists(checklist_path):
    def update_checklist():
        global checklist_data, checklist
        try: 
            with open(checklist_path, 'r') as f:
                checklist_data = json.loads(f.read())
                checklist = checklist_data["checklist"]
            reload_preview()
        except Exception as e:
            print("Failed")

    def watch_changes():
        last_time = os.path.getmtime(str(checklist_path))
        while True:
            current_time = os.path.getmtime(str(checklist_path))
            if last_time != current_time:
                time.sleep(0.5)
                update_checklist()
                last_time = current_time

    thread = threading.Thread(target=watch_changes)
    thread.start()
    update_checklist()

else:
    checklist_sync()

#- Window Registration -#

CHECKLIST_HEIGHT = 100

@lime.register("checklist", True)
def register_checklist():
    return lime.create(
        "Checklist",
        250,
        CHECKLIST_HEIGHT + 55,
        pos=("left", "top")
    )

@lime.register("checklist_popup")
def register_checklist_popup():
    return lime.create(
        "",
        350,
        300,
        pos=("center", "center")
    )

@lime.register("checklist_hint")
def register_checklist_hint():
    return lime.create(
        "",
        350,
        200,
        pos=("center", "center")
    )

#- Transparent Button -#

class TransparentButton(widgets.Button):
    def render(self, draw):
        self._text.color = self.fg_color - (10 if self.disabled else 0)
        self._text.calculate()

        self._text.render(draw)

    def calculate(self):
        super().calculate()
        self.size.y = self._text.size.h

#- Window Rendering -#

checklist_index = -1

@lime.init("checklist_hint")
def render_checklist(win: lime.Window):
    win.add_next(widgets.Text(checklist[checklist_index][0], 0, 14, auto_width=True, bold=True))
    win.add_next(widgets.Paragraph(checklist[checklist_index][-1], 250, 14))

def get_hint_callback(index: int):
    def cb(_):
        global checklist_hint
        checklist_index = index
        lime.open_window("checklist_hint", "checklist")

    return cb

def rerender_checklist(win: lime.Window = None):
    global checklist_window
    if checklist_window == None: checklist_window = win
    win = win or checklist_window
    

    def get_handler(index: int):
        def on_check(enabled):
            checklist_data["checked"].append(checklist[index])
            checklist_sync()
            reload_preview()

        return on_check

    index = 0
    while win._real_height < CHECKLIST_HEIGHT:
        if index > len(checklist) - 1:
            break

        if checklist[index] in checklist_data["checked"]:
            index += 1
            continue

        text = checklist[index]
        hint = None

        if isinstance(text, list):
            hint = text[1]
            text = text[0]

        if len(text) > 20:
            text = text[:17] + "..."

        checkbox = widgets.Checkbox(text)
        checkbox.on_change(get_handler(index))

        hint_button = TransparentButton("?", 10)
        hint_button._text.bold = True
        hint_button.on_click(get_hint_callback(index))

        hint_y = win._real_height + 5
        win.add_next(checkbox)
        if hint: win.add(235 - hint_button.size.w, hint_y, hint_button)
        
        index += 1

    view_button = widgets.Button("View all", 235)

    def open_popup(_):
        lime.open_window("checklist_popup", "checklist")
    view_button.on_click(open_popup)

    win.add(0, CHECKLIST_HEIGHT, view_button)

    total = widgets.Text(" / " + str(len(checklist)), 90, 15, Color(240 - (220 // len(checklist) * len(checklist_data["checked"])), 20 + (220 // len(checklist) * len(checklist_data["checked"])), 20), centered=False)
    checked = widgets.Text(str(len(checklist_data["checked"])), 8, 15, color=Color(20, 240, 20), auto_width=True)
    win.add(0, CHECKLIST_HEIGHT + 35, checked)
    win.add(checked.size.w + 2, CHECKLIST_HEIGHT + 35, total)

@lime.init("checklist_popup")
def render_checklist_popup(win: lime.Window):
    def get_handler(index: int):
        def on_check(enabled):
            if enabled: checklist_data["checked"].append(checklist[index])
            else: checklist_data["checked"].remove(checklist[index])
            checklist_sync()
            reload_preview()

        return on_check

    for index in range(len(checklist)):
        text = checklist[index]
        hint = None

        if isinstance(text, list):
            hint = text[1]
            text = text[0]

        if len(text) > 35:
            text = text[:32] + "..."

        checkbox = widgets.Checkbox(text)
        if checklist[index] in checklist_data["checked"]:
            checkbox.checked = True
        checkbox.on_change(get_handler(index))

        hint_button = TransparentButton("?", 10)
        hint_button._text.bold = True
        hint_button.on_click(get_hint_callback(index))

        hint_y = win._real_height + 5
        win.add_next(checkbox)
        if hint: win.add(335 - hint_button.size.w, hint_y, hint_button)

@lime.init("checklist")
def render_checklist(win: lime.Window):
    rerender_checklist(win)   
