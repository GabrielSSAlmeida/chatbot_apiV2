from flask import request, jsonify
from flask_restful import Resource
from lib import client
from lib.models.intent_db import IntentModel, intent_share_schema
from lib.models.response_db import ResponseModel, response_many_share_schema
from useful_variables import UsefulVariables
import os
from lib.auth.authenticate import jwt_required



#função que verifica se existe uma intenção
def verify_intent(intentName):
    intents = client.intent_list()
    for intent in intents:
        if intent['name'] == intentName:
            return True #Existe a intenção
    
    return False#não existe a intenção



#Adiciona intent no wit e no banco de dados
class AddIntent(Resource):
    @jwt_required
    def post(self, current_user):
        try:     
            #Pega o json pelo POST
            responseJson = request.get_json()
            intentName = responseJson['name']
            programId = responseJson['program_id']
            intentDescription = responseJson['description']
            responseArray = responseJson['response']

            intentNameWit = f"{intentName}_{programId}_"

            if(verify_intent(intentNameWit)):
                return 'Intent já existe'
            
            #Cria a intent no wit
            witResponse = client.create_intent(intentNameWit)
            if not "id" or not "name" in witResponse:
                return 'Erro ao criar intent'
            
            #Cria a intent com as respostas no banco de dados
            new_intent = IntentModel(id= witResponse['id'], name=intentName, program=programId, description=intentDescription)
            new_intent.save_to_db()
            
            if len(responseArray) != 0:
                type = ""
                value= ""
                for response in responseArray:
                    learn_more  = ""
                    if 'learnMore' in response: 
                        learn_more = response['learnMore']
                    if response['type'] == "text":
                        type = response['type']
                        value = response['value']
                        
                        new_response = ResponseModel(type=type, value=value, intent_id=witResponse['id'], learn_more= learn_more)
                        new_response.save_to_db()
                    else:
                        type = response['type']
                        description = response['description']
                        value = response['value']
                        new_response = ResponseModel(type=type, value=value, description=description, intent_id=witResponse['id'], learn_more=learn_more)
                        new_response.save_to_db()


            result_intent = intent_share_schema.dump(
                IntentModel.find_by_id(id=witResponse['id'])
            )
            result_response = response_many_share_schema.dump(
                ResponseModel.find_by_intent_id(intent_id=witResponse['id'])
            )

            result_intent['response'] =  result_response
            return jsonify(result_intent)

        except Exception as e:
            print(e)
            response = jsonify(
                    {
                        "Error": str(e), 
                    }
                )
            response.status_code = 400
            return response


#deleta intent no wit e no banco de dados
#OBS: TIVE QUE ALTERAR O ARQUIVO WIT, POIS TINHA UM ERRO COM A FUNÇÃO 'urllib.quote_plus()'
#A IMPORTAÇÃO MUDOU PARAR 'import urllib.parse' e a chamada foi para 'urllib.parse.quote_plus()'
class DeleteIntent(Resource):
    @jwt_required
    def delete(self, intentName, program, current_user):
        try:
            intentNameWit = f"{intentName}_{program}_"
            if(verify_intent(intentNameWit)):
                witResponse = client.delete_intent(intentNameWit)

                if witResponse["deleted"] != intentNameWit:
                    return 'Erro ao apagar Intent'

                #Deleta a Intent e suas respectivas respostas do banco de dados
                delete_intent = IntentModel.find_by_name_program(name=intentName, program=program)
                if delete_intent:
                    intentId = delete_intent.id
                    delete_intent.delete_from_db()

                    delete_response = ResponseModel.find_by_intent_id(intent_id=intentId)
                    if delete_response:
                        for delete in delete_response:
                            delete.delete_from_db()
                        
                    else:
                        response = jsonify({"erro": "Erro ao apagar Respostas no db"})
                        response.status_code = 400
                        return response 
                else:
                    response = jsonify({"erro": "Erro ao apagar Intent no db"})
                    response.status_code = 400
                    return response
                


                return witResponse
            
            return 'Intent não existe'
        except Exception as e:
                print(e)
                return 'Error'
        



