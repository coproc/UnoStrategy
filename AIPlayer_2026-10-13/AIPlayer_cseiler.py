import sys
sys.path.append('..')
from UnoDeck import CardValue, CardColor, Card, CARD_COLORS_STANDARD
from GameState import Player, GameStatePublic, Move, DrawCard, PlayCard, PlayColorChoiceCard


class AIPlayer(Player):

    def play(self, game_state: GameStatePublic) -> Move:
        # Aktuelle Farbe und Zahl/Symbol auf dem Ablagestapel
        expected_color = game_state.game_state_base.expected_color
        expected_value = game_state.game_state_base.expected_value

        # Liste aller möglichen Spielzüge
        legal_moves: list[Move] = []

        # Alle spielbaren Karten suchen
        for card in self.hand:
            if card.value in (CardValue.NEW_COLOR, CardValue.PLUS4):
                # Für Wildkarten jede Farbe testen
                for color in CARD_COLORS_STANDARD:
                    move = PlayColorChoiceCard(card, color)
                    if game_state.game_state_base.is_move_valid(self.hand, move):
                        legal_moves.append(move)
            else:
                move = PlayCard(card)
                if game_state.game_state_base.is_move_valid(self.hand, move):
                    legal_moves.append(move)

        # Wenn nichts gespielt werden kann, Karte ziehen
        if not legal_moves:
            return DrawCard()

        def color_counts(hand: list[Card]) -> dict[CardColor, int]:
            # Anzahl jeder Farbe zählen
            counts = {color: 0 for color in CARD_COLORS_STANDARD}
            for card in hand:
                if card.color in counts:
                    counts[card.color] += 1
            return counts

        def move_priority(move: Move) -> float:
            card = move.card

            # Hand nach dem Ausspielen der Karte
            remaining = [c for c in self.hand if c != card]

            if isinstance(move, PlayColorChoiceCard):
                # Gewählte Farbe bei Wildkarten
                chosen_color = move.new_color
                chosen_value = None
                basic_bonus = 2.5
            else:
                chosen_color = card.color
                chosen_value = card.value
                basic_bonus = 0

            # Sofortiger Sieg
            if not remaining:
                return 1000

            score = 0.0

            # Gleiche Farbe bevorzugen
            if card.color == expected_color:
                score += 6

            # Gleichen Wert bevorzugen
            if card.value == expected_value:
                score += 5

            # Aktionskarten stärker bewerten
            if card.value in (CardValue.SKIP, CardValue.REVERSE):
                score += 3

            if card.value == CardValue.PLUS2:
                score += 4

            if card.value == CardValue.PLUS4:
                score += 3

            # Farbe behalten, von der man viele Karten hat
            counts = color_counts(remaining)
            score += counts.get(chosen_color, 0) * 1.5

            score += basic_bonus

            # Gleiche Werte in der Hand berücksichtigen
            duplicates = sum(1 for c in remaining if c.value == card.value)
            score += duplicates * 0.5

            # Viele spätere Optionen leicht bestrafen
            next_turn_options = 0
            for c in remaining:
                if c.value in (CardValue.NEW_COLOR, CardValue.PLUS4):
                    next_turn_options += 1
                elif c.color == chosen_color or c.value == chosen_value:
                    next_turn_options += 1

            score -= next_turn_options * 1.7

            # Gegner mit wenigen Karten blockieren
            if game_state.hand_sizes_of_other_players:
                next_player_cards = min(game_state.hand_sizes_of_other_players)

                if next_player_cards <= 2:
                    if card.value in (
                        CardValue.SKIP,
                        CardValue.PLUS2,
                        CardValue.PLUS4
                    ):
                        score += 6

                    # Reverse im 1-gegen-1 besonders stark
                    if (
                        len(game_state.hand_sizes_of_other_players) == 1
                        and card.value == CardValue.REVERSE
                    ):
                        score += 6

            # Wildkarten sinnvoll einsetzen
            if isinstance(move, PlayColorChoiceCard):
                score += counts.get(move.new_color, 0) * 1.5

                # Aktuelle Farbe leicht bevorzugen
                if move.new_color == expected_color:
                    score += 1.5

                # +4 nicht verschwenden
                if (
                    card.value == CardValue.PLUS4
                    and expected_color in CARD_COLORS_STANDARD
                ):
                    if any(c.color == expected_color for c in remaining):
                        score -= 1

            return score

        # Zug mit der höchsten Bewertung wählen
        return max(legal_moves, key=move_priority)