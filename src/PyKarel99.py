import pygame
import time
import threading
import os
from pprint import pprint

## CONFIG ##

flags_are_numbers = False  # True or False
interval = 250  # ms

## END OF CONFIG ##


class Game:
    size = 20
    running = True
    stop_code = False


class Karel:
    x = 0
    y = Game.size - 1  # 19

    home_x = 0
    home_y = Game.size - 1

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
        if Karel.dir == 0:
            Karel.y -= 1
        elif Karel.dir == 1:
            Karel.x -= 1
        elif Karel.dir == 2:
            Karel.y += 1
        elif Karel.dir == 3:
            Karel.x += 1

        if Karel.x < 0:
            Karel.x = 0
        elif Karel.x > Game.size - 1:
            Karel.x = Game.size - 1

        if Karel.y < 0:
            Karel.y = 0
        elif Karel.y > Game.size - 1:
            Karel.y = Game.size - 1

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
    size = Game.size
    max_flag = 8

    map = []
    # E = Empty
    # W = wall

    def init():
        for i in range(MapStorage.size):
            # Create a new row as a list
            row = []
            for j in range(MapStorage.size):
                # Append numbers to the row (you can use any values here)
                row.append("0")
            # Append the row to the array
            MapStorage.map.append(list(row))

    def valid_pos(pos):
        if pos[0] < 0 or pos[0] > Game.size - 1:
            return False
        if pos[1] < 0 or pos[1] > Game.size - 1:
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
    def Step():  # Krok
        if MapStorage.is_wall(Karel.get_pos_in_front()):
            return False

        Karel.step()
        return True

    def Turn_left():  # Vlevo-vbok
        Karel.turn_left()
        return True

    def Place_flag():  # Polož
        x = Karel.x
        y = Karel.y

        if MapStorage.map[x][y] == MapStorage.max_flag:
            return False
        MapStorage.map[x][y] = str(int(MapStorage.map[x][y]) + 1)

        return True

    def Pick_flag():  # Zvedni
        x = Karel.x
        y = Karel.y

        if MapStorage.map[x][y] == "0":
            return False

        MapStorage.map[x][y] = str(int(MapStorage.map[x][y]) - 1)

        return True

    def Is_wall_in_front():  # Zeď (dokud není zeď)
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
    size = 800
    square_size = size / Game.size
    screen = pygame.display.set_mode((size, size))


class Images:
    icon = pygame.image.load("assets/icon.png")

    wall = pygame.transform.scale(
        pygame.image.load("assets/wall.png"), (Screen.square_size, Screen.square_size)
    )

    home = pygame.transform.scale(
        pygame.image.load("assets/home.png"), (Screen.square_size, Screen.square_size)
    )

    karel = [
        pygame.transform.scale(
            pygame.image.load("assets/karel-0.png"),
            (Screen.square_size, Screen.square_size),
        ),
        pygame.transform.scale(
            pygame.image.load("assets/karel-1.png"),
            (Screen.square_size, Screen.square_size),
        ),
        pygame.transform.scale(
            pygame.image.load("assets/karel-2.png"),
            (Screen.square_size, Screen.square_size),
        ),
        pygame.transform.scale(
            pygame.image.load("assets/karel-3.png"),
            (Screen.square_size, Screen.square_size),
        ),
    ]

    if flags_are_numbers:
        flags = [
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-0.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-1.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-2.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-3.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-4.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-5.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-6.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-7.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/number-flags/flag-8.png"),
                (Screen.square_size, Screen.square_size),
            ),
        ]
    else:
        flags = [
            pygame.transform.scale(
                pygame.image.load("assets/flag-0.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-1.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-2.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-3.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-4.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-5.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-6.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-7.png"),
                (Screen.square_size, Screen.square_size),
            ),
            pygame.transform.scale(
                pygame.image.load("assets/flag-8.png"),
                (Screen.square_size, Screen.square_size),
            ),
        ]


code = []

code_function_definitions = {}  # The commands under the function

MapStorage.init()


pygame.display.set_icon(Images.icon)
pygame.display.set_caption("PyKarel 99")

if_list = {
    "WALL": Functions.Is_wall_in_front,
    "FLAG": Functions.Is_flag,
    "HOME": Functions.At_home,
    "NORTH": Functions.Facing_north,
    "SOUTH": Functions.Facing_south,
    "EAST": Functions.Facing_east,
    "WEST": Functions.Facing_west,
}


