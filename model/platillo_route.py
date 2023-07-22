import datetime, os
from flask import Blueprint, jsonify, request, make_response
from util.Connection import Connection

conexion = Connection()
platillo = Blueprint('platillo', __name__)
mysql = conexion.mysql

@platillo.route("/platillo/sel/", methods=["GET"])
@platillo.route("/platillo/sel/<int:idCateg>/", methods = ["GET"])
def platilloSelCateg(idCateg = None):
    """
    Selecciona todo los detalles del platillo

    Args:
        idCateg: Viene ser el id de la categoria. (default: None)
    Returns:
        Un json que tiene la lista de todos los platillos y el exito
    """
    resultado = []
    exito = True
    try:
        sql = "SELECT CodigoPlatillo, NombrePlatillo, Imagen, Precio, Descripcion, IDCategoria FROM platillo"
        conector = mysql.connect()
        cursor = conector.cursor()
        if idCateg != None:
            sql += " WHERE IDCategoria = %s"
            cursor.execute(sql, idCateg)
        else:
            cursor.execute(sql)
        datos = cursor.fetchall()
        if len(datos) == 0:
            resultado = f"No existen platillos con la categoria {idCateg}"
            exito = False
        else:
            resultado = [{
                "CodigoPlatillo": fila[0],
                "NombrePlatillo": fila[1],
                "Imagen": fila[2],
                "Precio": fila[3],
                "Descripcion": fila[4],
                "IDCategoria": fila[5]
            } for fila in datos]
        cursor.close()
    except Exception as ex:
        resultado = "Ocurrio un error: " + repr(ex)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

@platillo.route("/platillo/get/<int:id>/", methods = ["GET"])
def platilloGet(id):
    """
    Obtiene los detalles de un platillo

    Args:
        id: El ID del platillo que se desea obtener.
    Returns:
        Un json que tiene los detalles del platillos y el exito
    """
    resultado = obtenerPlatillo(id)
    return jsonify({"resultado": resultado[0], "exito": resultado[1]})

@platillo.route("/platillo/ins/", methods=["POST"])
def platilloIns():
    """
    Esta funcion inserta los nuevos platillos
    
    Returns:
        Un json que tiene el mensaje y el exito
    """
    exito = False
    try:
        __nombrePlatillo = request.form["txtNombrePlatillo"]
        __precio = request.form["txtPrecio"]
        __descripcion = request.form["txtDescripcion"]
        __idCategoria = request.form["txtIdCategoria"]

        if 'imagenPlatillo' in request.files:
            __imagen = request.files['imagenPlatillo']
            ruta = generarImagen(__imagen)
            sql = "INSERT INTO platillo(NombrePlatillo, Imagen, Precio, Descripcion, IDCategoria) VALUES (%s, %s, %s, %s, %s)"
            conn = mysql.connect()
            cursor = conn.cursor()
            datos = [__nombrePlatillo, ruta, __precio, __descripcion, __idCategoria]
            cursor.execute(sql, datos)
            conn.commit()
            mensaje = "Platillo registrado correctamente"
            exito = True
            cursor.close()
        else:
            mensaje = "Es necesario que insertes una imagen"
    except Exception as ex:
        mensaje = f"Error: {ex.__str__()}"
    return jsonify({"mensaje": mensaje, "exito": exito})

@platillo.route("/platillo/upd/<int:id>/", methods=["PUT"])
def platilloUpd(id):
    """
    Esta funcion actualiza los platillos

    Args:
        id: viene ser el id del platillo
    Returns:
        Un json que tiene el mensaje y el exito
    """
    exito = False
    try:
        __nombrePlatillo = request.form["txtNombrePlatillo"]
        __precio = request.form["txtPrecio"]
        __descripcion = request.form["txtDescripcion"]
        __idCategoria = request.form["txtIdCategoria"]

        datos = [__nombrePlatillo, __precio, __descripcion, __idCategoria]

        conn = mysql.connect()
        cursor = conn.cursor()

        if 'imagenPlatillo' in request.files:
            __imagen = request.files['imagenPlatillo']
            ruta = generarImagen(__imagen)
            sql = "UPDATE platillo SET NombrePlatillo = %s, Precio = %s, Descripcion = %s, IDCategoria = %s, Imagen = %s WHERE CodigoPlatillo = %s"
            datos.append(ruta)
            platillo = obtenerPlatillo(id)
            borrarImagen('upload/img/platillos/'+platillo[0]['Imagen'])
        else:
            sql = "UPDATE platillo SET NombrePlatillo = %s, Precio = %s, Descripcion = %s, IDCategoria = %s WHERE CodigoPlatillo = %s"
            
        datos.append(id)
        cursor.execute(sql, datos)
        conn.commit()
        mensaje = "Platillo actualizado correctamente"
        exito = True
        cursor.close()
    except Exception as ex:
        mensaje = f"Error: {ex.__str__()}"
    return jsonify({"mensaje": mensaje, "exito": exito})

