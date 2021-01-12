from enum import Enum


class OpCode(Enum):
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


class Modifier(Enum):
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
    A_PREDEC_IND = '{'
    A_POSTDEC_IND = '}'
    B_PREDEC_IND = '<'
    B_POSTDEC_IND = '>'
