# Documentación Tecnica - ISA Encoder - RISCV

## 1. Descripción de la Arquitectura del Código y Decisiones de Diseño

### Cobertura de Instrucciones y Fuentes
El codificador soporta únicamente un subconjunto de 12 instrucciones fundamentales de la arquitectura base RV32I:
* **Tipo R:** `add`, `sub`, `and`, `or`
* **Tipo I (Aritméticas y Carga):** `addi`, `andi`, `lw`, `lb`
* **Tipo S:** `sw`, `sb`
* **Tipo B:** `beq`, `bne`

Los valores numéricos de `opcode`, `funct3` y `funct7`, así como la distribución y empaquetado de bits para cada campo, se extrajeron directamente del manual oficial de la ISA:
> *Andrew Waterman and Krste Asanović. The RISC-V Instruction Set Manual, Volume I: User-Level ISA, Document Version 20191213. RISC-V Foundation, 2019.*

### Arquitectura de la Herramienta Principal
Toda la lógica de codificación e interpretación se concentró en un único archivo Python (`encoder_skeleton.py`), el cual fue estructurado modularmente en los siguientes componentes:

1. **Diccionario de Instrucciones (`instrucciones`):** Actúa como tabla de búsqueda central para mapear el mnemónico con su formato correspondiente (`R`, `I_aritmetico`, `I_carga`, `S`, `B`) y sus bits de control (`opcode`, `funct3`, `funct7`) expresados mediante literales binarios (`0b...`).
2. **Función `parse_reg`:** Parsea cadenas de registros convirtiéndolas a su valor entero equivalente de 5 bits. Soporta tanto la notación numérica directa (`x0`–`x31`) como los nombres oficiales de la convención ABI (`zero`, `ra`, `sp`, `t0`–`t6`, `a0`–`a7`, `s0`–`s11`).
3. **Función `encode_instruction`:** Procesa la cadena ingresada limpiando delimitadores, extrae operandos y empaqueta los bits aplicando operaciones de desplazamiento (`<<`) y máscaras bit a bit (`&` / `|`). En instrucciones de carga/almacenamiento (`I_carga` y `S`) extrae desplazamientos y registros base desde expresiones tipo `imm(rs1)` con expresiones regulares.
4. **Función `explain_instruction`:** Decodifica la palabra de 32 bits para reconstruir la interpretación en prosa de la instrucción, explicar la semántica de cada campo y generar una representación gráfica en tabla ASCII alineada con las especificaciones del proyecto.

### Arquitectura del Script de Validación (`comparacion.py`)
Para automatizar las pruebas y auditar el codificador, se implementó un script que ejecuta en lote los casos de prueba desde un archivo `.txt`. Para cada instrucción, invoca la herramienta del estudiante mediante `./run.sh "<instruccion>"` y la compara contra el ensamblador oficial (`riscv64-elf-as`), emitiendo una tabla comparativa con el veredicto de coincidencia.


## 2. Ejemplos de Salida

### Formato R (`add x7, x20, x6`)
```
=== Análisis de Instrucción: 'add x7, x20, x6' ===
add: Esta instrucción suma el contenido de los registros fuentes x20 y x6, almacenando el resultado en el registro destino x7.

Formato  : Tipo R
Binario  : 00000000011010100000001110110011

Significado de los campos en el binario:
  * opcode : Identificador principal de la instrucción y su formato en la ISA RISC-V.
  * rd     : Registro destino donde se almacenará el resultado de la operación.
  * funct3 : Selector de sub-operación (3 bits) que diferencia tipos de operaciones aritméticas/lógicas.
  * rs1    : Primer registro fuente que contiene el primer operando.
  * rs2    : Segundo registro fuente que contiene el segundo operando.
  * funct7 : Selector de extensión (7 bits) que distingue variantes de la instrucción.

Descomposición de Campos:
  * funct7 (31-25) : 0x00 (0000000)
  * rs2    (24-20) : x6 (00110)
  * rs1    (19-15) : x20 (10100)
  * funct3 (14-12) : 0x0 (000)
  * rd     (11-7)  : x7 (00111)
  * opcode (6-0)   : 0x33 (0110011)

+---------+----------+-------+-------+--------+-------+---------+
| Formato |  31-25   | 24-20 | 19-15 | 14-12  | 11-7  |   6-0   |
+---------+----------+-------+-------+--------+-------+---------+
| Campo   |  funct7  |  rs2  |  rs1  | funct3 |  rd   | opcode  |
+---------+----------+-------+-------+--------+-------+---------+
| Bits    | 0000000  | 00110 | 10100 |  000   | 00111 | 0110011 |
+---------+----------+-------+-------+--------+-------+---------+
HEX: 0x006a03b3
```

