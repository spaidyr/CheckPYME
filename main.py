import handler.socket_handler as socket_handler
import cli
import threading

def main():
    server_thread = threading.Thread(target=socket_handler.start_server)
    server_thread.start()

    cli_thread = threading.Thread(target=cli.main)
    cli_thread.start()

if __name__ == '__main__':
    main()
