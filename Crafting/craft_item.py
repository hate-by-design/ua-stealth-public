from py_stealth.methods import *

TINKER_TOOLS = 0x1EB8
INGOTS = 0x1BF2
LOCKPICK = 0x14FC

def craft_item(tool_category: int, tool_button: int, tool_type: int, item_type: int, required_qty: int) -> None:
    while Count(item_type) < required_qty:
        for _gump_counter in range(0, GetGumpsCount()):
            CloseSimpleGump(_gump_counter)

        if FindType(tool_type, Backpack()):
            UseType(tool_type, 0x0000)
            Wait(500)
            wait_for_gump(tool_category)
            wait_for_gump(tool_button)
            wait_for_gump(0)


def find_gump(gump_id: int) -> bool:
    for _gump in range(0, GetGumpsCount()):
        if GetGumpID(_gump) == gump_id:
            return True
    return False


def wait_for_gump(button: int) -> None:
    _try = 0
    while not find_gump(0x38920ABD):
        _try += 1
        Wait(500)
        if _try > 30:
            # print("wat_for_gump timeout")
            return

    WaitGump(button)
    Wait(2000)

if __name__ == "__main__":
    print("Ok")
    while FindTypeEx(INGOTS, 0x0000, Backpack()) and FindQuantity() > 10:
        print("Crafting")
        craft_item(8, 23, TINKER_TOOLS, TINKER_TOOLS, 2)
        craft_item(8, 149, TINKER_TOOLS, LOCKPICK, 2000)