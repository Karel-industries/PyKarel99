import sys
sys.path.append('support_files')

from support_files.map import *
from support_files.karel import *
from support_files.game import *
from support_files.flags import *
from support_files.functions import *

import pygame
import socket
import threading
import os
import time

exit_event = threading.Event()

class Screen:
    size = 600
    square_size = size/Game.size
    screen = pygame.display.set_mode((size, size))

class Images:
    wall = pygame.transform.scale(pygame.image.load("assets/wall.png"), (Screen.square_size, Screen.square_size))
    
    home = pygame.transform.scale(pygame.image.load("assets/home.png"), (Screen.square_size, Screen.square_size))
    
    karel = [pygame.transform.scale(pygame.image.load("assets/karel-0.png"), (Screen.square_size, Screen.square_size)),
             pygame.transform.scale(pygame.image.load("assets/karel-1.png"), (Screen.square_size, Screen.square_size)),
             pygame.transform.scale(pygame.image.load("assets/karel-2.png"), (Screen.square_size, Screen.square_size)),
             pygame.transform.scale(pygame.image.load("assets/karel-3.png"), (Screen.square_size, Screen.square_size))]
    
    flags = [pygame.transform.scale(pygame.image.load("assets/flag-1.png"), (Screen.square_size, Screen.square_size)),
            pygame.transform.scale(pygame.image.load("assets/flag-2.png"), (Screen.square_size, Screen.square_size)),
            pygame.transform.scale(pygame.image.load("assets/flag-3.png"), (Screen.square_size, Screen.square_size)),
            pygame.transform.scale(pygame.image.load("assets/flag-4.png"), (Screen.square_size, Screen.square_size)),
            pygame.transform.scale(pygame.image.load("assets/flag-5.png"), (Screen.square_size, Screen.square_size)),
            pygame.transform.scale(pygame.image.load("assets/flag-6.png"), (Screen.square_size, Screen.square_size)),
            pygame.transform.scale(pygame.image.load("assets/flag-7.png"), (Screen.square_size, Screen.square_size)),
            pygame.transform.scale(pygame.image.load("assets/flag-8.png"), (Screen.square_size, Screen.square_size))]

FlagStorage.init()
MapStorage.init()

# pygame.display.set_caption("Karel 99")


def main_loop():
    while Game.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game.running = False
                
                      
        # Clear the screen
        Screen.screen.fill((0, 0, 0))

        # Draw the grid and squares
        for y in range(Game.size):
            for x in range(Game.size):
                x_pos = x * Screen.square_size
                y_pos = y * Screen.square_size

                if MapStorage.map[x][y] == "W":
                    Screen.screen.blit(Images.wall, (x_pos, y_pos))
                else:
                    if (x + y) % 2 == 0:
                        color = (180, 180, 180)
                    else:
                        color = (200, 200, 200)
                    pygame.draw.rect(Screen.screen, color, (x_pos, y_pos, Screen.square_size, Screen.square_size))

                    if MapStorage.map[x][y] == "F":
                        Screen.screen.blit(Images.flags[FlagStorage.flags[x][y] - 1], (x_pos, y_pos))
                
        Screen.screen.blit(Images.home, (Karel.home_x * Screen.square_size, Karel.home_y * Screen.square_size))
        Screen.screen.blit(Images.karel[Karel.dir], (Karel.x * Screen.square_size, Karel.y * Screen.square_size))


        pygame.display.flip()
    pygame.quit()
    exit_event.set()
    
    
def handle_socket(data):
    if not data in function_list:
        return "error"
    
    if data == "step":
        return "ok" if      Functions.Step()             else "error"
    
    elif data == "left":
        return "ok" if      Functions.Turn_left()        else "error"
    
    elif data == "add":
        return "ok" if      Functions.Add_flag()         else "error"
    
    elif data == "remove":
        return "ok" if      Functions.Remove_flag()      else "error"
    
    elif data == "wall":
        return "yes" if     Functions.Is_wall_in_front() else "no"
    
    elif data == "flag":
        return "yes" if     Functions.Is_flag()          else "no"
    
    elif data == "home":
        return "yes" if     Functions.At_home()          else "no"
    
    elif data == "north":
        return "yes" if     Functions.Facing_north()     else "no"
    
    elif data == "south":
        return "yes" if     Functions.Facing_south()     else "no"
    
    elif data == "east":
        return "yes" if     Functions.Facing_east()      else "no"
    
    elif data == "west":
        return "yes" if     Functions.Facing_west()      else "no"




def socket_loop():
    while not exit_event.is_set():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        host = 'localhost'
        port = 12345
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Server listening on {host}:{port}")

        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")

        while not exit_event.is_set():
            data = conn.recv(1024).decode()
            if not data:
                break
            conn.send(handle_socket(data).encode())

        conn.close()
        server_socket.close()




# Create and start the socket handler thread
socket_thread = threading.Thread(target=socket_loop)
socket_thread.start()

main_loop()

socket_thread.join()