import importlib
from pathlib import Path
from GameLogic import AIPlayer
from GameState import GameStateBase, GameStatePublic
from UnoDeck import CardValue, Card, CardColor


def test_color_choice():
    state_base = GameStateBase()
    open_card = Card(CardColor.RED, CardValue.ZERO)
    state_base.update_expectation(open_card)
    state_public = GameStatePublic([], state_base)
    player = AIPlayer('tester')
    player.hand = [Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.SPECIAL, CardValue.NEW_COLOR)]
    move = player.play(state_public)
    assert move.new_color == CardColor.YELLOW, f'{move.new_color} != {CardColor.YELLOW}'

def test_lkreisma_when_specialcolor_used():
    state_base = GameStateBase()
    open_card = Card(CardColor.RED, CardValue.ZERO)
    state_public = GameStatePublic([], state_base)
    player = AIPlayer('tester')
    player.hand = [Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.YELLOW, CardValue.TWO), Card(CardColor.GREEN, CardValue.TWO), Card(CardColor.SPECIAL, CardValue.NEW_COLOR)]
    move = player.play(state_public)
    assert move.new_color == CardColor.YELLOW, f'{move.new_color} != {CardColor.YELLOW}'

def test_lkreisma_ai_plays_matching_card():
    player = AIPlayer('tester')
    red_five = Card(CardColor.RED, CardValue.FIVE)
    blue_two = Card(CardColor.BLUE, CardValue.TWO)
    player.hand = [red_five, blue_two]
    base = GameStateBase(expected_color=CardColor.RED, expected_value=CardValue.ONE)
    state = GameStatePublic([], base)
    move = player.play(state)
    assert isinstance(move, PlayCard)
    assert move.card == red_five
    assert base.is_move_valid(player.hand, move)

def test_lkreisma_playing_duplicate_removes_only_one_copy():
    player = Player('tester')
    game = Game((player,))
    duplicate = Card(CardColor.RED, CardValue.FIVE)
    player.hand = [duplicate, duplicate]
    game.game_state.game_state_base.expected_color = CardColor.RED
    game.game_state.game_state_base.expected_value = CardValue.ONE
    game.play(player, PlayCard(duplicate))
    assert player.hand == [duplicate]

def test_lmilicev_new_color_chooses_most_common_color():
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic([], state_base)
    player = LmilicevAIPlayer('tester')
    wild = Card(CardColor.SPECIAL, CardValue.NEW_COLOR)
    player.hand = [Card(CardColor.GREEN, CardValue.TWO), Card(CardColor.GREEN, CardValue.THREE), Card(CardColor.BLUE, CardValue.FIVE), wild]
    move = player.play(state_public)
    assert move.card == wild
    assert move.new_color == CardColor.GREEN

def test_lmilicev_plays_plus4_when_no_expected_color_is_held():
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic([], state_base)
    player = LmilicevAIPlayer('tester')
    plus4 = Card(CardColor.SPECIAL, CardValue.PLUS4)
    player.hand = [Card(CardColor.YELLOW, CardValue.THREE), plus4]
    move = player.play(state_public)
    assert move.card == plus4
    assert move.new_color == CardColor.YELLOW

def test_fobermay_draw_if_nothing_fits():
    """Keine passende Karte und kein Joker -> ziehen"""
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic([], state_base)
    player = AIPlayer('tester')
    player.hand = [Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.BLUE, CardValue.FIVE)]
    move = player.play(state_public)
    assert isinstance(move, DrawCard), f'expected DrawCard, got {move}'

def test_fobermay_normal_card_before_wild():
    """Passende Karte hat Vorrang, Joker und +4 bleiben in der Hand"""
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic([], state_base)
    player = AIPlayer('tester')
    player.hand = [Card(CardColor.SPECIAL, CardValue.PLUS4), Card(CardColor.SPECIAL, CardValue.NEW_COLOR), Card(CardColor.RED, CardValue.NINE)]
    move = player.play(state_public)
    assert type(move) is PlayCard, f'expected a normal PlayCard, got {move}'
    assert move.card == Card(CardColor.RED, CardValue.NINE), f'played {move.card}'
project_root = Path(__file__).resolve().parent
mraschk_path = project_root / 'AIPlayer_2026-10-13' / 'AIPlayer_mraschk1.py'
mraschk_spec = importlib.util.spec_from_file_location('AIPlayer_mraschk1', mraschk_path)
mraschk_module = importlib.util.module_from_spec(mraschk_spec)
#MraschkAIPlayer = mraschk_module.AIPlayer

def test_mraschk1_plays_card_with_strongest_color():
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic((), state_base)
    player = MraschkAIPlayer('tester')
    player.hand = [Card(CardColor.RED, CardValue.ONE), Card(CardColor.RED, CardValue.PLUS2), Card(CardColor.BLUE, CardValue.ZERO)]
    move = player.play(state_public)
    assert isinstance(move, PlayCard)
    assert move.card == Card(CardColor.RED, CardValue.PLUS2)

