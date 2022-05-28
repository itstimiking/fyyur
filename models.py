from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    seeking_description = db.Column(db.String(500),nullable=True)
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String(200)),nullable=False)
    website_link = db.Column(db.String(120),nullable=False)
    seeking_talent = db.Column(db.Boolean,default=True)
    shows = db.relationship('Shows',backref='vanue', lazy="joined", cascade="delete")
    #artists_data = db.relationship('Artist',secondary='shows', backref=db.backref('venues_data',lazy=True))

    def __repr__(self):
        return f'<Venue id="{self.id}" name="{self.name}" city="{self.city}">'

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=True)
    genres = db.Column(db.ARRAY(db.String(200)),nullable=False)
    image_link = db.Column(db.String(500),nullable=True)
    facebook_link = db.Column(db.String(120),nullable=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120),nullable=True)
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.String(500),nullable=True)
    shows = db.relationship('Shows',backref='artist', lazy="joined", cascade="delete")

    def __repr__(self):
        return f'<Artist id="{self.id}" name="{self.name}" city="{self.city}" >'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    start_time = db.Column(db.String(120),nullable=False)

    def __repr__(self):
        return f'<Venue id="{self.id}" time={self.start_time}">'