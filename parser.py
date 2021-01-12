from dataclasses import dataclass
from redcode import Modifier, OpCode, AddressingMode


class Parser():
    @staticmethod
    def get_default_modifier(
        op_code: OpCode, a_mode: AddressingMode, b_mode: AddressingMode
    ) -> Modifier:
        """
        Returns the default instruction modifier for the
        given combination of an OpCode and addressing modes.
        Used if modifier is not explicitly specified in the code.
        """
        if op_code in [OpCode.DAT, OpCode.NOP]:
            return Modifier.F
        if op_code in [OpCode.MOV, OpCode.SEQ, OpCode.SNE, OpCode.CMP]:
            if a_mode == AddressingMode.IMMEDIATE:
                return Modifier.AB
            if b_mode == AddressingMode.IMMEDIATE and a_mode != AddressingMode.IMMEDIATE:
                return Modifier.B
            return Modifier.I
        if op_code in [OpCode.ADD, OpCode.SUB, OpCode.MUL, OpCode.DIV, OpCode.MOD]:
            if a_mode == AddressingMode.IMMEDIATE:
                return Modifier.AB
            if b_mode == AddressingMode.IMMEDIATE and a_mode != AddressingMode.IMMEDIATE:
                return Modifier.B
            return Modifier.F
        if op_code in [OpCode.SLT]:
            if a_mode == AddressingMode.IMMEDIATE:
                return Modifier.AB
            else:
                return Modifier.B
        if op_code in [OpCode.JMP, OpCode.JMZ, OpCode.JMN, OpCode.DJN, OpCode.SPL]:
            return Modifier.B
        return None


@dataclass
class Instruction():
    op_code: OpCode
    modifier: Modifier
    a_value: int
    a_mode: AddressingMode
    b_value: int
    b_mode: AddressingMode
