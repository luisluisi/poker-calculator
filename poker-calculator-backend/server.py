import http.server
import socketserver
import json
import random
from collections import Counter
from itertools import combinations, product
import sys
import traceback
import time # Para medir tiempo

PORT = 3000
NUM_SIMULATIONS = 10000 # Mantener simulaciones (puede ser necesario bajar si es muy lento)

# --- Definiciones de Poker ---
suits = ['H', 'S', 'C', 'D']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
deck = [rank + suit for rank in ranks for suit in suits]
rank_values = {rank: idx + 2 for idx, rank in enumerate(ranks)}
hand_names = {9: "Escalera Real", 8: "Escalera de Color", 7: "Póker", 6: "Full House", 5: "Color", 4: "Escalera", 3: "Trío", 2: "Doble Par", 1: "Par", 0: "Carta Alta"}

# --- Lógica de Rangos (NUEVO) ---

# 1. Definiciones de Rangos Básicos (Ejemplos muy simplificados)
# Usamos notación estándar: AA, KQs, T9o, 22+, A5s+, KTo+, etc.
# Estos son conjuntos de strings que representan los tipos de manos.
# (Referencia rápida: '+' significa 'y mejor', 's'=suited, 'o'=offsuit)

# Rango Tight (Ej: ~10-15% de manos - típico UTG/MP temprano)
RANGE_TIGHT = {
    'AA', 'KK', 'QQ', 'JJ', 'TT', '99', '88', # Pares altos/medios
    'AKs', 'AQs', 'AJs', 'ATs', # Ases suited altos
    'KQs', 'KJs', 'KTs',       # Reyes suited altos
    'QJs', 'QTs',             # Reinas suited altas
    'JTs',                    # Jotas suited altas
    'AKo', 'AQo'              # Ases offsuit muy altos
}

# Rango Medium (Ej: ~20-30% de manos - típico MP/CO)
RANGE_MEDIUM = RANGE_TIGHT | { # Incluye el rango tight y añade más
    '77', '66', '55',         # Pares medios/bajos
    'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s', # Resto Ases suited
    'K9s',                    # Reyes suited
    'Q9s',                    # Reinas suited
    'J9s',                    # Jotas suited
    'T9s', 'T8s',             # Dieces suited
    '98s', '97s',             # Nueves suited
    '87s', '86s',             # Ochos suited
    '76s', '75s',             # Sietes suited
    '65s', '64s',             # Seises suited
    '54s',                    # Cincos suited
    'AJo', 'ATo',             # Ases offsuit medios
    'KQo', 'KJo', 'KTo',       # Reyes offsuit altos
    'QJo', 'QTo',             # Reinas offsuit altas
    'JTo'                     # Jotas offsuit altas
}

# Rango Wide (Ej: ~40-60%+ de manos - típico BTN/SB/BB defensa)
RANGE_WIDE = RANGE_MEDIUM | { # Incluye el rango medium y añade más
    '44', '33', '22',          # Pares bajos
    'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s', # Resto Reyes suited
    'Q8s', 'Q7s', 'Q6s', 'Q5s', # Resto Reinas suited
    'J8s', 'J7s',              # Resto Jotas suited
    'T7s',
    '96s',
    '85s',
    '74s',
    '63s',
    '53s', '52s',
    '43s', '42s',
    '32s',
    'A9o', 'A8o', 'A7o', 'A6o', 'A5o', 'A4o', 'A3o', 'A2o', # Resto Ases offsuit
    'K9o', 'K8o', 'K7o', 'K6o', 'K5o', # Reyes offsuit medios/bajos
    'Q9o', 'Q8o',              # Reinas offsuit medias
    'J9o', 'J8o',              # Jotas offsuit medias
    'T9o', 'T8o',              # Dieces offsuit
    '98o', '97o',              # Nueves offsuit
    '87o', '86o',              # Ochos offsuit
    '76o'                      # Sietes offsuit
}

# 2. Mapeo de Posición a Rango (Simplificado)
# Asume mesa 9-max. Puedes ajustar esto.
POSITION_TO_RANGE = {
    "UTG": RANGE_TIGHT,
    "UTG+1": RANGE_TIGHT,
    "MP1": RANGE_MEDIUM,
    "MP2": RANGE_MEDIUM,
    "HJ": RANGE_MEDIUM, # Hijack
    "CO": RANGE_MEDIUM, # Cutoff
    "BTN": RANGE_WIDE,  # Button
    "SB": RANGE_WIDE,   # Small Blind
    "BB": RANGE_WIDE,   # Big Blind
    # Añadir un default por si la posición no coincide
    "default": RANGE_WIDE # O podrías usar 100% (todas las manos)
}

