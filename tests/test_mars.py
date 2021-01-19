from typing import List
from corewars.redcode import OpCode
from corewars.mars import MARS

# where MARS loads up the warrior by default
ADDRESS = 0

def test_load_warrior():
    mars = MARS()
    with open('tests/warriors/imp.red') as file:
        imp = file.readlines()
    warriors_data = [imp, imp]
    mars.load_warriors(warriors_data)
    assert mars.core.current_warrior.name == "IMP"
    assert mars.core.warriors_count == 2
    assert any(instruction.op_code == OpCode.MOV for instruction in mars.core)


def get_mars_with_warrior(data: List[str]) -> MARS:
    mars = MARS()
    mars.load_warriors([data], ADDRESS)
    return mars


def test_instruction_dat():
    # tests whether dat A and B values are still evaluated
    # despite the instruction killing the active process
    data = ['DAT.F 1, <1', 'DAT.F 1, 1']
    mars = get_mars_with_warrior(data)
    mars.cycle()
    assert mars.core[ADDRESS + 1].b_value == 0
    # check if warrior has been killed after executing DAT
    assert mars.core.warriors_count == 0


def test_instruction_spl():
    data = ['SPL 0']
    mars = get_mars_with_warrior(data)
    assert len(mars.core.current_warrior) == 1
    # SPL call is executed
    mars.cycle()
    assert len(mars.core.current_warrior) == 2
    # ensure the first process is still active (new process has to 'wait' 1 cycle)
    assert mars.core.current_warrior.current_pointer == 1
    # new process is executed
    mars.cycle()
    assert mars.core.current_warrior.current_pointer == 0


def test_imp():
    with open('tests/warriors/imp.red') as file:
        imp = file.readlines()
    mars = get_mars_with_warrior(imp)
    assert mars.core[ADDRESS] != mars.core[ADDRESS + 1]
    mars.cycle()
    assert mars.core[ADDRESS] == mars.core[ADDRESS + 1]


def test_dwarf():
    # tests behaviour of one of the basic warriors - the Dwarf
    # basically drops DATs every 4 instructions
    with open('tests/warriors/dwarf.red') as file:
        dwarf = file.readlines()
    mars = get_mars_with_warrior(dwarf)
    mars.cycle()
    assert mars.core[ADDRESS + 3].b_value == 4
    mars.cycle()
    assert mars.core[ADDRESS + 7] == mars.core[ADDRESS + 3]
    mars.cycle()
    assert mars.core.current_warrior.current_pointer == 0
    mars.cycle()
    assert mars.core[ADDRESS + 3].b_value == 8
    mars.cycle()
    assert mars.core[ADDRESS + 11] == mars.core[ADDRESS + 3]
