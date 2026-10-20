import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard


class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        state = game_state.game_state_base

        # 1. normale Karten, die gerade passen
        playable = [
            i for i, card in enumerate(self.hand)
            if card.value not in CARD_VALUES_SPECIAL
            and state.is_move_valid(self.hand, PlayCard(card))
        ]
        if playable:
            # Die Karte mit den wenigsten "Verbindungen" zu den anderen Karten
            # zuerst loswerden: die wird sonst spaeter schwer los.
            # Gut vernetzte Karten behalten wir, damit wir seltener ziehen muessen.
            best = min(playable, key=self._connections)
            return PlayCard(self.hand[best])

        # 2. Joker nur, wenn nichts anderes geht (normaler Joker vor +4)
        wild_cards = [card for card in self.hand if card.value in CARD_VALUES_SPECIAL]
        wild_cards.sort(key=lambda card: card.value == CardValue.PLUS4)
        for card in wild_cards:
            move = PlayColorChoiceCard(card, self._choose_color())
            if state.is_move_valid(self.hand, move):
                return move

        # 3. ziehen
        return DrawCard()

    def _choose_color(self) -> CardColor:
        """Farbe waehlen, von der wir die meisten Karten haben."""
        return max(
            CARD_COLORS_STANDARD,
            key=lambda color: sum(card.color == color for card in self.hand),
        )

    def _connections(self, index: int) -> int:
        """Wie viele andere Karten in der Hand haben die gleiche Farbe oder den gleichen Wert?"""
        card = self.hand[index]
        return sum(
            i != index and (other.color == card.color or other.value == card.value)
            for i, other in enumerate(self.hand)
        )