from lib import ma, db



class ResponseModel(db.Model):
    __tablename__ = 'response'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20))
    value = db.Column(db.String(200))
    description = db.Column(db.String(200))
    intent_id = db.Column(db.Integer, db.ForeignKey('intent.id'))

    def __init__(self, type,  value,  intent_id, description = ""):
        self.type = type
        self.value = value
        self.description = description
        self.intent_id = intent_id

    
    def __repr__(self):
        return f"<Response Value: {self.value}>"
    
    @classmethod
    def find_by_intent_id(cls, intent_id):#acho que retorna list
        return cls.query.filter_by(intent_id=intent_id).all()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class ResponseSchema(ma.Schema):
    class Meta:
        fields= ('id', 'type', 'value', 'description', 'intent')

response_share_schema = ResponseSchema()
response_many_share_schema = ResponseSchema(many=True)