from corewars.redcode import AddressingMode, Instruction, Modifier, OpCode, Warrior
from corewars.core import Core, CoreInstruction, CoreWarrior


def test_load_warrior():
    core_size = 8000
    core = Core(core_size)
    warrior = Warrior('test', [
        Instruction(OpCode.MOV, Modifier.B, 0, AddressingMode('$'), 3, AddressingMode('#')),
        Instruction(OpCode.DIV, Modifier.A, 22, AddressingMode('>'), 1, AddressingMode('$')),
    ])
    # tests if loading works properly when having to go 'through' the end of the memory
    core.load_warrior(warrior, core_size - 1)
    assert core.warriors[0].current_pointer == core_size - 1
    assert core[core_size - 1].op_code == OpCode.MOV
    # same as core[0]
    assert core[core_size].op_code == OpCode.DIV


def test_instructions_separate():
    # makes sure instructions aren't all references to the same one
    core = Core(20)
    core[0].op_code = OpCode.MOV
    assert not any(x.op_code == OpCode.MOV for x in core[1:])


def test_instruction_normalized():
    core = Core()
    instruction = Instruction(
        OpCode.CMP, Modifier.A, -2, AddressingMode('$'), -8001, AddressingMode('#'))
    core_instruction = CoreInstruction(core, instruction)
    assert core_instruction.a_value > 0
    assert core_instruction.b_value > 0


def test_process_queue():
    core = Core()
    warrior = CoreWarrior(core, 'test', 1)
    assert warrior.current_pointer == 1
    warrior.add_process(2)
    warrior.add_process(3)
    warrior.turn_next()
    assert warrior.current_pointer == 2
    warrior.kill_current()
    warrior.turn_next()
    assert not any(x == 2 for x in warrior._processes)
    assert warrior.current_pointer == 3
    warrior.turn_next()
    warrior.kill_current()
    warrior.turn_next()
    assert warrior.current_pointer == 3
