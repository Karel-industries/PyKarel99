#!/bin/python3.10

import ctypes
import pygame
import time
import threading
import os
import platform
from pprint import pprint


class Config:
    size = [49, 49]  # default is 20x20
    screen_size = 800
    interval = 0  # ms
    fps_cap = 30
    flags_are_numbers = False  # True or False
    use_diferent_karel = False  # True or False
    just_use_simple_colors = False  # True or False

    platform = platform.system()

    ignore_out_of_screen = True

    use_KVM = False

    KPU_mode = True
    
    save_translated_file_as_utf8 = False
    default_file = "../../../Kpu/Keap/asembly/KPU"  # Can be without .K99 extension
    default_func = "==BOOT=="
    # default_file = ""   # Can be without .K99 extension
    # default_func = ""


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

    border_width = 2
    borders = []  # (x, y, rot, clr)

    # generate borders:
    def gen_borders():
        for x in range(6):
            Screen.borders.append((x, 0, 0, (255, 0, 0)))
        for x in range(6):
            Screen.borders.append((x, 1, 0, (255, 0, 0)))
        for x in range(6):
            Screen.borders.append((x, 2, 0, (255, 0, 0)))
    
        for x in range(3):
            Screen.borders.append((x+6, 0, 0, (0, 255, 255)))
        Screen.borders.append((6, 0, 1, (0, 255, 255)))
        Screen.borders.append((9, 0, 1, (0, 255, 255)))
    
        for x in range(3):
            Screen.borders.append((x+6, 1, 0, (0, 255, 0)))
        for x in range(3):
            Screen.borders.append((x+6, 2, 0, (0, 255, 0)))
        Screen.borders.append((6, 1, 1, (0, 255, 0)))
        Screen.borders.append((9, 1, 1, (0, 255, 0)))
    
        for x in range(11):
            Screen.borders.append((x+9, 2, 0, (255, 0, 0)))
    
        for y in range(0, 18, 3):
            for x in range(20):
                Screen.borders.append((x, y+5, 0, (255, 0, 0)))
    
        for x in range(21):
            for y in range(0, 18):
                Screen.borders.append((x, y+2, 1, (255, 0, 0)))
    
        for y in range(2):
            Screen.borders.append((0, y, 1, (255, 0, 0)))
        for y in range(2):
            Screen.borders.append((3, y, 1, (255, 0, 0)))
    
        for y in range(2):
            Screen.borders.append((18, y, 1, (0, 0, 0)))
    
        Screen.borders.append((19, 0, 1, (0, 0, 255)))
        Screen.borders.append((20, 0, 1, (0, 0, 255)))
    
        Screen.borders.append((19, 0, 0, (0, 0, 255)))
        Screen.borders.append((19, 1, 0, (0, 0, 255)))
    
        Screen.borders.append((19, 1, 1, (0, 0, 0)))

    def draw_frame():
        global prg_ctr
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Karel.stop_code = True
                if Config.use_KVM:
                    KVM.stop()
                Karel.running_gui = False
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Karel.stop_code = True
                    if Config.use_KVM:
                        KVM.stop()
                    Karel.running_gui = False
                elif event.key == pygame.K_q:
                    Karel.stop_code = True
                    if Config.use_KVM:
                        KVM.stop()

        if Config.use_KVM:
            KVM.update()

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
                                        SimpleColors.FLAGS[int(
                                            MapStorage.map[x][y])][0]
                                        + SimpleColors.HOME[0]
                                    )
                                    / 2
                                ),
                                255,
                            ),
                            min(
                                (
                                    (
                                        SimpleColors.FLAGS[int(
                                            MapStorage.map[x][y])][1]
                                        + SimpleColors.HOME[1]
                                    )
                                    / 2
                                ),
                                255,
                            ),
                            min(
                                (
                                    (
                                        SimpleColors.FLAGS[int(
                                            MapStorage.map[x][y])][2]
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
            for y in range(Config.size[1]):
                for x in range(Config.size[0]):
                    if (x + y) % 2 == 0:
                        color = (180, 180, 180)
                    else:
                        color = (200, 200, 200)

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

            if Config.KPU_mode:
                for x, y, rot, color in Screen.borders:

                    if rot == 0:
                        pygame.draw.rect(
                            Screen.screen,
                            color,
                            (
                                x * Screen.SQUARE_SIZE,
                                y * Screen.SQUARE_SIZE -
                                        (Screen.border_width/2),
                                Screen.SQUARE_SIZE,
                                Screen.border_width,
                            ),
                        )
                    else:
                        pygame.draw.rect(
                            Screen.screen,
                            color,
                            (
                                x * Screen.SQUARE_SIZE -
                                        (Screen.border_width/2),
                                y * Screen.SQUARE_SIZE,
                                Screen.border_width,
                                Screen.SQUARE_SIZE,
                            ),
                        )

            # Draw the grid and squares
            for y in range(Config.size[1]):
                for x in range(Config.size[0]):
                    if MapStorage.map[x][y] == "W":
                        Screen.screen.blit(
                            Images.WALL,
                            (x * Screen.SQUARE_SIZE, y * Screen.SQUARE_SIZE),
                        )

                    elif MapStorage.map[x][y] == "0":
                        pass
                    else:
                        Screen.screen.blit(
                            Images.FLAGS[int(MapStorage.map[x][y])],
                            (x * Screen.SQUARE_SIZE, y * Screen.SQUARE_SIZE),
                        )

            Screen.screen.blit(
                Images.HOME,
                (Karel.home_x * Screen.SQUARE_SIZE,
                 Karel.home_y * Screen.SQUARE_SIZE),
            )
            Screen.screen.blit(
                Images.KAREL[Karel.dir],
                (Karel.x * Screen.SQUARE_SIZE, Karel.y * Screen.SQUARE_SIZE),
            )

        prg_ctr = 0

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
            elif in_code[i].count("//") > 0:
                tmp_line = line[: line.index("//")]
            else:
                tmp_line = line

            if not tmp_line == "" and not tmp_line == "   ":
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
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                Code.commented_code, Code.code = Code.format_code(
                    f.readlines())
        except:
            with open(file_path, "r", encoding="iso_8859_2") as f:
                Code.commented_code, Code.code = Code.format_code(
                    f.readlines())

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

                    function_definition.append(
                        Code.code[o].replace("   ", "", 1))
                Code.function_definitions[function_name] = function_definition


        Code.save_as_utf8(file_path)

        # Load data from code

        map_size_raw = Code.code[start_config_index].replace(
            "Map size: ", "").split(", ")
        map_size = [int(map_size_raw[0]), int(map_size_raw[1])]

        Config.size = map_size

        # Karel pos
        karel_pos_raw = (
            Code.code[start_config_index +
                      1].replace("Karel position: ", "").split(", ")
        )
        Karel.x = int(karel_pos_raw[0]) - 1
        Karel.y = int(karel_pos_raw[1]) - 1

        # Karel home
        karel_home_pos_raw = (
            Code.code[start_config_index +
                      3].replace("Home position: ", "").split(", ")
        )
        Karel.home_x = int(karel_home_pos_raw[0]) - 1
        Karel.home_y = int(karel_home_pos_raw[1]) - 1

        # Karel rot
        rotations = ["NORTH", "WEST", "SOUTH", "EAST"]
        Karel.dir = rotations.index(
            Code.code[start_config_index + 2].replace("Karel rotation: ", "").replace(" ", "")
        )

        # Map
        tmp_map = []
        for i in range(Config.size[1]):
            tmp_map.append(list(Code.code[start_config_index + 5 + i]))

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
            line = func_list[index].replace("   ", "")
            if line.startswith("STEP"):
                Functions.Step()
                if not Config.interval == 0:
                    time.sleep(Config.interval / 1000)
            elif line.startswith("LEFT"):
                Functions.Turn_left()
                if not Config.interval == 0:
                    time.sleep(Config.interval / 1000)
            elif line.startswith("PICK"):
                Functions.Pick_flag()
                if not Config.interval == 0:
                    time.sleep(Config.interval / 1000)
            elif line.startswith("PLACE"):
                Functions.Place_flag()
                if not Config.interval == 0:
                    time.sleep(Config.interval / 1000)
            elif line.startswith("UNTIL"):
                tab_count = func_list[0].count("   ")
                tmp_index = int(index + 1)
                tmp_code = []
                conditions = line.replace("UNTIL ", "").split(" ")
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

            elif line.startswith("IF IS"):
                tab_count = func_list[0].count("   ")
                tmp_index = int(index + 1)
                if_tmp_code = []
                else_tmp_code = []
                conditions = line.replace("IF ", "").split(" ")
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

            elif line.startswith("REPEAT"):
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
                        line
                        .replace("REPEAT", "")
                        .replace("-TIMES", "")
                    )
                ):
                    if Karel.stop_code == True:
                        return
                    Code.run_func_list(tmp_code)

            elif line.startswith("PRINT"):
                print(line.replace("PRINT ", ""))
            elif line.startswith("END"):  # just to be safe, but not used (hopefully)
                pass
            else:
                try:
                    Code.run_func_list(
                        Code.function_definitions[line]
                    )  # recursive
                except KeyError:
                    pass  # missing funcs are interpreted as no-ops

            index += 1


class KVM:
    lib = None

    # used to stop updating PyKarels map with Kvms map when loading a new map into Kvm
    update_freeze = True

    def init():
        print("\nLoading KVM")
        if Config.platform == "Windows":
            os.system(
                "cd KVM && git submodule update --init --remote --rebase && cd KVM && zig build -Doptimize=ReleaseFast && echo ' '"
            )
            KVM.lib = ctypes.CDLL("KVM/KVM/zig-out/lib/Kvm.dll")
        elif Config.platform == "Linux":
            #print("LINUX")
            os.system(
                "cd KVM && git submodule update --init --remote --rebase && cd KVM && zig build -Doptimize=ReleaseFast"
            )
            KVM.lib = ctypes.CDLL("KVM/KVM/zig-out/lib/libKvm.so")
        elif Config.platform == "Darwin":  # aka MacOS
            print("Don't care about MacOS\n F*** you!")
            return
        else:
            print("Fuck")
            return

        KVM.lib.init()

    def deinit():
        if Config.use_KVM:
            KVM.lib.deinit()

    def load():
        src = ""

        for line in Code.code:
            if "Map size" in line:
                break
            src += line + '\n'

        KVM.lib.load(src.encode("utf-8"))

    def load_world():
        map_buffer_type = ctypes.c_ubyte * (Config.size[0] * Config.size[1])
        map_buffer = map_buffer_type()

        i = 0
        # KVM has a flipped y axis compared to PyKarel
        for y in range(Config.size[1] - 1, -1, -1):
            for x in range(Config.size[0]):
                map_buffer[i] = 255 if MapStorage.map[x][y] == "W" else int(
                    MapStorage.map[x][y])
                i += 1

        karel_buffer_type = ctypes.c_uint * 5
        karel_buffer = karel_buffer_type(
            Karel.x, Config.size[1] - 1 - Karel.y, Karel.dir, Karel.home_x, Config.size[1] - 1 - Karel.home_y)  # y axis flip

        KVM.lib.load_world(ctypes.pointer(map_buffer),
                           ctypes.pointer(karel_buffer))

    def update():
        if KVM.update_freeze:
            return

        # a little ctypes shenanigans to read world data from KVM
        map_buffer_type = ctypes.c_ubyte * (Config.size[0] * Config.size[1])
        map_buffer = map_buffer_type()

        karel_buffer_type = ctypes.c_uint * 5
        karel_buffer = karel_buffer_type()

        KVM.lib.read_world(ctypes.pointer(map_buffer),
                           ctypes.pointer(karel_buffer))

        i = 0
        # KVM has a flipped y axis compared to PyKarel
        for y in range(Config.size[1] - 1, -1, -1):
            for x in range(Config.size[0]):
                if not map_buffer[i] == 255:
                    MapStorage.map[x][y] = str(map_buffer[i])
                else:
                    MapStorage.map[x][y] = str("W")
                i += 1

        Karel.x = int(karel_buffer[0])
        Karel.y = int(Config.size[1] - 1 - karel_buffer[1])  # y axis flip

        Karel.dir = int(karel_buffer[2])

    def stop():
        KVM.lib.short_circuit()

    def run_func(func_name):
        KVM.lib.run_symbol(func_name.encode("utf-8"))


class Images:
    ICON = pygame.image.load("assets/icon.png")

    WALL = pygame.transform.scale(
        pygame.image.load(
            "assets/wall.png"), (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE)
    )

    HOME = pygame.transform.scale(
        pygame.image.load(
            "assets/home.png"), (Screen.SQUARE_SIZE, Screen.SQUARE_SIZE)
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
}


def quit():
    KVM.deinit()
    pygame.quit()
    exit()


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
        file_name = f"{file_name}.K99"
    if not "scripts/" in file_name:
        file_name = f"scripts/{file_name}"

    if not os.path.isfile(file_name):
        print("\033[31mFile does not exist!\033[0m")
        print()
        Karel.running_gui = False
        quit()

    if Karel.running_gui:
        Code.load(file_name)
        if Config.use_KVM:
            KVM.load_world()
            KVM.update_freeze = False

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
            if Karel.running_gui:
                KVM.run_func(func_name)
        else:
            Code.run(func_name)

        print("\033[01m\n\033[91mStopped\033[00m\n")


def main():
    if Config.use_KVM:
        KVM.init()

    Screen.gen_borders()

    # handle_args(sys.argv[1:])
    t1 = threading.Thread(target=ask_user, args=())
    t1.start()

    main_loop()


if __name__ == "__main__":
    main()