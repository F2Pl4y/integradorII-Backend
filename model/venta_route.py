# from flask import Blueprint, jsonify
# from util.Connection import Connection

# conexion = Connection()
# venta = Blueprint('venta', __name__)
# mysql = conexion.mysql

# @venta.route('/venta/ventaActual/')
# def ventaActual():
#     """
#     Obtiene información de la venta de la fecha actual

#     Returns:
#         Una respuesta JSON con la venta y el exito
#     """
#     exito = True
#     try:
#         sql = "SELECT IDVenta, Fecha, Recaudado FROM venta WHERE `Fecha` = DATE_FORMAT(NOW(), '%Y-%m-%d')"
#         conector = mysql.connect()
#         cursor = conector.cursor()
#         cursor.execute(sql)
#         dato = cursor.fetchone()
#         if dato != None:
#             resultado = {
#                 "IDVenta": dato[0],
#                 "Fecha": dato[1],
#                 "Recaudado": dato[2]
#             }
#         else:
#             resultado = "No existe una venta para la fecha actual"
#             exito = False
#         cursor.close()
#     except Exception as ex:
#         resultado = f"Error: {ex.__str__()}"
#         exito = False
#     return jsonify({"resultado": resultado, "exito": exito})

# @venta.route('/venta/sel/')
# def ventaSel():
#     """
#     Obtiene la lista de ventas ordenadas por fecha en orden descendente.

#     Returns:
#         Una respuesta JSON con la lista de ventas y el estado de éxito.
#     """
#     resultado = []
#     exito = True
#     try:
#         sql = "SELECT IDVenta, Fecha, Recaudado FROM venta ORDER BY Fecha DESC"
#         conector = mysql.connect()
#         cursor = conector.cursor()
#         cursor.execute(sql)
#         datos = cursor.fetchall()
#         if len(datos) == 0:
#             resultado = f"No existen datos en la tabla venta"
#             exito = False
#         else:
#             for fila in datos:
#                 venta = {
#                     "IDVenta": fila[0],
#                     "Fecha": fila[1],
#                     "Recaudado": fila[2]
#                 }
#                 resultado.append(venta)
#         cursor.close()
#     except Exception as ex:
#         resultado = "Ocurrio un error: " + repr(ex)
#         exito = False
#     return jsonify({"resultado": resultado, "exito": exito})
