from lib import ma, db



class IntentModel(db.Model):
    __tablename__ = 'intent'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    program = db.Column(db.Integer)
    description = db.Column(db.String(100))
    resposta = db.relationship('ResponseModel')

    def __init__(self, id,  name, program, description):
        self.id = id
        self.name = name
        self.program = program
        self.description = description

    
    def __repr__(self):
        return f"<Intent name: {self.name}>"
    

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def find_by_name_program(cls, name, program):
        return cls.query.filter_by(name=name, program = program).first()
    
    @classmethod
    def find_by_program(cls, program):
        return cls.query.filter_by(program = program).all()

    @classmethod
    def find_by_name_or_404(cls, name, program):
        return cls.query.filter_by(name=name, program = program).first_or_404()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class IntentSchema(ma.Schema):
    class Meta:
        fields= ('id', 'name', 'program', 'description')

intent_share_schema = IntentSchema()
intent_many_share_schema = IntentSchema(many=True)