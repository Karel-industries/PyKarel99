#!/bin/python3.10

import ctypes
import pygame
import time
import threading
import os, sys
import serial
from pprint import pprint


class Config:
    size = [20, 20]  # default is 20x20
    screen_size = 600
    interval = 100  # ms
    fps_cap = 0
    flags_are_numbers = False  # True or False
    use_diferent_karel = False  # True or False
    just_use_simple_colors = False  # True or False

    ignore_out_of_screen = True

    use_KVM = True

    save_translated_file_as_utf8 = True
    default_file = "mainutf8"  # Can be without .K99 extension
    default_func = "TEST"
    # default_file = ""   # Can be without .K99 extension
    # default_func = ""

    EspPort = "/dev/ttyACM0"  # For future emulator on a esp32
    EspKarelMode = False


class Karel:
    running_gui = True
    stop_code = False

    x = 0
    y = Config.size[1] - 1  # 19

    home_x = 0
    home_y = Config.size[1] - 1

    # 0 = up            [North]     Sever
    # 1 = left  (<-)    [WEST]      Západ
    # 2 = down          [SOUTH]     Jih
    # 3 = right (->)    [EAST]      Východ
    dir = 3

    def turn_left():
        Karel.dir += 1
        if Karel.dir == 4:
            Karel.dir = 0

    def step():
        if MapStorage.is_wall(Karel.get_pos_in_front()):
            return

        if Karel.dir == 0:
            Karel.y -= 1
        elif Karel.dir == 1:
            Karel.x -= 1
        elif Karel.dir == 2:
            Karel.y += 1
        elif Karel.dir == 3:
            Karel.x += 1

    def get_pos_in_front():
        if Karel.dir == 0:
            return [Karel.x, Karel.y - 1]

        elif Karel.dir == 1:
            return [Karel.x - 1, Karel.y]

        elif Karel.dir == 2:
            return [Karel.x, Karel.y + 1]

        elif Karel.dir == 3:
            return [Karel.x + 1, Karel.y]


class MapStorage:
    MAX_FLAG = 8

    map = []
    # 0   = Empty
    # 1-8 = Flags
    # W   = wall

    def init():
        MapStorage.map = [
            ["0" for _ in range(Config.size[0])] for _ in range(Config.size[1])
        ]

    def valid_pos(pos):
        if pos[0] < 0 or pos[0] > Config.size[0] - 1:
            return False
        if pos[1] < 0 or pos[1] > Config.size[1] - 1:
            return False
        return True

    def is_wall(pos):
        # Everything outside of game field is a wall
        if not MapStorage.valid_pos(pos):
            return True

        if MapStorage.map[pos[0]][pos[1]] == "W":
            return True
        else:
            return False


class Functions:
    def Step():
        if not MapStorage.is_wall(Karel.get_pos_in_front()):
            Karel.step()

    def Turn_left():
        Karel.turn_left()

    def Place_flag():
        if not int(MapStorage.map[Karel.x][Karel.y]) >= MapStorage.MAX_FLAG:
            MapStorage.map[Karel.x][Karel.y] = str(
                int(MapStorage.map[Karel.x][Karel.y]) + 1
            )

    def Pick_flag():
        if not MapStorage.map[Karel.x][Karel.y] == "0":
            MapStorage.map[Karel.x][Karel.y] = str(
                int(MapStorage.map[Karel.x][Karel.y]) - 1
            )

    def Is_wall_in_front():
        return MapStorage.is_wall(Karel.get_pos_in_front())

    def Is_flag():
        return not MapStorage.map[Karel.x][Karel.y] in ["0", "W"]

    def At_home():
        return Karel.home_x == Karel.x and Karel.home_y == Karel.y

    def Facing_north():
        return Karel.dir == 0

    def Facing_south():
        return Karel.dir == 2

    def Facing_east():
        return Karel.dir == 3

    def Facing_west():
        return Karel.dir == 1


