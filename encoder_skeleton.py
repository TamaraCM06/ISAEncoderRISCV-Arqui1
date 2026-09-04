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

    elif formato in ["I_carga", "S"]:
            # Direccionamiento con desplazamiento: op rd/rs2, imm(rs1)
            target_token = tokens[2] if len(tokens) > 2 else ""
            # Si los espacios separaron el offset del paréntesis, unimos tokens restantes
            # Esto se hace pues la separacion puede causar problemas al parsear instrucciones con espacios entre el inmediato y el rs1
            full_operand = "".join(tokens[2:])
            match = re.match(r"^([^\(]+)\(([^\)]+)\)$", full_operand)
            if not match:
                raise ValueError(f"Sintaxis inválida: '{full_operand}'. Esperado: imm(rs1)")
            
            imm = int(match.group(1), 0) & 0xFFF
            rs1 = parse_reg(match.group(2))

            if formato == "I_carga":
                rd = parse_reg(tokens[1])
                word = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
            else:  # Formato S
                rs2 = parse_reg(tokens[1])
                imm_11_5 = (imm >> 5) & 0x7F
                imm_4_0 = imm & 0x1F
                word = (imm_11_5 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_4_0 << 7) | opcode

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
    # Se arma y desarma el resultado binario para demostrar la estructura de la instruccion.

    clean_instr = instruction.strip().replace(",", " ")
    mnemonico = clean_instr.split()[0].lower()
    info = instrucciones[mnemonico]
    formato = info["formato"]

    bits = f"{word:032b}"
    hex_str = f"0x{word:08x}"

    output = []

    # ExtracciOn de campos según el formato de la instrucciOn
    opcode = word & 0x7F
    rd = (word >> 7) & 0x1F
    funct3 = (word >> 12) & 0x7
    rs1 = (word >> 15) & 0x1F
    rs2 = (word >> 20) & 0x1F
    funct7 = (word >> 25) & 0x7F
    output.append("")
    output.append(f"=== Análisis de Instrucción: '{instruction}' ===\n")
    
    # EXPLICACION EN PROSA DE CADA INSTRUCCION
    prosa = ""
    if formato == "R":
        operaciones = {"add": "suma el contenido de", "sub": "resta el contenido de", "and": "realiza una operación AND bit a bit entre", "or": "realiza una operación OR bit a bit entre"}
        prosa = f"Esta instrucción {operaciones[mnemonico]} los registros fuentes x{rs1} y x{rs2}, almacenando el resultado en el registro destino x{rd}."

    elif formato == "I_aritmetico":
        imm = (word >> 20) & 0xFFF
        if imm & 0x800: imm -= 0x1000  # Extensión de signo para la prosa
        operaciones = {"addi": "suma el valor inmediato", "andi": "realiza un AND bit a bit con el inmediato"}
        prosa = f"Esta instrucción {operaciones[mnemonico]} {imm} al valor del registro fuente x{rs1} y guarda el resultado en el registro destino x{rd}."

    elif formato == "I_carga":
        imm = (word >> 20) & 0xFFF
        if imm & 0x800: imm -= 0x1000
        tam = "una palabra de 32 bits (4 bytes)" if mnemonico == "lw" else "un byte de 8 bits"
        prosa = f"Esta instrucción carga {tam} desde la memoria (dirección calculada como x{rs1} . {imm}) y la almacena en el registro destino x{rd}."

    elif formato == "S":
        imm_hi = (word >> 25) & 0x7F
        imm_lo = (word >> 7) & 0x1F
        imm = (imm_hi << 5) | imm_lo
        if imm & 0x800: imm -= 0x1000
        tam = "una palabra de 32 bits (4 bytes)" if mnemonico == "sw" else "un byte de 8 bits"
        prosa = f"Esta instrucción almacena el valor presente en el registro fuente x{rs2} en la memoria, en la dirección calculada sumando la base x{rs1} y el desplazamiento {imm}."

    elif formato == "B":
        imm_12 = (word >> 31) & 0x1
        imm_10_5 = (word >> 25) & 0x3F
        imm_4_1 = (word >> 8) & 0x0F
        imm_11 = (word >> 7) & 0x1
        imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)
        if imm & 0x1000: imm -= 0x2000
        cond = "son iguales" if mnemonico == "beq" else "son diferentes"
        prosa = f"Esta instrucción compara los registros x{rs1} y x{rs2}; si sus valores {cond}, realiza un salto en el flujo del programa con un desplazamiento de {imm} bytes."

    output.append(f"{mnemonico}: {prosa}\n")

    output.append(f"Formato  : Tipo {formato.replace('_LOAD', '').replace('_aritmetico', '').replace('_carga', '')}")
    output.append(f"Binario  : {bits}\n")

    output.append("Descomposición de Campos:")

    if formato == "R":
        output.append(f"  * funct7 (31-25) : 0x{funct7:02x} ({bits[0:7]})")
        output.append(f"  * rs2    (24-20) : x{rs2} ({bits[7:12]})")
        output.append(f"  * rs1    (19-15) : x{rs1} ({bits[12:17]})")
        output.append(f"  * funct3 (14-12) : 0x{funct3:x} ({bits[17:20]})")
        output.append(f"  * rd     (11-7)  : x{rd} ({bits[20:25]})")
        output.append(f"  * opcode (6-0)   : 0x{opcode:02x} ({bits[25:32]})\n")

        output.append(".---------.----------.-------.-------.--------.-------.---------.")
        output.append("| Formato |  31-25   | 24-20 | 19-15 | 14-12  | 11-7  |   6-0   |")
        output.append(".---------.----------.-------.-------.--------.-------.---------.")
        output.append("| Campo   |  funct7  |  rs2  |  rs1  | funct3 |  rd   | opcode  |")
        output.append(".---------.----------.-------.-------.--------.-------.---------.")
        output.append(f"| Bits    | {bits[0:7]}  | {bits[7:12]} | {bits[12:17]} |  {bits[17:20]}   | {bits[20:25]} | {bits[25:32]} |")
        output.append(".---------.----------.-------.-------.--------.-------.---------.")

    elif formato in ["I_aritmetico", "I_carga"]:
        imm = (word >> 20) & 0xFFF
        output.append(f"  * imm[11:0] (31-20) : {imm} (0b{bits[0:12]})")
        output.append(f"  * rs1       (19-15) : x{rs1} ({bits[12:17]})")
        output.append(f"  * funct3    (14-12) : 0x{funct3:x} ({bits[17:20]})")
        output.append(f"  * rd        (11-7)  : x{rd} ({bits[20:25]})")
        output.append(f"  * opcode    (6-0)   : 0x{opcode:02x} ({bits[25:32]})\n")

        output.append(".---------.------------------.-------.--------.-------.---------.")
        output.append("| Formato |      31-20       | 19-15 | 14-12  | 11-7  |   6-0   |")
        output.append(".---------.------------------.-------.--------.-------.---------.")
        output.append("| Campo   |    imm[11:0]     |  rs1  | funct3 |  rd   | opcode  |")
        output.append(".---------.------------------.-------.--------.-------.---------.")
        output.append(f"| Bits    |   {bits[0:12]}   | {bits[12:17]} |  {bits[17:20]}   | {bits[20:25]} | {bits[25:32]} |")
        output.append(".---------.------------------.-------.--------.-------.---------.")

    elif formato == "S":
        imm_hi = (word >> 25) & 0x7F
        imm_lo = (word >> 7) & 0x1F
        imm = (imm_hi << 5) | imm_lo
        output.append(f"  * imm[11:5] (31-25) : 0b{bits[0:7]}")
        output.append(f"  * rs2       (24-20) : x{rs2} ({bits[7:12]})")
        output.append(f"  * rs1       (19-15) : x{rs1} ({bits[12:17]})")
        output.append(f"  * funct3    (14-12) : 0x{funct3:x} ({bits[17:20]})")
        output.append(f"  * imm[4:0]  (11-7)  : 0b{bits[20:25]}")
        output.append(f"  * Inmediato completo: {imm}")
        output.append(f"  * opcode    (6-0)   : 0x{opcode:02x} ({bits[25:32]})\n")

        output.append(".---------.----------.-------.-------.--------.-----------.---------.")
        output.append("| Formato |  31-25   | 24-20 | 19-15 | 14-12  |   11-7    |   6-0   |")
        output.append(".---------.----------.-------.-------.--------.-----------.---------.")
        output.append("| Campo   | imm[11:5]|  rs2  |  rs1  | funct3 | imm[4:0]  | opcode  |")
        output.append(".---------.----------.-------.-------.--------.-----------.---------.")
        output.append(f"| Bits    | {bits[0:7]}  | {bits[7:12]} | {bits[12:17]} |  {bits[17:20]}   |   {bits[20:25]}   | {bits[25:32]} |")
        output.append(".---------.----------.-------.-------.--------.-----------.---------.")

    elif formato == "B":
        imm_12 = (word >> 31) & 0x1
        imm_10_5 = (word >> 25) & 0x3F
        imm_4_1 = (word >> 8) & 0x0F
        imm_11 = (word >> 7) & 0x1
        imm = (imm_12 << 12) | (imm_11 << 11) | (imm_10_5 << 5) | (imm_4_1 << 1)
        
        output.append(f"  * imm[12|10:5] (31-25) : 0b{bits[0:7]} (bit 12: {bits[0]}, bits 10-5: {bits[1:7]})")
        output.append(f"  * rs2          (24-20) : x{rs2} ({bits[7:12]})")
        output.append(f"  * rs1          (19-15) : x{rs1} ({bits[12:17]})")
        output.append(f"  * funct3       (14-12) : 0x{funct3:x} ({bits[17:20]})")
        output.append(f"  * imm[4:1|11]  (11-7)  : 0b{bits[20:25]} (bits 4-1: {bits[20:24]}, bit 11: {bits[24]})")
        output.append(f"  * Inmediato completo   : {imm} (con bit 0 en 0 implícito)")
        output.append(f"  * opcode       (6-0)   : 0x{opcode:02x} ({bits[25:32]})\n")

        output.append(".---------.---------------.-------.-------.--------.--------------.---------.")
        output.append("| Formato |     31-25     | 24-20 | 19-15 | 14-12  |    11-7      |   6-0   |")
        output.append(".---------.---------------.-------.-------.--------.--------------.---------.")
        output.append("| Campo   | imm[12|10:5]  |  rs2  |  rs1  | funct3 | imm[4:1|11]  | opcode  |")
        output.append(".---------.---------------.-------.-------.--------.--------------.---------.")
        output.append(f"| Bits    |    {bits[0]}{bits[1:7]}    | {bits[7:12]} | {bits[12:17]} |  {bits[17:20]}   |    {bits[20:24]}{bits[24]}    | {bits[25:32]} |")
        output.append(".---------.---------------.-------.-------.--------.--------------.---------.")

    return "\n".join(output)

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
