from datetime import datetime
from os import path, remove
from flask import Blueprint, jsonify, request, make_response
from util.Connection import Connection

conexion = Connection()
trabajador = Blueprint('trabajador', __name__)
mysql = conexion.mysql

@trabajador.route("/trabajador/cargo/", methods=["GET"])
@trabajador.route("/trabajador/cargo/<int:idCargo>/", methods=["GET"])
def trabajadorSelCargo(idCargo = None):
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
        sql = "SELECT CodTrabajador, CorreoTrabajador, DNITrabajador, NomTrabajador, TelefonoTrabajador, DireccionTrabajador, cargo.`IDCargo`, cargo.`NomCargo` FROM trabajador INNER JOIN cargo ON trabajador.`IDCargo` = cargo.`IDCargo`"
        if idCargo != None:
            sql += " WHERE cargo.`IDCargo` = %s"
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
                "CodTrabajador": fila[0],
                "CorreoTrabajador": fila[1],
                "DNITrabajador": fila[2],
                "NomTrabajador": fila[3],
                "TelefonoTrabajador": fila[4],
                "DireccionTrabajador": fila[5],
                "IDCargo": fila[6],
                "NomCargo": fila[7]
            } for fila in datos]
        cursor.close()
    except Exception as ex:
        resultado = "Ocurrio un error: " + repr(ex)
        exito = False
    return jsonify({"resultado": resultado, "exito": exito})

@trabajador.route('/trabajador/get/<int:id>/', methods=["GET"])
def trabajadorGet(id):
    """
    Obtiene los detalles de un trabajador.

    Args: 
        id: viene ser el id del trabajador que se desea obtener.
    Returns:
        Un json que contiene los detalles del trabajador y el exito
    """
    resultado = obtenerTrabajador(id)
    return jsonify({"resultado": resultado[0], "exito": resultado[1]})

@trabajador.route("/trabajador/ins/", methods=["POST"])
def trabajadorIns():
    """
    Esta funcion inserta nuevos trabajadores.

    Returns:
        Un json que contiene un mensaje y el exito
    """
    try:
        __correo = request.form["txtCorreoTrabajador"]
        __dni = request.form["txtDNITrabajador"]
        __nombre = request.form['txtNomTrabajador']
        __password = request.form["txtPassword"]
        __telefono = request.form["txtTelefonoTrabajador"]
        __direccion = request.form["txtDireccionTrabajador"]
        __idcargo = request.form["txtIDCargo"]
        
        if "imagenTrabajador" in request.files:
            __imagen = request.files["imagenTrabajador"];
            ruta = generarImagen(__imagen)
            sql = "INSERT INTO trabajador(CorreoTrabajador, DNITrabajador, NomTrabajador, PasswordTrabajador, TelefonoTrabajador, DireccionTrabajador, imagenTrabajador, IDCargo) VALUES (%s, %s, %s, AES_ENCRYPT(%s, %s), %s, %s, %s, %s)"
            conn = mysql.connect()
            cursor = conn.cursor()
            datos = [__correo, __dni, __nombre, __password, __password, __telefono, __direccion, ruta, __idcargo]
            cursor.execute(sql, datos)
            conn.commit()
            mensaje = "Trabajador registrado correctamente"
            exito = True
            cursor.close()
            exito = True
        else:
            mensaje = "Falta introducir una imagen"
            exito = False
    except Exception as ex:
        mensaje = f"Error: {ex.__str__()}"
        exito = False
    return make_response(jsonify({"mensaje": mensaje, "exito": exito}))

@trabajador.route("/trabajador/upd/<int:id>/", methods=["PUT"])
def trabajadorUpd(id):
    """
    Esta funcion actualiza a los trabajadores por el id.

    Args: 
        id: viene ser el id del trabajor 
    Returns:
        Un json que contiene un mensaje y el exito
    """
    exito = False
    try:
        __correo = request.form["txtCorreoTrabajador"]
        __dni = request.form["txtDNITrabajador"]
        __nombre = request.form['txtNomTrabajador']
        __telefono = request.form["txtTelefonoTrabajador"]
        __direccion = request.form["txtDireccionTrabajador"]
        __idcargo = request.form["txtIDCargo"]

        datos = [__correo, __dni, __nombre, __telefono, __direccion, __idcargo]

        conn = mysql.connect()
        cursor = conn.cursor()
        if 'imagenTrabajador' in request.files:
            __imagen = request.files['imagenTrabajador']
            ruta = generarImagen(__imagen)
            sql = "UPDATE trabajador SET CorreoTrabajador = %s, DNITrabajador = %s, NomTrabajador = %s, TelefonoTrabajador = %s, DireccionTrabajador = %s, IDCargo = %s, imagenTrabajador = %s WHERE CodTrabajador = %s"
            datos.append(ruta)
            trabajador = obtenerTrabajador(id)
            borrarImagen('upload/img/trabajadores/'+trabajador[0]['imagenTrabajador'])
        else:
            sql = "UPDATE trabajador SET CorreoTrabajador = %s, DNITrabajador = %s, NomTrabajador = %s, TelefonoTrabajador = %s, DireccionTrabajador = %s, IDCargo = %s WHERE CodTrabajador = %s"
            
        datos.append(id)
        cursor.execute(sql, datos)
        conn.commit()
        mensaje = "Trabajador actualizado correctamente"
        exito = True
        cursor.close()
    except Exception as ex:
        mensaje = f"Error: {ex.__str__()}"
    return jsonify({"mensaje": mensaje, "exito": exito})

