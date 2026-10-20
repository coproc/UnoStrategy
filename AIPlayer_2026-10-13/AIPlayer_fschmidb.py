from GameState import DrawCard, GameStatePublic, Move, Player, PlayCard, PlayColorChoiceCard
from UnoDeck import CARD_COLORS_STANDARD, CARD_VALUES_SPECIAL, Card, CardColor, CardValue


class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        expected_color = game_state.game_state_base.expected_color
        expected_value = game_state.game_state_base.expected_value

        # Wie viele Karten pro Farbe habe ich auf der Hand?
        color_counts = {
            color: sum(card.color == color for card in self.hand)
            for color in CARD_COLORS_STANDARD
        }

        # Alle normalen Karten, die passen (Farbe ODER Wert)
        playable = [
            card
            for card in self.hand
            if card.color in CARD_COLORS_STANDARD
            and (card.color == expected_color or card.value == expected_value)
        ]

        # Die Karte mit der häufigsten Farbe spielen -> danach kann ich weiterlegen
        if playable:
            best_card = max(playable, key=lambda card: color_counts[card.color])
            return PlayCard(best_card)

        # Joker nur, wenn keine normale Karte passt
        for card in self.hand:
            if card.value in CARD_VALUES_SPECIAL:
                color_counts = {
                    color: sum(other.color == color for other in self.hand if other is not card)
                    for color in CARD_COLORS_STANDARD
                }

                best_color = max(color_counts, key=color_counts.get)
                move = PlayColorChoiceCard(card, best_color)

                if game_state.game_state_base.is_move_valid(self.hand, move):
                    return move

        return DrawCard()