class Screen:
    SQUARE_SIZE = Config.screen_size / max(Config.size)
    screen = pygame.display.set_mode((Config.screen_size, Config.screen_size))
    clock = pygame.time.Clock()

    def draw_frame():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Karel.stop_code = True
                Karel.running_gui = False
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Karel.stop_code = True
                    Karel.running_gui = False
                elif event.key == pygame.K_q:
                    Karel.stop_code = True

        Screen.screen.fill((180, 180, 180))

        if Config.just_use_simple_colors:
            # Draw the grid and squares
            for y in range(Config.size[1]):
                for x in range(Config.size[0]):
                    if MapStorage.map[x][y] == "W":
                        color = SimpleColors.WALL
                    elif Karel.home_x == x and Karel.home_y == y:
                        color = (
                            min(
                                (
                                    (
                                        SimpleColors.FLAGS[int(MapStorage.map[x][y])][0]
                                        + SimpleColors.HOME[0]
                                    )
                                    / 2
                                ),
                                255,
                            ),
                            min(
                                (
                                    (
                                        SimpleColors.FLAGS[int(MapStorage.map[x][y])][1]
                                        + SimpleColors.HOME[1]
                                    )
                                    / 2
                                ),
                                255,
                            ),
                            min(
                                (
                                    (
                                        SimpleColors.FLAGS[int(MapStorage.map[x][y])][2]
                                        + SimpleColors.HOME[2]
                                    )
                                    / 2
                                ),
                                255,
                            ),
                        )
                    else:
                        color = SimpleColors.FLAGS[int(MapStorage.map[x][y])]

                    pygame.draw.rect(
                        Screen.screen,
                        color,
                        (
                            x * Screen.SQUARE_SIZE,
                            y * Screen.SQUARE_SIZE,
                            Screen.SQUARE_SIZE,
                            Screen.SQUARE_SIZE,
                        ),
                    )

            if Karel.home_x == Karel.x and Karel.home_y == Karel.y:
                color = (
                    min(
                        (
                            (
                                SimpleColors.FLAGS[
                                    int(MapStorage.map[Karel.x][Karel.y])
                                ][0]
                                + SimpleColors.KAREL[Karel.dir][0]
                                + SimpleColors.HOME[0]
                            )
                            / 2
                        ),
                        255,
                    ),
                    min(
                        (
                            (
                                SimpleColors.FLAGS[
                                    int(MapStorage.map[Karel.x][Karel.y])
                                ][1]
                                + SimpleColors.KAREL[Karel.dir][1]
                                + SimpleColors.HOME[1]
                            )
                            / 2
                        ),
                        255,
                    ),
                    min(
                        (
                            (
                                SimpleColors.FLAGS[
                                    int(MapStorage.map[Karel.x][Karel.y])
                                ][2]
                                + SimpleColors.KAREL[Karel.dir][2]
                                + SimpleColors.HOME[2]
                            )
                            / 2
                        ),
                        255,
                    ),
                )
            else:
                color = (
                    min(
                        (
                            (
                                SimpleColors.FLAGS[
                                    int(MapStorage.map[Karel.x][Karel.y])
                                ][0]
                                + SimpleColors.KAREL[Karel.dir][0]
                            )
                            / 2
                        ),
                        255,
                    ),
                    min(
                        (
                            (
                                SimpleColors.FLAGS[
                                    int(MapStorage.map[Karel.x][Karel.y])
                                ][1]
                                + SimpleColors.KAREL[Karel.dir][1]
                            )
                            / 2
                        ),
                        255,
                    ),
                    min(
                        (
                            (
                                SimpleColors.FLAGS[
                                    int(MapStorage.map[Karel.x][Karel.y])
                                ][2]
                                + SimpleColors.KAREL[Karel.dir][2]
                            )
                            / 2
                        ),
                        255,
                    ),
                )

            pygame.draw.rect(
                Screen.screen,
                color,
                (
                    Karel.x * Screen.SQUARE_SIZE,
                    Karel.y * Screen.SQUARE_SIZE,
                    Screen.SQUARE_SIZE,
                    Screen.SQUARE_SIZE,
                ),
            )

        else:
            # Draw the grid and squares
            for y in range(Config.size[1]):
                for x in range(Config.size[0]):
                    if MapStorage.map[x][y] == "W":
                        Screen.screen.blit(
                            Images.WALL,
                            (x * Screen.SQUARE_SIZE, y * Screen.SQUARE_SIZE),
                        )

                    elif MapStorage.map[x][y] == "0":
                        if (x + y) % 2 == 0:
                            continue
                        pygame.draw.rect(
                            Screen.screen,
                            (200, 200, 200),
                            (
                                x * Screen.SQUARE_SIZE,
                                y * Screen.SQUARE_SIZE,
                                Screen.SQUARE_SIZE,
                                Screen.SQUARE_SIZE,
                            ),
                        )
                    else:
                        Screen.screen.blit(
                            Images.FLAGS[int(MapStorage.map[x][y])],
                            (x * Screen.SQUARE_SIZE, y * Screen.SQUARE_SIZE),
                        )

            Screen.screen.blit(
                Images.HOME,
                (Karel.home_x * Screen.SQUARE_SIZE, Karel.home_y * Screen.SQUARE_SIZE),
            )
            Screen.screen.blit(
                Images.KAREL[Karel.dir],
                (Karel.x * Screen.SQUARE_SIZE, Karel.y * Screen.SQUARE_SIZE),
            )

        pygame.display.flip()


