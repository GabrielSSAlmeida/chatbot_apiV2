from lib import ma, db



class HelpModel(db.Model):
    __tablename__ = 'help'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    description = db.Column(db.String(100))

    def __init__(self, title, description):
        self.title = title
        self.description = description

    
    def __repr__(self):
        return f"<Help title: {self.title}>"
    

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).first()
    

    @classmethod
    def find_by_title_or_404(cls, title):
        return cls.query.filter_by(title=title).first_or_404()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class HelpSchema(ma.Schema):
    class Meta:
        fields= ('id', 'title','description')

help_share_schema = HelpSchema()
help_many_share_schema = HelpSchema(many=True)