from elasticsearch import Elasticsearch, exceptions as es_exceptions

ES = Elasticsearch(
    ['https://127.0.0.1:9200'],  # Cambia 'localhost:9200' por tu host y puerto
    verify_certs=True,  # Cambia a True y proporciona la ruta al certificado SSL si es necesario
    ca_certs='./certs/ca/ca.crt',
    basic_auth=('elastic', 'elastic'),  # Descomenta y añade las credenciales si tu servidor Elasticsearch requiere autenticación
    )
INDEX_NAME = 'checkpyme-agents'
INDEX_RESULT = 'checkpyme-results-levels'
INDEX_STATUS = 'checkpyme-results-status'

ROL_NAME = 'index_checkpyme'

def check_and_create_index():
    """
    Comprueba y crea índices si no existen en Elasticsearch.

    Devuelve:
        list: una lista de mensajes que indican el resultado de cada operación de índice.
    """
    if not ES.ping():
        raise ValueError("Connection failed")

    messages = []
    # Código para verificar y crear índices
    indices = [INDEX_NAME, INDEX_RESULT, INDEX_STATUS]
    for index in indices:
        if not ES.indices.exists(index=index):
            settings = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            }
            res = ES.indices.create(index=index, body=settings)
            print (res)
            if res['acknowledged']:
                messages.append(f"Índice {index} creado con éxito.")
            else:
                messages.append(f"El índice {index} ya existe.")
        else:
            messages.append(f"El índice {index} ya existe.")

    return messages

def create_role():
    """
    Crea un nuevo rol en Elasticsearch con el nombre ROL_NAME.
    Este rol tiene los privilegios 'create_doc' e 'index' en el índice INDEX_NAME.
    """
    role_definition = {
        "indices" : [
            {
                "names" : [INDEX_NAME],
                "privileges" : ["create_doc", "index"]
            }
        ]
    }
    
    try:
        ES.security.put_role(name=ROL_NAME, body=role_definition)
        print(f"Role {ROL_NAME} has been created successfully.")
    except es_exceptions.NotFoundError:
        print(f"Role {ROL_NAME} could not be created.")

def create_user(username, password, roles):
    """
    Crea un nuevo usuario en Elasticsearch.

    Argumentos:
        username (str): el nombre de usuario para el nuevo usuario.
        password (str): la contraseña para el nuevo usuario.
        roles (list): una lista de roles para asignar al nuevo usuario.

    Devuelve:
        str: un mensaje que indica si el usuario fue creado con éxito o no.
    """
    user_definition = {
        "password" : password,
        "roles" : roles,
        "full_name" : "User Full Name",
        "email" : "user@example.com",
        "metadata" : {
            "intelligence" : 7
        },
        "enabled": True
    }
    
    try:
        ES.security.put_user(username=username, body=user_definition)
        return f"User {username} has been created successfully."
    except es_exceptions.NotFoundError:
        return f"User {username} could not be created."

def get_doc(module_name, hostname, index_name):
    """
    Consulta Elasticsearch para obtener información sobre un módulo y hostname específicos.

    Argumentos:
        module_name (str): el nombre del módulo.
        hostname (str): el nombre del host.
        index_name (str): el nombre del índice donde buscar.

    Devuelve:
        dict: el último documento indexado para ese módulo y hostname, o None si no hay ninguno.
    """
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"module_name.keyword": module_name}},  # Usamos la variable module_name
                    {"match": {"hostname.keyword": hostname}}  # Usamos la variable hostname
                ]
            }
        },
        "sort": [{"timestamp": {"order": "desc"}}],
        "size": 1
    }

    response = ES.search(index=index_name, body=query)  # Cambiado el índice a "checkpyme"

    # Devuelve el último documento indexado si existe
    if response['hits']['hits']:
        return response['hits']['hits'][0]
    else:
        return None

def get_security_compliance(module_name, hostname, security_level):
    """
    Consulta Elasticsearch para obtener información sobre la conformidad de un módulo y hostname específicos.

    Argumentos:
        module_name (str): el nombre del módulo.
        hostname (str): el nombre del host.
        security_level (str): el nivel de seguridad a consultar.

    Devuelve:
        dict: el último documento indexado para esa conformidad de módulo y hostname, o None si no hay ninguno.
    """
    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"module_name.keyword": module_name}},  # Usamos la variable module_name
                    {"match": {"hostname.keyword": hostname}},  # Usamos la variable hostname
                    {"match": {"security_level.keyword": security_level}}  # Usamos la variable hostname
                ]
            }
        },
        "sort": [{"timestamp": {"order": "desc"}}],
        "size": 1
    }

    response = ES.search(index=INDEX_RESULT, body=query)  # Cambiado el índice a "checkpyme"

    # Devuelve el último documento indexado si existe
    if response['hits']['hits']:
        return response['hits']['hits'][0]
    else:
        return None

def set_doc(doc_body, index_type):
    """
    Publica los resultados en Elasticsearch en el índice especificado.

    Argumentos:
        doc_body (dict): el cuerpo del documento a indexar.
        index_type (str): el nombre del índice donde se publicarán los resultados.

    Devuelve:
        str: un mensaje que indica si el documento fue creado con éxito o no, o un mensaje de error.
    """
    try:
        res = ES.index(index=index_type, body=doc_body)
        if res['result'] == 'created':
            return f"Document successfully created with _id: {res['_id']}"
        else:
            return "Unexpected result: " + res['result']
    except es_exceptions.ElasticsearchException as e:
        return "Error: " + str(e)