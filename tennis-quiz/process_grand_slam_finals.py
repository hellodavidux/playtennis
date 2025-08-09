#!/usr/bin/env python3
"""
Process Grand Slam finals data from ATP tennis matches (2000-2024)
Extract finals with complete score information for the quiz game.
"""

import os
import pandas as pd
import json
import re
from typing import Dict, List, Tuple, Optional

def parse_score(score_str: str) -> Optional[List[Dict[str, int]]]:
    """
    Parse tennis score string into structured set data.
    
    Examples:
    "6-3 6-2 3-6 6-3" -> [{"winner": 6, "loser": 3}, {"winner": 6, "loser": 2}, ...]
    "6-7(3) 7-6(5) 6-4 6-2" -> [{"winner": 6, "loser": 7}, {"winner": 7, "loser": 6}, ...]
    
    Returns None if score cannot be parsed properly.
    """
    if not score_str or pd.isna(score_str):
        return None
        
    score_str = score_str.strip()
    
    # Handle retirement, walkover, or incomplete scores
    if any(keyword in score_str.upper() for keyword in ['RET', 'W/O', 'DEF']):
        return None
    
    # Split by spaces to get individual sets
    sets = score_str.split()
    parsed_sets = []
    
    for set_score in sets:
        # Remove tiebreak scores in parentheses for parsing
        clean_set = re.sub(r'\(\d+\)', '', set_score)
        
        # Match pattern like "6-4" or "7-5"
        match = re.match(r'^(\d+)-(\d+)$', clean_set)
        if not match:
            # Invalid set format, skip this match
            return None
            
        winner_games = int(match.group(1))
        loser_games = int(match.group(2))
        
        # Basic validation for tennis scores
        if winner_games > 7 or loser_games > 7:
            return None
        if winner_games < 6 and loser_games < 6:
            return None
        if winner_games == loser_games:
            return None
            
        parsed_sets.append({
            "winner": winner_games,
            "loser": loser_games
        })
    
    # Should have 3-5 sets for a complete match
    if len(parsed_sets) < 3 or len(parsed_sets) > 5:
        return None
        
    return parsed_sets

def get_tournament_display_name(tournament_name: str) -> str:
    """Convert tournament name to display format."""
    tournament_map = {
        'Australian Open': 'Australian Open',
        'Roland Garros': 'French Open', 
        'Wimbledon': 'Wimbledon',
        'US Open': 'US Open'
    }
    return tournament_map.get(tournament_name, tournament_name)

def process_grand_slam_finals(data_dir: str = 'tennis_atp-master') -> Dict:
    """
    Process all Grand Slam finals from 2000-2024.
    
    Returns dictionary with finals data structured for the quiz game.
    """
    finals_data = {
        'finals': [],
        'metadata': {
            'data_range': '2000-2024',
            'total_finals': 0,
            'tournaments': ['Australian Open', 'French Open', 'Wimbledon', 'US Open']
        }
    }
    
    # Process years from 2000 to 2024
    for year in range(2000, 2025):
        csv_file = os.path.join(data_dir, f'atp_matches_{year}.csv')
        
        if not os.path.exists(csv_file):
            print(f"Warning: File {csv_file} not found, skipping...")
            continue
            
        print(f"Processing {year}...")
        
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            
            # Filter for Grand Slam finals
            grand_slam_finals = df[
                (df['tourney_level'] == 'G') & 
                (df['round'] == 'F')
            ].copy()
            
            for _, match in grand_slam_finals.iterrows():
                # Parse the score
                parsed_sets = parse_score(match.get('score', ''))
                
                if parsed_sets is None:
                    print(f"  Skipping {year} {match.get('tourney_name', 'Unknown')} - invalid score: {match.get('score', 'N/A')}")
                    continue
                
                # Helper function to clean NaN values
                def clean_value(value, default=''):
                    if pd.isna(value) or value == '' or str(value).lower() == 'nan':
                        return default if default != '' else None
                    return value

                # Create final data structure
                final_data = {
                    'id': f"{year}_{match.get('tourney_name', '').replace(' ', '_').lower()}",
                    'year': year,
                    'tournament': get_tournament_display_name(match.get('tourney_name', '')),
                    'surface': clean_value(match.get('surface', ''), 'Hard'),
                    'date': clean_value(match.get('tourney_date', '')),
                    'winner': {
                        'name': clean_value(match.get('winner_name', ''), 'Unknown'),
                        'country': clean_value(match.get('winner_ioc', ''), 'Unknown'),
                        'seed': clean_value(match.get('winner_seed', '')),
                        'age': clean_value(match.get('winner_age', ''))
                    },
                    'loser': {
                        'name': clean_value(match.get('loser_name', ''), 'Unknown'),
                        'country': clean_value(match.get('loser_ioc', ''), 'Unknown'),  
                        'seed': clean_value(match.get('loser_seed', '')),
                        'age': clean_value(match.get('loser_age', ''))
                    },
                    'score_raw': clean_value(match.get('score', ''), ''),
                    'sets': parsed_sets,
                    'duration_minutes': clean_value(match.get('minutes', '')),
                    'best_of': clean_value(match.get('best_of', 5), 5)
                }
                
                finals_data['finals'].append(final_data)
                print(f"  Added: {final_data['tournament']} - {final_data['winner']['name']} def. {final_data['loser']['name']}")
        
        except Exception as e:
            print(f"Error processing {year}: {e}")
            continue
    
    # Sort finals by year and tournament order
    tournament_order = ['Australian Open', 'French Open', 'Wimbledon', 'US Open']
    
    def sort_key(final):
        year = final['year']
        tournament = final['tournament']
        tournament_index = tournament_order.index(tournament) if tournament in tournament_order else 99
        return (year, tournament_index)
    
    finals_data['finals'].sort(key=sort_key)
    finals_data['metadata']['total_finals'] = len(finals_data['finals'])
    
    print(f"\nTotal finals processed: {finals_data['metadata']['total_finals']}")
    
    return finals_data

def main():
    """Main execution function."""
    print("Processing Grand Slam finals from 2000-2024...")
    
    # Check if data directory exists
    data_dir = 'tennis_atp-master'
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' not found!")
        return
    
    # Process the data
    finals_data = process_grand_slam_finals(data_dir)
    
    # Save to JSON file
    output_file = 'grand_slam_finals.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(finals_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to {output_file}")
    
    # Print some statistics
    metadata = finals_data['metadata']
    print(f"Total finals: {metadata['total_finals']}")
    
    # Count by tournament
    tournament_counts = {}
    for final in finals_data['finals']:
        tournament = final['tournament']
        tournament_counts[tournament] = tournament_counts.get(tournament, 0) + 1
    
    print("\nFinals by tournament:")
    for tournament, count in tournament_counts.items():
        print(f"  {tournament}: {count}")
    
    # Show some examples
    print(f"\nFirst 3 finals:")
    for final in finals_data['finals'][:3]:
        sets_str = " ".join([f"{s['winner']}-{s['loser']}" for s in final['sets']])
        print(f"  {final['year']} {final['tournament']}: {final['winner']['name']} def. {final['loser']['name']} ({sets_str})")

if __name__ == "__main__":
    main()