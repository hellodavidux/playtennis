#!/usr/bin/env python3
"""
Process tennis data to create connections for the Tennis Web Six Degrees game.
This script builds a comprehensive player connection network.
"""

import pandas as pd
import json
import glob
import os
from collections import defaultdict, Counter
from datetime import datetime
import re
import numpy as np
import math

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            if math.isnan(obj):
                return None
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(CustomJSONEncoder, self).default(obj)

def load_all_match_data():
    """Load all ATP match data from CSV files."""
    print("Loading match data...")
    
    match_files = glob.glob('tennis_atp-master/atp_matches_*.csv')
    all_matches = []
    
    for file in sorted(match_files):
        year = int(re.search(r'(\d{4})', file).group(1))
        if year >= 1990:  # Focus on modern era for better data quality
            try:
                df = pd.read_csv(file, low_memory=False)
                # Add year column for easier processing
                df['year'] = year
                all_matches.append(df)
                print(f"  Loaded {len(df)} matches from {year}")
            except Exception as e:
                print(f"  Error loading {file}: {e}")
    
    if all_matches:
        combined_df = pd.concat(all_matches, ignore_index=True)
        print(f"Total matches loaded: {len(combined_df)}")
        return combined_df
    else:
        return pd.DataFrame()

def load_player_data():
    """Load player data from JSON and CSV files."""
    print("Loading player data...")
    
    # Load from tennis_players_data.json
    players_data = {}
    try:
        with open('tennis_players_data.json', 'r') as f:
            players_list = json.load(f)
            for player in players_list:
                players_data[player['id']] = {
                    'name': player['name'],
                    'country': player['country'],
                    'hand': player['hand'],
                    'height': player.get('height'),
                    'titles': player.get('titles', 0)
                }
        print(f"  Loaded {len(players_data)} players from JSON")
    except Exception as e:
        print(f"  Error loading players JSON: {e}")
    
    # Load additional data from ATP players CSV
    try:
        atp_players = pd.read_csv('tennis_atp-master/atp_players.csv')
        for _, row in atp_players.iterrows():
            player_id = row['player_id']
            if player_id not in players_data:
                players_data[player_id] = {}
            
            # Add DOB if available
            if pd.notna(row['dob']):
                try:
                    dob_str = str(int(row['dob']))
                    if len(dob_str) == 8:
                        year = int(dob_str[:4])
                        month = int(dob_str[4:6])
                        day = int(dob_str[6:8])
                        players_data[player_id]['birth_date'] = f"{year}-{month:02d}-{day:02d}"
                        players_data[player_id]['birth_year'] = year
                except:
                    pass
            
            # Update other fields if not already present
            if 'name' not in players_data[player_id]:
                players_data[player_id]['name'] = f"{row['name_first']} {row['name_last']}"
            if 'country' not in players_data[player_id]:
                players_data[player_id]['country'] = row['ioc']
            if 'hand' not in players_data[player_id]:
                players_data[player_id]['hand'] = row['hand']
            if 'height' not in players_data[player_id] and pd.notna(row['height']):
                players_data[player_id]['height'] = row['height']
        
        print(f"  Enhanced data for {len(players_data)} players")
    except Exception as e:
        print(f"  Error loading ATP players CSV: {e}")
    
    return players_data

def load_grand_slam_data():
    """Load Grand Slam finals data."""
    print("Loading Grand Slam finals data...")
    
    try:
        with open('grand_slam_finals.json', 'r') as f:
            gs_data = json.load(f)
        print(f"  Loaded {len(gs_data['finals'])} Grand Slam finals")
        return gs_data['finals']
    except Exception as e:
        print(f"  Error loading Grand Slam data: {e}")
        return []

def extract_head_to_head_connections(matches_df, players_data):
    """Extract direct opponent connections from match data."""
    print("Building head-to-head connections...")
    
    h2h_connections = defaultdict(set)
    match_details = defaultdict(list)
    
    for _, match in matches_df.iterrows():
        winner_id = match['winner_id']
        loser_id = match['loser_id']
        
        if pd.notna(winner_id) and pd.notna(loser_id):
            winner_id = int(winner_id)
            loser_id = int(loser_id)
            
            # Add bidirectional connection
            h2h_connections[winner_id].add(loser_id)
            h2h_connections[loser_id].add(winner_id)
            
            # Store match details
            match_info = {
                'opponent_id': loser_id,
                'tournament': match.get('tourney_name', '') or '',
                'year': match.get('year', '') or '',
                'surface': match.get('surface', '') if pd.notna(match.get('surface', '')) else '',
                'round': match.get('round', '') or '',
                'score': match.get('score', '') or '',
                'result': 'W'
            }
            match_details[winner_id].append(match_info)
            
            match_info_loser = match_info.copy()
            match_info_loser['opponent_id'] = winner_id
            match_info_loser['result'] = 'L'
            match_details[loser_id].append(match_info_loser)
    
    print(f"  Found direct connections for {len(h2h_connections)} players")
    return dict(h2h_connections), dict(match_details)

