"""CPU functionality."""
import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0  # starts program counter/ instruction pointer
        self.register = [0] * 8  # sets registers R0-R7
        self.ram = [0] * 256  # available memory

    def ram_read(self, read_address):
        MDR = self.ram[read_address]
        return MDR

    def ram_write(self, value, write_address):
        self.ram[write_address] = value
        MAR = value
        return MAR

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

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        # elif op == "SUB": etc
        elif op == MUL:
            self.register[reg_a] *= self.register[reg_b]
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
        while True:
            # set memory to pointer
            instruction = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if instruction == LDI:
                self.register[operand_a] = operand_b
                self.pc += 3
            elif instruction == PRN:
                print(self.register[operand_a])
                self.pc += 2
            elif instruction == MUL:
                self.alu(instruction, operand_a, operand_b)
                self.pc += 3
            elif instruction == HLT:
                break
            else:
                print(f'Not working')
                sys.exit(1)
