from datetime import datetime
from bs4 import BeautifulSoup
import platform
import pytz

GPRESULT_PATH = "C:\\TEMP\\report.html"

class PA_CW_PrivacidadApp():

    def __init__(self) -> dict:

        self.result = {}
        name = 'PA_CW_PrivacidadApp'
        self.result['module_name'] = name
        self.result['policy_name'] = "Componentes de Windows/Privacidad de la aplicación"
        self.result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')
        self.result['timestamp'] = datetime.now(madrid_tz).isoformat()
        self.log_file = None
        self.log_file = self.check()

    def check(self):
        values = self.__read_gpResult()

        apps_to_check = ["Permitir que las aplicaciones de Windows accedan a dispositivos de confianza",
                         "Permitir que las aplicaciones de Windows accedan a la cámara",
                         "Permitir que las aplicaciones de Windows accedan a la información de diagnóstico sobre otras aplicaciones",     
                         "Permitir que las aplicaciones de Windows accedan a la información de la cuenta",
                         "Permitir que las aplicaciones de Windows accedan a la ubicación",
                         "Permitir que las aplicaciones de Windows accedan a las notificaciones",
                         "Permitir que las aplicaciones de Windows accedan a las tareas",
                         "Permitir que las aplicaciones de Windows accedan a los mensajes",
                         "Permitir que las aplicaciones de Windows accedan al calendario",
                         "Permitir que las aplicaciones de Windows accedan al correo electrónico",
                         "Permitir que las aplicaciones de Windows accedan al historial de llamadas",
                         "Permitir que las aplicaciones de Windows accedan al micrófono",
                         "Permitir que las aplicaciones de Windows accedan al movimiento",
                         "Permitir que las aplicaciones de Windows controlen las radios",
                         "Permitir que las aplicaciones de Windows realicen llamadas telefónicas",
                         "Permitir que las aplicaciones de Windows se comuniquen con dispositivos desemparejados",
                         "Permitir que las aplicaciones de Windows se ejecuten en el fondo",
                         "Permitir que las aplicaciones de Windows tengan acceso a los contactos"]

        for app in apps_to_check:
            if app in values:
                self.result[app] = values[app]

                # Look for the corresponding default value in the keys after the current app key
                default_value = None
                app_found = False
                for key in values:
                    if app_found and "Valor predeterminado para todas las aplicaciones:" in key:
                        default_value = key.split("Valor predeterminado para todas las aplicaciones:", 1)[1].strip().split("\n")[0]
                        break
                    if key == app:
                        app_found = True

                default_key = app + " - Valor predeterminado para todas las aplicaciones:"
                if default_value is not None:
                    self.result[default_key] = default_value
                else:
                    self.result[default_key] = "No Configurado"
            else:
                self.result[app] = "No Configurado"
                self.result[app + " - Valor predeterminado para todas las aplicaciones:"] = "No Configurado"

        return self.result

    def get_policy_info(self, cells):
        if len(cells) >= 2:
            policy_name = cells[0].text.strip()
            policy_status = cells[1].text.strip()
            return policy_name, policy_status
        else:
            return None, None
    
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