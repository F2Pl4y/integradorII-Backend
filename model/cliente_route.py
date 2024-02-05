# from flask import Blueprint, jsonify, request, make_response
# from util.Connection import Connection
# from flask_jwt_extended import create_access_token

# conexion = Connection()
# cliente = Blueprint('cliente', __name__)
# mysql = conexion.mysql

# @cliente.route("/cliente/sel/", methods=["GET"])
# def clienteSel():
#     '''
#     Esta función lista todos los clientes del restaurante

#     Returns:
#         Un json que contiene el listado de clientes
#     '''
#     resultado = []
#     exito = False
#     try:
#         sql = "SELECT CodCliente, CorreoCliente, DNI, NomCliente, TelefonoCliente  FROM cliente;"
#         conector = mysql.connect()
#         cursor = conector.cursor()
#         cursor.execute(sql)
#         arreglo = cursor.fetchall()
#         if len(arreglo) == 0:
#             resultado = "No hay datos en la tabla Cliente"
#         else:
#             for fila in arreglo:
#                 DatosCliente = {
#                     "CodCliente": fila[0],
#                     "CorreoCliente": fila[1],
#                     "DNI": fila[2],
#                     "NomCliente": fila[3],
#                     "TelefonoCliente": fila[4]
#                 }
#                 resultado.append(DatosCliente)
#             exito = True
#     except Exception as e:
#         resultado = f"Error: {e.__str__()}"
#     return jsonify({"resultado": resultado, "exito": exito})

# @cliente.route("/cliente/ins/", methods=["POST"])
# def clienteIns():
#     '''
#     Esta función inserta nuevos clientes del restaurante

#     Returns:
#         json: Mensaje de confirmacion 
#     '''
#     exito = False
#     try:
#         __correoCliente= request.form["txtCorreoCliente"]
#         __dni = request.form["txtDNI"]
#         __nomCliente = request.form["txtNomCliente"]
#         __passwordCliente = request.form["txtPasswordCliente"]
#         __telefonoCliente = request.form["txtTelefonoCliente"]

#         access_token = create_access_token(identity=__correoCliente, additional_claims={'cabecera': "valor ejemplo"})
#         sql = "INSERT INTO cliente(CorreoCliente, DNI, NomCliente, PasswordCliente, TelefonoCliente, validarTKN) VALUES (%s, %s, %s, AES_ENCRYPT(%s,%s), %s, %s);"
#         conn = mysql.connect()
#         cursor = conn.cursor()
#         datos = [__correoCliente, __dni, __nomCliente, __passwordCliente, __passwordCliente, __telefonoCliente, access_token]
#         cursor.execute(sql, datos)
#         conn.commit()

#         validarTokenCreado(access_token, __correoCliente)

#         response = make_response(jsonify({"valorMensaje": access_token}))
#         response.set_cookie('access_token', access_token, httponly=True)
#         mensaje = "Cliente registrado correctamente"
#         exito = True
#     except Exception as e:
#          mensaje = f"Error: {e.__str__()}"
#     return jsonify({"mensaje": mensaje, "exito": exito, "miAccessToken": access_token})

# def validarTokenCreado(token, correo):
#     '''
#     Esta función valida un usuario por token y correo

#     Args:
#         token: Viene ser el validarTKN
#         correo: Viene ser el CorreoCliente
#     Returns:
#         retorna un booleano indicando el exito de la función
#     '''
#     exito = True
#     try:
#         sql = "UPDATE cliente SET validarTKN = %s WHERE CorreoCliente = %s;"
#         conector = mysql.connect()
#         cursor = conector.cursor()
#         datos = (token, correo)
#         cursor.execute(sql, datos)
#         conector.commit()
#     except Exception as e:
#         exito = False
#     finally:
#         cursor.close()
#     return exito

# @cliente.route('/cliente/loginCli/', methods=['POST'])
# def login():
#     '''
#     Esta función valida el inicio de sesion del cliente

#     Returns:
#         Un json que contiene el token de acceso
#     '''
#     estado = False
#     mensaje = "Correo o contraseña incorrecta"
#     __correo = request.json.get('CorreoCliente')
#     __password = request.json.get('PasswordCliente')
#     if (validar_credenciales(__correo, __password)):
#         access_token = create_access_token(identity="usuariolog")
#         estado = validarTokenCreado(access_token, __correo)
#         mensaje = access_token
#     return jsonify({"mensaje": mensaje, "estado":estado})

# # Ruta protegida
# @cliente.route('/secureCli', methods=['GET'])
# def protected():
#     '''
#     Permite validar si el token existe.

#     Retorna:
#         Un json con la información del cliente
#     '''
#     token = request.headers.get('Authorization').split('Token ')[1]
#     exito = False
#     try:
#         sql = "SELECT CodCliente, CorreoCliente, DNI, NomCliente, TelefonoCliente FROM `cliente` WHERE validarTKN = %s;"
#         conector = mysql.connect()
#         cursor = conector.cursor()
#         cursor.execute(sql, token)
#         dato = cursor.fetchone()
#         resultado = dato if dato is not None else "No existe el usuario"
#         exito = dato is not None
#         cursor.close()
#     except Exception as ex:
#         resultado = f"Error: {ex.__str__()}"
#     return jsonify({"resultado": resultado, "exito": exito})

# def validar_credenciales(correo, password):
#     '''
#     Valida las credenciales de un cliente.

#     Args:
#         correo: El correo electrónico del cliente.
#         password: La contraseña del cliente.
#     Returns:
#         Un booleano validador
#     '''
#     resultado = False
#     try:
#         sql = "SELECT CodCliente FROM cliente WHERE CorreoCliente = %s AND PasswordCliente = AES_ENCRYPT(%s, %s);"
#         conector = mysql.connect()
#         cursor = conector.cursor()
#         datos = (correo, password, password)
#         cursor.execute(sql, datos)
#         resultado = cursor.fetchone()
#     except Exception as e:
#         resultado = False
#     finally:
#         cursor.close()
#     return resultado