def draw_frame():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Game.stop_code = True
            Game.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                Game.stop_code = True
                Game.running = False
            elif event.key == pygame.K_q:
                Game.stop_code = True
                Game.running = False
    # Clear the screen
    Screen.screen.fill((200, 200, 200))

    # Draw the grid and squares
    for y in range(Game.size):
        for x in range(Game.size):
            x_pos = x * Screen.square_size
            y_pos = y * Screen.square_size

            if (x + y) % 2 == 0:
                color = (180, 180, 180)
            else:
                color = (200, 200, 200)
            pygame.draw.rect(
                Screen.screen,
                color,
                (x_pos, y_pos, Screen.square_size, Screen.square_size),
            )

            if MapStorage.map[x][y] == "W":
                Screen.screen.blit(Images.wall, (x_pos, y_pos))

            elif MapStorage.map[x][y] == "0":
                pass # dont render anything
            else:
                Screen.screen.blit(
                    Images.flags[int(MapStorage.map[x][y])], (x_pos, y_pos)
                )

    Screen.screen.blit(
        Images.home,
        (Karel.home_x * Screen.square_size, Karel.home_y * Screen.square_size),
    )
    Screen.screen.blit(
        Images.karel[Karel.dir],
        (Karel.x * Screen.square_size, Karel.y * Screen.square_size),
    )

    pygame.display.flip()


def main_loop():
    while Game.running:
        draw_frame()
    pygame.quit()
    exit()


def load_code(file_path):
    global code
    with open(file_path, "r") as f:
        raw_file = f.readlines()

    uncomented_file = []
    for i in range(len(raw_file)):
        if not raw_file[i].startswith(";") and not raw_file[i] == "\n":
            uncomented_file.append(str(raw_file[i]))

    unnewlined_file = []
    for line in uncomented_file:
        unnewlined_file.append(str(line.replace("\n", "").replace("\t", "")))

    translated_code = []
    for line in unnewlined_file:
        translated_code.append(
            line.replace("KROK", "STEP")
            .replace("VLEVO-VBOK", "LEFT")
            .replace("ZVEDNI", "PICK")
            .replace("POLOŽ", "PLACE")
            .replace("OPAKUJ", "REPEAT")
            .replace("KRÁT", "TIMES")
            .replace("DOKUD", "UNTIL")
            .replace("KDYŽ", "IF")
            .replace("JINAK", "ELSE")
            .replace("JE", "IS")
            .replace("NENÍ", "ISNOT")
            .replace("ZEĎ", "WALL")
            .replace("ZNAČKA", "FLAG")
            .replace("DOMOV", "HOME")
            .replace("SEVER", "NORTH")
            .replace("JIH", "SOUTH")
            .replace("ZÁPAD", "WEST")
            .replace("VÝCHOD", "EAST")
            .replace("KONEC", "END")
        )

    for index, string in enumerate(translated_code):
        if "Velikost města" in string:
            start_config_index = index
            break

    for i in range(start_config_index):
        line = translated_code[i]
        is_new = True
        if line.startswith("   ") or line.startswith("END"):
            is_new = False

        if is_new:
            if ";" in translated_code[i]:
                function_name = translated_code[i][: translated_code[i].index(";")]
            else:
                function_name = translated_code[i]
            function_definition = []
            for o in range(i + 1, start_config_index):
                if translated_code[o].startswith("END"):
                    break

                function_definition.append(translated_code[o])

            code_function_definitions[function_name] = function_definition

    code = translated_code
    # pprint(code)


def load_data_from_code():
    global code_function_definitions, code
    first_index = 0
    for line in code:
        if line.startswith("Velikost města"):
            first_index = int(code.index(line))
            break

    map_size_raw = code[first_index].replace("Velikost města: ", "").split(", ")
    map_size = [int(map_size_raw[0]), int(map_size_raw[1])]

    karel_pos_raw = code[first_index + 1].replace("Pozice Karla: ", "").split(", ")
    Karel.x = int(karel_pos_raw[0]) - 1
    Karel.y = int(karel_pos_raw[1]) - 1

    karel_home_pos_raw = (
        code[first_index + 3].replace("Umístění domova: ", "").split(", ")
    )
    Karel.home_x = int(karel_home_pos_raw[0]) - 1
    Karel.home_y = int(karel_home_pos_raw[1]) - 1

    rotations = ["NORTH", "WEST", "SOUTH", "EAST"]
    Karel.dir = rotations.index(code[first_index + 2].replace("Otočení Karla: ", ""))

    tmp_map = []
    for i in range(map_size[1]):
        "".split()
        tmp_map.append(list(code[first_index + 5 + i]))

    for y in range(Game.size):
        for x in range(Game.size):
            if x < map_size[0] and y < map_size[1]:
                if tmp_map[y][x] == ".":
                    MapStorage.map[x][y] = "0"
                elif tmp_map[y][x] == "X":
                    MapStorage.map[x][y] = "W"
                elif tmp_map[y][x] in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    MapStorage.map[x][y] = tmp_map[y][x]
            else:
                MapStorage.map[x][y] = "W"  # if the map is smaller, put walls


