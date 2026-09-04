#!/usr/bin/env python3
import os
import subprocess
import sys

# Variable para definir el archivo de vectores a evaluar
# Al validar funcionamiento del modelo se puso "vectores_ejemplo.txt", pero para los 36 casos de prueba son con "36casosprueba.txt"
ARCHIVO_VECTORES = "36casosprueba.txt"


def prepare_for_toolchain(instruction: str) -> str:
    # Adaptación de la instrucción para que sea compatible con el ensamblador GNU
    clean = instruction.strip()
    tokens = clean.replace(",", " ").split()

    if not tokens:
        return instruction

    mnemonic = tokens[0].lower()
    if mnemonic in ["beq", "bne"]:
        imm_str = tokens[3]
        if not imm_str.startswith(".+"):
            if imm_str.startswith("-"):
                imm_str = ".-" + imm_str[1:]
            else:
                imm_str = ".+" + imm_str
        return f"{tokens[0]} {tokens[1]}, {tokens[2]}, {imm_str}"

    return instruction


def encode_with_python_model(instruction: str) -> str:
    # Ejecuta las pruebas con ./run.sh
    cmd = ["./run.sh", instruction]
    try:
        res = subprocess.check_output(cmd, text=True, stderr=subprocess.PIPE)
        for line in res.splitlines():
            line = line.strip()
            if line.startswith("HEX:"):
                # Extrae "0x........" de la línea final
                return line.split(":")[1].strip().lower()
    except Exception:
        return "ERROR_RUN_SH"
    return "N/A"


def encode_with_toolchain(instruction: str) -> str:
    # Ensambla la instrucción adaptada usando GNU Assembler
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
    if not os.path.exists(ARCHIVO_VECTORES):
        print(f"Error: No se encontró el archivo '{ARCHIVO_VECTORES}'.", file=sys.stderr)
        sys.exit(1)

    print("\n" + "=" * 90)
    print(f" VALIDACIÓN COMPARATIVA DESDE: {ARCHIVO_VECTORES}")
    print("=" * 90)
    print(
        f"{'Instrucción':<22} | {'Esperado':<10} | {'Modelo (run.sh)':<20} | {'Toolchain':<12} | ESTADO"
    )
    print("-" * 90)

    exitos = 0
    total = 0

    with open(ARCHIVO_VECTORES, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(";")
            instruction = parts[0].strip()
            esperado = parts[1].strip().lower() if len(parts) > 1 else "N/A"

            hex_model = encode_with_python_model(instruction)

            hex_toolchain = encode_with_toolchain(instruction)

            # 3. Comparación
            coincide = hex_model == esperado and hex_toolchain == esperado
            estado = " OK " if coincide else " FAIL "

            if coincide:
                exitos += 1
            total += 1

            print(
                f"{instruction:<22} | {esperado:<10} | {hex_model:<20} | {hex_toolchain:<12} | [{estado}]"
            )

    print("-" * 90)
    print(f"RESUMEN: {exitos}/{total} pruebas pasaron correctamente.")
    print("=" * 90 + "\n")


if __name__ == "__main__":
    main()