import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from User import User
import logging
from datetime import timedelta
import secrets

app = Flask(__name__)

# Modern Flask configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            mood = request.form.get('mood', '').strip()

            if not username or not mood:
                flash('Please provide both username and mood.', 'error')
                return render_template('index.html')

            # Create user session
            user = User()
            user.set_name(username)
            user.set_mood(mood)
            user.set_mood_scores()

            # Store user in session
            session['user_data'] = {
                'name': user.name,
                'mood': user.mood,
                'mood_scores': user.mood_scores,
                'genres': [],
                'artists': [],
                'artist_ids': [],
                'recommendations': []
            }

            app.logger.info(f"User {username} started session with mood: {mood}")
            return redirect(url_for('genres'))

        return render_template('index.html')
    
    except Exception as e:
        app.logger.error(f"Error in index route: {e}")
        flash('An error occurred. Please try again.', 'error')
        return render_template('index.html')

@app.route('/genres', methods=['GET', 'POST'])
def genres():
    try:
        if 'user_data' not in session:
            flash('Session expired. Please start over.', 'warning')
            return redirect(url_for('index'))

        user = User()
        user_data = session['user_data']
        user.name = user_data['name']
        user.mood = user_data['mood']
        user.mood_scores = user_data['mood_scores']

        if request.method == 'POST':
            selected_genres_combined = request.form.get('selected_genres', '')
            
            if not selected_genres_combined:
                flash('Please select at least one genre.', 'error')
                return render_template('genres.html', preset_genres=user.preset_genres, user=user)

            selected_genres = [genre.strip() for genre in selected_genres_combined.split(',') if genre.strip()]
            
            # Validate and add genres
            for genre in selected_genres:
                user.add_genre(genre)
            
            if not user.genres:
                flash('No valid genres selected. Please try again.', 'error')
                return render_template('genres.html', preset_genres=user.preset_genres, user=user)

            # Get top artists for selected genres
            user.set_top_artist_for_genre()
            user.get_top_artist_for_genre()
            user.set_top_artist_for_genre_details()

            # Update session
            session['user_data']['genres'] = user.genres
            session['user_data']['top_artist_per_genre_details'] = user.top_artist_per_genre_details

            app.logger.info(f"User {user.name} selected {len(user.genres)} genres")
            return redirect(url_for('artists'))

        return render_template('genres.html', preset_genres=user.preset_genres, user=user)
    
    except Exception as e:
        app.logger.error(f"Error in genres route: {e}")
        flash('An error occurred while processing genres. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/artists', methods=['GET', 'POST'])
def artists():
    try:
        if 'user_data' not in session or 'top_artist_per_genre_details' not in session['user_data']:
            flash('Please complete the previous steps first.', 'warning')
            return redirect(url_for('index'))

        user_data = session['user_data']
        user = User()
        user.name = user_data['name']
        user.top_artist_per_genre_details = user_data['top_artist_per_genre_details']

        if request.method == 'POST':
            selected_artists = request.form.getlist('selected_artists')
            
            if not selected_artists:
                flash('Please select at least one artist.', 'error')
                return render_template('artists.html', user=user, top_artist_details=user.top_artist_per_genre_details)

            # Process selected artists
            for artist in selected_artists:
                if '|' in artist:
                    artist_name = artist.split('|')[0].strip()
                    user.add_artist(artist_name)

            if not user.artists:
                flash('No valid artists selected. Please try again.', 'error')
                return render_template('artists.html', user=user, top_artist_details=user.top_artist_per_genre_details)

            user.set_artist_ids()

            # Update session
            session['user_data']['artists'] = user.artists
            session['user_data']['artist_ids'] = user.artist_ids

            app.logger.info(f"User {user.name} selected {len(user.artists)} artists")
            return redirect(url_for('recommendations'))

        return render_template('artists.html', user=user, top_artist_details=user.top_artist_per_genre_details)
    
    except Exception as e:
        app.logger.error(f"Error in artists route: {e}")
        flash('An error occurred while processing artists. Please try again.', 'error')
        return redirect(url_for('genres'))

@app.route('/recommendations')
def recommendations():
    try:
        if 'user_data' not in session:
            flash('Session expired. Please start over.', 'warning')
            return redirect(url_for('index'))

        user_data = session['user_data']
        
        # Reconstruct user object
        user = User()
        user.name = user_data['name']
        user.mood = user_data['mood']
        user.mood_scores = user_data['mood_scores']
        user.genres = user_data.get('genres', [])
        user.artists = user_data.get('artists', [])
        user.artist_ids = user_data.get('artist_ids', [])

        # Generate recommendations
        user.set_recommendations()
        recommendation_data = user.get_recommendations()

        # Update session with recommendations
        session['user_data']['recommendations'] = recommendation_data

        app.logger.info(f"Generated {len(recommendation_data)} recommendations for user {user.name}")
        return render_template('recommendations.html', user=user, recommendation_data=recommendation_data)
    
    except Exception as e:
        app.logger.error(f"Error generating recommendations: {e}")
        flash('An error occurred while generating recommendations. Please try again.', 'error')
        return redirect(url_for('artists'))

@app.route('/api/user-session')
def get_user_session():
    """API endpoint to get current user session data"""
    if 'user_data' not in session:
        return jsonify({'error': 'No active session'}), 404
    return jsonify(session['user_data'])

@app.route('/start_over')
def start_over():
    """Clear session and start over"""
    session.clear()
    flash('Session cleared. Ready for a fresh start!', 'success')
    return redirect(url_for('index'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'JbTunez is running'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
