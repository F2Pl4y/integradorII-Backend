from flask import Blueprint, jsonify, request, make_response
from util.Connection import Connection
from flask_jwt_extended import create_access_token
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


validaciones = Blueprint('validaciones', __name__)

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
@validaciones.route('/login', methods=['POST'])
def login():
    """
    Realiza el proceso de inicio de sesión.

    Returns:
        Una respuesta JSON con un token y el estado del inicio de sesión.
    """
    
    __correo = request.json.get('CorreoTrabajador')
    __password = request.json.get('PasswordTrabajador')

    if (validar_credenciales(__correo, __password)):
        access_token = create_access_token(identity=__correo, additional_claims={'cabecera': "valor ejemplo"})
        validador = validarTokenCreado(access_token, __correo)
        if validador:
            return jsonify({"mensaje": access_token, "estado": True})
        else:
            return jsonify({"mensaje": "Error al validar token", "estado": False})
    else:
        return jsonify({"mensaje": "Correo o contraseña incorrecta", "estado": False})

@validaciones.route('/protected', methods=['GET'])
def protected():
    """
    Accede a una ruta protegida que requiere autenticación.
    Returns:
        Una respuesta JSON con el resultado de la consulta y el estado de éxito.
    """
    token = request.headers.get('Authorization').split('cabecera')[1]
    exito = True
    try:
        sql = "SELECT CorreoTrabajador FROM `trabajador` WHERE validarTKN = %s"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, token)
        dato = cursor.fetchone()
        if dato is not None:
            resultado = {"TKN": dato[0]}
        else:
            resultado = "NO TIENES TOKEN"
            exito = False
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

def validar_credenciales(correo, contraseña):
    """
    Valida las credenciales de un trabajador en la base de datos.

    Args:
        correo: El correo del trabajador.
        contraseña: La contraseña del trabajador.
    Returns:
        Validacion si se encontró al trabajador o no
    """
    try:
        sql = "SELECT COUNT(*) FROM trabajador WHERE CorreoTrabajador = %s AND PasswordTrabajador = AES_ENCRYPT(%s, %s) AND IDCargo = 1;"
        conector = mysql.connect()
        cursor = conector.cursor()
        datos = (correo, contraseña, contraseña)
        cursor.execute(sql, datos)
        resultado = cursor.fetchone()

        return resultado[0] > 0
    except Exception as e:
        return False
    finally:
        cursor.close()

def validarTokenCreado(token, correo):
    """
    Actualiza el token en la base de datos para el trabajador especificado.

    Parámetros:
        token: El nuevo token a actualizar en la base de datos.
        correo: El correo del trabajador cuyo token se va a actualizar.
    """
    try:
        sql = "UPDATE trabajador SET validarTKN = %s WHERE CorreoTrabajador = %s;"
        conector = mysql.connect()
        cursor = conector.cursor()
        datos = (token, correo)
        cursor.execute(sql, datos)
        conector.commit()
        return True
    except Exception as e:
        return False
    finally:
        cursor.close()