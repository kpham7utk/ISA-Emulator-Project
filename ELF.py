# COSC 530 ISA Emulator Project
# ELF Portion
import struct

# '<' specifies little-endian byte order
# '4s' corresponds to the ELF magic number (4 bytes)
# 'B' specifies a single byte (unsigned char)
# '7x' for 7 padding bytes, 'H' specifies a two-byte (unsigned short) field
# 'I' specifies a four-byte (unsigned int) field, 'H' specifies another two-byte field
ELF_HEADER_FORMAT = '<4sBBBBB7xHHIIIIIHHHHHH'
# 4 + 5*1 + 7 + 2*2 + 6*4 + 5*2 = 52 bytes
ELF_HEADER_SIZE = 52

# Define the program header structure for 32-bit little-endian RISC-V architecture
PROGRAM_HEADER_FORMAT = '<IIIIIIII'
# 8 * 4 = 32 bytes (each 'I' represents a 4-byte unsigned int, and there are 8 fields)
PROGRAM_HEADER_SIZE = 32

# Constants for checking the ELF file
ELF_MAGIC = b'\x7fELF'
RISC_V_MACHINE = 243
PT_LOAD = 1

def load_elf(filename):
    with open(filename, 'rb') as file:
        # Read ELF header
        elf_header_data = file.read(ELF_HEADER_SIZE)
        elf_header = struct.unpack(ELF_HEADER_FORMAT, elf_header_data)

        # Verify ELF header
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

        # Read and process program headers
        file.seek(e_phoff)
        for _ in range(e_phnum):
            program_header_data = file.read(PROGRAM_HEADER_SIZE)
            program_header = struct.unpack(PROGRAM_HEADER_FORMAT, program_header_data)

            if program_header[0] == PT_LOAD:
                copy_segment(file, program_header)

        # Set the program counter to the entry point
        print(f"Entry point: 0x{e_entry:x}")

# vaddr added for later
def allocate_memory(size, vaddr):
    memory = bytearray(size)
    return memory

def copy_segment(file, ph):
    p_offset, p_vaddr, p_filesz, p_memsz = ph[1], ph[2], ph[4], ph[5]

    # Allocate memory for the segment
    memory = allocate_memory(p_memsz, p_vaddr)

    # Seek to the segment in the file
    file.seek(p_offset)

    # Read the segment into memory
    segment_data = file.read(p_filesz)
    memory[:p_filesz] = segment_data

    # Zero out the remaining memory if p_memsz > p_filesz
    if p_memsz > p_filesz:
        memory[p_filesz:p_memsz] = b'\x00' * (p_memsz - p_filesz)

    print(f"Loaded segment at 0x{p_vaddr:x}, size {p_memsz}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <elf-file>")
        sys.exit(1)

    load_elf(sys.argv[1])
