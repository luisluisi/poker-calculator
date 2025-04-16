// --- Variables Globales y Constantes ---
const ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2'];
const suits = ['s', 'h', 'd', 'c']; // Spades, Hearts, Diamonds, Clubs
let cardOptionsHtml = '<option value="">-- Vacío --</option>'; // Opción por defecto
const positions9Max = ["BTN", "SB", "BB", "UTG", "UTG+1", "MP1", "MP2", "HJ", "CO"];
let positionOptionsHtml = '';

// --- Funciones de Inicialización ---
function generateCardOptions() {
    let options = '<option value="">-- Vacío --</option>';
    suits.forEach(suit => {
        ranks.forEach(rank => {
            const cardValue = rank + suit; // Variable para valor (ej: Ah)
            const cardLabel = getCardLabel(rank, suit); // Variable para etiqueta (ej: A♥)
            // Usar template literals para insertar los VALORES de las variables
            options += `<option value="${cardValue.toUpperCase()}">${cardLabel}</option>`;
        });
    });
    cardOptionsHtml = options;
    console.log("Opciones de cartas generadas.");
}

function generatePositionOptions(positions = positions9Max) {
    // Genera HTML para options de posición
    let options = '<option value="">-- Posición --</option>'; // Opción por defecto
    positions.forEach(pos => { // La variable aquí es 'pos'
        // Usar template literals para insertar el VALOR de 'pos'
        options += `<option value="${pos}">${pos}</option>`;
    });
    positionOptionsHtml = options;
    console.log("Opciones de posición generadas."); // Mensaje de depuración
}

function getCardLabel(rank, suit) {
    // Devuelve la representación visual de la carta para el desplegable
    let suitSymbol = '?';
    switch (suit) { case 's': suitSymbol = '♠'; break; case 'h': suitSymbol = '♥'; break; case 'd': suitSymbol = '♦'; break; case 'c': suitSymbol = '♣'; break; }
    return `${rank}${suitSymbol}`; // Ej: A♠, K♥, T♦, 2♣
}

// --- Funciones de Manipulación del DOM ---
function addOpponent() { /* ... código sin cambios ... */
    const opponentsDiv = document.getElementById('opponents'); if (!opponentsDiv) { console.error("#opponents no encontrado."); return; }
    const totalPlayers = 1 + opponentsDiv.children.length; if (totalPlayers >= 9) { alert("Máximo 9 jugadores."); return; }
    const opponentNum = totalPlayers; const newOpponentDiv = document.createElement('div'); newOpponentDiv.className = 'player opponent'; newOpponentDiv.id = `player-${opponentNum}`;
    newOpponentDiv.innerHTML = ` <div class="player-controls"> <span class="opponent-label">Oponente ${opponentNum - 1}:</span> <div class="position-selector-container"> <label for="player-${opponentNum}-position" class="inline-label">Posición:</label> <select id="player-${opponentNum}-position" class="position-select opponent-position-select"> ${positionOptionsHtml} </select> </div> </div> <div id="player-${opponentNum}-display" class="card-display opponent-display"> <img src="cards/back.png" alt="Op C1"> <img src="cards/back.png" alt="Op C2"> </div>`;
    opponentsDiv.appendChild(newOpponentDiv); console.log(`Opponent ${opponentNum-1} added`);
}

function updateCardDisplay(selectElement, displayDivId, cardIndex) { /* ... código sin cambios ... */
    console.log(`updateCardDisplay: ${displayDivId}, index: ${cardIndex}`); const displayDiv = document.getElementById(displayDivId); if (!displayDiv) { console.error(`Display #${displayDivId} not found!`); return; } const selectedCard = selectElement ? selectElement.value : ""; if (cardIndex < 0) cardIndex = 0; let imgElement = displayDiv.children[cardIndex]; let imgSrc = 'cards/blank.png'; let imgAlt = `Carta ${cardIndex + 1}`; let isPlaceholder = true; if (selectedCard) { const cardFilename = selectedCard.toUpperCase() + '.png'; imgSrc = `cards/${cardFilename}`; imgAlt = selectedCard; isPlaceholder = false; console.log(` > Update to: ${imgSrc}`);} else { console.log(` > Update to: blank.png`);} if (imgElement && imgElement.tagName === 'IMG') { imgElement.src = imgSrc; imgElement.alt = imgAlt; imgElement.className = isPlaceholder ? 'card-image-placeholder' : ''; imgElement.onerror = () => { if (!isPlaceholder) { console.error(`Fail load ${imgSrc}`); imgElement.src = 'cards/error.png'; imgElement.alt = 'Error'; imgElement.className = ''; }}; } else { console.log(` > Creating new img for index ${cardIndex}`); imgElement = document.createElement('img'); imgElement.src = imgSrc; imgElement.alt = imgAlt; imgElement.className = isPlaceholder ? 'card-image-placeholder' : ''; imgElement.onerror = () => { if (!isPlaceholder) { console.error(`Fail load ${imgSrc}`); imgElement.src = 'cards/error.png'; imgElement.alt = 'Error'; imgElement.className = ''; }}; if (displayDiv.children[cardIndex]) { displayDiv.replaceChild(imgElement, displayDiv.children[cardIndex]); } else { displayDiv.appendChild(imgElement); } } ensureCorrectCardOrder(displayDiv); console.log(`updateCardDisplay finished: ${displayDivId}, index: ${cardIndex}`);
}

