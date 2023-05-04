from flask import jsonify
from flask_restful import Resource, reqparse
from lib.models.help_db import HelpModel, help_share_schema, help_many_share_schema
from lib.auth.authenticate import jwt_required

class AddHelp(Resource):
    help_args = reqparse.RequestParser()
    help_args.add_argument("title", type=str, help="name required")
    help_args.add_argument("description", type=str, help="password required")
    @jwt_required
    def post(self, current_user):
        try:
            data = self.help_args.parse_args()
            title = data["title"]
            description = data["description"]
            

            new_help = HelpModel(title=title, description=description)

            new_help.save_to_db()

            result_help = help_share_schema.dump(
                HelpModel.find_by_title_or_404(title=title)
            )
            
            return jsonify(result_help)
        except Exception as e:
            print(e)
            response = jsonify(
                    {
                        "Error": "Erro ao adicionar", 
                    }
                )
            response.status_code = 400
            return response

class GetAllHelps(Resource):
    def get(self):
        try:
            result_help = help_many_share_schema.dump(
                HelpModel.find_all()
            )
            return jsonify(result_help)
        
        except Exception as e:
            print(e)
            response = jsonify(
                    {
                        "Error": "Não foi possível baixar a lista de ajuda", 
                    }
                )
            response.status_code = 400
            return response

class DeleteHelps(Resource):
    @jwt_required
    def delete(self, current_user):
        try:
            
            result_help = HelpModel.find_all()
        
            for help in result_help:
                help.delete_from_db()
            
            response = jsonify(
                    {
                        "Sucess": "Lista Excluida", 
                    }
                )
            response.status_code = 200
            return response
        
        except Exception as e:
            print(e)
            response = jsonify(
                    {
                        "Error": "Não foi possível excluir a lista de ajuda", 
                    }
                )
            response.status_code = 400
            return response