@platillo.route("/platillo/del/<int:id>/", methods = ['DELETE'])
def platilloDel(id):
    """
    Esta funcion elimina el platillo por id

    Args:
        id: viene ser el id del platillo
    Returns:
        Un json que tiene el mensaje y el exito
    """
    try:
        conector = mysql.connect()
        cursor = conector.cursor()

        #Borrando imagen del platillo
        platillo = obtenerPlatillo(id)
        borrarImagen('upload/img/platillos/'+platillo[0]['Imagen'])

        cursor.callproc('DeletePlatillo', [id])
        conector.commit()
        mensaje = f"Se ha borrado el platillo con el id {id}"
        exito = True
        cursor.close()
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
        exito = False
    return jsonify({"mensaje": mensaje, "exito": exito})

@platillo.route("/platillo/foto/<int:id>/", methods = ['GET'])
def cargarImagenPlatillo(id):
    """
    Esta funcion permite retornar la imagen a imprimir

    Args:
        id: viene ser el id del platillo
    Returns:
        Retorna la imagen impresa
    """
    # MODIFICAR
    # r'/home/f3rn4nd021py/backEnd/upload/img/platillos/'
    # image_data = open("upload/img/platillos/"+platillo[0]["Imagen"], "rb").read()
    platillo = obtenerPlatillo(id)
    if platillo[1]:
        image_data = open("upload/img/platillos/"+platillo[0]["Imagen"], "rb").read()
        resultado = make_response(image_data)
        resultado.headers['Content-Type'] = 'image/png'
        resultado.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        resultado.headers['Pragma'] = 'no-cache'
        resultado.headers['Expires'] = '0'
        return resultado
    
@platillo.route("/platillo/total/", methods = ['POST'])
def platilloTotal():
    """
    Calcula el total de un conjunto de platillos.

    Retorna:
        Un json que contiene el total calculado y el éxito.
    """
    exito = False
    resultado = 0
    try:
        arreglo = request.get_json()
        for elemento in arreglo:
            platillo = obtenerPlatillo(elemento[0])
            resultado = resultado + (elemento[1]*platillo[0]["Precio"])
        exito = True
    except Exception as e:
        resultado = f"Error: {e.__str__()}"
    return jsonify({"resultado": resultado, "exito": exito})

def obtenerPlatillo(id):
    """
    Esta Funcion llama la lista de platillos por id de categoria

    Args: 
        id: El el id de platillo
    Returns:
        Un json que contiene la información de un platillo
    """
    exito = True
    try:
        sql = "SELECT CodigoPlatillo, NombrePlatillo, Precio, Descripcion, Imagen, IDCategoria FROM platillo WHERE CodigoPlatillo = %s"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, id)
        dato = cursor.fetchone()
        if dato != None:
            resultado = {
                "CodigoPlatillo": dato[0],
                "NombrePlatillo": dato[1],
                "Precio": dato[2],
                "Descripcion": dato[3],
                "Imagen": dato[4],
                "IDCategoria": dato[5]
            }
        else:
            resultado = "No se ha encontrado el platillo"
            exito = False
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return [resultado, exito]

def generarImagen(__imagen):
    """
    Permite guardar una imagen en el servidor

    Args: 
        __imagen: Es la imagen a guardar
    Returns:
        La ruta en la cual se guardó la imagen
    """
    fecha = datetime.datetime.now()
    nombreImagen = fecha.strftime("%Y%m%d%H%M%S")
    extension = __imagen.content_type.split("/")[1]
    ruta = nombreImagen + "." + extension
    __imagen.save("upload/img/platillos/"+ruta)
    return ruta

def borrarImagen(ruta):
    """
    Permite eliminar una imagen del servidor

    Args: 
        ruta: La ruta de la imagen a eliminar
    Returns:
        Devuelve un validador indicando si se eliminó o no la imagen
    """
    if os.path.exists(ruta):
        os.remove(ruta)
        return True
    else:
        return False
    
