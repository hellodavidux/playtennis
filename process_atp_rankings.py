#!/usr/bin/env python3
"""
Process ATP ranking data to extract yearly highest rankings for top 10 players.
"""
import pandas as pd
import json
import os
from collections import defaultdict
from datetime import datetime

def load_player_data():
    """Load player information mapping."""
    players_file = 'tennis_atp-master/atp_players.csv'
    players_df = pd.read_csv(players_file)
    
    player_map = {}
    for _, row in players_df.iterrows():
        player_id = str(row['player_id'])
        player_map[player_id] = {
            'name': f"{row['name_first']} {row['name_last']}",
            'first_name': row['name_first'],
            'last_name': row['name_last'],
            'country': row['ioc'] if pd.notna(row['ioc']) else 'Unknown',
            'hand': row['hand'] if pd.notna(row['hand']) else 'Unknown',
            'dob': row['dob'] if pd.notna(row['dob']) else None
        }
    
    print(f"Loaded {len(player_map)} player records")
    return player_map

def process_ranking_files():
    """Process all ATP ranking files to find yearly highest rankings."""
    ranking_files = [
        'tennis_atp-master/atp_rankings_70s.csv',
        'tennis_atp-master/atp_rankings_80s.csv',
        'tennis_atp-master/atp_rankings_90s.csv',
        'tennis_atp-master/atp_rankings_00s.csv',
        'tennis_atp-master/atp_rankings_10s.csv',
        'tennis_atp-master/atp_rankings_20s.csv',
        'tennis_atp-master/atp_rankings_current.csv'
    ]
    
    # Dictionary to store player rankings: player_id -> year -> best_rank
    player_year_rankings = defaultdict(lambda: defaultdict(lambda: float('inf')))
    top10_players = set()
    
    for file_path in ranking_files:
        if not os.path.exists(file_path):
            print(f"Warning: {file_path} not found")
            continue
            
        print(f"Processing {file_path}...")
        
        try:
            # Read file in chunks due to large size
            chunk_size = 50000
            for chunk in pd.read_csv(file_path, chunksize=chunk_size):
                for _, row in chunk.iterrows():
                    try:
                        # Handle both string and float date formats
                        ranking_date_raw = row['ranking_date']
                        if pd.isna(ranking_date_raw):
                            continue
                            
                        # Convert to string and remove decimal if present
                        ranking_date = str(ranking_date_raw).replace('.0', '')
                        
                        if len(ranking_date) >= 8:
                            year = int(ranking_date[:4])
                            month = int(ranking_date[4:6])
                            day = int(ranking_date[6:8])
                        else:
                            continue
                            
                        # Handle player ID - convert float to int to string to avoid .0 suffix
                        player_id_raw = row['player']
                        if pd.isna(player_id_raw):
                            continue
                        player_id = str(int(player_id_raw))
                        
                        # Handle rank
                        rank_raw = row['rank']
                        if pd.isna(rank_raw):
                            continue
                        rank = int(rank_raw)
                        
                        # Track players who have been in top 10
                        if rank <= 10:
                            top10_players.add(player_id)
                        
                        # Update best rank for this year (lower number = better rank)
                        if rank < player_year_rankings[player_id][year]:
                            player_year_rankings[player_id][year] = rank
                            
                    except (ValueError, KeyError) as e:
                        # Skip malformed rows
                        continue
                        
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue
    
    print(f"Found {len(top10_players)} players who reached top 10")
    return player_year_rankings, top10_players

def create_ranking_timeline_data():
    """Create the final ranking timeline data."""
    player_map = load_player_data()
    player_rankings, top10_players = process_ranking_files()
    
    # Filter for only top 10 players and create timeline
    final_data = {}
    
    for player_id in top10_players:
        if player_id not in player_map:
            continue
            
        player_data = player_map[player_id]
        player_timeline = dict(player_rankings[player_id])
        
        # Only include players with at least 3 years of data
        if len(player_timeline) < 3:
            continue
            
        # Convert inf values back to None (no ranking that year)
        cleaned_timeline = {}
        for year, rank in player_timeline.items():
            if rank != float('inf'):
                cleaned_timeline[year] = rank
        
        if len(cleaned_timeline) >= 3:  # Ensure we still have enough data after cleaning
            final_data[player_id] = {
                'player_info': player_data,
                'timeline': cleaned_timeline
            }
    
    print(f"Final dataset: {len(final_data)} top 10 players with sufficient data")
    return final_data

def main():
    """Main function to process ATP ranking data."""
    print("Processing ATP highest ranking data for top 10 players...")
    
    ranking_data = create_ranking_timeline_data()
    
    # Save to JSON file
    output_file = 'atp_ranking_timelines.json'
    with open(output_file, 'w') as f:
        json.dump(ranking_data, f, indent=2)
    
    print(f"✅ Highest ranking timeline data saved to {output_file}")
    
    # Print some statistics
    player_count = len(ranking_data)
    avg_years = sum(len(data['timeline']) for data in ranking_data.values()) / player_count if player_count > 0 else 0
    
    print(f"📊 Statistics:")
    print(f"   - Players included: {player_count}")
    print(f"   - Average years of data per player: {avg_years:.1f}")
    
    # Show some examples
    print(f"\n🎾 Sample players included (with highest rankings):")
    for i, (player_id, data) in enumerate(list(ranking_data.items())[:5]):
        player_name = data['player_info']['name']
        years = len(data['timeline'])
        best_rank = min(data['timeline'].values())
        print(f"   {i+1}. {player_name} ({years} years, best: #{best_rank})")

if __name__ == "__main__":
    main()