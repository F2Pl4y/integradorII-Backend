from flask import Blueprint, jsonify, request
from model.pedido_route import pedidoIns
from model.platillo_route import obtenerPlatillo
from util.Connection import Connection
import traceback

conexion = Connection()
detallepedido = Blueprint("detallepedido", __name__)
mysql = conexion.mysql


@detallepedido.route("/detallepedido/selectDetallePedido/<int:id>/", methods=["GET"])
def pedidoEmpleado(id):
    '''
    Permite seleccionar todos los detalles pedidos por el id pedido

    Args:
        id: Es el id del pedido
    Returns:
        Un json que tiene el listado de detalle pedido y el exito
    '''
    resultado = []
    exito = True
    try:
        sql = "SELECT CodPedido, cantidad, CostoDetalle, p.nombreProducto, p.imagen FROM detallepedido as dp INNER JOIN producto as p ON dp.idProducto = p.idProducto WHERE idPedido = %s;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, id)
        datos = cursor.fetchall()
        if len(datos) == 0:
            resultado = "No existen datos en la tabla"
            exito = False
        else:
            for fila in datos:
                detallepedido = {
                    "idPedido": fila[0],
                    "cantidad": fila[1],
                    "costodetalle": fila[2],
                    "nombreProducto": fila[3],
                    "imagen": fila[4]
                }
                resultado.append(detallepedido)
    except Exception as ex:
        resultado = "Ocurrio un error " + repr(ex)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

@detallepedido.route("/detallepedido/carritoDetalle/", methods=["POST"])
def detalleCarrito():
    '''
    Esta Funcion obtiene los detalles de los productos en el carrito.

    Returns:
        Un json que tiene el listado de los pedidos con sus detalles.
    '''
    arreglo = request.form["carrito"]
    lista = arreglo.split(",")
    resultado = []
    elemento = []
    for i in range(len(lista)):
        if i % 2 == 0:
            producto = obtenerPlatillo(lista[i])
            elemento.append(producto[0]["idProducto"])
            elemento.append(producto[0]["nombreProducto"])
            elemento.append(producto[0]["imagen"])
            elemento.append(float(producto[0]["precio"]))
        else:
            elemento.append(int(lista[i]))
            precioTotal = elemento[4] * elemento[3]
            elemento.append(round(precioTotal, 2))
            resultado.append(elemento)
            elemento = []
    return jsonify({"resultado": resultado})


@detallepedido.route("/detallepedido/ins/", methods=["POST"])
def detalleInsert():
    '''
    Inserta los detalles de un pedido en la base de datos.

    Returns:
        Un json que contiene un mensaje de éxito o error
    '''
    exito = False
    try:
        sql = "INSERT INTO detallepedido(CodPedido, CodigoPlatillo, Cantidad, SubTotal) VALUES (%s, %s, %s, %s);"
        direccion = request.json.get("direccion")
        total = request.json.get("total")
        idcliente = request.json.get("idcliente")
        carrito = request.json.get("carrito")
        conn = mysql.connect()
        cursor = conn.cursor()
        idpedido = pedidoIns(direccion, total, idcliente, cursor)
        if(idpedido[1]):
            for element in carrito:
                datos = []
                platillo = obtenerPlatillo(element[0])
                datos.append(idpedido[0])
                datos.append(element[0])
                datos.append(element[1])
                datos.append(element[1]*platillo[0]["Precio"])
                cursor.execute(sql, datos)
            conn.commit()
            mensaje = "Pedido registrado correctamente"
            exito = True
        else:
            mensaje = "Error al registrar pedido"
        cursor.close()
    except Exception as ex:
        traceback.print_exc()
        mensaje = f"Error: {ex.__str__()}" 
    return jsonify({"resultado":mensaje, "exito": exito})