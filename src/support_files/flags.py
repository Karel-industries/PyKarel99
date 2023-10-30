from game import *

class FlagStorage:
    size = Game.size
    max_flag = 8
    flags = []

    def init():
        for i in range(FlagStorage.size):
            # Create a new row as a list
            row = []
            for j in range(FlagStorage.size):
                # Append numbers to the row (you can use any values here)
                row.append(0)
            # Append the row to the array
            FlagStorage.flags.append(list(row))

