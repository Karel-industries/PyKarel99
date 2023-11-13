import sys

sys.path.append("support_files")
from support_files.map import *
from support_files.karel import *
from support_files.game import *
from support_files.functions import *
import pygame
from pprint import pprint
import time

flags_are_numbers = True

code = []

code_function_definitions = {}  # The commands under the function


class Screen:
    size = 800
    square_size = size / Game.size
    screen = pygame.display.set_mode((size, size))


class Images:
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


MapStorage.init()

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
            Game.running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
            elif event.key == pygame.K_w:
                Functions.Step()
            elif event.key == pygame.K_a:
                Functions.Turn_left()
            elif event.key == pygame.K_q:
                Functions.Pick_flag()
            elif event.key == pygame.K_e:
                Functions.Place_flag()
            elif event.key == pygame.K_r:
                print(Functions.Is_flag())
            elif event.key == pygame.K_f:
                print(Functions.Is_wall_in_front())
            elif event.key == pygame.K_l:
                handle_code("test.K99")
    # Clear the screen
    Screen.screen.fill((0, 0, 0))

    # Draw the grid and squares
    for y in range(Game.size):
        for x in range(Game.size):
            x_pos = x * Screen.square_size
            y_pos = y * Screen.square_size

            if MapStorage.map[x][y] == "W":
                Screen.screen.blit(Images.wall, (x_pos, y_pos))

            elif MapStorage.map[x][y] == "0":
                if (x + y) % 2 == 0:
                    color = (180, 180, 180)
                else:
                    color = (200, 200, 200)
                pygame.draw.rect(
                    Screen.screen,
                    color,
                    (x_pos, y_pos, Screen.square_size, Screen.square_size),
                )
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


def load_code(file_path):
    global code
    with open(file_path) as f:
        raw_file = f.readlines()

    uncomented_file = []
    for i in range(len(raw_file)):
        if not raw_file[i].startswith(";") and not raw_file[i] == "\n":
            uncomented_file.append(str(raw_file[i]))

    unnewlined_file = []
    for line in uncomented_file:
        unnewlined_file.append(str(line.replace("\n", "").replace("\t", "")))
    raw_code = unnewlined_file

    translated_code = []
    for line in raw_code:
        translated_code.append(
            line.replace("KROK", "STEP")
            .replace("VLEVO-VBOK", "LEFT")
            .replace("ZVEDNI", "PICK")
            .replace("POLOŽ", "PLACE")
            .replace("OPAKUJ", "REPEAT")
            .replace("KRÁT", "TIMES")
            .replace("DOKUD", "UNTIL")
            .replace("POKUD", "IF")
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
            function_name = translated_code[i][: translated_code[i].index(";")]
            function_definition = []
            for o in range(i + 1, start_config_index):
                if translated_code[o].startswith("END"):
                    break

                function_definition.append(translated_code[o])

            code_function_definitions[function_name] = function_definition

    code = translated_code
    # pprint(code)


def load_data_from_code():
    global code_functions, code_function_definitions, code
    first_index = 0
    for line in code:
        if line.startswith("Velikost města"):
            first_index = int(code.index(line))
            break

    map_size_raw = code[first_index].replace("Velikost města: ", "").split(", ")
    map_size = [int(map_size_raw[0]), int(map_size_raw[1])]
    # pprint(map_size)

    karel_pos_raw = code[first_index + 1].replace("Pozice Karla: ", "").split(", ")
    karel_pos = [int(karel_pos_raw[0]) - 1, int(karel_pos_raw[1]) - 1]
    Functions.ADMIN_Set_Karel_pos(karel_pos)
    # pprint(karel_pos)

    rotations = ["NORTH", "WEST", "SOUTH", "EAST"]
    karel_rotation = rotations.index(
        code[first_index + 2].replace("Otočení Karla: ", "")
    )
    Functions.ADMIN_Set_Karel_dir(karel_rotation)
    # pprint(karel_rotation)

    karel_home_pos_raw = code[first_index + 1].replace("Pozice Karla: ", "").split(", ")
    karel_home_pos = [int(karel_home_pos_raw[0]) - 1, int(karel_home_pos_raw[1]) - 1]
    Functions.ADMIN_Set_Karel_home(karel_home_pos)
    # pprint(karel_home_pos)

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
    tab_count = func_list[0].count("   ")
    # pprint(func_list)

    # print(tab_count)

    while index < len(func_list):
        line = func_list[index]
        print(line)
        if "STEP" in line:
            Functions.Step()
            draw_frame()
            time.sleep(0.5)
        elif "LEFT" in line:
            Functions.Turn_left()
            draw_frame()
            time.sleep(0.5)
        elif "PICK" in line:
            Functions.Pick_flag()
            draw_frame()
            time.sleep(0.5)
        elif "PLACE" in line:
            Functions.Place_flag()
            draw_frame()
            time.sleep(0.5)
        elif "UNTIL" in line:
            tmp_index = int(index + 1)
            tmp_code = []
            while True:
                if func_list[tmp_index] == str(str("   " * tab_count) + "END"):
                    break
                else:
                    tmp_code.append(func_list[tmp_index])
                tmp_index += 1
            index = tmp_index
            conditions = line.replace("   ", "").replace("UNTIL ", "").split(" ")
            if conditions[0] == "IS":
                while if_list[conditions[1]]():
                    run_function(tmp_code)
            elif conditions[0] == "ISNOT":
                while not if_list[conditions[1]]():
                    run_function(tmp_code)

        elif "IF" in line:
            # dont care for now
            pass

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
            for _ in range(int(line.replace("   ", "").replace("REPEAT", "").replace("-TIMES", ""))):
                run_function(tmp_code)

        elif "END" in line: # just to be safe, but not used (hopefully)
            pass
        else:
            run_function(
                code_function_definitions[line.replace("   ", "")]
            )  # recursive

        index += 1
        
        


def handle_code(file_path):
    load_code(file_path)
    load_data_from_code()
    # pprint(code_function_definitions)
    run_function(code_function_definitions["TEST"])


main_loop()
