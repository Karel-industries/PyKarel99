import socket

# Client setup
host = 'localhost'
port = 12345

cmd = ""
should_send = False

last_responce = ""

# for code file
code = ""

def send_cmd(_cmd):
    global cmd, should_send
    cmd = _cmd
    should_send = True

def load_file(_file_name):
    global code
    with open(_file_name, "r") as f:
        _code = f.read()

    _cmds = _code.split("\n")
    cmds = []

    # remove comments
    for _cmd in _cmds:
        if not _cmd.startswith(";"):
            cmds.append(_cmd)
    
    #_cmds = list(cmds)

    for _cmd in _cmds:
        if _cmd.startswith("Definice města:"):
            index = _cmds.index(_cmd)
            for _row in range(20):
                row = _cmds[index+1+_row]
                if row == "\n":
                    break
                cols = row.split()

                print(cols)

            #send_cmd(f"set_size;{map_size[0]};{map_size[1]}")



    print("\n".join(_cmds))

cmds_dict = {   "step"         : "send_cmd('step')"         ,
                "turn-left"    : "send_cmd('turn-left')"    ,
                "add-flag"     : "send_cmd('add-flag')"     ,
                "remove-flag"  : "send_cmd('remove-flag')"  ,
                "at-home"      : "send_cmd('at-home')"      ,
                "is-flag"      : "send_cmd('is-flag')"      ,
                "is-wall"      : "send_cmd('is-wall')"      ,
                "facing-north" : "send_cmd('facing-north')" ,
                "facing-south" : "send_cmd('facing-south')" ,
                "facing-east"  : "send_cmd('facing-east')"  ,
                "facing-west"  : "send_cmd('facing-west')"  ,
                "load-file"    : "load_file('test.K99')"    ,
                }


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    client_socket.connect((host, port))
    while True:
        key = input("\n".join(list(cmds_dict.keys())) + f"\n\nresponce: {last_responce} -> ")
        eval(cmds_dict[key])
        if(should_send):
            should_send = False
            try:
                client_socket.sendall(cmd.encode())

                response = client_socket.recv(1024).decode()

                last_responce = response
            except KeyboardInterrupt:
                exit()
            except KeyError:
                pass
