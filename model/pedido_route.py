from flask import Blueprint, jsonify
from util.Connection import Connection
import datetime
import locale
import qrcode
import base64
from io import BytesIO


conexion = Connection()
pedido = Blueprint('pedido', __name__)
mysql = conexion.mysql
rucEmpresa = "20567894561"
direccionEmpresa = "AV. Tupac Amaru, Chorrillos, Lima, Perú"

@pedido.route('/pedido/dtoPedidoVenta/<int:idVenta>/')
def pedidoDtoVenta(idVenta):
    '''
    Esta funcion selecciona todos los detalle del pedidoventa

    Args:
        idVenta: Es el id de venta
    Returns:
        Un json que contiene un mensaje de éxito o error y los detalles del pedido por venta
    '''
    resultado = []
    exito = True
    try:
        sql = "SELECT CodPedido, Total, puntajePedido, HOUR(`horarioPedido`), MINUTE(`horarioPedido`), trabajador.`NomTrabajador` FROM pedido INNER JOIN venta ON pedido.`IDVenta` = venta.`IDVenta` INNER JOIN trabajador ON pedido.`CodTrabajador` = trabajador.`CodTrabajador` WHERE venta.`IDVenta` = %s AND pedido.`EstadoPedido` = '1';"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, idVenta)
        datos = cursor.fetchall()
        if len(datos) == 0:
            resultado = "No existen datos en la tabla pedido con dicha venta"
            exito = False
        else:
            for fila in datos:
                pedido = {
                    "CodPedido": fila[0],
                    "Total": fila[1],
                    "puntajePedido": fila[2],
                    "hora": fila[3],
                    "minuto": fila[4],
                    "NomTrabajador": fila[5]
                }
                horario = datetime.time(pedido["hora"], pedido["minuto"], 0)
                pedido["horarioPedido"] = horario.strftime("%H:%M")
                del pedido["hora"]
                del pedido["minuto"]
                resultado.append(pedido)
        cursor.close()
    except Exception as ex:
        resultado = "Ocurrio un error: " + repr(ex)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

locale.setlocale(locale.LC_TIME, 'es_ES')
@pedido.route("/PDF/sel/<int:codCliente>/", methods=["GET"])
def datosPDF(codCliente):
    """
    Genera los datos necesarios para generar un PDF

    Args:
        codCliente: El código del cliente
    Returns:
        Un json con los datos para generar el PDF y el indicador de éxito.
    """
    resultado = {}
    exito = True
    try:
        sql = "SELECT p.NombrePlatillo, p.Precio, dp.Cantidad, dp.SubTotal FROM detallepedido dp INNER JOIN platillo p ON dp.CodigoPlatillo = p.CodigoPlatillo WHERE dp.CodPedido = %s;"
        sql2 = "SELECT SUM(dp.SubTotal) AS Total, pe.direccion, v.Fecha, pe.horarioPedido FROM detallepedido dp INNER JOIN platillo p ON dp.CodigoPlatillo = p.CodigoPlatillo INNER JOIN pedido pe ON dp.CodPedido = pe.CodPedido INNER JOIN venta v ON pe.IDVenta = v.IDVenta WHERE dp.CodPedido = %s;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, codCliente)
        arreglo = cursor.fetchall()
        if len(arreglo) == 0:
            resultado = "No hay datos en la tabla Cliente"
        else:
            resultado["detalles"] = []
            for fila in arreglo:
                DatosPDF = {
                    "nombre": fila[0],
                    "pUnitario": fila[1],
                    "cantidad": fila[2],
                    "subTotal": fila[3]
                }
                resultado["detalles"].append(DatosPDF)
            exito = True
            resultado["total"] = []

            cursor.execute(sql2, codCliente)
            total = cursor.fetchone()
            horas = str(total[3])
            horas2 = horas.split(':')[0]
            minutos = str(total[3])
            minutos2 = minutos.split(':')[1]
            segundos = str(total[3])
            segundos2 = segundos.split(':')[2]
            lafecha = total[2].strftime("%d%m%Y")
            fechaQR = total[2].strftime("%d-%m-%Y")
            lafecha2 = total[2].strftime("%d de %B de %Y")
            numBoleta = f"{lafecha}{horas2}{minutos2}{segundos2}"
            codigo_qr_datos = f"Boleta: {numBoleta}\nMonto: {total[0]}\nFecha: {fechaQR}\nCodPedido: {codCliente}"
            codigo_qr_base64 = generar_codigo_qr(codigo_qr_datos)

            resultado["codigoQR"] = codigo_qr_base64
            resultado["total"] = [total[0], total[1], lafecha2, numBoleta, rucEmpresa, direccionEmpresa]

    except Exception as e:
        resultado = f"Error: {e.__str__()}"
    return jsonify({"resultado": resultado, "exito": exito, "numBoleta": resultado["total"][3], "horaBoleta": lafecha2})

@pedido.route("/valoresFactura/<int:codCliente2>/", methods=["GET"])
def tablaFactura(codCliente2):
    """
    Genera una tabla de facturas para un cliente en específico

    Args:
        codCliente2: El código del cliente
    Returns:
        Un json con la tabla factura y el indicador de exito
    """
    resultado = {}
    exito = True
    try:
        sql = "SELECT p.Direccion, p.horarioPedido, v.Fecha, p.EstadoPedido, p.CodPedido FROM pedido p INNER JOIN detallepedido d ON p.CodPedido = d.CodPedido INNER JOIN venta v ON p.IDVenta = v.IDVenta WHERE p.CodCliente = %s GROUP BY p.CodPedido, v.Fecha, p.EstadoPedido ORDER BY MAX(v.Fecha) DESC;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, codCliente2)
        arreglo = cursor.fetchall()
        if len(arreglo) == 0:
            resultado = "No hay datos en la tabla Cliente"
        else:
            resultado["detallesTabla"] = []
            for fila in arreglo:

                datoTabla = {
                    "direccion": fila[0],
                    "horarioPedido": str(fila[1]),
                    "fecha": fila[2].strftime("%d-%m-%Y"),
                    "estadoPedido": fila[3],
                    "CodPedido": fila[4]
                }
                resultado["detallesTabla"].append(datoTabla)
            exito = True
    except Exception as e:
        resultado = f"Error: {e.__str__()}"
    return jsonify({"resultado": resultado, "exito": exito})

def generar_codigo_qr(datos):
    """
    Genera el código QR que usaremos para la boleta

    Args:
        datos: La información a codificar en código QR
    Returns:
        Retorna un validador si la creación de QR es válido o no
    """
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
        qr.add_data(datos)
        qr.make(fit=True)
        # Generar una imagen del código QR
        qr_image = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        qr_image.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return qr_base64
    except Exception as e:
        resultado = f"Error QR: {e.__str__()}"
    return resultado

def pedidoIns(direccion, total, idcliente, cursor):
    """
    Inserta un pedido principal en la base de datos.

    Args:
        direccion: La dirección del pedido.
        total: El total del pedido.
        idcliente: El ID del cliente asociado al pedido.
        cursor: El cursor de la conexión a la base de datos.
    Returns:
        Una lista que contiene el ID del pedido y  éxito.
    """
    exito = True
    try:
        sql = "SELECT crearPedido(%s, %s, %s)"
        cursor.execute(sql, [direccion, total, idcliente])
        resultado = cursor.fetchone()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return [resultado[0], exito]
