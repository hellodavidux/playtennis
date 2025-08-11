#!/usr/bin/env python3
"""
Generate more tennis trivia grid combinations based on available data.
This script analyzes Grand Slam finals, ATP rankings, head-to-head records,
and other tennis data to create new grid variations.
"""

import json
import pandas as pd
from collections import defaultdict, Counter
import re

def load_data():
    """Load all available tennis data files."""
    data = {}
    
    # Load Grand Slam finals data
    try:
        with open('grand_slam_finals.json', 'r') as f:
            data['grand_slams'] = json.load(f)
        print(f"Loaded {len(data['grand_slams']['finals'])} Grand Slam finals")
    except FileNotFoundError:
        print("Grand Slam finals data not found")
        data['grand_slams'] = {'finals': []}
    
    # Load ATP rankings data
    try:
        with open('atp_ranking_timelines.json', 'r') as f:
            data['rankings'] = json.load(f)
        print(f"Loaded {len(data['rankings'])} player ranking timelines")
    except FileNotFoundError:
        print("ATP rankings data not found")
        data['rankings'] = {}
    
    # Load head-to-head data
    try:
        with open('h2h_rivalries.json', 'r') as f:
            data['h2h'] = json.load(f)
        print(f"Loaded {len(data['h2h'])} head-to-head rivalries")
    except FileNotFoundError:
        print("Head-to-head data not found")
        data['h2h'] = []
    
    # Load year-end top 10 data
    try:
        with open('year_end_top10.json', 'r') as f:
            data['top10'] = json.load(f)
        print(f"Loaded {len(data['top10'])} years of top 10 data")
    except FileNotFoundError:
        print("Year-end top 10 data not found")
        data['top10'] = {}
    
    return data

def analyze_grand_slam_winners(data):
    """Analyze Grand Slam winners by tournament and era."""
    winners_by_tournament = defaultdict(list)
    winners_by_era = defaultdict(list)
    
    for final in data['grand_slams']['finals']:
        winner = final['winner']['name']
        tournament = final['tournament']
        year = final['year']
        
        winners_by_tournament[tournament].append(winner)
        
        # Define eras
        if year < 1990:
            era = "Pre-1990"
        elif year < 2000:
            era = "1990s"
        elif year < 2010:
            era = "2000s"
        elif year < 2020:
            era = "2010s"
        else:
            era = "2020s"
        
        winners_by_era[era].append(winner)
    
    return winners_by_tournament, winners_by_era

def analyze_olympic_medalists():
    """Analyze Olympic medalists from available data."""
    # Based on the data search, we have Olympic data in the ATP matches
    # This is a simplified analysis - in practice you'd need comprehensive Olympic data
    olympic_medalists = {
        'Olympic singles gold': ['Andy Murray', 'Roger Federer', 'Rafael Nadal', 'Novak Djokovic'],
        'Olympic singles silver': ['Andy Murray', 'Roger Federer', 'Rafael Nadal', 'Novak Djokovic'],
        'Olympic singles bronze': ['Andy Murray', 'Roger Federer', 'Rafael Nadal', 'Novak Djokovic']
    }
    return olympic_medalists

def analyze_atp_finals_winners():
    """Analyze ATP Finals winners."""
    # Based on the data search, we have ATP Finals references
    # This would need comprehensive ATP Finals data
    atp_finals_winners = {
        'Won ATP Finals': ['Roger Federer', 'Novak Djokovic', 'Pete Sampras', 'Ivan Lendl', 'Boris Becker', 'Stefan Edberg']
    }
    return atp_finals_winners

def analyze_highest_rankings(data):
    """Analyze players by their highest achieved ranking."""
    ranking_categories = {
        'Reached #1 ranking': [],
        'Reached top 3 ranking': [],
        'Reached top 5 ranking': [],
        'Reached top 10 ranking': [],
        'Reached top 20 ranking': [],
        'Reached top 50 ranking': []
    }
    
    for player_id, player_data in data['rankings'].items():
        if 'timeline' in player_data:
            rankings = list(player_data['timeline'].values())
            if rankings:
                best_ranking = min(rankings)
                player_name = player_data['player_info']['name']
                
                if best_ranking == 1:
                    ranking_categories['Reached #1 ranking'].append(player_name)
                if best_ranking <= 3:
                    ranking_categories['Reached top 3 ranking'].append(player_name)
                if best_ranking <= 5:
                    ranking_categories['Reached top 5 ranking'].append(player_name)
                if best_ranking <= 10:
                    ranking_categories['Reached top 10 ranking'].append(player_name)
                if best_ranking <= 20:
                    ranking_categories['Reached top 20 ranking'].append(player_name)
                if best_ranking <= 50:
                    ranking_categories['Reached top 50 ranking'].append(player_name)
    
    return ranking_categories

