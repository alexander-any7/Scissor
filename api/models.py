from datetime import datetime

from api.utils import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.Text(), nullable=False)
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    custom_domain = db.Column(db.Text(), nullable=True)
    urls = db.relationship("Url", backref="url", lazy=True)
    deleted_urls = db.relationship("DeletedUrl", backref="deleted_url", lazy=True)

    def __repr__(self) -> str:
        return self.username

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Url(db.Model):
    __tablename__ = "urls"
    id = db.Column(db.Integer(), primary_key=True)
    uuid = db.Column(db.String(10), nullable=False, unique=True)
    long_url = db.Column(db.String(1000), nullable=False, unique=False)
    qr_code = db.Column(db.String(500), nullable=True, unique=True)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    clicks = db.Column(db.Integer(), default=0)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)
    referrer = db.Column(db.Text())

    def __repr__(self) -> str:
        return self.uuid

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
        db.session.commit()


class DeletedUrl(db.Model):
    __tablename__ = "deleted_urls"
    id = db.Column(db.Integer(), primary_key=True)
    long_url = db.Column(db.String(1000), nullable=False, unique=False)
    created_at = db.Column(db.DateTime())
    deleted_at = db.Column(db.DateTime(), default=datetime.utcnow)
    user_id = db.Column(db.Integer(), db.ForeignKey("users.id"), nullable=False)

    def __repr__(self) -> str:
        return self.long_url

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
        db.session.commit()
