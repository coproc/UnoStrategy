import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from UnoDeck import (
    CardValue,
    CardColor,
    Card,
    CARD_COLORS_STANDARD,
    CARD_VALUES_ACTION,
    CARD_VALUES_SPECIAL,
)
from GameState import (
    Player,
    GameStateBase,
    GameStatePublic,
    Move,
    DrawCard,
    PlayCard,
    PlayColorChoiceCard,
)

class AIPlayer(Player):
    def count_colors(self) -> dict[CardColor, int]:
        return {
            color: sum(card.color == color for card in self.hand)
            for color in CARD_COLORS_STANDARD
        }

    def strongest_color(self) -> CardColor:
        color_counts = self.count_colors()
        return max(
            CARD_COLORS_STANDARD,
            key=lambda color: (
                color_counts[color],
                sum(
                    card.value.value
                    for card in self.hand
                    if card.color == color
                ),
            ),
        )

    def is_playable(self, card: Card, game_state: GameStatePublic) -> bool:
        return (
            card.color in CARD_COLORS_STANDARD
            and (
                card.color == game_state.game_state_base.expected_color
                or card.value == game_state.game_state_base.expected_value
            )
        )

    def _wild_move(self, card: Card, game_state: GameStatePublic) -> Move:
        return PlayColorChoiceCard(card, self.strongest_color_after(card))

    def strongest_color_after(self, card: Card) -> CardColor:
        remaining = [hand_card for hand_card in self.hand if hand_card is not card]
        counts = {
            color: sum(other.color == color for other in remaining)
            for color in CARD_COLORS_STANDARD
        }
        return max(CARD_COLORS_STANDARD, key=lambda color: counts[color])

    def _card_score(
        self,
        card: Card,
        color_counts: dict[CardColor, int],
        opponents_almost_out: bool,
    ) -> tuple[int, int, int, int, int]:
        action_priority = {
            CardValue.PLUS2: 4,
            CardValue.SKIP: 3,
            CardValue.REVERSE: 2,
        }
        same_value = sum(other.value == card.value for other in self.hand)
        # Prefer the dominant color, but do not spend its last bridge card
        # when the same value exists in another color.
        bridge_penalty = int(
            same_value > 1
            and sum(
                other.value == card.value and other.color != card.color
                for other in self.hand
            ) > 0
        )
        return (
            color_counts[card.color],
            1 if opponents_almost_out and card.value in action_priority else 0,
            -bridge_penalty,
            action_priority.get(card.value, 0),
            card.value.value,
        )

    def play(self, game_state: GameStatePublic) -> Move:
        base = game_state.game_state_base
        color_counts = self.count_colors()
        opponents_almost_out = any(
            hand_size <= 1
            for hand_size in game_state.hand_sizes_of_other_players
        )
        playable_cards = [
            card for card in self.hand
            if self.is_playable(card, game_state)
        ]
        if playable_cards:
            return PlayCard(
                max(
                    playable_cards,
                    key=lambda card: self._card_score(
                        card, color_counts, opponents_almost_out
                    ),
                )
            )

        wild_cards = [
            card for card in self.hand if card.value in CARD_VALUES_SPECIAL
        ]
        for card in wild_cards:
            move = self._wild_move(card, game_state)
            if base.is_move_valid(self.hand, move):
                return move

        return DrawCard()
