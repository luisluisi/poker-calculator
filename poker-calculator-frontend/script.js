function addPlayer() {
    const playersDiv = document.getElementById('players');
    const playerCount = playersDiv.children.length + 1;
    const newPlayerDiv = document.createElement('div');
    newPlayerDiv.className = 'player';
    newPlayerDiv.innerHTML = `
        <label>Jugador ${playerCount} (ej. Ah Kh):</label>
        <input type="text" class="hole-cards" placeholder="Ah Kh" oninput="updateCards(this)">
        <div class="card-display"></div>
    `;
    playersDiv.appendChild(newPlayerDiv);
}

function updateCards(input) {
    let value = input.value.toUpperCase();
    let cards = value.split(/\s+/).filter(card => card !== '');
    const cardDisplay = input.nextElementSibling;
    cardDisplay.innerHTML = '';
    if (cards.length === 0) return;
    cards.forEach(card => {
        // Validar que la carta tenga el formato correcto
        const isValidCard = /^(A|K|Q|J|T|[2-9])(H|S|C|D)$/i.test(card) || card === 'JOKER1' || card === 'JOKER2';
        if (isValidCard) {
            console.log(`Intentando cargar carta: ${card}`);
            const img = document.createElement('img');
            const cardName = card;
            img.src = `cards/${cardName}.png`;
            img.alt = card;
            img.onerror = () => {
                console.error(`Error al cargar la imagen: cards/${cardName}.png`);
                cardDisplay.innerHTML += `<span style="color: red; font-size: 0.9rem;">Carta no encontrada: ${card}</span>`;
            };
            img.onload = () => {
                console.log(`Imagen cargada correctamente: cards/${cardName}.png`);
            };
            cardDisplay.appendChild(img);
        } else {
            console.log(`Carta inválida ignorada: ${card}`);
        }
    });
}

function updateCommunityCards() {
    let value = document.getElementById('communityCards').value.toUpperCase();
    let communityCards = value.split(/\s+/).filter(card => card !== '');
    const cardDisplay = document.getElementById('communityCardDisplay');
    cardDisplay.innerHTML = '';
    if (communityCards.length === 0) return;
    communityCards.forEach(card => {
        // Validar que la carta tenga el formato correcto
        const isValidCard = /^(A|K|Q|J|T|[2-9])(H|S|C|D)$/i.test(card) || card === 'JOKER1' || card === 'JOKER2';
        if (isValidCard) {
            console.log(`Intentando cargar carta comunitaria: ${card}`);
            const img = document.createElement('img');
            const cardName = card;
            img.src = `cards/${cardName}.png`;
            img.alt = card;
            img.onerror = () => {
                console.error(`Error al cargar la imagen: cards/${cardName}.png`);
                cardDisplay.innerHTML += `<span style="color: red; font-size: 0.9rem;">Carta no encontrada: ${card}</span>`;
            };
            img.onload = () => {
                console.log(`Imagen cargada correctamente: cards/${cardName}.png`);
            };
            cardDisplay.appendChild(img);
        } else {
            console.log(`Carta comunitaria inválida ignorada: ${card}`);
        }
    });
}

function updateCommunityCardsInput() {
    const gameStage = document.getElementById('gameStage').value;
    const communityCardsInput = document.getElementById('communityCards');
    let placeholder = '';
    if (gameStage === 'preflop') {
        placeholder = 'Sin cartas comunitarias (preflop)';
        communityCardsInput.disabled = true;
        communityCardsInput.value = '';
    } else if (gameStage === '1card') {
        placeholder = 'Th (1 carta)';
        communityCardsInput.disabled = false;
    } else if (gameStage === '2cards') {
        placeholder = 'Th 9s (2 cartas)';
        communityCardsInput.disabled = false;
    } else if (gameStage === 'flop') {
        placeholder = 'Th 9s 2c (3 cartas)';
        communityCardsInput.disabled = false;
    } else if (gameStage === 'turn') {
        placeholder = 'Th 9s 2c 4d (4 cartas)';
        communityCardsInput.disabled = false;
    } else if (gameStage === 'river') {
        placeholder = 'Th 9s 2c 4d 7h (5 cartas)';
        communityCardsInput.disabled = false;
    }
    communityCardsInput.placeholder = placeholder;
    updateCommunityCards();
}

