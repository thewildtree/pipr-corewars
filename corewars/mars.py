from copy import copy
import operator
from random import randint, randrange, shuffle
from corewars.redcode import AddressingMode, Instruction, Modifier, OpCode, Warrior
from typing import List
from corewars.core import Core
from corewars.parser import Parser


class MARS():
    """
    Memory Array Redcode Simulator - represents a single Core Wars simulation environment.
    """
    def __init__(self):
        self.core = Core()


    def load_warriors(self, data_arrays: List[List[str]], starting_address: int = None):
        """
        Parses each of the provided arrays as separate warriors and loads them into the Core.
        """
        warriors: List[Warrior] = []
        for warrior_data in data_arrays:
            warrior = Parser.parse_warrior(warrior_data)
            if warrior:
                warriors.append(warrior)
        spacing = self.core.size // len(warriors)
        if starting_address is None:
            starting_address = randrange(0, self.core.size)
        # randomize order in which warriors are loaded
        shuffle(warriors)
        for i, warrior in enumerate(warriors):
            # add small random offset to each starting address apart from the 1st one
            spacing_offset = 0 if i == 0 else randint(-50, 50)
            address = starting_address + i * (spacing + spacing_offset)
            self.core.load_warrior(warrior, address)


    def cycle(self) -> List[int]:
        """
        Runs one simulation cycle - executes one task of the currently active warrior.
        Returns addresses of core cells that were accessed during the cycle.
        """
        temp_pointer: int = 0 # used for keeping addresses in case we need to post-increment
        cells_written = [] # keeps track of what cells we've written data to
        # determine the current warrior
        warrior = self.core.current_warrior
        if not warrior:
            return
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
                    cells_written.append(temp_pointer)
                elif inst_reg.a_mode == AddressingMode.B_PREDEC:
                    self.core[temp_pointer].b_value -= 1
                    cells_written.append(temp_pointer)
                # determine the address of our actual source (A) instruction
                if inst_reg.a_mode in [AddressingMode.A_PREDEC, AddressingMode.A_POSTINC, AddressingMode.A_INDIRECT]:
                    a_pointer = a_pointer + self.core[temp_pointer].a_value
                # B-addresing modes
                else:
                    a_pointer = a_pointer + self.core[temp_pointer].b_value
        # copy source instruction to register
        source_address = inst_pointer + a_pointer
        source_reg = copy(self.core[source_address])
        # post-increment if necessary
        if inst_reg.a_mode == AddressingMode.A_POSTINC:
            self.core[temp_pointer].a_value += 1
            cells_written.append(temp_pointer)
        elif inst_reg.a_mode == AddressingMode.B_POSTINC:
            self.core[temp_pointer].b_value += 1
            cells_written.append(temp_pointer)
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
                    cells_written.append(temp_pointer)
                elif inst_reg.b_mode == AddressingMode.B_PREDEC:
                    self.core[temp_pointer].b_value -= 1
                    cells_written.append(temp_pointer)
                # determine the address of our actual source (A) instruction
                if inst_reg.b_mode in [AddressingMode.A_PREDEC, AddressingMode.A_POSTINC, AddressingMode.A_INDIRECT]:
                    b_pointer = b_pointer + self.core[temp_pointer].a_value
                # B-addresing modes
                else:
                    b_pointer = b_pointer + self.core[temp_pointer].b_value
        # copy source instruction to register
        dest_address = inst_pointer + b_pointer
        dest_reg = copy(self.core[dest_address])
        # for simplicity let's assume that the destination address is always written to
        cells_written.append(dest_address)
        # post-increment if necessary
        if inst_reg.b_mode == AddressingMode.A_POSTINC:
            self.core[temp_pointer].a_value += 1
            cells_written.append(temp_pointer)
        elif inst_reg.b_mode == AddressingMode.B_POSTINC:
            self.core[temp_pointer].b_value += 1
            cells_written.append(temp_pointer)

        # actual execution phase
        op_code, modifier = inst_reg.op_code, inst_reg.modifier
        # increment current process' pointer (might be overwritten by a JMP instruction)
        self.core.current_warrior.current_pointer += 1
        if op_code == OpCode.DAT:
            # kills the current process
            self.core.current_warrior.kill_current_process()
        elif op_code == OpCode.MOV:
            if modifier == Modifier.A:
                self.core[dest_address].a_value = source_reg.a_value
            elif modifier == Modifier.B:
                self.core[dest_address].b_value = source_reg.b_value
            elif modifier == Modifier.AB:
                self.core[dest_address].b_value = source_reg.a_value
            elif modifier == Modifier.BA:
                self.core[dest_address].a_value = source_reg.b_value
            elif modifier == Modifier.F:
                self.core[dest_address].a_value = source_reg.a_value
                self.core[dest_address].b_value = source_reg.b_value
            elif modifier == Modifier.X:
                self.core[dest_address].a_value = source_reg.b_value
                self.core[dest_address].b_value = source_reg.a_value
            elif modifier == Modifier.I:
                # moves the whole instruction instead of just its operand values
                self.core[dest_address] = source_reg
        elif op_code == OpCode.ADD:
            self._perform_math(operator.add, dest_address, modifier, source_reg, dest_reg)
        elif op_code == OpCode.SUB:
            self._perform_math(operator.sub, dest_address, modifier, source_reg, dest_reg)
        elif op_code == OpCode.MUL:
            self._perform_math(operator.mul, dest_address, modifier, source_reg, dest_reg)
        elif op_code == OpCode.DIV:
            try:
                self._perform_math(operator.floordiv, dest_address, modifier, source_reg, dest_reg)
            except ZeroDivisionError:
                self.core.current_warrior.kill_current_process()
        elif op_code == OpCode.MOD:
            try:
                self._perform_math(operator.mod, dest_address, modifier, source_reg, dest_reg)
            except ZeroDivisionError:
                self.core.current_warrior.kill_current_process()
        elif op_code == OpCode.JMP:
            # address from the A operand
            self.core.current_warrior.current_pointer = source_address
        elif op_code == OpCode.JMZ:
            if self._should_jump(modifier, dest_reg):
                self.core.current_warrior.current_pointer = source_address
        elif op_code == OpCode.JMN:
            if not self._should_jump(modifier, dest_reg):
                self.core.current_warrior.current_pointer = source_address
        elif op_code == OpCode.DJN:
            # decrement necessary values in the core and re-fetch them to the dest. register
            if modifier in [Modifier.A, Modifier.BA, Modifier.X, Modifier.F, Modifier.I]:
                self.core[dest_address].a_value -= 1
            if modifier in [Modifier.B, Modifier.AB, Modifier.X, Modifier.F, Modifier.I]:
                self.core[dest_address].b_value -= 1
            dest_reg = copy(self.core[dest_address])
            if not self._should_jump(modifier, dest_reg):
                self.core.current_warrior.current_pointer = source_address
        elif op_code in [OpCode.SEQ, OpCode.CMP]:
            self._perform_skip(operator.eq, modifier, source_reg, dest_reg)
        elif op_code == OpCode.SNE:
            self._perform_skip(operator.ne, modifier, source_reg, dest_reg)
        elif op_code == OpCode.SLT:
            self._perform_skip(operator.lt, modifier, source_reg, dest_reg)
        elif op_code == OpCode.SPL:
            # adds a new process to the currently active warrior
            # it will be executed the next time that warrior is active
            self.core.current_warrior.add_process(source_address)
        elif op_code == OpCode.NOP:
            pass
        # move to the next warrior (automatically kills ones without any processes left)
        self.core.rotate_warrior()
        # return address written to during execution
        return cells_written


    def _perform_math(
        self, opr: operator, address: int, modifier: Modifier, src_reg: Instruction, dest_reg: Instruction
    ):
        """
        Performs an arithmetical operation using the given operator.
        Saves the result of said operation at the given address in the Core.
        """
        if modifier == Modifier.A:
            self.core[address].a_value = opr(dest_reg.a_value, src_reg.a_value)
        elif modifier == Modifier.B:
            self.core[address].b_value = opr(dest_reg.b_value, src_reg.b_value)
        elif modifier == Modifier.AB:
            self.core[address].b_value = opr(dest_reg.b_value, src_reg.a_value)
        elif modifier == Modifier.BA:
            self.core[address].a_value = opr(dest_reg.a_value, src_reg.b_value)
        elif modifier in [Modifier.F, Modifier.I]:
            # combined A and B modifiers
            self.core[address].a_value = opr(dest_reg.a_value, src_reg.a_value)
            self.core[address].b_value = opr(dest_reg.b_value, src_reg.b_value)
        elif modifier == Modifier.X:
            # combined AB and BA
            self.core[address].b_value = opr(dest_reg.b_value, src_reg.a_value)
            self.core[address].a_value = opr(dest_reg.a_value, src_reg.b_value)


    def _perform_skip(self, opr: operator, modifier: Modifier, src_reg: Instruction, dest_reg: Instruction):
        if self._should_skip(opr, modifier, src_reg, dest_reg):
            self.core.current_warrior.current_pointer += 1

    def _should_skip(
        self, opr: operator, modifier: Modifier, src_reg: Instruction, dest_reg: Instruction
    ) -> bool:
        """
        Performs a comparison with a given operator.
        Used when executing SEQ/CMP, SLT and SNE instructions.
        Returns whether the instruction skip should be performed.
        """
        if modifier == Modifier.A:
            return opr(src_reg.a_value, dest_reg.a_value)
        elif modifier == Modifier.B:
            return opr(src_reg.b_value, dest_reg.b_value)
        elif modifier == Modifier.AB:
            return opr(src_reg.a_value, dest_reg.b_value)
        elif modifier == Modifier.BA:
            return opr(src_reg.b_value, dest_reg.a_value)
        elif modifier == Modifier.F:
            return (opr(src_reg.a_value, dest_reg.a_value) and
                    opr(src_reg.b_value, dest_reg.b_value))
        elif modifier == Modifier.X:
            return (opr(src_reg.a_value, dest_reg.b_value) and
                    opr(src_reg.b_value, dest_reg.a_value))
        elif modifier == Modifier.I:
            return src_reg == dest_reg


    def _should_jump(self, modifier: Modifier, dest_reg: Instruction) -> bool:
        if modifier in [Modifier.A, Modifier.BA]:
            return dest_reg.a_value == 0
        elif modifier in [Modifier.B, Modifier.AB]:
            return dest_reg.b_value == 0
        else:
            # F, X and I modifiers
            return dest_reg.a_value == dest_reg.b_value == 0
