from lib import api, app

from lib.Routes.collect_wit import GetTextAnswer, AudioDownload, ImageDownload, VideoDownload, UploadAudio #,DeleteAudio
from lib.Routes.access_key import AccessLogin, AccessRegister, DeleteAccess
from lib.Routes.train_wit import AddIntent, DeleteIntent, EditResponses, TrainBot, DeleteUtterance, FileEditResponse
from lib.Routes.get_infos import GetAllIntents, GetAllUtterances, GetResponsesIntent, GetIntentsbyProgram



api.add_resource(GetTextAnswer, "/<string:typeResponse>")
api.add_resource(UploadAudio, "/uploadAudio/<string:typeResponse>")
api.add_resource(AudioDownload, "/audio/download")
api.add_resource(ImageDownload, "/image/download")
api.add_resource(VideoDownload, "/video/download")
#api.add_resource(DeleteAudio, "/audio/delete")

api.add_resource(AccessRegister, "/register")
api.add_resource(AccessLogin, "/login")
api.add_resource(DeleteAccess, "/delete_access")


api.add_resource(AddIntent, "/intent")
api.add_resource(DeleteIntent, "/delete/<string:intentName>/<string:program>")
api.add_resource(EditResponses, "/edit")
api.add_resource(FileEditResponse, "/response_file")
api.add_resource(TrainBot, "/train")
api.add_resource(DeleteUtterance, "/delete_utterance")


api.add_resource(GetAllIntents, "/get_intents")
api.add_resource(GetAllUtterances, "/get_utterances/<int:numberOfUtterances>")
api.add_resource(GetResponsesIntent, "/get_response")
api.add_resource(GetIntentsbyProgram, "/get_intents_program")






if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")