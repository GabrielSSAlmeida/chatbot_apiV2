from flask import jsonify
from flask_restful import Resource, reqparse
from lib.models.access_db import AccessModel, access_share_schema
import datetime
from lib import app
import jwt

class AccessRegister(Resource):
    access_args = reqparse.RequestParser()
    access_args.add_argument("name", type=str, help="name required")
    access_args.add_argument("password", type=str, help="password required")
    access_args.add_argument("secret_key", type=str, help="Secret Key is required")

    def post(self):

        data = self.access_args.parse_args()
        name = data["name"]
        password = data["password"]
        secret_key = data["secret_key"]


        if secret_key != app.config['SECRET_KEY']:
            response = jsonify({"error": "Secret Key inválida"})
            response.status_code = 403
            return response
        
        elif AccessModel.find_by_name(name= name):
            response = jsonify({"error": "name já existe"})
            response.status_code = 403
            return response
        
        else:
            new_access = AccessModel(name = name, password = str(password))
            new_access.save_to_db()

            result_access = access_share_schema.dump(
                AccessModel.find_by_name(name=name)
            )
            
            return jsonify(result_access)


class AccessLogin(Resource):
    access_args = reqparse.RequestParser()
    access_args.add_argument("name", type=str, help="name required")
    access_args.add_argument("password", type=str, help="password required")

    def post(self):
        data = self.access_args.parse_args()
        name = data["name"]
        password = data["password"]


        access = AccessModel.find_by_name_or_404(name=name)
        
        if not access.verify_password(password):
            response = jsonify({"error": "Suas credenciais estão incorretas"})
            response.status_code = 403
            return response

        payload={
            "id": access.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
        }

        token = jwt.encode(payload, app.config['SECRET_KEY'])

        return jsonify({"token": token.decode('utf-8')})
    
class DeleteAccess(Resource):
    access_args = reqparse.RequestParser()
    access_args.add_argument("name", type=str, help="name required")
    access_args.add_argument("secret_key", type=str, help="Secret Key is required")

    def post(self):

        data = self.access_args.parse_args()
        name = data["name"]
        secret_key = data["secret_key"]


        if secret_key != app.config['SECRET_KEY']:
            response = jsonify({"error": "Secret Key inválida"})
            response.status_code = 403
            return response
        
        delete_access = AccessModel.find_by_name(name= name)
        if delete_access:
            delete_access.delete_from_db()
            response = jsonify({"message": "Registro deletado"})
            response.status_code = 200
            return response

        else:
            response = jsonify({"error": "Registro não encontrado"})
            response.status_code = 403
            return response