from Spotipy_song_rec import get_artist_id, get_track_id, get_recommendations, get_top_artist_for_genres, get_artist_details
class User:

    preset_genres = ['afrobeat', 'alt-rock', 'alternative','blues', 'chicago-house', 'children', 'chill', 'classical', 'club', 'country', 'dance', 'dancehall', 'drum-and-bass', 'dubstep', 'edm', 'electronic', 'funk', 'hip-hop', 'house', 'indie', 'indie-pop', 'jazz', 'k-pop', 'kids', 'latin', 'new-release', 'pop', 'r-n-b', 'reggaeton', 'rock', 'rock-n-roll', 'salsa', 'samba', 'singer-songwriter', 'sleep', 'songwriter', 'soul', 'spanish', 'study', 'synth-pop', 'folk', 'world-music']

    mood_presets = {
        'happy': {
            'target_valence': 0.8,  # High positiveness
            'target_energy': 0.8,  # High energy
            'target_danceability': 0.8,  # High danceability
            'target_tempo': 120,  # Medium tempo (adjust as needed)
            'target_instrumentalness': 0.2,  # Low instrumentalness (some vocals)
            'target_acousticness': 0.3,  # Low acousticness (not too acoustic)
        },
        'sad': {
            'target_valence': 0.3,  # Low positiveness
            'target_energy': 0.3,  # Low energy
            'target_speechiness': 0.1,  # Low speechiness (more instrumental)
            'target_tempo': 80,  # Slow tempo (adjust as needed)
            'target_acousticness': 0.7,  # High acousticness (more acoustic)
            'target_loudness': -10,  # Soft volume (adjust as needed)
        },
        'angry': {
            'target_valence': 0.2,  # Low positiveness
            'target_energy': 0.9,  # High energy
            'target_speechiness': 0.8,  # High speechiness (more intense)
            'target_tempo': 130,  # Fast tempo (adjust as needed)
            'target_instrumentalness': 0.1,  # Low instrumentalness (some vocals)
            'target_loudness': -5,  # Loud volume (adjust as needed)
        },
        'excited': {
            'target_valence': 0.9,  # High positiveness
            'target_energy': 0.9,  # High energy
            'target_danceability': 0.9,  # High danceability
            'target_tempo': 130,  # Fast tempo (adjust as needed)
            'target_instrumentalness': 0.1,  # Low instrumentalness (some vocals)
            'target_acousticness': 0.3,  # Low acousticness (not too acoustic)
        },
        'chill': {
            'target_valence': 0.5,  # Neutral positiveness
            'target_energy': 0.4,   # Low to medium energy
            'target_danceability': 0.5,  # Neutral danceability
            'target_tempo': 100,   # Medium tempo (adjust as needed)
            'target_instrumentalness': 0.5,  # Moderate instrumentalness
            'target_acousticness': 0.6,  # Moderate acousticness
            'target_loudness': -11,  # Very soft volume (adjust as needed)
        }
    }
    preset_moods = ['happy', 'sad', 'angry', 'excited', 'chill']

    def __init__(self):

        self.name = None
        self.mood = None
        self.artists = []
        self.tracks = []

        self.genres = []
        self.mood_scores = None
        self.artist_ids = []
        self.track_ids = []
        self.genre_top_artist_ids = None
        self.top_artist_per_genre_ids = None
        self.top_artist_per_genre_details = None
        self.recommendations = []

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_genres(self):
        return self.genres

    def add_genre(self, genre):
        # Check if the provided genre (in lowercase) is in the preset genres (all lowercase)
        lowercase_genre = genre.lower()

        if lowercase_genre in self.preset_genres:
            self.genres.append(lowercase_genre)
        else:
            print(f"{genre} is not a valid genre.")

    def get_mood(self):
        return self.mood

    def set_mood(self, mood):
        self.mood = mood.lower()

    def get_artists(self):
        return self.artists

    def add_artist(self,artist):
        self.artists.append(artist)

    def get_tracks(self):
        return self.tracks

    def add_track(self,song, artist):
        self.tracks.append({'song': song, 'artist': artist})

    def set_artist_ids(self):
        for artist in self.artists:
            artist_id = get_artist_id(artist)
            self.artist_ids.append(artist_id)

    def get_artist_ids(self):
        return self.artist_ids

    def set_track_ids(self):
        # Iterate over the user's tracks and get track IDs using get_track_id function
        for track in self.tracks:
            track_id = get_track_id(track['song'], track['artist'])
            self.track_ids.append(track_id)

    def get_track_ids(self):
        return self.track_ids

    def set_mood_scores(self):
        selected_mood = self.mood
        selected_attributes = self.mood_presets.get(selected_mood, {})

        if selected_attributes:
            self.mood_scores = selected_attributes
        else:
            print(f"Invalid mood: {self.mood}")

    def get_mood_scores(self):
        return self.mood_scores

    def set_recommendations(self):
        # Set mood scores if not already set
        if not self.mood_scores:
            self.set_mood_scores()

        # Call the get_recommendations method from YourClass
        recommendations = get_recommendations(
            seed_genres=self.genres,
            seed_artists=self.artist_ids,
            attributes=self.mood_scores,
            seed_tracks=self.track_ids
        )

        # Process recommendations and add to self.recommendations
        for track in recommendations['tracks']:

            song_name = track['name']
            artist_name = ', '.join([artist['name'] for artist in track['artists']])
            song_url = track['external_urls']['spotify']

            recommendation_entry = {'song_name': song_name, 'artist_name': artist_name, 'song_url': song_url}
            self.recommendations.append(recommendation_entry)

    def get_recommendations(self):
        return self.recommendations

    def set_top_artist_for_genre(self):
        top_artist = []

        for genre in self.genres:
            top_artist.append(get_top_artist_for_genres(genre))

        self.genre_top_artist_ids = top_artist

    def get_top_artist_for_genre(self):
        if len(self.genres) != len(self.genre_top_artist_ids):
            raise ValueError("Input lists must have the same length.")

        genre_artist_dict = {}

        for genre, artist_ids in zip(self.genres, self.genre_top_artist_ids):
            genre_artist_dict[genre] = artist_ids

        self.top_artist_per_genre_ids = genre_artist_dict
        return genre_artist_dict

    def set_top_artist_for_genre_details(self):
        result_dict = {}

        for genre, artist_ids in self.top_artist_per_genre_ids.items():
            result_dict[genre] = []
            for artist_id in artist_ids:
                details = get_artist_details(artist_id)
                result_dict[genre].append(details)

        self.top_artist_per_genre_details = result_dict
        return result_dict


