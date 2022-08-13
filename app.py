#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import enum
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from flask_migrate import Migrate
from sqlalchemy import Enum
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database : DONE

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # instead of just date = dateutil.parser.parse(value)
  if isinstance(value, str):
      date = dateutil.parser.parse(value)
  else:
      date = value

  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  venues_by_area = dict()

  venues = Venue.query.order_by('id').all()

  states_and_cities = Venue.query.with_entities(Venue.state, Venue.city).group_by('state', 'city').all()

  #raise Exception(states_and_cities)

  for state_and_city in states_and_cities:
    venues = Venue.query.filter_by(state=state_and_city[0], city=state_and_city[1])
    venues_by_area[state_and_city[1]+'-'+state_and_city[0]] = {'city':state_and_city[1], 'state':state_and_city[0], 'venues': []}
    for venue in venues:
      num_upcoming_shows = Show.query.filter(Show.start_time > datetime.now()).filter_by(venue_id=venue.id).count()
      venues_by_area[state_and_city[1]+'-'+state_and_city[0]]['venues'].append({
        'id' : venue.id,
        'name' : venue.name,
        'num_upcoming_shows' : num_upcoming_shows        
      })

  #data=[{
  # "city": "San Francisco",
  # "state": "CA",
  # "venues": [{
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "num_upcoming_shows": 0,
  #  }, {
  #    "id": 3,
  #    "name": "Park Square Live Music & Coffee",
  #    "num_upcoming_shows": 1,
  #  }]
  #}, {
  #  "city": "New York",
  #  "state": "NY",
  #  "venues": [{
  #    "id": 2,
  #    "name": "The Dueling Pianos Bar",
  #    "num_upcoming_shows": 0,
  #  }]
  #}]
  return render_template('pages/venues.html', areas=venues_by_area.values())

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_term = request.form.get('search_term', '')

  search = "%{}%".format(search_term)
  venues = Venue.query.filter(Venue.name.like(search)).all()

  data = []
  for venue in venues:
    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': Show.query.filter(Show.start_time > datetime.now()).filter_by(venue_id=venue.id).count()
    })

  response={
    "count": len(venues),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = venue.shows
  #venue.upcoming_shows = Show.query.filter(Show.start_time > datetime.now()).all()
  #venue.past_shows = Show.query.filter(Show.start_time < datetime.now()).all()

  for show in shows:
    if show.start_time > datetime.now():
      venue.upcoming_shows.append({
        'artist_id': show.artist_id,
        'artist_name' : show.artist.name,
        'artist_image_link' : show.artist.image_link,
        'start_time' : show.start_time
      })
    else:
      venue.past_shows.append({
        'artist_id': show.artist_id,
        'artist_name' : show.artist.name,
        'artist_image_link' : show.artist.image_link,
        'start_time' : show.start_time
    })


  return render_template('pages/show_venue.html', 
    venue=venue
  )

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  
  form = VenueForm()
  if form.validate_on_submit():    
    try:
      # TODO: insert form data as a new Venue record in the db, instead
      venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,      
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
        genres=form.genres.data
      )
      db.session.add(venue)
      db.session.commit()

      # TODO: modify data to be the data object returned from db insertion

      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('show_venue', venue_id=venue.id)) 

    except Exception as e:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      raise(e)
      #print(sys.exc_info())
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
      return render_template('forms/new_venue.html', form=form)
    finally:
      db.session.close()
  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash("Error in {}: {}".format(
          getattr(form, field).label.text, error), 'error')
        
    return render_template('forms/new_venue.html', form=form)
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.order_by('id').all()
  data = []
  for artist in artists:
    data.append({
      'id': artist.id, 
      'name' : artist.name, 
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term = request.form.get('search_term', '')

  search = "%{}%".format(search_term)
  artists = Artist.query.filter(Artist.name.like(search)).all()

  data = []
  for artist in artists:
    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': Show.query.filter(Show.start_time > datetime.now()).filter_by(artist_id=artist.id).count()
    })

  response={
    "count": len(artists),
    "data": data
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  
  shows = artist.shows #Show.query.filter(artist_id).all()
  
  #artist.past_shows = Show.query.filter(Show.start_time < datetime.now())
  #artist.upcoming_shows = Show.query.filter(Show.start_time > datetime.now()) 



  #past_shows = []
  #upcoming_shows = []
  
  for show in shows:
    if show.start_time > datetime.now():
      artist.upcoming_shows.append({
        'venue_id': show.venue_id,
        'venue_name' : show.venue.name,
        'venue_image_link' : show.venue.image_link,
        'start_time' : show.start_time
      })
    else:
      artist.past_shows.append({
        'venue_id': show.venue_id,
        'venue_name' : show.venue.name,
        'venue_image_link' : show.venue.image_link,
        'start_time' : show.start_time
    })


  #data = {
  #  'id' : artist.id,
  #  'name' : artist.name,
  #  'genres' : artist.genres,
  #  'city' : artist.city,
  #  'state' : artist.state,
  #  'phone' : artist.city,
  #  'website_link': artist.website_link,
  #  'facebook_link': artist.facebook_link,
  #  'seeking_venue': artist.seeking_venue,
  #  'seeking_description': artist.seeking_description,
  #  'image_link': artist.image_link,
  #  'past_shows' : artist.past_shows,
  #  'upcoming_shows': artist.upcoming_shows,
  #  'past_shows_count': 0, #len(past_shows),
  #  'upcoming_shows_count': 0 #len(upcoming_shows)
  #}

  #raise Exception(artist)

  return render_template('pages/show_artist.html', 
    artist=artist
  )

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  #form = ArtistForm()
  #artist={
  #  "id": 4,
  #  "name": "Guns N Petals",
  #  "genres": ["Rock n Roll"],
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "326-123-5000",
  #  "website": "https://www.gunsnpetalsband.com",
  #  "facebook_link": "https://www.facebook.com/GunsNPetals",
  #  "seeking_venue": True,
  #  "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #  "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  #}
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_description.data = artist.seeking_description
  form.genres.data = artist.genres
  form.seeking_venue.data = artist.seeking_venue

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  artist = Artist.query.get(artist_id)
  form = ArtistForm()
  if form.validate_on_submit():    
    try:
      # TODO: insert form data as a new Artist record in the db, instead
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data      
      artist.phone=form.phone.data
      artist.image_link=form.image_link.data
      artist.facebook_link=form.facebook_link.data
      artist.website_link=form.website_link.data     
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data
      artist.genres=form.genres.data
          
      db.session.commit()

      flash('Artist ' + artist.name + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist.id)) 
    except Exception as e:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')      
      raise(e)
      #print(sys.exc_info())
      flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')
      return render_template('forms/edit_artist.html', form=form, artist=artist)
    finally:
      db.session.close()
  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash("Error in {}: {}".format(
          getattr(form, field).label.text, error), 'error')
    return render_template('forms/new_artist.html', form=form)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_description.data = venue.seeking_description
  form.genres.data = venue.genres
  form.seeking_talent.data = venue.seeking_talent

  #venue={
  #  "id": 1,
  #  "name": "The Musical Hop",
  #  "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #  "address": "1015 Folsom Street",
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "phone": "123-123-1234",
  #  "website": "https://www.themusicalhop.com",
  #  "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #  "seeking_talent": True,
  #  "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #  "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  #}
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  form = VenueForm()
  if form.validate_on_submit():    
    try:
      # TODO: insert form data as a new Artist record in the db, instead
      venue.name=form.name.data
      venue.city=form.city.data
      venue.state=form.state.data      
      venue.phone=form.phone.data
      venue.address=form.address.data
      venue.image_link=form.image_link.data
      venue.facebook_link=form.facebook_link.data
      venue.website_link=form.website_link.data     
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      venue.genres=form.genres.data
          
      db.session.commit()

      flash('Venue ' + venue.name + ' was successfully updated!')
      return redirect(url_for('show_venue', venue_id=venue.id)) 
    except Exception as e:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')      
      raise(e)
      #print(sys.exc_info())
      flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')
      return render_template('forms/edit_venue.html', form=form, venue=venue)
    finally:
      db.session.close()
  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash("Error in {}: {}".format(
          getattr(form, field).label.text, error), 'error')
    return render_template('forms/new_venue.html', form=form)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  form = ArtistForm()
  if form.validate_on_submit():    
    try:
      # TODO: insert form data as a new Artist record in the db, instead
      artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,        
        phone=form.phone.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,      
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
        genres=form.genres.data
      )
      db.session.add(artist)
      db.session.commit()
      
      # TODO: modify data to be the data object returned from db insertion

      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return redirect(url_for('show_artist', artist_id=artist.id)) 
    
    except Exception as e:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')      
      raise(e)
      #print(sys.exc_info())
      flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
      return render_template('forms/new_artist.html', form=form)
    
    finally:
      db.session.close()    
  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash("Error in {}: {}".format(
          getattr(form, field).label.text, error), 'error')
      return render_template('forms/new_artist.html', form=form)

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.order_by('id').all()
  data = []
  for show in shows:
    data.append({
      'venue_id': show.venue_id, 
      'venue_name' : show.venue.name, 
      'artist_id' : show.artist_id,
      'artist_name' : show.artist.name,
      'artist_image_link' : show.artist.image_link,
      'start_time' : show.start_time
      })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm()
  if form.validate_on_submit():    
    try:
      # TODO: insert form data as a new Show record in the db, instead
      show = Show(
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data,
      )
      db.session.add(show)
      db.session.commit()      
      # TODO: modify data to be the data object returned from db insertion
      # on successful db insert, flash success
      flash('Show was successfully listed!')
      return redirect(url_for('shows')) 
    except Exception as e:
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      raise(e)
      #print(sys.exc_info())
      flash('An error occurred. Show could not be listed.')
      return render_template('forms/new_show.html', form=form)
    finally:
      db.session.close() 
  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash("Error in {}: {}".format(
          getattr(form, field).label.text, error), 'error')
    return render_template('forms/new_show.html', form=form)
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
