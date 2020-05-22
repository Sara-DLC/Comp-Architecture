"""CPU functionality."""
import sys

"""
Binary values listed in spec
"""
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101
ADDI = 0b10101110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.branchtable = {}
        self.branchtable[LDI] = self.ldi_handler
        self.branchtable[PRN] = self.prn_handler
        self.branchtable[HLT] = self.hlt_handler
        self.branchtable[MUL] = self.mul_handler
        self.branchtable[PUSH] = self.push_handler
        self.branchtable[POP] = self.pop_handler
        self.branchtable[CALL] = self.call_handler
        self.branchtable[RET] = self.ret_handler
        self.branchtable[ADD] = self.add_handler
        self.branchtable[CMP] = self.cmp_handler
        self.branchtable[JMP] = self.jmp_handler
        self.branchtable[JNE] = self.jne_handler
        self.branchtable[JEQ] = self.jeq_handler
        self.branchtable[ADDI] = self.addi_handler
        self.running = False
        self.pc = 0  # starts program counter/ instruction pointer
        self.register = [0] * 8  # sets registers R0-R7
        self.ram = [0] * 256  # available memory
        self.pointer = 7  # stack pointer
        # pointing to R7 and setting it F4 per spec
        self.register[self.pointer] = 0xF4
        self.flag = [0] * 8  # sets register flag

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def ldi_handler(self, *argv):
        self.register[argv[0]] = argv[1]
        self.pc += 3

    def prn_handler(self, *argv):
        print(self.register[argv[0]])
        self.pc += 2

    def mul_handler(self, *argv):
        self.alu(MUL, argv[0], argv[1])
        self.pc += 3

    def push_handler(self, *argv):
        self.register[self.pointer] -= 1
        self.ram[self.register[self.pointer]] = self.register[argv[0]]
        self.pc += 2

    def pop_handler(self, *argv):
        stack = self.ram[self.register[self.pointer]]
        self.register[argv[0]] = stack
        self.register[self.pointer] += 1
        self.pc += 2

    def call_handler(self, *argv):
        self.register[self.pointer] -= 1
        self.ram[self.register[self.pointer]] = self.pc + 2

        updated_register = self.ram[self.pc + 1]
        self.pc = self.register[updated_register]

    def ret_handler(self, *argv):
        self.pc = self.ram[self.register[self.pointer]]
        self.register[self.pointer] += 1

    def add_handler(self, *argv):
        self.alu(ADD, argv[0], argv[1])
        self.pc += 3

    def hlt_handler(self, *argv):
        self.running = False
        self.pc += 3

    def cmp_handler(self, *argv):
        self.alu(CMP, argv[0], argv[1])
        self.pc += 3

    def jmp_handler(self, *argv):
        self.pc = self.register[argv[0]]

    def jne_handler(self, *argv):
        if self.flag[-1] == 0:
            self.pc = self.register[argv[0]]
        else:
            self.pc += 2

    def jeq_handler(self, *argv):
        if self.flag[-1] == 1:
            self.pc = self.register[argv[0]]
        else:
            self.pc += 2

    def addi_handler(self, *argv):
        self.alu('ADDI', argv[0], argv[1])
        self.pc += 3

    def load(self, filename):
        """Load a program into memory."""
        address = 0
        try:
            with open(sys.argv[1]) as files:
                # read lines
                for line in files:
                    # go through comments and strip out input and ignore anything after # as they are comments
                    comment = line.strip().split("#")
                    result = comment[0].strip()
                    # ignore blanks
                    if result == "":
                        continue
                    # convert binary string to integer
                    instruction = int(result, 2)
                    # add to memory
                    self.ram[address] = instruction
                    address += 1
        except FileExistsError:
            # exit with error code
            print('File not found')
            sys.exit(1)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == ADD:
            self.register[reg_a] += self.register[reg_b]
        # elif op == "SUB": etc
        elif op == MUL:
            self.register[reg_a] *= self.register[reg_b]
        elif op == CMP:
            if self.register[reg_a] == self.register[reg_b]:
                self.flag[-1] = 1
                self.flag[-2] = 0
                self.flag[-3] = 0
            elif self.register[reg_a] > self.register[reg_b]:
                self.flag[-1] = 0
                self.flag[-2] = 1
                self.flag[-3] = 0
            elif self.register[reg_a] < self.register[reg_b]:
                self.flag[-1] = 0
                self.flag[-2] = 0
                self.flag[-3] = 1
            elif op == ADDI:
                self.register[reg_a] += reg_b
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            instruction = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if instruction in self.branchtable:
                self.branchtable[instruction](operand_a, operand_b)
            else:
                print('Instruction Not Found')
                sys.exit()
