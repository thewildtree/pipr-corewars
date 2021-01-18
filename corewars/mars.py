from copy import copy
import operator
from random import randint, randrange, shuffle
from corewars.redcode import AddressingMode, Warrior
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


    def cycle(self):
        """
        Runs one simulation cycle - executes one task of the currently active warrior.
        """
        temp_pointer: int = 0 # used for keeping addresses in case we need to post-increment
        # determine the current warrior
        warrior = self.core.current_warrior
        # determine address of the instruction that we want to execute
        inst_pointer = warrior.current_pointer
        # copy it to the instruction register
        inst_reg = copy(self.core[inst_pointer])
        # evaluating the A operand
        if inst_reg.a_mode == AddressingMode.IMMEDIATE:
            # immediate operand values are always evaluated as an address of 0
            a_pointer = 0
        else:
            a_pointer = inst_reg.a_value
            # indirect modes - we need to calculate the actual address of the source instruction
            if inst_reg.a_mode != AddressingMode.DIRECT:
                # first, save the current pointer in case it's needed for post-increments
                temp_pointer = inst_pointer + a_pointer
                # pre-decrement if necessary
                if inst_reg.a_mode == AddressingMode.A_PREDEC:
                    self.core[temp_pointer].a_value -= 1
                elif inst_reg.a_mode == AddressingMode.B_PREDEC:
                    self.core[temp_pointer].b_value -= 1
                # determine the address of our actual source (A) instruction
                if inst_reg.a_mode in [AddressingMode.A_PREDEC, AddressingMode.A_POSTINC, AddressingMode.A_INDIRECT]:
                    a_pointer = a_pointer + self.core[temp_pointer].a_value
                # B-addresing modes
                else:
                    a_pointer = a_pointer + self.core[temp_pointer].b_value
        # copy source instruction to register
        source_reg = copy(self.core[inst_pointer + a_pointer])
        # post-increment if necessary
        if inst_reg.a_mode == AddressingMode.A_POSTINC:
            self.core[temp_pointer].a_value += 1
        elif inst_reg.a_mode == AddressingMode.B_POSTINC:
            self.core[temp_pointer].b_value += 1
        # evaluating the A operand - almost identical to B
        if inst_reg.b_mode == AddressingMode.IMMEDIATE:
            # immediate operand values are always evaluated as an address of 0
            b_pointer = 0
        else:
            b_pointer = inst_reg.b_value
            # indirect modes - we need to calculate the actual address of the source instruction
            if inst_reg.b_mode != AddressingMode.DIRECT:
                # first, save the current pointer in case it's needed for post-increments
                temp_pointer = inst_pointer + b_pointer
                # pre-decrement if necessary
                if inst_reg.b_mode == AddressingMode.A_PREDEC:
                    self.core[temp_pointer].a_value -= 1
                elif inst_reg.b_mode == AddressingMode.B_PREDEC:
                    self.core[temp_pointer].b_value -= 1
                # determine the address of our actual source (A) instruction
                if inst_reg.b_mode in [AddressingMode.A_PREDEC, AddressingMode.A_POSTINC, AddressingMode.A_INDIRECT]:
                    b_pointer = b_pointer + self.core[temp_pointer].a_value
                # B-addresing modes
                else:
                    b_pointer = b_pointer + self.core[temp_pointer].b_value
        # copy source instruction to register
        dest_reg = copy(self.core[inst_pointer + b_pointer])
        # post-increment if necessary
        if inst_reg.a_mode == AddressingMode.A_POSTINC:
            self.core[temp_pointer].a_value += 1
        elif inst_reg.a_mode == AddressingMode.B_POSTINC:
            self.core[temp_pointer].b_value += 1

