from game import *
from karel import *

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

