from Spotipy_song_rec import get_artist_id, get_track_id, get_recommendations, get_top_artist_for_genres, get_artist_details
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class User:
    """Modern User class with enhanced functionality for music recommendations"""

    preset_genres = [
        'afrobeat', 'alt-rock', 'alternative', 'blues', 'chicago-house', 'children', 
        'chill', 'classical', 'club', 'country', 'dance', 'dancehall', 'drum-and-bass', 
        'dubstep', 'edm', 'electronic', 'funk', 'hip-hop', 'house', 'indie', 'indie-pop', 
        'jazz', 'k-pop', 'kids', 'latin', 'new-release', 'pop', 'r-n-b', 'reggaeton', 
        'rock', 'rock-n-roll', 'salsa', 'samba', 'singer-songwriter', 'sleep', 'songwriter', 
        'soul', 'spanish', 'study', 'synth-pop', 'folk', 'world-music'
    ]

    mood_presets = {
        'happy': {
            'target_valence': 0.8,  # High positiveness
            'target_energy': 0.8,  # High energy
            'target_danceability': 0.8,  # High danceability
            'target_tempo': 120,  # Medium tempo
            'target_instrumentalness': 0.2,  # Low instrumentalness (some vocals)
            'target_acousticness': 0.3,  # Low acousticness (not too acoustic)
        },
        'sad': {
            'target_valence': 0.3,  # Low positiveness
            'target_energy': 0.3,  # Low energy
            'target_speechiness': 0.1,  # Low speechiness (more instrumental)
            'target_tempo': 80,  # Slow tempo
            'target_acousticness': 0.7,  # High acousticness (more acoustic)
            'target_loudness': -10,  # Soft volume
        },
        'angry': {
            'target_valence': 0.2,  # Low positiveness
            'target_energy': 0.9,  # High energy
            'target_speechiness': 0.8,  # High speechiness (more intense)
            'target_tempo': 130,  # Fast tempo
            'target_instrumentalness': 0.1,  # Low instrumentalness (some vocals)
            'target_loudness': -5,  # Loud volume
        },
        'excited': {
            'target_valence': 0.9,  # High positiveness
            'target_energy': 0.9,  # High energy
            'target_danceability': 0.9,  # High danceability
            'target_tempo': 130,  # Fast tempo
            'target_instrumentalness': 0.1,  # Low instrumentalness (some vocals)
            'target_acousticness': 0.3,  # Low acousticness (not too acoustic)
        },
        'chill': {
            'target_valence': 0.5,  # Neutral positiveness
            'target_energy': 0.4,   # Low to medium energy
            'target_danceability': 0.5,  # Neutral danceability
            'target_tempo': 100,   # Medium tempo
            'target_instrumentalness': 0.5,  # Moderate instrumentalness
            'target_acousticness': 0.6,  # Moderate acousticness
            'target_loudness': -11,  # Very soft volume
        }
    }
    
    preset_moods = ['happy', 'sad', 'angry', 'excited', 'chill']

    def __init__(self, name: Optional[str] = None):
        """Initialize a new User instance"""
        self.name: Optional[str] = name
        self.mood: Optional[str] = None
        self.artists: List[str] = []
        self.tracks: List[Dict[str, str]] = []
        self.genres: List[str] = []
        self.mood_scores: Optional[Dict] = None
        self.artist_ids: List[str] = []
        self.track_ids: List[str] = []
        self.genre_top_artist_ids: Optional[List] = None
        self.top_artist_per_genre_ids: Optional[Dict] = None
        self.top_artist_per_genre_details: Optional[Dict] = None
        self.recommendations: List[Dict] = []

    def get_name(self) -> Optional[str]:
        """Get user's name"""
        return self.name

    def set_name(self, name: str) -> None:
        """Set user's name with validation"""
        if not name or not name.strip():
            raise ValueError("Name cannot be empty")
        self.name = name.strip()

    def get_genres(self) -> List[str]:
        """Get user's selected genres"""
        return self.genres.copy()

    def add_genre(self, genre: str) -> bool:
        """Add a genre to user's preferences with validation"""
        if not genre:
            return False
            
        lowercase_genre = genre.lower().strip()
        
        if lowercase_genre in self.preset_genres and lowercase_genre not in self.genres:
            self.genres.append(lowercase_genre)
            logger.info(f"Added genre: {lowercase_genre}")
            return True
        elif lowercase_genre in self.genres:
            logger.warning(f"Genre {lowercase_genre} already selected")
            return True
        else:
            logger.warning(f"{genre} is not a valid genre")
            return False

    def remove_genre(self, genre: str) -> bool:
        """Remove a genre from user's preferences"""
        lowercase_genre = genre.lower().strip()
        if lowercase_genre in self.genres:
            self.genres.remove(lowercase_genre)
            logger.info(f"Removed genre: {lowercase_genre}")
            return True
        return False

    def get_mood(self) -> Optional[str]:
        """Get user's current mood"""
        return self.mood

    def set_mood(self, mood: str) -> bool:
        """Set user's mood with validation"""
        if not mood:
            return False
            
        mood_lower = mood.lower().strip()
        if mood_lower in self.preset_moods:
            self.mood = mood_lower
            logger.info(f"Set mood: {mood_lower}")
            return True
        else:
            logger.warning(f"Invalid mood: {mood}")
            return False

    def get_artists(self) -> List[str]:
        """Get user's selected artists"""
        return self.artists.copy()

    def add_artist(self, artist: str) -> bool:
        """Add an artist to user's preferences"""
        if not artist or not artist.strip():
            return False
            
        artist_clean = artist.strip()
        if artist_clean not in self.artists:
            self.artists.append(artist_clean)
            logger.info(f"Added artist: {artist_clean}")
            return True
        else:
            logger.warning(f"Artist {artist_clean} already selected")
            return True

    def remove_artist(self, artist: str) -> bool:
        """Remove an artist from user's preferences"""
        artist_clean = artist.strip()
        if artist_clean in self.artists:
            self.artists.remove(artist_clean)
            logger.info(f"Removed artist: {artist_clean}")
            return True
        return False

    def add_multiple_artists(self, artists: List[str]) -> int:
        """Add multiple artists and return count of successfully added"""
        added_count = 0
        for artist in artists:
            if self.add_artist(artist):
                added_count += 1
        return added_count

    def get_tracks(self) -> List[Dict[str, str]]:
        """Get user's selected tracks"""
        return self.tracks.copy()

    def add_track(self, song: str, artist: str) -> bool:
        """Add a track to user's preferences"""
        if not song or not artist:
            return False
            
        track = {'song': song.strip(), 'artist': artist.strip()}
        if track not in self.tracks:
            self.tracks.append(track)
            logger.info(f"Added track: {song} by {artist}")
            return True
        return False

    def set_artist_ids(self) -> None:
        """Convert artist names to Spotify IDs with error handling"""
        self.artist_ids = []
        for artist in self.artists:
            try:
                artist_id = get_artist_id(artist)
                if artist_id:
                    self.artist_ids.append(artist_id)
                    logger.info(f"Found ID for artist: {artist}")
                else:
                    logger.warning(f"Could not find ID for artist: {artist}")
            except Exception as e:
                logger.error(f"Error getting ID for artist {artist}: {e}")

    def get_artist_ids(self) -> List[str]:
        """Get Spotify artist IDs"""
        return self.artist_ids.copy()

    def set_track_ids(self) -> None:
        """Convert track names to Spotify IDs with error handling"""
        self.track_ids = []
        for track in self.tracks:
            try:
                track_id = get_track_id(track['song'], track['artist'])
                if track_id:
                    self.track_ids.append(track_id)
                    logger.info(f"Found ID for track: {track['song']}")
                else:
                    logger.warning(f"Could not find ID for track: {track['song']}")
            except Exception as e:
                logger.error(f"Error getting ID for track {track['song']}: {e}")

    def get_track_ids(self) -> List[str]:
        """Get Spotify track IDs"""
        return self.track_ids.copy()

    def set_mood_scores(self) -> bool:
        """Set mood-based audio features"""
        if not self.mood:
            logger.error("No mood set")
            return False
            
        selected_attributes = self.mood_presets.get(self.mood, {})
        
        if selected_attributes:
            self.mood_scores = selected_attributes.copy()
            logger.info(f"Set mood scores for mood: {self.mood}")
            return True
        else:
            logger.error(f"Invalid mood: {self.mood}")
            return False

    def get_mood_scores(self) -> Optional[Dict]:
        """Get mood-based audio features"""
        return self.mood_scores.copy() if self.mood_scores else None

    def set_recommendations(self, limit: int = 20) -> bool:
        """Generate personalized recommendations with error handling"""
        try:
            # Ensure mood scores are set
            if not self.mood_scores:
                if not self.set_mood_scores():
                    logger.error("Could not set mood scores")
                    return False

            # Ensure we have some preferences
            if not self.genres and not self.artist_ids and not self.track_ids:
                logger.error("No preferences set for recommendations")
                return False

            # Get recommendations from Spotify
            recommendations = get_recommendations(
                seed_genres=self.genres[:5],  # Spotify limits to 5 total seeds
                seed_artists=self.artist_ids[:5],
                attributes=self.mood_scores,
                seed_tracks=self.track_ids[:5]
            )

            # Process and store recommendations
            self.recommendations = []
            for track in recommendations.get('tracks', [])[:limit]:
                try:
                    song_name = track['name']
                    artist_name = ', '.join([artist['name'] for artist in track['artists']])
                    song_url = track['external_urls']['spotify']
                    preview_url = track.get('preview_url')
                    album_cover = track['album']['images'][0]['url'] if track['album']['images'] else None

                    recommendation_entry = {
                        'song_name': song_name,
                        'artist_name': artist_name,
                        'song_url': song_url,
                        'preview_url': preview_url,
                        'album_cover': album_cover,
                        'popularity': track.get('popularity', 0)
                    }
                    self.recommendations.append(recommendation_entry)
                except Exception as e:
                    logger.error(f"Error processing track recommendation: {e}")
                    continue

            logger.info(f"Generated {len(self.recommendations)} recommendations")
            return True
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return False

    def get_recommendations(self) -> List[Dict]:
        """Get generated recommendations"""
        return self.recommendations.copy()

    def set_top_artist_for_genre(self) -> bool:
        """Get top artists for each selected genre"""
        try:
            self.genre_top_artist_ids = []
            for genre in self.genres:
                top_artist_ids = get_top_artist_for_genres(genre)
                self.genre_top_artist_ids.append(top_artist_ids)
            return True
        except Exception as e:
            logger.error(f"Error getting top artists for genres: {e}")
            return False

    def get_top_artist_for_genre(self) -> Optional[Dict]:
        """Map genres to their top artists"""
        try:
            if not self.genres or not self.genre_top_artist_ids:
                return None
                
            if len(self.genres) != len(self.genre_top_artist_ids):
                logger.error("Mismatch between genres and artist IDs")
                return None

            genre_artist_dict = {}
            for genre, artist_ids in zip(self.genres, self.genre_top_artist_ids):
                genre_artist_dict[genre] = artist_ids

            self.top_artist_per_genre_ids = genre_artist_dict
            return genre_artist_dict
        except Exception as e:
            logger.error(f"Error mapping genres to artists: {e}")
            return None

    def set_top_artist_for_genre_details(self) -> bool:
        """Get detailed information for top artists"""
        try:
            if not self.top_artist_per_genre_ids:
                return False
                
            result_dict = {}
            for genre, artist_ids in self.top_artist_per_genre_ids.items():
                result_dict[genre] = []
                for artist_id in artist_ids[:8]:  # Limit to 8 artists per genre
                    try:
                        details = get_artist_details(artist_id)
                        if details:
                            result_dict[genre].append(details)
                    except Exception as e:
                        logger.error(f"Error getting details for artist {artist_id}: {e}")
                        continue

            self.top_artist_per_genre_details = result_dict
            return True
        except Exception as e:
            logger.error(f"Error getting artist details: {e}")
            return False

    def get_user_summary(self) -> Dict:
        """Get a summary of user's current state"""
        return {
            'name': self.name,
            'mood': self.mood,
            'genres_count': len(self.genres),
            'artists_count': len(self.artists),
            'tracks_count': len(self.tracks),
            'recommendations_count': len(self.recommendations),
            'has_mood_scores': self.mood_scores is not None
        }

    def clear_all_data(self) -> None:
        """Clear all user data for a fresh start"""
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
        logger.info(f"Cleared all data for user: {self.name}")

# Remove the test code at the bottom of the file
if __name__ == "__main__":
    # Example usage
    user = User("test_user")
    user.set_mood("happy")
    user.add_genre("pop")
    user.add_genre("rock")
    print(user.get_user_summary())