function ensureCorrectCardOrder(displayDiv){ /* ... código sin cambios ... */
    if (!displayDiv) return; let expectedCount = 0; if (displayDiv.id === 'hero-display') expectedCount = 2; else if (displayDiv.id.startsWith('player-')) expectedCount = 2; else if (displayDiv.id === 'communityCardDisplay') expectedCount = 5; else return; while(displayDiv.children.length > expectedCount && displayDiv.lastChild){ displayDiv.removeChild(displayDiv.lastChild); } while(displayDiv.children.length < expectedCount){ const ph = document.createElement('img'); ph.src = 'cards/blank.png'; ph.alt = `Carta ${displayDiv.children.length + 1}`; ph.className = 'card-image-placeholder'; displayDiv.appendChild(ph); } }

function updateCommunityCardSelectors() { /* ... código sin cambios ... */
    console.log("updateCommunityCardSelectors called"); const gameStageSelect = document.getElementById('gameStage'); const communityDisplay = document.getElementById('communityCardDisplay'); if (!gameStageSelect || !communityDisplay) return; const stage = gameStageSelect.value; let cardsToShow = 0; switch (stage) { case 'flop': cardsToShow = 3; break; case 'turn': cardsToShow = 4; break; case 'river': cardsToShow = 5; break; default: cardsToShow = 0; } console.log(` > Stage: ${stage}, cardsToShow: ${cardsToShow}`); communityDisplay.innerHTML = ''; for (let i = 1; i <= 5; i++) { const select = document.getElementById(`community-card-${i}`); if (!select) continue; if (i <= cardsToShow) { select.classList.remove('hidden-select'); select.disabled = false; const img = document.createElement('img'); const cardValue = select.value; img.src = cardValue ? `cards/${cardValue}.png` : 'cards/blank.png'; img.alt = cardValue || `Com ${i}`; img.className = cardValue ? '' : 'card-image-placeholder'; img.onerror = () => { if(cardValue){ img.src='cards/error.png'; img.alt='Err'; img.className='';}}; communityDisplay.appendChild(img); } else { select.classList.add('hidden-select'); select.disabled = true; if(select.value !== "") select.value = ""; } } ensureCorrectCardOrder(communityDisplay); console.log("updateCommunityCardSelectors finished");
}

// --- Función showCardLegend Eliminada ---

function clearFields() { /* ... código sin cambios ... */
    console.log("clearFields called"); const hSel1 = document.getElementById('hero-card-1'); if (hSel1) hSel1.value = ""; const hSel2 = document.getElementById('hero-card-2'); if (hSel2) hSel2.value = ""; const hPosSel = document.getElementById('hero-position'); if (hPosSel) hPosSel.value = ""; if(hSel1) updateCardDisplay(hSel1, 'hero-display', 0); if(hSel2) updateCardDisplay(hSel2, 'hero-display', 1); const oppDivs = document.getElementById('opponents'); if (oppDivs) oppDivs.innerHTML = ''; addOpponent(); const stageSel = document.getElementById('gameStage'); if (stageSel) stageSel.value = 'flop'; for (let i = 1; i <= 5; i++) { const sel = document.getElementById(`community-card-${i}`); if (sel) sel.value = ""; } updateCommunityCardSelectors(); const resultsDiv = document.getElementById('results'); if (resultsDiv) { resultsDiv.innerHTML = ''; resultsDiv.classList.remove('visible'); } const potSizeInput = document.getElementById('potSize'); if (potSizeInput) potSizeInput.value = ''; const amountToCallInput = document.getElementById('amountToCall'); if (amountToCallInput) amountToCallInput.value = ''; console.log("clearFields finished");
}

