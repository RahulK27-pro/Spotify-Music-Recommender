import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
from typing import List, Dict
from collections import Counter
import json
import os
from datetime import datetime
import pathlib

class ArtistSimilarity:
    def __init__(self, sp_client: spotipy.Spotify):
        self.sp = sp_client
        self.cache = {}
        # Use the Spotify folder for cache
        self.data_file = pathlib.Path('Spotify/artist_cache.json')
        self.load_cached_data()
        
    def load_cached_data(self):
        """Load artist data from local storage."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"Loaded {len(self.cache)} artists from cache at {self.data_file}")
            else:
                print(f"No cache file found at {self.data_file}. Creating new cache.")
                self.save_cached_data()  # Create initial cache file
        except json.JSONDecodeError:
            print(f"Error: Cache file {self.data_file} is corrupted. Creating new cache.")
            self.cache = {}
            self.save_cached_data()
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
            self.cache = {}
            self.save_cached_data()
    
    def save_cached_data(self):
        """Save artist data to local storage."""
        try:
            # Create backup of existing file if it exists
            if self.data_file.exists():
                backup_file = self.data_file.parent / f'artist_cache_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                with open(self.data_file, 'r', encoding='utf-8') as src, \
                     open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"Created backup at {backup_file}")

            # Save new data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.cache)} artists to cache at {self.data_file}")
            
            # Verify the save was successful
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                if len(saved_data) == len(self.cache):
                    print("Cache verification successful")
                else:
                    print("Warning: Cache verification failed - data mismatch")
            else:
                print("Error: Cache file was not created")
                
        except Exception as e:
            print(f"Error saving cache: {str(e)}")
            # Try to restore from backup if available
            backup_files = list(self.data_file.parent.glob('artist_cache_backup_*.json'))
            if backup_files:
                latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
                try:
                    with open(latest_backup, 'r', encoding='utf-8') as f:
                        self.cache = json.load(f)
                    print(f"Restored cache from backup {latest_backup}")
                except Exception as backup_error:
                    print(f"Error restoring from backup: {str(backup_error)}")

    def get_artist_features(self, artist_id: str) -> Dict:
        """Get essential features for an artist."""
        if artist_id in self.cache:
            print(f"Retrieved {self.cache[artist_id]['name']} from cache")
            return self.cache[artist_id]
            
        try:
            print(f"Fetching data for artist ID: {artist_id}")
            
            # Get basic artist info
            artist = self.sp.artist(artist_id)
            print(f"Retrieved basic info for: {artist['name']}")
            
            # Get artist's top tracks
            top_tracks = self.sp.artist_top_tracks(artist_id)
            print(f"Retrieved {len(top_tracks['tracks'])} top tracks")
            
            # Initialize features dictionary
            features = {
                'id': artist_id,
                'name': artist['name'],
                'genres': artist['genres'],
                'popularity': artist['popularity'],
                'followers': artist['followers']['total'],
                'top_tracks': [],
                'audio_features': [],
                'last_updated': datetime.now().isoformat(),
                'image_url': artist['images'][0]['url'] if artist['images'] else None
            }
            
            # Process top tracks and their audio features
            track_ids = [track['id'] for track in top_tracks['tracks']]
            if track_ids:
                audio_features = self.sp.audio_features(track_ids)
                features['audio_features'] = audio_features
                print(f"Retrieved audio features for {len(audio_features)} tracks")
                
                for track, audio_feat in zip(top_tracks['tracks'], audio_features):
                    if audio_feat:  # Check if audio features exist
                        features['top_tracks'].append({
                            'name': track['name'],
                            'popularity': track['popularity'],
                            'duration_ms': track['duration_ms'],
                            'explicit': track['explicit'],
                            'danceability': audio_feat['danceability'],
                            'energy': audio_feat['energy'],
                            'valence': audio_feat['valence'],
                            'tempo': audio_feat['tempo']
                        })
            
            # Cache the results
            self.cache[artist_id] = features
            self.save_cached_data()
            
            print(f"Successfully cached data for {features['name']}")
            return features
            
        except Exception as e:
            print(f"Error getting features for artist {artist_id}: {str(e)}")
            return None

    def calculate_similarity(self, artist1_features: Dict, artist2_features: Dict) -> float:
        """Calculate similarity between two artists using multiple features."""
        if not artist1_features or not artist2_features:
            return 0.0
            
        # Calculate genre similarity using Jaccard similarity
        genres1 = set(artist1_features['genres'])
        genres2 = set(artist2_features['genres'])
        genre_similarity = len(genres1 & genres2) / max(len(genres1 | genres2), 1)
        
        # Calculate audio feature similarity
        if artist1_features['top_tracks'] and artist2_features['top_tracks']:
            # Calculate average audio features
            avg_features1 = {
                'danceability': np.mean([t['danceability'] for t in artist1_features['top_tracks']]),
                'energy': np.mean([t['energy'] for t in artist1_features['top_tracks']]),
                'valence': np.mean([t['valence'] for t in artist1_features['top_tracks']]),
                'tempo': np.mean([t['tempo'] for t in artist1_features['top_tracks']])
            }
            
            avg_features2 = {
                'danceability': np.mean([t['danceability'] for t in artist2_features['top_tracks']]),
                'energy': np.mean([t['energy'] for t in artist2_features['top_tracks']]),
                'valence': np.mean([t['valence'] for t in artist2_features['top_tracks']]),
                'tempo': np.mean([t['tempo'] for t in artist2_features['top_tracks']])
            }
            
            # Calculate audio feature similarity using normalized differences
            audio_similarity = 1 - np.mean([
                abs(avg_features1['danceability'] - avg_features2['danceability']),
                abs(avg_features1['energy'] - avg_features2['energy']),
                abs(avg_features1['valence'] - avg_features2['valence']),
                abs(avg_features1['tempo'] - avg_features2['tempo']) / 200  # Normalize tempo difference
            ])
        else:
            audio_similarity = 0.0
        
        # Calculate popularity similarity
        pop_similarity = 1 - abs(artist1_features['popularity'] - artist2_features['popularity']) / 100
        
        # Weighted combination of similarities
        weights = {
            'genre': 0.4,      # Genre similarity
            'audio': 0.4,      # Audio features similarity
            'popularity': 0.2  # Popularity similarity
        }
        
        final_similarity = (
            weights['genre'] * genre_similarity +
            weights['audio'] * audio_similarity +
            weights['popularity'] * pop_similarity
        )
        
        return final_similarity

    def find_similar_artists(self, artist_id: str, limit: int = 3) -> List[Dict]:
        """Find popular artists to display in the similar artists section."""
        try:
            # Get a mix of popular artists from different genres
            popular_artists = []
            
            # Get some popular artists from 2024
            results = self.sp.search(q='year:2024', type='artist', limit=limit)
            if results['artists']['items']:
                popular_artists.extend(results['artists']['items'])
            
            # If we don't have enough, get some more from 2023
            if len(popular_artists) < limit:
                results = self.sp.search(q='year:2023', type='artist', limit=limit)
                if results['artists']['items']:
                    # Add only new artists
                    for artist in results['artists']['items']:
                        if artist not in popular_artists:
                            popular_artists.append(artist)
            
            # If we still don't have enough, get some from different genres
            if len(popular_artists) < limit:
                genres = ['pop', 'rock', 'hip-hop']
                for genre in genres:
                    if len(popular_artists) >= limit:
                        break
                    results = self.sp.search(q=f'genre:{genre}', type='artist', limit=2)
                    if results['artists']['items']:
                        for artist in results['artists']['items']:
                            if artist not in popular_artists:
                                popular_artists.append(artist)
            
            # Return the artists we found, up to the limit
            return popular_artists[:limit]
            
        except Exception as e:
            print(f"Error finding artists: {str(e)}")
            # Return some default popular artists if everything fails
            try:
                results = self.sp.search(q='year:2024', type='artist', limit=limit)
                return results['artists']['items']
            except:
                return [] 