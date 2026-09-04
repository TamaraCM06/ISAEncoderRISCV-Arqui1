# ISA Encoder - RISCV // Requisitos y Preparación del Entorno

La herramienta principal fue desarrollada en **Python 3** utilizando únicamente su biblioteca estándar (`re` y `sys`). Por lo tanto, no es necesario instalar ninguna dependencia ni paquete de terceros a través de `pip`.

El único requisito previo es contar con un entorno de ejecución que disponga de **Python 3.6 o superior** e intérprete de comandos **Bash** para invocar el script ejecutable `./run.sh`.

### 1. Instalación de Python 3 según el Sistema Operativo

#### En Linux (EndeavourOS / Arch Linux)
En distribuciones basadas en Arch Linux, Python suele estar preinstalado. Si requiere instalarlo o actualizarlo, ejecute el siguiente comando en la terminal para descargar el paquete oficial:

```
sudo pacman -S python
```

#### En Linux (Ubuntu / Debian / Linux Mint)

Para sistemas basados en Debian, actualice primero el índice de paquetes del sistema y posteriormente instale el intérprete de Python 3:

```
sudo apt update
sudo apt install python3
```
#### En macOS

En macOS se recomienda instalar Python 3 a través del gestor de paquetes Homebrew. Abra la terminal e introduzca el siguiente comando:
```
brew install python
```
(Alternativamente, puede descargar el instalador oficial de macOS desde el sitio web python.org).

#### En Windows

Para ejecutar la herramienta en Windows existen dos opciones principales:

    Uso mediante WSL2 (Windows Subsystem for Linux):
    Abra PowerShell como Administrador e instale un entorno Ubuntu integrado mediante PowerShell

```
    wsl --install
```
    Una vez reiniciado el sistema, dispondrá de una terminal Bash nativa de Linux donde podrá seguir las instrucciones de Ubuntu.

    Uso Nativo con Python para Windows:
    Descargue e instale Python 3 desde python.org. Durante la instalación, asegúrese de marcar la casilla "Add Python to PATH". Para ejecutar la herramienta con el archivo Bash en Windows, puede utilizar la terminal Git Bash (incluida al instalar Git for Windows).

### 2. Configuración de Permisos de Ejecución

Antes de ejecutar el script por primera vez en sistemas basados en Unix (Linux, macOS o WSL/Git Bash), es necesario otorgar permisos de ejecución al archivo del punto de entrada run.sh.

Abra una terminal en la raíz del proyecto y ejecute el siguiente comando:
```
chmod +x run.sh
```
Este comando modifica los atributos del archivo para permitir que el sistema operativo lo reconozca como un programa ejecutable.
Modo de Uso

Para codificar e interpretar una instrucción, convoque el script run.sh pasando la instrucción deseada entre comillas dobles como único argumento:
Bash
```
./run.sh "add x7, x20, x6"
```
El script imprimirá la descripción semántica, el desglose de bits por campos en formato ASCII y la línea final estandarizada con el resultado en hexadecimal.