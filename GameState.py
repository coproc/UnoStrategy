from dataclasses import dataclass, field

from UnoDeck import Card, CardColor, CardValue, CARD_COLORS_STANDARD

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
    turn_index: int = 0
    game_state_base: GameStateBase = field(default_factory=GameStateBase)

    def next_turn(self):
        next_turn_index = self.turn_index
        for _ in range(len(self.players)-1):
            play_dir_incr = 1 if not self.game_state_base.reversed else -1
            next_turn_index += play_dir_incr
            next_turn_index %= len(self.players)
            if len(self.players[next_turn_index].hand) > 0:
                break
        return next_turn_index

    def move_turn(self):
        self.turn_index = self.next_turn()

    def current_player(self) -> Player:
        return self.players[self.turn_index]

    def next_player(self) -> Player:
        return self.players[self.next_turn()]

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
