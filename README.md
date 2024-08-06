# RISC-V Processor Simulator

## Overview

This project is a simulation of a RISC-V processor written in Python. The simulator supports the complete pipeline stages including fetching, decoding, executing instructions, memory access, and writeback. Additionally, it can load and execute ELF files.

## File Descriptions

- **`writeback.py`**: Handles the writeback stage of the processor pipeline.
- **`memory.py`**: Manages memory operations including reading from and writing to memory.
- **`Machine.py`**: The main class that integrates all parts of the processor pipeline.
- **`FetchDecodeExecute.py`**: Manages the fetch, decode, and execute stages of the pipeline.
- **`ELF.py`**: Responsible for loading ELF files into memory for execution.

## Requirements

- Python 3.8+

## Installation

1. Download or clone the project folder to your local machine.

## Usage

1. Open a terminal and navigate to the project folder.

2. Load an ELF file and run the simulation:
   ```bash
   python Machine.py <path-to-elf-file>
   ```

   Example:
   ```bash
   python Machine.py examples/hello_world.elf
   ```

## Project Structure

- `writeback.py`: Writeback stage of the processor.
- `memory.py`: Memory operations.
- `Machine.py`: Main class integrating all pipeline stages.
- `FetchDecodeExecute.py`: Fetch, decode, and execute stages.
- `ELF.py`: Loading ELF files.

## Contributing

1. Create a new branch (`git checkout -b feature-branch`).
2. Commit your changes (`git commit -am 'Add new feature'`).
3. Push to the branch (`git push origin feature-branch`).
4. Share the updated folder with collaborators.

## License

This project is licensed under the MIT License.