### Formato I (addi x10, x11, 100)

```
=== Análisis de Instrucción: 'addi x10, x11, 100' ===
addi: Esta instrucción suma el valor inmediato 100 al valor del registro fuente x11 y guarda el resultado en el registro destino x10.

Formato  : Tipo I
Binario  : 00000110010001011000001010010011

Significado de los campos en el binario:
  * opcode : Identificador principal de la instrucción y su formato en la ISA RISC-V.
  * rd     : Registro destino donde se guardará el resultado o la carga desde memoria.
  * funct3 : Selector de sub-operación (3 bits) para el tipo de operación.
  * rs1    : Registro fuente base sobre el cual se aplica la operación.
  * imm    : Valor inmediato constante (12 bits con signo).

Descomposición de Campos:
  * imm[11:0] (31-20) : 100 (0b000001100100)
  * rs1       (19-15) : x11 (01011)
  * funct3    (14-12) : 0x0 (000)
  * rd        (11-7)  : x10 (01010)
  * opcode    (6-0)   : 0x13 (0010011)

+---------+------------------+-------+--------+-------+---------+
| Formato |      31-20       | 19-15 | 14-12  | 11-7  |   6-0   |
+---------+------------------+-------+--------+-------+---------+
| Campo   |    imm[11:0]     |  rs1  | funct3 |  rd   | opcode  |
+---------+------------------+-------+--------+-------+---------+
| Bits    |   000001100100   | 01011 |  000   | 01010 | 0010011 |
+---------+------------------+-------+--------+-------+---------+
HEX: 0x06458513
```

### Formato S (sw x5, 20(x10))

```
=== Análisis de Instrucción: 'sw x5, 20(x10)' ===
Descripción: Esta instrucción almacena el valor presente en el registro fuente x5 en la memoria, en la dirección calculada sumando la base x10 y el desplazamiento 20.

Formato  : Tipo S
Binario  : 00000000010101010010101000100011

Significado de los campos en el binario:
  * opcode : Identificador principal de la instrucción y su formato en la ISA RISC-V.
  * imm    : Desplazamiento constante (12 bits con signo) dividido en partes alta [11:5] y baja [4:0].
  * funct3 : Selector del tamaño de dato a almacenar en memoria (palabra de 32 bits).
  * rs1    : Registro fuente base que contiene la dirección de memoria inicial.
  * rs2    : Registro fuente que contiene el dato que será escrito en la memoria.

Descomposición de Campos:
  * imm[11:5] (31-25) : 0b0000000
  * rs2       (24-20) : x5 (00101)
  * rs1       (19-15) : x10 (01010)
  * funct3    (14-12) : 0x2 (010)
  * imm[4:0]  (11-7)  : 0b10100
  * Inmediato completo: 20
  * opcode    (6-0)   : 0x23 (0100011)

+---------+----------+-------+-------+--------+-----------+---------+
| Formato |  31-25   | 24-20 | 19-15 | 14-12  |   11-7    |   6-0   |
+---------+----------+-------+-------+--------+-----------+---------+
| Campo   | imm[11:5]|  rs2  |  rs1  | funct3 | imm[4:0]  | opcode  |
+---------+----------+-------+-------+--------+-----------+---------+
| Bits    | 0000000  | 00101 | 01010 |  010   |   10100   | 0100011 |
+---------+----------+-------+-------+--------+-----------+---------+
HEX: 0x00552a23
```

### Formato B (beq x1, x2, 8)

