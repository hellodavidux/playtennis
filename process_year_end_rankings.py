#!/usr/bin/env python3
"""
Process ATP year-end rankings data to extract top 10 for each year from 2000-2024.
Creates a JSON file for the top 10 guessing game.
"""

import csv
import json
from collections import defaultdict
from datetime import datetime
import os

def load_players():
    """Load player information from atp_players.csv"""
    players = {}
    players_file = 'tennis_atp-master/atp_players.csv'
    
    print(f"Loading players from {players_file}...")
    
    with open(players_file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            player_id = row['player_id']
            first_name = row['name_first'] or ''
            last_name = row['name_last'] or ''
            full_name = f"{first_name} {last_name}".strip()
            
            players[player_id] = {
                'name': full_name,
                'first_name': first_name,
                'last_name': last_name,
                'hand': row['hand'],
                'dob': row['dob'],
                'country': row['ioc'],
                'height': row['height']
            }
    
    print(f"Loaded {len(players)} players")
    return players

def load_rankings_from_file(filename):
    """Load rankings from a specific CSV file"""
    rankings = defaultdict(dict)
    
    print(f"Loading rankings from {filename}...")
    
    with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = row['ranking_date']
            rank = int(row['rank'])
            player_id = row['player']
            points = int(row['points']) if row['points'] else 0
            
            # Store only if this is a better (lower) rank for this player on this date
            if date not in rankings or rank not in rankings[date]:
                rankings[date][rank] = {
                    'player_id': player_id,
                    'points': points
                }
    
    print(f"Loaded rankings for {len(rankings)} dates from {filename}")
    return rankings

def get_year_end_rankings(rankings, year):
    """Get the last ranking of the year for the given year"""
    year_str = str(year)
    year_dates = []
    
    # Find all dates for this year
    for date in rankings.keys():
        if date.startswith(year_str):
            year_dates.append(date)
    
    if not year_dates:
        return None
    
    # Get the latest date in the year
    latest_date = max(year_dates)
    year_end_ranking = rankings[latest_date]
    
    # Get top 10 only
    top_10 = {}
    for rank in range(1, 11):
        if rank in year_end_ranking:
            top_10[rank] = year_end_ranking[rank]
    
    return {
        'date': latest_date,
        'rankings': top_10
    }

def process_all_rankings():
    """Process all ranking files and extract year-end top 10 for 2000-2024"""
    players = load_players()
    
    # Load rankings from all files
    all_rankings = defaultdict(dict)
    
    ranking_files = [
        'tennis_atp-master/atp_rankings_00s.csv',
        'tennis_atp-master/atp_rankings_10s.csv', 
        'tennis_atp-master/atp_rankings_20s.csv',
        'tennis_atp-master/atp_rankings_current.csv'
    ]
    
    for filename in ranking_files:
        if os.path.exists(filename):
            file_rankings = load_rankings_from_file(filename)
            # Merge with all_rankings
            for date, date_rankings in file_rankings.items():
                all_rankings[date].update(date_rankings)
    
    # Extract year-end top 10 for each year from 2000 to 2024
    year_end_data = {}
    
    for year in range(2000, 2025):
        print(f"Processing year {year}...")
        year_data = get_year_end_rankings(all_rankings, year)
        
        if year_data:
            # Add player names and details
            processed_rankings = []
            for rank in range(1, 11):
                if rank in year_data['rankings']:
                    player_info = year_data['rankings'][rank]
                    player_id = player_info['player_id']
                    
                    if player_id in players:
                        processed_rankings.append({
                            'rank': rank,
                            'player_id': player_id,
                            'name': players[player_id]['name'],
                            'first_name': players[player_id]['first_name'],
                            'last_name': players[player_id]['last_name'],
                            'country': players[player_id]['country'],
                            'points': player_info['points'],
                            'hand': players[player_id]['hand']
                        })
                    else:
                        print(f"Warning: Player {player_id} not found in players database")
                        processed_rankings.append({
                            'rank': rank,
                            'player_id': player_id,
                            'name': f'Unknown Player {player_id}',
                            'first_name': 'Unknown',
                            'last_name': f'Player {player_id}',
                            'country': 'UNK',
                            'points': player_info['points'],
                            'hand': 'U'
                        })
            
            year_end_data[str(year)] = {
                'year': year,
                'date': year_data['date'],
                'top_10': processed_rankings
            }
            
            print(f"Year {year}: Found {len(processed_rankings)} players in top 10")
            if processed_rankings:
                print(f"  #1: {processed_rankings[0]['name']} ({processed_rankings[0]['country']})")
        else:
            print(f"Warning: No data found for year {year}")
    
    return year_end_data

def main():
    """Main function to process rankings and create JSON file"""
    print("Processing ATP year-end rankings (2000-2024)...")
    
    year_end_data = process_all_rankings()
    
    # Save to JSON file
    output_file = 'year_end_top10.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(year_end_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nProcessing complete! Data saved to {output_file}")
    print(f"Processed data for {len(year_end_data)} years")
    
    # Show summary
    print("\nSummary by year:")
    for year in sorted(year_end_data.keys()):
        data = year_end_data[year]
        top_player = data['top_10'][0] if data['top_10'] else None
        if top_player:
            print(f"{year}: {top_player['name']} ({top_player['country']}) - {len(data['top_10'])} players")
        else:
            print(f"{year}: No data available")

if __name__ == "__main__":
    main()