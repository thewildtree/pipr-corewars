from corewars.redcode import OpCode
from corewars.mars import MARS



def test_load_warrior():
    mars = MARS()
    with open('tests/warriors/imp.red') as file:
        imp = file.readlines()
    warriors_data = [imp, imp]
    mars.load_warriors(warriors_data)
    assert mars.core.current_warrior.name == "IMP"
    assert mars.core.warriors_count == 2
    assert any(instruction.op_code == OpCode.MOV for instruction in mars.core)