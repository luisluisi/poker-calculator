import http.server
import socketserver
import json
import random
from collections import Counter
from itertools import combinations
import sys

PORT = 3000

suits = ['h', 's', 'c', 'd']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
deck = [rank + suit for rank in ranks for suit in suits]
rank_values = {rank: idx + 2 for idx, rank in enumerate(ranks)}

hand_names = {
    9: "Escalera Real",
    8: "Escalera de Color",
    7: "Póker",
    6: "Full House",
    5: "Color",
    4: "Escalera",
    3: "Trío",
    2: "Doble Par",
    1: "Par",
    0: "Carta Alta"
}

def evaluate_hand(cards):
    print(f"Evaluando mano: {cards}")
    try:
        best_score = (0, [])
        for hand in combinations(cards, 5):
            ranks = sorted([card[0] for card in hand], key=lambda r: rank_values[r], reverse=True)
            suits = [card[1] for card in hand]
            rank_counts = Counter(ranks)
            suit_counts = Counter(suits)

            is_flush = max(suit_counts.values()) == 5
            rank_nums = sorted([rank_values[r] for r in ranks], reverse=True)
            is_straight = False
            if rank_nums == list(range(rank_nums[0], rank_nums[0] - 5, -1)):
                is_straight = True
            elif rank_nums == [14, 5, 4, 3, 2]:
                is_straight = True
                rank_nums = [5, 4, 3, 2, 1]

            rank_counts_sorted = sorted(rank_counts.items(), key=lambda x: (x[1], rank_values[x[0]]), reverse=True)
            counts = [count for rank, count in rank_counts_sorted]
            high_cards = [rank_values[rank] for rank, count in rank_counts_sorted]

            if is_flush and is_straight:
                if rank_nums[0] == 14:
                    score = (9, rank_nums)
                else:
                    score = (8, rank_nums)
            elif counts[0] == 4:
                score = (7, [high_cards[0], high_cards[1]])
            elif counts[0] == 3 and counts[1] >= 2:
                score = (6, [high_cards[0], high_cards[1]])
            elif is_flush:
                score = (5, rank_nums)
            elif is_straight:
                score = (4, rank_nums)
            elif counts[0] == 3:
                score = (3, [high_cards[0]] + high_cards[1:3])
            elif counts[0] == 2 and counts[1] == 2:
                score = (2, high_cards[:2] + [high_cards[2]])
            elif counts[0] == 2:
                score = (1, [high_cards[0]] + high_cards[1:3])
            else:
                score = (0, rank_nums)

            best_score = max(best_score, score, key=lambda s: (s[0], s[1]))

        print(f"Mejor puntaje: {best_score}")
        return best_score
    except Exception as e:
        print(f"Error en evaluate_hand: {str(e)}")
        raise

