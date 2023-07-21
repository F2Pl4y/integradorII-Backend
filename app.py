from util.Aplication import Aplication
from flask_jwt_extended import JWTManager 
from model.trabajador_route import trabajador
from model.cliente_route import cliente
from model.categoria_route import categoria
from model.cargo_route import cargo
from model.platillo_route import platillo
from model.venta_route import venta
from model.pedido_route import pedido
from model.detallepedido_route import detallepedido
from model.validacion_route import validaciones 

aplication = Aplication()
app = aplication.app
app.register_blueprint(cliente)
app.register_blueprint(categoria)
app.register_blueprint(cargo)
app.register_blueprint(platillo)
app.register_blueprint(venta)
app.register_blueprint(pedido)
app.register_blueprint(trabajador)
app.register_blueprint(validaciones)
app.register_blueprint(detallepedido)

# Configurar JWTManager en la aplicación Flask
jwt = JWTManager(app)
# Establecer la clave secreta de la aplicación
app.config['SECRET_KEY'] = 'secretito'
# Configurar la ubicación del token JWT en las cookies
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
# Desactivar la protección CSRF para las cookies JWT
app.config['JWT_COOKIE_CSRF_PROTECT'] = False

# # Configurar el host y el puerto para que la aplicación escuche en todas las interfaces
# app.run(host='0.0.0.0', port=5000)

def pagina_no_encontrada(error):
    return "<h1>Método no encontrado</h1>"

# if __name__ == "__main__":
#     app.register_error_handler(404, pagina_no_encontrada)
#     app.run(debug = True)
if __name__ == "__main__":
    app.register_error_handler(404, pagina_no_encontrada)
    app.run(debug=True, host='0.0.0.0', port=5000)