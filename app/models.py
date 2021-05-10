# models.py

from flask_login import UserMixin
from . import db
from datetime import datetime

  


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    photo = db.Column(db.String(100))
 

class Todo(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(100), unique=True)
    mark_task = db.Column(db.Integer, nullable=False, default=0)
    list_name = db.Column(db.String(100), nullable=False, default='New List')
    share_list = db.Column(db.String(100), nullable=False)

 


    def __repr__(self):
        return '(%r,)' % self.id