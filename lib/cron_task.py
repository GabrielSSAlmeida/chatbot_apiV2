import os
from useful_variables import UsefulVariables

class CronTask:
    def deleteAudio(filename):
        if os.path.isdir(UsefulVariables.PATH_AUDIOS):
            if os.path.isfile(os.path.join(UsefulVariables.PATH_AUDIOS, filename)):
                os.remove(os.path.join(UsefulVariables.PATH_AUDIOS, filename))
            else:
                print("Não foi possivel encontrar o arquivo "+filename)
        else:
            print("Não foi possivel encontrar o diretorio /audios")