def extract_attribute_connections(players_data):
    """Extract connections based on player attributes (optimized for memory)."""
    print("Building attribute-based connections...")
    
    # Only work with players that have sufficient data
    valid_players = {}
    for player_id, data in players_data.items():
        if isinstance(data, dict) and 'name' in data:
            valid_players[player_id] = data
    
    print(f"  Working with {len(valid_players)} valid players")
    
    # Group players by attributes for efficient lookup
    country_groups = defaultdict(list)
    hand_groups = defaultdict(list)
    height_groups = defaultdict(list)
    year_groups = defaultdict(list)
    
    for player_id, data in valid_players.items():
        if data.get('country'):
            country_groups[data['country']].append(player_id)
        if data.get('hand'):
            hand_groups[data['hand']].append(player_id)
        if data.get('height'):
            # Group by 5cm ranges for height
            height_range = int(data['height'] // 5) * 5
            height_groups[height_range].append(player_id)
        if data.get('birth_year'):
            year_groups[data['birth_year']].append(player_id)
    
    attribute_connections = defaultdict(lambda: defaultdict(list))
    
    # Build connections within groups
    for country, players in country_groups.items():
        if len(players) > 1:
            for player in players:
                others = [p for p in players if p != player]
                attribute_connections[player]['same_country'] = others
    
    for hand, players in hand_groups.items():
        if len(players) > 1:
            for player in players:
                others = [p for p in players if p != player]
                attribute_connections[player]['same_hand'] = others
    
    for height_range, players in height_groups.items():
        if len(players) > 1:
            for player in players:
                others = [p for p in players if p != player]
                attribute_connections[player]['similar_height'] = others
    
    for year, players in year_groups.items():
        if len(players) > 1:
            for player in players:
                others = [p for p in players if p != player]
                attribute_connections[player]['same_birth_year'] = others
    
    print(f"  Built attribute connections for {len(attribute_connections)} players")
    return dict(attribute_connections)

def extract_tournament_connections(matches_df, gs_finals):
    """Extract connections based on tournament participation."""
    print("Building tournament connections...")
    
    tournament_connections = defaultdict(lambda: defaultdict(set))
    
    # From regular matches - same tournament participation
    tournament_players = defaultdict(set)
    for _, match in matches_df.iterrows():
        tournament = match.get('tourney_name', '')
        year = match.get('year', '')
        if tournament and year:
            tournament_key = f"{tournament}_{year}"
            if pd.notna(match['winner_id']):
                tournament_players[tournament_key].add(int(match['winner_id']))
            if pd.notna(match['loser_id']):
                tournament_players[tournament_key].add(int(match['loser_id']))
    
    # Create connections for players who played same tournaments
    for tournament_key, players in tournament_players.items():
        players_list = list(players)
        for i, player1 in enumerate(players_list):
            for player2 in players_list[i+1:]:
                tournament_connections[player1]['same_tournament'].add(player2)
                tournament_connections[player2]['same_tournament'].add(player1)
    
    # Grand Slam finals connections
    gs_finalists = defaultdict(set)
    for final in gs_finals:
        tournament = final.get('tournament', '')
        if tournament:
            winner_name = final.get('winner', {}).get('name', '')
            loser_name = final.get('loser', {}).get('name', '')
            
            if winner_name and loser_name:
                gs_finalists[tournament].add(winner_name)
                gs_finalists[tournament].add(loser_name)
    
    # Create GS finals connections by player names (we'll need to map to IDs later)
    for tournament, finalists in gs_finalists.items():
        finalists_list = list(finalists)
        for i, player1 in enumerate(finalists_list):
            for player2 in finalists_list[i+1:]:
                # Store as names for now, will convert to IDs in final processing
                pass
    
    # Convert sets to lists
    for player_id in tournament_connections:
        for connection_type in tournament_connections[player_id]:
            tournament_connections[player_id][connection_type] = list(tournament_connections[player_id][connection_type])
    
    print(f"  Built tournament connections for {len(tournament_connections)} players")
    return dict(tournament_connections)

def get_popular_players(players_data, h2h_connections, min_connections=10):
    """Get list of players with sufficient connections for the game."""
    popular_players = []
    
    for player_id, data in players_data.items():
        if (isinstance(data, dict) and 
            'name' in data and 
            player_id in h2h_connections and
            len(h2h_connections[player_id]) >= min_connections):
            
            player_info = {
                'id': player_id,
                'name': data['name'],
                'country': data.get('country', ''),
                'hand': data.get('hand', ''),
                'height': data.get('height'),
                'birth_year': data.get('birth_year'),
                'titles': data.get('titles', 0),
                'connections': len(h2h_connections[player_id])
            }
            popular_players.append(player_info)
    
    # Sort by number of connections (most connected first)
    popular_players.sort(key=lambda x: x['connections'], reverse=True)
    
    print(f"Found {len(popular_players)} players with {min_connections}+ connections")
    return popular_players

def build_connection_graph(h2h_connections, attribute_connections, tournament_connections):
    """Build the final connection graph combining all connection types."""
    print("Building final connection graph...")
    
    connection_graph = {}
    
    all_player_ids = set()
    all_player_ids.update(h2h_connections.keys())
    all_player_ids.update(attribute_connections.keys())
    all_player_ids.update(tournament_connections.keys())
    
    for player_id in all_player_ids:
        connections = {
            'direct_opponents': list(h2h_connections.get(player_id, [])),
            'same_country': attribute_connections.get(player_id, {}).get('same_country', []),
            'same_hand': attribute_connections.get(player_id, {}).get('same_hand', []),
            'similar_height': attribute_connections.get(player_id, {}).get('similar_height', []),
            'same_birth_year': attribute_connections.get(player_id, {}).get('same_birth_year', []),
            'same_tournament': tournament_connections.get(player_id, {}).get('same_tournament', [])
        }
        
        # Calculate total unique connections
        all_connections = set()
        for connection_type, connected_players in connections.items():
            all_connections.update(connected_players)
        
        connections['total_connections'] = len(all_connections)
        connection_graph[player_id] = connections
    
    print(f"Built connection graph for {len(connection_graph)} players")
    return connection_graph

def main():
    """Main function to process all tennis data."""
    print("Starting Tennis Web data processing...")
    
    # Load all data
    matches_df = load_all_match_data()
    players_data = load_player_data()
    gs_finals = load_grand_slam_data()
    
    if matches_df.empty:
        print("Error: No match data loaded. Cannot continue.")
        return
    
    # Extract connections
    h2h_connections, match_details = extract_head_to_head_connections(matches_df, players_data)
    attribute_connections = extract_attribute_connections(players_data)
    tournament_connections = extract_tournament_connections(matches_df, gs_finals)
    
    # Build final graph
    connection_graph = build_connection_graph(h2h_connections, attribute_connections, tournament_connections)
    
    # Get popular players for the game
    popular_players = get_popular_players(players_data, h2h_connections, min_connections=8)
    
    # Focus on top players only to reduce data size
    top_players = popular_players[:800]  # Top 800 most connected players
    top_player_ids = {player['id'] for player in top_players}
    
    # Filter connections to only include top players
    filtered_connections = {}
    for player_id in top_player_ids:
        if player_id in connection_graph:
            filtered_connections[str(player_id)] = connection_graph[player_id]
    
    # Filter player details and match details for top players only
    filtered_player_details = {}
    filtered_match_details = {}
    for player_id in top_player_ids:
        if player_id in players_data and isinstance(players_data[player_id], dict):
            filtered_player_details[str(player_id)] = players_data[player_id]
        if player_id in match_details:
            # Limit match details to avoid huge data
            filtered_match_details[str(player_id)] = match_details[player_id][:50]  # Max 50 matches per player
    
    # Prepare final data structure
    tennis_web_data = {
        'players': top_players,
        'connections': filtered_connections,
        'player_details': filtered_player_details,
        'match_details': filtered_match_details,
        'metadata': {
            'total_players': len(top_players),
            'total_matches': len(matches_df),
            'data_range': f"1990-{datetime.now().year}",
            'generated_on': datetime.now().isoformat(),
            'connection_types': [
                'direct_opponents',
                'same_country', 
                'same_hand',
                'similar_height',
                'same_birth_year',
                'same_tournament'
            ]
        }
    }
    
    # Save the data
    output_file = 'tennis_web_connections.json'
    with open(output_file, 'w') as f:
        json.dump(tennis_web_data, f, indent=2, cls=CustomJSONEncoder)
    
    print(f"\nData processing complete!")
    print(f"Saved {len(tennis_web_data['players'])} players to {output_file}")
    print(f"Total connections in graph: {len(tennis_web_data['connections'])}")
    
    # Print some interesting stats
    if popular_players:
        most_connected = popular_players[0]
        print(f"Most connected player: {most_connected['name']} ({most_connected['connections']} direct opponents)")
        
        # Sample connection types for top player
        top_player_id = str(most_connected['id'])
        if top_player_id in tennis_web_data['connections']:
            conns = tennis_web_data['connections'][top_player_id]
            print(f"  - Direct opponents: {len(conns.get('direct_opponents', []))}")
            print(f"  - Same country: {len(conns.get('same_country', []))}")
            print(f"  - Same hand: {len(conns.get('same_hand', []))}")
            print(f"  - Similar height: {len(conns.get('similar_height', []))}")
            print(f"  - Same birth year: {len(conns.get('same_birth_year', []))}")
            print(f"  - Same tournaments: {len(conns.get('same_tournament', []))}")

if __name__ == "__main__":
    main()