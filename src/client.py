import socket

# Client setup
host = 'localhost'
port = 12345

cmds_dict = {   "w":"step"  ,
                "a":"left"  ,
                "e":"add"   ,
                "q":"remove",
                "d":"home"  ,
                "f":"flag"  ,
                "r":"wall"  ,
                "y":"north" ,
                "x":"south" ,
                "c":"east"  ,
                "v":"west"  ,}

last_responce = ""

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((host, port))

    while True:
        try:
            key = input(f"\n\nStep:          w\nTurn_left:     a\nAdd_flag:      e\nRemove_flag:   q\nIs_flag:       f\nIs_wall:       r\nAt_home:       d\nFacing_north:  y\nFacing_south:  x\nFacing_east:   c\nFacing_west:   v\n\nresponce: {last_responce}   -> ")
            cmd = cmds_dict[key]

            client_socket.sendall(cmd.encode())

            response = client_socket.recv(1024).decode()

            last_responce = response
        except KeyboardInterrupt:
            exit()
        except KeyError:
            pass
