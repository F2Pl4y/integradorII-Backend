from re import match
from flask import Blueprint, jsonify, request
from util.Connection import Connection

conexion = Connection()
cargo = Blueprint('cargo', __name__)
mysql = conexion.mysql
expresiones = {
    'nombreCargo': r'^[\w,\s]{5,30}$',
    'dinero': r'^\d+(.(\d{1,2})?)?$'
}

def comprobar(nombreCargo, dinero):
    return match(expresiones['nombreCargo'], nombreCargo) and match(expresiones['dinero'], dinero)

@cargo.route("/cargo/sel/<int:opcion>/", methods = ["GET"])
def cargoSel(opcion):
    '''
    Esta Función permite seleccionar todos los detalles del Cargo
    
    Args:
        opcion: El ID del cargo que se desea obtener.
    Returns:
        Un json que tiene el listado de los cargos y el exito
    '''
    resultado = []
    exito = True
    try:
        sql = "SELECT IDCargo, NomCargo, Sueldo FROM cargo"
        sql += " WHERE IDCargo != 1;" if (opcion == 1) else ""
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql)
        datos = cursor.fetchall()
        if len(datos) == 0:
            resultado = "No existen datos en la tabla"
            exito = False
        else:
            resultado = [{
                "IDCargo": fila[0],
                "NomCargo": fila[1],
                "Sueldo": fila[2]
            } for fila in datos]
        cursor.close()
    except Exception as ex:
        resultado = "Ocurrio un error: " + repr(ex)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

@cargo.route("/cargo/get/<int:id>/", methods = ["GET"])
def cargoGet(id):
    '''
    Selecciona los detalles de cargo por IDCargo

    Args:
        id: viene ser el IDCargo
    Returns:
        Un json que tiene los datos del cargo solicitado por IDCargo y el exito
    '''
    exito = True
    try:
        sql = "SELECT IDCargo, NomCargo, Sueldo FROM cargo WHERE IDCargo = %s"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, id)
        dato = cursor.fetchone()
        if dato != None:
            resultado = {
                "IDCargo": dato[0],
                "NomCargo": dato[1],
                "Sueldo": dato[2]
            }
        else:
            resultado = "No se ha encontrado el cargo"
            exito = False
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

@cargo.route("/cargo/ins/", methods = ["POST"])
def cargoIns():
    '''
    Se inserta un cargo Nuevo

    Returns:
        Un json que tiene mensaje de validacion y el exito
    '''
    exito = False
    try:
        __nombreCargo = request.form["txtNomCargo"]
        __sueldo = request.form["txtSueldo"]
        if comprobar(__nombreCargo, __sueldo):
            sql = "INSERT INTO cargo(`NomCargo`, `Sueldo`) VALUES(%s, %s);"
            conector = mysql.connect()
            cursor = conector.cursor()
            datos = [__nombreCargo, __sueldo]
            cursor.execute(sql, datos)
            conector.commit()
            mensaje = "Cargo registrado correctamente"
            exito = True
        else:
            mensaje = "Los datos agregados no son validos"
        cursor.close()
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
    return jsonify({"mensaje": mensaje, "exito": exito})

@cargo.route("/cargo/upd/<int:id>/", methods = ["PUT"])
def cargoUpd(id):
    '''
    En esta funcion se actualiza un cargo

    Args:
        id: Viene ser el IDcargo que se quiere actualizar
    Returns:
        Un json que tiene mensaje de validacion y el exito
    '''
    exito = False
    try:
        __nombreCargo = request.form["txtNomCargo"]
        __sueldo = request.form["txtSueldo"]
        if comprobar(__nombreCargo, __sueldo):
            sql = "UPDATE cargo SET NomCargo = %s, Sueldo = %s WHERE IDCargo = %s"
            datos = [__nombreCargo, __sueldo, id]
            conector = mysql.connect()
            cursor = conector.cursor()
            cursor.execute(sql, datos)
            conector.commit()
            mensaje = "Cargo actualizado correctamente"
            exito = True
            cursor.close()
        else:
            mensaje = "Los datos agregados no son validos"
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
    return jsonify({"mensaje": mensaje, "exito": exito})

@cargo.route('/cargo/del/<int:id>/', methods=["DELETE"])
def cargoDel(id):
    '''
    En esta funcion se elimina un cargo por su ID

    Args:
        id: Viene ser el IDcargo que se quiere eliminar
    Returns:
        Un json que tiene mensaje de validacion y el exito
    '''
    try:
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.callproc('DeleteCargo', [id])
        conector.commit()
        mensaje = "El cargo se ha eliminado correctamente"
        exito = True
        cursor.close()
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
        exito = False
    return jsonify({"mensaje": mensaje, "exito": exito})