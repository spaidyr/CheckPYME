import os
import shutil
import subprocess

class AgentFilePacket:
    """
    Una clase utilizada para representar el paquete de archivos del Agente.
    
    ...

    Atributos
    ----------
    No hay atributos públicos para esta clase.

    Métodos
    -------
    check_files_exist():
        Verifica la existencia de archivos y directorios específicos en la estructura de archivos del Agente.
        
    delete_file(file_path: str):
        Elimina el archivo en la ruta especificada si existe.
        
    delete_directory(dir_path: str):
        Elimina el directorio en la ruta especificada si existe.

    copy_file(src_path: str, dest_path: str):
        Copia un archivo desde la ruta de origen especificada a la ruta de destino.

    exec_innoSetup():
        Ejecuta el instalador Inno Setup si se encuentra en la ruta especificada.
        
    update_source_paths_in_iss(iss_filepath: str):
        Actualiza las rutas de origen en el archivo Inno Setup Script (.iss) con la ruta del directorio de trabajo actual.
    """
    def __init__(self):
        """
        El constructor de la clase AgentFilePacket.
        """
        if self.__check_files_exist():
            self.__update_source_paths_in_iss('handler/Installer/setup.iss')
            self.__exec_innoSetup()
        else:
            pass  # Implementa lo que quieras hacer si los archivos NO existen.

    def __check_files_exist(self):
        """
        Verifica la existencia de archivos y directorios específicos en la estructura de archivos del Agente.
        
        Retorna
        -------
        bool
            Retorna True si todos los archivos y directorios existen, False de lo contrario.
        """
        base_dir = 'Agent'
        files_dirs = [
            'certs/ca.crt',
            'certs/client.crt',
            'certs/client.key',
            'agent.json',
            'client.py',
            'checkpyme.py',
            'config.json',
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
        """
        Elimina el archivo en la ruta especificada si existe.

        Parámetros
        ----------
        file_path : str
            La ruta del archivo a eliminar.
        """
        if os.path.exists(file_path):
            os.remove(file_path)

    def delete_directory(self, dir_path):
        """
        Elimina el directorio en la ruta especificada si existe.

        Parámetros
        ----------
        dir_path : str
            La ruta del directorio a eliminar.
        """
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
    
    def copy_file(self, src_path, dest_path):
        """
        Copia un archivo desde la ruta de origen especificada a la ruta de destino.

        Parámetros
        ----------
        src_path : str
            La ruta de origen del archivo a copiar.
        dest_path : str
            La ruta de destino donde se copiará el archivo.
        """
        try:
            shutil.copy2(src_path, dest_path)
            print(f"El archivo ha sido copiado de {src_path} a {dest_path} con éxito.")
        except Exception as e:
            print(f"Ha ocurrido un error al copiar el archivo: {e}")       

    def __exec_innoSetup(self):
        """
        Ejecuta el instalador Inno Setup si se encuentra en la ruta especificada.
        """
        if not os.path.exists("C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"):
            subprocess.run('handler\Installer\innosetup.exe', shell=True)
        inno_setup_path = '"C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe"'
        iss_script_path = '".\handler\Installer\setup.iss"'
        subprocess.run(f'{inno_setup_path} /Qp {iss_script_path}', shell=True)
    

    def __update_source_paths_in_iss(self, iss_filepath):
        """
        Actualiza las rutas de origen en el archivo Inno Setup Script (.iss) con la ruta del directorio de trabajo actual.

        Parámetros
        ----------
        iss_filepath : str
            La ruta del archivo Inno Setup Script (.iss) a modificar.
        """
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
