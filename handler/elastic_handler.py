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

    if not ES.ping():
        raise ValueError("Connection failed")

    if not ES.indices.exists(index=INDEX_NAME):
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }

        res = ES.indices.create(index=INDEX_NAME, body=settings)
        if res['acknowledged']:
            print("Índice creado con éxito.")
    else:
        print("El índice ya existe.")
    
    if not ES.indices.exists(index=INDEX_RESULT):
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }

        res = ES.indices.create(index=INDEX_RESULT, body=settings)
        if res['acknowledged']:
            print("Índice creado con éxito.")
    else:
        print("El índice ya existe.")
    
    if not ES.indices.exists(index=INDEX_STATUS):
        settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }

        res = ES.indices.create(index=INDEX_STATUS, body=settings)
        if res['acknowledged']:
            print("Índice creado con éxito.")
    else:
        print("El índice ya existe.")

def create_role():
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

def get_checkpyme(module_name, hostname):

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

    response = ES.search(index=INDEX_NAME, body=query)  # Cambiado el índice a "checkpyme"

    # Devuelve el último documento indexado si existe
    if response['hits']['hits']:
        return response['hits']['hits'][0]
    else:
        return None


def post_results(doc_body, index_type):
    try:
        res = ES.index(index=index_type, body=doc_body)
        if res['result'] == 'created':
            return f"Document successfully created with _id: {res['_id']}"
        else:
            return "Unexpected result: " + res['result']
    except es_exceptions.ElasticsearchException as e:
        return "Error: " + str(e)