from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Commodity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)

class UserRation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)  # Store unique user ID
    commodity = db.Column(db.String(50), nullable=False)
    quota_limit = db.Column(db.Integer, nullable=False)  # Monthly ration limit
    consumed = db.Column(db.Integer, default=0)  # How much user already took

    _table_args_ = (db.UniqueConstraint('user_id', 'commodity', name='user_commodity_uc'),)