// --- Función Principal de Cálculo ---
async function calculate() { /* ... código sin cambios ... */
    const resultsDiv = document.getElementById('results'); if (!resultsDiv) return; resultsDiv.innerHTML = '<p class="calculating">Validando datos...</p>'; resultsDiv.classList.add('visible'); let heroCards = []; let opponentPositions = []; let communityCards = []; let allSelectedCards = new Set(); let errorMessage = null; let heroPosition = '';
    const hSel1 = document.getElementById('hero-card-1'); const hSel2 = document.getElementById('hero-card-2'); const hPosSel = document.getElementById('hero-position'); if (!hSel1 || !hSel2 || !hPosSel) errorMessage = "Err interno Héroe."; else { const c1=hSel1.value, c2=hSel2.value, pos=hPosSel.value; if (!c1||!c2) errorMessage="Selecciona 2 cartas Héroe."; else if (c1===c2) errorMessage=`Héroe tiene '${c1}' duplicada.`; else if (!pos) errorMessage="Selecciona posición Héroe."; else { heroCards = [c1, c2]; heroPosition = pos; heroCards.forEach(c => { if(allSelectedCards.has(c)) errorMessage=`Dup: ${c}`; allSelectedCards.add(c); }); } }
    if (!errorMessage) { const opDivs = document.getElementById('opponents').children; for (let i=0; i<opDivs.length; i++) { const opNum = opDivs[i].id.split('-')[1]; const opPosSel = document.getElementById(`player-${opNum}-position`); if (!opPosSel || !opPosSel.value) { errorMessage = `Selecciona pos Oponente ${opNum-1}.`; break; } opponentPositions.push(opPosSel.value); } } const numOpponents = opponentPositions.length; const totalPlayers = 1 + numOpponents; if (!errorMessage && totalPlayers < 2) errorMessage = "Necesita >= 1 Oponente."; if (!errorMessage && totalPlayers > 9) errorMessage = "Máx 9 jugadores.";
    if (!errorMessage) { const stageSel = document.getElementById('gameStage'); const stage = stageSel ? stageSel.value : 'flop'; let expCount = 0; if (stage === 'flop') expCount=3; else if (stage === 'turn') expCount=4; else if (stage === 'river') expCount=5; for (let i = 1; i <= expCount; i++) { const sel = document.getElementById(`community-card-${i}`); if (!sel) { errorMessage = `Err sel com #${i}.`; break; } const card = sel.value; if (!card) { errorMessage = `Falta com #${i} para '${stage}'.`; break; } if (allSelectedCards.has(card)) { errorMessage = `Dup '${card}' (com #${i}).`; break; } communityCards.push(card); allSelectedCards.add(card); } if(!errorMessage) { for (let i = expCount + 1; i <= 5; i++) { const sel = document.getElementById(`community-card-${i}`); if (sel && sel.value) { errorMessage = `Err: Com #${i} ('${sel.value}') selec. para '${stage}'.`; break; } } } }
    if (errorMessage) { console.error("Validación:", errorMessage); resultsDiv.innerHTML = `<p class="error">Error: ${errorMessage}</p>`; resultsDiv.classList.add('visible'); return; }
    const potSizeInput = document.getElementById('potSize'); const amountToCallInput = document.getElementById('amountToCall'); let potSize = 0; let amountToCall = 0; let calculateOdds = false; if (potSizeInput && amountToCallInput && potSizeInput.value && amountToCallInput.value) { potSize = parseFloat(potSizeInput.value); amountToCall = parseFloat(amountToCallInput.value); if (!isNaN(potSize) && !isNaN(amountToCall) && potSize >= 0 && amountToCall > 0) { calculateOdds = true; } else if (potSizeInput.value || amountToCallInput.value) { console.warn("Valores Pot Odds inválidos."); } }
    let playersData = [{ holeCards: heroCards, position: heroPosition }]; opponentPositions.forEach(pos => { playersData.push({ holeCards: [], position: pos }); });
    resultsDiv.innerHTML = '<p class="calculating">Enviando al servidor...</p>';
    try { console.log('Enviando:', { players: playersData, communityCards }); const controller = new AbortController(); const timeoutId = setTimeout(() => controller.abort(), 60000); const response = await fetch('http://localhost:3000/calculate', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ players: playersData, communityCards }), signal: controller.signal }); clearTimeout(timeoutId); if (!response.ok) { let errDet = `Error Servidor: ${response.status}.`; try { const data = await response.json(); if (data.error) errDet += ` ${data.error}`; } catch (e) {} throw new Error(errDet); } const data = await response.json(); if (data.error) throw new Error(`Error Cálculo: ${data.error}`); let resultsHtml = '<h3>Resultados:</h3>'; let heroEquity = 0; if (data.player1) { const info = data.player1; heroEquity = parseFloat(info.probability); const prob = heroEquity.toFixed(2); resultsHtml += `<p><b>Equity Estimada (Héroe ${heroPosition}): ${prob}%</b> (Mejor mano: ${info.hand || 'N/A'})</p><p><small>(${numOpponents} oponente${numOpponents !== 1 ? 's' : ''})</small></p>`; } else { resultsHtml += "<p>No se recibió resultado Héroe.</p>"; } if (calculateOdds) { const totalPotAfterCall = potSize + amountToCall + amountToCall; const equityNeeded = (totalPotAfterCall > 0) ? (amountToCall / totalPotAfterCall) * 100 : 0; resultsHtml += `<div id="potOddsInfo">Pot: ${potSize.toFixed(2)}, Call: ${amountToCall.toFixed(2)} => Necesitas <b>${equityNeeded.toFixed(2)}%</b> equity.<br>`; if (heroEquity > equityNeeded) { resultsHtml += `<span class="positive">Tienes ${heroEquity.toFixed(2)}% > ${equityNeeded.toFixed(2)}%. Call rentable.</span>`; } else if (heroEquity < equityNeeded) { resultsHtml += `<span class="negative">Tienes ${heroEquity.toFixed(2)}% < ${equityNeeded.toFixed(2)}%. Fold o reevaluar.</span>`; } else { resultsHtml += `<span>Tienes ${heroEquity.toFixed(2)}% = ${equityNeeded.toFixed(2)}%. Break-even.</span>`; } resultsHtml += `</div>`; } else if (potSizeInput.value || amountToCallInput.value) { resultsHtml += `<p id="potOddsInfo"><small><i>Introduce valores Pot y Call válidos (>0) para calcular Pot Odds.</i></small></p>`; } resultsDiv.innerHTML = resultsHtml;
    } catch (error) { console.error('Error en calculate():', error); let displayError="Ocurrió un error."; if (error.name === 'AbortError') { displayError = "Error: Timeout (60s)."; } else if (error.message.includes('Failed to fetch')) { displayError = "Error Conexión: No se pudo conectar a http://localhost:3000."; } else { displayError = error.message; } resultsDiv.innerHTML = `<p class="error">${displayError}</p>`; } finally { resultsDiv.classList.add('visible'); }
}

