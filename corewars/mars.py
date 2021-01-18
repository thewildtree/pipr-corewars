from copy import copy
from random import randint, randrange, shuffle
from corewars.redcode import Warrior
from typing import List
from corewars.core import Core
from corewars.parser import Parser


class MARS():
    """
    Memory Array Redcode Simulator - represents a single Core Wars simulation environment.
    """
    def __init__(self):
        self.core = Core()


    def load_warriors(self, data_arrays: List[List[str]]):
        """
        Parses each of the provided arrays as separate warriors and loads them into the Core.
        """
        warriors: List[Warrior] = []
        for warrior_data in data_arrays:
            warrior = Parser.parse_warrior(warrior_data)
            if warrior:
                warriors.append(warrior)
        spacing = self.core.size // len(warriors)
        starting_address = randrange(0, self.core.size)
        # randomize order in which warriors are loaded
        shuffle(warriors)
        for i, warrior in enumerate(warriors):
            # add small random offset to each starting address
            spacing_offset = randint(-50, 50)
            address = starting_address + i * (spacing + spacing_offset)
            self.core.load_warrior(warrior, address)