def test_mraschk1_plays_wild_card_with_strongest_color():
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic((), state_base)
    player = MraschkAIPlayer('tester')
    player.hand = [Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.YELLOW, CardValue.TWO), Card(CardColor.BLUE, CardValue.NEW_COLOR)]
    move = player.play(state_public)
    assert isinstance(move, PlayColorChoiceCard)
    assert move.card == Card(CardColor.BLUE, CardValue.NEW_COLOR)
    assert move.new_color == CardColor.YELLOW

def make_state(open_card):
    state_base = GameStateBase()
    state_base.update_expectation(open_card)
    return GameStatePublic([], state_base)

def test_fschmidb_prefers_matching_color_over_matching_value():
    state_public = make_state(Card(CardColor.RED, CardValue.ZERO))
    player = AIPlayer_fschmidb('tester')
    player.hand = [Card(CardColor.GREEN, CardValue.ZERO), Card(CardColor.RED, CardValue.SEVEN)]
    move = player.play(state_public)
    assert isinstance(move, PlayCard), f'{type(move)} ist kein PlayCard'
    assert move.card.color == CardColor.RED and move.card.value == CardValue.SEVEN, f'Falsche Karte gespielt: {move.card.color} {move.card.value}'

def test_fschmidb_plays_action_card_when_it_keeps_the_most_cards_in_color():
    state_public = make_state(Card(CardColor.RED, CardValue.ZERO))
    player = AIPlayer_fschmidb('tester')
    player.hand = [Card(CardColor.RED, CardValue.ONE), Card(CardColor.RED, CardValue.TWO), Card(CardColor.RED, CardValue.SKIP), Card(CardColor.YELLOW, CardValue.ZERO)]
    move = player.play(state_public)
    assert isinstance(move, PlayCard)
    assert move.card.value == CardValue.SKIP

def test_fschmidb_draws_when_no_card_playable():
    state_public = make_state(Card(CardColor.RED, CardValue.ZERO))
    player = AIPlayer_fschmidb('tester')
    player.hand = [Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.BLUE, CardValue.TWO)]
    move = player.play(state_public)
    assert isinstance(move, DrawCard), f'{type(move)} != DrawCard'
ROOT_DIR = Path(__file__).resolve().parent.parent

def test_cseiler_choose_most_common_color():
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic([], state_base)
    player = AIPlayer('tester')
    player.hand = [Card(CardColor.BLUE, CardValue.ONE), Card(CardColor.BLUE, CardValue.TWO), Card(CardColor.BLUE, CardValue.THREE), Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.SPECIAL, CardValue.NEW_COLOR)]
    move = player.play(state_public)
    assert move.new_color == CardColor.BLUE

def test_cseiler_prefer_normal_card_over_wild():
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic([], state_base)
    player = AIPlayer('tester')
    player.hand = [Card(CardColor.RED, CardValue.ONE), Card(CardColor.SPECIAL, CardValue.NEW_COLOR)]
    move = player.play(state_public)
    assert move.card.color == CardColor.RED

def test_cseiler_card_removed_from_hand():
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))
    state_public = GameStatePublic([], state_base)
    player = AIPlayer('tester')
    game = Game((player,))
    game.game_state.game_state_base = state_base
    player.hand = [Card(CardColor.RED, CardValue.ONE)]
    old_size = len(player.hand)
    move = player.play(state_public)
    game.play(player, move)
    assert len(player.hand) == old_size - 1

# Test that the AIPlayer chooses the color it has the most of when playing a PLUS4 card
def test_mstuebl_color_choice_with_plus4():
    state_base = GameStateBase()
    open_card = Card(CardColor.RED, CardValue.ZERO)
    state_base.update_expectation(open_card)
    state_public = GameStatePublic([], state_base)
    player = AIPlayer("tester")
    player.hand = [Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.SPECIAL, CardValue.PLUS4)]
    move = player.play(state_public)
    assert move.new_color == CardColor.YELLOW, f"{move.new_color} != {CardColor.YELLOW}"


# Test that the AIPlayer chooses the best playable card based on the most common color in hand
# The best playable card is the one with the highest value of the most common color in hand.
def test_mstuebl_best_playable_card_case_1():
    state_base = GameStateBase()
    open_card = Card(CardColor.YELLOW, CardValue.ZERO)
    state_base.update_expectation(open_card)
    state_public = GameStatePublic([], state_base)
    player = AIPlayer("tester")
    player.hand = [Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.YELLOW, CardValue.TWO), Card(CardColor.BLUE, CardValue.THREE)]
    best_card = player.getbestplayablecard(state_public)
    assert best_card.color == CardColor.YELLOW, f"{best_card.color} != {CardColor.YELLOW}"
    assert best_card.value == CardValue.TWO, f"{best_card.value} != {CardValue.TWO}"


