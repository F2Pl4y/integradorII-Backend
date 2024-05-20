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
    try:
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
        __dniValue = getDNI(__valueTKN)
        print("valor DNI en selViaje:", __dniValue)
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
            sql = "SELECT idRuta, puntoInicio, puntoFin, horaPartida, costo, asientos FROM rutas WHERE estadoViaje = 0 AND puntoInicio COLLATE utf8_general_ci LIKE %s AND puntoFin COLLATE utf8_general_ci LIKE %s AND DATE(horaPartida) = %s AND dnifkrutas <> %s ORDER BY 1 ASC;"
            conector = mysql.connect()
            cursor = conector.cursor()
            # datos = ('%' + __valorOrigen + '%', '%' + __valorDestino + '%', f"'"+ fecha_formateada + f"'")
            datosSQL = ('%' + __valorOrigen + '%', '%' + __valorDestino + '%', fecha_formateada, __dniValue)
            cursor.execute(sql, datosSQL)
            datosSQL = cursor.fetchall()
            # print("VALORES DE DATOS:", datosSQL)
            # print("VALOR DEL SQL:", sql)
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

@clienteViaje.route('/detalleViaje/get/<int:id>', methods=['GET'])
def detViajeGet(id):
    resultado = obtenerDetViaje(id)
    return jsonify({"resultado": resultado[0], "exito": resultado[1]})

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
    
def obtenerDetViaje(id):
    exito = True
    try:
        sql = "SELECT puntoInicio, detalleInicio, puntoFin, detalleFin, horaPartida, costo, asientos, vehiculo, tipoPago FROM rutas WHERE estadoViaje = 0 AND idRuta = %s;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, (id,))  # Asegúrate de pasar id como una tupla
        dato = cursor.fetchone()
        if dato:
            resultado = {
                "inicioViaje": dato[0],
                "detalle1Viaje": dato[1],
                "finViaje": dato[2],
                "detalle2Viaje": dato[3],
                "hora": dato[4],
                "costo": dato[5],
                "asientos": dato[6],
                "vehiculo": dato[7],
                "tPago": dato[8]
            }
        else:
            resultado = "sin datos"
            exito = False
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return [resultado, exito]
