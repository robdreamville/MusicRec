import spotipy
import spotify
from spotipy.oauth2 import SpotifyOAuth


scope = "user-library-read playlist-read-private "
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=spotify.client_id,
                                               client_secret=spotify.client_secret, redirect_uri=spotify.redirect_url,
                                               scope=scope))


def get_track_id(song_name, artist_name):
    # Search for the track using the provided song name and artist name
    query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)

    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        return track_id
    else:
        return None


def get_artist_id(artist_name):
    # Search for the artist using the provided artist name
    query = f"artist:{artist_name}"
    results = sp.search(q=query, type='artist', limit=1)

    if results['artists']['items']:
        artist_id = results['artists']['items'][0]['id']
        return artist_id
    else:
        return None


def get_album_id(album_name, artist_name):
    # Search for the album using the provided album name and artist name
    query = f"album:{album_name} artist:{artist_name}"
    results = sp.search(q=query, type='album', limit=1)

    if results['albums']['items']:
        album_id = results['albums']['items'][0]['id']
        return album_id
    else:
        return None


def get_recommendations(seed_genres, seed_artists, seed_tracks, attributes):

    try:

        new_seed_genres = []
        new_seed_artists  = []
        new_seed_tracks = []
        # Combine all seed lists into one
        all_seeds = seed_genres + seed_artists + seed_tracks

        # Check the total number of seeds and truncate if necessary
        total_seeds = len(all_seeds)
        max_total_seeds = 5

        # If the total number of seeds exceeds the limit, adjust distribution
        if total_seeds > max_total_seeds:
            print(f"Warning: Adjusting seed distribution to {max_total_seeds} items.")

            # Distribute seeds among categories until the limit is reached
            while total_seeds > max_total_seeds and seed_genres:
                if total_seeds > max_total_seeds:
                    new_seed_genres.append(seed_genres.pop())
                    total_seeds -= 1

                if total_seeds > max_total_seeds and seed_artists:
                    new_seed_artists.append(seed_artists.pop())
                    total_seeds -= 1

                if total_seeds > max_total_seeds and seed_tracks:
                    new_seed_tracks.append(seed_tracks.pop())
                    total_seeds -= 1

            # Merge the mood scores with additional attributes
            recommendation_attributes = {**attributes, 'seed_genres': new_seed_genres, 'seed_artists': new_seed_artists,
                                                 'seed_tracks': new_seed_tracks}

            # Call sp.recommendations with the merged attributes
            recommendations = sp.recommendations(**recommendation_attributes)

            return recommendations


        # Merge the mood scores with additional attributes
        recommendation_attributes = {**attributes, 'seed_genres': seed_genres, 'seed_artists': seed_artists, 'seed_tracks': seed_tracks}

        # Call sp.recommendations with the merged attributes
        recommendations = sp.recommendations(**recommendation_attributes)

        return recommendations

    except spotipy.SpotifyException as e:
        # Print the exception details for debugging
        print("Exception:", e)
        raise


def get_top_artist_for_genres(*genres):

    list_of_artists = []
    for genre in genres:
        #print(f"\nTop Artists for {genre}:")
        results = sp.search(q=f'genre:{genre}', type='artist', limit=10)

        for i, artist in enumerate(results['artists']['items']):
            #print(f"{i + 1}. {artist['name']} (ID: {artist['id']})")
            list_of_artists.append(artist['id'])

    return list_of_artists

def get_artist_details(artist_id):
    artist_details = sp.artist(artist_id)

    # Extract relevant details
    artist_name = artist_details['name']
    cover_image_url = artist_details['images'][0]['url'] if artist_details['images'] else None

    return {
        'name': artist_name,
        'cover_image_url': cover_image_url
    }


