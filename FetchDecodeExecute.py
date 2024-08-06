# Comprised of the Fetch, Decode, and Execute portions of the ISA project

import struct

ELF_HEADER_FORMAT = '<4sBBBBB7xHHIIIIIHHHHHH'
ELF_HEADER_SIZE = 52

# Defines the program header structure for 32-bit little-endian RISC-V architecture
PROGRAM_HEADER_FORMAT = '<IIIIIIII'
PROGRAM_HEADER_SIZE = 32

# Constants for checking the ELF file
ELF_MAGIC = b'\x7fELF'
RISC_V_MACHINE = 243
PT_LOAD = 1

class Machine:
    def __init__(self):
        self.memory = bytearray(1024 * 1024)  # Initialize 1MB of memory
        self.registers = [0] * 32
        self.pc = 0  # Program counter
        self.registers[2] = len(self.memory)  # Set the stack pointer to the bottom of the RAM memory
        self.alu = ALU()

    def load_elf(self, filename):
        with open(filename, 'rb') as file:
            # Read ELF Header
            elf_header_data = file.read(ELF_HEADER_SIZE)
            elf_header = struct.unpack(ELF_HEADER_FORMAT, elf_header_data)

            # Verifies ELF Header
            if elf_header[0] != ELF_MAGIC:
                raise ValueError("Not an ELF file")
            if elf_header[10] != 2:
                raise ValueError("Not an executable file")
            if elf_header[11] != RISC_V_MACHINE:
                raise ValueError("Not a RISC-V file")
            if elf_header[4] != 1:
                raise ValueError("Not a 32-bit file")

            e_phoff = elf_header[9]
            e_phnum = elf_header[17]
            e_entry = elf_header[8]

            # Read and progress program headers
            file.seek(e_phoff)
            for _ in range(e_phnum):
                program_header_data = file.read(PROGRAM_HEADER_SIZE)
                program_header = struct.unpack(PROGRAM_HEADER_FORMAT, program_header_data)

                if program_header[0] == PT_LOAD:
                    self.copy_segment(file, program_header)

            # Set the program counter to the entry point
            self.pc = e_entry

    def copy_segment(self, file, program_header):
        p_offset = program_header[1]
        p_vaddr = program_header[2]
        p_filesz = program_header[4]
        p_memsz = program_header[5]

        file.seek(p_offset)
        segment_data = file.read(p_filesz)
        self.memory[p_vaddr:p_vaddr + p_memsz] = segment_data.ljust(p_memsz, b'\x00')

    def fetch(self):
        instruction = struct.unpack('<I', self.memory[self.pc:self.pc + 4])[0]
        return {'inst': instruction}

    def decode(self, fetched_instruction):
        instruction = fetched_instruction['inst']
        opcode = instruction & 0x7f

        decoded_instruction = {
            'inst': instruction,
            'left': None,
            'right': None,
            'disp_strval': None,
            'rd': None,
            'memop': 0,
            'aluop': 'Nop',  # Default ALU operation
        }

        if opcode == 0x33:  # R-type
            decoded_instruction.update({
                'funct7': (instruction >> 25) & 0x7f,
                'rs2': (instruction >> 20) & 0x1f,
                'rs1': (instruction >> 15) & 0x1f,
                'funct3': (instruction >> 12) & 0x7,
                'rd': (instruction >> 7) & 0x1f,
                'left': self.read_register((instruction >> 15) & 0x1f),
                'right': self.read_register((instruction >> 20) & 0x1f)
            })
        elif opcode in [0x03, 0x13, 0x67, 0x73]:  # I-type
            imm = (instruction >> 20) & 0xfff
            decoded_instruction.update({
                'imm': sign_extend(imm, 12),
                'rs1': (instruction >> 15) & 0x1f,
                'funct3': (instruction >> 12) & 0x7,
                'rd': (instruction >> 7) & 0x1f,
                'left': self.read_register((instruction >> 15) & 0x1f),
                'right': sign_extend(imm, 12)
            })
        elif opcode == 0x23:  # S-type
            imm = ((instruction >> 25) << 5) | ((instruction >> 7) & 0x1f)
            decoded_instruction.update({
                'imm': sign_extend(imm, 12),
                'rs2': (instruction >> 20) & 0x1f,
                'rs1': (instruction >> 15) & 0x1f,
                'funct3': (instruction >> 12) & 0x7,
                'left': self.read_register((instruction >> 15) & 0x1f),
                'right': self.read_register((instruction >> 20) & 0x1f)
            })
        elif opcode == 0x63:  # B-type
            imm = ((instruction >> 31) << 12) | (((instruction >> 25) & 0x3f) << 5) | (((instruction >> 8) & 0xf) << 1) | (((instruction >> 7) & 0x1) << 11)
            decoded_instruction.update({
                'imm': sign_extend(imm, 13),
                'rs2': (instruction >> 20) & 0x1f,
                'rs1': (instruction >> 15) & 0x1f,
                'funct3': (instruction >> 12) & 0x7,
                'left': self.read_register((instruction >> 15) & 0x1f),
                'right': self.read_register((instruction >> 20) & 0x1f)
            })
        elif opcode in [0x37, 0x17]:  # U-type
            imm = instruction & 0xfffff000
            decoded_instruction.update({
                'imm': sign_extend(imm, 32),
                'rd': (instruction >> 7) & 0x1f,
                'right': sign_extend(imm, 32)
            })
        elif opcode == 0x6f:  # J-type
            imm = ((instruction >> 31) << 20) | (((instruction >> 21) & 0x3ff) << 1) | (((instruction >> 20) & 0x1) << 11) | ((instruction >> 12) & 0xff)
            decoded_instruction.update({
                'imm': sign_extend(imm, 21),
                'rd': (instruction >> 7) & 0x1f,
                'right': sign_extend(imm, 21)
            })

        return decoded_instruction

    def execute(self, decoded_instruction):
        opcode = decoded_instruction['inst'] & 0x7f
        if opcode == 0x6f:  # JAL instruction
            imm = decoded_instruction['imm']
            decoded_instruction['pc_update'] = self.pc + imm
        else:
            decoded_instruction['pc_update'] = self.pc + 4  # Default PC update for other instructions

        if opcode in [0x03, 0x13, 0x67, 0x73]:  # I-type
            funct3 = decoded_instruction['funct3']
            if opcode == 0x03:  # LOAD
                decoded_instruction['memop'] = 'load'
            elif opcode == 0x13:  # OP-IMM
                decoded_instruction['aluop'] = self.decode_alu_operation(opcode, funct3, 0)
            elif opcode == 0x67:  # JALR
                decoded_instruction['aluop'] = 'jalr'
            elif opcode == 0x73:  # SYSTEM (ECALL)
                if funct3 == 0:
                    decoded_instruction['aluop'] = 'ecall'

        elif opcode == 0x23:  # S-type (STORE)
            decoded_instruction['memop'] = 'store'

        elif opcode == 0x63:  # B-type (BRANCH)
            decoded_instruction['aluop'] = 'Cmp'

        elif opcode == 0x37:  # U-type (LUI)
            decoded_instruction['aluop'] = 'lui'

        elif opcode == 0x17:  # U-type (AUIPC)
            decoded_instruction['aluop'] = 'auipc'

        elif opcode == 0x33:  # R-type
            funct3 = decoded_instruction['funct3']
            funct7 = decoded_instruction['funct7']
            decoded_instruction['aluop'] = self.decode_alu_operation(opcode, funct3, funct7)

        decoded_instruction['result'] = self.alu.perform_operation(decoded_instruction['aluop'], decoded_instruction['left'], decoded_instruction['right'])
        return decoded_instruction

    def memory_access(self, decoded_instruction):
        memop = decoded_instruction['memop']
        if memop == 'load':
            pass
        elif memop == 'store':
            pass

    def writeback(self, decoded_instruction):
        rd = decoded_instruction['rd']
        result = decoded_instruction['result']

    def step(self):
        fetched_instruction = self.fetch()
        decoded_instruction = self.decode(fetched_instruction)
        executed_instruction = self.execute(decoded_instruction)
        self.memory_access(executed_instruction)
        self.writeback(executed_instruction)
        self.pc = executed_instruction['pc_update']  # Update PC after instruction execution

    def read_register(self, reg_num):
        if reg_num == 0:
            return 0
        return self.registers[reg_num]

    def decode_alu_operation(self, opcode, funct3, funct7):
        if opcode == 0x33:  # R-type
            if funct3 == 0x0:
                if funct7 == 0x00:
                    return 'Add'
                elif funct7 == 0x20:
                    return 'Sub'
            elif funct3 == 0x1:
                return 'LeftShift'
            elif funct3 == 0x5:
                if funct7 == 0x00:
                    return 'RightShiftL'
                elif funct7 == 0x20:
                    return 'RightShiftA'
            elif funct3 == 0x2:
                return 'Slt'
            elif funct3 == 0x3:
                return 'SltU'
            elif funct3 == 0x4:
                return 'Xor'
            elif funct3 == 0x6:
                return 'Or'
            elif funct3 == 0x7:
                return 'And'
            elif funct3 == 0x8:
                return 'Mul'
            elif funct3 == 0x9:
                return 'Div'
            elif funct3 == 0xa:
                return 'DivU'
            elif funct3 == 0xb:
                return 'Rem'
            elif funct3 == 0xc:
                return 'RemU'
        elif opcode == 0x13:  # I-type OP-IMM
            if funct3 == 0x0:
                return 'Add'
            elif funct3 == 0x1:
                return 'LeftShift'
            elif funct3 == 0x5:
                if funct7 == 0x00:
                    return 'RightShiftL'
                elif funct7 == 0x20:
                    return 'RightShiftA'
            elif funct3 == 0x2:
                return 'Slt'
            elif funct3 == 0x3:
                return 'SltU'
            elif funct3 == 0x4:
                return 'Xor'
            elif funct3 == 0x6:
                return 'Or'
            elif funct3 == 0x7:
                return 'And'
        elif opcode == 0x63:  # B-type (BRANCH)
            return 'Cmp'
        return 'Nop'