# 3. Funciones Auxiliares para generar combos específicos
def get_pair_combos(rank):
    """Genera los 6 combos de un par (ej: AA -> AcAd, AcAh, AcAs, AdAh, AdAs, AhAs)"""
    if rank not in ranks: return set()
    cards = [rank + s for s in suits]
    return set(frozenset(combo) for combo in combinations(cards, 2))

def get_suited_combos(r1, r2):
    """Genera los 4 combos suited (ej: AKs -> AsKs, AhKh, AdKd, AcKc)"""
    if r1 not in ranks or r2 not in ranks or r1 == r2: return set()
    # Asegurar orden (Rey-As -> AKs, no KAs)
    r_high, r_low = (r1, r2) if rank_values[r1] > rank_values[r2] else (r2, r1)
    return set(frozenset([r_high + s, r_low + s]) for s in suits)

def get_offsuit_combos(r1, r2):
    """Genera los 12 combos offsuit (ej: AKo -> AcKd, AcKh, AcKs, AdKc, AdKh...)"""
    if r1 not in ranks or r2 not in ranks or r1 == r2: return set()
    r_high, r_low = (r1, r2) if rank_values[r1] > rank_values[r2] else (r2, r1)
    combos = set()
    for s1 in suits:
        for s2 in suits:
            if s1 != s2: # Asegurar que son offsuit
                combos.add(frozenset([r_high + s1, r_low + s2]))
    return combos

# 4. Función para obtener todos los combos de un rango definido por notación
# Cache para no regenerar combos de rango cada vez
range_combo_cache = {}

def get_all_combos_for_range(range_notation_set):
    """
    Convierte un set de notaciones de rango (ej: {'AA', 'KQs', 'T9o'})
    en un set de todos los combos específicos (frozenset({'Ac','Ad'}), frozenset({'Ks','Qs'}), ...)
    """
    # Usar tuple ordenada como clave de caché porque los sets no son hashables
    cache_key = tuple(sorted(list(range_notation_set)))
    if cache_key in range_combo_cache:
        return range_combo_cache[cache_key]

    all_combos = set()
    for notation in range_notation_set:
        if len(notation) == 2: # Par, ej: QQ
            all_combos.update(get_pair_combos(notation[0]))
        elif len(notation) == 3:
            r1, r2, type = notation[0], notation[1], notation[2]
            if type == 's': # Suited, ej: KQs
                all_combos.update(get_suited_combos(r1, r2))
            elif type == 'o': # Offsuit, ej: T9o
                all_combos.update(get_offsuit_combos(r1, r2))
        # Podríamos añadir lógica para rangos como A5s+ o 88+ aquí, pero lo dejamos simple por ahora
    print(f"Generados {len(all_combos)} combos para rango: {range_notation_set}")
    range_combo_cache[cache_key] = all_combos
    return all_combos

# --- Lógica de Evaluación de Manos (sin cambios) ---
# ... (evaluate_hand function remains exactly the same) ...
def evaluate_hand(seven_cards):
    best_score = (-1, [])
    for hand_tuple in combinations(seven_cards, 5):
        hand = list(hand_tuple); hand_ranks_str = sorted([card[0] for card in hand], key=lambda r: rank_values[r], reverse=True); hand_suits = [card[1] for card in hand]
        is_flush = len(set(hand_suits)) == 1; rank_nums = sorted([rank_values[r] for r in hand_ranks_str], reverse=True)
        is_ace_low_straight = (set(hand_ranks_str) == {'A', '2', '3', '4', '5'}); is_straight = False
        if not is_ace_low_straight: is_straight = all(rank_nums[i] == rank_nums[0] - i for i in range(5))
        elif is_ace_low_straight: is_straight = True; rank_nums = [5, 4, 3, 2, 1]
        rank_counts = Counter(hand_ranks_str); sorted_counts = sorted(rank_counts.items(), key=lambda item: (item[1], rank_values[item[0]]), reverse=True)
        counts = [count for rank, count in sorted_counts]; ordered_rank_values = [rank_values[rank] for rank, count in sorted_counts]
        score = (-1, [])
        if is_straight and is_flush:
             if rank_nums[0] == 14 and not is_ace_low_straight: score = (9, [])
             else: score = (8, [rank_nums[0]])
        elif counts[0] == 4: score = (7, [ordered_rank_values[0], ordered_rank_values[1]])
        elif counts == [3, 2]: score = (6, [ordered_rank_values[0], ordered_rank_values[1]])
        elif is_flush: score = (5, rank_nums)
        elif is_straight: score = (4, [rank_nums[0]])
        elif counts[0] == 3: score = (3, [ordered_rank_values[0]] + ordered_rank_values[1:3])
        elif counts == [2, 2, 1]: score = (2, [ordered_rank_values[0], ordered_rank_values[1], ordered_rank_values[2]])
        elif counts[0] == 2: score = (1, [ordered_rank_values[0]] + ordered_rank_values[1:4])
        else: score = (0, rank_nums)
        if score > best_score: best_score = score
    return best_score