// --- Inicialización al Cargar la Página ---
window.onload = () => {
     console.log("Inicializando v3.1.2 (Debug)...");
     generateCardOptions(); // Generar HTML <option> cartas
     generatePositionOptions(); // Generar HTML <option> posición
     console.log("Poblando selects...");
     // Poblar selects comunitarios
     for (let i = 1; i <= 5; i++) { const sel = document.getElementById(`community-card-${i}`); if (sel) sel.innerHTML = cardOptionsHtml; }
     // Poblar selects Héroe
     const hSel1 = document.getElementById('hero-card-1'); if(hSel1) hSel1.innerHTML = cardOptionsHtml;
     const hSel2 = document.getElementById('hero-card-2'); if(hSel2) hSel2.innerHTML = cardOptionsHtml;
     const hPosSel = document.getElementById('hero-position'); if(hPosSel) hPosSel.innerHTML = positionOptionsHtml;
     console.log("Verificando estructura HTML...");
     if (document.getElementById('hero-section') && document.getElementById('opponents')) {
          clearFields(); // Limpia y añade 1 oponente por defecto
          console.log("Interfaz inicializada OK.");
     } else { console.error("Falta #hero-section o #opponents."); }
     if (document.getElementById('gameStage') && document.getElementById('community-card-selectors')) { updateCommunityCardSelectors(); } else { console.warn("Faltan elementos comunitarios."); }
     console.log("Nota: blank.png, error.png, back.png deben existir en /cards.");
     console.log("--- Fin Inicialización ---");
};