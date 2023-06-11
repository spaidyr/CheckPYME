import os
import re
import shutil
import subprocess

class AgentFilePacket:
    def __init__(self):
        if self.check_files_exist():
            self.update_source_paths_in_iss('handler/Installer/setup.iss')
            self.exec_innoSetup()
        else:
            pass  # Implementa lo que quieras hacer si los archivos NO existen.

    def check_files_exist(self):
        base_dir = 'Agent'
        files_dirs = [
            'certs/ca.crt',
            'certs/client.crt',
            'certs/client.key',
            'modules',
            'agent.json',
            'client.py',
            'checkpyme.py',
            'config.json',
            'icon.ico',
            'elk_credentials.txt'
        ]

        all_files_exist = True

        for file_dir in files_dirs:
            full_path = os.path.join(base_dir, file_dir)
            if not os.path.exists(full_path):
                print(f"El archivo o directorio {full_path} no existe")
                all_files_exist = False
            else:
                print(f"El archivo o directorio {full_path} existe")

        return all_files_exist

    def delete_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    def delete_directory(self, dir_path):
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    
    def copy_file(self, src_path, dest_path):
        try:
            shutil.copy2(src_path, dest_path)
            print(f"El archivo ha sido copiado de {src_path} a {dest_path} con éxito.")
        except Exception as e:
            print(f"Ha ocurrido un error al copiar el archivo: {e}")       

    def exec_innoSetup(self):
        if not os.path.exists("C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"):
            subprocess.run('handler\Installer\innosetup.exe', shell=True)
        inno_setup_path = '"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"'
        iss_script_path = '".\handler\Installer\setup.iss"'
        subprocess.run(f'{inno_setup_path} /Qp {iss_script_path}', shell=True)
    

    def update_source_paths_in_iss(self, iss_filepath):
        # Get the current working directory
        current_dir = os.getcwd()
        print(current_dir)
    
        # Open the ISS file
        with open(iss_filepath, 'r') as file:
            iss_file_contents = file.read()
    
        # Define the old path to be replaced
        old_path = "C:\your_path\CheckPYME"
    
        # Replace all occurrences of the old path with the new path
        new_contents = iss_file_contents.replace(old_path, current_dir)
        
        # Write the updated content back to the ISS file
        with open(iss_filepath, 'w') as file:
            file.write(new_contents)
