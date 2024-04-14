from datetime import datetime
def validar_fecha(fecha_str):
    """Valida que la fecha sea igual o posterior a hoy y la devuelve en formato 'DD-MM-YYYY' si es válida."""
    try:
        # fecha = datetime.strptime(fecha_str, "%m/%d/%Y")  # Asegurarse que el formato de entrada sea correcto
        fecha = datetime.strptime(fecha_str, "%d/%m/%Y")  # Asegurarse que el formato de entrada sea correcto
        hoy = datetime.now()
        if fecha.date() >= hoy.date():
            # return True, fecha.strftime("%d-%m-%Y")  # Devuelve la fecha en el formato deseado
            return True, fecha.strftime("%Y-%m-%d")  # Devuelve la fecha en el formato deseado
        else:
            return False, ""
    except ValueError as e:
        return False, str(e)
    
def validar_hora(hora_str):
    """Valida que la hora esté en el formato 'HH:MM' y elimina AM o PM si está presente."""
    try:
        # Primero intentamos parsear la hora considerando que puede tener AM o PM
        formatos_posibles = ["%I:%M %p", "%H:%M"]  # Formatos 12 y 24 horas
        hora_objeto = None
        for formato in formatos_posibles:
            try:
                # p rint("valor entrante de la hora:", hora_str)
                hora_objeto = datetime.strptime(hora_str, formato)
                break  # Si el parsing es exitoso, salimos del bucle
            except ValueError:
                continue  # Si falla, intentamos con el siguiente formato
        if hora_objeto is None:
            return False, "Formato de hora inválido."
        # Convertimos a formato 24 horas sin AM/PM
        hora_sin_am_pm = hora_objeto.strftime("%H:%M")
        # p rint("valor final de la hora:", hora_sin_am_pm)
        return True, hora_sin_am_pm  # Devolvemos True y la hora ajustada
    except ValueError:
        return False, "Formato de hora inválido."
    
def juntarHora(fecha, hora):
    # Unir fecha y hora en un solo string
    fecha_hora_str = f"{validar_fecha(fecha)[1]} {validar_hora(hora)[1]}"
    # print(validar_fecha(fecha)[1])
    # print(validar_hora(hora)[1])
    # Convertir a objeto datetime
    fecha_hora_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%d %H:%M")

    return fecha_hora_obj

def validar_entero(valor_str):
    """Valida que el valor sea un número entero."""
    return valor_str.isdigit()
def convertir_a_string(valor):
    try:
        # Intentamos convertir el valor a string.
        _ = str(valor)
        return True  # Si la conversión es exitosa, devuelve True.
    except Exception as e:
        print(f"Error al convertir a string: {e}")
        return False  # Si ocurre un error en la conversión, devuelve False.
def validar_numero(valor_str):
    """Valida que el valor sea un número (entero o decimal)."""
    try:
        float(valor_str)
        if float(valor_str) > 0:
            return True
        else:
            return False
    except ValueError:
        return False
    
def validar_rango_pago(pago_str):
    """Valida que el tipo de pago esté en el rango [1, 2]."""
    try:
        pago = int(pago_str)  # Intenta convertir a entero
        if 1 <= pago <= 2:
            return True  # Si está en el rango, retorna True
        else:
            # p rint("VALOR FUERA DE RANGO")  # Informa si está fuera de rango
            return False
    except ValueError:
        # Si la conversión a entero falla, significa que no era un entero válido
        # p rint("VALOR NO ES UN ENTERO")
        return False
    









        # print(f"__viajeA: {__viajeA}, __detViajeA: {__detViajeA}, __viajeB: {__viajeB}, __detViajeB: {__detViajeB}, __datePart: {__datePart}, __timePart: {__timePart}, __carSel: {__carSel}, __asiCant: {__asiCant}, __costPasaje: {__costPasaje}, __pagoType: {__pagoType}, mitkn: {__valueTKN}, DNI: {getDNI(__valueTKN)}")

        # p rint("validacion_total", validacion_total)
        # Resultados de las validaciones
        # p rint(f"Fecha válida: {fecha_valida[1]}")
        # p rint(f"Hora válida: {hora_valida[1]}")
        # p rint(f"fecha junta: {fechaUnida}")
        # p rint(f"Selección de carro válida: {carro_valido}")
        # p rint(f"Cantidad de asientos válida: {asientos_validos}")
        # p rint(f"Costo de pasaje válido: {costo_valido}")
        # p rint(f"Tipo de pago válido: {tipo_pago_valido}")
        # p rint(f"valor del dni: {getDNI(__valueTKN)}")
        # if (validar_credenciales(__dni, __pass)):
        # current_user_dni = get_jwt_identity()