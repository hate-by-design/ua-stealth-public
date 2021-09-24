from py_stealth.methods import *
from datetime import timedelta, datetime as dt
import inspect

VERBOSE = True
WEIGHT_TO_PACK = 390
WEIGHT_TO_UNLOAD = 450

# Right
POINTS = [
    (2901, 870, 5),
    (2896, 846, 5),
    (2862, 838, 5),
    (2889, 792, 5),
    (2925, 769, 5),
    (2947, 796, 5),
    (2956, 828, 5)
]

# POINTS = [
#     (2801, 1113, 5),
#     (2782, 1157, 5),
#     (2831, 1214, 5)
# ]
TREE_TILES = [
    3274, 3275, 3277, 3280,
    3283, 3286, 3288, 3290,
    3293, 3296, 3299, 3302,
    3320, 3323, 3326, 3329,
    3393, 3394, 3395, 3396,
    3415, 3416, 3417, 3418,
    3419, 3438, 3439, 3440,
    3441, 3442, 3460, 3461,
    3462, 3476, 3478, 3480,
    3482, 3484, 3492, 3496
]
SAW_MILL_POINT = (2942, 1051)
# Common types
LUMBER_BAG = 0x1C10
AXE = 0x0F43
LOG = 0x1BE0
SAW_MILL = 0x0788
BOARDS = 0x1BD7

# Messages to skip current tile (depleted, etc0
SKIP_TILE_MESSAGES = [
                "not enough",
                "You cannot",
]
# Messages to continue chopping
NEXT_TRY_MESSAGES = [
                     "You hack at",
                     "You put",
                     "You chop",
                     "You have worn"
]
# Messages to mark tile as bad
BAD_POINT_MESSAGES = [
                        "You can't use",
                        "be seen",
                        "is too far",
                        "no line of",
                        "axe on that",
]
BAD_POINTS = []

def find_tiles(centerx: int, centery: int, radius: int) -> list[tuple[int, int, int, int]]:
    _minx, _miny = centerx-radius, centery-radius
    _maxx, _maxy = centerx+radius, centery+radius
    _tiles_coordinates = []
    for _tile in TREE_TILES:
        _tiles_coordinates += GetStaticTilesArray(_minx, _miny, _maxx, _maxy, WorldNum(), _tile)
    log("[FindTiles] Found "+str(len(_tiles_coordinates))+" tiles")
    return _tiles_coordinates

def log(message: str = "") -> None:
    if VERBOSE:
        AddToSystemJournal(f"[{inspect.stack()[1].function}] {message}")

def cancel_targets() -> None:
    CancelWaitTarget()
    if TargetPresent():
        CancelTarget()


def check_and_equip_tool() -> None:
    if not ObjAtLayer(LhandLayer()):
        if FindType(AXE, Backpack()):
            Equip(LhandLayer(), FindItem())
            Wait(500)
        else:
            log("No more axes left in pack!")
            exit()


def to_bag() -> None:
    if bag := FindType(LUMBER_BAG, Backpack()):
        while FindType(LOG, Backpack()):
            MoveItem(FindItem(), -1, bag, 0, 0, 0)
            Wait(1000)

def cut() -> None:
    mill_x, mill_y = SAW_MILL_POINT
    newMoveXY(mill_x, mill_y, True, 1, True)

    while LastContainer() != Backpack():
        UseObject(Backpack())
        Wait(1000)

    while LastContainer() == Backpack():
        UseType(LUMBER_BAG, 0xFFFF)
        Wait(1000)

    while FindType(LOG, LastContainer()):
        WaitTargetGround(SAW_MILL)
        UseObject(FindItem())
        WaitJournalLine(dt.now(), "cut", 5000)
        Wait(1000)

def lumberjacking(tile: tuple[int, int, int, int]) -> None:
    tile, x, y, z = tile
    if ([x, y] not in BAD_POINTS) and NewMoveXY(x, y, True, 1, True):
        while Dead():
            log("I'm dead =(")
            Wait(1000)

        while not Dead():
            _starting_ts = dt.now()
            cancel_targets()
            check_and_equip_tool()
            if Weight() > WEIGHT_TO_PACK:
                to_bag()
                if Weight() > WEIGHT_TO_UNLOAD:
                    cut()
                    NewMoveXY(x, y, True, 1, True)

            UseObject(ObjAtLayer(LhandLayer()))
            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetTile(tile, x, y, GetZ(Self()))
                WaitJournalLine(_starting_ts, "|".join(NEXT_TRY_MESSAGES + SKIP_TILE_MESSAGES + BAD_POINT_MESSAGES),
                                15000)

                # If we waited full WaitJournalLine timeout, something went wrong
                if dt.now() >= _starting_ts+timedelta(seconds=15):
                    log(f"{x} {y} WaitJournalLine timeout exceeded, bad tree?")
                    break

                if InJournalBetweenTimes("|".join(BAD_POINT_MESSAGES), _starting_ts, dt.now()) > 0:
                    if [x, y] not in BAD_POINTS:
                        log(f"Added tree to bad points, trigger => {BAD_POINT_MESSAGES[FoundedParamID()]}")
                        BAD_POINTS.append([x, y])
                        break

                if InJournalBetweenTimes("|".join(SKIP_TILE_MESSAGES), _starting_ts, dt.now()) > 0:
                    # print("Tile depleted, skipping")
                    break
            else:
                log("No target present for some reason...")
            Wait(500)


# Start
ClearSystemJournal()
SetARStatus(True)
SetMoveOpenDoor(True)
SetPauseScriptOnDisconnectStatus(True)
IgnoreReset()
SetFindDistance(25)

if __name__ == "__main__":
    while Connected():
        for point in POINTS:
            point_x, point_y, _ = point
            newMoveXY(point_x, point_y, True, 1, True)
            tiles_list = find_tiles(point_x, point_y, 15)
            for tile_data in tiles_list:
                lumberjacking(tile_data)
                Wait(1000)