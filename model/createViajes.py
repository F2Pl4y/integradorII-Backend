from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from model.validarLogin_route import obtenerDNI
# from datetime import datetime
from model.validaciones import *
from util.Connection import Connection

createViaje = Blueprint('createViaje', __name__)
conexion = Connection()
mysql = conexion.mysql

# Ruta para el inicio de sesión
@createViaje.route('/regViaje/', methods=["POST"])
@jwt_required()
def regViaje():
    try:
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
        __valueTKN = request.json.get('mitkn')
        __dniValue = getDNI(__valueTKN)
        # Validaciones
        fecha_valida = validar_fecha(__datePart)
        hora_valida = validar_hora(__timePart)
        carro_valido = convertir_a_string(__carSel)
        asientos_validos = validar_entero(__asiCant)
        costo_valido = validar_numero(__costPasaje)
        tipo_pago_valido = validar_rango_pago(__pagoType)
        fechaUnida = juntarHora(__datePart, __timePart)
        # Almacenamiento de las validaciones en un arreglo
        validaciones = [fecha_valida, hora_valida, carro_valido, asientos_validos, costo_valido, tipo_pago_valido]
        # Validación de que todos los elementos del arreglo son True
        validacion_total = all(validaciones)
        print("VALIDACIONES:", validaciones)
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT tipoUser FROM usuario WHERE dni = %s", (__dniValue,))
        result = cursor.fetchone()
        # tipo_usuario = result['tipoUser'] if result else None
        tipo_usuario = result
        print("valor de tipo_usuario:", tipo_usuario[0])
        print("valor de validacion_total:", validacion_total)
        if (validacion_total and tipo_usuario[0]==2):
            sql = "INSERT INTO rutas (dnifkrutas, puntoInicio, puntoFin, horaPartida, tipoPago, costo, detalleInicio, detalleFin, vehiculo, asientos, estadoViaje) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            conn = mysql.connect()
            cursor = conn.cursor()
            datos = [__dniValue, __viajeA, __viajeB, fechaUnida, __pagoType, __costPasaje, __detViajeA, __detViajeB, __carSel, __asiCant, 0]
            cursor.execute(sql, datos)
            conn.commit()
            mensaje = "viaje creado"
            exito = True
            cursor.close()
            validador = validarTokenCreado(__valueTKN, __dniValue)
            if validador:
                return jsonify({"mensaje": mensaje, "estado": exito})
            
            return jsonify({"mensaje": mensaje, "exito": exito})
        else:
            return jsonify({"mensaje": f"no se registro", "estado": True})
    except Exception as e:
        # Aquí manejas el error general, puedes ser más específico con el tipo de excepción si lo deseas
        return jsonify({"mensaje": f"Error en el servidor: {str(e)}", "estado": False}), 500


@createViaje.route('/selVehic/', methods=['GET'])
@jwt_required()
def selVehic():
    __valueDNI = get_jwt_identity()
    print("Identidad DEL VALORRRRRR:", __valueDNI)
    exito = True
    try:
        sql = "SELECT marcaV, modeloV, numPlaca, numAsientos FROM vehiculo WHERE dnifkvehi = %s;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, __valueDNI)
        dato = cursor.fetchall()
        if len(dato) == 0:
            resultado = f"no info"
            exito = False
        else:
            # print("VALOR DEL DATO:", dato)
            resultado = [{
                "marca": fila[0],
                "modelo": fila[1],
                "placa": fila[2],
                "asientos": fila[3]
            } for fila in dato]
            exito = True
        cursor.close()
    except Exception as ex:
        resultado = f"Excepcion: {ex.__str__()}"
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})


@createViaje.route('/validarUser', methods=['GET'])
def validarUser():
    token = request.headers.get('Authorization').split('cabecera')[1]
    exito = True
    try:
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



@createViaje.route('/selViaUserIna/', methods=['GET'])
@jwt_required()
def selViaUserIna():
    __valueDNI = get_jwt_identity()
    print("Identidad DEL VALORRRRRR:", __valueDNI)
    exito = True
    try:
        # sql = "SELECT * FROM viajes WHERE dnifkviajes = %s AND estadoviaje = 1;"
        sql = "SELECT puntoInicio, puntoFin, horaPartida, costo FROM viajes WHERE dnifkviajes = %s AND estadoviaje = 1;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, __valueDNI)
        dato = cursor.fetchall()
        if len(dato) == 0:
            resultado = f"no info"
            exito = False
        else:
            # print("VALOR DEL DATO:", dato)
            # resultado = dato
            resultado = [{
                "inicio": fila[0],
                "final": fila[1],
                "fechaPart": fila[2],
                # "horaPart": fila[3],
                "monto": fila[3]
            } for fila in dato]
            exito = True
        cursor.close()
    except Exception as ex:
        resultado = f"Excepcion: {ex.__str__()}"
        print("valor del resultado:", resultado)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

@createViaje.route('/selViaUserAct/', methods=['GET'])
@jwt_required()
def selViaUserAct():
    __valueDNI = get_jwt_identity()
    print("Identidad DEL VALORRRRRR:", __valueDNI)
    exito = True
    try:
        sql = "SELECT puntoInicio, puntoFin, horaPartida, costo FROM viajes WHERE dnifkviajes = %s AND estadoviaje = 0;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, __valueDNI)
        dato = cursor.fetchall()
        if len(dato) == 0:
            resultado = f"no info"
            exito = False
        else:
            # print("VALOR DEL DATO:", dato)
            # resultado = dato
            resultado = [{
                "inicio": fila[0],
                "final": fila[1],
                "fechaPart": fila[2],
                # "horaPart": fila[3],
                "monto": fila[3]
            } for fila in dato]
            exito = True
        cursor.close()
    except Exception as ex:
        resultado = f"Excepcion: {ex.__str__()}"
        print("valor del resultado:", resultado)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})










def validar_credenciales(dni, contra):
    try:
        sql = "SELECT COUNT(*) FROM usuario WHERE dni = %s AND pass = %s AND tipoUser = 1;"
        conector = mysql.connect()
        cursor = conector.cursor()
        datos = (dni, contra)
        cursor.execute(sql, datos)
        resultado = cursor.fetchone()
        return resultado[0] > 0
    except Exception as e:
        print(f"Error: {e.__str__()}")
        return False
    finally:
        cursor.close()


def validarTokenCreado(token, correo):
    try:
        sql = "UPDATE usuario SET validarTKN = %s WHERE dni = %s;"
        conector = mysql.connect()
        cursor = conector.cursor()
        datos = (token, correo)
        cursor.execute(sql, datos)
        conector.commit()
        return True
    except Exception as e:
        print(f"Error: {e.__str__()}")
        return False
    finally:
        cursor.close()


def validarTipoUserA():
    try:
        token = request.headers.get('Authorization').split('cabecera')[1]
        sql = "SELECT tipou.nombre FROM usuario JOIN tipou ON usuario.tipoUser = tipou.idTipo WHERE usuario.validarTKN = %s"
        conector = mysql.connect()
        cursor = conector.cursor()
        datos = (token)
        cursor.execute(sql, datos)
        resultado = cursor.fetchone()
        # p rint("valor del resultado[0]", resultado[0])
        return resultado[0] > 0
    except Exception as e:
        print(f"Error: {e.__str__()}")
        return False
    finally:
        cursor.close()


def getDNI(token):
    try:
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

