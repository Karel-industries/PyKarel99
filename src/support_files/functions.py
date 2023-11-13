from map import *
from karel import *
from game import *

class Functions:
    def Step(): # Krok
        if MapStorage.is_wall(Karel.get_pos_in_front()):
            return False
        
        Karel.step()
        return True

    def Turn_left(): # Vlevo-vbok
        Karel.turn_left()
        return True

    def Place_flag(): # Polož
        x = Karel.x
        y = Karel.y
        
        if MapStorage.map[x][y] == MapStorage.max_flag:
            return False
        MapStorage.map[x][y] = str(int(MapStorage.map[x][y]) + 1)

        return True
    
    def Pick_flag(): # Zvedni
        x = Karel.x
        y = Karel.y
        
        if MapStorage.map[x][y] == "0":
            return False
        
        MapStorage.map[x][y] = str(int(MapStorage.map[x][y]) - 1)
        
        return True
    
    def Is_wall_in_front(): # Zeď (dokud není zeď)
        return MapStorage.is_wall(Karel.get_pos_in_front())
    
    def Is_flag():
        return (not MapStorage.map[Karel.x][Karel.y] in ["0", "W"])
    
    def At_home():
        return (Karel.home_x == Karel.x and Karel.home_y == Karel.y)
    
    def Facing_north():
        return (Karel.dir == 0)
    
    def Facing_south():
        return (Karel.dir == 2)
    
    def Facing_east():
        return (Karel.dir == 3)
    
    def Facing_west():
        return (Karel.dir == 1)
    


    ########################
    # Just for Admin panel #
    ########################
    def ADMIN_Set_Karel_pos(pos):
        Karel.x = int(pos[0])
        Karel.y = int(pos[1])

    def ADMIN_Set_Karel_dir(direction):
        if direction < 0 or direction > 3:
            return False
        Karel.dir = direction
        return True
    
    def ADMIN_Set_Karel_home(pos):
        Karel.home_x = pos[0]
        Karel.home_y = pos[1]

    def ADMIN_Set_Wall(pos):
        MapStorage.map[pos[0]][pos[1]] = "W"

    def ADMIN_Set_Flag(pos, flag):
        MapStorage.map[pos[0]][pos[1]] = str(flag)

    def ADMIN_Set_Empty(pos):
        MapStorage.map[pos[0]][pos[1]] = "0"
