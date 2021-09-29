from py_stealth.methods import *
from datetime import datetime as dt
import math
import inspect
# Can be changed
TILE_SEARCH_RANGE = 5
WEIGHT_TO_PACK = 450
WEIGHT_TO_UNLOAD = 200
WEIGHT_TO_SMELT = 460
INITIAL_LOCATION = (2349, 887)
FORGE_LOCATION = (2477, 888)
BANK_ENTRY = (2476, 861)
BANK_ENTRY_DOOR = 0x4023A70C
BANK_INSIDE = (3438, 3422)
BANK_EXIT = (3445, 3442)
BANK_EXIT_DOOR = 0x4023AA50
POINTS = [
    (2342, 873),
    (2369, 864),
    (2389, 849),
    (2383, 857),
    (2412, 848),
    (2415, 835),
    (2422, 830),
    (2432, 828),
    (2447, 822),
    (2455, 822),
    (2473, 826),
    (2481, 830),
    (2490, 833),
    (2499, 837),
    (2506, 840),
    (2516, 846),
    (2523, 855),
    (2522, 846),
    (2527, 866),
    (2532, 873),
    (2531, 867),
    (2526, 884),
    (2517, 888),
    (2510, 892),
    (2496, 897),
    (2488, 899),
    (2482, 902),
    (2476, 905),
    (2465, 907),
    (2457, 911),
    (2448, 911),
    (2437, 910),
    (2426, 907),
    (2411, 905),
    (2398, 909),
    (2390, 909),
    (2377, 905),
    (2362, 899),
]

FORGE = 0x10DE
VERBOSE = True
# Generic types
GEMS = [0x0F10,
        0x0F13,
        0x0F25,
        0x0F15,
        0x0F16,
        0x0F26
]

INGOTS = 0x1BF2
#SHOVEL = 0x0F3A
SHOVEL = 0x0F39
MINING_BAG = 0x1C10
TINKER_TOOLS = 0x1EB8
ORE = 0x19B9


# Generic messages and tiles
SKIP_TILE_MESSAGES = ["no metal", "far away", "cannot be seen", "can't mine"]
NEXT_TRY_MESSAGES = ["loosen", "You dig some", "You dig up"]
# From UA sources
CAVE_TILES = [
    220, 221, 222, 223, 224, 225, 226, 227, 228, 229,
    230, 231, 236, 237, 238, 239, 240, 241, 242, 243,
    244, 245, 246, 247, 252, 253, 254, 255, 256, 257,
    258, 259, 260, 261, 262, 263, 268, 269, 270, 271,
    272, 273, 274, 275, 276, 277, 278, 279, 286, 287,
    288, 289, 290, 291, 292, 293, 294, 296, 296, 297,
    321, 322, 323, 324, 467, 468, 469, 470, 471, 472,
    473, 474, 476, 477, 478, 479, 480, 481, 482, 483,
    484, 485, 486, 487, 492, 493, 494, 495, 543, 544,
    545, 546, 547, 548, 549, 550, 551, 552, 553, 554,
    555, 556, 557, 558, 559, 560, 561, 562, 563, 564,
    565, 566, 567, 568, 569, 570, 571, 572, 573, 574,
    575, 576, 577, 578, 579, 581, 582, 583, 584, 585,
    586, 587, 588, 589, 590, 591, 592, 593, 594, 595,
    596, 597, 598, 599, 600, 601, 610, 611, 612, 613,

    1010, 1741, 1742, 1743, 1744, 1745, 1746, 1747, 1748, 1749,
    1750, 1751, 1752, 1753, 1754, 1755, 1756, 1757, 1771, 1772,
    1773, 1774, 1775, 1776, 1777, 1778, 1779, 1780, 1781, 1782,
    1783, 1784, 1785, 1786, 1787, 1788, 1789, 1790, 1801, 1802,
    1803, 1804, 1805, 1806, 1807, 1808, 1809, 1811, 1812, 1813,
    1814, 1815, 1816, 1817, 1818, 1819, 1820, 1821, 1822, 1823,
    1824, 1831, 1832, 1833, 1834, 1835, 1836, 1837, 1838, 1839,
    1840, 1841, 1842, 1843, 1844, 1845, 1846, 1847, 1848, 1849,
    1850, 1851, 1852, 1853, 1854, 1861, 1862, 1863, 1864, 1865,
    1866, 1867, 1868, 1869, 1870, 1871, 1872, 1873, 1874, 1875,
    1876, 1877, 1878, 1879, 1880, 1881, 1882, 1883, 1884, 1981,
    1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991,
    1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001,
    2002, 2003, 2004, 2028, 2029, 2030, 2031, 2032, 2033, 2100,
    2101, 2102, 2103, 2104, 2105,

    0x453B, 0x453C, 0x453D, 0x453E, 0x453F, 0x4540, 0x4541,
    0x4542, 0x4543, 0x4544,	0x4545, 0x4546, 0x4547, 0x4548,
    0x4549, 0x454A, 0x454B, 0x454C, 0x454D, 0x454E,	0x454F
]
##########


