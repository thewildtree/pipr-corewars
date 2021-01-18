from dataclasses import field
from typing import List
from corewars.redcode import AddressingMode, Instruction, Modifier, OpCode, Warrior


def default_dat():
    return Instruction(OpCode.DAT, Modifier.F, 0, AddressingMode('$'), 0, AddressingMode('$'))


class Core():
    def __init__(self, size=8000):
        self._size = size
        self._instructions: List[CoreInstruction]
        self._warriors: List[CoreWarrior]
        self._warrior_index: int
        self.clear()


    def clear(self, default_instruction=default_dat()):
        self._instructions = []
        for _ in range(self._size):
            self._instructions.append(CoreInstruction(self, default_instruction))
        self._warriors = []
        self._warrior_index = 0


    def load_warrior(self, warrior: Warrior, address: int):
        """
        Loads all instructions of the given Warrior into the Core
        starting at the given address.
        """
        if not address:
            # TODO: automatically determine the default address
            address = 2137
        # create initial process for the given warrior
        core_warrior = CoreWarrior(self, warrior.name, address)
        self._warriors.append(core_warrior)
        # load warrior's instructions into core
        for i, instruction in enumerate(warrior.instructions):
            core_instruction = CoreInstruction(self, instruction)
            self[address + i] = core_instruction


    def switch_warrior(self):
        """
        Removes the currently active warrior if it does not have any active processes anymore.
        Changes the 'active' warrior to the next one on the list.
        """
        if len(self.current_warrior) == 0:
            self._remove_current_warrior()
        self._warrior_index = (self._warrior_index + 1) % len(self._warriors)


    @property
    def current_warrior(self):
        return self._warriors[self._warrior_index]


    def normalize_value(self, value: int) -> int:
        "Returns a value converted into the range [0 - coreSize-1]"
        if value >= 0:
            return value % self._size
        while value < 0:
            value += self._size
        return value


    def _remove_current_warrior(self):
        """
        Rremoves the current warrior from the core.
        Requires next_warrior() to be called afterwards to ensure proper behaviour.
        """
        self._warriors.remove(self._warriors[self._warrior_index])
        # in most cases switch backwards (turn_next() will correctly jump to next process afterwards)
        if self._warrior_index != 0:
            self._warrior_index -= 1
        # removing first process - switch to the last one so that turn_next() will circle back to the beginning
        else:
            self._warrior_index = len(self._warriors) - 1


    def __getitem__(self, key):
        if isinstance(key, slice):
            start = 0 if key.start is None else key.start
            stop = self._size if key.stop is None else key.stop
            if start > stop:
                return self._instructions[start:] + self._instructions[:stop]
            else:
                return self._instructions[start:stop]
        else:
            return self._instructions[key % self._size]


    def __setitem__(self, key, value):
        self._instructions[key % self._size] = value


    def __iter__(self):
        return iter(self._instructions)


class CoreInstruction(Instruction):
    """
    A representation of an Instruction used in a given Core.
    Takes the core size into consideration when handling A/B values
    to make sure they stay in the [0 - coreSize-1] range.
    """
    _a_value = field(init=False, repr=False)
    _b_value = field(init=False, repr=False)


    def __init__(self, core: Core, instruction: Instruction):
        self._core = core
        self.op_code = instruction.op_code
        self.modifier = instruction.modifier
        self.a_value = instruction.a_value
        self.a_mode = instruction.a_mode
        self.b_value = instruction.b_value
        self.b_mode = instruction.b_mode


    @property
    def a_value(self) -> int:
        return self._a_value


    @a_value.setter
    def a_value(self, value: int):
        self._a_value = self._core.normalize_value(value)


    @property
    def b_value(self) -> int:
        return self._b_value


    @b_value.setter
    def b_value(self, value: int):
        self._b_value = self._core.normalize_value(value)


class CoreWarrior():
    """
    Represents an instance of a program (warrior) running in the Core.
    Acts as a basic process queue, keeping track of which one of its processes
    is supposed to be executed in the next turn.
    """
    def __init__(self, core: Core, name: str, initial_address: int):
        self.name = name
        self._core = core
        self._current_index = 0
        self._processes: List[int] = []
        # a list of integers - each one is an instruction pointer for one process
        # pointers contain absolute Core memory addresses.
        self.add_process(initial_address)


    def __len__(self):
        return len(self._processes)


    def next_process(self):
        self._current_index = (self._current_index + 1) % len(self._processes)


    def add_process(self, starting_address: int):
        """
        Creates a new process with its pointer set to the given address.
        It is then added to the last position of the queue.
        """
        self._processes.append(self._core.normalize_value(starting_address))


    def kill_current(self):
        """
        Simply removes the current proccess from the list.
        Requires turn_next() to be called afterwards to ensure proper behaviour.
        """
        self._processes.remove(self._processes[self._current_index])
        # in most cases switch backwards (turn_next() will correctly jump to next process afterwards)
        if self._current_index != 0:
            self._current_index -= 1
        # removing first process - switch to the last one so that turn_next() will circle back to the beginning
        else:
            self._current_index = len(self._processes) - 1


    @property
    def current_pointer(self) -> int:
        "Returns an instruction pointer of the process currently being executed."
        return self._processes[self._current_index]


    @current_pointer.setter
    def current_pointer(self, value: int):
        # in case we're at coreSize-1 and increment, for example
        self._processes[self._current_index] = self._core.normalize_value(value)
