from collections import Counter
from dataclasses import replace

from GameLogic import Move, PlayCard, PlayColorChoiceCard, DrawCard
from GameState import GameStateBase, GameStatePublic, Player
from UnoDeck import CardValue, Card, CardColor, CARD_VALUES_SPECIAL, CARD_VALUES_ACTION, CARD_COLORS_STANDARD


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

        remaining = [c for c in self.hand if c != card]

        # Simulate the state after playing this card
        next_base = replace(base)
        next_base.update_from_move(move)

        # Count playable cards for the next turn
        playable_next = sum(
            self._move_for(c, remaining) is not None
            and next_base.is_move_valid(remaining, self._move_for(c, remaining))
            for c in remaining
        )

        # Prioritize avoiding a situation with no playable cards
        can_play_next = playable_next > 0

        return (
            can_play_next,  # 1. Avoid being stuck next turn
            playable_next,  # 2. Keep more options open
            not self._is_wild(card),  # 3. Save wild cards if possible
            self._points(card),  # 4. Get rid of expensive cards
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