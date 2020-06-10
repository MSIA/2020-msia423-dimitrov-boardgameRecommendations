import numpy as np
import pickle
import dill
from boardgamegeek import BGGClient
from boardgamegeek.exceptions import BGGApiError, BGGError, BGGItemNotFoundError, BGGValueError
bgg = BGGClient(requests_per_minute=100)

# Configuration
final_game_id = 100
games_per_request = 50

def batch_api_call(games_per_request, final_game_id):
    
    gameDump = []
    batch = 0
    # Prepare batches of game ids
    flatArray = np.array(range(final_game_id))
    npArray = flatArray.reshape((int(final_game_id/games_per_request),games_per_request))
    lstArray = list(npArray)
    lstArray = [lst.tolist() for lst in lstArray]
    
    for lst in lstArray:
        print(batch)
        batch += 1
        try:
            games = bgg.game_list(lst)
            gameDump.extend(games)
        except BGGApiError:
            continue
    
    return gameDump


def fetch_game_ids(games):
    ids = []
    for game in games:
        ids.append(game.id)
    return set(ids)

def find_missing_ids(expected, actual):
    return list(set(expected).difference(set(actual)))


def missing_games_api_call(missing_ids):
    
    missing_games = []
    
    for missing_id in missing_ids:
        print(missing_id)
        try:
            missing_games.append(bgg.game(game_id=missing_id))
        except BGGApiError:
            continue 
    return missing_games

if __name__ == '__main__':
    gameDump = batch_api_call(games_per_request, final_game_id)
    with open('mydill.dill', 'wb') as f:
        dill.dump(gameDump, f)
