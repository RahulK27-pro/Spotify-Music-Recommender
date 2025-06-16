import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
from typing import List, Dict
import json
import os
from datetime import datetime
import pathlib

class SongSimilarity:
    def __init__(self, sp_client: spotipy.Spotify):
        self.sp = sp_client
        self.cache = {}
        # Use the Spotify folder for cache
        self.data_file = pathlib.Path('Spotify/song_cache.json')
        self.load_cached_data()
        
    def load_cached_data(self):
        """Load song data from local storage."""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                print(f"Loaded {len(self.cache)} songs from cache at {self.data_file}")
            else:
                print(f"No cache file found at {self.data_file}. Creating new cache.")
                self.save_cached_data()
        except json.JSONDecodeError:
            print(f"Error: Cache file {self.data_file} is corrupted. Creating new cache.")
            self.cache = {}
            self.save_cached_data()
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
            self.cache = {}
            self.save_cached_data()
    
    def save_cached_data(self):
        """Save song data to local storage."""
        try:
            # Create backup of existing file if it exists
            if self.data_file.exists():
                backup_file = self.data_file.parent / f'song_cache_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
                with open(self.data_file, 'r', encoding='utf-8') as src, \
                     open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
                print(f"Created backup at {backup_file}")

            # Save new data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.cache)} songs to cache at {self.data_file}")
            
        except Exception as e:
            print(f"Error saving cache: {str(e)}")
            # Try to restore from backup if available
            backup_files = list(self.data_file.parent.glob('song_cache_backup_*.json'))
            if backup_files:
                latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
                try:
                    with open(latest_backup, 'r', encoding='utf-8') as f:
                        self.cache = json.load(f)
                    print(f"Restored cache from backup {latest_backup}")
                except Exception as backup_error:
                    print(f"Error restoring from backup: {str(backup_error)}")

    def get_song_features(self, track_id: str) -> Dict:
        """Get essential features for a song."""
        if track_id in self.cache:
            print(f"Retrieved song from cache")
            return self.cache[track_id]
            
        try:
            # Get track info
            track = self.sp.track(track_id)
            
            # Get audio features
            audio_features = self.sp.audio_features(track_id)[0]
            
            # Combine track info and audio features
            features = {
                'id': track_id,
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms'],
                'explicit': track['explicit'],
                'danceability': audio_features['danceability'],
                'energy': audio_features['energy'],
                'valence': audio_features['valence'],
                'tempo': audio_features['tempo'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the results
            self.cache[track_id] = features
            self.save_cached_data()
            
            return features
            
        except Exception as e:
            print(f"Error getting features for song {track_id}: {str(e)}")
            return None

    def find_similar_songs(self, track_id: str, limit: int = 3) -> List[Dict]:
        """Find popular songs to display in the similar songs section."""
        try:
            # Get a mix of popular songs from different genres and years
            popular_songs = []
            
            # Get some popular songs from 2024
            results = self.sp.search(q='year:2024', type='track', limit=limit)
            if results['tracks']['items']:
                popular_songs.extend(results['tracks']['items'])
            
            # If we don't have enough, get some more from 2023
            if len(popular_songs) < limit:
                results = self.sp.search(q='year:2023', type='track', limit=limit)
                if results['tracks']['items']:
                    # Add only new songs
                    for song in results['tracks']['items']:
                        if song not in popular_songs:
                            popular_songs.append(song)
            
            # If we still don't have enough, get some from different genres
            if len(popular_songs) < limit:
                genres = ['pop', 'rock', 'hip-hop']
                for genre in genres:
                    if len(popular_songs) >= limit:
                        break
                    results = self.sp.search(q=f'genre:{genre}', type='track', limit=2)
                    if results['tracks']['items']:
                        for song in results['tracks']['items']:
                            if song not in popular_songs:
                                popular_songs.append(song)
            
            # Return the songs we found, up to the limit
            return popular_songs[:limit]
            
        except Exception as e:
            print(f"Error finding songs: {str(e)}")
            # Return some default popular songs if everything fails
            try:
                results = self.sp.search(q='year:2024', type='track', limit=limit)
                return results['tracks']['items']
            except:
                return [] 