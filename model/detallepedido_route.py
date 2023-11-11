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
        # print("VALORESSSS",direccion)
        # print("VALORESSSS",total)
        # print("VALORESSSS",idcliente)
        # print("VALORESSSS",cursor)
        # print("VALORESSSS",idpedido)
        # print("22222222",idpedido[2])
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


# ------ FINAL PARA PUNTAJE ------
@detallepedido.route("/puntaje/insdp/", methods = ["POST"])
def puntajeInsDP():
    '''
    Se inserta un cargo Nuevo

    Returns:
        Un json que tiene mensaje de validacion y el exito
    '''
    exito = False
    try:
        __miPuntaje = int(request.form["puntaje"])
        __nombrePlato = request.form["nombrePlato"]
        __codPlato = request.form["codPlato"]
        __codPedido = int(request.form["codPedido"])

        # print("__codPedido, __codPlato, __miPuntaje", __codPedido, __codPlato, __miPuntaje)
        conector = mysql.connect()
        cursor = conector.cursor()
        if isEmptyPuntajeInsert(__codPedido, __codPlato) == True:
            print("PRIMERA FASE APROBADA", isEmptyPuntajeInsert(__codPedido, __codPlato))
            # print("VACIO----:", __codPlato)
            # print("PRIMERA FASE APROBADA", isEmptyP untajeInsert(__codPedido, __codPlato))
            if 0 < __miPuntaje < 6:
                # print("PASO TO DO")
                sql = "UPDATE detallepedido dp SET dp.puntaje = %s WHERE dp.CodPedido = %s AND dp.CodigoPlatillo = %s;"
                datos = [__miPuntaje, __codPedido, __codPlato]
                cursor.execute(sql, datos)
                conector.commit()
                mensaje = "puntaje insertado correctamente"
                exito = True
                cursor.close()
            else:
                mensaje = "el puntaje debe de ser entre 1 y 5"
                cursor.close()
        else:
            mensaje = "ya se le asigno un puntaje"
        cursor.close()

        # print("PUNTAJE ES: ", mensaje)
        # cursor.close()
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
    return jsonify({"mensaje": mensaje, "exito": exito})


def obtenerDatosPuntaje(id):
    """
    Obtiene los detalles de un trabajador en base a su ID.

    Args:
        id: El ID del trabajador que se desea obtener.
    Returns:
        Una lista que contiene un diccionario con los detalles del trabajador y el éxito.
    """
    exito = True
    try:
        sql = "SELECT p.NombrePlatillo FROM detallepedido dp INNER JOIN platillo p ON dp.CodigoPlatillo = p.CodigoPlatillo WHERE dp.CodPedido = %s;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, id)
        dato = cursor.fetchone()
        if dato != None:
            resultado = {
                "NombrePlatillo": dato[0]
            }
        else:
            resultado = "No se ha encontrado el platillo"
            exito = False
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return [resultado, exito]



# @cargo.route("/puntaje/sel/", methods=["GET"])
@detallepedido.route("/puntaje/seldp/<int:idCargo>/", methods=["GET"])
def trabajadorSelCargoDP(idCargo = None):
    """
    Esta Funcion selecciona a todos los trabajadores por id
    Args: 
        idcargo: viene ser el id de cargo. (default: None)
    Returns:
        Un json que contiene la lista de los trabajadores por idcargo, y el exito
    """
    resultado = []
    exito = True
    try:
        conector = mysql.connect()
        cursor = conector.cursor()
        sql = "SELECT p.NombrePlatillo, p.CodigoPlatillo FROM detallepedido dp INNER JOIN platillo p ON dp.CodigoPlatillo = p.CodigoPlatillo INNER JOIN pedido pe ON dp.CodPedido = pe.CodPedido"
        if idCargo != None:
            sql += " WHERE pe.CodPedido = %s;"
            cursor.execute(sql, [idCargo])
        else:
            cursor.execute(sql)
        datos = cursor.fetchall()
        if len(datos) == 0 and idCargo == None:
            resultado = "No existan datos en la tabla trabajador"
            exito = False
        elif len(datos) == 0 and idCargo != None:
            resultado = f"No existen datos en la tabla trabajador con el cargo {idCargo}"
            exito = False
        else:
            resultado = [{
                "NombrePlatillo": fila[0],
                "CodigoPlatillo": fila[1]
            } for fila in datos]
        cursor.close()
    except Exception as ex:
        resultado = "Ocurrio un error: " + repr(ex)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})


# codPedido

# si EXISTEN valores, entonces es Falso
# si NO EXISTEN valores, es True
def isEmptyPuntajeInsert(codPedido,codPlato):

    try:
        conector = mysql.connect()
        cursor = conector.cursor()

        sql = "SELECT dp.puntaje, p.NombrePlatillo, p.CodigoPlatillo, dp.CodPedido as codigoPedido FROM detallepedido dp INNER JOIN platillo p ON dp.CodigoPlatillo = p.CodigoPlatillo WHERE dp.CodPedido = %s AND dp.CodigoPlatillo = %s;"

        cursor.execute(sql, [codPedido, codPlato])
        # print("datossss:",codPedido, codPlato, codPedido, codPlato)
        datos = cursor.fetchone()
        cursor.close()
        print("info BD:",datos[0])
        if datos[0] == None:
            # print(datos)
            cursor.close()
            return True
        else:
            # print(datos)
            cursor.close()
            return False

    except Exception as ex:
        # if 'cursor' in locals():
        #     cursor.close()
        return False