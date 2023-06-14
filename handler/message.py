import handler.socket_handler as socket_handler

def online (token, client_socket, content):
    """
    Comprueba la autenticación, ejecuta módulos o actualiza módulos en función de la 'content' proporcionada.
    La función cierra el socket cliente al final de la ejecución.

    Argumentos:
        token (str): El token de autorización esperado para la autenticación.
        client_socket (socket): El socket del cliente con el que se establece la conexión.
        content (str): La instrucción que se debe ejecutar. Debe ser 'Hello' para la autenticación,
                       'exec_modules' para la ejecución de módulos o 'update_modules' para la actualización de módulos.

    Devuelve:
        bool: True si la instrucción se ejecutó con éxito y False en caso contrario o si el socket del cliente no está presente.
    """
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

