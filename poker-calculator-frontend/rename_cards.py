import os

# Mapeo de nombres largos a nombres cortos
rank_map = {
    'ace': 'A',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
    '10': 'T',
    'jack': 'J',
    'queen': 'Q',
    'king': 'K'
}

suit_map = {
    'hearts': 'h',
    'spades': 's',
    'clubs': 'c',
    'diamonds': 'd'
}

# Directorio donde están las imágenes
cards_dir = "cards"

# Asegúrate de que la carpeta exista
if not os.path.exists(cards_dir):
    print(f"La carpeta {cards_dir} no existe. Créala y coloca las imágenes allí.")
    exit(1)

# Lista de archivos en la carpeta
for filename in os.listdir(cards_dir):
    if filename.endswith(".png"):
        # Ejemplo: "ace_of_hearts.png" → ["ace", "of", "hearts.png"]
        parts = filename.split("_")
        if len(parts) != 3:
            print(f"Nombre de archivo no esperado: {filename}")
            continue

        rank_part = parts[0]  # "ace"
        suit_part = parts[2].replace(".png", "")  # "hearts"

        # Mapear a los nombres cortos
        if rank_part not in rank_map or suit_part not in suit_map:
            print(f"No se puede mapear: {filename}")
            continue

        new_rank = rank_map[rank_part]  # "A"
        new_suit = suit_map[suit_part]  # "h"
        new_name = f"{new_rank}{new_suit}.png"  # "Ah.png"

        # Renombrar el archivo
        old_path = os.path.join(cards_dir, filename)
        new_path = os.path.join(cards_dir, new_name)
        os.rename(old_path, new_path)
        print(f"Renombrado: {filename} → {new_name}")

print("Renombrado completado.")
