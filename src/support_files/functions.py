from map import *
from karel import *
from game import *
from flags import *


function_list = ["step"   ,  # Step()
                 "left"   ,  # Turn_left() 
                 "add"    ,  # Add_flag()
                 "remove" ,  # Remove_flag()
                 "wall"   ,  # Is_wall_in_front()
                 "flag"   ,  # Is_flag()
                 "home"   ,  # At_home()
                 "north"  ,  # Facing_north()
                 "south"  ,  # Facing_south()
                 "east"   ,  # Facing_east()
                 "west"   ]  # Facing_west()

class Functions:
    def Step(): # Krok
        if MapStorage.is_wall(Karel.get_pos_in_front()):
            return False
        
        Karel.step()
        return True

    def Turn_left(): # Vlevo-vbok
        Karel.turn_left()
        return True

    def Add_flag(): # Polož
        x = Karel.x
        y = Karel.y
        
        if FlagStorage.flags[x][y] == FlagStorage.max_flag:
            return False

        FlagStorage.flags[x][y] += 1
        MapStorage.map[x][y] = "F"

        return True
    
    def Remove_flag(): # Zvedni
        x = Karel.x
        y = Karel.y
        
        if FlagStorage.flags[x][y] == 0:
            return False
        
        FlagStorage.flags[x][y] -= 1

        if FlagStorage.flags[x][y] == 0:
            MapStorage.map[x][y] = "E"
        
        return True
    
    def Is_wall_in_front(): # Zeď (dokud není zeď)
        return MapStorage.is_wall(Karel.get_pos_in_front())
    
    def Is_flag():
        return (MapStorage.map[Karel.x][Karel.y] == "F")
    
    def At_home():
        return (MapStorage.map[Karel.x][Karel.y] == "H")
    
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
    def _ADMIN_Set_Karel_pos(pos):
        Karel.x = pos[0]
        Karel.y = pos[1]

    def _ADMIN_Set_Karel_dir(direction):
        if direction < 0 or direction > 3:
            return False
        Karel.dir = direction
        return True
    
    def _ADMIN_Set_Karel_home(pos):
        Karel.home_x = pos[0]
        Karel.home_y = pos[1]

    def _ADMIN_Set_Wall(pos):
        MapStorage.map[pos[0]][pos[1]] = "W"
        FlagStorage.flags[pos[0]][pos[1]] = 0

    def _ADMIN_Set_Flag(pos, flag):
        MapStorage.map[pos[0]][pos[1]] = "F"
        FlagStorage.flags[pos[0]][pos[1]] = flag

    def _ADMIN_Set_Empty(pos):
        MapStorage.map[pos[0]][pos[1]] = "E"
        FlagStorage.flags[pos[0]][pos[1]] = 0
