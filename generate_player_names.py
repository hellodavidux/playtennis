#!/usr/bin/env python3
"""
Script to generate a comprehensive list of tennis player names from ATP CSV data
for use in the tennis trivia grid autocomplete functionality.
"""

import pandas as pd
import json
import os
import re
from pathlib import Path

def clean_player_name(name):
    """Clean and validate a player name."""
    if pd.isna(name) or name == 'nan':
        return None
    
    # Convert to string and strip whitespace
    name = str(name).strip()
    
    # Remove extra whitespace
    name = ' '.join(name.split())
    
    # Skip if too short or contains problematic characters
    if len(name) < 2:
        return None
    
    # Skip names that are just initials or numbers
    if re.match(r'^[A-Z\s\.]+$', name) and len(name) <= 5:
        return None
    
    # Skip names that are mostly numbers or special characters
    if re.match(r'^[\d\s\.]+$', name):
        return None
    
    return name

def extract_player_names():
    """Extract all player names from ATP CSV files and create a comprehensive list."""
    
    # Path to the ATP data directory
    atp_dir = Path('tennis_atp-master')
    players_file = atp_dir / 'atp_players.csv'
    
    if not players_file.exists():
        print(f"Error: {players_file} not found!")
        return []
    
    print(f"Reading player data from {players_file}...")
    
    try:
        # Read the players CSV file with low_memory=False to avoid warnings
        df = pd.read_csv(players_file, low_memory=False)
        
        # Combine first and last names
        player_names = []
        for _, row in df.iterrows():
            first_name = clean_player_name(row['name_first'])
            last_name = clean_player_name(row['name_last'])
            
            # Skip if either name is missing
            if not first_name or not last_name:
                continue
                
            # Create full name
            full_name = f"{first_name} {last_name}"
            
            # Clean up the name (remove extra spaces, etc.)
            full_name = ' '.join(full_name.split())
            
            if full_name and len(full_name) > 2:
                player_names.append(full_name)
        
        # Remove duplicates and sort
        unique_names = sorted(list(set(player_names)))
        
        print(f"Extracted {len(unique_names)} unique player names from {len(player_names)} total entries")
        
        return unique_names
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

def create_player_names_json():
    """Create a JSON file with all player names for autocomplete."""
    
    player_names = extract_player_names()
    
    if not player_names:
        print("No player names extracted. Exiting.")
        return
    
    # Create the output data structure
    output_data = {
        "total_players": len(player_names),
        "players": player_names,
        "description": "Comprehensive list of tennis players from ATP data for autocomplete functionality"
    }
    
    # Write to JSON file
    output_file = 'all_tennis_players.json'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"Successfully created {output_file} with {len(player_names)} player names")
        print(f"File size: {os.path.getsize(output_file) / 1024:.1f} KB")
        
        # Show some examples
        print("\nSample player names:")
        for i, name in enumerate(player_names[:15]):
            print(f"  {i+1:2d}. {name}")
        
        if len(player_names) > 15:
            print(f"  ... and {len(player_names) - 15} more players")
        
        # Show some famous players to verify quality
        famous_players = ['Roger Federer', 'Rafael Nadal', 'Novak Djokovic', 'Pete Sampras', 'Andre Agassi']
        print("\nChecking for famous players:")
        for player in famous_players:
            if player in player_names:
                print(f"  ✓ {player}")
            else:
                print(f"  ✗ {player} (not found)")
            
    except Exception as e:
        print(f"Error writing JSON file: {e}")

if __name__ == "__main__":
    create_player_names_json() 