from game import *

class Karel:
    x = 0
    y = Game.size - 1 # 19

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
            Karel.x = Game.size -1

        if Karel.y < 0:
            Karel.y = 0
        elif Karel.y > Game.size - 1:
            Karel.y = Game.size -1
    
    def get_pos_in_front():
        if Karel.dir == 0:
            return [Karel.x,     Karel.y - 1]
        
        elif Karel.dir == 1:
            return [Karel.x - 1, Karel.y]
        
        elif Karel.dir == 2:
            return [Karel.x,     Karel.y + 1]
        
        elif Karel.dir == 3:
            return [Karel.x + 1, Karel.y]
    