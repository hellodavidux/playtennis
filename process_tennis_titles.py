#!/usr/bin/env python3
"""
Process ATP match data to calculate tournament titles for tennis players from 1990 onwards.
Creates a JSON file with player data including ATP titles for the tennis tier list game.
"""

import pandas as pd
import json
import os
from collections import defaultdict

def get_atp_titles(data_dir="tennis_atp-master"):
    """
    Process ATP match data from 1990 onwards to count tournament titles per player.
    
    Returns:
        dict: Player data with titles count, sorted by titles descending
    """
    
    # Dictionary to store title counts per player
    player_titles = defaultdict(int)
    player_info = {}  # Store player details
    
    # Get list of all available ATP match files
    match_files = []
    for year in range(1968, 2025):  # From first Open Era year to 2024
        filename = f"atp_matches_{year}.csv"
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            match_files.append(filepath)
    
    print(f"Processing {len(match_files)} files...")
    
    # Process each year's matches
    for filepath in match_files:
        year = filepath.split('_')[-1].split('.')[0]
        print(f"Processing {year}...")
        
        try:
            # Read the CSV file
            df = pd.read_csv(filepath)
            
            # Filter for final matches only (tournament winners)
            finals = df[df['round'] == 'F'].copy()
            
            # Filter for main tour events (excluding Challengers, ITFs, etc.)
            # Keep Grand Slams (G), Masters (M), ATP Tour (A), and Finals (F)
            main_tour = finals[finals['tourney_level'].isin(['G', 'M', 'A', 'F'])]
            
            # Count titles for each player
            for _, match in main_tour.iterrows():
                winner_id = match['winner_id']
                winner_name = match['winner_name']
                
                # Skip if missing essential data
                if pd.isna(winner_id) or pd.isna(winner_name):
                    continue
                    
                player_titles[winner_id] += 1
                
                # Store player info (will overwrite with most recent info)
                player_info[winner_id] = {
                    'name': winner_name,
                    'hand': match.get('winner_hand', 'U'),
                    'country': match.get('winner_ioc', ''),
                    'height': match.get('winner_ht', ''),
                }
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            continue
    
    # Create final player data structure
    players_data = []
    for player_id, titles in player_titles.items():
        if player_id in player_info and titles > 0:  # Only include players with titles
            player_data = {
                'id': int(player_id),
                'name': player_info[player_id]['name'],
                'titles': titles,
                'hand': player_info[player_id]['hand'],
                'country': player_info[player_id]['country'],
                'height': player_info[player_id]['height']
            }
            players_data.append(player_data)
    
    # Sort by titles (descending)
    players_data.sort(key=lambda x: x['titles'], reverse=True)
    
    print(f"\nProcessed {len(players_data)} players with ATP titles")
    print(f"Top 10 title holders:")
    for i, player in enumerate(players_data[:10]):
        print(f"{i+1}. {player['name']}: {player['titles']} titles")
    
    return players_data

def save_tennis_data():
    """
    Process ATP data from all available years and save to JSON file for the tennis tier list game.
    """
    print("Processing ATP tournament data from all available years...")
    players_data = get_atp_titles()
    
    # Filter to get a good selection for the game
    # Take top performers but also include some variety
    game_players = []
    
    # Take top 50 title holders
    top_players = players_data[:50]
    
    # Also include some players with fewer titles for variety (5-20 titles range)
    variety_players = [p for p in players_data if 5 <= p['titles'] <= 20][:30]
    
    # Combine and deduplicate
    all_game_players = top_players + variety_players
    seen_ids = set()
    for player in all_game_players:
        if player['id'] not in seen_ids:
            game_players.append(player)
            seen_ids.add(player['id'])
    
    # Limit to reasonable number for game
    game_players = game_players[:80]
    
    # Save to JSON file
    output_file = "tennis_players_data.json"
    with open(output_file, 'w') as f:
        json.dump(game_players, f, indent=2)
    
    print(f"\nSaved {len(game_players)} players to {output_file}")
    print("Data ready for tennis tier list game!")

if __name__ == "__main__":
    save_tennis_data()