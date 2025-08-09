#!/usr/bin/env python3
"""
Process Grand Slam tournament data from ATP match files.
Creates a consolidated JSON file with player Grand Slam performance timelines.
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path

def load_players():
    """Load player information from atp_players.csv"""
    try:
        players_df = pd.read_csv('tennis_atp-master/atp_players.csv')
        players = {}
        for _, row in players_df.iterrows():
            players[str(row['player_id'])] = {
                'id': str(row['player_id']),
                'name': f"{row['name_first']} {row['name_last']}".strip(),
                'first_name': str(row['name_first']).strip(),
                'last_name': str(row['name_last']).strip(),
                'country': str(row['ioc']).strip() if pd.notna(row['ioc']) else '',
                'hand': str(row['hand']).strip() if pd.notna(row['hand']) else '',
                'dob': str(row['dob']).strip() if pd.notna(row['dob']) else ''
            }
        print(f"Loaded {len(players)} players")
        return players
    except Exception as e:
        print(f"Error loading players: {e}")
        return {}

def process_year_matches(year, players):
    """Process matches for a specific year"""
    filename = f'tennis_atp-master/atp_matches_{year}.csv'
    
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return {}
    
    try:
        print(f"Processing {year}...")
        df = pd.read_csv(filename, low_memory=False)
        
        # Filter for Grand Slam matches only (tourney_level = 'G')
        grand_slam_matches = df[df['tourney_level'] == 'G'].copy()
        
        if grand_slam_matches.empty:
            print(f"No Grand Slam matches found in {year}")
            return {}
        
        print(f"Found {len(grand_slam_matches)} Grand Slam matches in {year}")
        
        # Dictionary to store player results for this year
        year_results = {}
        
        # Grand Slam tournament name mapping
        tournament_map = {
            'Australian Open': 'AO',
            'Roland Garros': 'RG',
            'Wimbledon': 'W',
            'US Open': 'USO',
            'Us Open': 'USO'  # Handle inconsistent naming
        }
        
        # Round order for determining best result
        round_order = ['R128', 'R64', 'R32', 'R16', 'QF', 'SF', 'F', 'W']
        
        for _, match in grand_slam_matches.iterrows():
            tournament_name = match['tourney_name']
            tournament_code = tournament_map.get(tournament_name)
            
            if not tournament_code:
                continue
                
            winner_id = str(match['winner_id'])
            loser_id = str(match['loser_id'])
            round_code = match['round']
            
            # Process winner
            if winner_id in players:
                if winner_id not in year_results:
                    year_results[winner_id] = {}
                
                # For winner, check if this is a final to determine if they won the tournament
                result = 'W' if round_code == 'F' else round_code
                
                # Keep the best result for this tournament
                if tournament_code not in year_results[winner_id]:
                    year_results[winner_id][tournament_code] = result
                else:
                    current_result = year_results[winner_id][tournament_code]
                    if round_order.index(result) > round_order.index(current_result):
                        year_results[winner_id][tournament_code] = result
            
            # Process loser
            if loser_id in players:
                if loser_id not in year_results:
                    year_results[loser_id] = {}
                
                result = round_code
                
                # Keep the best result for this tournament
                if tournament_code not in year_results[loser_id]:
                    year_results[loser_id][tournament_code] = result
                else:
                    current_result = year_results[loser_id][tournament_code]
                    if round_order.index(result) > round_order.index(current_result):
                        year_results[loser_id][tournament_code] = result
        
        print(f"Processed {len(year_results)} players with Grand Slam results in {year}")
        return year_results
        
    except Exception as e:
        print(f"Error processing {year}: {e}")
        return {}

def main():
    """Main processing function"""
    print("Starting Grand Slam data processing...")
    
    # Load players
    players = load_players()
    if not players:
        print("Failed to load players data")
        return
    
    # Process years 1990-2024
    start_year = 1990
    end_year = 2024
    
    # Dictionary to store all player timelines
    all_timelines = {}
    
    # Process each year
    for year in range(start_year, end_year + 1):
        year_results = process_year_matches(year, players)
        
        # Merge results into main timelines
        for player_id, tournaments in year_results.items():
            if player_id not in all_timelines:
                all_timelines[player_id] = {}
            
            all_timelines[player_id][str(year)] = tournaments
    
    # Filter players who have at least some Grand Slam results
    filtered_timelines = {}
    for player_id, timeline in all_timelines.items():
        if timeline:  # Only include players with some Grand Slam data
            # Add player info
            player_info = players.get(player_id, {})
            filtered_timelines[player_id] = {
                'player_info': player_info,
                'timeline': timeline
            }
    
    print(f"Total players with Grand Slam data: {len(filtered_timelines)}")
    
    # Calculate some statistics
    total_tournaments = 0
    for player_data in filtered_timelines.values():
        for year_data in player_data['timeline'].values():
            total_tournaments += len(year_data)
    
    print(f"Total tournament entries processed: {total_tournaments}")
    
    # Save to JSON file
    output_file = 'grand_slam_timelines.json'
    try:
        with open(output_file, 'w') as f:
            json.dump(filtered_timelines, f, indent=2)
        print(f"Successfully saved data to {output_file}")
        
        # Print some sample data
        sample_players = list(filtered_timelines.keys())[:5]
        print(f"\nSample players processed:")
        for player_id in sample_players:
            player_data = filtered_timelines[player_id]
            name = player_data['player_info'].get('name', 'Unknown')
            years_with_data = len(player_data['timeline'])
            print(f"  {name} ({player_id}): {years_with_data} years of data")
            
    except Exception as e:
        print(f"Error saving data: {e}")

if __name__ == "__main__":
    main()