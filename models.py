#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))    
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate    
    website_link = db.Column(db.String(250), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='venue', lazy=True)
    # genres = db.relationship('Genre', secondary=venue_genres,
    # backref=db.backref('venues', lazy=True))
    # genres = db.Column(db.Enum(Genres, create_type=True))

    upcoming_shows = []
    past_shows = []

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(250), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)
    # genres = db.relationship('Genre', secondary=artist_genres,
    #  backref=db.backref('artists', lazy=True))
    #genres = db.Column(db.Enum(Genres, create_type=True))

    upcoming_shows = []
    past_shows = []

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

class Genres(enum.Enum):
  Alternative = 'Alternative'
  Blues = 'Blues'
  Classical = 'Classical'
  Country = 'Country'
  Electronic = 'Electronic'
  Folk = 'Folk'
  Funk = 'Funk'
  Hip_Hop = 'Hip-Hop'
  Heavy_Metal = 'Heavy Metal'
  Instrumental = 'Instrumental'
  Jazz = 'Jazz'
  Musical_Theatre = 'Musical Theatre'
  Pop = 'Pop'
  Punk = 'Punk'
  R_B = 'R&B'
  Reggae = 'Reggae'
  Rock_n_Roll = 'Rock n Roll'
  Soul = 'Soul'
  Other = 'Other'

#class Genre(db.Model):
#    __tablename__ = 'genres'
#
#    id = db.Column(db.Integer, primary_key=True)
#    label = db.Column(db.String(20), nullable=True)

# many_to_many relation venues with genres: association table 
#venue_genres = db.Table('venue_genres',
#    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
#    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
#)

# many_to_many relation artists with genres: association table 
#artist_genres = db.Table('artist_genres',
#    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
#    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
#)