class Code:
    code = []
    commented_code = []
    function_definitions = {}  # The commands under the function

    def format_code(raw_code):
        # Fix some characters and remove newlines
        in_code = raw_code
        ungibrished_code = []
        for line in in_code:
            ungibrished_code.append(
                str(
                    line.replace("\x8e", "Ž")
                    .replace("\x9e", "ž")
                    .replace("\n", "")
                    .replace("\t", "")
                )
            )

        # Translate to english
        in_code = ungibrished_code
        translated_code = []
        for line in in_code:
            edited_line = line
            for alias in ALIASES.keys():
                edited_line = edited_line.replace(alias, ALIASES[alias])
            translated_code.append(edited_line)

        # Remove comments
        in_code = translated_code
        uncomented_code = []

        for i, line in enumerate(in_code):
            tmp_line = ""
            if in_code[i].count(";") > 0:
                tmp_line = line[: line.index(";")]
            else:
                tmp_line = line

            if not tmp_line == "":
                uncomented_code.append(tmp_line)

        return (translated_code, uncomented_code)

    def save_as_utf8(file_path):
        if Config.save_translated_file_as_utf8:
            if "utf8" in file_path:
                path = file_path
            else:
                path = file_path.replace(".K99", "utf8.K99")
            with open(path, "w") as f:
                for line in Code.code:
                    f.write(line + "\n")

    def load(file_path):
        if "utf8" in file_path:
            with open(file_path, "r") as f:
                Code.commented_code, Code.code = Code.format_code(f.readlines())
        else:
            with open(file_path, "r", encoding="iso_8859_2") as f:
                Code.commented_code, Code.code = Code.format_code(f.readlines())

        for index, string in enumerate(Code.code):
            if "Map size" in string:
                start_config_index = index
                break

        for i, line in enumerate(Code.code):
            is_new = True
            if line.startswith("   ") or line.startswith("END"):
                is_new = False

            if is_new:
                if ";" in line:
                    function_name = line[: line.index(";")]
                else:
                    function_name = line
                function_definition = []
                for o in range(i + 1, start_config_index):
                    if Code.code[o].startswith("END"):
                        break

                    function_definition.append(Code.code[o].replace("   ", "", 1))

                Code.function_definitions[function_name] = function_definition

        Code.save_as_utf8(file_path)

        # Load data from code

        first_index = 0
        for line in Code.code:
            if line.startswith("Map size"):
                first_index = int(Code.code.index(line))
                break

        map_size_raw = Code.code[first_index].replace("Map size: ", "").split(", ")
        map_size = [int(map_size_raw[0]), int(map_size_raw[1])]

        Config.size = map_size

        # Karel pos
        karel_pos_raw = (
            Code.code[first_index + 1].replace("Karel position: ", "").split(", ")
        )
        Karel.x = int(karel_pos_raw[0]) - 1
        Karel.y = int(karel_pos_raw[1]) - 1

        # Karel home
        karel_home_pos_raw = (
            Code.code[first_index + 3].replace("Home position: ", "").split(", ")
        )
        Karel.home_x = int(karel_home_pos_raw[0]) - 1
        Karel.home_y = int(karel_home_pos_raw[1]) - 1

        # Karel rot
        rotations = ["NORTH", "WEST", "SOUTH", "EAST"]
        Karel.dir = rotations.index(
            Code.code[first_index + 2].replace("Karel rotation: ", "")
        )

        # Map
        tmp_map = []
        for i in range(Config.size[1]):
            "".split()
            tmp_map.append(list(Code.code[first_index + 5 + i]))

        for y in range(Config.size[1]):
            for x in range(Config.size[0]):
                if tmp_map[y][x] == ".":
                    MapStorage.map[x][y] = "0"
                elif tmp_map[y][x] == "X":
                    MapStorage.map[x][y] = "W"
                elif tmp_map[y][x] in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    MapStorage.map[x][y] = tmp_map[y][x]

    def run(func_name):
        if Karel.running_gui:
            if not func_name in Code.function_definitions.keys():
                print("\033[31mWrong func name: " + func_name + "\033[0m")
                return

            print("\n\033[32mRunning\033[0m " + func_name)
            Code.run_func_list(Code.function_definitions[func_name])

    def run_func_list(func_list):
        if Karel.stop_code == True or len(func_list) == 0:
            return
        index = 0

        while index < len(func_list):
            if Karel.stop_code == True:
                return
            line = func_list[index]
            if "STEP" in line:
                Functions.Step()
                if not Config.interval == 0:
                    time.sleep(Config.interval / 1000)
            elif "LEFT" in line:
                Functions.Turn_left()
                if not Config.interval == 0:
                    time.sleep(Config.interval / 1000)
            elif "PICK" in line:
                Functions.Pick_flag()
                if not Config.interval == 0:
                    time.sleep(Config.interval / 1000)
            elif "PLACE" in line:
                Functions.Place_flag()
                if not Config.interval == 0:
                    time.sleep(Config.interval / 1000)
            elif "UNTIL" in line:
                tab_count = func_list[0].count("   ")
                tmp_index = int(index + 1)
                tmp_code = []
                conditions = line.replace("   ", "").replace("UNTIL ", "").split(" ")
                while True:
                    if func_list[tmp_index] == str(str("   " * tab_count) + "END"):
                        break
                    else:
                        tmp_code.append(func_list[tmp_index])
                    tmp_index += 1
                index = tmp_index

                if len(tmp_code) == 0:
                    continue

                if conditions[0] == "IS":
                    while IF_LIST[conditions[1]]() and Karel.stop_code == False:
                        Code.run_func_list(tmp_code)
                elif conditions[0] == "ISNOT":
                    while not IF_LIST[conditions[1]]() and Karel.stop_code == False:
                        Code.run_func_list(tmp_code)

            elif "IF IS" in line:
                tab_count = func_list[0].count("   ")
                tmp_index = int(index + 1)
                if_tmp_code = []
                else_tmp_code = []
                conditions = line.replace("   ", "").replace("IF ", "").split(" ")
                while True:
                    if func_list[tmp_index] == str(
                        str("   " * tab_count) + "END, ELSE"
                    ):
                        break
                    else:
                        if_tmp_code.append(func_list[tmp_index])
                    tmp_index += 1
                tmp_index += 1
                while True:
                    if func_list[tmp_index] == str(str("   " * tab_count) + "END"):
                        break
                    else:
                        else_tmp_code.append(func_list[tmp_index])
                    tmp_index += 1
                index = tmp_index

                if len(if_tmp_code) == 0 and len(else_tmp_code) == 0:
                    continue

                if conditions[0] == "IS":
                    if IF_LIST[conditions[1]]():
                        Code.run_func_list(if_tmp_code)
                    else:
                        Code.run_func_list(else_tmp_code)
                elif conditions[0] == "ISNOT":
                    if not IF_LIST[conditions[1]]():
                        Code.run_func_list(if_tmp_code)
                    else:
                        Code.run_func_list(else_tmp_code)

            elif "REPEAT" in line:
                tab_count = func_list[0].count("   ")
                tmp_index = int(index + 1)
                tmp_code = []
                while True:
                    if func_list[tmp_index] == str(str("   " * tab_count) + "END"):
                        break
                    else:
                        tmp_code.append(func_list[tmp_index])
                    tmp_index += 1
                index = tmp_index

                if len(tmp_code) == 0:
                    continue

                for _ in range(
                    int(
                        line.replace("   ", "")
                        .replace("REPEAT", "")
                        .replace("-TIMES", "")
                    )
                ):
                    if Karel.stop_code == True:
                        return
                    Code.run_func_list(tmp_code)

            elif "PRINT" in line:
                print(line.replace("   ", "").replace("PRINT ", ""))
            elif "END" in line:  # just to be safe, but not used (hopefully)
                pass
            else:
                Code.run_func_list(
                    Code.function_definitions[line.replace("   ", "")]
                )  # recursive

            index += 1


