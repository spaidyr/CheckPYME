import json
from ipaddress import IPv4Address
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization import NoEncryption
from datetime import datetime, timedelta


def read_config():
    with open(".\certs\config.json", "r") as f:
        return json.load(f)

def generate_ca(config):

    # Genera la clave privada de la CA
    ca_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Genera el certificado de la CA
    ca_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, config["ca"]["country_name"]),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, config["ca"]["state_or_province_name"]),
        x509.NameAttribute(NameOID.LOCALITY_NAME, config["ca"]["locality_name"]),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, config["ca"]["organization_name"]),
        x509.NameAttribute(NameOID.COMMON_NAME, config["ca"]["common_name"]),
    ])
    ca_cert = (
        x509.CertificateBuilder()
        .subject_name(ca_subject)
        .issuer_name(ca_subject)
        .public_key(ca_private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=int(config["ca"]["validity_days"])))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(ca_private_key, hashes.SHA256())
    )

    # Guarda la clave privada de la CA en un archivo
    with open(".\certs\ca\ca.key", "wb") as f:
        f.write(ca_private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()))

    # Guarda el certificado de la CA en un archivo
    with open(".\certs\ca\ca.crt", "wb") as f:
        f.write(ca_cert.public_bytes(Encoding.PEM))
    
    # Guarda el certificado de la CA en el cliente
    with open(".\Agent\certs\ca.crt", "wb") as f:
        f.write(ca_cert.public_bytes(Encoding.PEM))

    return ca_private_key, ca_cert


def generate_client_key_cert(ca_private_key, ca_cert, config):

    # Genera la clave privada del cliente
    client_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Genera el certificado del cliente, firmado por la CA
    client_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, config["client"]["country_name"]),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, config["client"]["state_or_province_name"]),
        x509.NameAttribute(NameOID.LOCALITY_NAME, config["client"]["locality_name"]),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, config["client"]["organization_name"]),
        x509.NameAttribute(NameOID.COMMON_NAME, config["client"]["common_name"]),
    ])

    # Agrega la IP a los nombres alternativos del sujeto
    san = x509.SubjectAlternativeName([x509.IPAddress(IPv4Address(config["server"]["san_ip"]))])

    client_cert = (
        x509.CertificateBuilder()
        .subject_name(client_subject)
        .issuer_name(ca_cert.subject)
        .public_key(client_private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=int(config["client"]["validity_days"])))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(san, critical=False)  # Agrega la extensión SAN al certificado
        .sign(ca_private_key, hashes.SHA256())
    )

    # Guarda la clave privada del cliente en un archivo
    with open(".\certs\client\client.key", "wb") as f:
        f.write(client_private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()))

    # Guarda la clave privada del cliente en un archivo
    with open(".\Agent\certs\client.key", "wb") as f:
        f.write(client_private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()))

    # Guarda el certificado del cliente en un archivo
    with open(".\certs\client\client.crt", "wb") as f:
        f.write(client_cert.public_bytes(Encoding.PEM))

    # Guarda el certificado del cliente en un archivo
    with open(".\Agent\certs\client.crt", "wb") as f:
        f.write(client_cert.public_bytes(Encoding.PEM))
    
    return client_private_key, client_cert

def generate_server_key_cert(ca_private_key, ca_cert, config):

    # Genera la clave privada del cliente
    server_private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Genera el certificado del cliente, firmado por la CA
    server_subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, config["server"]["country_name"]),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, config["server"]["state_or_province_name"]),
        x509.NameAttribute(NameOID.LOCALITY_NAME, config["server"]["locality_name"]),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, config["server"]["organization_name"]),
        x509.NameAttribute(NameOID.COMMON_NAME, config["server"]["common_name"]),
    ])

    # Agrega la IP a los nombres alternativos del sujeto
    san = x509.SubjectAlternativeName([
        x509.IPAddress(IPv4Address(config["server"]["san_ip"])),
        x509.IPAddress(IPv4Address('127.0.0.1'))
        ])

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(server_subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=int(config["server"]["validity_days"])))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(san, critical=False)  # Agrega la extensión SAN al certificado
        .sign(ca_private_key, hashes.SHA256())
    )

    # Guarda la clave privada del cliente en un archivo
    with open(".\certs\server\server.key", "wb") as f:
        f.write(server_private_key.private_bytes(Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()))

    # Guarda el certificado del cliente en un archivo
    with open(".\certs\server\server.crt", "wb") as f:
        f.write(server_cert.public_bytes(Encoding.PEM))

    return server_private_key, server_cert