from statistics import median
import sys

from AIPlayer_cseiler import AIPlayer as AIPlayer_cseiler
from AIPlayer_fobermay import AIPlayer as AIPlayer_fobermay
from AIPlayer_fschmidb import AIPlayer as AIPlayer_fschmidb
from AIPlayer_lkreisma import AIPlayer as AIPlayer_lkreisma
from AIPlayer_lmilicev import AIPlayer as AIPlayer_lmilicev
from AIPlayer_mstuebl import AIPlayer as AIPlayer_mstuebl
from AIPlayer_pplatzer import AIPlayer as AIPlayer_pplatzer
from AIPlayer_mraschk1 import AIPlayer as AIPlayer_mraschk1
from AIPlayer_sthurner import AIPlayer as AIPlayer_sthurner

AIPLAYERS = (
    AIPlayer_cseiler('cseiler'),
    AIPlayer_fobermay('fobermay'),
    AIPlayer_fschmidb('fschmidb'),
    AIPlayer_lkreisma('lkreisma'),
    AIPlayer_lmilicev('lmilicev'),
    AIPlayer_mstuebl('mstuebl'),
    AIPlayer_pplatzer('pplatzer'),
    AIPlayer_mraschk1('mraschk1'),
    AIPlayer_sthurner('sthurner'),
)

sys.path.append('..')
from GameLogic import Game as UnoGame


def evaluate_single_AIPlayer(player, runCount: int = 100):
    TURN_COUNT_MAX = 500
    turn_counts = [
        players_done[0][1] if (players_done := UnoGame((player,)).run(turn_count_max=TURN_COUNT_MAX)) else TURN_COUNT_MAX + 1
        for _ in range(runCount)
    ]
    return player.name, median(turn_counts)


def run_tournament_with_single_AIPlayers(players, runCount: int = 100):
    evals_single = [evaluate_single_AIPlayer(player, runCount) for player in players]
    evals_single.sort(key=lambda ev: ev[1])
    for name, median_turn_count in evals_single:
      print(f"{name}: {median_turn_count}")


if __name__ == "__main__":
  run_tournament_with_single_AIPlayers(AIPLAYERS)
"""
mstuebl: 34.0
pplatzer: 63.0
cseiler: 65.0
fschmidb: 65.0
lmilicev: 70.0
sthurner: 71.0
lkreisma: 115.0
mraschk1: 119.0
fobermay: 147.0
"""