```
=== Análisis de Instrucción: 'beq x1, x2, 8' ===
Descripción: Esta instrucción compara los registros x1 y x2; si sus valores son iguales, realiza un salto en el flujo del programa con un desplazamiento de 8 bytes.

Formato  : Tipo B
Binario  : 00000000001000001000010001100011

Significado de los campos en el binario:
  * opcode : Identificador principal de la instrucción y su formato en la ISA RISC-V.
  * imm    : Desplazamiento relativo al PC (13 bits con signo, bit 0 implícito en 0).
  * funct3 : Selector de la condición de salto (igualdad ==).
  * rs1    : Primer registro fuente para la evaluación condicional.
  * rs2    : Segundo registro fuente para la evaluación condicional.

Descomposición de Campos:
  * imm[12|10:5] (31-25) : 0b0000000 (bit 12: 0, bits 10-5: 000000)
  * rs2          (24-20) : x2 (00010)
  * rs1          (19-15) : x1 (00001)
  * funct3       (14-12) : 0x0 (000)
  * imm[4:1|11]  (11-7)  : 0b01000 (bits 4-1: 0100, bit 11: 0)
  * Inmediato completo   : 8 (con bit 0 en 0 implícito)
  * opcode       (6-0)   : 0x63 (1100011)

+---------+---------------+-------+-------+--------+--------------+---------+
| Formato |     31-25     | 24-20 | 19-15 | 14-12  |    11-7      |   6-0   |
+---------+---------------+-------+-------+--------+--------------+---------+
| Campo   | imm[12|10:5]  |  rs2  |  rs1  | funct3 | imm[4:1|11]  | opcode  |
+---------+---------------+-------+-------+--------+--------------+---------+
| Bits    |    0000000    | 00010 | 00001 |  000   |    01000     | 1100011 |
+---------+---------------+-------+-------+--------+--------------+---------+
HEX: 0x00208463
```

## 3. Evidencia de Comparación Contra el Toolchain

A continuación se presenta la evidencia de validación contra el toolchain oficial de RISC-V (riscv64-elf-as):

### Validacion de pruebas de vectores_ejemplo.txt

![ValidacionEjemplos](/documentacion/EvidenciaValidacion/EvidenciaVectoresEjemplo.png)

### Validacion de pruebas de 36casosprueba.txt

![Validacion36pruebas](/documentacion/EvidenciaValidacion/Evidencia36Pruebas.png)

Nota: Durante la ejecución automática con el ensamblador oficial GNU, se detectó que al enviar instrucciones de salto como beq x30, x4, -80, el toolchain interprete el número -80 como una dirección de memoria absoluta y calcule el desplazamiento relativo respecto a la dirección base .text. Para forzar al ensamblador GNU a codificar el número como un offset constante relativo al PC, el script de prueba adapta automáticamente los argumentos de las instrucciones beq y bne anteponiendo .- a números negativos y .+ a números positivos (ej. beq x30, x4, .-80).

Como se observa en las capturas de pantalla, el 100% de las 36 pruebas fueron exitosas, demostrando que la salida del modelo en Python coincide exactamente bit a bit con el toolchain oficial.

## 4. Instrucciones de Instalación del Toolchain

Para la instalación del toolchain oficial de ensamblado se consultó la documentación oficial de la distribución Arch Linux (Pues EndeavorOS es basado en Arch Linux).
Comandos de Instalación

En distribuciones basadas en Arch Linux (EndeavourOS):
```
sudo pacman -S riscv64-elf-binutils
```
Para instalacion en otros sistemas operativos, referirse al README.md

Y para probar manualmente el ensamblado de una instrucción en el toolchain:
```
echo "add x7, x20, x6" | riscv64-elf-as -march=rv32i -mabi=ilp32 -o /tmp/test.o && riscv64-elf-objdump -d /tmp/test.o
```

## 5. Referencias

    Waterman, A., & Asanović, K. (2019). The RISC-V Instruction Set Manual, Volume I: User-Level ISA, Document Version 20191213. RISC-V Foundation.

    Arch Linux Wiki. (2026). RISC-V toolchain. Recuperado de https://wiki.archlinux.org/
