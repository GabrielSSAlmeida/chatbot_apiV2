from flask import request, make_response, jsonify
from flask_restful import Resource
from lib import client
import json, tempfile, shutil
from useful_variables import UsefulVariables
from lib.models.intent_db import IntentModel, intent_share_schema, intent_many_share_schema
from lib.models.response_db import ResponseModel, response_many_share_schema

from lib.auth.authenticate import jwt_required

#get todas as intents do wit
class GetAllIntents(Resource):
    def get(self):
        try:
            return client.intent_list()
        except Exception as e:
            print(e)
            return 'Error'


#get all utterances do wit
#numberOfUtterances <Obrigatorio>= Numero de Utterances(Mensagens de treinamento) maximos que deve receber entre 1 a 10000.
class GetAllUtterances(Resource):
    def get(self, numberOfUtterances):
        try:
            intentName = request.args.get('intent')
            return client.get_utterances(limit= numberOfUtterances,intents=[intentName])
        except Exception as e:
            print(e)
            return 'Error'

#get todas as respostas do bd
class GetResponsesIntent(Resource):
    def get(self):
        try:
            intentName = request.args.get('intent')
            programId = request.args.get('programId')

            result_intent = intent_share_schema.dump(
                IntentModel.find_by_name_program(name=intentName, program=programId)
            )
            intentId = result_intent['id']
            result_response = response_many_share_schema.dump(
                ResponseModel.find_by_intent_id(intent_id=intentId)
            )

            result_intent['response'] =  result_response
            return jsonify(result_intent)
        except Exception as e:
            print(e)
            return 'Error'
        
class GetIntentsbyProgram(Resource):
    def get(self):
        try:
            programId = request.args.get('programId')

            result_intent = intent_many_share_schema.dump(
                IntentModel.find_by_program(program=programId)
            )
            
            return result_intent
        except Exception as e:
            print(e)
            return 'Error'
