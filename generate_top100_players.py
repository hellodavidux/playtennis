#!/usr/bin/env python3
"""
Script to generate a list of tennis players who have been in the ATP top 100
for use in the tennis trivia grid autocomplete functionality.
"""

import pandas as pd
import json
import os
from pathlib import Path

def extract_top100_players():
    """Extract players who have been in the ATP top 100 rankings."""
    
    # Path to the ATP data directory
    atp_dir = Path('tennis_atp-master')
    players_file = atp_dir / 'atp_players.csv'
    
    if not players_file.exists():
        print(f"Error: {players_file} not found!")
        return []
    
    print(f"Reading player data from {players_file}...")
    
    try:
        # Read the players CSV file
        df_players = pd.read_csv(players_file, low_memory=False)
        print(f"Loaded {len(df_players)} players from CSV")
        
        # Create a set to store unique player IDs who have been in top 100
        top100_player_ids = set()
        
        # Check all ranking files for top 100 players
        ranking_files = [
            'atp_rankings_70s.csv',
            'atp_rankings_80s.csv', 
            'atp_rankings_90s.csv',
            'atp_rankings_00s.csv',
            'atp_rankings_10s.csv',
            'atp_rankings_20s.csv',
            'atp_rankings_current.csv'
        ]
        
        for ranking_file in ranking_files:
            file_path = atp_dir / ranking_file
            if file_path.exists():
                print(f"Processing {ranking_file}...")
                try:
                    df_rankings = pd.read_csv(file_path, low_memory=False)
                    
                    # Filter for players ranked in top 100
                    top100_rankings = df_rankings[df_rankings['rank'] <= 100]
                    
                    # Add player IDs to our set
                    if 'player_id' in top100_rankings.columns:
                        top100_player_ids.update(top100_rankings['player_id'].unique())
                    elif 'player' in top100_rankings.columns:
                        # Some files might use 'player' instead of 'player_id'
                        top100_player_ids.update(top100_rankings['player'].unique())
                        
                    print(f"  Found {len(top100_rankings['player_id'].unique()) if 'player_id' in top100_rankings.columns else len(top100_rankings['player'].unique())} unique players in top 100")
                    
                except Exception as e:
                    print(f"  Error processing {ranking_file}: {e}")
            else:
                print(f"  {ranking_file} not found, skipping...")
        
        print(f"\nTotal unique players who have been in top 100: {len(top100_player_ids)}")
        
        # Now get the player names for these IDs
        player_names = []
        for _, row in df_players.iterrows():
            if row['player_id'] in top100_player_ids:
                first_name = str(row['name_first']).strip()
                last_name = str(row['name_last']).strip()
                
                # Skip if either name is missing or contains NaN
                if pd.isna(first_name) or pd.isna(last_name) or first_name == 'nan' or last_name == 'nan':
                    continue
                    
                # Create full name
                full_name = f"{first_name} {last_name}"
                
                # Clean up the name (remove extra spaces, etc.)
                full_name = ' '.join(full_name.split())
                
                if full_name and len(full_name) > 2:
                    player_names.append(full_name)
        
        # Remove duplicates and sort
        unique_names = sorted(list(set(player_names)))
        
        print(f"Extracted {len(unique_names)} unique player names from top 100 players")
        
        return unique_names
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def create_top100_players_json():
    """Create a JSON file with top 100 players for autocomplete."""
    
    player_names = extract_top100_players()
    
    if not player_names:
        print("No player names extracted. Exiting.")
        return
    
    # Create the output data structure
    output_data = {
        "total_players": len(player_names),
        "players": player_names,
        "description": "List of tennis players who have been in ATP top 100 rankings for autocomplete functionality"
    }
    
    # Write to JSON file
    output_file = 'top100_tennis_players.json'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created {output_file} with {len(player_names)} player names")
        print(f"File size: {os.path.getsize(output_file) / 1024:.1f} KB")
        
        # Show some examples
        print("\nSample top 100 players:")
        for i, name in enumerate(player_names[:15]):
            print(f"  {i+1:2d}. {name}")
        
        if len(player_names) > 15:
            print(f"  ... and {len(player_names) - 15} more players")
        
        # Show some famous players to verify quality
        famous_players = ['Roger Federer', 'Rafael Nadal', 'Novak Djokovic', 'Pete Sampras', 'Andre Agassi', 'Juan Carlos Ferrero']
        print("\nChecking for famous players:")
        for player in famous_players:
            if player in player_names:
                print(f"  ✓ {player}")
            else:
                print(f"  ✗ {player} (not found)")
            
    except Exception as e:
        print(f"Error writing JSON file: {e}")

if __name__ == "__main__":
    create_top100_players_json() 