# Extension of test_best_playable_card_case_1
# The best playable card ist the one with the value which is not the same as another card in hand of a different color.
def test_mstuebl_best_playable_card_case_2():
    state_base = GameStateBase()
    open_card = Card(CardColor.YELLOW, CardValue.ZERO)
    state_base.update_expectation(open_card)
    state_public = GameStatePublic([], state_base)
    player = AIPlayer("tester")
    player.hand = [Card(CardColor.YELLOW, CardValue.ONE), Card(CardColor.YELLOW, CardValue.TWO), Card(CardColor.YELLOW, CardValue.THREE), Card(CardColor.BLUE, CardValue.THREE)]
    best_card = player.getbestplayablecard(state_public)
    assert best_card.color == CardColor.YELLOW, f"{best_card.color} != {CardColor.YELLOW}"
    assert best_card.value == CardValue.TWO, f"{best_card.value} != {CardValue.TWO}"

def test_sthurner_draws_card_when_no_fittin_cards_available():
    # die aktuelle Farbe ist Rot. Die hand hat keine Roten und auch keine Spezialkarten.
    # Die AI muss um einen ungültigenZug zu vermeiden
    state_base = GameStateBase()
    open_card = Card(CardColor.RED, CardValue.ZERO)
    state_base.update_expectation(open_card)
    state_public = GameStatePublic([], state_base)

    player = AIPlayer_sthurner('tester')
    player.hand = [
        Card(CardColor.YELLOW, CardValue.ONE),
        Card(CardColor.GREEN, CardValue.ONE),
        Card(CardColor.GREEN, CardValue.TWO),
        Card(CardColor.BLUE, CardValue.SEVEN),
        Card(CardColor.YELLOW, CardValue.REVERSE),
        Card(CardColor.BLUE, CardValue.REVERSE),
    ]
    move = player.play(state_public)
    assert isinstance(move, DrawCard), f"{type(move)} != DrawCard"


def test_sthurner_plays_plus2_when_opponent_has_one_card():
    # Erzeugt ein Spiel mit genau zwei Spielern und einer offenen roten Null.
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))

    # Die AI hat acht Karten, darunter eine spielbare rote PLUS2-Karte.
    player = AIPlayer_sthurner('tester')
    player.hand = [
        Card(CardColor.RED, CardValue.ONE),
        Card(CardColor.RED, CardValue.PLUS2),
        Card(CardColor.YELLOW, CardValue.ONE),
        Card(CardColor.YELLOW, CardValue.THREE),
        Card(CardColor.GREEN, CardValue.FOUR),
        Card(CardColor.GREEN, CardValue.FIVE),
        Card(CardColor.BLUE, CardValue.SIX),
        Card(CardColor.BLUE, CardValue.SEVEN),
        Card(CardColor.YELLOW, CardValue.EIGHT),
    ]
    opponent = Player('opponent', [Card(CardColor.BLUE, CardValue.NINE)])
    game_state = GameState(players=(player, opponent), game_state_base=state_base)
    state_public = GameStatePublic.from_state(game_state)

    move = player.play(state_public)

    assert isinstance(move, PlayCard), f"{type(move)} != PlayCard"
    assert move.card == Card(CardColor.RED, CardValue.PLUS2), (
        f"{move.card} != {Card(CardColor.RED, CardValue.PLUS2)}"
    )


def test_sthurner_does_not_play_plus4_when_holding_expected_color():
    # Der Gegner hat eine Karte, aber die AI hält auch eine rote Karte.
    # Es wäre laut Spielregeln ein ungültiger Zug jetzt die Plus 4 zu spielen!
    state_base = GameStateBase()
    state_base.update_expectation(Card(CardColor.RED, CardValue.ZERO))

    player = AIPlayer_sthurner('tester')
    player.hand = [
        Card(CardColor.RED, CardValue.ONE),
        Card(CardColor.SPECIAL, CardValue.PLUS4),
        Card(CardColor.YELLOW, CardValue.THREE),
        Card(CardColor.YELLOW, CardValue.FOUR),
        Card(CardColor.GREEN, CardValue.FIVE),
        Card(CardColor.GREEN, CardValue.SIX),
        Card(CardColor.BLUE, CardValue.SEVEN),
        Card(CardColor.BLUE, CardValue.EIGHT),
    ]
    opponent = Player('opponent', [Card(CardColor.BLUE, CardValue.NINE)])
    game_state = GameState(players=(player, opponent), game_state_base=state_base)
    state_public = GameStatePublic.from_state(game_state)

    move = player.play(state_public)

    # Die rote Karte ist legal; PLUS4 wäre ungültig, solange Rot auf der Hand ist.
    assert isinstance(move, PlayCard), f"{type(move)} != PlayCard"
    assert move.card == Card(CardColor.RED, CardValue.ONE), (
        f"{move.card} != {Card(CardColor.RED, CardValue.ONE)}"
    )

if __name__ == '__main__':
    test_color_choice()
