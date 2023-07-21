from flask import Blueprint, jsonify, request
from util.Connection import Connection

conexion = Connection()
categoria = Blueprint('categoria', __name__)
mysql = conexion.mysql

@categoria.route("/categoria/sel/", methods = ["GET"])
def categoriaSel():
    '''
    En esta funcion llama a la lista de categorias

    Returns:
        Un json que tiene todos los detalles de categoria y el exito
    '''
    resultado = []
    exito = True
    try:
        sql = "SELECT IDCategoria, NomCategoria FROM categoria;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql)
        datos = cursor.fetchall()
        if len(datos) == 0:
            resultado = "No existen datos en la tabla"
            exito = False
        else:
            resultado = [{
                "IDCategoria": fila[0],
                "NomCategoria": fila[1]
            } for fila in datos]
        cursor.close()
    except Exception as ex:
        resultado = "Ocurrio un error: " + repr(ex)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

@categoria.route("/categoria/get/<int:id>/", methods = ["GET"])
def categoriaGet(id):
    '''
    En esta funcion llama a la categoria por ID

    Args:
        id: viene ser el IdCategoria
    Returns:
        Un json que lleva al detalle de categoria por id y el exito
    '''
    exito = True
    try:
        sql = "SELECT IDCategoria, NomCategoria FROM categoria WHERE IDCategoria = %s;"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, id)
        dato = cursor.fetchone()
        if dato != None:
            resultado = {
                "IDCategoria": dato[0],
                "NomCategoria": dato[1]
            }
        else:
            resultado = "No se ha encontrado al empleado"
            exito = False
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

@categoria.route("/categoria/ins/", methods = ["POST"])
def categoriaIns():
    '''
    En esta funcion se inserta una nueva categoria

    Returns:
        Un json que lleva al mensaje confirmacion y el exito
    '''
    try:
        __nombreCategoria = request.form["txtNomCategoria"]
        sql = "INSERT INTO categoria(`NomCategoria`) VALUES(%s);"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, __nombreCategoria)
        conector.commit()
        mensaje = "Se realizó el registro de la categoria con éxito"
        exito = True
        cursor.close()
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
        exito = False
    return jsonify({"mensaje": mensaje, "exito": exito})

@categoria.route("/categoria/upd/<int:id>/", methods = ["PUT"])
def categoriaUpd(id):
    '''
    En esta funcion actualiza una categoria llamado por ID

    Args:
        id: viene ser el IdCategoria
    Returns:
        Un json que lleva al mensaje confirmacion de la actualizacion y el exito
    '''
    try:
        __nombreCategoria = request.form["txtNomCategoria"]
        sql = "UPDATE categoria SET NomCategoria = %s WHERE IDCategoria = %s;"
        datos = [__nombreCategoria, id]
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, datos)
        conector.commit()
        mensaje = "Se realizó la actualizacion de la categoria con éxito"
        exito = True
        cursor.close()
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
        exito = False
    return jsonify({"mensaje": mensaje, "exito": exito})

@categoria.route('/categoria/del/<int:id>/', methods=["DELETE"])
def categoriaDel(id):
    '''
    En esta funcion elimina una categoria por ID
    
    Args:
        id: viene ser el IdCategoria
    Returns:
        Un json que lleva al mensaje confirmacion de la eliminacion y el exito
    '''
    try:
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.callproc('DeleteCategoria', [id])
        conector.commit()
        mensaje = f"Se ha borrado la categoria con el id {id}"
        exito = True
        cursor.close()
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
        exito = False
    return jsonify({"mensaje": mensaje, "exito": exito})