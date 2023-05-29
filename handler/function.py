import handler.socket_handler as socket_handler
import subprocess
import stat
import sys
import os
import shutil
import time
from handler.socket_handler import clients
import certs.certs as certs


def stop_server():
    socket_handler.stop_server()

def list_clients():
    content = 'Hello'
    online_clients = socket_handler.sendToEveryClient(content)
    return online_clients

# Esta duncion solo funciona con cly.py, no está en uso en MyApp
def confirm_exit():
    while True:
        confirmacion = input("Are you sure you want to shut down the server? (y/n): ").lower()
        if confirmacion == "y":
            return True
        elif confirmacion == "n":
            return False
        else:
            print("Invalid option. Please try again.")

def excute_modules():
    content = 'exec_modules'
    result_clients = socket_handler.sendToEveryClient(content)
    return result_clients

def update_clients():
    content = 'update_modules'
    result_clients = socket_handler.sendToEveryClient(content)
    return result_clients

def delete_client(hostname):
    result = socket_handler.delete_client(hostname)
    return result

def check_files():
    mod_times = get_mod_times()
    for file, mod_time in mod_times.items():
        if file not in last_mod_times or last_mod_times[file] != mod_time:
            last_mod_times = mod_times  # Update stored mod times
            return True
    return False

def get_mod_times():
        mod_times = {}
        for file in os.listdir("./modules"):
            if file.endswith(".py"):  # Check only python files
                mod_times[file] = os.path.getmtime("./modules/" + file)
        return mod_times

def get_server_running():
    server_running = socket_handler.get_server_running()
    return server_running

def generate_certificates():
    config = certs.read_config()
    ca_private_key, ca_cert = certs.generate_ca(config)
    if ca_private_key and ca_cert:
        client_private_key, client_cert = certs.generate_client_key_cert(ca_private_key, ca_cert, config)
        server_private_key, server_cert = certs.generate_server_key_cert(ca_private_key, ca_cert, config)
