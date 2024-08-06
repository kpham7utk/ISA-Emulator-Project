class WriteBack:
    def __init__(self, machine):
        self.machine = machine
        self.syscall = SystemCall(machine)

    def writeback(self, decoded_instruction):
        rd = decoded_instruction['rd']
        result = decoded_instruction['result']

        if rd == 0:  # Writes to x0 are discarded
            return

        if decoded_instruction['inst'] & 0x7f == 0x73:
            self.syscall.ecall()
        else:
            if rd is not None:
                self.machine.registers[rd] = result

    def update_pc(self, decoded_instruction):
        inst = decoded_instruction['inst']
        opcode = inst & 0x7f
        current_pc = self.machine.pc

        # JAL or JALR
        if opcode in {0x6f, 0x67}:  # 0x6f for JAL and 0x67 for JALR
            self.machine.pc = decoded_instruction['result']  # Result contains target address

        # BRANCH
        elif opcode == 0x63:
            if decoded_instruction['branch_taken']:
                self.machine.pc = current_pc + decoded_instruction['imm']  # imm contains the branch target offset
            else:
                self.machine.pc = current_pc + 4  # Next instruction

        # Non-BRANCH or Non-JUMP
        else:
            self.machine.pc = current_pc + 4

class SystemCall:
    def __init__(self, machine):
        self.machine = machine

    def ecall(self):
        a7 = self.machine.registers[17]  # x17 holds the syscall number
        if a7 == 0:
            self.exit()
        elif a7 == 1:
            self.putchar()
        elif a7 == 2:
            self.getchar()
        elif a7 == 3:
            self.debug()
        else:
            raise ValueError("Unknown system call")

    def exit(self):
        exit_code = self.machine.registers[10]  # x10 holds the exit code
        print(f"Exit with code {exit_code}")
        exit(exit_code)

    def putchar(self):
        char = chr(self.machine.registers[10])  # x10 holds the character to print
        print(char, end='')

    def getchar(self):
        char = input("Input a character: ")[0]
        self.machine.registers[10] = ord(char)  # Store the character in x10

    def debug(self):
        print("Debug system call")