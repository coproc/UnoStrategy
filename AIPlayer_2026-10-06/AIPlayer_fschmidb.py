import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        # Determine the expected color and value from the game state
        expected_color = game_state.game_state_base.expected_color
        expected_value = game_state.game_state_base.expected_value

        # Use a matching color before matching only the value, to save other colors.
        for card in self.hand:
            if card.color == expected_color and card.color in CARD_COLORS_STANDARD:
                return PlayCard(card)
        for card in self.hand:
            if card.value == expected_value and card.color in CARD_COLORS_STANDARD:
                return PlayCard(card)

        #Counts the colors of the cards in hand and chooses the color with the most cards for special cards.
        for card in self.hand:
            if card.value in CARD_VALUES_SPECIAL:
                color_counts = {
                    color: sum(other.color == color for other in self.hand if other is not card)
                    for color in CARD_COLORS_STANDARD
                }

                best_color = max(color_counts, key=color_counts.get)
                move = PlayColorChoiceCard(card, best_color)

                # Check if the move is valid before returning it
                if game_state.game_state_base.is_move_valid(self.hand, move):
                    return move
        return DrawCard()
