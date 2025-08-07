import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import logging
from typing import List, Dict, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Try to load from environment variables first (production)
client_id = os.environ.get('SPOTIFY_CLIENT_ID')
client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
redirect_url = os.environ.get('SPOTIFY_REDIRECT_URI', 'http://localhost:5000/callback')

# Fallback to spotify.py file (development)
if not client_id or not client_secret:
    try:
        import spotify
        client_id = spotify.client_id
        client_secret = spotify.client_secret
        redirect_url = getattr(spotify, 'redirect_url', redirect_url)
        logger.info("Loaded Spotify credentials from spotify.py")
    except ImportError:
        logger.error("No Spotify credentials found. Please set environment variables or create spotify.py")
        raise ValueError("Spotify credentials not configured. See README.md for setup instructions.")

# OAuth scope for the application
scope = "user-library-read playlist-read-private"

# Initialize Spotify client with enhanced error handling
try:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_url,
        scope=scope,
        cache_path=".spotify_cache"
    ))
    logger.info("Spotify client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Spotify client: {e}")
    raise


def get_track_id(song_name: str, artist_name: str) -> Optional[str]:
    """
    Search for a track using song name and artist name.
    
    Args:
        song_name: Name of the song
        artist_name: Name of the artist
        
    Returns:
        Spotify track ID if found, None otherwise
    """
    try:
        query = f"track:{song_name} artist:{artist_name}"
        results = sp.search(q=query, type='track', limit=1)

        if results['tracks']['items']:
            track_id = results['tracks']['items'][0]['id']
            logger.debug(f"Found track ID for '{song_name}' by '{artist_name}': {track_id}")
            return track_id
        else:
            logger.warning(f"No track found for '{song_name}' by '{artist_name}'")
            return None
    except Exception as e:
        logger.error(f"Error searching for track '{song_name}' by '{artist_name}': {e}")
        return None


def get_artist_id(artist_name: str) -> Optional[str]:
    """
    Search for an artist using their name.
    
    Args:
        artist_name: Name of the artist
        
    Returns:
        Spotify artist ID if found, None otherwise
    """
    try:
        query = f"artist:{artist_name}"
        results = sp.search(q=query, type='artist', limit=1)

        if results['artists']['items']:
            artist_id = results['artists']['items'][0]['id']
            logger.debug(f"Found artist ID for '{artist_name}': {artist_id}")
            return artist_id
        else:
            logger.warning(f"No artist found for '{artist_name}'")
            return None
    except Exception as e:
        logger.error(f"Error searching for artist '{artist_name}': {e}")
        return None


def get_album_id(album_name: str, artist_name: str) -> Optional[str]:
    """
    Search for an album using album name and artist name.
    
    Args:
        album_name: Name of the album
        artist_name: Name of the artist
        
    Returns:
        Spotify album ID if found, None otherwise
    """
    try:
        query = f"album:{album_name} artist:{artist_name}"
        results = sp.search(q=query, type='album', limit=1)

        if results['albums']['items']:
            album_id = results['albums']['items'][0]['id']
            logger.debug(f"Found album ID for '{album_name}' by '{artist_name}': {album_id}")
            return album_id
        else:
            logger.warning(f"No album found for '{album_name}' by '{artist_name}'")
            return None
    except Exception as e:
        logger.error(f"Error searching for album '{album_name}' by '{artist_name}': {e}")
        return None


