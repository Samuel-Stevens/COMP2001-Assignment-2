from __init__ import db
from __init__ import app

class Users(db.Model):
    __tablename__ = 'USERS'
    __table_args__ = {'schema': 'CW2'}

    UserID = db.Column(db.Integer, primary_key=True)
    Email = db.Column(db.String(75), nullable=False)
    Username = db.Column(db.String(25), nullable=False)
    Password = db.Column(db.String(25), nullable=False)
    Role = db.Column(db.String(50), nullable=False)

class Trails(db.Model):
    __tablename__ = 'TRAIL'
    __table_args__ = {'schema': 'CW2'}

    TrailID = db.Column(db.Integer, primary_key=True)
    TrailName = db.Column(db.String(100), nullable=False)
    TrailSummary = db.Column(db.String(100))
    TrailDescription = db.Column(db.String(100))
    Difficulty = db.Column(db.String(50))
    Location = db.Column(db.String(100))
    Length = db.Column(db.Float)
    ElevationGain = db.Column(db.Float)
    RouteType = db.Column(db.String(100))
    OwnedBy = db.Column(db.Integer, db.ForeignKey('USERS.UserID'))
    Rating = db.Column(db.Float)
    Pt1_Lat = db.Column(db.Float)
    Pt1_Long = db.Column(db.Float)
    Pt1_Desc = db.Column(db.String(100))
    Pt2_Lat = db.Column(db.Float)
    Pt2_Long = db.Column(db.Float)
    Pt2_Desc = db.Column(db.String(100))
    Pt3_Lat = db.Column(db.Float)
    Pt3_Long = db.Column(db.Float)
    Pt3_Desc = db.Column(db.String(100))
    Pt4_Lat = db.Column(db.Float)
    Pt4_Long = db.Column(db.Float)
    Pt4_Desc = db.Column(db.String(100))
    Pt5_Lat = db.Column(db.Float)
    Pt5_Long = db.Column(db.Float)
    Pt5_Desc = db.Column(db.String(100))

class Feature(db.Model):
    __tablename__ = 'FEATURE'
    __table_args__ = {'schema': 'CW2'}

    TrailFeatureID = db.Column(db.Integer, primary_key=True)
    TrailFeature = db.Column(db.String(50), nullable=False)

class Trail_Feature(db.Model):
    __tablename__ = 'TRAIL_FEATURE'
    __table_args__ = {'schema': 'CW2'}

    TrailID = db.Column(db.Integer , db.ForeignKey('TRAIL.TrailID'), primary_key=True)
    TrailFeatureID = db.Column(db.Integer, db.ForeignKey('FEATURE.TrailFeatureID'), primary_key=True)

with app.app_context():
    print("Tables Registered with SQLALCHEMY:")
    print(db.metadata.tables.keys())