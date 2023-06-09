import json
import threading
from client import start_client, listen_for_server

def read_config():
    with open("config.json", "r") as f:
        return json.load(f)

if __name__ == '__main__':

    config = read_config()
    start_client(config)
    threading.Thread(target=listen_for_server(config)).start()