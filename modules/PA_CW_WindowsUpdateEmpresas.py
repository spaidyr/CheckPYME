from datetime import datetime
from bs4 import BeautifulSoup
import platform
import pytz

GPRESULT_PATH = "C:\\TEMP\\report.html"

class PA_CW_WindowsUpdateEmpresas():

    def __init__(self) -> dict:

        self.result = {}
        name = 'PA_CW_WindowsUpdateEmpresas'
        self.result['module_name'] = name
        self.result['policy_name'] = "Componentes de Windows/Windows Update/Actualización de Windows para empresas"
        self.result['hostname'] = platform.node()
        madrid_tz = pytz.timezone('Europe/Madrid')
        self.result['timestamp'] = datetime.now(madrid_tz).isoformat()
        self.log_file = None
        self.log_file = self.check()

    def check(self):
        values = self.__read_gpResult()
        #print(values)  # imprimir resultados para verificar
        
        # Comprobar y actualizar los valores
        keys_to_check = ["Administrar compilaciones preliminares",
                         "Seleccione el nivel de preparación de Windows para obtener las actualizaciones que desea recibir:"]
        for key in keys_to_check:
            if key in values:
                self.result[key] = values[key]
            else:
                self.result[key] = "No Configurado"
        
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