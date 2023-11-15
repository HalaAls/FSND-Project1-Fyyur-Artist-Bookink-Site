#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://hala@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # genre = db.Column(db.ARRAY(db.String()))
    seeking_talent = db.Column(db.Boolean , nullable = False , default = False)
    talent_description = db.Column(db.String(300), default='')
    website = db.Column(db.String(200))
    venueShow = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
          return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.facebook_link}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    ##
    # genre = db.Column(db.ARRAY(db.String(200)))
    seeking_venue = db.Column(db.Boolean , nullable = False , default = False)
    venue_description = db.Column(db.String(300), default='')
    website = db.Column(db.String(200))
    artistShow = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
          return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link}>'

          
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model): ## DONE
      __tablename__: 'Show'
      id = db.Column(db.Integer, primary_key=True)
      artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
      venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
      start_time = db.Column(db.DateTime , nullable=False)

      def __repr__(self):
            return f'<Show {self.id} {self.artist_id} { self.venue_id} {self.start_time}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venue = Venue.query.all()
  data = []
  for ven in venue:
        d = {
          "city": ven.city ,
          "state": ven.state ,
          "venues": [{
            "id" : ven.id,
            "name" : ven.name,
          }]
        }
        data.append(d)
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues(): ## done
      # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike('%'+search+'%')).all() 
  data = []
  for ven in venues:
        showCoun= Show.query.filter_by(venue_id = ven.id).count()
        d ={
          "id" : ven.id,
          "name" : ven.name,
          "num_upcoming_shows" : showCoun
        }
        data.append(d)

  response={
    "count": len(venues),
    "data" : data
    }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id): ## DONE
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  upcomingShow = []
  pastShow = []
  for showVenue in venue.venueShow :
      atristDate = {
        "artist_id": showVenue.artist_id,
        "artist_name" : showVenue.artist.name,
        "start_time" : str(showVenue.start_time),
        "artist_image_link" : showVenue.artist.image_link
      }
      if showVenue.start_time > datetime.now():
        upcomingShow.append(atristDate)
      else :
        pastShow.append(atristDate)

  data={
    "id": venue.id,
    "name": venue.name,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":venue.talent_description,
    "image_link": venue.image_link,
    "past_shows": pastShow,
    "upcoming_shows": upcomingShow ,
    "past_shows_count": len(pastShow),
    "upcoming_shows_count": len(upcomingShow)
    }

  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission(): #### DONE
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  name = request.form.get('name'),
  city = request.form.get('city'),
  state = request.form.get('state'),
  address = request.form.get('address'),
  phone = request.form.get('phone'),
  facebook_link = request.form.get('facebook_link'),
  data = Venue(name=name, city=city, state=state, address=address, phone=phone, facebook_link=facebook_link)
  try:
    db.session.add(data)
    db.session.commit()
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except : 
    error=True
    print(sys.exc_info())
    flash('An error occurred. Venue ' +request.form['name'] + ' could not be listed.')
    db.session.rollback()
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally :
    db.session.close()
  return render_template('pages/home.html')



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try :
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue was successfully deleted!')
  except : 
    flash('An error occurred venue could not be deleted.')
    db.session.rollback()
  finally :
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None



#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists(): # done
  # TODO: replace with real data returned from querying the database
  artist = Artist.query.all()

  data = []
  for a in artist:
        d = {
          "id" : a.id,
          "name" : a.name
        }
        data.append(d)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists(): ## done
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term', '')
  artist = Artist.query.filter(Artist.name.ilike('%'+search+'%')).all()
  data = []
  for art in artist:
      showCoun= Show.query.filter_by(artist_id = art.id).count()
      d ={
        "id" : art.id,
        "name" : art.name,
        "num_upcoming_shows" : showCoun
        }
      data.append(d)
  
  response={
    "count": len(artist),
    "data" : data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  upcomingSh = []
  pastSh = []
  for showArtist in artist.artistShow :
      venData = {
        "venue_id": showArtist.venue_id,
        "venue_name" : showArtist.venue.name,
        "start_time" : str(showArtist.start_time),
        "venue_image_link" : showArtist.venue.image_link
      }
      if showArtist.start_time > datetime.now():
        upcomingSh.append(venData)
      else :
        pastSh.append(venData)

  data={
    "id": artist.id,
    "name": artist.name,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link,
    "past_shows": pastSh,
    "upcoming_shows": upcomingSh ,
    "past_shows_count": len(pastSh),
    "upcoming_shows_count": len(upcomingSh)
  }

  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
  artists = Artist.query.get(artist_id)
  # #
  artist = {
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    "website": artists.website,
    "facebook_link": artists.facebook_link,
    "seeking_venue": artists.seeking_venue,
    "seeking_description": artists.seeking_description,
    "image_link": artists.image_link
  }

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artistID = Artist.query.get(artist_id)
  try : 
    artistID.name = request.form['name'],
    artistID.city = request.form['city'],
    artistID.state = request.form['state'],
    artistID.address = request.form['address'],
    artistID.phone = request.form['phone'],
    artistID.facebook_link = request.form['facebook_link'],
    artistID.genres = request.form['genres']
    db.session.commit()
    flash('Artist was successfully updated!')
  except :
    db.session.rollback()
    flash('An error occurred .')
  finally :
    db.session.close()
    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  vens = Venue.query.get(venue_id)
  venue={
    "id": vens.id,
    "name": vens.name,
    # "genres": vens.genres,
    "address": vens.address,
    "city": vens.city,
    "state": vens.state,
    "phone": vens.phone,
    "website": vens.website,
    "facebook_link": vens.facebook_link,
    "seeking_talen": vens.seeking_talent,
    "seeking_description": vens.seeking_description,
    "image_link": vens.image_link
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venID = Venue.query.get(venue_id)
  try : 
    venID.name = request.form['name'],
    venID.city = request.form['city'],
    venID.state = request.form['state'],
    venID.address = request.form['address'],
    venID.phone = request.form['phone'],
    venID.facebook_link = request.form['facebook_link'],
    venID.genres = request.form['genres']
    db.session.commit()
    flash('Venue was successfully updated!')
  except :
    db.session.rollback()
    flash('An error occurred .')
  finally :
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission(): ## done
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  facebook_link = request.form.get('facebook_link')
  data = Artist(
    name = name,
    city = city,
    state = state, phone = phone,
    facebook_link = facebook_link
    )
  try:
 
    db.session.add(data)
    db.session.commit()
  # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except : 
    flash('An error occurred. Venue ' +request.form['name'] + ' could not be listed.')
    db.session.rollback()
  finally :
    db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data=[]
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
      })
    # data.append(d)
  
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
    error : False
    venue_id = request.form.get('venue_id'),
    artist_id = request.form.get('artist_id'),
    start_time = request.form.get('start_time'),
    # image_link = request.form.get('image_link'),

    data = Show(
      venue_id=venue_id,
      artist_id=artist_id,
      start_time=start_time,
      # image_link=image_link
      )
    try:
      db.session.add(data)
      db.session.commit()
  # on successful db insert, flash success
      flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
    except: 
      error = True
      flash('An error occurred. Venue ' +request.form['name'] + ' could not be listed.')
      db.session.rollback()
    finally :
      db.session.close()
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
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
