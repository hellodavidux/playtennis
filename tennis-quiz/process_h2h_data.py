#!/usr/bin/env python3
"""
Process ATP match data to extract historical head-to-head records for tennis quiz game.
Focuses on famous rivalries from tennis history.
"""

import pandas as pd
import json
import os
from collections import defaultdict, Counter
import glob

def load_atp_matches():
    """Load all ATP match data from CSV files."""
    matches_dir = "tennis_atp-master"
    all_matches = []
    
    # Get all match files
    match_files = glob.glob(f"{matches_dir}/atp_matches_*.csv")
    
    for file in sorted(match_files):
        try:
            df = pd.read_csv(file)
            year = file.split('_')[-1].replace('.csv', '')
            df['year'] = int(year)
            all_matches.append(df)
            print(f"Loaded {len(df)} matches from {year}")
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    if all_matches:
        combined_df = pd.concat(all_matches, ignore_index=True)
        print(f"Total matches loaded: {len(combined_df)}")
        return combined_df
    else:
        return pd.DataFrame()

def load_players_data():
    """Load player names and info."""
    try:
        players_df = pd.read_csv("tennis_atp-master/atp_players.csv")
        # Create a mapping of player_id to name
        player_names = {}
        for _, row in players_df.iterrows():
            player_names[row['player_id']] = f"{row['name_first']} {row['name_last']}"
        return player_names
    except Exception as e:
        print(f"Error loading players data: {e}")
        return {}

def calculate_h2h_records(matches_df, player_names):
    """Calculate head-to-head records between all players."""
    h2h_records = defaultdict(lambda: defaultdict(lambda: {'wins': 0, 'losses': 0, 'matches': []}))
    
    for _, match in matches_df.iterrows():
        winner_id = match['winner_id']
        loser_id = match['loser_id']
        
        # Skip if either player ID is missing
        if pd.isna(winner_id) or pd.isna(loser_id):
            continue
            
        winner_id = int(winner_id)
        loser_id = int(loser_id)
        
        # Get player names
        winner_name = player_names.get(winner_id, f"Player_{winner_id}")
        loser_name = player_names.get(loser_id, f"Player_{loser_id}")
        
        # Record the match
        match_info = {
            'year': match.get('year', 'Unknown'),
            'tournament': match.get('tourney_name', 'Unknown'),
            'surface': match.get('surface', 'Unknown'),
            'score': match.get('score', 'Unknown')
        }
        
        # Update records for both players
        h2h_records[winner_name][loser_name]['wins'] += 1
        h2h_records[loser_name][winner_name]['losses'] += 1
        h2h_records[winner_name][loser_name]['matches'].append(match_info)
        h2h_records[loser_name][winner_name]['matches'].append(match_info)
    
    return h2h_records

def get_famous_rivalries():
    """Define famous tennis rivalries to focus on, prioritizing 80s onwards."""
    return [
        # Big 3 era (prioritized)
        ("Roger Federer", "Rafael Nadal"),
        ("Roger Federer", "Novak Djokovic"),
        ("Rafael Nadal", "Novak Djokovic"),
        ("Roger Federer", "Andy Murray"),
        ("Rafael Nadal", "Andy Murray"),
        ("Novak Djokovic", "Andy Murray"),
        
        # 80s-90s era (prioritized)
        ("Ivan Lendl", "John McEnroe"),
        ("Ivan Lendl", "Jimmy Connors"),
        ("Pete Sampras", "Andre Agassi"),
        ("Stefan Edberg", "Boris Becker"),
        ("Ivan Lendl", "Mats Wilander"),
        ("Andre Agassi", "Jim Courier"),
        ("Pete Sampras", "Jim Courier"),
        ("Stefan Edberg", "Ivan Lendl"),
        ("Boris Becker", "Ivan Lendl"),
        ("Pete Sampras", "Boris Becker"),
        ("Andre Agassi", "Michael Chang"),
        ("Stefan Edberg", "Pat Rafter"),
        
        # 2000s generation
        ("Andy Roddick", "Roger Federer"),
        ("Lleyton Hewitt", "Roger Federer"),
        ("David Ferrer", "Rafael Nadal"),
        ("Stan Wawrinka", "Novak Djokovic"),
        ("Juan Martin del Potro", "Roger Federer"),
        ("Juan Martin del Potro", "Rafael Nadal"),
        ("Andy Roddick", "Lleyton Hewitt"),
        ("Marat Safin", "Roger Federer"),
        ("Gustavo Kuerten", "Andre Agassi"),
        ("Lleyton Hewitt", "David Nalbandian"),
        
        # Next gen (modern)
        ("Daniil Medvedev", "Rafael Nadal"),
        ("Stefanos Tsitsipas", "Novak Djokovic"),
        ("Alexander Zverev", "Novak Djokovic"),
        ("Dominic Thiem", "Rafael Nadal"),
        ("Daniil Medvedev", "Stefanos Tsitsipas"),
        ("Alexander Zverev", "Dominic Thiem"),
        
        # Classic era (reduced priority)
        ("Jimmy Connors", "John McEnroe"),
        ("Bjorn Borg", "John McEnroe"),
        ("Bjorn Borg", "Jimmy Connors"),
    ]

