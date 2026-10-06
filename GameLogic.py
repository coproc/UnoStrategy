from random import shuffle
from GameState import GameState, GameStatePublic, Player, Move, DrawCard, PlayCard, PlayColorChoiceCard, Card, CardValue, CardColor, UNO_DECK, CARD_COUNT_START

class AIPlayer(Player):
    def play(self, game_state: GameStatePublic) -> Move:
        for card in self.hand:
            if card.value == game_state.game_state_base.expected_value or card.color == game_state.game_state_base.expected_color:
                return PlayCard(card)

        for card in self.hand:
            if card.value in [CardValue.NEW_COLOR, CardValue.PLUS4]:
                return PlayColorChoiceCard(card, CardColor.RED)

        return DrawCard()


class Game:
    def __init__(self, players: tuple[Player,...]):
        assert len(players) > 0, "need at least one player"
        assert len(players) <= (len(UNO_DECK)-1) // CARD_COUNT_START, "too many players"
        self.game_state = GameState(players = players)
        self.unplayed_cards = UNO_DECK.copy()
        shuffle(self.unplayed_cards)
        self.played_cards: list[Card,...] = []
        self.init_cards()

    def init_cards(self):
        for player in self.game_state.players:
            assert len(player.hand) == 0, f"player {player} already has cards"
            assert len(self.unplayed_cards) >= CARD_COUNT_START, f"not enough cards to start with"
            player.hand = self.unplayed_cards[:CARD_COUNT_START]
            self.unplayed_cards = self.unplayed_cards[len(player.hand):]
        while self.game_state.game_state_base.expected_color is None:
            open_card = self.next_card()
            self.game_state.update_from_card(open_card)
            self.played_cards.append(open_card)

    def next_card(self) -> Card:
        if not self.unplayed_cards:
            self.unplayed_cards = self.played_cards
            self.played_cards = []
            shuffle(self.unplayed_cards)
        return self.unplayed_cards.pop()

    def run(self):
        round_count = 0
        while not self.game_state.is_game_over():
            round_count += 1
            print(f"round {round_count}: {self.game_state.game_state_base}")
            game_state_public = GameStatePublic.from_state(self.game_state)
            current_player = self.game_state.current_player()
            print(current_player)
            move = current_player.play(game_state_public)
            print("  tries ", move)
            if not self.game_state.is_move_valid(current_player.hand, move):
                print("  invalid move, must draw a card")
                move = DrawCard()
            self.play(current_player, move)
            if len(current_player.hand) > 0:
                print("  now holds ", ', '.join([str(card) for card in current_player.hand]))
            else:
                print("  done")

    def play(self, player:Player, move: Move):
        match move:
            case DrawCard():
                card = self.next_card()
                player.hand.append(card)
            case PlayCard(card=card):
                player.hand.remove(card)
                self.played_cards.append(card)
                self.game_state.game_state_base.update_from_move( move)
            case _:
                raise RuntimeError(f"unhandled move '{move}' of type {type(move)}")



if __name__ == "__main__":
    game = Game((AIPlayer("Player 1"),))
    game.run()