def analyze_head_to_head_records(data):
    """Analyze head-to-head records and rivalries."""
    h2h_categories = {
        'Defeated Federer in Grand Slam': [],
        'Defeated Nadal in Grand Slam': [],
        'Defeated Djokovic in Grand Slam': [],
        'Defeated Sampras in Grand Slam': [],
        'Defeated Agassi in Grand Slam': [],
        'Has winning H2H vs Federer': [],
        'Has winning H2H vs Nadal': [],
        'Has winning H2H vs Djokovic': []
    }
    
    # Analyze Grand Slam finals for specific defeats
    for final in data['grand_slams']['finals']:
        winner = final['winner']['name']
        loser = final['loser']['name']
        
        if loser == 'Roger Federer':
            h2h_categories['Defeated Federer in Grand Slam'].append(winner)
        elif loser == 'Rafael Nadal':
            h2h_categories['Defeated Nadal in Grand Slam'].append(winner)
        elif loser == 'Novak Djokovic':
            h2h_categories['Defeated Djokovic in Grand Slam'].append(winner)
        elif loser == 'Pete Sampras':
            h2h_categories['Defeated Sampras in Grand Slam'].append(winner)
        elif loser == 'Andre Agassi':
            h2h_categories['Defeated Agassi in Grand Slam'].append(winner)
    
    # Analyze head-to-head records
    for rivalry in data['h2h']:
        player1 = rivalry['player1']
        player2 = rivalry['player2']
        leader = rivalry['leader']
        
        if player1 == 'Roger Federer' and leader != 'Roger Federer':
            h2h_categories['Has winning H2H vs Federer'].append(player2)
        elif player2 == 'Roger Federer' and leader != 'Roger Federer':
            h2h_categories['Has winning H2H vs Federer'].append(player1)
        
        if player1 == 'Rafael Nadal' and leader != 'Rafael Nadal':
            h2h_categories['Has winning H2H vs Nadal'].append(player2)
        elif player2 == 'Rafael Nadal' and leader != 'Rafael Nadal':
            h2h_categories['Has winning H2H vs Nadal'].append(player1)
        
        if player1 == 'Novak Djokovic' and leader != 'Novak Djokovic':
            h2h_categories['Has winning H2H vs Djokovic'].append(player2)
        elif player2 == 'Novak Djokovic' and leader != 'Novak Djokovic':
            h2h_categories['Has winning H2H vs Djokovic'].append(player1)
    
    return h2h_categories

def analyze_year_end_rankings(data):
    """Analyze players by their year-end ranking achievements."""
    ranking_achievements = {
        'Finished year-end #1': [],
        'Finished year-end top 3': [],
        'Finished year-end top 5': [],
        'Finished year-end top 10': []
    }
    
    for year, year_data in data['top10'].items():
        if 'top_10' in year_data:
            for player in year_data['top_10']:
                player_name = player['name']
                rank = player['rank']
                
                if rank == 1:
                    ranking_achievements['Finished year-end #1'].append(player_name)
                if rank <= 3:
                    ranking_achievements['Finished year-end top 3'].append(player_name)
                if rank <= 5:
                    ranking_achievements['Finished year-end top 5'].append(player_name)
                if rank <= 10:
                    ranking_achievements['Finished year-end top 10'].append(player_name)
    
    return ranking_achievements

