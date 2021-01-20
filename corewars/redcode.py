from dataclasses import dataclass
from enum import Enum
from typing import List


class ExtendedEnum(Enum):
    @classmethod
    def keys(cls):
        return list(map(lambda c: c.name, cls))


class OpCode(ExtendedEnum):
    DAT = 0
    MOV = 1
    ADD = 2
    SUB = 3
    MUL = 4
    DIV = 5
    MOD = 6
    JMP = 7
    JMZ = 8
    JMN = 9
    DJN = 10
    CMP = 11
    SEQ = 12
    SNE = 13
    SLT = 14
    SPL = 15
    NOP = 16


class Modifier(ExtendedEnum):
    A = 0
    B = 1
    AB = 2
    BA = 3
    F = 4
    X = 5
    I = 6


class AddressingMode(Enum):
    IMMEDIATE = '#'
    DIRECT = '$'
    A_INDIRECT = '*'
    B_INDIRECT = '@'
    A_PREDEC = '{'
    A_POSTINC = '}'
    B_PREDEC = '<'
    B_POSTINC = '>'


@dataclass
class Instruction():
    op_code: OpCode
    modifier: Modifier
    a_value: int
    a_mode: AddressingMode
    b_value: int
    b_mode: AddressingMode


    def __repr__(self) -> str:
        return self.__str__()


    def __str__(self) -> str:
        return f'{self.op_code.name}.{self.modifier.name} {self.a_mode.value}{self.a_value}, {self.b_mode.value}{self.b_value}'


@dataclass
class Warrior():
    name: str
    instructions: List[Instruction]
