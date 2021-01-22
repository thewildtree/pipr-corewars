from typing import List
import re
from .redcode import Instruction, Modifier, OpCode, AddressingMode, Warrior
from .exceptions import ParserException



class Parser():
    @staticmethod
    def parse_warrior(lines: List[str]) -> Warrior:
        """
        Attempts to parse all the provided strings as Redcode instructions of one warrior.
        Returns: a Warrior object upon succeeding, None value otherwise.
        """
        warrior = Warrior(
            name="Warrior",
            instructions=[]
        )
        for i, line in enumerate(lines):
            line = line.strip()
            # comment lines - we should only check for them before the code starts
            # for now let's ignore that check
            if line.startswith(';'):
                data = line.split(maxsplit=1)
                if data[0].lower() == ';name':
                    warrior.name = data[1]
            # actual instruction parsing
            elif line:
                instruction = Parser.parse_instruction(line, i)
                warrior.instructions.append(instruction)
        if warrior.instructions:
            return warrior
        else:
            return None


    @staticmethod
    def parse_instruction(line: str, index: int = 0) -> Instruction:
        """
        Attempts to parse a given line as either a comment or a Redcode instruction.
        Throws exceptions if instructions are found but don't suit a given set of criteria.
        """
        # temporary - uppercase everything
        line = line.upper()
        # instruction regex - pretty basic, but works fine
        # only problem is that it catches post-instruction comments in the last group
        match = re.match(
            r'([a-zA-Z]{3})(?:\s*\.\s*([AaBbFfXxIi]{1,2}))?(?:\s*([#\$\*@\{<\}>])?\s*([^,$]+))?(?:\s*,\s*([#\$\*@\{<\}>])?\s*(.+))?$',
            line
        )
        if not match:
            # throws if line is not empty and is neither a comment nor an instruction
            raise ParserException(index, line, 'Expected a comment or a instruction but none found')

        op_code, modifier, a_mode, a_value, b_mode, b_value = match.groups()
        # opcode
        if op_code not in OpCode.keys():
            raise ParserException(index, line, 'Invalid OpCode')
        else:
            op_code = OpCode[op_code]
        # operand values
        if not a_value:
            raise ParserException(index, line, 'A operand value not specified')
        else:
            # if the b field is not present, we might have a comment 'caught' in the a_value group
            if not b_value:
                a_value = a_value.split()[0]
            a_value = int(a_value)
        # only the DAT, JMP, SPL and NOP opcodes can work without the B operand specified
        if not b_value:
            if op_code not in [OpCode.DAT, OpCode.JMP, OpCode.SPL, OpCode.NOP]:
                raise ParserException(index, line, 'B operand value required but not found')
            elif op_code == OpCode.DAT:
                # "One unusual thing about DAT, a relic of the previous standards, is that if it has only one argument it's placed in the B-field."
                b_value = a_value
                b_mode = a_mode
                a_value = a_mode = None
            else:
                b_value = 0
        else:
            # remove potential comments from the last group (regex problem described above)
            b_value = int(b_value.split()[0])

        # if no addressing mode specified, default is $ (direct) except for DAT opcode - in that case it's # (immediate)
        default_mode = AddressingMode.DIRECT if op_code != OpCode.DAT else AddressingMode.IMMEDIATE
        a_mode = AddressingMode(a_mode) if a_mode else default_mode
        b_mode = AddressingMode(b_mode) if b_mode else default_mode

        # modifier at the end because we need addressing modes to determine the default one
        if modifier is not None and modifier not in Modifier.keys():
            raise ParserException(index, line, 'Invalid modifier')
        elif not modifier:
            modifier = Parser.get_default_modifier(op_code, a_mode, b_mode)
        else:
            modifier = Modifier[modifier]

        return Instruction(
            op_code=op_code,
            modifier=modifier,
            a_value=a_value,
            a_mode=a_mode,
            b_value=b_value,
            b_mode=b_mode
        )


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