@trabajador.route("/trabajador/del/<int:id>/", methods = ['DELETE'])
def trabajadorDel(id):
    """
    Esta funcion elimina a los trabajadores por el id.

    Args: 
        id: viene ser el id del trabajor 
    Returns:
        Un json que contiene un mensaje y el exito
    """
    try:
        conector = mysql.connect()
        cursor = conector.cursor()

        #Borrando imagen del platillo
        trabajador = obtenerTrabajador(id)
        borrarImagen('upload/img/trabajadores/'+trabajador[0]['imagenTrabajador'])

        cursor.callproc('DeleteTrabajador', [id])
        conector.commit()
        mensaje = f"Se ha borrado el trabajador con el id {id}"
        exito = True
        cursor.close()
    except Exception as e:
        mensaje = f"Error: {e.__str__()}"
        exito = False
    return jsonify({"mensaje": mensaje, "exito": exito})

def obtenerTrabajador(id):
    """
    Obtiene los detalles de un trabajador en base a su ID.

    Args:
        id: El ID del trabajador que se desea obtener.
    Returns:
        Una lista que contiene un diccionario con los detalles del trabajador y el éxito.
    """
    exito = True
    try:
        sql = "SELECT `CodTrabajador`, `CorreoTrabajador`, `DNITrabajador`, `NomTrabajador`, `TelefonoTrabajador`, `DireccionTrabajador`, `imagenTrabajador`, `IDCargo` FROM trabajador WHERE `CodTrabajador` = %s"
        conector = mysql.connect()
        cursor = conector.cursor()
        cursor.execute(sql, id)
        dato = cursor.fetchone()
        if dato != None:
            resultado = {
                "CodTrabajador": dato[0],
                "CorreoTrabajador": dato[1],
                "DNITrabajador": dato[2],
                "NomTrabajador": dato[3],
                "TelefonoTrabajador": dato[4],
                "DireccionTrabajador": dato[5],
                "imagenTrabajador": dato[6],
                "IDCargo": dato[7]
            }
        else:
            resultado = "No se ha encontrado el platillo"
            exito = False
        cursor.close()
    except Exception as ex:
        resultado = f"Error: {ex.__str__()}"
        exito = False
    return [resultado, exito]

@trabajador.route("/trabajador/foto/<int:id>/", methods = ['GET'])
def cargarImagenTrabajador(id):
    """
    Carga y devuelve la imagen de perfil de un trabajador.

    Args:
        id: El ID del trabajador
    Returns:
        La imagen del trabajador
    """
    trabajador = obtenerTrabajador(id)
    if trabajador[1]:
        image_data = open("upload/img/trabajadores/"+trabajador[0]["imagenTrabajador"], "rb").read()
        resultado = make_response(image_data)
        resultado.headers['Content-Type'] = 'image/png'
        resultado.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0'
        resultado.headers['Pragma'] = 'no-cache'
        resultado.headers['Expires'] = '0'
        return resultado

def generarImagen(imagen):
    """
    Genera un nombre único para una imagen y la guarda en una ruta específica.

    Parámetros:
        imagen: La imagen a guardar.

    Retorna:
        La ruta de la imagen generada
    """
    fecha = datetime.now()
    fechaCadena = fecha.strftime("%Y%m%d%H%M%S")
    extension = imagen.filename.rsplit('.', 1)[-1]
    nombreFoto = fechaCadena + "." +extension
    ruta = path.join("upload/img/trabajadores", nombreFoto)
    imagen.save(ruta)
    return nombreFoto

def borrarImagen(ruta):
    if path.exists(ruta):
        remove(ruta)
        return True
    else:
        return False