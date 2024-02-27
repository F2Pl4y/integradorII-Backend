from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import create_access_token
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.asymmetric import rsa
from util.Connection import Connection

# from flask import _request_ctx_stack
# from flaskext.mysql import MySQL



createViaje = Blueprint('createViaje', __name__)

conexion = Connection()
mysql = conexion.mysql



# Ruta para el inicio de sesión
@createViaje.route('/regViaje/', methods=["POST"])
def login():
    print("ingreso a viajes")
    """
    Realiza el proceso de inicio de sesión.

    Returns:
        Una respuesta JSON con un token y el estado del inicio de sesión.
    """
    __viajeA = request.json.get('viajeA')
    __detViajeA = request.json.get('detViajeA')
    __viajeB = request.json.get('viajeB')
    __detViajeB = request.json.get('detViajeB')
    __datePart = request.json.get('datePart')
    __timePart = request.json.get('timePart')
    __carSel = request.json.get('carSel')
    __asiCant = request.json.get('asiCant')
    __costPasaje = request.json.get('costPasaje')
    __pagoType = request.json.get('pagoType')
    print("__viajeA ", __viajeA)
    print("__detViajeA ", __detViajeA)
    print("__viajeB ", __viajeB)
    print("__detViajeB ", __detViajeB)
    print("__datePart ", __datePart)
    print("__timePart ", __timePart)
    print("__carSel ", __carSel)
    print("__asiCant ", __asiCant)
    print("__costPasaje ", __costPasaje)
    print("__pagoType ", __pagoType)
    # if (validar_credenciales(__dni, __pass)):
    if (1==1):
        # print("hola")
        # access_token = create_access_token(identity=__dni, additional_claims={'cabecera': "valor ejemplo"})
        # validador = validarTokenCreado(access_token, __dni)
        # if validador:
            # return jsonify({"mensaje": access_token, "estado": True})
        
        return jsonify({"mensaje": "todo OK", "exito": True})
        # else:
        #     return jsonify({"mensaje": "Error al validar token", "estado": False})
    else:
        return jsonify({"mensaje": "Correo o contraseña incorrecta", "estado": False})

@createViaje.route('/protectedctc', methods=['GET'])
def protected():
    """
    Accede a una ruta protegida que requiere autenticación.

    Returns:
        Una respuesta JSON con el resultado de la consulta y el estado de éxito.
    """
    token = request.headers.get('Authorization').split('cabecera')[1]
    exito = True
    try:
        # sql = "SELECT CorreoTrabajador FROM `trabajador` WHERE validarTKN = %s"
        sql = "SELECT dni FROM usuario WHERE validarTKN = %s"
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

# def validar_credenciales(dni):
def validar_credenciales(dni, contra):
    """
    Valida las credenciales de un trabajador en la base de datos.

    Args:
        correo: El correo del trabajador.
        contraseña: La contraseña del trabajador.
    Returns:
        Validacion si se encontró al trabajador o no
    """
    # print("entro a validar_credenciales principal")
    try:
        # token = request.headers.get('Authorization').split('cabecera')[1]
        # sql = "SELECT COUNT(*) FROM trabajador WHERE CorreoTrabajador = %s AND PasswordTrabajador = AES_ENCRYPT(%s, %s) AND IDCargo = 1;"
        sql = "SELECT COUNT(*) FROM usuario WHERE dni = %s AND pass = %s AND tipoUser = 1;"
        
        # sql = "SELECT tipou.nombre FROM usuario JOIN tipou ON usuario.tipoUser = tipou.idTipo WHERE usuario.dni = %s"
        # sql = "SELECT tipou.nombre FROM usuario JOIN tipou ON usuario.tipoUser = tipou.idTipo WHERE usuario.validarTKN = %s"

        conector = mysql.connect()
        cursor = conector.cursor()
        # datos = (token)
        datos = (dni, contra)
        cursor.execute(sql, datos)
        resultado = cursor.fetchone()
        # print("valor del resultado[0]", resultado[0])
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
    # print("valor token:", token)
    # print("valor correo:", correo)
    try:
        # sql = "UPDATE trabajador SET validarTKN = %s WHERE CorreoTrabajador = %s;"
        sql = "UPDATE usuario SET validarTKN = %s WHERE dni = %s;"
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


@createViaje.route('/validarUser', methods=['GET'])
def validarUser():
    """
    Accede a una ruta protegida que requiere autenticación.

    Returns:
        Una respuesta JSON con el resultado de la consulta y el estado de éxito.
    """
    token = request.headers.get('Authorization').split('cabecera')[1]
    exito = True
    try:
        # sql = "SELECT CorreoTrabajador FROM `trabajador` WHERE validarTKN = %s"
        sql = "SELECT dni FROM usuario WHERE validarTKN = %s"
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


def validarTipoUserA():
    """
    Valida las credenciales de un trabajador en la base de datos.

    Args:
        correo: El correo del trabajador.
        contraseña: La contraseña del trabajador.
    Returns:
        Validacion si se encontró al trabajador o no
    """
    # print("entro a validar _ credenciales principal")
    try:
        token = request.headers.get('Authorization').split('cabecera')[1]
        # sql = "SELECT COUNT(*) FROM trabajador WHERE CorreoTrabajador = %s AND PasswordTrabajador = AES_ENCRYPT(%s, %s) AND IDCargo = 1;"
        # sql = "SELECT COUNT(*) FROM usuario WHERE dni = %s AND pass = %s AND tipoUser = 1;"
        
        # sql = "SELECT tipou.nombre FROM usuario JOIN tipou ON usuario.tipoUser = tipou.idTipo WHERE usuario.dni = %s"
        sql = "SELECT tipou.nombre FROM usuario JOIN tipou ON usuario.tipoUser = tipou.idTipo WHERE usuario.validarTKN = %s"

        conector = mysql.connect()
        cursor = conector.cursor()
        datos = (token)
        # datos = (correo, contraseña)
        cursor.execute(sql, datos)
        resultado = cursor.fetchone()
        # print("valor del resultado[0]", resultado[0])
        return resultado[0] > 0
    except Exception as e:
        return False
    finally:
        cursor.close()