# --- Lógica de Simulación (MODIFICADA para usar Rangos) ---
def simulate_game(players_data, community_cards, num_simulations=NUM_SIMULATIONS):
    """
    Simula el juego usando rangos de manos basados en posición para los oponentes.
    """
    start_time = time.time()
    num_players = len(players_data)
    if num_players < 2: raise ValueError("Se necesitan al menos 2 jugadores.")
    hero_hole_cards = players_data[0].get('holeCards', [])
    if len(hero_hole_cards) != 2: raise ValueError("Héroe debe tener 2 cartas.")

    print(f"Iniciando simulación con RANGOS: {num_players} jug, Comm: {community_cards}, Sims: {num_simulations}")
    wins = [0] * num_players; ties = [0] * num_players
    best_overall_hand_score = [(-1, []) for _ in range(num_players)]
    range_errors = 0 # Contador si no se pueden asignar manos del rango

    # Pre-calcular combos para los rangos de los oponentes una vez
    opponent_range_combos = []
    for p_idx in range(1, num_players):
        pos = players_data[p_idx].get('position', 'default')
        range_notation = POSITION_TO_RANGE.get(pos, POSITION_TO_RANGE['default'])
        opponent_range_combos.append(get_all_combos_for_range(range_notation))
        print(f"  Oponente {p_idx} (Pos: {pos}) usando rango con {len(opponent_range_combos[-1])} combos.")


    # --- Bucle de Simulación ---
    for i in range(num_simulations):
        # Cartas conocidas al inicio de esta simulación: Héroe + Comunitarias
        current_known_cards = set(community_cards) | set(hero_hole_cards)
        current_remaining_deck = [card for card in deck if card not in current_known_cards]
        random.shuffle(current_remaining_deck) # Barajar solo una vez por sim

        assigned_opponent_cards = [] # Cartas asignadas a oponentes en esta simulación
        possible_to_deal = True

        # 1. Asignar cartas a Oponentes según su rango
        for opp_idx in range(num_players - 1): # Índice relativo a oponentes (0 a N-2)
            player_data_idx = opp_idx + 1 # Índice en players_data (1 a N-1)
            range_combos = opponent_range_combos[opp_idx] # Combos precalculados para este oponente

            # Filtrar los combos del rango que son posibles con las cartas restantes *actuales*
            # (Considera cartas ya asignadas a oponentes anteriores en esta simulación)
            available_cards_set = set(current_remaining_deck)
            possible_hands_in_range = [
                list(combo) for combo in range_combos
                if all(card in available_cards_set for card in combo)
            ]

            if possible_hands_in_range:
                # Elegir una mano aleatoria del rango posible
                chosen_hand = random.choice(possible_hands_in_range)
                assigned_opponent_cards.append(chosen_hand)
                # Quitar cartas elegidas de la baraja restante para esta simulación
                current_remaining_deck.remove(chosen_hand[0])
                current_remaining_deck.remove(chosen_hand[1])
            else:
                # No quedan manos del rango! ¿Qué hacer?
                # Opción 1: Asignar mano aleatoria (menos preciso pero evita parar)
                if len(current_remaining_deck) >= 2:
                     chosen_hand = current_remaining_deck[:2]
                     assigned_opponent_cards.append(chosen_hand)
                     current_remaining_deck = current_remaining_deck[2:]
                     if i == 0: # Log solo una vez para no spamear
                          print(f"  AVISO: No se encontraron manos del rango para Oponente {player_data_idx} (Pos: {players_data[player_data_idx]['position']}). Asignando mano aleatoria.")
                     range_errors += 1
                else:
                    # Opción 2: Marcar simulación como inválida y continuar
                    print(f"  ERROR: No quedan cartas suficientes para Oponente {player_data_idx}. Saltando simulación {i}.")
                    possible_to_deal = False
                    break # Salir del bucle de oponentes

        if not possible_to_deal: continue # Saltar al siguiente ciclo de simulación

        # 2. Repartir cartas comunitarias restantes
        cards_to_deal_board = 5 - len(community_cards)
        if len(current_remaining_deck) < cards_to_deal_board:
             print(f"  ERROR: No quedan cartas suficientes para la mesa. Saltando simulación {i}.")
             continue # Saltar al siguiente ciclo de simulación
        simulated_board = community_cards + current_remaining_deck[:cards_to_deal_board]

        # 3. Evaluar Manos y Ganadores
        player_scores = []
        current_sim_best_score = (-1, [])
        for player_idx in range(num_players):
            if player_idx == 0: # Héroe
                full_hand = hero_hole_cards + simulated_board
            else: # Oponente (usar cartas asignadas)
                full_hand = assigned_opponent_cards[player_idx - 1] + simulated_board

            score = evaluate_hand(full_hand)
            player_scores.append(score)
            if score > best_overall_hand_score[player_idx]: best_overall_hand_score[player_idx] = score
            if score > current_sim_best_score: current_sim_best_score = score

        # Determinar ganadores/empates
        winners_indices = [idx for idx, score in enumerate(player_scores) if score == current_sim_best_score]
        if len(winners_indices) == 1: wins[winners_indices[0]] += 1
        elif len(winners_indices) > 1:
            for idx in winners_indices: ties[idx] += 1

    # --- Calcular Probabilidades Finales ---
    probabilities = []
    if num_simulations > 0:
        effective_sims = num_simulations - range_errors # Podríamos ajustar por simulaciones donde no se pudo asignar rango
        if effective_sims <= 0: effective_sims = num_simulations # Evitar división por cero si todos fallaron

        for i in range(num_players):
             # Calcular sobre simulaciones efectivas o totales? Usemos totales por simplicidad.
             win_or_tie_prob = (wins[i] + ties[i]) / num_simulations * 100
             probabilities.append(round(win_or_tie_prob, 2))
    else: probabilities = [0.0] * num_players

    end_time = time.time()
    duration = end_time - start_time
    print(f"Simulación (rangos) finalizada en {duration:.2f} seg. Errores de rango: {range_errors}/{num_simulations}")
    print(f"Probabilidades (Ganar o Empatar) %: {probabilities}")
    best_hand_names = [hand_names.get(s[0], "N/A") for s in best_overall_hand_score]
    print(f"Mejores manos encontradas: {best_hand_names}")

    return probabilities, best_overall_hand_score

