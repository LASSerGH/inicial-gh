# LASSer
# -*- coding: utf-8 -*-
import os
import sys
import hashlib

def calcular_hash(ruta_archivo, tamano_bloque=65536):
    """Calcula el hash SHA256 de un archivo, leyéndolo en bloques para ser eficiente con la memoria."""
    sha256 = hashlib.sha256()
    try:
        with open(ruta_archivo, 'rb') as f:
            # Lee el archivo en bloques para no consumir demasiada memoria con archivos grandes
            for bloque in iter(lambda: f.read(tamano_bloque), b''):
                sha256.update(bloque)
        return sha256.hexdigest()
    except IOError:
        # El archivo podría no ser legible (ej. por permisos) o ser un enlace simbólico roto
        print(f"Advertencia: No se pudo leer el archivo {ruta_archivo}")
        return None

def encontrar_duplicados(directorio):
    """Encuentra archivos duplicados en un directorio basándose en el hash de su contenido."""
    hashes = {}
    print("Analizando archivos...")
    # os.walk recorre de forma recursiva todas las carpetas y archivos
    for ruta_dir, _, nombres_archivo in os.walk(directorio):
        for nombre in nombres_archivo:
            ruta_completa = os.path.join(ruta_dir, nombre)
            # Solo procesa si es un archivo real y no un directorio o enlace
            if os.path.isfile(ruta_completa):
                hash_archivo = calcular_hash(ruta_completa)
                if hash_archivo:
                    # Agrega la ruta del archivo a la lista de su hash correspondiente
                    if hash_archivo in hashes:
                        hashes[hash_archivo].append(ruta_completa)
                    else:
                        hashes[hash_archivo] = [ruta_completa]
    
    # Filtra para obtener solo los hashes que tienen más de un archivo (los duplicados)
    duplicados = {valor_hash: archivos for valor_hash, archivos in hashes.items() if len(archivos) > 1}
    return duplicados

def main():
    # Verifica que se haya proporcionado la ruta de la carpeta como argumento
    if len(sys.argv) < 2:
        print("Uso: python limpiar_duplicados.py <ruta_de_la_carpeta>")
        sys.exit(1)

    directorio_objetivo = sys.argv[1]

    # Verifica que la ruta proporcionada sea una carpeta válida
    if not os.path.isdir(directorio_objetivo):
        print(f"Error: La ruta '{directorio_objetivo}' no es una carpeta válida.")
        sys.exit(1)

    print(f"Buscando duplicados en la carpeta: {os.path.abspath(directorio_objetivo)}\n")
    duplicados = encontrar_duplicados(directorio_objetivo)

    if not duplicados:
        print("\n¡Excelente! No se encontraron archivos duplicados.")
        return

    print("\n--- Se encontraron los siguientes grupos de archivos duplicados ---")
    archivos_a_eliminar = []
    for lista_archivos in duplicados.values():
        # Ordena la lista alfabéticamente para mantener siempre el mismo archivo como "original"
        lista_archivos.sort()
        original, *copias = lista_archivos
        print(f"\n  Original (se conservará): {original}")
        for copia in copias:
            print(f"    - Duplicado (a eliminar): {copia}")
            archivos_a_eliminar.append(copia)

    if not archivos_a_eliminar:
        print("\nNo hay archivos para borrar.")
        return

    print(f"\n-----------------------------------------------------------------")
    print(f"Total de archivos a eliminar: {len(archivos_a_eliminar)}")
    
    try:
        confirmacion = raw_input("¿Desea continuar y eliminar estos archivos? (s/n): ")
    except NameError:
        confirmacion = input("¿Desea continuar y eliminar estos archivos? (s/n): ")

    if confirmacion.lower() == 's':
        print("\nEliminando archivos...")
        for ruta_archivo in archivos_a_eliminar:
            try:
                os.remove(ruta_archivo)
                print(f"  Eliminado: {ruta_archivo}")
            except OSError as e:
                print(f"  Error al eliminar {ruta_archivo}: {e}")
        print("\n¡Limpieza completada!")
    else:
        print("\nOperación cancelada por el usuario. No se eliminó ningún archivo.")

if __name__ == "__main__":
    main()