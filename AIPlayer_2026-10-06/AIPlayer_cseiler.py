import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        color_counts = {color: 0 for color in CARD_COLORS_STANDARD}
        for card in self.hand:
            if card.color in color_counts:
                color_counts[card.color] += 1

        moves: list[Move] = []
        for card in self.hand:
            if card.value in [CardValue.NEW_COLOR, CardValue.PLUS4]:
                # Eine Farbwahlkarte wird nur angeboten, wenn sie nach den Regeln erlaubt ist.
                if game_state.game_state_base.is_move_valid(
                        self.hand, PlayColorChoiceCard(card, CARD_COLORS_STANDARD[0])
                ):
                    for color in CARD_COLORS_STANDARD:
                        moves.append(PlayColorChoiceCard(card, color))
            else:
                move = PlayCard(card)
                if game_state.game_state_base.is_move_valid(self.hand, move):
                    moves.append(move)

        if not moves:
            return DrawCard()

        opponents_almost_out = any(
            size <= 2 for size in game_state.hand_sizes_of_other_players
        )

        def move_score(move: Move) -> float:
            card = move.card
            if isinstance(move, PlayColorChoiceCard):
                chosen_color = move.new_color
                # Farbwahlkarten bleiben wertvoll; setze sie daher nur ein, wenn sie
                # wirklich helfen, und wähle die Farbe mit den meisten Anschlusskarten.
                score = color_counts[chosen_color] * 2 - 6
                if card.value == CardValue.PLUS4:
                    score -= 2
            else:
                chosen_color = card.color
                # Bewertet wird, wie viele Karten dieser Farbe nach dem Zug bleiben.
                score = max(0, color_counts[chosen_color] - 1) * 2

            # Hohe Kartenpunkte lieber früh ablegen, damit sie am Spielende nicht zählen.
            score += card.value.value * 0.15

            # Aktionskarten sind besonders nützlich, wenn ein Gegner fast gewonnen hat.
            if opponents_almost_out and card.value in (
                    CardValue.SKIP, CardValue.REVERSE, CardValue.PLUS2, CardValue.PLUS4
            ):
                score += 4

            return score

        return max(moves, key=move_score)
