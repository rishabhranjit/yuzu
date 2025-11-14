import lime
from lime.util import *
import lime.widgets as widgets
import sys, os
sys.path.append(os.path.dirname(__file__))

from checklist import TransparentButton

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

@lime.init("main")
def render_main(win: lime.Window):
    #- Section 1 -#
    basic_security = widgets.Button("Basic Security", 295)
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
