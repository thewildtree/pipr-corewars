import pytest
from corewars.redcode import AddressingMode, Instruction, Modifier, OpCode
from corewars.parser import Parser
from corewars.exceptions import ParserException


def test_instruction_parse():
    line = 'MOV.i {0, }0'
    desired_instruction = Instruction(
        OpCode.MOV,
        Modifier.I,
        0,
        AddressingMode('{'),
        0,
        AddressingMode('}')
    )
    assert_parsed_correctly(line, desired_instruction)


def test_instruction_default_modifier():
    line = 'ADD <2, #-1'
    desired_instruction = Instruction(
        OpCode.ADD,
        Modifier.B,
        2,
        AddressingMode('<'),
        -1,
        AddressingMode('#')
    )
    assert_parsed_correctly(line, desired_instruction)


def test_instruction_default_mode():
    line = 'SUB.x -5, -3'
    desired_instruction = Instruction(
        OpCode.SUB,
        Modifier.X,
        -5,
        AddressingMode('$'),
        -3,
        AddressingMode('$')
    )
    assert_parsed_correctly(line, desired_instruction)


def test_instruction_all_defaults():
    line = 'NOP 2, 3'
    desired_instruction = Instruction(
        OpCode.NOP,
        Modifier.F,
        2,
        AddressingMode('$'),
        3,
        AddressingMode('$')
    )
    assert_parsed_correctly(line, desired_instruction)


def test_instruction_missing_b_field():
    with pytest.raises(ParserException):
        line = 'JMZ 2'
        Parser.parse_instruction(line)


def assert_parsed_correctly(line: str, instruction: Instruction):
    parsed_instruction = Parser.parse_instruction(line)
    assert parsed_instruction == instruction