def run_function(func_list):
    index = 0
    if len(func_list) == 0:
        return
    tab_count = func_list[0].count("   ")
    while index < len(func_list):
        if Game.stop_code == True:
            break
        line = func_list[index]
        if "STEP" in line:
            Functions.Step()
            draw_frame()
            time.sleep(interval / 1000)
        elif "LEFT" in line:
            Functions.Turn_left()
            draw_frame()
            time.sleep(interval / 1000)
        elif "PICK" in line:
            Functions.Pick_flag()
            draw_frame()
            time.sleep(interval / 1000)
        elif "PLACE" in line:
            Functions.Place_flag()
            draw_frame()
            time.sleep(interval / 1000)
        elif "UNTIL" in line:
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
                while if_list[conditions[1]]():
                    run_function(tmp_code)
            elif conditions[0] == "ISNOT":
                while not if_list[conditions[1]]():
                    run_function(tmp_code)

        elif "IF IS" in line:
            tmp_index = int(index + 1)
            if_tmp_code = []
            else_tmp_code = []
            conditions = line.replace("   ", "").replace("IF ", "").split(" ")
            while True:
                if func_list[tmp_index] == str(str("   " * tab_count) + "END, ELSE"):
                    break
                else:
                    if_tmp_code.append(func_list[tmp_index])
                tmp_index += 1
            while True:
                if func_list[tmp_index] == str(str("   " * tab_count) + "END"):
                    break
                else:
                    else_tmp_code.append(func_list[tmp_index])
                tmp_index += 1
            index = tmp_index

            if len(if_tmp_code) == 0:
                continue
            if len(else_tmp_code) == 0:
                continue

            if conditions[0] == "IS":
                if if_list[conditions[1]]():
                    run_function(if_tmp_code)
                else:
                    run_function(else_tmp_code)
            elif conditions[0] == "ISNOT":
                if not if_list[conditions[1]]():
                    run_function(if_tmp_code)
                else:
                    run_function(else_tmp_code)

        elif "REPEAT" in line:
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
                int(line.replace("   ", "").replace("REPEAT", "").replace("-TIMES", ""))
            ):
                run_function(tmp_code)

        elif "END" in line:  # just to be safe, but not used (hopefully)
            pass
        else:
            run_function(
                code_function_definitions[line.replace("   ", "")]
            )  # recursive

        index += 1


def pre_load_code(file_path):
    if Game.running:
        Game.stop_code = False
        load_code(file_path)
        load_data_from_code()


def run_code(func_name):
    if Game.running:
        Game.stop_code = False
        if not func_name in code_function_definitions.keys():
            print("\033[31mWrong func name: " + func_name + "\033[0m")
            return
    
        print("\033[32mRunning\033[0m " + func_name + "\n")
        run_function(code_function_definitions[func_name])


def ask_user():
    print()
    print()
    print("█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█")
    print("█  \033[1m PyKarel99 \033[0m  █")
    print("█▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█")
    print()
    print("File name:")
    file_name = input("-> ")
    if not os.path.isfile(file_name):
        print("\033[31mFile does not exist!\033[0m")
        print()
        Game.stop_code = True
        Game.running = False
        exit()

    if Game.running:
        pre_load_code(file_name)

    last_func_name = ""
    while Game.running:
        if len(last_func_name) > 0:
            print("Function name: (If same, press enter)")
            func_name = input("-> ")
            if len(func_name) == 0:  # if empty
                func_name = last_func_name
        else:
            print("Function name:")
            func_name = input("-> ")
        last_func_name = func_name

        if Game.running:
            run_code(func_name)


t1 = threading.Thread(target=ask_user, args=())
t1.start()

main_loop()
