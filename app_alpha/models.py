from sqlalchemy import sql, orm
from app import db

class Game(db.Model):
    __tablename__ = 'game'
    gid = db.Column('gid', db.String(20), primary_key=True)
    day = db.Column('day', db.String(20))
    opponent = db.Column('opponent', db.String(20))
    city = db.Column('city', db.String(40))
    shots = orm.relationship('Shot')

class Shot(db.Model):
    __tablename__ = 'shot'
    sid = db.Column('sid', db.String(20), primary_key = True)
    gid = db.Column('gid', db.String(20),
                        db.ForeignKey('game.gid'))
    name = db.Column('name', db.String(40))
    period = db.Column('period', db.String(20))
    clock = db.Column('clock', db.String(20))
    shot_type  = db.Column('shot_type', db.String(20))
    made = db.Column('made', db.String(20))
    dribbles = db.Column('dribbles', db.String(20))
    x = db.Column('x', db.Integer)
    y = db.Column('y', db.Integer)
    def_name = db.Column('def_name', db.String(40))
