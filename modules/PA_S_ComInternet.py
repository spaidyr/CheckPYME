from datetime import datetime
from bs4 import BeautifulSoup
import platform
import pytz
import string


GPRESULT_PATH = "C:\\TEMP\\report.html"

class PA_S_ComInternet():

    def __init__(self) -> dict:

        self.result = {}
        name = 'PA_S_ComInternet'
        self.result['module_name'] = name
        self.result['policy_name'] = "Sistema/Administración de comunicaciones de Internet/Configuración de comunicaciones de Internet"
        self.result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')
        self.result['timestamp'] = datetime.now(madrid_tz).isoformat()
        self.log_file = None
        self.log_file = self.check()

    def check(self):
        values = self.__read_gpResult()
        #print(values)  # imprimir resultados para verificar
        
        # Comprobar y actualizar los valores
        keys_to_check = ["Desactivar el acceso a Store",
                        'Desactivar el contenido "¿Sabía que...?" del Centro de ayuda y soporte técnico',
                        "Desactivar el informe de errores de Windows",
                        "Desactivar el Programa para la mejora de la experiencia del usuario de Windows",
                        "Desactivar informe de errores de reconocimiento de escritura a mano",
                        "Desactivar la actualización de archivos de contenido del Asistente para búsqueda",
                        "Desactivar la búsqueda en Microsoft Knowledge Base del Centro de ayuda y soporte técnico",
                        'Desactivar la tarea de imágenes "Pedir copias fotográficas"',
                        'Desactivar los vínculos "Events.asp" del Visor de eventos',
                        "Desactivar uso compartido de datos de personalización de escritura a mano"]
        for key in keys_to_check:
            no_special_chars_key = self.remove_special_chars(key)
            if key in values:
                self.result[no_special_chars_key] = values[key]
            else:
                self.result[no_special_chars_key] = "No Configurado"
        return self.result

    def get_policy_info(self, cells):
        if len(cells) >= 2:
            policy_name = cells[0].text.strip()
            policy_status = cells[1].text.strip()
            return policy_name, policy_status
        else:
            return None, None
    
    def remove_special_chars(self, input_str):
        # Declarar una tabla de traducción que reemplace los caracteres especiales con None
        special_chars = string.punctuation  # contiene todos los caracteres especiales
        translate_table = str.maketrans('', '', special_chars)

        # Usa la tabla de traducción para eliminar los caracteres especiales
        no_special_chars_str = input_str.translate(translate_table)
        return no_special_chars_str

    def __read_gpResult(self):
        values = {}

        with open(GPRESULT_PATH, 'r', encoding='utf-16') as f:
            contents = f.read()

        soup = BeautifulSoup(contents, 'html.parser')
        containers = soup.find_all('div', class_='container')

        for container in containers:
            title = container.find('span', class_='sectionTitle', string='Plantillas administrativas')

            if title:
                policies = container.find_all('div', class_='he3')

                for div_he3 in policies:
                    if div_he3:
                        section_titles = div_he3.find_all('span', class_='sectionTitle')

                        for section_title in section_titles:
                            table = section_title.find_next('table', class_='info3')

                            if table:
                                rows = table.find_all('tr')

                                for row in rows:
                                    policy_name, policy_status = self.get_policy_info(row.find_all('td'))
                                    if policy_name:
                                        values[policy_name] = policy_status

                                    subtable = row.find('table', class_='subtable_frame')

                                    if subtable:
                                        for subrow in subtable.find_all('tr'):
                                            subpolicy_name, subpolicy_status = self.get_policy_info(subrow.find_all('td'))
                                            if subpolicy_name:
                                                values[subpolicy_name] = subpolicy_status

                                break
                break
        return values