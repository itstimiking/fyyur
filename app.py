#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import datetime
from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import ArtistForm, VenueForm, ShowForm
from models import db, Artist, Venue, Shows

from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
# TODO: connect to a local postgresql database


migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  venues = Venue.query.all()
  temp = {}
  now = datetime.datetime.now()
  data = []

  for v in venues:
    if v.state in temp.keys():
      v.num_upcoming_shows = 0
      for show in v.shows:
        time = datetime.datetime.strptime(show.start_time,"%Y-%m-%d %H:%M:%S")
        if time > now:
          v.num_upcoming_shows += 1
      temp[v.state]['venues'].append(v)
    else:
      v.num_upcoming_shows = 0
      for show in v.shows:
        time = datetime.datetime.strptime(show.start_time,"%Y-%m-%d %H:%M:%S")
        if time > now:
          v.num_upcoming_shows += 1
      temp[v.state] = {
        'city':v.city,
        'state':v.state,
        'venues':[v]
      }
      
  for item in temp.values():
    data.append(item)
    
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%'))

  now = datetime.datetime.now()
  data = []

  for venue in venues.all():
    upcoming_shows = 0
    for show in venue.shows:
      time = datetime.datetime.strptime(show.start_time,"%Y-%m-%d %H:%M:%S")
      if time > now:
        upcoming_shows += 1
    venue.num_upcoming_shows = upcoming_shows
    data.append(venue)
  
  response={
    "count": venues.count(),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get(venue_id)
  now = datetime.datetime.now()

  data.past_shows = []
  data.upcoming_shows = []
  for show in data.shows:
    time = datetime.datetime.strptime(show.start_time,"%Y-%m-%d %H:%M:%S")
    artist = Artist.query.get(show.artist_id)
    item = {
      'artist_id':artist.id,
      'artist_name':artist.name,
      'artist_image_link':artist.image_link,
      'start_time':show.start_time
    }
    if time > now:
      data.upcoming_shows.append(item)
    else:
      data.past_shows.append(item)

  data.website = data.website_link
  data.past_shows_count = len(data.past_shows)
  data.upcoming_shows_count = len(data.upcoming_shows)
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm()
  # TODO: insert form data as a new Venue record in the db, instead
  print(form.seeking_talent.data, request.form.get('seeking_talent'),":::::::::::::::::: bool val ::::::::::::")
  boolValue = False 
  if request.form.get('seeking_talent'):
     boolValue = True
  venue = Venue(
    name=request.form['name'],
    genres=request.form.getlist('genres'),
    address=request.form['address'],
    city=request.form['city'],
    state=request.form['state'],
    phone=request.form['phone'],
    website_link=request.form['website_link'],
    facebook_link=request.form['facebook_link'],
    seeking_talent= boolValue,
    image_link=request.form['image_link'],
    seeking_description=request.form['seeking_description']
  )

  # TODO: modify data to be the data object returned from db insertion
  try:
    db.session.add(venue)
    print(venue)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
    print(sys.exc_info(),"::::::::::::::::::::: ERROR :::::::::::::::::::")
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%'))

  now = datetime.datetime.now()
  data = []

  for artist in artists.all():
    upcoming_shows = 0
    for show in artist.shows:
      time = datetime.datetime.strptime(show.start_time,"%Y-%m-%d %H:%M:%S")
      if time > now:
        upcoming_shows += 1
    artist.num_upcoming_shows = upcoming_shows
    data.append(artist)
  
  response={
    "count": artists.count(),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  now = datetime.datetime.now()
  data = Artist.query.get(artist_id)
  data.past_shows = []
  data.upcoming_shows = []
  for show in data.shows:
    time = datetime.datetime.strptime(show.start_time,"%Y-%m-%d %H:%M:%S")
    venue = Venue.query.get(show.venue_id)
    item = {
      'venue_id':venue.id,
      'venue_name':venue.name,
      'venue_image_link':venue.image_link,
      'start_time':show.start_time
    }
    if time > now:
      data.upcoming_shows.append(item)
    else:
      data.past_shows.append(item)

  data.website = data.website_link
  data.past_shows_count = len(data.past_shows)
  data.upcoming_shows_count = len(data.upcoming_shows)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist=Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm()
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  boolValue = False 
  if request.form.get('seeking_venue'):
     boolValue = True
  try:
    artist=Artist.query.get(artist_id)
    artist.name = request.form['name']
    artist.state = request.form['state']
    artist.city = request.form['city']
    artist.phone = request.form['phone']
    artist.genres = request.form.getlist('genres')
    artist.seeking_venue = boolValue
    artist.seeking_description = request.form['seeking_description']
    artist.facebook_link = request.form['facebook_link']
    artist.image_link = request.form['image_link']
    artist.website_link = request.form['website_link']

    db.session.commit()
    flash("Success")
  except:
    db.session.rollback()
    print(sys.exc_info(),"::::::::::::::::")
    flash("Error artist data was not edited")
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue= Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  boolValue = False 
  if request.form.get('seeking_talent'):
     boolValue = True
  try:
    venue=Venue.query.get(venue_id)
    venue.name = request.form['name']
    venue.state = request.form['state']
    venue.city = request.form['city']
    venue.phone = request.form['phone']
    venue.address = request.form['address']
    venue.genres = request.form.getlist('genres')
    venue.seeking_talent = boolValue
    venue.seeking_description = request.form['seeking_description']
    venue.facebook_link = request.form['facebook_link']
    venue.image_link = request.form['image_link']
    venue.website_link = request.form['website_link']

    db.session.commit()
    flash("Success")
  except:
    db.session.rollback()
    print(sys.exc_info(),"::::::::::::::::")
    flash("Error venue data was not edited")
  finally:
    db.session.close()
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
  # TODO: insert form data as a new Venue record in the db, instead
  form = ArtistForm()
  boolValue = False 
  if request.form.get('seeking_venue'):
     boolValue = True

  artist = Artist(
    name= request.form['name'],
    genres= request.form.getlist('genres'),
    city= request.form['city'],
    state= request.form['state'],
    phone= request.form['phone'],
    website_link= request.form['website_link'],
    facebook_link= request.form['facebook_link'],
    seeking_venue= boolValue,
    image_link= request.form['image_link'],
    seeking_description= request.form['seeking_description']
  )
  # TODO: modify data to be the data object returned from db insertion
  try:
    db.session.add(artist)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Shows.query.all() 
  for show in shows:
    val = {
      'venue_id':show.vanue.id,
      'venue_name':show.vanue.name,
      'artist_id':show.artist.id,
      'artist_name':show.artist.name,
      "artist_image_link":show.artist.image_link,
      'start_time':show.start_time
    }
    data.append(val)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    show = Shows(artist_id=request.form['artist_id'],venue_id=request.form['venue_id'],start_time=request.form['start_time'])
    db.session.add(show)
    db.session.commit()
  # on successful db insert, flash success
    flash('Show was successfully listed for')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
    db.session.rollback()
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
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