# Testing Functionality


#rg = User("rob")

# #rg.add_artist("Lucky Daye")
# #rg.add_artist("Drake")
# rg.add_genre("blues")
# rg.add_genre("r-n-b")
# rg.set_mood("sad")
# #rg.add_track("Drake", "Marvins room")
# #rg.add_track("Zacari", "Don't Trip")
# rg.set_artist_ids()
# rg.set_track_ids()
# rg.set_mood_scores()
# rg.set_top_artist_for_genre()
# rg.get_top_artist_for_genre()

#rg.set_recommendations()


#print(rg.get_mood())
#print(rg.get_artists())
#print(rg.get_artist_ids())
#print(rg.get_genres())
#print(rg.get_tracks())
#print(rg.get_track_ids())
#print(rg.get_mood_scores())

#rg.get_recommendations()

#print(rg.set_top_artist_for_genre_details())
# other = User("other")
#
# other.add_artist("Beyonce")
# other.add_artist("Kehlani")
# other.add_genre("blues")
# other.add_genre("r-n-b")
# other.set_mood("chill")
# other.add_track("Kehlani", "Distraction")
# other.add_track("SZA", "Snooze")
# other.set_artist_ids()
# other.set_track_ids()
# other.set_mood_scores()
# other.set_recommendations()

print("--------------------------------------")
#other.get_recommendations()

print("--------------------------------------")

