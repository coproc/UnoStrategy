import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        state = game_state.game_state_base
        playable = [
            card for card in self.hand
            if card.value not in CARD_VALUES_SPECIAL
            and state.is_move_valid(self.hand, PlayCard(card))
        ]

        if playable:
            # Keep a strong follow-up: prefer a card whose color or value
            # matches several cards still in hand. Action cards break ties.
            card = max(
                playable,
                key=lambda candidate: self._card_score(candidate),
            )
            return PlayCard(card)

        wild_cards = [card for card in self.hand if card.value in CARD_VALUES_SPECIAL]
        # Use +4 only if it is valid; prefer a regular wild when both are available.
        wild_cards.sort(key=lambda card: card.value == CardValue.PLUS4)
        for card in wild_cards:
            move = PlayColorChoiceCard(card, self._choose_color())
            if state.is_move_valid(self.hand, move):
                return move

        return DrawCard()

    def _choose_color(self) -> CardColor:
        """Choose the standard color that appears most often in the hand."""
        return max(
            (CardColor.RED, CardColor.YELLOW, CardColor.GREEN, CardColor.BLUE),
            key=lambda color: sum(card.color == color for card in self.hand),
        )

    def _card_score(self, card: Card) -> int:
        scores = {
            CardValue.SKIP: 3,
            CardValue.REVERSE: 2,
            CardValue.PLUS2: 4,
        }
        follow_up_options = sum(
            other is not card
            and (other.color == card.color or other.value == card.value)
            for other in self.hand
        )
        return 2 * follow_up_options + scores.get(card.value, 0)
