from py_stealth.methods import *
import inspect

TARGET = "dagger"
KEEP = False
VERBOSE = True
#
TINKER_TOOLS = 0x1EB8
INGOTS = 0x1BF2
CRAFTING_GUMP = 0x38920ABD
ITEMS = {
    "tinker_tools": {"category": 8, "button": 23, "type": 0x1EB8, "tool": "tinker_tools", "material": 0x1BF2},
    "saw": {"category": 8, "button": 65, "type": 0x1034, "tool": "tinker_tools", "material": 0x1BF2},
    "lockpick": {"category": 8, "button": 149, "type": 0x14FC, "tool": "tinker_tools", "material": 0x1BF2},
    "smiths_hammer": {"category": 8, "button": 121, "type": 0x0FB4, "tool": "tinker_tools", "material": 0x1BF2},
    "dagger": {"category": 43, "button": 44, "type": 0x0F52, "tool": "smiths_hammer", "material": 0x1BF2},

}

def log(message = ""):
    if VERBOSE:
        AddToSystemJournal(f"[{inspect.stack()[1].function}] {message}")

def craft_item(item: dict, required_qty: int = 9999) -> None:
    if Count(item["type"]) < required_qty:
        for gump_counter in range(0, GetGumpsCount()):
            CloseSimpleGump(gump_counter)

        tool = ITEMS[item["tool"]]["type"]
        if FindType(tool, Backpack()):
            UseType(tool, 0xFFFF)
            for button in [item["category"], item["button"], 0]:
                wait_for_gump(button)
        else:
            log("No tools in backpack!")


def find_gump(gump_id: int) -> bool:
    for gump in range(0, GetGumpsCount()):
        if GetGumpID(gump) == gump_id:
            return True
    return False


def wait_for_gump(button: int) -> None:
    attempt = 0
    while not find_gump(CRAFTING_GUMP):
        attempt += 1
        Wait(100)
        if attempt > 30:
            log("wat_for_gump timeout")
            return

    WaitGump(button)
    Wait(2000)

if __name__ == "__main__":
    item_to_craft = ITEMS[TARGET]
    required_tools = ITEMS[item_to_craft["tool"]]
    tinker_tools = ITEMS["tinker_tools"]

    while not Dead():
        # Keep 2 tinker tools, required tools in pack
        # Craft 1 target item to be able to use Make Last button
        craft_item(tinker_tools, 2)
        craft_item(required_tools, 2)
        craft_item(item_to_craft)

        UseType(required_tools["type"], 0xFFFF)
        wait_for_gump(21)
        for _ in range(10):
            # If we can reuse opened gump
            if find_gump(CRAFTING_GUMP):
                # Make last
                log("Making last item...")
                wait_for_gump(21)

        if not KEEP:
            AutoSell(item_to_craft["type"], 0xFFFF, -1)
            UOSay("sell")