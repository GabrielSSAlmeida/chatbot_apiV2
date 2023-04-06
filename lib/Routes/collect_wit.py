from flask import request, jsonify, make_response, send_from_directory
from flask_restful import Resource
from lib import client, recognizer, AudioSegment, sr
from gtts import gTTS
import random, os, shutil
from useful_variables import UsefulVariables
from datetime import datetime, timedelta
from lib.models.intent_db import IntentModel
from lib.models.response_db import ResponseModel, response_many_share_schema
from apscheduler.schedulers.background import BackgroundScheduler
from lib.cron_task import CronTask



class GetTextAnswer(Resource):
    def get(self, typeResponse):
        contentUserMessage = request.args.get('message')

        response = getIntentWit(contentUserMessage)
        
        match typeResponse: #Devolve uma resposta em forma de texto
            case 'text':
                return make_response(
                    jsonify(response)
                )

            case 'audio': #devolve uma resposta em forma de audio
                newResponse = createResponseAudio(response)

                return make_response(
                    jsonify(newResponse)
                )
                

class UploadAudio(Resource):
    def post(self, typeResponse):
        try:
            arquivo = request.files
            file = arquivo.getlist('file')[0]
            #Cria pasta de audio caso nao exista
            if not os.path.isdir(UsefulVariables.PATH_AUDIO_USER):
                os.mkdir(UsefulVariables.PATH_AUDIO_USER)
        
            path = os.path.join(UsefulVariables.PATH_AUDIO_USER, file.filename)
            file.save(path)#Salva o arquivo na pasta audioFromUser
            
            newFileName = file.filename[:-4] + ".flac"

            if os.path.isfile(path):
                audioMp4 = AudioSegment.from_file(path, "mp4")
                audioMp4.export(os.path.join(UsefulVariables.PATH_AUDIO_USER, newFileName), format="flac")
            else:
                response = jsonify({"erro": "Problema para criar o arquivo de audio"})
                response.status_code = 400
                return response 
            
            text=""

            with sr.AudioFile(os.path.join(UsefulVariables.PATH_AUDIO_USER, newFileName)) as source:
                recognizer.adjust_for_ambient_noise(source)
                # listen for the data (load audio to memory)
                audio_data = recognizer.record(source)
                # recognize (convert from speech to text)
                text = recognizer.recognize_google(audio_data, language="pt-BR")
                
            print(text)
            
            response = getIntentWit(text)
            
            shutil.rmtree(UsefulVariables.PATH_AUDIO_USER)
            
            match typeResponse: #Devolve uma resposta em forma de texto
                case 'text':
                    return make_response(
                        jsonify(response)
                    )

                case 'audio': #devolve uma resposta em forma de audio
                    newResponse = createResponseAudio(response)
                    
                    return make_response(
                        jsonify(newResponse)
                    )

        except Exception as e:
            print(e)
            response = jsonify(
                    {
                        "Error": "Não foi possível entender o que foi dito", 
                    }
                )
            response.status_code = 400
            return response


class AudioDownload(Resource):
    def get(self):
        nameFile = request.args.get('filename')
        return send_from_directory(UsefulVariables.PATH_AUDIOS, nameFile, as_attachment=False)


class ImageDownload(Resource):
    def get(self):
        nameFile = request.args.get('filename')
        return send_from_directory(UsefulVariables.PATH_IMAGE, nameFile, as_attachment=False)
    
class VideoDownload(Resource):
    def get(self):
        nameFile = request.args.get('filename')
        return send_from_directory(UsefulVariables.PATH_VIDEO, nameFile, as_attachment=False)

""" class DeleteAudio(Resource):
    def get(self):
        dirName = request.args.get('dirname')
        final_dirname = os.path.join(UsefulVariables.BASENAME_DIRECTORY, dirName)
        if os.path.isdir(final_dirname):#se existe o diretorio
            shutil.rmtree(final_dirname)
            return ('', 204)
        else:
            return ('', 404) """



def getIntentWit(message):
    data_message = client.message(message)

    intent = data_message.get("intents")[0].get("name")
    intent_confidence = data_message.get("intents")[0].get("confidence")
    
    intentNameWit = intent.split('_')
    
    intentName = intentNameWit[0]
    programId = intentNameWit[1]

    if(intent_confidence > 0.6):
        search_intent = IntentModel.find_by_name_program(name=intentName, program=programId)

        if search_intent:
            intentId = search_intent.id

            search_response = response_many_share_schema.dump(
                ResponseModel.find_by_intent_id(intent_id=intentId)
            )
            if search_response:
                tam = len(search_response)
                response = search_response[random.randint(0, tam-1)]
                response.pop('id')
            

        else:
            response = jsonify({"erro": "Intent não encontrada"})
            response.status_code = 400
            return response   
    else:
        response = UsefulVariables.MESSAGE_ERRO

    return response

def createResponseAudio(response):
    if response['type'] == "text":
        mytext = response["value"]
    else:
        mytext = response["description"]
    
    audioObj = gTTS(text=mytext, lang=UsefulVariables.LANGUAGE, slow=False, tld=UsefulVariables.TLD)

    #Cria pasta de audio caso nao exista
    if not os.path.isdir(UsefulVariables.PATH_AUDIOS):
        os.mkdir(UsefulVariables.PATH_AUDIOS)
    
    #O nome do arquivo tem a data de criação
    date_now = datetime.now().strftime('%d-%m-%Y-%H.%M.%S.%f')
    filename = f"audio{date_now}.mp3"

    #salva o arquivo de audio
    audioObj.save(os.path.join(UsefulVariables.PATH_AUDIOS, filename))
    future20min = (datetime.now() + timedelta(minutes=20)).replace(fold=1).strftime('%Y-%m-%d %H:%M:%S')

    #cria CronTask para apagar o arquivo de audio
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(func = CronTask.deleteAudio,trigger='date',next_run_time= future20min, args=[filename])
    sched.start()


    response['audio'] = UsefulVariables.API_URL+"audio/download?filename=" + filename

    return response