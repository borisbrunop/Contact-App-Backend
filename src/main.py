"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Contact, Group
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/contact/all', methods=['GET'])
def r_contact():
    # crar variable y asignarle todos los contactos
    contacts = Contact.query.all()

    contact_serialize = list(map(lambda contact: contact.serialize(), contacts))
    print(contact_serialize)
    return jsonify(contact_serialize), 200

@app.route('/contact/<contact_id>', methods=["GET", "PATCH", "DELETE"])
def rud_contact_id(contact_id):
    #crea variable y le asigna el contacto del id especificado
    contact = Contact.query.get(contact_id)
    #verificar si el contact existe
    if isinstance(contact, Contact):
        if request.method == "GET":
            return jsonify(contact.serialize()), 200
        elif request.method == "PATCH":
            #crear variable con contenido del body
            dictionary = request.json
            if ("groups" not in dictionary):
                #actualizar propiedades con el diccionario
                contact.update_contact(dictionary)
                #hacer commit
                try:
                    db.session.commit()
                    #devolver el donante serializado 
                    return jsonify(contact.serialize()), 200
                except Exception as error:
                    db.session.rollback()
                    print(f"{error.args} {type(error)}")
                    return jsonify({
                        "result": f"{error.args}"
                    }), 500
            else:
                #crea variable y le asigna el grupo con el id indicado en el body(diccionario)
                group = Group.query.get(dictionary["groups"])
                #group = dictionary["groups"]
                #agrega el grupo en el contacto
                contact.groups.append(group)
                #hacer commit
                try:
                    db.session.commit()
                    #devolver el donante serializado 
                    return jsonify(contact.serialize()), 200
                except Exception as error:
                    db.session.rollback()
                    print(f"{error.args} {type(error)}")
                    return jsonify({
                        "result": f"{error.args}"
                    }), 500
        else:
            #remover el contact especifico 
            db.session.delete(contact)
            #hacer commit
            try:
                db.session.commit()
                return jsonify({}), 204
            except Exception as error:
                db.session.rollback()
                print(f"{error.args} {typr(error)}")
                return jsonify({
                    "result": f"{error.args}"
                }), 500
    else:
        #el contacto no existe
        return jsonify({
            "result": "contact not here"
        }), 404



@app.route('/contact', methods=['POST'])
def c_contact():
    # crea una variable y le asigna el body enviado con .json
    body = request.json

    # verificacion de que los datos esten en orden 
    if body is None:
        return jsonify({
            "result": "nothing in body"
        }), 400
    
    if (
        "full_name" not in body or
        "email" not in body or
        "address" not in body or
        "phone" not in body 
    ):
        return jsonify({
            "result": "check the properties"
        }), 400
    
    if (
        body["full_name"] == "" or
        body["email"] == "" or
        body["address"] == "" or
        body["phone"] == "" 
    ):
        return jsonify({
            "result": "check the porperties"
        }), 400 
    
    # crea una varieble y se le asigna los datos validos
    new_contact = Contact.register(
        body["full_name"],
        body["email"],
        body["address"],
        body["phone"]
    )

    # agregar a la sesion de datos sqlalchemy y hacer commit de la transacción
    db.session.add(new_contact)
    try:
        db.session.commit()
        # devolvemos el nuevo contacto serializado y 201
        return jsonify(new_contact.serialize()), 201
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
        # devolvemos el error
        return jsonify({
            "result": f"{error.args}"
        }),500


#creamos los endpoints para los GRUPOS
@app.route('/group/all', methods=['GET'])
def r_group():
    # crar variable y asignarle todos los contactos
    groups = Group.query.all()

    group_serialize = list(map(lambda group: group.serialize(), groups))
    print(group_serialize)
    return jsonify(group_serialize), 200


@app.route('/group', methods=['POST'])
def c_group():
    #crea variable y asigna body
    body = request.json
    #verificar contenido
    if body is None:
        return jsonify({
            "result": "nothing in body"
        }), 400
    if (
        "name" not in body
    ):
        return jsonify({
            "result": "check the properties"
        }), 400

    if (
        body["name"] == ""
    ):
        return jsonify({
            "result": "check the properties"
        }), 400
    #crear grupo en sesion de base de datos si los datos estan en orden
    new_group = Group.create_group(body["name"])
    #agregar sesion en base da datos 
    db.session.add(new_group)
    try:
        db.session.commit()
        # devolvemos el nuevo grupo serializado y 201
        return jsonify(new_group.serialize()), 201
    except Exception as error:
        db.session.rollback()
        print(f"{error.args} {type(error)}")
        # devolvemos el error
        return jsonify({
            "result": f"{error.args}"
        }),500

@app.route('/group/<group_id>', methods=['GET', 'PATCH', 'DELETE'])
def rud_group(group_id):
    #crea variable y le asigna un grupo con id especifico
    group = Group.query.get(group_id)
    if isinstance(group, Group):
        if request.method == "GET":
            return jsonify(group.serialize()), 200
        elif request.method == "PATCH":
            #crear variable con contenido del body
            dictionary = request.json
            #actualizar propiedades con el diccionario
            group.update_group(dictionary)
            #hacer commit
            try: 
                db.session.commit()
                #devolver el donante serializado 
                return jsonify(group.serialize()), 200
            except Exception as error:
                db.session.rollback()
                print(f"{error.args} {type(error)}")
                return jsonify({
                    "result": f"{error.args}"
                }), 500
        else:
            #remover el contact especifico 
            db.session.delete(group)
            #hacer commit
            try:
                db.session.commit()
                return jsonify({}), 204
            except Exception as error:
                db.session.rollback()
                print(f"{error.args} {typr(error)}")
                return jsonify({
                    "result": f"{error.args}"
                }), 500
    else:
        #el contacto no existe
        return jsonify({
            "result": "contact not here"
        }), 404


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
