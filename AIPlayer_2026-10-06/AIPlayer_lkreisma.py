from collections import Counter
from dataclasses import replace
import sys

sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    """
     i use a point system to choose which card should be played
    """

    # ---------- helpers ----------
    @staticmethod
    def _is_wild(card: Card) -> bool:
        return card.value in CARD_VALUES_SPECIAL

    @staticmethod
    def _points(card: Card) -> int:
        if card.value in CARD_VALUES_SPECIAL:
            return 50
        if card.value in CARD_VALUES_ACTION:
            return 20
        return card.value.value  # ZERO..NINE

    def _best_color(self, hand: list[Card]) -> CardColor:
        """Colour we hold the most of (ties: higher total points)."""
        counts = Counter(c.color for c in hand if c.color in CARD_COLORS_STANDARD)
        if not counts:
            return CARD_COLORS_STANDARD[0]
        return max(
            counts,
            key=lambda col: (
                counts[col],
                sum(self._points(c) for c in hand if c.color == col),
            ),
        )

    def _move_for(self, card: Card, hand: list[Card]) -> Move:
        """Build the correct move type for a card."""
        if self._is_wild(card):
            rest = list(hand)
            rest.remove(card)
            return PlayColorChoiceCard(card, self._best_color(rest))
        return PlayCard(card)

    def _score(self, move: PlayCard, base: GameStateBase) -> tuple:

        card = move.card
        remaining = list(self.hand)
        remaining.remove(card)

        # simulate the state after this move
        next_base = replace(base)
        next_base.update_from_move(move)

        playable_next = sum(
            1
            for c in remaining
            if next_base.is_move_valid(remaining, self._move_for(c, remaining))
        )
        return (
            not self._is_wild(card),  # 1) save wild cards
            playable_next,            # 2) keep options open
            self._points(card),       # 3) get rid of expensive cards
        )

    # ---------- decision ----------
    def play(self, game_state: GameStatePublic) -> Move:
        base = game_state.game_state_base

        options: list[Move] = []
        seen = set()
        for card in self.hand:
            key = (card.color, card.value)
            if key in seen:  # duplicate cards give identical moves
                continue
            seen.add(key)

            move = self._move_for(card, self.hand)
            if base.is_move_valid(self.hand, move):
                options.append(move)

        if not options:
            return DrawCard()

        return max(options, key=lambda m: self._score(m, base))