import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        base = game_state.game_state_base

        # Meistvertretene Farbe auf der Hand finden
        color_counts = {color: 0 for color in CARD_COLORS_STANDARD}
        for card in self.hand:
            if card.color in color_counts:
                color_counts[card.color] += 1

        best_color = CARD_COLORS_STANDARD[0]
        max_count = -1
        for color, count in color_counts.items():
            if count > max_count:
                max_count = count
                best_color = color

        has_color = any(c.color == base.expected_color for c in self.hand)

        # 1. Normale Farbe (keine Aktionskarte)
        for card in self.hand:
            if card.color == base.expected_color and card.value not in CARD_VALUES_ACTION:
                return PlayCard(card)

        # 2. Normaler Wert (keine Aktionskarte)
        for card in self.hand:
            if base.expected_value is not None and card.value == base.expected_value:
                if card.value not in CARD_VALUES_ACTION:
                    return PlayCard(card)

        # 3. Aktionskarten wenn nötig
        for card in self.hand:
            if card.color == base.expected_color or card.value == base.expected_value:
                return PlayCard(card)

        # 4. Farbwunsch
        for card in self.hand:
            if card.value == CardValue.NEW_COLOR:
                return PlayColorChoiceCard(card, best_color)

        # 5. Plus 4
        if not has_color:
            for card in self.hand:
                if card.value == CardValue.PLUS4:
                    return PlayColorChoiceCard(card, best_color)

        return DrawCard()