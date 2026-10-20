import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        base = game_state.game_state_base

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

        # Unter den passenden normalen Karten die mit den meisten Anschlusszügen wählen.
        playable_cards = []
        next_player_cards = (
            game_state.hand_sizes_of_other_players[0]
            if game_state.hand_sizes_of_other_players
            else None
        )
        solo_game = not game_state.hand_sizes_of_other_players
        for index, card in enumerate(self.hand):
            if card.color not in CARD_COLORS_STANDARD:
                continue
            if card.color != base.expected_color and (
                base.expected_value is None or card.value != base.expected_value
            ):
                continue

            remaining_hand = self.hand[:index] + self.hand[index + 1:]
            follow_up_count = sum(
                other.color == card.color or other.value == card.value
                for other in remaining_hand
            )
            can_hurt_next_player = (
                next_player_cards is not None
                and next_player_cards <= 2
                and card.value in (CardValue.PLUS2, CardValue.SKIP)
            )
            solo_penalty = int(
                solo_game and card.value in (CardValue.PLUS2, CardValue.PLUS4)
            )
            action_priority = int(can_hurt_next_player)
            normal_card_priority = int(card.value not in CARD_VALUES_ACTION)
            playable_cards.append(
                ((-solo_penalty, follow_up_count, action_priority, normal_card_priority), card)
            )

        if playable_cards:
            _, best_card = max(playable_cards, key=lambda option: option[0])
            return PlayCard(best_card)

        has_color = any(card.color == base.expected_color for card in self.hand)
        plus4_cards = [
            card for card in self.hand
            if card.value == CardValue.PLUS4 and not has_color
        ]
        # +4 ist besonders nützlich, wenn der nächste Spieler fast fertig ist.
        if plus4_cards and next_player_cards is not None and next_player_cards <= 2:
            return PlayColorChoiceCard(plus4_cards[0], best_color)

        # Farbwahlkarten behalten die häufigste eigene Farbe für den nächsten Zug.
        for card in self.hand:
            if card.value == CardValue.NEW_COLOR:
                return PlayColorChoiceCard(card, best_color)

        if plus4_cards:
            return PlayColorChoiceCard(plus4_cards[0], best_color)

        return DrawCard()