class PA_CW_Autocompletar():

    def __init__(self, doc_file, template):
        self.template = template
        self.doc_file = doc_file
        self.doc_low = None
        self.doc_medium = None
        self.doc_high = None
        self.doc_security_status = {}
        self.check()

    def get_result(self):
        return self.doc_low, self.doc_medium, self.doc_high, self.doc_security_status

    def check(self):

        # Remove the '_source' key from doc_file
        source_content = self.doc_file['_source']

        # Create a new dictionary with the first three parameters
        result_dict = {
            "module_name": source_content["module_name"],
            "hostname": source_content["hostname"],
            "timestamp": source_content["timestamp"],
            'policy_name': source_content["policy_name"]
        }

        # Get the keys of the 'low' block in the template
        template_keys = set(self.template["low"][0].keys())

        # Get the keys of the doc_file
        doc_file_keys = set(source_content.keys())

        # Find the intersection of the keys
        common_keys = template_keys.intersection(doc_file_keys)

        # Add the common keys to the result_dict
        for key in common_keys:
            result_dict[key] = source_content[key]
        
        comparison_dict01 = result_dict.copy()
        comparison_dict02 = result_dict.copy()
        
        self.comparision(comparison_dict01, source_content, common_keys)
        self.full_comparision(comparison_dict02, source_content, common_keys)

    
    def comparision(self, comparison_dict, source_content, common_keys):

        for security_level in ["low", "medium", "high"]:
            # Crea una copia de comparison_dict para cada nivel de seguridad
            comparison_dict_copy = comparison_dict.copy()
            # Añade la etiqueta del nivel de seguridad
            comparison_dict_copy["security_level"] = security_level
            for key in common_keys:
                # Compara todos y crea un doc por cada nivel de seguridad
                comparison_dict_copy[key] = source_content[key] == self.template[security_level][0][key]
            # Asigna el diccionario modificado al atributo correspondiente
            setattr(self, f"doc_{security_level}", comparison_dict_copy)
    
    def full_comparision (self, comparison_dict, source_content, common_keys):
        
        for key in common_keys:
            comparison_dict[key] = "None"
        
        comparison_dict["security_level"] = "security_status"
        for key in common_keys:
            for security_level in ["low", "medium", "high"]:
                if source_content[key] == self.template[security_level][0][key]:
                    comparison_dict[key] = security_level
        self.doc_security_status.update(comparison_dict)

