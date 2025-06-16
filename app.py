import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from style import apply_custom_style, create_track_card, create_stats_section, create_search_bar, create_playlist_card
from artist import ArtistSimilarity
from songs import SongSimilarity
import numpy as np

# Apply custom styling
apply_custom_style()

# Spotify API credentials
CLIENT_ID = "fe36360b8b8242389605cf89e3858128"
CLIENT_SECRET = "06d82531d2fd4b0ab49a79d95153f3cb"

# Initialize Spotify client with client credentials
client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Initialize similarity engines
artist_similarity = ArtistSimilarity(sp)
song_similarity = SongSimilarity(sp)

st.title('🎵 Spotify Music Explorer')

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Search Songs", "Search Artists"])

if page == "Search Songs":
    # Create styled search bar
    search_query = create_search_bar()

    if search_query:
        # Search for tracks
        results = sp.search(q=search_query, limit=10, type='track')
        
        if results['tracks']['items']:
            # Create a list of track names for the selectbox
            track_names = [f"{item['name']} - {item['artists'][0]['name']}" for item in results['tracks']['items']]
            
            # Display selectbox with search results
            selected_track = st.selectbox(
                'Select a track to view details:',
                track_names
            )
            
            # Find the selected track's details
            selected_index = track_names.index(selected_track)
            track = results['tracks']['items'][selected_index]
            
            # Create track card with main information
            create_track_card(track)
            
            # Create stats section
            create_stats_section(track)
            
            # Additional track information
            st.markdown("### 📝 Additional Information")
            st.markdown(f"**Release Date:** {track['album']['release_date']}")
            st.markdown(f"**Album Type:** {track['album']['album_type'].title()}")
            
            # Display available markets in a more compact way
            if track['available_markets']:
                st.markdown(f"**Available in {len(track['available_markets'])} markets**")
            
            # Similar Songs section
            st.markdown("### 🎵 Similar Songs")
            similar_songs = song_similarity.find_similar_songs(track['id'])
            
            if similar_songs:
                cols = st.columns(3)
                for idx, similar in enumerate(similar_songs):
                    with cols[idx]:
                        if similar['album']['images']:
                            st.image(similar['album']['images'][0]['url'], width=100)
                        st.markdown(f"**{similar['name']}**")
                        st.markdown(f"*{similar['artists'][0]['name']}*")
                        st.markdown(f"Album: {similar['album']['name']}")
            else:
                st.info("No similar songs found.")
        else:
            st.error("No results found. Try a different search term.")

elif page == "Search Artists":
    st.header("Search Artists")
    
    # Create styled search bar for artists
    artist_query = st.text_input('', placeholder='Enter artist name...', key='artist_search')
    
    if artist_query:
        try:
            # Search for artists
            results = sp.search(q=artist_query, limit=10, type='artist')
            
            if results['artists']['items']:
                # Create a list of artist names for the selectbox
                artist_names = [f"{item['name']} ({item['genres'][0] if item['genres'] else 'No genre'})" 
                              for item in results['artists']['items']]
                
                # Display selectbox with search results
                selected_artist = st.selectbox(
                    'Select an artist to view details:',
                    artist_names
                )
                
                # Find the selected artist's details
                selected_index = artist_names.index(selected_artist)
                artist = results['artists']['items'][selected_index]
                
                # Get artist features
                artist_features = artist_similarity.get_artist_features(artist['id'])
                
                # Display artist information
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if artist['images']:
                        st.image(artist['images'][0]['url'], width=200)
                
                with col2:
                    st.subheader(artist['name'])
                    st.markdown(f"**Popularity:** {artist['popularity']}/100")
                    if artist['genres']:
                        st.markdown("**Genres:** " + ", ".join(artist['genres']))
                    
                    # Display audio features if available
                    if artist_features and artist_features['top_tracks']:
                        avg_features = {
                            'danceability': np.mean([t['danceability'] for t in artist_features['top_tracks']]),
                            'energy': np.mean([t['energy'] for t in artist_features['top_tracks']]),
                            'valence': np.mean([t['valence'] for t in artist_features['top_tracks']]),
                            'tempo': np.mean([t['tempo'] for t in artist_features['top_tracks']])
                        }
                        st.markdown("### Audio Features")
                        st.markdown(f"**Danceability:** {avg_features['danceability']:.2f}")
                        st.markdown(f"**Energy:** {avg_features['energy']:.2f}")
                        st.markdown(f"**Valence:** {avg_features['valence']:.2f}")
                        st.markdown(f"**Tempo:** {avg_features['tempo']:.0f} BPM")
                    
                    # Get artist's top tracks
                    st.markdown("### Top Tracks")
                    top_tracks = sp.artist_top_tracks(artist['id'])
                    
                    if top_tracks['tracks']:
                        for track in top_tracks['tracks'][:5]:  # Show top 5 tracks
                            st.markdown(f"• {track['name']} - {track['album']['name']}")
                    
                    # Get similar artists using our custom algorithm
                    st.markdown("### Similar Artists")
                    similar_artists = artist_similarity.find_similar_artists(artist['id'])
                    
                    if similar_artists:
                        cols = st.columns(3)
                        for idx, similar in enumerate(similar_artists):
                            with cols[idx]:
                                if similar['images']:
                                    st.image(similar['images'][0]['url'], width=100)
                                st.markdown(f"**{similar['name']}**")
                                if similar['genres']:
                                    st.markdown(f"*{similar['genres'][0]}*")
                    else:
                        st.info("No similar artists found.")
            else:
                st.error("No artists found. Try a different search term.")
        except Exception as e:
            st.error(f"Error searching for artists: {str(e)}")
            st.info("Please try again with a different search term.")

