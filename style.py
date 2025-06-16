import streamlit as st

def apply_custom_style():
    """Apply custom CSS styling to the app"""
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        
        /* Title styling */
        .stTitle {
            color: #1DB954;
            font-size: 3rem !important;
            font-weight: 700 !important;
            text-align: center;
            margin-bottom: 2rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            background-color: #282828;
            color: #FFFFFF;
            border: 2px solid #1DB954;
            border-radius: 25px;
            padding: 10px 20px;
            font-size: 1rem;
        }
        
        /* Selectbox styling */
        .stSelectbox > div > div {
            background-color: #282828;
            color: #FFFFFF;
            border: 2px solid #1DB954;
            border-radius: 25px;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #1DB954;
            color: #FFFFFF;
            border: none;
            border-radius: 25px;
            padding: 10px 20px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #1ed760;
            transform: scale(1.05);
        }
        
        /* Card styling */
        .card {
            background-color: #282828;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        /* Link styling */
        a {
            color: #1DB954;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        a:hover {
            color: #1ed760;
        }
        
        /* Track info styling */
        .track-info {
            background-color: #282828;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
        }
        
        /* Progress bar styling */
        .stProgress > div > div {
            background-color: #1DB954;
        }
        
        /* Divider styling */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, #1DB954, transparent);
            margin: 20px 0;
        }
        
        /* Stats styling */
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            padding: 15px;
            background-color: #282828;
            border-radius: 15px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-value {
            color: #1DB954;
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        .stat-label {
            color: #B3B3B3;
            font-size: 0.9rem;
        }
        
        /* Playlist card styling */
        .playlist-card {
            background-color: #282828;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            cursor: pointer;
        }
        
        .playlist-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.2);
        }
        
        .playlist-image {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .playlist-name {
            color: #FFFFFF;
            font-size: 1.1rem;
            font-weight: 600;
            margin: 5px 0;
        }
        
        .playlist-info {
            color: #B3B3B3;
            font-size: 0.9rem;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #282828;
            border-radius: 25px;
            color: #FFFFFF;
            font-size: 1rem;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1DB954;
        }
        </style>
    """, unsafe_allow_html=True)

def create_track_card(track):
    """Create a styled track card with track information"""
    st.markdown(f"""
        <div class="card">
            <div style="display: flex; align-items: center; gap: 20px;">
                <img src="{track['album']['images'][0]['url']}" width="150" style="border-radius: 10px;">
                <div>
                    <h2 style="color: #FFFFFF; margin: 0;">{track['name']}</h2>
                    <p style="color: #B3B3B3; margin: 5px 0;">{track['artists'][0]['name']}</p>
                    <p style="color: #B3B3B3; margin: 5px 0;">{track['album']['name']}</p>
                    <a href="{track['external_urls']['spotify']}" target="_blank" style="color: #1DB954; text-decoration: none;">
                        Open in Spotify
                    </a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_playlist_card(playlist):
    """Create a styled playlist card"""
    # Get the first image from the playlist
    image_url = playlist['images'][0]['url'] if playlist['images'] else "https://community.spotify.com/t5/image/serverpage/image-id/25294i2836BD1C1A31BDF2/image-size/medium"
    
    st.markdown(f"""
        <div class="playlist-card">
            <img src="{image_url}" class="playlist-image">
            <div class="playlist-name">{playlist['name']}</div>
            <div class="playlist-info">
                {playlist['tracks']['total']} tracks • {playlist['owner']['display_name']}
            </div>
            <a href="{playlist['external_urls']['spotify']}" target="_blank" style="color: #1DB954; text-decoration: none;">
                Open in Spotify
            </a>
        </div>
    """, unsafe_allow_html=True)

def create_stats_section(track):
    """Create a styled stats section for track information"""
    duration_min = int(track['duration_ms']/1000//60)
    duration_sec = int(track['duration_ms']/1000%60)
    
    st.markdown(f"""
        <div class="stats">
            <div class="stat-item">
                <div class="stat-value">{track['popularity']}</div>
                <div class="stat-label">Popularity</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{duration_min}:{duration_sec:02d}</div>
                <div class="stat-label">Duration</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">{len(track['available_markets'])}</div>
                <div class="stat-label">Markets</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def create_search_bar():
    """Create a styled search bar"""
    st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <h2 style="color: #FFFFFF; margin-bottom: 20px;">Search for your favorite music</h2>
        </div>
    """, unsafe_allow_html=True)
    return st.text_input('', placeholder='Enter song name, artist, or album...', key='search_input') 