class KVM:
    lib = None

    def init():
        print("\nLoading KVM")
        os.system(
            "mkdir -p KVM && cd KVM && git submodule update --init --remote --rebase && cd KVM && zig build -Doptimize=ReleaseFast"
        )
        if os.path.exists("KVM/KVM/zig-out/lib/libKvm.so"):  # LINUX
            KVM.lib = ctypes.CDLL("KVM/KVM/zig-out/lib/libKvm.so")
        elif os.path.exists("KVM/KVM/zig-out/lib/Kvm.dll"):  # WINDOWS
            KVM.lib = ctypes.CDLL("KVM/KVM/zig-out/lib/Kvm.dll")
        elif os.path.exists("KVM/KVM/zig-out/lib/libKvm.dylib"):  # OSX
            KVM.lib = ctypes.CDLL("KVM/KVM/zig-out/lib/libKvm.dylib")
        else:
            print(
                "I tried to make it for this os and it looks i failed, btw this is in the part that loads the KVM"
            )
            quit()

        KVM.lib.init()

    def deinit():
        if Config.use_KVM:
            KVM.lib.deinit()

    def save_code():
        with open("KVM/code.kl", "w") as f:
            for line in Code.code:
                if "Map size" in line:
                    break
                f.write(line + "\n")

    def save_map():
        with open("KVM/code.km", "w") as f:
            f.write(f"{Config.size[0]},{Config.size[1]};")
            for y in range(Config.size[1]):
                for x in range(Config.size[0]):
                    f.write(MapStorage.map[x][y])

    def load():
        KVM.lib.load("KVM/code.kl".encode("utf-8"))

    def load_world():
        KVM.lib.load_world()

    def stop():
        KVM.lib.short_circuit()

    def run_func(func_name):
        KVM.lib.run_symbol(func_name.encode("utf-8"))


