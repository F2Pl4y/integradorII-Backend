from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity 
from flask_cors import cross_origin
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from util.Connection import Connection

# from flask import _request_ctx_stack
# from flaskext.mysql import MySQL

validarLogin = Blueprint('validarLogin', __name__)

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

# # Ruta para el inicio de sesión
# @jwt_required()
# @validarLogin.route('/loginctc', methods=['POST'])
# @cross_origin()
# def login():
#     try:
#         __dni = request.json.get('dniUser')
#         __pass = request.json.get('PasswordTrabajador')
#         print("VALOR DE MI DNI:",__dni)
#         print("VALOR __pass:",__pass)
#         # print("validar_credenciales:",validar_credenciales(__dni, __pass))
#         if (validar_credenciales(__dni, __pass)):
#             # access_token = create_access_token(identity=__dni, additional_claims={'cabecera': "valor ejemplo"})
#             access_token = create_access_token(identity=__dni, additional_claims={'Bearer': "valor ejemplo"})
#             # esto no es
#             # access_token = create_access_token(identity=__dni, additional_claims={'cabecera': "valor ejemplo", 'dni': __dni})
#             # print("print access_token", get_jwt_identity()('dni'))
#             # dni_claim = get_jwt_identity().get('dni')
#             # print("print access_token", dni_claim)
#             validador = validarTokenCreado(access_token, __dni)
#             if validador:
#                 return jsonify({"mensaje": access_token, "estado": True})
#             else:
#                 return jsonify({"mensaje": "Error al validar token", "estado": False})
#         else:
#             return jsonify({"mensaje": "Correo o contraseña incorrecta", "estado": False})
#     except Exception as ex:
#         resultado = f"Error: {ex.__str__()}"
#         print(f"Error: {ex}")
#         exito = False
@validarLogin.route('/loginctc', methods=['POST'])
@cross_origin()
def login():
    try:
        __dni = request.json.get('dniUser')
        __pass = request.json.get('PasswordTrabajador')

        if validar_credenciales(__dni, __pass):
            access_token = create_access_token(identity=__dni)  # DNI como identidad del token
            print("access_token")
            print(access_token)
            validador = validarTokenCreado(access_token, __dni)
            # return jsonify({"mensaje": access_token, "estado": True})
            if validador:
                return jsonify({"mensaje": access_token, "estado": True})
            else:
                return jsonify({"mensaje": "Error al validar token", "estado": False})
        else:
            return jsonify({"mensaje": "Correo o contraseña incorrecta", "estado": False})
    except Exception as ex:
        return jsonify({"mensaje": f"Error: {ex}", "estado": False})

@validarLogin.route('/protectedctc/', methods=['GET'])
@jwt_required()
@cross_origin()
def protected():
    """
    Accede a una ruta protegida que requiere autenticación.
    Returns:
        Una respuesta JSON con el resultado de la consulta y el estado de éxito.
    """
    # token = request.headers.get('Authorization').split('cabecera')[0]
    # token = request.headers.get('Authorization').split('cabecera')[1].strip()
    current_user_identity = get_jwt_identity()
    print("Identidad del JWT:", current_user_identity)
    # token = token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    # token2 = request.headers.get('Authorization').split('cabecera')[1]
    exito = True
    print("valor del tokennnnn:", token)
    try:
        # Extrayendo 'dni' de las reclamaciones adicionales
        # dni_claim = get_jwt_identity().get('dni')
        # print("valor del dni_claim", dni_claim)
        
        # sql = "SELECT CorreoTrabajador FROM `trabajador` WHERE validarTKN = %s"
        sql = "SELECT dni FROM usuario WHERE validarTKN = %s"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, token)
        # dni_claim = get_jwt_identity()('dni')
        # dni_claim = get_jwt_identity().get('dni')
        # print("valor dni_claim: ", get_jwt_identity()["cabecera"])
        dato = cursor.fetchone()
        if dato is not None:
            # resultado = {"TKN": dato[0]}
            resultado = {"TKN": dato}
            # resultado = {"TKN": dato[0], "dni": get_jwt_identity().get('dni')}
        else:
            resultado = "NO TIENES TOKEN"
            exito = False
            print("valor del resultado en protected: ", resultado)
        cursor.close()
        # print("Reclamaciones del token:", get_jwt_identity())
        # dni_claim = get_jwt_identity().get('dni')
        # print("Valor del dni_claim:", dni_claim)

    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        print(f"Error: {ex}")
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})


# def validar_credenciales(dni):
def validar_credenciales(dni, contra):

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
        # print("valor del resultado[0] en validar_credenciales", resultado[0])
        return resultado[0] > 0
    except Exception as e:
        return False
    finally:
        cursor.close()
def validarTokenCreado(token, correo):
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

@validarLogin.route('/validarUser/', methods=['GET'])
def validarUser():
    # token = request.headers.get('Authorization').split('cabecera')[1]
    token = request.headers.get('Authorization').split('Bearer ')[1]
    print("valor del token en validarUser:", token)
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
        # print("valor del resultado: ", resultado)
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})


def validarTipoUserA():
    # print("entro a validar _ credenciales principal")
    try:
        # token = request.headers.get('Authorization').split('cabecera')[1]
        token = request.headers.get('Authorization').split('Bearer ')[1]
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


# def obtenerDNI():
#     """
#     Accede a una ruta protegida que requiere autenticación.

#     Returns:
#         Una respuesta JSON con el resultado de la consulta y el estado de éxito.
#     """
#     # token = request.headers.get('Authorization').split('cabecera')[1]
#     token = request.headers.get('Authorization').split('Bearer ')[1]
#     print("valor del token en validarUser:", token)
#     exito = True
#     try:
#         # sql = "SELECT CorreoTrabajador FROM `trabajador` WHERE validarTKN = %s"
#         sql = "SELECT dni FROM usuario WHERE validarTKN = %s"
#         conector = mysql.connect()
#         cursor = conector.cursor()
#         cursor.execute(sql, token)
#         dato = cursor.fetchone()
#         if dato is not None:
#             resultado = {"TKN": dato[0]}
#         else:
#             resultado = "NO TIENES TOKEN"
#             exito = False
#         # print("valor del resultado: ", resultado)
#         cursor.close()
#     except Exception as ex:
#         resultado = f"Error: {ex.__str__()}"
#         exito = False
#     return resultado
        
def obtenerDNI(token):
    try:
        sql = "SELECT dni FROM usuario WHERE validarTKN = %s"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, [token])  # Asegúrate de pasar el token como una lista
        dato = cursor.fetchone()
        cursor.close()
        if dato:
            return dato[0]  # Retorna directamente el DNI
        return None
    except Exception as ex:
        print(f"Error al obtener DNI: {ex}")
        return None