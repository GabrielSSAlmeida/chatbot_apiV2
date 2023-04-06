from werkzeug.security import generate_password_hash, check_password_hash
from lib import ma, db



class AccessModel(db.Model):
    __tablename__ = 'access'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, name, password):
        self.name = name
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return f"<Access name: {self.name}>"
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_by_name_or_404(cls, name):
        return cls.query.filter_by(name=name).first_or_404()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class AccessSchema(ma.Schema):
    class Meta:
        fields= ('id', 'name')

access_share_schema = AccessSchema()
access_many_share_schema = AccessSchema(many=True)