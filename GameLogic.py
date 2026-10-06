from dataclasses import dataclass, field
from enum import Enum, auto
from random import shuffle

CARD_COUNT_START = 7

class CardColor(Enum):
    RED = 1
    YELLOW = 2
    GREEN = 3
    BLUE = 4
    SPECIAL = 5

CARD_COLORS_STANDARD = [CardColor.RED, CardColor.YELLOW, CardColor.GREEN, CardColor.BLUE]

class CardValue(Enum):
    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    REVERSE = auto()
    SKIP = auto()
    PLUS2 = auto()
    PLUS4 = auto()
    NEW_COLOR = auto()

    def __str__(self):
        if 0 <= self.value <= 9:
            return str(self.value)
        return self.name


CARD_VALUES_ONE_TO_NINE = [CardValue(val) for val in range(1,10)]
CARD_VALUES_ACTION = [CardValue.REVERSE, CardValue.SKIP, CardValue.PLUS2]
CARD_VALUES_SPECIAL = [CardValue.NEW_COLOR, CardValue.PLUS4]

@dataclass
class Card:
    color: CardColor
    value: CardValue

    def __str__(self):
        if self.color == CardColor.SPECIAL:
            return f"{self.value}"
        return f"{self.color.name}-{self.value}"


def flatten_list(nested_list: list[list]) -> list:
    return sum(nested_list, [])

def split_at_index(data: list|tuple, index: int) -> tuple[list|tuple, list|tuple]:
    return data[:index], data[index:]

UNO_DECK = flatten_list(
    [
        [Card(color, CardValue.ZERO) ] +
        2 * [Card(color, val) for val in CARD_VALUES_ONE_TO_NINE] +
        2 * [Card(color, val) for val in CARD_VALUES_ACTION]
        for color in CARD_COLORS_STANDARD
    ]) + \
    4 * [Card(CardColor.SPECIAL, val) for val in CARD_VALUES_SPECIAL]

assert len(UNO_DECK) == 108, f"expected 108 cards, got {len(UNO_DECK)}"

class DrawCard:
    def __str__(self):
        return "draw card"

@dataclass
class PlayCard:
    card: Card

    def __str__(self):
        return f"play {self.card}"

@dataclass
class PlayColorChoiceCard(PlayCard):
    new_color: CardColor

    def __str__(self):
        return f"play {self.card} as {self.new_color}"

Move = DrawCard | PlayCard | PlayColorChoiceCard

@dataclass(slots=True)
class Player:
    name: str
    hand: list[Card,...] = field(default_factory=list)

    def __str__(self):
        return f"{self.name}: {', '.join([str(card) for card in self.hand])}"


@dataclass(slots=True)
class GameStateBase:
    reversed: bool = False
    expected_color: CardColor | None = None
    expected_value: CardValue | None = None

    def update_expectation(self, data: Move | Card) -> None:
        match data:
            case Card():
                self.update_from_card(data)
            case Move():
                self.update_from_move(data)

    def update_from_card(self, card: Card) -> None:
        self.expected_value = card.value
        self.expected_color = card.color if card.color in CARD_COLORS_STANDARD else None
        if card.value == CardValue.REVERSE:
            self.reversed = not self.reversed

    def update_from_move(self, move: Move) -> None:
        match move:
            case DrawCard():
                pass
            case PlayColorChoiceCard():
                self.expected_value = None
                self.expected_color = move.new_color
            case PlayCard():
                self.expected_value = move.card.value
                self.expected_color = move.card.color
            case _:
                raise RuntimeError(f"unhandled move '{move}' of type {type(move)}")

    def is_move_valid(self, hand: list[Card], move: Move) -> bool:
        match move:
            case DrawCard():
                return True
            case PlayColorChoiceCard(card=card):
                if card.value == CardValue.PLUS4:
                    return self.expected_color not in [card.color for card in hand]
                return True
            case PlayCard(card=card):
                return self.expected_color == card.color or self.expected_value == card.value
            case _:
                raise RuntimeError(f"unhandled move '{move}' of type {type(move)}")

    def __str__(self):
        expected_str = f"expected {self.expected_color.name}"
        if self.expected_value is not None:
            expected_str += " or " + str(self.expected_value)
        reversed_str = ", reversed" if self.reversed else ""
        return expected_str + reversed_str


@dataclass
class GameState:
    players: tuple[Player, ...]
    turn_index: int = -1
    game_state_base: GameStateBase = field(default_factory=GameStateBase)

    def current_player(self) -> Player:
        for _ in range(len(self.players)-1):
            play_dir_incr = 1 if not self.game_state_base.reversed else -1
            self.turn_index = (self.turn_index + play_dir_incr) % len(self.players)
            if len(self.players[self.turn_index].hand) > 0:
                break
        return self.players[self.turn_index]

    def update_from_card(self, card: Card):
        self.game_state_base.update_from_card(card)

    def is_move_valid(self, hand:list, move: Move):
        return self.game_state_base.is_move_valid(hand, move)

    def is_game_over(self) -> bool:
        if len(self.players) == 1:
            return len(self.players[0].hand) == 0
        return len([p for p in self.players if len(p.hand) > 0]) == 1


@dataclass(slots=True)
class GameStatePublic:
    hand_sizes: tuple[int, ...]
    game_state_base: GameStateBase = field(default_factory=GameStateBase)

    @classmethod
    def from_state(cls, state:GameState):
        return cls(game_state_base=state.game_state_base, hand_sizes=tuple(len(player.hand) for player in state.players))

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
        while not self.game_state.is_game_over():
            print(self.game_state.game_state_base)
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