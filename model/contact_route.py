from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import create_access_token
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from util.Connection import Connection

# from flask import _request_ctx_stack
# from flaskext.mysql import MySQL



contact = Blueprint('contact', __name__)

conexion = Connection()
mysql = conexion.mysql

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

public_key = private_key.public_key()

with open('private_key.pem', 'wb') as f:
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    f.write(pem)

with open('public_key.pem', 'wb') as f:
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    f.write(pem)

# Ruta para el inicio de sesión
@contact.route('/sndmsg', methods=['POST'])
def login():
    """
    Realiza el proceso de inicio de sesión.

    Returns:
        Una respuesta JSON con un token y el estado del inicio de sesión.
    """
    __dni = request.json.get('CorreoTrabajador')
    __pass = request.json.get('PasswordTrabajador')
    print("VALOR __dni:",__dni)
    print("VALOR __pass:",__pass)
    # print("validar_credenciales:",validar_credenciales(__dni, __pass))
    if (1==1):
    # if (validar_credenciales(__dni, __pass)):
        access_token = create_access_token(identity=__dni, additional_claims={'cabecera': "valor ejemplo"})
        validador = True
        # validador = validarTokenCreado(access_token, __dni)
        if validador:
            return jsonify({"mensaje": access_token, "estado": True})
        else:
            return jsonify({"mensaje": "Error al validar token", "estado": False})
    else:
        return jsonify({"mensaje": "Correo o contraseña incorrecta", "estado": False})
