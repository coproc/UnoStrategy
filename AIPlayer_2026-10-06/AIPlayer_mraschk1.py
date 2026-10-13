import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    def count_colors(self) -> dict[CardColor, int]:
        return {
            color: sum(card.color == color for card in self.hand)
            for color in CARD_COLORS_STANDARD
        }

    def strongest_color(self) -> CardColor:
        color_counts = self.count_colors()
        return max(color_counts, key=color_counts.get)

    def is_playable(self, card: Card, game_state: GameStatePublic) -> bool:
        return (
            card.color in CARD_COLORS_STANDARD
            and (
                card.color == game_state.game_state_base.expected_color
                or card.value == game_state.game_state_base.expected_value
            )
        )

    def play(self, game_state: GameStatePublic) -> Move:
        color_counts = self.count_colors()
        playable_cards = [
            card for card in self.hand if self.is_playable(card, game_state)
        ]
        if playable_cards:
            action_values = {
                CardValue.PLUS2: 3,
                CardValue.SKIP: 2,
                CardValue.REVERSE: 1,
            }
            return PlayCard(
                max(
                    playable_cards,
                    key=lambda card: (
                        color_counts[card.color],
                        action_values.get(card.value, 0),
                        sum(other.value == card.value for other in self.hand),
                    ),
                )
            )

        for card in self.hand:
            if card.value in [CardValue.NEW_COLOR, CardValue.PLUS4]:
                return PlayColorChoiceCard(card, self.strongest_color())

        return DrawCard()