def simulate_game(players_hole_cards, community_cards, num_simulations=10):
    stage = (
        "preflop" if len(community_cards) == 0 else
        "1 carta comunitaria" if len(community_cards) == 1 else
        "2 cartas comunitarias" if len(community_cards) == 2 else
        "flop" if len(community_cards) == 3 else
        "turn" if len(community_cards) == 4 else
        "river"
    )
    print(f"Simulando juego con {len(players_hole_cards)} jugadores, etapa: {stage}, community: {community_cards}")
    try:
        known_cards = set(community_cards)
        for hole_cards in players_hole_cards:
            known_cards.update(hole_cards)
        remaining_deck = [card for card in deck if card not in known_cards]
        print(f"Cartas restantes: {len(remaining_deck)}")

        cards_to_deal = 5 - len(community_cards)
        if cards_to_deal < 0:
            return {"error": "Too many community cards"}

        wins = [0] * len(players_hole_cards)
        ties = [0] * len(players_hole_cards)
        best_hands = [None] * len(players_hole_cards)

        for i in range(num_simulations):
            if i % 10 == 0:
                print(f"Simulación {i}/{num_simulations}")
            random.shuffle(remaining_deck)
            simulated_community = community_cards + remaining_deck[:cards_to_deal]

            scores = []
            for player_idx, hole_cards in enumerate(players_hole_cards):
                full_hand = hole_cards + simulated_community
                score = evaluate_hand(full_hand)
                scores.append(score)
                if best_hands[player_idx] is None or score > best_hands[player_idx]:
                    best_hands[player_idx] = score

            max_score = max(scores)
            winners = [i for i, score in enumerate(scores) if score == max_score]
            if len(winners) == 1:
                wins[winners[0]] += 1
            else:
                for winner in winners:
                    ties[winner] += 1

        total_games = num_simulations
        probabilities = []
        for i in range(len(players_hole_cards)):
            win_prob = (wins[i] / total_games) * 100
            tie_prob = (ties[i] / total_games) * 100
            probabilities.append(round(win_prob + tie_prob / len(players_hole_cards), 2))

        print(f"Probabilities: {probabilities}")
        return probabilities, best_hands
    except Exception as e:
        print(f"Error en simulate_game: {str(e)}")
        raise

class PokerHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        print(f"Recibida solicitud POST: {self.path}")
        if self.path == '/calculate':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                print(f"Datos recibidos: {post_data.decode('utf-8')}")
                data = json.loads(post_data.decode('utf-8'))

                players_hole_cards = data.get('playersHoleCards', [])
                community_cards = data.get('communityCards', [])

                # Convertir todas las cartas a mayúsculas
                players_hole_cards = [[card.upper() for card in hole_cards] for hole_cards in players_hole_cards]
                community_cards = [card.upper() for card in community_cards]

                if len(players_hole_cards) < 2:
                    self.send_error(400, "At least 2 players are required")
                    return

                for i, hole_cards in enumerate(players_hole_cards):
                    if len(hole_cards) != 2:
                        self.send_error(400, f"Player {i+1} must have exactly 2 hole cards")
                        return

                if len(community_cards) > 5:
                    self.send_error(400, "Community cards must be between 0 and 5")
                    return

                all_cards = set()
                for hole_cards in players_hole_cards:
                    for card in hole_cards:
                        if card == 'JOKER1' or card == 'JOKER2':
                            self.send_error(400, f"Jokers are not supported in calculations: {card}")
                            return
                        if card not in deck:
                            self.send_error(400, f"Invalid card: {card}")
                            return
                        if card in all_cards:
                            self.send_error(400, f"Duplicate card: {card}")
                            return
                        all_cards.add(card)
                for card in community_cards:
                    if card == 'JOKER1' or card == 'JOKER2':
                        self.send_error(400, f"Jokers are not supported in calculations: {card}")
                        return
                    if card not in deck:
                        self.send_error(400, f"Invalid card: {card}")
                        return
                    if card in all_cards:
                        self.send_error(400, f"Duplicate card: {card}")
                        return
                    all_cards.add(card)

                probabilities, best_hands = simulate_game(players_hole_cards, community_cards)

                result = {}
                for i, (prob, hand) in enumerate(zip(probabilities, best_hands)):
                    hand_name = hand_names[hand[0]]
                    result[f"player{i+1}"] = {"probability": prob, "hand": hand_name}

                print(f"Enviando respuesta: {result}")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                print(f"Error en do_POST: {str(e)}")
                self.send_error(500, f"Server error: {str(e)}")
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        print("Recibida solicitud OPTIONS")
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        print("Recibida solicitud GET")
        if self.path == '/test':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Server is working"}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    while True:
        try:
            with socketserver.TCPServer(("", PORT), PokerHandler) as httpd:
                print(f"Server running on port {PORT}")
                httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"Server error: {str(e)}")
            print("Restarting server in 5 seconds...")
            import time
            time.sleep(5)

if __name__ == "__main__":
    run_server()
