from .app import db


class Station(db.Model):
    __table_args__ = {'sqlite_autoincrement': True}
    id = db.Column(db.Integer, primary_key=True)
    metro_id = db.Column(db.Float())
    name = db.Column(db.String(150))
    lat = db.Column(db.Float())
    lng = db.Column(db.Float())
    order = db.Column(db.Integer())

# db.create_all()
