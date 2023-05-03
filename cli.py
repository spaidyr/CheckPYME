import handler.socket_handler as socket_handler

def main():
    while True:
        print("\nMenú de opciones:")
        print("1. Listar clientes conectados")
        print("2. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            listar_clientes()
        elif opcion == "2":
            if confirmar_salida():
                socket_handler.stop_server()
                break
        else:
            print("Opción no válida. Intente nuevamente.")

def listar_clientes():
    online_clients = socket_handler.listar_clientes()
    for token, client_data in online_clients.items():
        online_status = "En línea" if client_data['online'] else "Desconectado"
        print(f"{token}: {client_data['hostname']} ({client_data['address'][0]}) - {online_status}")

def confirmar_salida():
    while True:
        confirmacion = input("¿Está seguro de que desea apagar el servidor? (s/n): ").lower()
        if confirmacion == "s":
            return True
        elif confirmacion == "n":
            return False
        else:
            print("Respuesta no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()