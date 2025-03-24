const express = require('express');
const cors = require('cors');
const PokerOddsCalculator = require('poker-odds-calculator');
const Card = PokerOddsCalculator.Card;
const app = express();
const port = 3000;

// Habilitar CORS para todas las solicitudes
app.use(cors());

app.use(express.json());

app.post('/calculate', (req, res) => {
    try {
        const { playersHoleCards, communityCards } = req.body;

        // Validar los datos recibidos
        if (!playersHoleCards || !Array.isArray(playersHoleCards) || playersHoleCards.length < 2) {
            return res.status(400).json({ error: 'Se requieren al menos 2 jugadores con cartas.' });
        }

        if (!communityCards || !Array.isArray(communityCards)) {
            return res.status(400).json({ error: 'Las cartas comunitarias deben ser un arreglo.' });
        }

        // Convertir las cartas a objetos Card
        const players = playersHoleCards.map(playerCards =>
            playerCards.map(card => new Card(card))
        );
        const board = communityCards.map(card => new Card(card));

        // Calcular las probabilidades
        const calculator = PokerOddsCalculator.calculate(players, board);
        const results = {};
        calculator.equities.forEach((equity, index) => {
            results[`Jugador ${index + 1}`] = {
                probability: (equity.getEquity() * 100).toFixed(2),
                hand: equity.getHand() || 'Desconocida'
            };
        });

        res.json(results);
    } catch (error) {
        console.error('Error en /calculate:', error);
        res.status(500).json({ error: 'Error interno del servidor' });
    }
});

app.listen(port, () => {
    console.log(`Servidor escuchando en http://localhost:${port}`);
});
