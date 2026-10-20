from collections import defaultdict
from itertools import combinations
from statistics import median, mean
import sys

from AIPlayer_cseiler import AIPlayer as AIPlayer_cseiler
from AIPlayer_fobermay import AIPlayer as AIPlayer_fobermay
from AIPlayer_fschmidb import AIPlayer as AIPlayer_fschmidb
from AIPlayer_lkreisma import AIPlayer as AIPlayer_lkreisma
from AIPlayer_lmilicev import AIPlayer as AIPlayer_lmilicev
from AIPlayer_mstuebl import AIPlayer as AIPlayer_mstuebl
#from AIPlayer_pplatzer import AIPlayer as AIPlayer_pplatzer
from AIPlayer_mraschk1 import AIPlayer as AIPlayer_mraschk1
from AIPlayer_sthurner import AIPlayer as AIPlayer_sthurner

AIPLAYERS = (
    AIPlayer_cseiler('cseiler'),
    AIPlayer_fobermay('fobermay'),
    AIPlayer_fschmidb('fschmidb'),
    AIPlayer_lkreisma('lkreisma'),
    AIPlayer_lmilicev('lmilicev'),
    AIPlayer_mstuebl('mstuebl'),
    #AIPlayer_pplatzer('pplatzer'),
    AIPlayer_mraschk1('mraschk1'),
    AIPlayer_sthurner('sthurner'),
)
for idx, player in enumerate(AIPLAYERS):
    player.idx = idx

sys.path.append('..')
from GameLogic import Game as UnoGame


def evaluate_single_AIPlayer(player, runCount: int = 100):
    TURN_COUNT_MAX = 500
    turn_counts = [
        next(iter(players_done.items()))[1] if (players_done := UnoGame((player,)).run(turn_count_max=TURN_COUNT_MAX)) else TURN_COUNT_MAX + 1
        for _ in range(runCount)
    ]
    return player.name, median(turn_counts)


def run_tournament_with_single_AIPlayers(players, runCount: int = 100):
    evals_single = [evaluate_single_AIPlayer(player, runCount) for player in players]
    evals_single.sort(key=lambda ev: ev[1])
    for name, median_turn_count in evals_single:
      print(f"{name}: {median_turn_count}")


def evaluate_grouped_AIPlayers(players, runCount: int = 100):
    assert len(players) >= 2, f"only works for at least 2 players, {len(players)} given"
    TURN_COUNT_MAX = 500
    turn_counts = defaultdict(list)
    for _ in range(runCount):
        players_done = UnoGame(players).run(turn_count_max=TURN_COUNT_MAX)
        for player in players:
            if player.idx in players_done:
                turn_count = players_done[player.idx]
            else:
                turn_count = TURN_COUNT_MAX + 2*len(player.hand)
            turn_counts[player.idx].append(turn_count)
    turn_medians = [(idx, median(counts)) for idx, counts in turn_counts.items()]
    turn_medians.sort(key=lambda ev: ev[1])
    ranking =  {pl_idx: rank for rank, (pl_idx, _) in enumerate(turn_medians, start=1)}
    return ranking


def run_tournament_with_paired_AIPlayers(players, runCount: int = 100):
    # for all pairs of players, evaluate the median turn count
    rankings = defaultdict(list)
    for player1, player2 in combinations(players, 2):
        ranking = evaluate_grouped_AIPlayers((player1, player2), runCount)
        print(player1.name, player2.name, ranking)
        for pl_idx, rank in ranking.items():
            rankings[pl_idx].append(rank)
    ranking_mean = [(pl_idx, mean(ranks)) for pl_idx, ranks in rankings.items()]
    ranking_mean.sort(key=lambda ev: ev[1])
    for pl_idx, mean_rank in ranking_mean:
        print(f"{players[pl_idx].name}: {mean_rank}")


if __name__ == "__main__":
    #run_tournament_with_single_AIPlayers(AIPLAYERS)
    """
mraschk1: 30.0
fobermay: 35.0
cseiler: 38.0
mstuebl: 41.0
sthurner: 70.0
fschmidb: 74.0
lmilicev: 116.0
lkreisma: 156.0
"""
    run_tournament_with_paired_AIPlayers(AIPLAYERS, runCount=30)