def format_rivalry_data(h2h_records, player1, player2):
    """Format rivalry data for the game."""
    if player1 not in h2h_records or player2 not in h2h_records[player1]:
        return None
    
    p1_record = h2h_records[player1][player2]
    p1_wins = p1_record['wins']
    p1_losses = p1_record['losses']
    
    total_matches = p1_wins + p1_losses
    
    if total_matches < 3:  # Skip rivalries with too few matches
        return None
    
    # Determine who leads
    if p1_wins > p1_losses:
        leader = player1
        leader_wins = p1_wins
        trail_wins = p1_losses
    elif p1_losses > p1_wins:
        leader = player2
        leader_wins = p1_losses
        trail_wins = p1_wins
    else:
        leader = "Tied"
        leader_wins = p1_wins
        trail_wins = p1_losses
    
    # Get surface breakdown
    surface_breakdown = defaultdict(lambda: {'wins': 0, 'losses': 0})
    tournaments = set()
    years_active = set()
    
    for match in p1_record['matches']:
        surface = match.get('surface', 'Unknown')
        year = match.get('year', 'Unknown')
        tournament = match.get('tournament', 'Unknown')
        
        if year != 'Unknown':
            years_active.add(year)
        if tournament != 'Unknown':
            tournaments.add(tournament)
    
    return {
        'player1': player1,
        'player2': player2,
        'total_matches': total_matches,
        'leader': leader,
        'leader_wins': leader_wins,
        'trail_wins': trail_wins,
        'h2h_display': f"{leader_wins}-{trail_wins}",
        'years_span': f"{min(years_active)}-{max(years_active)}" if years_active else "Unknown",
        'total_tournaments': len(tournaments),
        'difficulty': 'medium' if total_matches > 10 else 'easy'
    }

def main():
    """Main function to process data and create H2H quiz data."""
    print("Processing ATP match data for Head-to-Head Masters game...")
    
    # Load data
    print("Loading ATP matches...")
    matches_df = load_atp_matches()
    
    if matches_df.empty:
        print("No match data found!")
        return
    
    print("Loading player names...")
    player_names = load_players_data()
    
    print("Calculating H2H records...")
    h2h_records = calculate_h2h_records(matches_df, player_names)
    
    # Process famous rivalries
    famous_rivalries = get_famous_rivalries()
    rivalry_data = []
    
    print("\nProcessing famous rivalries...")
    for player1, player2 in famous_rivalries:
        rivalry = format_rivalry_data(h2h_records, player1, player2)
        if rivalry:
            rivalry_data.append(rivalry)
            print(f"✓ {player1} vs {player2}: {rivalry['h2h_display']} ({rivalry['total_matches']} matches)")
        else:
            print(f"✗ {player1} vs {player2}: Insufficient data")
    
    # Add some additional interesting rivalries from the data (prioritize 80s onwards)
    print("\nFinding additional rivalries with 15+ matches (prioritizing 80s onwards)...")
    additional_rivalries = []
    processed_pairs = set()
    
    # List of players from 80s onwards to prioritize
    modern_era_keywords = [
        'Ivan Lendl', 'Stefan Edberg', 'Boris Becker', 'Mats Wilander', 'Pat Rafter',
        'Michael Chang', 'Jim Courier', 'Todd Martin', 'Goran Ivanisevic', 'Richard Krajicek',
        'Yevgeny Kafelnikov', 'Alex Corretja', 'Carlos Moya', 'Gustavo Kuerten', 'Marat Safin',
        'Thomas Enqvist', 'Nicolas Escude', 'Fabrice Santoro', 'Arnaud Clement',
        'Tommy Haas', 'Nicolas Kiefer', 'Paradorn Srichaphan', 'Fernando Gonzalez',
        'Nikolay Davydenko', 'David Nalbandian', 'Guillermo Coria', 'Gaston Gaudio',
        'Robin Soderling', 'Tomas Berdych', 'Jo-Wilfried Tsonga', 'Gael Monfils',
        'Janko Tipsarevic', 'Mardy Fish', 'John Isner', 'Kei Nishikori', 'Milos Raonic'
    ]
    
    for p1, opponents in h2h_records.items():
        for p2, record in opponents.items():
            if p1 < p2:  # Avoid duplicates
                pair_key = (p1, p2)
                if pair_key not in processed_pairs:
                    processed_pairs.add(pair_key)
                    total = record['wins'] + record['losses']
                    if total >= 12 and (p1, p2) not in famous_rivalries and (p2, p1) not in famous_rivalries:
                        # Prioritize rivalries involving modern era players
                        is_modern_rivalry = any(keyword in p1 or keyword in p2 for keyword in modern_era_keywords)
                        rivalry = format_rivalry_data(h2h_records, p1, p2)
                        if rivalry:
                            # Add priority score
                            rivalry['priority'] = 2 if is_modern_rivalry else 1
                            additional_rivalries.append(rivalry)
    
    # Sort by priority first (modern era), then by total matches
    additional_rivalries.sort(key=lambda x: (x['priority'], x['total_matches']), reverse=True)
    rivalry_data.extend(additional_rivalries[:25])
    
    print(f"\nTotal rivalries processed: {len(rivalry_data)}")
    
    # Save to JSON file
    output_file = "h2h_rivalries.json"
    with open(output_file, 'w') as f:
        json.dump(rivalry_data, f, indent=2)
    
    print(f"\nH2H data saved to {output_file}")
    print(f"Ready for Head-to-Head Masters game!")
    
    # Print some statistics
    total_matches = sum(r['total_matches'] for r in rivalry_data)
    avg_matches = total_matches / len(rivalry_data) if rivalry_data else 0
    print(f"\nStatistics:")
    print(f"- Total rivalries: {len(rivalry_data)}")
    print(f"- Total matches covered: {total_matches}")
    print(f"- Average matches per rivalry: {avg_matches:.1f}")

if __name__ == "__main__":
    main()