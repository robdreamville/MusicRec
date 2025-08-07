# JbTunez - Spotify API Configuration Template
# Copy this file to 'spotify.py' and fill in your actual credentials
# 
# Get your credentials from: https://developer.spotify.com/dashboard/
# 
# IMPORTANT: Never commit spotify.py to version control!
# This file should remain in .gitignore for security.

# Your Spotify App Credentials
client_id = "your_spotify_client_id_here"
client_secret = "your_spotify_client_secret_here"

# Redirect URI for OAuth flow
# For local development, use: http://localhost:5000/callback
# For production, use your domain: https://yourdomain.com/callback
redirect_url = "http://localhost:5000/callback"

# OAuth Scopes (what permissions your app needs)
# Current scopes for JbTunez:
# - user-library-read: Access user's saved tracks
# - playlist-read-private: Access user's private playlists
scopes = "user-library-read playlist-read-private"

# Optional: Additional configuration
# These can be used for advanced features

# Cache settings for token storage
cache_path = ".spotify_cache"

# API request timeout (seconds)
request_timeout = 10

# Market/Country code for recommendations (ISO 3166-1 alpha-2)
market = "US"

# Example usage:
# After filling in your credentials, import this file in Spotipy_song_rec.py:
# 
# import spotify
# 
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id=spotify.client_id,
#     client_secret=spotify.client_secret,
#     redirect_uri=spotify.redirect_url,
#     scope=spotify.scopes
# ))

"""
Setup Instructions:

1. Go to https://developer.spotify.com/dashboard/
2. Click "Create App"
3. Fill in app details:
   - App Name: JbTunez
   - App Description: AI-powered music discovery app
   - Website: http://localhost:5000 (for development)
   - Redirect URI: http://localhost:5000/callback
4. Copy Client ID and Client Secret from the app settings
5. Paste them in the variables above
6. Save this file as 'spotify.py' (remove '_template' from filename)
7. Keep spotify.py secure and never commit it to version control!

For production deployment:
- Use environment variables instead of this file
- Update redirect_url to your production domain
- Consider using a proper secrets management system
"""