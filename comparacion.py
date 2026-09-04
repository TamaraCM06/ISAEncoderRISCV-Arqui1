#!/usr/bin/env python3
import re
import subprocess
import sys
from encoder_skeleton import encode_instruction

# String con los 36 vectores de prueba originales (sintaxis estándar)
VECTORES_TEXTO = """
# --- add ---
add x7, x20, x6 ; 0x006a03b3
add x14, x26, x31 ; 0x01fd0733
add x28, x15, x0 ; 0x00078e33
# --- sub ---
sub x5, x7, x18 ; 0x412382b3
sub x6, x28, x0 ; 0x400e0333
sub x31, x20, x13 ; 0x40da0fb3
# --- and ---
and x25, x16, x22 ; 0x01687cb3
and x22, x24, x4 ; 0x004c7b33
and x21, x5, x18 ; 0x0122fab3
# --- or ---
or x18, x29, x9 ; 0x009ee933
or x19, x1, x23 ; 0x0170e9b3
or x23, x29, x27 ; 0x01beebb3
# --- addi ---
addi x5, x25, 2035 ; 0x7f3c8293
addi x7, x27, 1974 ; 0x7b6d8393
addi x25, x16, 1392 ; 0x57080c93
# --- andi ---
andi x30, x1, -209 ; 0xf2f0ff13
andi x8, x3, -1208 ; 0xb481f413
andi x27, x30, -882 ; 0xc8ef7d93
# --- lw ---
lw x30, -1049(x14) ; 0xbe772f03
lw x29, 8(x30) ; 0x008f2e83
lw x25, 1875(x19) ; 0x7539ac83
# --- lb ---
lb x25, -389(x27) ; 0xe7bd8c83
lb x18, -1973(x17) ; 0x84b88903
lb x2, 1705(x9) ; 0x6a948103
# --- sw ---
sw x31, -411(x23) ; 0xe7fba2a3
sw x16, 1774(x31) ; 0x6f0fa723
sw x31, -1773(x27) ; 0x91fda9a3
# --- sb ---
sb x18, 1701(x20) ; 0x6b2a02a3
sb x6, 72(x28) ; 0x046e0423
sb x28, 1439(x11) ; 0x59c58fa3
# --- beq ---
beq x30, x4, -80 ; 0xfa4f08e3
beq x31, x23, 16 ; 0x017f8863
beq x26, x9, 60 ; 0x029d0e63
# --- bne ---
bne x5, x0, 60 ; 0x02029e63
bne x12, x15, 16 ; 0x00f61863
bne x17, x22, 20 ; 0x01689a63
"""


def prepare_for_toolchain(instruction: str) -> str:
    """Adapta la sintaxis de saltos para que el GNU Assembler reconozca la PC-relatividad."""
    clean = instruction.strip()
    tokens = clean.replace(",", " ").split()

    if not tokens:
        return instruction

    mnemonic = tokens[0].lower()
    if mnemonic in ["beq", "bne"]:
        # Se asume que el tercer token/argumento es el inmediato
        imm_str = tokens[3]
        # Evitar duplicar si ya traía .+ o .-
        if not imm_str.startswith(".+"):
            if imm_str.startswith("-"):
                # Reemplazar '-' por '.-'
                imm_str = ".-" + imm_str[1:]
            else:
                # Anteponer '.+' a inmediatos positivos
                imm_str = ".+" + imm_str

        return f"{tokens[0]} {tokens[1]}, {tokens[2]}, {imm_str}"

    return instruction


def encode_with_toolchain(instruction: str) -> str:
    """Ensambla la instrucción adaptada usando GNU Assembler y extrae su valor hexadecimal."""
    adapted_instruction = prepare_for_toolchain(instruction)

    cmd = (
        f'echo "{adapted_instruction}" | riscv64-elf-as -march=rv32i -mabi=ilp32 -o /tmp/test_runner.o '
        f"&& riscv64-elf-objdump -d /tmp/test_runner.o"
    )
    try:
        res = subprocess.check_output(cmd, shell=True, text=True)
        for line in res.splitlines():
            if ":" in line and "\t" in line:
                hex_val = line.split("\t")[1].strip()
                parts = hex_val.split()
                if parts:
                    return f"0x{int(parts[0], 16):08x}"
    except Exception:
        return "ERROR_TOOLCHAIN"
    return "N/A"


def main():
    print("\n" + "=" * 90)
    print(" VALIDACIÓN COMPARATIVA: MODELO PYTHON vs. TOOLCHAIN OFICIAL DE RISC-V")
    print("=" * 90)
    print(
        f"{'INSTRUCCIÓN':<22} | {'ESPERADO':<10} | {'MODELO (.py)':<12} | {'TOOLCHAIN':<12} | ESTADO"
    )
    print("-" * 90)

    exitos = 0
    total = 0

    for line in VECTORES_TEXTO.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split(";")
        instruction = parts[0].strip()
        esperado = parts[1].strip().lower()

        # Modelo recibe la instrucción en su formato normal
        try:
            val_modelo = encode_instruction(instruction) & 0xFFFFFFFF
            hex_modelo = f"0x{val_modelo:08x}"
        except Exception as e:
            hex_modelo = "ERROR_PY"

        # Toolchain recibe la instrucción adaptada internamente
        hex_toolchain = encode_with_toolchain(instruction)

        # Comparación de resultados
        coincide = hex_modelo == esperado and hex_toolchain == esperado
        estado = " OK " if coincide else " FAIL "

        if coincide:
            exitos += 1
        total += 1

        print(
            f"{instruction:<22} | {esperado:<10} | {hex_modelo:<12} | {hex_toolchain:<12} | [{estado}]"
        )

    print("-" * 90)
    print(f"RESUMEN: {exitos}/{total} pruebas pasaron correctamente.")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()