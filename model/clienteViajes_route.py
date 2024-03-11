from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import create_access_token
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required, get_jwt_identity
from model.validarLogin_route import obtenerDNI
from datetime import datetime
from util.Connection import Connection

clienteViaje = Blueprint('clienteViaje', __name__)
conexion = Connection()
mysql = conexion.mysql
# Ruta para el inicio de sesión
@clienteViaje.route('/selViaje/', methods=["POST"])
@jwt_required()
def login():
    print("ESTOY UN PASO ANTES EL TRY")
    try:
        print("INGRESE AL TRY")
        __valorOrigen = request.json.get('jsonOrigen')
        __valorDestino = request.json.get('jsonDestino')
        __valorFecha = request.json.get('jsonFecha')
        print("__valorOrigen:", __valorOrigen)
        print("__valorDestino:", __valorDestino)
        print("__valorFecha:", __valorFecha)
        # Primero, convertimos la cadena a un objeto datetime usando el formato correcto
        fecha_obj = datetime.strptime(__valorFecha, "%m/%d/%Y")

        # Luego, lo convertimos al formato deseado
        fecha_formateada = fecha_obj.strftime("%Y-%m-%d")

        print("__valorFecha Formateada:", fecha_formateada)
        print("Formateada:", fecha_formateada)
        # fecha_añoMesDia = datetime.strptime(__valorFecha, "%d/%m/%Y")
        # fecha_añoMesDia = fecha_añoMesDia.date()
        # print("__valorFechaCAMBIADA:", fecha_formateada)
        __valueTKN = request.json.get('mitkn')
        # __dniValue = getDNI(__valueTKN)
        # Almacenamiento de las validaciones en un arreglo
        # validaciones = [fecha_valida, hora_valida, carro_valido, asientos_validos, costo_valido, tipo_pago_valido]
        validaciones = [1]
        # Validación de que todos los elementos del arreglo son True
        validacion_total = all(validaciones)
        print("validacion_total", validacion_total)
        resultado = []
        exito = True
        try:
            # sql = "SELECT idRuta, puntoInicio, puntoFin, horaPartida, costo, asientos FROM rutas WHERE estadoViaje = 0;"
            sql = "SELECT idRuta, puntoInicio, puntoFin, horaPartida, costo, asientos FROM rutas WHERE estadoViaje = 0 AND puntoInicio LIKE %s AND puntoFin LIKE %s AND DATE(horaPartida) = %s ORDER BY 1 ASC;"
            conector = mysql.connect()
            cursor = conector.cursor()
            # datos = ('%' + __valorOrigen + '%', '%' + __valorDestino + '%', f"'"+ fecha_formateada + f"'")
            datosSQL = ('%' + __valorOrigen + '%', '%' + __valorDestino + '%', fecha_formateada)
            cursor.execute(sql, datosSQL)
            datosSQL = cursor.fetchall()
            print("VALORES DE DATOS:", datosSQL)
            print("VALOR DEL SQL:", sql)
            if len(datosSQL) == 0:
                resultado = f"no info"
                exito = False
            else:
                resultado = [{
                    "viajeID": fila[0],
                    "inicioViaje": fila[1],
                    "finViaje": fila[2],
                    "hora": fila[3],
                    "costo": fila[4],
                    "asientos": fila[5]
                } for fila in datosSQL]
            cursor.close()
        except Exception as ex:
            resultado = "Ocurrio un error: " + repr(ex)
            exito = False
        return jsonify({"mensaje": resultado, "exito": exito})
    except Exception as e:
        # Aquí manejas el error general, puedes ser más específico con el tipo de excepción si lo deseas
        return jsonify({"mensaje": f"Error en el servidor: {str(e)}", "estado": False}), 500

# @clienteViaje.route('/protectedctc', methods=['GET'])
# @jwt_required()
# @cross_origin()
# def protected():

