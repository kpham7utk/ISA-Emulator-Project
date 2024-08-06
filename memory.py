import struct

class MemoryStage:
    def __init__(self, memory):
        self.memory = memory

    def load(self, address, size, signed=True):
        data = self.memory[address:address + size]
        if size == 1:  # lb or lbu
            value = struct.unpack('<b' if signed else '<B', data)[0]
        elif size == 2:  # lh or lhu
            value = struct.unpack('<h' if signed else '<H', data)[0]
        elif size == 4:  # lw
            value = struct.unpack('<i', data)[0]
        return value

    def store(self, address, size, value):
        if size == 1:  # sb
            data = struct.pack('<B', value & 0xFF)
        elif size == 2:  # sh
            data = struct.pack('<H', value & 0xFFFF)
        elif size == 4:  # sw
            data = struct.pack('<I', value & 0xFFFFFFFF)
        self.memory[address:address + size] = data

class Machine:
    def __init__(self):
        self.memory = bytearray(1024 * 1024)
        self.registers = [0] * 32
        self.pc = 0
        self.registers[2] = len(self.memory)  # Set the stack pointer to the bottom of the RAM memory
        self.alu = ALU()
        self.memory_stage = MemoryStage(self.memory)

    def memory_access(self, decoded_instruction):
        memop = decoded_instruction['memop']
        address = decoded_instruction['result']
        if memop == 'load':
            size = self.get_size(decoded_instruction['funct3'])
            signed = self.is_signed(decoded_instruction['funct3'])
            decoded_instruction['result'] = self.memory_stage.load(address, size, signed)
        elif memop == 'store':
            size = self.get_size(decoded_instruction['funct3'])
            value = decoded_instruction['strval']
            self.memory_stage.store(address, size, value)

    def get_size(self, funct3):
        if funct3 == 0:  # lb, sb
            return 1
        elif funct3 == 1:  # lh, sh
            return 2
        elif funct3 == 2:  # lw, sw
            return 4
        return 4  # Default to word size

    def is_signed(self, funct3):
        return funct3 in [0, 1, 2]  # lb, lh, lw are signed; lbu, lhu are unsigned

    def step(self):
        fetched_instruction = self.fetch()
        decoded_instruction = self.decode(fetched_instruction)
        executed_instruction = self.execute(decoded_instruction)
        self.memory_access(executed_instruction)
        self.writeback(executed_instruction)
        self.pc = executed_instruction['pc_update']  # Update PC after instruction execution


class ALU:
    pass

def sign_extend(value, bit_length):
    sign_bit = 1 << (bit_length - 1)
    return (value & (sign_bit - 1)) - (value & sign_bit)
