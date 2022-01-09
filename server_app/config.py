class Config:
    server_ip = '127.0.0.1'
    server_port = 3389
    server_address = server_ip + ':' + str(server_port)
    server_listen = 5
    room_listen = 10
    colors = ((0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
              (0, 255, 255), (255, 255, 255), (125, 125, 125), (125, 0, 255))
    task_per_player = 5
