#!/usr/bin/env python3

import sys

SOPORTADAS = ["add", "sub", "and", "or", "addi", "andi",
              "lw", "lb", "sw", "sb", "beq", "bne"]

# Diccionario de instrucciones soportadas con respectiva informacion
instrucciones = {
    # Instrucciones formato R
    "add": {"formato": "R", "opcode": 0b0110011, "funct3": 0b000, "funct7": 0b0000000},
    "sub": {"formato": "R", "opcode": 0b0110011, "funct3": 0b000, "funct7": 0b0100000},
    "and": {"formato": "R", "opcode": 0b0110011, "funct3": 0b111, "funct7": 0b0000000},
    "or":  {"formato": "R", "opcode": 0b0110011, "funct3": 0b110, "funct7": 0b0000000},
    
    # Instrucciones formato I Aritmética 
    "addi": {"formato": "I_aritmetico", "opcode": 0b0010011, "funct3": 0b000},
    "andi": {"formato": "I_aritmetico", "opcode": 0b0010011, "funct3": 0b111},
    
    # Instrucciones formato I Carga
    "lw": {"formato": "I_carga", "opcode": 0b0000011, "funct3": 0b010},
    "lb": {"formato": "I_carga", "opcode": 0b0000011, "funct3": 0b000},
    
    # Instrucciones formato S
    "sw": {"formato": "S", "opcode": 0b0100011, "funct3": 0b010},
    "sb": {"formato": "S", "opcode": 0b0100011, "funct3": 0b000},
    
    # Instrucciones formato B
    "beq": {"formato": "B", "opcode": 0b1100011, "funct3": 0b000},
    "bne": {"formato": "B", "opcode": 0b1100011, "funct3": 0b001},
}

def encode_instruction(instruction: str) -> int:
    """
    Recibe una instrucción como texto, p. ej. "add x5, x6, x7", y debe
    retornar su codificación de 32 bits como entero (0 <= valor < 2**32).

    Debe soportar únicamente las instrucciones en SOPORTADAS. Los valores
    de opcode/funct3/funct7 de cada una NO se proveen aquí: deben
    investigarse en el manual oficial de la ISA RISC-V (ver referencia en
    la especificación) y documentarse en el README.
    """
    # TODO: implementar. Sugerencia: parsear el mnemónico y los operandos,
    # despachar según el formato (R/I/S/B), y ensamblar los campos con
    # operaciones de bits.
    raise NotImplementedError("encode_instruction: pendiente de implementar")


def explain_instruction(instruction: str, word: int) -> str:
    """
    Debe retornar un texto (para imprimirse en pantalla) que muestre, de
    forma visual, los 32 bits de 'word' divididos en los campos del
    formato correspondiente (R, I, S o B) — indicando el rango de bits y
    el valor de cada campo — junto con una breve explicación de cada uno.
    El formato visual (colores, tabla, arte ASCII, etc.) queda a su
    criterio, siempre que sea claro.
    """
    # TODO: implementar.
    raise NotImplementedError("explain_instruction: pendiente de implementar")


def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} "<instruccion>"', file=sys.stderr)
        print(f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"', file=sys.stderr)
        sys.exit(2)

    instruction = sys.argv[1]
    word = encode_instruction(instruction) & 0xFFFFFFFF

    print(explain_instruction(instruction, word))

    # No modificar el formato de la siguiente línea: la especificación la
    # requiere, literal, para permitir la validación automática.
    print(f"HEX: 0x{word:08x}")


if __name__ == "__main__":
    main()
