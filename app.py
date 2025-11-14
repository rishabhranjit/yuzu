import lime
from lime.util import *
import lime.widgets as widgets
import sys, os, subprocess, shutil, json
from pathlib import Path
sys.path.append(os.path.dirname(__file__))

from checklist import TransparentButton, checklist

#- Entry -#

entry = """Y88b    /═══════════════════════════╗            
 Y88b  /  888  888  ~~~d88P 888  888║ 
  Y88b/   888  888    d88P  888  888║ 
   Y8Y    888  888   d88P   888  888║     LINUX SCRIPTS (PROPERTY OF FHS FRESHMAN╱THE UNSTOPPABLE FORCE)
    Y     888  888  d88P    888  888║ 
   /      "88_-888 d88P___  "88_-888╣ 
R╱I╱S╱H╱A╱B╱H═══════════════════════╝       
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀   """

for i in range(len(entry.split("\n"))):
    print(f"\x1b[{(i + 1) % 2};38;2;{int(30 + (155 / len(entry.split("\n")) * (i + 1)))};{int(30 + 55 / len(entry.split("\n")) * (i + 1))};255m{entry.split("\n")[i]}")

#- Window Registration -#

@lime.register("main")
def register_main():
    return lime.create(
        "YUZU",
        310,
        277,
        pos=("left", "center")
    )

#- Window Rendering -#

def run_if_exists(cmd):
    if shutil.which(cmd[0]) is None:
        return False

    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.stderr:
        return False

    return result.stdout


checklist_path = Path.home() / ".checklist.json"

def check_checklist(index):
    checklist_dat = {}
    with open(checklist_path, 'r') as f:
        checklist_dat = json.load(f)

    if checklist[index] in checklist_dat["checked"]: return
    checklist_dat["checked"].append(checklist[index])

    with open(checklist_path, "w") as f:
        json.dump(checklist_dat, f)

@lime.init("main")
def render_main(win: lime.Window):
    #- Section 1 -#
    def secure(_):
        if (res := run_if_exists(["ufw", "enable"])):
            if "Firewall is active" in res:
                check_checklist(0)

        if (res := run_if_exists(["apt", "get", "update", "&&", "apt", "get", "upgrade"])):
            check_checklist(2)
            check_checklist(3)

        if (res := run_if_exists(["apt", "get", "dist-update"])):
            check_checklist(4)

        if (res := run_if_exists(["passwd", "-l", "root"])):
            check_checklist(7)

    basic_security = widgets.Button("Basic Security", 295)
    basic_security.on_click(secure)
    win.add_next(basic_security)

    #- Section 2 -#
    users = widgets.Button("Users", 145)
    services = widgets.Button("Services", 145)

    win.add_next(users)
    win.add(150, win._real_height - users.size.h, services)

    #- Section 3 -#
    permissions = widgets.Button("Perms", 95)
    binaries = widgets.Button("Binaries", 95)
    unauthorized_files = widgets.Button("Files", 95)

    win.add_next(permissions)
    win.add(100, win._real_height - permissions.size.h, binaries)
    win.add(200, win._real_height - permissions.size.h, unauthorized_files)

    #- Checklist -#
    checklist_button = TransparentButton("CHK", 30)
    checklist_button.on_click(lambda _: lime.open_window("checklist"))
    win.add(0, 242, checklist_button)
