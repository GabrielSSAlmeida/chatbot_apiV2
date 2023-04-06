from functools import wraps

import jwt
from flask import request, jsonify, current_app

from lib.models.access_db import AccessModel

def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None

        if 'authorization' in request.headers:
            token = request.headers['authorization']
        
        if not token:
            response = jsonify({"error": "Você não tem permissão para acessar essa rota"})
            response.status_code = 403
            return response
        
        if not "Bearer" in token:
            response = jsonify({"error": "Token inválido"})
            response.status_code = 401
            return response
        try:
            token_pure = token.replace("Bearer ", "")
            decoded = jwt.decode(token_pure, current_app.config['SECRET_KEY'])
            current_user = AccessModel.query.get(decoded['id'])
        except Exception as e:
            print(e)
            response = jsonify({"error": "Token inválido"})
            response.status_code = 402
            return response

        return f(current_user = current_user, *args, **kwargs)
    
    return wrapper