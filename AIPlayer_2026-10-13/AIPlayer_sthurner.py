import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

"""
class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        color_counts = {color: 0 for color in CARD_COLORS_STANDARD}
        for card in self.hand:
            if card.color in color_counts:
                color_counts[card.color] += 1

            enemy_handsizes = game_state.hand_sizes
            print(enemy_handsizes)
            ones = enemy_handsizes.count(1)
            print(type(self.hand))


            if card.value == game_state.game_state_base.expected_value or card.color == game_state.game_state_base.expected_color:
                return PlayCard(card)

        for card in self.hand:
            if card.value in [CardValue.NEW_COLOR, CardValue.PLUS4]:
                most_common_color = max(CARD_COLORS_STANDARD, key=color_counts.get)
                return PlayColorChoiceCard(card, most_common_color)

        return DrawCard()
"""
class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        # 1. Häufigste Farbe in der eigenen Hand ermitteln
        color_counts = {color: 0 for color in CARD_COLORS_STANDARD}
        for card in self.hand:
            if card.color in color_counts:
                color_counts[card.color] += 1
        most_common_color = max(CARD_COLORS_STANDARD, key=color_counts.get)

        # 2. Prüfen, ob ein Gegner (oder man selbst) nur noch 1 Karte hat
        enemy_has_one_card = game_state.hand_sizes_of_other_players.count(1) > (1 if len(self.hand) == 1 else 0)

        # Alle spielbaren Standardkarten filtern
        playable_cards = [
            card for card in self.hand
            if card.color == game_state.game_state_base.expected_color
               or card.value == game_state.game_state_base.expected_value
        ]

        # Eine PLUS4 darf nur gespielt werden, wenn keine Karte der erwarteten Farbe auf der Hand ist
        can_play_plus4 = game_state.game_state_base.expected_color not in [card.color for card in self.hand]

        # LOGIK 1: Notfall-Angriff (Plus-Karten sparen/einzusetzen)
        if enemy_has_one_card:
            plus2_cards = [c for c in playable_cards if c.value == CardValue.PLUS2]
            if plus2_cards:
                return PlayCard(plus2_cards[0])

            plus4_cards = [c for c in self.hand if c.value == CardValue.PLUS4 and can_play_plus4]
            if plus4_cards:
                return PlayColorChoiceCard(plus4_cards[0], most_common_color)

        # LOGIK 2: Farborientiertes Ausspielen
        if playable_cards:
            # Bevorzuge Karten der Farbe, von der die KI am meisten auf der Hand hat
            same_color_playable = [c for c in playable_cards if c.color == most_common_color]
            if same_color_playable:
                return PlayCard(same_color_playable[0])

            # Ansonsten eine beliebige spielbare Karte
            return PlayCard(playable_cards[0])

        # 3. Schwarze / Spezialkarten ablegen, wenn sonst nichts passt
        for card in self.hand:
            if card.value == CardValue.NEW_COLOR or (card.value == CardValue.PLUS4 and can_play_plus4):
                return PlayColorChoiceCard(card, most_common_color)

        # 4. Ziehen, wenn keine Aktion möglich ist
        return DrawCard()