def get_recommendations(seed_genres: List[str], seed_artists: List[str], 
                       seed_tracks: List[str], attributes: Dict, 
                       limit: int = 20) -> Optional[Dict]:
    """
    Get music recommendations based on seed data and audio features.
    
    Args:
        seed_genres: List of genre strings
        seed_artists: List of artist IDs
        seed_tracks: List of track IDs
        attributes: Dictionary of audio feature targets
        limit: Maximum number of recommendations to return
        
    Returns:
        Spotify recommendations response or None if error
    """
    try:
        # Make working copies to avoid modifying original lists
        working_genres = seed_genres.copy()
        working_artists = seed_artists.copy()
        working_tracks = seed_tracks.copy()
        
        # Spotify API allows maximum 5 seeds total
        max_total_seeds = 5
        all_seeds = working_genres + working_artists + working_tracks
        
        if len(all_seeds) > max_total_seeds:
            logger.info(f"Adjusting seed distribution from {len(all_seeds)} to {max_total_seeds} items")
            
            # Prioritize in order: genres, artists, tracks
            final_genres = working_genres[:min(2, len(working_genres))]
            remaining_slots = max_total_seeds - len(final_genres)
            
            final_artists = working_artists[:min(remaining_slots, len(working_artists))]
            remaining_slots -= len(final_artists)
            
            final_tracks = working_tracks[:min(remaining_slots, len(working_tracks))]
            
            working_genres = final_genres
            working_artists = final_artists
            working_tracks = final_tracks
            
            logger.debug(f"Final seeds - Genres: {len(working_genres)}, Artists: {len(working_artists)}, Tracks: {len(working_tracks)}")

        # Merge attributes with seed data
        recommendation_params = {
            **attributes,
            'seed_genres': working_genres,
            'seed_artists': working_artists,
            'seed_tracks': working_tracks,
            'limit': limit
        }
        
        # Remove empty seed lists to avoid API errors
        recommendation_params = {k: v for k, v in recommendation_params.items() 
                               if not (isinstance(v, list) and len(v) == 0)}

        # Call Spotify recommendations API
        recommendations = sp.recommendations(**recommendation_params)
        
        logger.info(f"Successfully retrieved {len(recommendations.get('tracks', []))} recommendations")
        return recommendations

    except spotipy.SpotifyException as e:
        logger.error(f"Spotify API error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting recommendations: {e}")
        return None


def get_top_artist_for_genres(*genres: str) -> List[str]:
    """
    Get top artists for specified genres.
    
    Args:
        *genres: Variable number of genre strings
        
    Returns:
        List of artist IDs for top artists in those genres
    """
    artist_ids = []
    
    for genre in genres:
        try:
            logger.debug(f"Searching for top artists in genre: {genre}")
            results = sp.search(q=f'genre:{genre}', type='artist', limit=10)
            
            genre_artists = []
            for artist in results['artists']['items']:
                if artist['id']:  # Ensure artist has valid ID
                    genre_artists.append(artist['id'])
                    
            artist_ids.extend(genre_artists)
            logger.debug(f"Found {len(genre_artists)} artists for genre '{genre}'")
            
        except Exception as e:
            logger.error(f"Error getting top artists for genre '{genre}': {e}")
            continue

    logger.info(f"Total top artists found: {len(artist_ids)}")
    return artist_ids


def get_artist_details(artist_id: str) -> Optional[Dict[str, str]]:
    """
    Get detailed information about an artist.
    
    Args:
        artist_id: Spotify artist ID
        
    Returns:
        Dictionary with artist name and cover image URL, or None if error
    """
    try:
        artist_details = sp.artist(artist_id)

        # Extract relevant details with fallbacks
        artist_name = artist_details.get('name', 'Unknown Artist')
        
        # Get the highest quality image available
        cover_image_url = None
        if artist_details.get('images'):
            # Sort images by size (largest first) and take the first one
            images = sorted(artist_details['images'], 
                          key=lambda x: x.get('height', 0) * x.get('width', 0), 
                          reverse=True)
            cover_image_url = images[0]['url']

        result = {
            'name': artist_name,
            'cover_image_url': cover_image_url
        }
        
        logger.debug(f"Retrieved details for artist '{artist_name}'")
        return result
        
    except Exception as e:
        logger.error(f"Error getting artist details for ID '{artist_id}': {e}")
        return None


def get_track_audio_features(track_ids: List[str]) -> Optional[List[Dict]]:
    """
    Get audio features for multiple tracks.
    
    Args:
        track_ids: List of Spotify track IDs
        
    Returns:
        List of audio feature dictionaries or None if error
    """
    try:
        if not track_ids:
            return []
            
        # Spotify API allows max 100 tracks per request
        chunk_size = 100
        all_features = []
        
        for i in range(0, len(track_ids), chunk_size):
            chunk = track_ids[i:i + chunk_size]
            features = sp.audio_features(chunk)
            
            # Filter out None values (tracks without audio features)
            valid_features = [f for f in features if f is not None]
            all_features.extend(valid_features)
            
        logger.info(f"Retrieved audio features for {len(all_features)} tracks")
        return all_features
        
    except Exception as e:
        logger.error(f"Error getting audio features: {e}")
        return None


# Health check function for the API
def check_spotify_connection() -> bool:
    """
    Check if Spotify API connection is working.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        # Simple API call to check connection
        sp.search(q='test', type='track', limit=1)
        logger.info("Spotify API connection successful")
        return True
    except Exception as e:
        logger.error(f"Spotify API connection failed: {e}")
        return False


