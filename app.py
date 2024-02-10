from flask import Flask, render_template, request, redirect, url_for
from User import User
import logging

app = Flask(__name__)

# Set the logging level to DEBUG for more detailed logs
app.logger.setLevel(logging.DEBUG)

# Sample user instance
user = User()

@app.route('/', methods=['GET', 'POST'])
def index(user=user):
    if request.method == 'POST':
        username = request.form.get('username')
        mood = request.form.get('mood')

        # Create an instance of your User class
        user.set_name(username)
        user.set_mood(mood)
        user.set_mood_scores()

        # Log the top artist details
        app.logger.debug(f"mood_scores: {user.mood_scores}")

        # Redirect to the genres page after processing the form data
        return redirect(url_for('genres'))

    return render_template('index.html')

@app.route('/genres', methods=['GET', 'POST'])
def genres():
    if request.method == 'POST':
        # Assuming you have a form field named 'selected_genres' in your genres.html template
        selected_genres_combined = request.form.get('selected_genres')
        #app.logger.debug(f"selected_genres_combined: {selected_genres_combined}")

        # Split the combined genres into a list
        selected_genres = [genre.strip() for genre in selected_genres_combined.split(',')]
        #app.logger.debug(f"selected_genres: {selected_genres}")

        # Add selected genres to the user
        for genre in selected_genres:
            app.logger.debug(f"genre: {genre}")
            user.add_genre(genre)
        user.set_top_artist_for_genre()
        user.get_top_artist_for_genre()
        user.set_top_artist_for_genre_details()

        # Log the top artist details
        #app.logger.debug(f"Top Artist Details: {user.top_artist_per_genre_details}")

        # Now redirect to the artists page
        return redirect(url_for('artists'))

    return render_template('genres.html', preset_genres=user.preset_genres, user=user)


# Artists route for selecting artists
@app.route('/artists', methods=['GET', 'POST'])
def artists():
    if request.method == 'POST':
        # Assuming you have a form field named 'selected_artists' in your artists.html template
        selected_artists = request.form.getlist('selected_artists')

        # Add selected artists to the user
        for artist in selected_artists:
            # Extract artist name and add to user
            artist_name = artist.split('|')[0].strip()
            user.add_artist(artist_name)
            #app.logger.debug(f"artists: {artist_name}")
        user.set_artist_ids()

        # Redirect to the recommendations page
        return redirect(url_for('recommendations'))

    # Render the artists.html template initially
    return render_template('artists.html', user=user, top_artist_details=user.top_artist_per_genre_details)

# Recommendations route
@app.route('/recommendations')
def recommendations():
    # Implement the logic for generating and displaying recommendations here
    user.set_recommendations()

    #app.logger.debug(f"RECS: {user.get_recommendations()}")
    recommendation_data = user.get_recommendations()
    return render_template('recommendations.html', user=user, recommendation_data=recommendation_data)

@app.route('/start_over')
def start_over():
    # Assuming you have a function to reset user data
    userame = None
    user.mood = None
    user.artists = []
    user.tracks = []

    user.genres = []
    user.mood_scores = None
    user.artist_ids = []
    user.track_ids = []
    user.genre_top_artist_ids = None
    user.top_artist_per_genre_ids = None
    user.top_artist_per_genre_details = None
    user.recommendations = []

    # Redirect to the starting page (replace 'index' with your actual starting page route)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
