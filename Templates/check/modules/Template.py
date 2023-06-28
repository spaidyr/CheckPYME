class Template():
    """
    La clase Template se encarga de inicializar y gestionar información obtenida de un archivo (doc_file), 
    realizando comparaciones con una plantilla dada (template) para determinar niveles de seguridad.

    Atributos
    ----------
    template : dict
        Plantilla predefinida que contiene las claves a comparar con el documento.
    doc_file : dict
        Documento original del cual se extraerá la información para comparar con la plantilla.
    doc_low : dict
        Documento resultado con las claves que coinciden con el nivel de seguridad "bajo".
    doc_medium : dict
        Documento resultado con las claves que coinciden con el nivel de seguridad "medio".
    doc_high : dict
        Documento resultado con las claves que coinciden con el nivel de seguridad "alto".
    doc_security_status : dict
        Documento resultado que asocia a cada atributo un nivel de seguridad.

    Métodos
    -------
    __init__(doc_file: dict, template: dict):
        Constructor de la clase que inicializa los atributos y llama al método 'check'.
    get_result():
        Devuelve una tupla con los documentos resultado para cada nivel de seguridad y el estado de seguridad.
    check():
        Realiza las comprobaciones de coincidencias entre el doc_file y la template, actualizando los documentos de resultado.
    translate_values(dictionary: dict) -> dict:
        Traduce los valores "Nunca" y "Ninguna" a "0" en un diccionario y lo devuelve.
    comparision(comparison_dict: dict, source_content: dict, common_keys: set):
        Realiza una comparación a diferentes niveles de seguridad y actualiza los documentos de resultado correspondientes.
    full_comparision(comparison_dict: dict, source_content: dict, common_keys: set):
        Realiza una comparación a todos los niveles de seguridad y actualiza el atributo 'doc_security_status'.
    """

    def __init__(self, doc_file, template):
        """
        Constructor de la clase. Inicializa los atributos y realiza las comprobaciones correspondientes.

        Parámetros
        ----------
        doc_file : dict
            Documento original que contiene la información a comparar con la plantilla.
        template : dict
            Plantilla que contiene las claves a comparar con el documento.
        """

        self.template = template
        self.doc_file = doc_file
        self.doc_low = None
        self.doc_medium = None
        self.doc_high = None
        self.doc_security_status = {}
        self.check()

    def get_result(self):
        """
        Devuelve una tupla con los documentos resultado para cada nivel de seguridad y el estado de seguridad.

        Returns
        -------
        tuple
            Tupla con los documentos de resultado: doc_low, doc_medium, doc_high y doc_security_status.
        """

        return self.doc_low, self.doc_medium, self.doc_high, self.doc_security_status

    def check(self):
        """
        Realiza las comprobaciones de coincidencias entre el doc_file y la template, actualizando los documentos de resultado.
        """

        # Elimina la clave '_source' del doc_file
        source_content = self.doc_file['_source']
        
        # Traduce "NUNCA" y "Ninguna" a "0"
        # Ejecutar esta función si es necesario convertir valores str a int
        source_content = self.translate_values(source_content)

        # Crea un nuevo diccionario con los primeros tres parámetros.
        result_dict = {
            "module_name": source_content["module_name"],
            "hostname": source_content["hostname"],
            "timestamp": source_content["timestamp"],
        }

        # Obtiene las keys del bloque 'low' en la plantilla.
        # se utiliza este bloque pero son todo iguales, se podria usar cualquiera
        template_keys = set(self.template["low"][0].keys())

        # Obttiene las keys del doc_file.
        doc_file_keys = set(source_content.keys())

        # Obtiene la intersección con las claves
        common_keys = template_keys.intersection(doc_file_keys)

        # Añade las keys comunes al diccionario
        for key in common_keys:
            result_dict[key] = source_content[key]
        
        # Se generan dos copias para evitar conflictos de solapamiento dentro de la aplicación.
        comparison_dict01 = result_dict.copy()
        comparison_dict02 = result_dict.copy()
        
        self.comparision(comparison_dict01, source_content, common_keys)
        self.full_comparision(comparison_dict02, source_content, common_keys)
        
    def translate_values(self, dictionary):
        """
        Traduce los valores "Nunca" y "Ninguna" a "0" en un diccionario y lo devuelve.

        Parámetros
        ----------
        dictionary : dict
            Diccionario que contiene las claves y valores a traducir.

        Returns
        -------
        dict
            Diccionario con los valores traducidos.
        """

        for key, value in dictionary.items():
            if isinstance(value, dict):
                # Si el valor es otro diccionario, llama a la función de forma recursiva
                self.translate_values(value)
            elif isinstance(value, str):
                # Comprueba si el valor es una cadena antes de compararlo con "Nunca" o "Ninguna"
                if value == "Nunca" or value == "Ninguna":
                    dictionary[key] = 0
        return dictionary

    
    def comparision(self, comparison_dict, source_content, common_keys):
        """
        Realiza una comparación a diferentes niveles de seguridad y actualiza los documentos de resultado correspondientes.

        Parámetros
        ----------
        comparison_dict : dict
            Diccionario base para realizar las comparaciones.
        source_content : dict
            Diccionario que contiene el contenido del documento original.
        common_keys : set
            Conjunto de claves que se encuentran tanto en la plantilla como en el documento original.
        """

        for security_level in ["low", "medium", "high"]:
            # Crea una copia de comparison_dict para cada nivel de seguridad
            comparison_dict_copy = comparison_dict.copy()
            # Añade la etiqueta del nivel de seguridad
            comparison_dict_copy["security_level"] = security_level
            for key in common_keys:
                # Compara todos y crea un doc por cada nivel de seguridad

                ## Implementa aquí las comprobaciones que deba realizar la aplicación,
                ## de modo que el resultado de cada uno de los valores asociados a las keys,
                # sean valores booleanos
                pass

            # Asigna el diccionario modificado al atributo correspondiente
            setattr(self, f"doc_{security_level}", comparison_dict_copy)
    
    def full_comparision (self, comparison_dict, source_content, common_keys):
        """
        Realiza una comparación a todos los niveles de seguridad y actualiza el atributo 'doc_security_status'.

        Parámetros
        ----------
        comparison_dict : dict
            Diccionario base para realizar las comparaciones.
        source_content : dict
            Diccionario que contiene el contenido del documento original.
        common_keys : set
            Conjunto de claves que se encuentran tanto en la plantilla como en el documento original.
        """

        for key in common_keys:
            comparison_dict[key] = "None"
        
        comparison_dict["security_level"] = "security_status"
        for key in common_keys:
            for security_level in ["low", "medium", "high"]:
                # Crea un doc asociando a cada atributo un nivel de seguridad
                
                ## Implementa aquí las comprobaciones que deba realizar la aplicación,
                ## de modo que el resultado de cada uno de los valores asociados a las keys,
                # sean los valores ["None", "low", "medium", "high"]
                pass

        self.doc_security_status.update(comparison_dict)