#edita as respostas na bd
class EditResponses(Resource):
    @jwt_required
    def put(self, current_user):
        try:     
            responseJson = request.get_json()
            intentName = responseJson['name']
            programId = responseJson['program_id']
            responseArray = responseJson['response']

            if intentName != "" and programId != "":
                intent_update = IntentModel.find_by_name_program(name=intentName, program=programId)
                if intent_update:

                    intentId = intent_update.id

                    update_response = ResponseModel.find_by_intent_id(intent_id=intentId)
                    if update_response:#Se existir respostas para essa intent, apague
                        for delete in update_response:
                            delete.delete_from_db()
                        
                        if len(responseArray) != 0:
                            #Adiciona novas Respostas ======================
                            type = ""
                            value= ""
                            for response in responseArray:
                                learn_more = ""
                                if 'learnMore' in response:
                                    learn_more = response['learnMore']
                                if response['type'] == "text":
                                    type = response['type']
                                    value = response['value']
                                    
                                    new_response = ResponseModel(type=type, value=value, intent_id=intentId, learn_more=learn_more)
                                    new_response.save_to_db()
                                else:
                                    type = response['type']
                                    description = response['description']
                                    value = response['value']
                                    new_response = ResponseModel(type=type, value=value, description=description, intent_id=intentId, learn_more=learn_more)
                                    new_response.save_to_db()
                    else:
                        response = jsonify({"erro": "Não existe respostas para essa Intent"})
                        response.status_code = 400
                        return response       
                else:
                    response = jsonify({"erro": "Erro ao atualizar Intent no db"})
                    response.status_code = 400
                    return response

            else:
                response = jsonify({"erro": "É preciso o nome da Intent e do Programa"})
                response.status_code = 400
                return response 
            

            result_intent = intent_share_schema.dump(
                IntentModel.find_by_id(id=intentId)
            )
            result_response = response_many_share_schema.dump(
                ResponseModel.find_by_intent_id(intent_id=intentId)
            )

            result_intent['response'] =  result_response
            return jsonify(result_intent)
        
        except Exception as e:
            print(e)
            return 'Error'
        

#recebe foto e video como resposta possivel
class FileEditResponse(Resource):
    @jwt_required
    def post(self, current_user):
        try:
            arquivo = request.files
            file = arquivo.getlist('file')[0]
            intent = request.form['intent']
            programId = request.form['program_id']
            description = request.form['description']

            path=""
            type=""
            #Cria pasta de audio caso nao exista
            if "image" in file.content_type:
                basePath = UsefulVariables.PATH_IMAGE
                type="image"
            elif "video" in file.content_type:
                basePath = UsefulVariables.PATH_VIDEO
                type="video"
            else:
                response = jsonify({"erro": "content_type error / tipo de arquivo nao suportado"})
                response.status_code = 400
                return response
            
            if not os.path.isdir(basePath):
                os.mkdir(basePath)

            filenameTratado = file.filename.replace(" ", "_")
            path = os.path.join(basePath, filenameTratado)


            file.save(path)

            intent_update = IntentModel.find_by_name_program(name=intent, program=programId)
            
            value = UsefulVariables.API_URL+type+"/download?filename=" + filenameTratado
            new_response = ResponseModel(type=type, value=value, description=description, intent_id=intent_update.id)
            new_response.save_to_db()

            response = jsonify(
                    {
                        "Sucess": "Upload realizado com sucesso", 
                        "url": value
                    }
                )
            response.status_code = 200
            return response

        except Exception as e:
            print(e)
            return 'Error'


#Enviar as perguntas(Utterances) para treinar o bot
class TrainBot(Resource):
    @jwt_required
    def post(self, current_user):
        try:
            utterances = request.get_json()
            #Verificando se a intenção existe (Add entidade caso precise)
            for utterance in utterances:
                intentNameWit = f"{utterance['intent']}_{utterance['program_id']}_"
                if(not verify_intent(intentNameWit)): #Se não existe a intent, retorna o erro
                    return 'Alguma intent enviada não existe'
                utterance['intent'] = intentNameWit
                utterance.pop("program_id")
                
            witResponse = client.train(utterances)
            return witResponse
        
        except Exception as e:
            print(e)
            return 'Error'
        
        

class DeleteUtterance(Resource):
    @jwt_required
    def delete(self, current_user):
        try:
            utterances = request.get_json()
            utterances_array = [] #Array de strings com as utterances que deseja excluir
            for utterance in utterances:
                utterances_array.append(utterance['text'])

            witResponse = client.delete_utterances(utterances_array)
            return witResponse
        except Exception as e:
            print(e)
            return 'Error'
