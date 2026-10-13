import logging
from pathlib import Path
from random import shuffle
from GameState import GameState, GameStatePublic, Player, Move, DrawCard, PlayCard, PlayColorChoiceCard
from UnoDeck import UNO_DECK, Card, CardValue, CardColor

CARD_COUNT_START = 7


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
            #assert len(player.hand) == 0, f"player {player} already has cards"
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

    def run(self, turn_count_max: int = 1000):
        players_str = ', '.join([pl.name for pl in self.game_state.players])
        logging.info(f"starting game with {players_str}")
        turn_count = 0
        players_done = []
        pre_play_msg = None
        while not self.game_state.is_game_over() and turn_count < turn_count_max:
            if pre_play_msg:
                logging.info(pre_play_msg)
            turn_count += 1
            current_player = self.game_state.current_player()
            logging.info(f"turn {turn_count}: {self.game_state.game_state_base} from {current_player.name}")
            game_state_public = GameStatePublic.from_state(self.game_state)
            try:
                move = current_player.play(game_state_public)
                logging.info(f"{current_player.name} tries {move}")
            except Exception as exc:
                logging.warning(f"{current_player.name} error generating move ('{type(exc)}'): {exc}")
                logging.info("  must draw a card")
                move = DrawCard()
            if not self.game_state.is_move_valid(current_player.hand, move):
                logging.warning("  invalid move, must draw a card")
                move = DrawCard()
            pre_play_msg = self.play(current_player, move)
            if len(current_player.hand) > 0:
                hand_str = ', '.join([str(card) for card in current_player.hand])
                logging.info(f"  now holds {hand_str}")
            else:
                logging.info("  done")
                players_done.append((current_player, turn_count))
        return players_done

    def play(self, player:Player, move: Move) -> str:
        after_play_msg = None
        match move:
            case DrawCard():
                card = self.next_card()
                player.hand.append(card)
            case PlayCard(card=card):
                player.hand.remove(card)
                self.played_cards.append(card)
                self.game_state.game_state_base.update_from_move(move)
                if card.value in (CardValue.PLUS2, CardValue.PLUS4):
                    next_player = self.game_state.next_player()
                    card_count = 2 if card.value == CardValue.PLUS2 else 4
                    after_play_msg = f"{next_player.name} draws {card_count} cards"
                    for _ in range(card_count):
                        next_player.hand.append(self.next_card())
                if len(self.game_state.players) >= 2 and card.value == CardValue.SKIP or (
                        len(self.game_state.players) == 2 and card.value == CardValue.REVERSE):
                    self.game_state.move_turn()
                    skipped_player = self.game_state.current_player()
                    after_play_msg = f"{skipped_player.name} skipped"
            case _:
                raise RuntimeError(f"unhandled move '{move}' of type {type(move)}")
        self.game_state.move_turn()
        return after_play_msg


SCRIPT_DIR = Path(__file__).parent
APP_NAME = Path(__file__).stem

def _initializeLogger():
    logging.basicConfig(filename=SCRIPT_DIR / f"{APP_NAME}.log",
        format="%(asctime)-15s\t%(levelname)s\t%(message)s",
        level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())


_initializeLogger()

if __name__ == "__main__":
    players = AIPlayer("Player 1"),AIPlayer("Player 2")
    game = Game(players)
    players_done = game.run()
    players_done_str = ', '.join([f"{pl.name}: {turn_done}" for pl, turn_done in players_done])
    logging.info(f"players done: {players_done_str}")