#     # token = request.headers.get('Authorization').split('cabecera')[1]
#     token = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
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
#         cursor.close()
#     except Exception as ex:
#         resultado = f"Error: {ex.__str__()}"
#         exito = False
#     return jsonify({"resultado": resultado, "exito": exito})

# def validar_credenciales(dni):
def validar_credenciales(dni, contra):
    try:
        sql = "SELECT COUNT(*) FROM usuario WHERE dni = %s AND pass = %s AND tipoUser = 1;"
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

@clienteViaje.route('/validarUser', methods=['GET'])
def validarUser():
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
    try:
        token = request.headers.get('Authorization').split('cabecera')[1]
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

def getDNI(token):
    try:
        # sql = "SELECT CorreoTrabajador FROM `trabajador` WHERE validarTKN = %s"
        sql = "SELECT dni FROM usuario WHERE validarTKN = %s"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, token)
        dato = cursor.fetchone()
        if dato is not None:
            # resultado = {"TKN": dato[0]}
            resultado = dato[0]
        else:
            resultado = "NO TIENES TOKEN"
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
    return resultado

def validar_fecha(fecha_str):
    """Valida que la fecha sea igual o posterior a hoy y la devuelve en formato 'DD-MM-YYYY' si es válida."""
    try:
        fecha = datetime.strptime(fecha_str, "%m/%d/%Y")  # Asegurarse que el formato de entrada sea correcto
        hoy = datetime.now()
        if fecha.date() >= hoy.date():
            # return True, fecha.strftime("%d-%m-%Y")  # Devuelve la fecha en el formato deseado
            return True, fecha.strftime("%Y-%m-%d")  # Devuelve la fecha en el formato deseado
        else:
            return False, ""
    except ValueError as e:
        return False, str(e)

def validar_hora(hora_str):
    """Valida que la hora esté en el formato 'HH:MM' y elimina AM o PM si está presente."""
    try:
        # Primero intentamos parsear la hora considerando que puede tener AM o PM
        formatos_posibles = ["%I:%M %p", "%H:%M"]  # Formatos 12 y 24 horas
        hora_objeto = None
        for formato in formatos_posibles:
            try:
                hora_objeto = datetime.strptime(hora_str, formato)
                break  # Si el parsing es exitoso, salimos del bucle
            except ValueError:
                continue  # Si falla, intentamos con el siguiente formato
        if hora_objeto is None:
            return False, "Formato de hora inválido."
        # Convertimos a formato 24 horas sin AM/PM
        hora_sin_am_pm = hora_objeto.strftime("%H:%M")
        print("Hora sin AM/PM:", hora_sin_am_pm)
        return True, hora_sin_am_pm  # Devolvemos True y la hora ajustada
    except ValueError:
        return False, "Formato de hora inválido."
    
def juntarHora(fecha, hora):
    # Unir fecha y hora en un solo string
    print("segundos valores", validar_fecha(fecha))
    print("primeros valores", validar_hora(hora))
    fecha_hora_str = f"{validar_fecha(fecha)[1]} {validar_hora(hora)[1]}"
    # Convertir a objeto datetime
    fecha_hora_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")
    return fecha_hora_obj

def validar_entero(valor_str):
    """Valida que el valor sea un número entero."""
    return valor_str.isdigit()

def validar_numero(valor_str):
    """Valida que el valor sea un número (entero o decimal)."""
    try:
        float(valor_str)
        return True
    except ValueError:
        return False
    
def validar_rango_pago(pago_str):
    """Valida que el tipo de pago esté en el rango [1, 2]."""
    try:
        pago = int(pago_str)  # Intenta convertir a entero
        print("valorpago", pago_str)
        if 1 <= pago <= 2:
            print("valor de validarRANGOPAGO:", pago)
            return True  # Si está en el rango, retorna True
        else:
            print("VALOR FUERA DE RANGO")  # Informa si está fuera de rango
            return False
    except ValueError:
        # Si la conversión a entero falla, significa que no era un entero válido
        print("VALOR NO ES UN ENTERO")
        return False