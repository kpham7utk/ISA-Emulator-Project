# COSC 530 ISA Emulator
# by Khoa Pham
# Machine Part 1

class RV32IMEmulator:
    def __init__(self):
        # 32, 32-bit registers (x0 - x31)
        self.registers = [0] * 32
        # Program counter register (PC)
        self.pc = 0
        # 1 mebibyte of RAM
        self.ram = [0] * (1 * 1024 * 1024)
        # Initialize the ALU
        self.alu = ALU()

    def fetch(self):
        # Fetches the next instruction from RAM using the program counter
        # Combine four bytes from RAM into a 32-bit instruction
        # The instruction is stored in little-endian format, so need to read 4 consecutive bytes
        # from the RAM and combine them into a single 32-bit integer
        instruction = (self.ram[self.pc] << 24) | (self.ram[self.pc + 1] << 16) | (self.ram[self.pc + 2] << 8) | self.ram[self.pc + 3]

        # Update the program counter to point to the next instruction.
        # In RISC-V, instructions are always 4 bytes long, so increment the PC by 4.
        self.pc += 4
        return instruction

    def decode(self, instruction):
        # TBA: Decode the instruction
        # decoded_instruction = {'instruction' : instruction}
        return instruction

    def execute(self, decoded_instruction):
        # TBA: Execute the instruction using the ALU
        pass

    def memory(self, decoded_instruction):
        # TBA: Handle memory access
        pass

    def writeback(self, decoded_instruction):
        # Writes results back to registers or memory
        # Assuming decoded_instruction contains destination register (rd) and result
        rd = decoded_instruction['rd']
        result = decoded_instruction['result']
        
        # Ensure writes to x0 are discarded
        if rd != 0:
            self.registers[rd] = result

    def step(self):
        # Performs a single cycle of the execution pipeline
        # Just an outline currently
        instruction = self.fetch()
        decoded_instruction = self.decode(instruction)
        self.execute(decoded_instruction)
        self.memory(decoded_instruction)
        self.writeback(decoded_instruction)

    def read_register(self, reg_num):
        # Reads from the specified register, returning 0 for x0
        if reg_num == 0:
            return 0
        return self.registers[reg_num]
    
    def sign_extend(value, bit_length):
        # Calculate the position of the sign bit based on bit_length.
        # The sign bit is the highest bit in the specified bit length.
        sign_bit = 1 << (bit_length - 1)
        # If the sign bit is set, it means the value is negative.
        # The expression (value & sign_bit) will isolate the sign bit.
        # The expression (value & (sign_bit - 1)) masks out the sign bit, leaving the remaining bits of the value
        # Subtracting the sign bit from the masked value effectively performs the sign extension
        return (value & (sign_bit - 1)) - (value & sign_bit)


class ALU:
    def __init__(self):
        pass

    def perform_operation(self, operation, operand1, operand2):
        # TBA: Perform ALU operations based on the opcode
        result = 0
        return result
