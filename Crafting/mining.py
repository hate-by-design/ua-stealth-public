from py_stealth.methods import *
from datetime import datetime as dt
import inspect
##########
SHOVEL = 0x0F39
TINKER_TOOLS = 0x1EB8
ORE = [0x19B9, 0x19B8, 0x19B7]
SMALL_ORE = 0x19B7
#FORGE = 0x0FB1
FORGE = 0x198E
## Locations
INITIAL_LOCATION = (3039, 3958)
FORGE_LOCATION = (3037, 3972)
##
####
SKIP_TILE_MESSAGES = ["no metal", "far away"]
NEXT_TRY_MESSAGES = ["loosen", "You dig some", "You dig up"]

CAVE_TILES = range(1339, 1358)

VERBOSE = True
##########

def log(message = ""):
    if VERBOSE:
        AddToSystemJournal(f"[{inspect.stack()[1].function}] {message}")

def cancel_targets():
    CancelWaitTarget()
    if TargetPresent():
        CancelTarget()

def find_tiles(center_x: int, center_y: int, radius: int) -> set[int, int, int, int]:
    _min_x, _min_y = center_x-radius, center_y-radius
    _max_x, _max_y = center_x+radius, center_y+radius
    _tiles_coordinates = []
    for _tile in CAVE_TILES:
        _tiles_coordinates += GetStaticTilesArray(
            _min_x, _min_y, _max_x, _max_y, WorldNum(), _tile)
    log(f"Found {str(len(_tiles_coordinates))} tiles")
    return _tiles_coordinates

def smelt():
    IgnoreReset()
    forge_x, forge_y = FORGE_LOCATION
    newMoveXY(forge_x, forge_y, True, 1, True)

    # Stack small ore piles
    # TODO: Color ore support
    while FindType(SMALL_ORE, Backpack()) and len(GetFoundList()) > 1:
        UseObject(GetFoundList()[0])
        WaitTargetObject(GetFoundList()[1])
        Wait(1000)

    while FindTypesArrayEx(ORE, [0xFFFF], [Backpack()], False):
        # You can't smelt 1 ore =\
        if GetQuantity(FindItem()) > 1:
            WaitTargetTile(FORGE, forge_x, forge_y, GetZ(Self()))
            UseObject(FindItem())
            WaitJournalLine(dt.now(), "You smelt|You burn", 5000)
            Wait(1000)
        else:
            Ignore(FindItem())

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


def mine(tile):
    tile, x, y, z = tile
    if newMoveXY(x, y, True, 1, True):
        while not Dead():
            # Smelt and return back to mining point
            if Weight() > 330:
                smelt()
                newMoveXY(x, y, True, 1, True)
                craft_item(8, 23, TINKER_TOOLS, TINKER_TOOLS, 2)
                craft_item(8, 86, TINKER_TOOLS, SHOVEL, 2)

            started = dt.now()
            cancel_targets()
            UseType(SHOVEL, 0xFFFF)
            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetTile(tile, x, y, z)
                WaitJournalLine(started, "|".join(SKIP_TILE_MESSAGES + NEXT_TRY_MESSAGES), 15000)

            if InJournalBetweenTimes("|".join(SKIP_TILE_MESSAGES), started, dt.now()) > 0:
                break
    else:
        print(f"Can't reach X: {x} Y: {y}")

if __name__ == "__main__":
    init_x, init_y = INITIAL_LOCATION
    newMoveXY(init_x, init_y, True, 1, True)
    tiles = find_tiles(GetX(Self()), GetY(Self()), 20)
    for tile in range(0, len(tiles), 4):
        # print(tiles[tile])
        mine(tiles[tile])
