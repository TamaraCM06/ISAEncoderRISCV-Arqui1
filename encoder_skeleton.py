#!/usr/bin/env python3

import re
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

def parse_reg(reg_str: str) -> int:
    # Parsea el registro con nombre abi a el registro en hardware
    reg_str = reg_str.strip().lower()
    abi_names = {
        "zero": 0,
        "ra": 1,
        "sp": 2,
        "gp": 3,
        "tp": 4,
        "t0": 5,
        "t1": 6,
        "t2": 7,
        "s0": 8,
        "fp": 8,
        "s1": 9,
        "a0": 10,
        "a1": 11,
        "a2": 12,
        "a3": 13,
        "a4": 14,
        "a5": 15,
        "a6": 16,
        "a7": 17,
        "s2": 18,
        "s3": 19,
        "s4": 20,
        "s5": 21,
        "s6": 22,
        "s7": 23,
        "s8": 24,
        "s9": 25,
        "s10": 26,
        "s11": 27,
        "t3": 28,
        "t4": 29,
        "t5": 30,
        "t6": 31,
    }
    if reg_str in abi_names:
        return abi_names[reg_str]
    # Obtener solamente el numero en caso de registro en formato xN
    if reg_str.startswith("x") and reg_str[1:].isdigit():
        val = int(reg_str[1:])
        if 0 <= val <= 31:
            return val
    raise ValueError(f"Registro inválido: '{reg_str}'")

def encode_instruction(instruction: str) -> int:
    """
    Recibe una instrucción como texto, p. ej. "add x5, x6, x7", y debe
    retornar su codificación de 32 bits como entero (0 <= valor < 2**32).

    Debe soportar únicamente las instrucciones en SOPORTADAS. Los valores
    de opcode/funct3/funct7 de cada una NO se proveen aquí: deben
    investigarse en el manual oficial de la ISA RISC-V (ver referencia en
    la especificación) y documentarse en el README.
    """
    # Obtener los argumentos de la instruccion y guardar en variables que formaran la palabra
    clean_instr = instruction.strip().replace(",", " ")
    tokens = clean_instr.split()

    if not tokens:
        raise ValueError("Instrucción vacía")

    #Tomar instruccion
    mnemonico = tokens[0].lower()
    if mnemonico not in instrucciones:
        raise ValueError(
            f"Mnemónico '{mnemonico}' no soportado. Debe ser uno de {SOPORTADAS}"
        )

    info = instrucciones[mnemonico]
    formato = info["formato"]
    opcode = info["opcode"]
    funct3 = info["funct3"]

    word = 0

    if formato == "R":
        # Formato de instruccion: op rd, rs1, rs2
        rd = parse_reg(tokens[1])
        rs1 = parse_reg(tokens[2])
        rs2 = parse_reg(tokens[3])
        funct7 = info["funct7"]
        word = (
            (funct7 << 25)
            | (rs2 << 20)
            | (rs1 << 15)
            | (funct3 << 12)
            | (rd << 7)
            | opcode
        )

    elif formato == "I_aritmetico":
        # Formato de instruccion: op rd, rs1, imm
        rd = parse_reg(tokens[1])
        rs1 = parse_reg(tokens[2])
        imm = int(tokens[3], 0) & 0xFFF  # Inmediato 12 bits
        word = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

    elif formato == "I_carga":
        # Direccionamiento con desplazamiento: op rd, imm(rs1)
        rd = parse_reg(tokens[1])
        match = re.match(r"^([^\(]+)\(([^\)]+)\)$", tokens[2])
        if not match:
            raise ValueError(
                f"Sintaxis inválida para carga: '{tokens[2]}'. Esperado: imm(rs1)"
            )
        imm = int(match.group(1), 0) & 0xFFF
        rs1 = parse_reg(match.group(2))
        word = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    elif formato == "S":
        # Direccionamiento con desplazamiento: op rs2, imm(rs1)
        rs2 = parse_reg(tokens[1])
        match = re.match(r"^([^\(]+)\(([^\)]+)\)$", tokens[2])
        if not match:
            raise ValueError(
                f"Sintaxis inválida para store: '{tokens[2]}'. Esperado: imm(rs1)"
            )
        imm = int(match.group(1), 0) & 0xFFF
        rs1 = parse_reg(match.group(2))

        imm_11_5 = (imm >> 5) & 0x7F
        imm_4_0 = imm & 0x1F

        word = (
            (imm_11_5 << 25)
            | (rs2 << 20)
            | (rs1 << 15)
            | (funct3 << 12)
            | (imm_4_0 << 7)
            | opcode
        )

    elif formato == "B":
        # Formato: op rs1, rs2, imm
        rs1 = parse_reg(tokens[1])
        rs2 = parse_reg(tokens[2])
        imm = int(tokens[3], 0) & 0x1FFF  # Inmediato de 13 bits (bit 0 es 0)

        imm_12 = (imm >> 12) & 0x1
        imm_10_5 = (imm >> 5) & 0x3F
        imm_4_1 = (imm >> 1) & 0x0F
        imm_11 = (imm >> 11) & 0x1

        word = (
            (imm_12 << 31)
            | (imm_10_5 << 25)
            | (rs2 << 20)
            | (rs1 << 15)
            | (funct3 << 12)
            | (imm_4_1 << 8)
            | (imm_11 << 7)
            | opcode
        )
        
    return word


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
