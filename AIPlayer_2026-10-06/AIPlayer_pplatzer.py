import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        expected_value = game_state.game_state_base.expected_value
        expected_color = game_state.game_state_base.expected_color

        playable = [card for card in self.hand
                    if card.value == expected_value or card.color == expected_color]
        if playable:
            # save wild/+4 cards for when we're actually stuck
            non_wild = [card for card in playable if card.color != CardColor.SPECIAL]
            return PlayCard(non_wild[0] if non_wild else playable[0])

        wild_cards = [card for card in self.hand if card.value in (CardValue.NEW_COLOR, CardValue.PLUS4)]
        if wild_cards:
            return PlayColorChoiceCard(wild_cards[0], self.most_common_color())

        return DrawCard()

    def most_common_color(self) -> CardColor:
        counts = {color: 0 for color in CARD_COLORS_STANDARD}
        for card in self.hand:
            if card.color in counts:
                counts[card.color] += 1
        return max(counts, key=counts.get)