class ALU:
    def __init__(self):
        pass

    def perform_operation(self, operation, operand1, operand2):
        if operation == 'Add':
            return operand1 + operand2
        elif operation == 'Sub':
            return operand1 - operand2
        elif operation == 'Mul':
            return operand1 * operand2
        elif operation == 'Div':
            return operand1 // operand2 if operand2 != 0 else 0  # Handles division by zero
        elif operation == 'DivU':
            return (operand1 % (1 << 32)) // (operand2 % (1 << 32)) if operand2 != 0 else 0
        elif operation == 'Rem':
            return operand1 % operand2 if operand2 != 0 else 0
        elif operation == 'RemU':
            return (operand1 % (1 << 32)) % (operand2 % (1 << 32)) if operand2 != 0 else 0
        elif operation == 'LeftShift':
            return operand1 << operand2
        elif operation == 'RightShiftA':
            return operand1 >> operand2
        elif operation == 'RightShiftL':
            return (operand1 % (1 << 32)) >> operand2
        elif operation == 'Or':
            return operand1 | operand2
        elif operation == 'Xor':
            return operand1 ^ operand2
        elif operation == 'And':
            return operand1 & operand2
        elif operation == 'Slt':
            return 1 if operand1 < operand2 else 0
        elif operation == 'SltU':
            return 1 if (operand1 % (1 << 32)) < (operand2 % (1 << 32)) else 0
        elif operation == 'Cmp':
            result = 0
            if operand1 != operand2:
                result |= 0b01  # NE/EQ
            if operand1 < operand2:
                result |= 0b10  # GE/LT
            if (operand1 % (1 << 32)) < (operand2 % (1 << 32)):
                result |= 0b100  # GEU/LTU
            return result
        return 0

def sign_extend(value, bit_length):
    sign_bit = 1 << (bit_length - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)
