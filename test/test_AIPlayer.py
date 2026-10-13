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
    assert move.new_color == CardColor.YELLOW, f"{move.new_color} != {CardColor.YELLOW}"

if __name__ == '__main__':
    test_color_choice()