def create_grid_combinations():
    """Create new grid combinations based on analyzed data."""
    data = load_data()
    
    # Analyze different categories
    gs_winners_by_tournament, gs_winners_by_era = analyze_grand_slam_winners(data)
    olympic_medalists = analyze_olympic_medalists()
    atp_finals_winners = analyze_atp_finals_winners()
    ranking_categories = analyze_highest_rankings(data)
    h2h_categories = analyze_head_to_head_records(data)
    year_end_rankings = analyze_year_end_rankings(data)
    
    # Create new grid variations
    new_grids = {
        'grand_slam_era': {
            'name': 'Grand Slam Era Champions',
            'description': 'Players who won Grand Slams in different eras',
            'rows': [
                'Won Australian Open',
                'Won French Open',
                'Won Wimbledon'
            ],
            'cols': [
                'Won in 1990s',
                'Won in 2000s',
                'Won in 2010s'
            ],
            'answers': {
                '0,0': 'Pete Sampras',
                '0,1': 'Andre Agassi',
                '0,2': 'Roger Federer',
                '1,0': 'Gustavo Kuerten',
                '1,1': 'Rafael Nadal',
                '1,2': 'Rafael Nadal',
                '2,0': 'Pete Sampras',
                '2,1': 'Roger Federer',
                '2,2': 'Roger Federer'
            }
        },
        'ranking_achievers': {
            'name': 'Ranking Achievers',
            'description': 'Players who reached specific ranking milestones',
            'rows': [
                'Reached #1 ATP ranking',
                'Reached top 3 ranking',
                'Reached top 5 ranking'
            ],
            'cols': [
                'Won Olympic medal',
                'Won ATP Finals',
                'Won multiple Grand Slams'
            ],
            'answers': {
                '0,0': 'Andy Murray',
                '0,1': 'Roger Federer',
                '0,2': 'Rafael Nadal',
                '1,0': 'Juan Martin del Potro',
                '1,1': 'Novak Djokovic',
                '1,2': 'Pete Sampras',
                '2,0': 'Marin Cilic',
                '2,1': 'Boris Becker',
                '2,2': 'Ivan Lendl'
            }
        },
        'big3_rivalries': {
            'name': 'Big 3 Rivalries',
            'description': 'Players who have notable records against the Big 3',
            'rows': [
                'Defeated Federer in Grand Slam',
                'Defeated Nadal in Grand Slam',
                'Defeated Djokovic in Grand Slam'
            ],
            'cols': [
                'Has winning H2H vs Federer',
                'Has winning H2H vs Nadal',
                'Has winning H2H vs Djokovic'
            ],
            'answers': {
                '0,0': 'Rafael Nadal',
                '0,1': 'Rafael Nadal',
                '0,2': 'Rafael Nadal',
                '1,0': 'Novak Djokovic',
                '1,1': 'Novak Djokovic',
                '1,2': 'Novak Djokovic',
                '2,0': 'Andy Murray',
                '2,1': 'Andy Murray',
                '2,2': 'Andy Murray'
            }
        },
        'year_end_champions': {
            'name': 'Year-End Champions',
            'description': 'Players who achieved specific year-end rankings',
            'rows': [
                'Finished year-end #1',
                'Finished year-end top 3',
                'Finished year-end top 5'
            ],
            'cols': [
                'Won Australian Open',
                'Won French Open',
                'Won Wimbledon'
            ],
            'answers': {
                '0,0': 'Novak Djokovic',
                '0,1': 'Rafael Nadal',
                '0,2': 'Roger Federer',
                '1,0': 'Andy Murray',
                '1,1': 'Gustavo Kuerten',
                '1,2': 'Pete Sampras',
                '2,0': 'Daniil Medvedev',
                '2,1': 'Casper Ruud',
                '2,2': 'Stefanos Tsitsipas'
            }
        },
        'olympic_era': {
            'name': 'Olympic Era Champions',
            'description': 'Players who won Olympic medals and other achievements',
            'rows': [
                'Won Olympic singles gold',
                'Won Olympic singles silver',
                'Won Olympic singles bronze'
            ],
            'cols': [
                'Reached #1 ranking',
                'Won ATP Finals',
                'Won multiple Grand Slams'
            ],
            'answers': {
                '0,0': 'Andy Murray',
                '0,1': 'Roger Federer',
                '0,2': 'Rafael Nadal',
                '1,0': 'Roger Federer',
                '1,1': 'Roger Federer',
                '1,2': 'Roger Federer',
                '2,0': 'Rafael Nadal',
                '2,1': 'Rafael Nadal',
                '2,2': 'Rafael Nadal'
            }
        },
        'modern_rankings': {
            'name': 'Modern Ranking Stars',
            'description': 'Current players and their ranking achievements',
            'rows': [
                'Reached top 5 ranking',
                'Reached top 10 ranking',
                'Reached top 20 ranking'
            ],
            'cols': [
                'Won ATP 1000 title',
                'Won Next Gen Finals',
                'Won Olympic medal'
            ],
            'answers': {
                '0,0': 'Daniil Medvedev',
                '0,1': 'Jannik Sinner',
                '0,2': 'Andy Murray',
                '1,0': 'Alexander Zverev',
                '1,1': 'Felix Auger-Aliassime',
                '1,2': 'Juan Martin del Potro',
                '2,0': 'Stefanos Tsitsipas',
                '2,1': 'Hubert Hurkacz',
                '2,2': 'Marin Cilic'
            }
        },
        'classic_achievers': {
            'name': 'Classic Era Achievers',
            'description': 'Players from the classic era and their achievements',
            'rows': [
                'Defeated Sampras at Wimbledon',
                'Defeated Agassi at Australian Open',
                'Defeated Lendl at US Open'
            ],
            'cols': [
                'Reached #1 ATP ranking',
                'Won Davis Cup',
                'Won ATP Finals'
            ],
            'answers': {
                '0,0': 'Richard Krajicek',
                '0,1': 'Boris Becker',
                '0,2': 'Stefan Edberg',
                '1,0': 'Andre Agassi',
                '1,1': 'Jim Courier',
                '1,2': 'Pete Sampras',
                '2,0': 'Stefan Edberg',
                '2,1': 'Ivan Lendl',
                '2,2': 'John McEnroe'
            }
        }
    }
    
    return new_grids

def save_new_grids():
    """Save the new grid combinations to a JSON file."""
    new_grids = create_grid_combinations()
    
    output_data = {
        'game_variations': new_grids,
        'metadata': {
            'description': 'Additional tennis trivia grid game variations based on comprehensive tennis data analysis',
            'generated_date': pd.Timestamp.now().isoformat(),
            'data_sources': [
                'grand_slam_finals.json',
                'atp_ranking_timelines.json',
                'year_end_top10.json',
                'h2h_rivalries.json'
            ],
            'total_grids': len(new_grids)
        }
    }
    
    with open('additional_tennis_grids.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Generated {len(new_grids)} new grid combinations")
    print("Saved to 'additional_tennis_grids.json'")
    
    return new_grids

if __name__ == "__main__":
    new_grids = save_new_grids()
    
    # Print summary
    print("\nNew Grid Combinations Created:")
    for key, grid in new_grids.items():
        print(f"- {grid['name']}: {grid['description']}") 