def log(message=""):
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

    for tile in CAVE_TILES:
        _tiles_coordinates += GetStaticTilesArray(
            _min_x, _min_y, _max_x, _max_y, WorldNum(), tile)

        _tiles_coordinates += GetLandTilesArray(
            _min_x, _min_y, _max_x, _max_y, WorldNum(), tile)

    log(f"Found {str(len(_tiles_coordinates))} tiles")
    return _tiles_coordinates


def to_bag() -> None:
    if bag := FindType(MINING_BAG, Backpack()):
        # Can't use while cuz of item limit in bag
        if FindType(ORE, Backpack()):
            for ore in GetFoundList():
                MoveItem(ore, -1, bag, 0, 0, 0)
                Wait(1500)


def smelt():
    IgnoreReset()
    forge_x, forge_y = FORGE_LOCATION
    move_x_y(forge_x, forge_y)

    if FindType(MINING_BAG, Backpack()):
        UseObject(FindItem())
        Wait(1000)

    while FindTypeEx(ORE, 0xFFFF, Backpack(), True):
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
            log("wat_for_gump timeout")
            return

    WaitGump(button)
    Wait(2000)


def mine(tile):
    tile, x, y, z = tile

    if newMoveXY(x, y, True, 2, True):
        while not Dead():
            # Smelt and return back to mining point
            if Weight() > WEIGHT_TO_PACK:
                Wait(1000)
                to_bag()
                if Weight() > WEIGHT_TO_SMELT:
                    smelt()
                    if Weight() > WEIGHT_TO_UNLOAD:
                        unload_to_bank()
                    move_x_y(x, y)

            started = dt.now()
            cancel_targets()
            if FindType(SHOVEL, Backpack()):
                UseType(SHOVEL, 0xFFFF)
            else:
                craft_item(8, 23, TINKER_TOOLS, TINKER_TOOLS, 2)
                craft_item(8, 86, TINKER_TOOLS, SHOVEL, 2)

            WaitForTarget(2000)
            if TargetPresent():
                WaitTargetXYZ(x, y, z)
                WaitJournalLine(started, "|".join(
                    SKIP_TILE_MESSAGES + NEXT_TRY_MESSAGES), 15000)

            if InJournalBetweenTimes("|".join(SKIP_TILE_MESSAGES), started, dt.now()) > 0:
                Wait(500)
                break
    else:
        print(f"Can't reach X: {x} Y: {y}")


def distance_from_player(target_x: int, target_y: int) -> int:
    self_x = GetX(Self())
    self_y = GetY(Self())
    return math.hypot(target_x - self_x, target_y - self_y)


def move_x_y(x: int, y: int) -> bool:
    log(f"Heading to point {x}, {y}")
    _try = 0
    while not newMoveXY(x, y, True, 1, True):
        if newMoveXY(x, y, True, 1, True):
            return True
        else:
            log(f"Failed to reach point {x}, {y}")
            _try += 1
            if _try > 10:
                return False

    log(f"Reached point {x}, {y}")
    return True


def unload_to_bank():
    bank_x, bank_y = BANK_ENTRY
    inside_x, inside_y = BANK_INSIDE
    exit_x, exit_y = BANK_EXIT
    move_x_y(bank_x, bank_y)
    UseObject(BANK_ENTRY_DOOR)
    Wait(2000)
    move_x_y(inside_x, inside_y)
    while LastContainer() != Backpack():
        UseObject(Backpack())
        Wait(1000)

    attempt = 0
    while LastContainer() != ObjAtLayer(BankLayer()):
        attempt += 1
        if attempt > 5:
            log("Failed to open bank")
            exit()
        UOSay("bank")
        Wait(1000)

    #while FindType(INGOTS, Backpack()):
    while FindTypesArrayEx([INGOTS] + GEMS, [0xFFFF], [Backpack()], [True]):
        MoveItem(FindItem(), -1, ObjAtLayer(BankLayer()), 0, 0, 0)
        Wait(2000)

    # We have to keep some Iron ingots to craft shovels\tools
    if not FindTypeEx(INGOTS, 0x0000, Backpack()):
        FindTypeEx(INGOTS, 0x0000, ObjAtLayer(BankLayer()))
        Grab(FindItem(), 30)
        Wait(2000)

    move_x_y(exit_x, exit_y)
    UseObject(BANK_EXIT_DOOR)
    Wait(2000)


if __name__ == "__main__":
    SetMoveOpenDoor(True)
    SetMoveThroughNPC(True)
    while not Dead():
        for point in POINTS:
            point_x, point_y = point
            log(f"Point: {point_x}, {point_y}")
            move_x_y(point_x, point_y)
            tiles = find_tiles(GetX(Self()), GetY(Self()), TILE_SEARCH_RANGE)
            sorted_tiles = sorted(
                tiles, key=lambda tile: distance_from_player(tile[1], tile[2]))
            for tile_counter in range(0, len(sorted_tiles), 4):
                log(f"Tile #{tile_counter}")
                mine(sorted_tiles[tile_counter])
