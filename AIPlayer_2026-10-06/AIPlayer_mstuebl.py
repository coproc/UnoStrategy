import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD, CARD_VALUES_ACTION, CARD_VALUES_SPECIAL
from GameState import Player, GameStateBase, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard

class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        for card in self.hand:
            if card.value == game_state.game_state_base.expected_value or card.color == game_state.game_state_base.expected_color:
                card = self.getbestplayablecard(game_state)
                if card is not None:
                    return PlayCard(card)

        for card in self.hand:
            if card.value in [CardValue.NEW_COLOR, CardValue.PLUS4]:
                print("\033[33mPlayed a special card\033[0m")
                return PlayColorChoiceCard(card, self.getmostcommoncolor())

        return DrawCard()


    # Man nimmt die Farbe bei der Farbwahl, die man am meisten im Deck hat.
    # Default ist Rot.
    def getmostcommoncolor(self) -> CardColor:
        color_counts = {color: 0 for color in CARD_COLORS_STANDARD}
        for card in self.hand:
            if card.color in CARD_COLORS_STANDARD:
                color_counts[card.color] += 1
        most_common_color = max(color_counts, key=color_counts.get)
        return most_common_color if color_counts[most_common_color] > 0 else CardColor.RED


    # Es soll die bestmögliche Karte gespielt werden, die man spielen kann. Dabei wird die Farbe gewählt, die man am meisten im Deck hat.
    def getbestplayablecard(self, game_state: GameStatePublic) -> Card | None:
        playable_cards = [card for card in self.hand if card.value == game_state.game_state_base.expected_value or card.color == game_state.game_state_base.expected_color]
        color_counts = {color: 0 for color in CARD_COLORS_STANDARD}
        for card in playable_cards:
            if card.color in CARD_COLORS_STANDARD:
                color_counts[card.color] += 1
        most_common_color = max(color_counts, key=color_counts.get)
        print("\033[32m" + "playable cards: " + ", ".join(str(card) for card in playable_cards) + "\033[0m")

        card_avalible_to_play = [card for card in playable_cards if card.color == most_common_color]

        if len(card_avalible_to_play) > 1:
            card_to_hold = self.getbestcardtohold(card_avalible_to_play)
            best_cards_to_play = [card for card in card_avalible_to_play if card != card_to_hold]
            best_cards_to_play.sort(key=lambda card: card.value.value, reverse=True)
            return best_cards_to_play[0]
        elif len(card_avalible_to_play) == 1:
            return card_avalible_to_play[0]
        return None


    # Man behält sich die Karte einer Farbe als letzte Karte auf, wenn ich dieselbe Karte (mit derselben Nummer) in einer anderen Farbe habe.
    # Wenn ich z.B. eine 5 in Rot und eine 5 in Blau habe und aktuell Blau am Zug ist, spiele ich zuerst alle anderen blauen Karten, bevor ich die 5 in Blau spiele.
    # Erst zum Schluss spiele ich die 5 in Blau, um die 5 in Rot beim nächsten Zug draufzulegen.
    # Denn wenn viele Karten von der gleichen Farbe gespielt werden, ist es wahrscheinlich,
    # dass dem Gegner die Karten dieser Farbe ausgehen und er gezwungen ist, eine Karte zu ziehen.
    def getbestcardtohold(self, playable_cards_with_most_common_color) -> Card | None:
        most_duplicate_value = [card.value for card in playable_cards_with_most_common_color if sum(1 for c in self.hand if c.value == card.value) > 1]
        print("\033[34m" + "most duplicate value: " + ", ".join(str(value) for value in most_duplicate_value) + "\033[0m")
        if most_duplicate_value:
            for card in playable_cards_with_most_common_color:
                if card.value == most_duplicate_value[0]:
                    print("\033[35m" + "best card to play at least: " + str(card) + "\033[0m")
                    return card
        return None