function showCardLegend() {
    const cardLegend = document.getElementById('cardLegend');
    if (cardLegend.style.display === 'block') {
        cardLegend.style.display = 'none';
        return;
    }
    cardLegend.style.display = 'block';
    cardLegend.innerHTML = '<h3>Nombres de las Cartas</h3>';

    const ranks = {
        'A': 'As',
        'K': 'Rey',
        'Q': 'Reina',
        'J': 'Jota',
        'T': 'Diez',
        '9': 'Nueve',
        '8': 'Ocho',
        '7': 'Siete',
        '6': 'Seis',
        '5': 'Cinco',
        '4': 'Cuatro',
        '3': 'Tres',
        '2': 'Dos'
    };
    const suits = {
        'h': 'Corazones',
        's': 'Picas',
        'c': 'Tréboles',
        'd': 'Diamantes'
    };

    for (let rank in ranks) {
        for (let suit in suits) {
            const card = `${rank}${suit}`.toUpperCase();
            console.log(`Construyendo carta: ${card}`);

            const legendItem = document.createElement('div');
            legendItem.className = 'legend-item';

            const img = document.createElement('img');
            img.src = `cards/${card}.png`;
            img.alt = card;
            img.onerror = () => {
                console.error(`Error al cargar la imagen en la leyenda: cards/${card}.png`);
                legendItem.innerHTML += `<span style="color: red; font-size: 0.9rem;">Carta no encontrada: ${card}</span>`;
            };
            img.onload = () => {
                console.log(`Imagen cargada correctamente en la leyenda: cards/${card}.png`);
            };

            const span = document.createElement('span');
            span.textContent = `${ranks[rank]} de ${suits[suit]} (${card})`;

            legendItem.appendChild(img);
            legendItem.appendChild(span);
            cardLegend.appendChild(legendItem);
        }
    }

    ['JOKER1', 'JOKER2'].forEach(joker => {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';

        const img = document.createElement('img');
        img.src = `cards/${joker}.png`;
        img.alt = joker;
        img.onerror = () => {
            console.error(`Error al cargar la imagen en la leyenda: cards/${joker}.png`);
            legendItem.innerHTML += `<span style="color: red; font-size: 0.9rem;">Carta no encontrada: ${joker}</span>`;
        };
        img.onload = () => {
            console.log(`Imagen cargada correctamente en la leyenda: cards/${joker}.png`);
        };

        const span = document.createElement('span');
        span.textContent = `Comodín (${joker})`;

        legendItem.appendChild(img);
        legendItem.appendChild(span);
        cardLegend.appendChild(legendItem);
    });
}

function clearFields() {
    const playersDiv = document.getElementById('players');
    playersDiv.innerHTML = `
        <div class="player">
            <label>Jugador 1 (ej. Ah Kh):</label>
            <input type="text" class="hole-cards" placeholder="Ah Kh" oninput="updateCards(this)">
            <div class="card-display"></div>
        </div>
        <div class="player">
            <label>Jugador 2 (ej. Qd Jd):</label>
            <input type="text" class="hole-cards" placeholder="Qd Jd" oninput="updateCards(this)">
            <div class="card-display"></div>
        </div>
    `;
    document.getElementById('communityCards').value = '';
    document.getElementById('gameStage').value = 'flop';
    document.getElementById('results').innerHTML = '';
    document.getElementById('cardLegend').style.display = 'none';
    updateCommunityCardsInput();
}

async function calculate() {
    const gameStage = document.getElementById('gameStage').value;
    const holeCardsInputs = document.getElementsByClassName('hole-cards');
    const playersHoleCards = [];
    for (let input of holeCardsInputs) {
        const cards = input.value.trim().toUpperCase();
        if (cards) {
            const cardList = cards.split(/\s+/);
            const filteredCards = cardList.filter(card => card !== 'JOKER1' && card !== 'JOKER2');
            if (filteredCards.length > 0) {
                playersHoleCards.push(filteredCards);
            }
        }
    }
    const communityCardsInput = document.getElementById('communityCards').value.trim().toUpperCase().split(/\s+/).filter(card => card !== '');
    const communityCards = communityCardsInput.filter(card => card !== 'JOKER1' && card !== 'JOKER2');

    let expectedCommunityCards = 0;
    if (gameStage === 'preflop') expectedCommunityCards = 0;
    else if (gameStage === '1card') expectedCommunityCards = 1;
    else if (gameStage === '2cards') expectedCommunityCards = 2;
    else if (gameStage === 'flop') expectedCommunityCards = 3;
    else if (gameStage === 'turn') expectedCommunityCards = 4;
    else if (gameStage === 'river') expectedCommunityCards = 5;

    if (communityCards.length !== expectedCommunityCards) {
        document.getElementById('results').innerHTML = `<p style="color: red;">Error: Se esperan ${expectedCommunityCards} cartas comunitarias en la etapa ${gameStage}.</p>`;
        return;
    }

    try {
        document.getElementById('results').innerHTML = '<p>Calculando...</p>';

        console.log('Datos enviados al backend:', { playersHoleCards, communityCards });

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);

        const response = await fetch('http://localhost:3000/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                playersHoleCards: playersHoleCards,
                communityCards: communityCards
            }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (data.error) {
            document.getElementById('results').innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            return;
        }

        let resultsHtml = '<h3>Probabilidades:</h3>';
        for (const [player, info] of Object.entries(data)) {
            // Redondear la probabilidad a 2 decimales al mostrar
            const roundedProbability = parseFloat(info.probability).toFixed(2);
            resultsHtml += `<p>${player}: ${roundedProbability}% (${info.hand})</p>`;
        }
        document.getElementById('results').innerHTML = resultsHtml;
    } catch (error) {
        if (error.name === 'AbortError') {
            document.getElementById('results').innerHTML = `<p style="color: red;">Error: La solicitud tardó demasiado. Intenta reducir el número de jugadores o simulaciones.</p>`;
        } else {
            document.getElementById('results').innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
        }
    }
}

window.onload = updateCommunityCardsInput;
