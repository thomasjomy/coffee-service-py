import logging
from db import db

log = logging.getLogger(__name__)

class Coffee(db.Model):
    __tablename__ = 'coffee'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    version = db.Column(db.Integer, nullable=False)

    def __init__(self, coffee_id, name, version):
        self.id = coffee_id
        self.name = name
        self.version = version

    @classmethod
    def find_by_id(cls, coffee_id):
        log.debug('Finding coffee by id: %s', coffee_id)
        return cls.query.get(coffee_id)

    @classmethod
    def find_all(cls):
        log.debug('Finding all coffees')
        return cls.query.all()

    def save(self):
        log.debug('Saving coffee')
        db.session.add(self)
        db.session.commit()

    def delete(self):
        log.debug('Deleting coffee')
        db.session.delete(self)
        db.session.commit()

    @property
    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version
        }