class Images:
    ICON = pygame.image.load("assets/icon.png")

    WALL = pygame.transform.scale(
        pygame.image.load("assets/wall.png"), (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE)
    )

    HOME = pygame.transform.scale(
        pygame.image.load("assets/home.png"), (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE)
    )

    if Config.use_diferent_karel:
        KAREL = [
            pygame.transform.scale(
                pygame.image.load("assets/different-karel/karel-0.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/different-karel/karel-1.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/different-karel/karel-2.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/different-karel/karel-3.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
        ]
    else:
        KAREL = [
            pygame.transform.scale(
                pygame.image.load("assets/karel-0.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/karel-1.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/karel-2.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/karel-3.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
        ]

    if Config.flags_are_numbers:
        FLAGS = [
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-0.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-1.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-2.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-3.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-4.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-5.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-6.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-7.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-8.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
        ]
    else:
        FLAGS = [
            pygame.transform.scale(
                pygame.image.load("assets/flag-0.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-1.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-2.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-3.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-4.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-5.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-6.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-7.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-8.png"),
                (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE),
            ),
        ]


class SimpleColors:
    WALL = (255, 0, 0)
    HOME = (0, 0, 255)
    KAREL = [(128, 255, 0), (170, 213, 0), (213, 170, 0), (255, 128, 0)]
    FLAGS = [
        (128, 128, 128),
        (213, 61, 79),
        (244, 109, 67),
        (253, 174, 97),
        (254, 224, 139),
        (230, 245, 152),
        (171, 221, 164),
        (102, 194, 165),
        (50, 136, 189),
    ]


MapStorage.init()

IF_LIST = {
    "WALL": Functions.Is_wall_in_front,
    "FLAG": Functions.Is_flag,
    "HOME": Functions.At_home,
    "NORTH": Functions.Facing_north,
    "SOUTH": Functions.Facing_south,
    "EAST": Functions.Facing_east,
    "WEST": Functions.Facing_west,
}

ALIASES = {
    "KROK": "STEP",
    "VLEVO-VBOK": "LEFT",
    "ZVEDNI": "PICK",
    "POLOŽ": "PLACE",
    "OPAKUJ": "REPEAT",
    "KRÁT": "TIMES",
    "DOKUD": "UNTIL",
    "KDYŽ": "IF",
    "JINAK": "ELSE",
    "JE": "IS",
    "NENÍ": "ISNOT",
    "ZEĎ": "WALL",
    "ZNAČKA": "FLAG",
    "DOMOV": "HOME",
    "SEVER": "NORTH",
    "JIH": "SOUTH",
    "ZÁPAD": "WEST",
    "VÝCHOD": "EAST",
    "KONEC": "END",
    "Velikost města": "Map size",
    "Pozice Karla": "Karel position",
    "Otočení Karla": "Karel rotation",
    "Umístění domova": "Home position",
    "Definice města": "Map definition",
    "VYTISKNI": "PRINT",  # added feature
}


def quit():
    KVM.deinit()
    pygame.quit()
    exit()


def handle_esp(func_name):
    data_to_send = []

    for func in Code.function_definitions.keys():
        function_line = ""
        for line in Code.function_definitions[func]:
            function_line += line + ";"

        data_to_send.append(f"{func}:{function_line[:-1]}")

    data_to_send.append(f"RUN:{func_name}")

    pprint(data_to_send)

    with serial.Serial(Config.EspPort, 115200) as ser:
        for line in data_to_send:
            line = line.replace("\n", "") + "\n"  # make sure that there is a newline
            print(" -> " + line.replace("\n", ""))
            ser.write(line.encode())
            time.sleep(0.1)

        while True:
            line = ser.readline().decode().replace("\n", "")
            print(f" <- {line}")


def main_loop():
    pygame.display.set_icon(Images.ICON)
    pygame.display.set_caption("PyKarel 99")
    while Karel.running_gui:
        try:
            Screen.clock.tick(Config.fps_cap)
            Screen.draw_frame()
        except KeyboardInterrupt:
            print("\n\033[01m\n\033[91mExited\033[00m\n")
            Karel.running_gui = False
    quit()


def ask_user():
    print()
    print()
    print("█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█")
    print("█  \033[1m PyKarel99 \033[0m  █")
    print("█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█")
    print()

    if Config.default_file == "":
        print("File name: (Can be without .K99 extension)")
        file_name = input("-> ")
    else:
        file_name = Config.default_file

    if not ".K99" in file_name:
        file_name = file_name + ".K99"

    if not os.path.isfile(file_name):
        print("\033[31mFile does not exist!\033[0m")
        print()
        Karel.running_gui = False
        quit()

    if Karel.running_gui:
        Code.load(file_name)
        if Config.use_KVM:
            KVM.load()

    last_func_name = ""
    while Karel.running_gui:
        if len(last_func_name) > 0:
            print("Function name: (If same, press enter)")
            func_name = input("-> ")
            if len(func_name) == 0:  # if empty
                func_name = last_func_name
            Karel.stop_code = False
        else:
            if Config.default_func == "":
                print("Function name:")
                func_name = input("-> ")
            else:
                func_name = Config.default_func
                Config.default_func = ""
            Karel.stop_code = False

        last_func_name = func_name

        if Config.use_KVM:
            KVM.run_func(func_name)
        elif Config.EspKarelMode:
            handle_esp(func_name)
        else:
            Code.run(func_name)

        print("\033[01m\n\033[91mStopped\033[00m\n")


def main():
    if Config.use_KVM:
        KVM.init()

        Code.load("mainutf8.K99")

        print("\nLoading code and world")

        KVM.save_code()
        KVM.save_map()

        KVM.load()
        KVM.load_world()

        print("\nRunning func")

        KVM.run_func("TEST")

        time.sleep(1)

        quit()

    # handle_args(sys.argv[1:])
    t1 = threading.Thread(target=ask_user, args=())
    t1.start()

    main_loop()


if __name__ == "__main__":
    main()