# --- Servidor HTTP (Sin cambios en la lógica del handler, ya recibe 'players') ---
class PokerHandler(http.server.SimpleHTTPRequestHandler):
    def _send_cors_headers(self): self.send_header('Access-Control-Allow-Origin', '*'); self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS'); self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    def do_OPTIONS(self): self.send_response(200); self._send_cors_headers(); self.end_headers(); print("OPTIONS OK")
    def do_GET(self):
         if self.path == '/test': self.send_response(200); self.send_header('Content-Type', 'application/json'); self._send_cors_headers(); self.end_headers(); self.wfile.write(json.dumps({"message": "Server Python OK!"}).encode('utf-8')); print("GET /test OK")
         else: self.send_response(404); self.send_header('Content-Type', 'application/json'); self._send_cors_headers(); self.end_headers(); self.wfile.write(json.dumps({"error": "GET Endpoint no encontrado."}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/calculate':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data_bytes = self.rfile.read(content_length)
                post_data_str = post_data_bytes.decode('utf-8')
                print(f"Datos POST recibidos: {post_data_str}")
                data = json.loads(post_data_str)

                players_data_raw = data.get('players', [])
                community_cards_raw = data.get('communityCards', [])

                # --- Validación Estricta de Entrada (Sin Cambios Necesarios) ---
                if not isinstance(players_data_raw, list) or len(players_data_raw) < 2: raise ValueError("Se requieren >= 2 jugadores (en 'players').")
                if not isinstance(community_cards_raw, list) or len(community_cards_raw) > 5: raise ValueError("'communityCards' debe ser lista (0-5).")

                players_data_validated = []
                community_cards_validated = []
                all_input_cards = set()

                # Validar Héroe
                hero_data = players_data_raw[0]; hero_hole_cards = hero_data.get('holeCards'); hero_position = hero_data.get('position')
                if not isinstance(hero_hole_cards, list) or len(hero_hole_cards) != 2: raise ValueError("Héroe: 2 'holeCards'.")
                if not hero_position or not isinstance(hero_position, str): raise ValueError("Héroe: 'position' (string).")
                validated_hero_cards = []
                for card_str in hero_hole_cards:
                     if not isinstance(card_str, str) or len(card_str)!=2 or card_str[0] not in ranks or card_str[1] not in suits: raise ValueError(f"Héroe: Carta inválida '{card_str}'.")
                     if card_str in all_input_cards: raise ValueError(f"Duplicado '{card_str}' (Héroe).")
                     all_input_cards.add(card_str); validated_hero_cards.append(card_str)
                players_data_validated.append({'holeCards': validated_hero_cards, 'position': hero_position})

                # Validar Oponentes
                for i, opp_data in enumerate(players_data_raw[1:]):
                     opp_num = i + 1; opp_position = opp_data.get('position')
                     if not opp_position or not isinstance(opp_position, str): raise ValueError(f"Oponente {opp_num}: 'position' (string).")
                     players_data_validated.append({'holeCards': [], 'position': opp_position}) # Guardar solo posición

                # Validar Comunitarias
                for card_str in community_cards_raw:
                      if not isinstance(card_str, str) or len(card_str)!=2 or card_str[0] not in ranks or card_str[1] not in suits: raise ValueError(f"Comunitaria inválida: '{card_str}'.")
                      if card_str in all_input_cards: raise ValueError(f"Duplicado '{card_str}' (Comunitaria).")
                      all_input_cards.add(card_str); community_cards_validated.append(card_str)

                # --- Ejecutar simulación (AHORA USA RANGOS) ---
                probabilities, best_hands_scores = simulate_game(players_data_validated, community_cards_validated)

                # --- Preparar y enviar respuesta JSON (sin cambios) ---
                result = {};
                for i, (prob, hand_score) in enumerate(zip(probabilities, best_hands_scores)):
                    hand_name = hand_names.get(hand_score[0], "N/A")
                    result[f"player{i+1}"] = {"probability": prob, "hand": hand_name}

                response_body = json.dumps(result).encode('utf-8'); self.send_response(200); self.send_header('Content-Type', 'application/json'); self._send_cors_headers(); self.end_headers(); self.wfile.write(response_body)
                print(f"Respuesta (rangos) enviada: {result}")

            # --- Manejo de Errores (sin cambios) ---
            except json.JSONDecodeError: print("Error: JSON inválido."); self.send_response(400); self.send_header('Content-Type', 'application/json'); self._send_cors_headers(); self.end_headers(); self.wfile.write(json.dumps({"error": "JSON inválido."}).encode('utf-8'))
            except ValueError as ve: print(f"Error validación: {ve}"); self.send_response(400); self.send_header('Content-Type', 'application/json'); self._send_cors_headers(); self.end_headers(); self.wfile.write(json.dumps({"error": str(ve)}).encode('utf-8')) # Enviar error de validación al cliente
            except Exception as e: print(f"Error inesperado: {type(e).__name__}: {e}"); traceback.print_exc(); self.send_response(500); self.send_header('Content-Type', 'application/json'); self._send_cors_headers(); self.end_headers(); self.wfile.write(json.dumps({"error": f"Error interno: {type(e).__name__}"}).encode('utf-8'))
        else: self.send_response(404); self.send_header('Content-Type', 'application/json'); self._send_cors_headers(); self.end_headers(); self.wfile.write(json.dumps({"error": "Endpoint POST no encontrado."}).encode('utf-8'))

# --- Función para correr el servidor (sin cambios) ---
def run_server(server_class=socketserver.TCPServer, handler_class=PokerHandler, port=PORT):
    server_class.allow_reuse_address = True
    try: httpd = server_class(("", port), handler_class); print(f"Servidor Python (con Rangos) iniciado en http://localhost:{port}\nPresiona Ctrl+C para detener."); httpd.serve_forever()
    except OSError as oe: print(f"Error puerto {port}: {oe} (¿Ya en uso?)"); sys.exit(1)
    except KeyboardInterrupt: print("\nDeteniendo..."); httpd.shutdown(); httpd.server_close(); print("Servidor detenido."); sys.exit(0)
    except Exception as e: print(f"Error fatal: {e}"); traceback.print_exc(); sys.exit(1)

if __name__ == "__main__": run_server()