"""define the standard UNO cards and the standard UNO deck"""
from dataclasses import dataclass
from enum import Enum, auto

from aux_list import flatten_list, split_at_index

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


UNO_DECK = flatten_list(
    [
        [Card(color, CardValue.ZERO) ] +
        2 * [Card(color, val) for val in CARD_VALUES_ONE_TO_NINE] +
        2 * [Card(color, val) for val in CARD_VALUES_ACTION]
        for color in CARD_COLORS_STANDARD
    ]) + \
    4 * [Card(CardColor.SPECIAL, val) for val in CARD_VALUES_SPECIAL]

assert len(UNO_DECK) == 108, f"expected 108 cards, got {len(UNO_DECK)}"
