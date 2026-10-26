// Lógica de interacción en el Frontend y llamadas a la API de Inferencia

const emailInput = document.getElementById("emailInput");
const statsCounter = document.getElementById("statsCounter");
const btnPredict = document.getElementById("btnPredict");
const btnClear = document.getElementById("btnClear");
const testButtonsGrid = document.getElementById("testButtonsGrid");

const resultPlaceholder = document.getElementById("resultPlaceholder");
const resultContent = document.getElementById("resultContent");

const statusBanner = document.getElementById("statusBanner");
const statusIcon = document.getElementById("statusIcon");
const statusBadge = document.getElementById("statusBadge");
const statusSub = document.getElementById("statusSub");
const confidenceValue = document.getElementById("confidenceValue");

const probSpamText = document.getElementById("probSpamText");
const probThresholdText = document.getElementById("probThresholdText");
const progressBarFill = document.getElementById("progressBarFill");
const thresholdIndicator = document.getElementById("thresholdIndicator");

const metaLang = document.getElementById("metaLang");
const metaEngine = document.getElementById("metaEngine");
const metaLatency = document.getElementById("metaLatency");

const spamChips = document.getElementById("spamChips");
const hamChips = document.getElementById("hamChips");

// Actualización de conteo de palabras y caracteres
emailInput.addEventListener("input", () => {
  const text = emailInput.value.trim();
  const chars = emailInput.value.length;
  const words = text ? text.split(/\s+/).length : 0;
  statsCounter.textContent = `${words} palabras • ${chars} caracteres`;
});

let todosLosCasos = [];
let filtroActual = "todos";

// Cargar ejemplos del Banco de Pruebas con soporte de filtros
async function loadTestCases() {
  try {
    const res = await fetch("/api/pruebas");
    if (!res.ok) throw new Error("Error al obtener pruebas");
    todosLosCasos = await res.json();
    renderTestButtons();
  } catch (err) {
    console.error("No se pudieron cargar los casos de prueba:", err);
  }
}

function renderTestButtons() {
  testButtonsGrid.innerHTML = "";
  const filtrados = filtroActual === "todos" 
    ? todosLosCasos 
    : todosLosCasos.filter(c => c.subcategoria === filtroActual);

  filtrados.forEach(caso => {
    const btn = document.createElement("button");
    btn.className = "btn-sample";
    const tag = caso.etiqueta_esperada === "SPAM" ? "S" : "H";
    btn.innerHTML = `<strong>[${tag}]</strong> ${caso.categoria} <small>(${caso.idioma.toUpperCase()})</small>`;
    btn.title = `[${caso.subcategoria}] ${caso.descripcion}`;
    btn.addEventListener("click", () => {
      emailInput.value = caso.texto;
      emailInput.dispatchEvent(new Event("input"));
      ejecutarPrediccion();
    });
    testButtonsGrid.appendChild(btn);
  });
}

// Listeners de filtro
document.querySelectorAll(".pill-btn[data-filter]").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".pill-btn[data-filter]").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    filtroActual = btn.getAttribute("data-filter");
    renderTestButtons();
  });
});

// Botón de muestra aleatoria
const btnRandomSample = document.getElementById("btnRandomSample");
if (btnRandomSample) {
  btnRandomSample.addEventListener("click", () => {
    if (!todosLosCasos || todosLosCasos.length === 0) return;
    const randomCaso = todosLosCasos[Math.floor(Math.random() * todosLosCasos.length)];
    emailInput.value = randomCaso.texto;
    emailInput.dispatchEvent(new Event("input"));
    ejecutarPrediccion();
  });
}

// Limpiar formulario
btnClear.addEventListener("click", () => {
  emailInput.value = "";
  emailInput.dispatchEvent(new Event("input"));
  resultPlaceholder.classList.remove("hidden");
  resultContent.classList.add("hidden");
});

// Ejecutar Predicción
async function ejecutarPrediccion() {
  const texto = emailInput.value.trim();
  if (!texto) {
    alert("Por favor ingresa un correo para analizar.");
    return;
  }

  btnPredict.disabled = true;
  btnPredict.innerHTML = 'Analizando...';
  const startTime = performance.now();

  try {
    const res = await fetch("/api/predecir", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ texto })
    });

    if (!res.ok) throw new Error("Error en el servidor de inferencia");
    const data = await res.json();
    const duration = Math.max(1, Math.round(performance.now() - startTime));

    renderResultados(data, duration);
  } catch (err) {
    alert("Ocurrió un error al contactar al motor de predicción: " + err.message);
  } finally {
    btnPredict.disabled = false;
    btnPredict.innerHTML = 'Analizar Correo';
  }
}

btnPredict.addEventListener("click", ejecutarPrediccion);

// Renderizar UI con datos de predicción
function renderResultados(data, duration) {
  resultPlaceholder.classList.add("hidden");
  resultContent.classList.remove("hidden");

  const esSpam = data.etiqueta_tentativa === "SPAM";
  const pSpam = data.p_spam;
  const umbral = data.umbral;

  // Estado y Banner
  statusBanner.className = "status-banner " + (data.es_incierto ? "uncertain" : (esSpam ? "spam" : "ham"));
  statusIcon.textContent = data.es_incierto ? "?" : (esSpam ? "!" : "✓");
  statusBadge.textContent = data.es_incierto ? "ZONA DE INCERTIDUMBRE" : (esSpam ? "SPAM DETECTADO" : "CORREO HAM (LEGÍTIMO)");
  statusSub.textContent = data.es_incierto ? data.motivo_incertidumbre : `Clasificado con fiabilidad por el ${data.idioma_modelo}`;

  const confPercent = Math.round((esSpam ? pSpam : (1 - pSpam)) * 100);
  confidenceValue.textContent = `${confPercent}%`;

  // Barra y Gauge
  const pSpamPercent = Math.round(pSpam * 100);
  probSpamText.textContent = `${pSpamPercent}% (P=${pSpam.toFixed(3)})`;
  probThresholdText.textContent = umbral.toFixed(2);

  progressBarFill.style.width = `${pSpamPercent}%`;
  progressBarFill.style.backgroundColor = esSpam ? "var(--color-spam)" : "var(--color-ham)";
  thresholdIndicator.style.left = `${Math.round(umbral * 100)}%`;

  // Metadata
  metaLang.textContent = data.idioma_detectado;
  metaEngine.textContent = data.idioma_modelo.includes("Inglés") ? "Nativo EN (NB)" : "Nativo ES (NB)";
  metaLatency.textContent = `${duration} ms`;

  // XAI Chips
  renderChips(spamChips, data.explicacion.tokens_spam, "chip-spam");
  renderChips(hamChips, data.explicacion.tokens_ham, "chip-ham");
}

function renderChips(container, items, className) {
  container.innerHTML = "";
  if (!items || items.length === 0) {
    const empty = document.createElement("span");
    empty.className = "chip-empty";
    empty.textContent = "Ningún término significativo detectado en esta categoría";
    container.appendChild(empty);
    return;
  }

  items.forEach(item => {
    const chip = document.createElement("span");
    chip.className = `chip ${className}`;
    chip.textContent = item;
    container.appendChild(chip);
  });
}

// Botones de Entrenamiento Interactivo (Online Learning / Feedback)
const btnTeachSpam = document.getElementById("btnTeachSpam");
const btnTeachHam = document.getElementById("btnTeachHam");
const feedbackStatus = document.getElementById("feedbackStatus");

let ultimoResultado = null;

async function enviarFeedback(etiqueta) {
  const texto = emailInput.value.trim();
  if (!texto) {
    alert("El texto del correo está vacío.");
    return;
  }

  const idioma = (ultimoResultado && ultimoResultado.idioma_detectado) ? ultimoResultado.idioma_detectado.toLowerCase() : "es";
  const p_spam = (ultimoResultado && typeof ultimoResultado.p_spam === "number") ? ultimoResultado.p_spam : 0.5;
  const p_ham = (ultimoResultado && typeof ultimoResultado.p_ham === "number") ? ultimoResultado.p_ham : 0.5;
  const pred_prev = (ultimoResultado && ultimoResultado.etiqueta_tentativa) ? ultimoResultado.etiqueta_tentativa : "DESCONOCIDO";
  const umbral = (ultimoResultado && typeof ultimoResultado.umbral === "number") ? ultimoResultado.umbral : 0.5;

  btnTeachSpam.disabled = true;
  btnTeachHam.disabled = true;
  feedbackStatus.classList.remove("hidden");
  feedbackStatus.textContent = "Registrando en historial y entrenando el modelo con esta muestra...";

  try {
    const res = await fetch("/api/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        texto,
        label: etiqueta,
        idioma,
        p_spam,
        p_ham,
        pred_prev,
        umbral
      })
    });

    if (!res.ok) throw new Error("Error en la solicitud de entrenamiento");
    const data = await res.json();

    feedbackStatus.textContent = `${data.mensaje} (Muestras totales: ${data.total_muestras})`;
    
    // Cargar historial actualizado
    loadHistorial();

    // Re-evaluar de inmediato para ver cómo cambió la probabilidad tras el aprendizaje
    setTimeout(() => {
      ejecutarPrediccion();
    }, 1200);
  } catch (err) {
    feedbackStatus.textContent = `Error al entrenar: ${err.message}`;
  } finally {
    btnTeachSpam.disabled = false;
    btnTeachHam.disabled = false;
  }
}

if (btnTeachSpam) {
  btnTeachSpam.addEventListener("click", () => enviarFeedback(1));
}
if (btnTeachHam) {
  btnTeachHam.addEventListener("click", () => enviarFeedback(0));
}

// Actualizar variable global en renderResultados
const renderOrig = renderResultados;
renderResultados = function(data, duration) {
  ultimoResultado = data;
  renderOrig(data, duration);
  if (feedbackStatus) feedbackStatus.classList.add("hidden");
};

// Cargar Historial de Correos Entrenados
const historyTableBody = document.getElementById("historyTableBody");
const historyCounter = document.getElementById("historyCounter");
const historyPaginationInfo = document.getElementById("historyPaginationInfo");
const historyPageSizeSelect = document.getElementById("historyPageSizeSelect");
const historySearchInput = document.getElementById("historySearchInput");
const btnClearSearch = document.getElementById("btnClearSearch");
const paginationPageDetails = document.getElementById("paginationPageDetails");
const paginationNumbers = document.getElementById("paginationNumbers");
const btnPrevPage = document.getElementById("btnPrevPage");
const btnNextPage = document.getElementById("btnNextPage");

// Estado de filas expandidas, búsqueda y paginación
const expandedRows = new Set();
let allHistoryGroups = [];
let searchQuery = "";
let currentPage = 1;
let pageSize = 10; // Default: 10 correos por página

// Parsear strings de fecha "YYYY-MM-DD HH:MM:SS" a timestamp numérico
function parseTimestamp(tsStr) {
  if (!tsStr) return 0;
  const d = new Date(tsStr.replace(" ", "T"));
  return isNaN(d.getTime()) ? 0 : d.getTime();
}

async function loadHistorial() {
  if (!historyTableBody) return;
  try {
    const res = await fetch("/api/historial");
    if (!res.ok) return;
    const items = await res.json();

    if (historyCounter) {
      historyCounter.textContent = `${items.length} registros totales`;
    }

    if (items.length === 0) {
      allHistoryGroups = [];
      historyTableBody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">Aún no se han enviado correos para reentrenar.</td></tr>`;
      if (historyPaginationInfo) historyPaginationInfo.textContent = "Mostrando 0 de 0 correos";
      if (paginationPageDetails) paginationPageDetails.textContent = "Página 1 de 1";
      if (paginationNumbers) paginationNumbers.innerHTML = "";
      if (btnPrevPage) btnPrevPage.disabled = true;
      if (btnNextPage) btnNextPage.disabled = true;
      return;
    }

    // Agrupar registros por texto del mensaje
    const gruposMap = new Map();

    items.forEach((reg, idx) => {
      const key = (reg.texto || "").trim();
      if (!gruposMap.has(key)) {
        gruposMap.set(key, {
          id: `grupo_${idx}`,
          texto: key,
          primerRegistro: reg,
          ultimoRegistro: reg,
          historialCompleto: [reg]
        });
      } else {
        const grupo = gruposMap.get(key);
        grupo.ultimoRegistro = reg;
        grupo.historialCompleto.push(reg);
      }
    });

    // Reorganizar según la fecha y hora más reciente de su ÚLTIMA iteración/actualización
    allHistoryGroups = Array.from(gruposMap.values()).sort((a, b) => {
      const timeA = parseTimestamp(a.ultimoRegistro?.timestamp);
      const timeB = parseTimestamp(b.ultimoRegistro?.timestamp);
      return timeB - timeA; // Descendente: el más recientemente probado/actualizado arriba
    });

    renderPaginatedHistory();

  } catch (err) {
    console.error("Error al cargar historial:", err);
  }
}

function getFilteredHistoryGroups() {
  if (!searchQuery) return allHistoryGroups;
  const query = searchQuery.toLowerCase().trim();
  return allHistoryGroups.filter(g => {
    const textoCompleto = (g.texto || "").toLowerCase();
    const textoResumen = (g.ultimoRegistro?.texto_resumen || "").toLowerCase();
    const categoria = (g.ultimoRegistro?.categoria || "").toLowerCase();
    const idioma = (g.ultimoRegistro?.idioma || "").toLowerCase();
    return textoCompleto.includes(query) || textoResumen.includes(query) || categoria.includes(query) || idioma.includes(query);
  });
}

function renderPaginatedHistory() {
  const gruposFiltrados = getFilteredHistoryGroups();
  const totalItems = gruposFiltrados.length;

  if (totalItems === 0) {
    const mensajeVacio = searchQuery 
      ? `No se encontraron correos en el historial que coincidan con "${searchQuery}".`
      : "Aún no se han enviado correos para reentrenar.";
    historyTableBody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">${mensajeVacio}</td></tr>`;
    if (historyPaginationInfo) {
      historyPaginationInfo.textContent = searchQuery ? `0 resultados para "${searchQuery}"` : "Mostrando 0 de 0 correos";
    }
    if (paginationPageDetails) paginationPageDetails.textContent = "Página 1 de 1";
    if (paginationNumbers) paginationNumbers.innerHTML = "";
    if (btnPrevPage) btnPrevPage.disabled = true;
    if (btnNextPage) btnNextPage.disabled = true;
    return;
  }

  const effectivePageSize = pageSize === "all" ? totalItems : parseInt(pageSize, 10);
  const totalPages = Math.max(1, Math.ceil(totalItems / effectivePageSize));

  if (currentPage > totalPages) currentPage = totalPages;
  if (currentPage < 1) currentPage = 1;

  const startIdx = (currentPage - 1) * effectivePageSize;
  const endIdx = Math.min(startIdx + effectivePageSize, totalItems);
  const itemsEnPagina = gruposFiltrados.slice(startIdx, endIdx);

  historyTableBody.innerHTML = "";

  itemsEnPagina.forEach((grupo) => {
    const cant = grupo.historialCompleto.length;
    const tieneSubregistros = cant > 1;
    const reg = grupo.ultimoRegistro; // El estado más actual

    const pAntes = reg.porcentaje_antes || reg.porcentaje_spam || "-";
    const pDespues = reg.porcentaje_despues || "-";
    const delta = reg.cambio_delta || "-";
    const deltaColor = delta.startsWith("+") ? "color: #f09090;" : (delta.startsWith("-") ? "color: #5cd8a8;" : "");

    const badgePred = (reg.prediccion_posterior || reg.prediccion_modelo) === "SPAM" ? "badge-spam-sm" : "badge-ham-sm";
    const badgeHumano = reg.etiqueta_ensenada === "SPAM" ? "badge-spam-sm" : "badge-ham-sm";

    const statusIcon = reg.era_correcto 
      ? `<span class="badge-success-sm">Confirmado</span>` 
      : `<span class="badge-corrected-sm">Reentrenado</span>`;

    const isExpanded = expandedRows.has(grupo.id);

    // Fila Principal con su última fecha
    const trPadre = document.createElement("tr");
    trPadre.className = `history-row-parent ${isExpanded ? "expanded" : ""}`;
    trPadre.title = tieneSubregistros ? "Haz clic para ver las iteraciones y evaluaciones previas de este correo" : "";

    const arrow = tieneSubregistros ? `<span class="toggle-arrow">▶</span>` : "";
    const countBadge = tieneSubregistros ? `<span class="badge-version-count">${cant} evals</span>` : "";

    trPadre.innerHTML = `
      <td class="td-timestamp">${arrow}${reg.timestamp || "-"}</td>
      <td><strong>${reg.idioma || "ES"}</strong></td>
      <td class="td-message" title="${reg.texto}">
        ${reg.texto_resumen || reg.texto}
        ${countBadge}
      </td>
      <td class="td-percent">${pAntes}</td>
      <td class="td-percent" style="color: var(--accent);">${pDespues}</td>
      <td class="td-percent" style="${deltaColor}">${delta}</td>
      <td><span class="badge-sm ${badgePred}">${reg.prediccion_posterior || reg.prediccion_modelo}</span></td>
      <td><span class="badge-sm ${badgeHumano}">${reg.etiqueta_ensenada}</span></td>
      <td>${statusIcon}</td>
    `;

    historyTableBody.appendChild(trPadre);

    // Fila de sub-historial desplegable
    if (tieneSubregistros) {
      const trHija = document.createElement("tr");
      trHija.className = `subhistory-row ${isExpanded ? "" : "hidden"}`;
      trHija.id = `sub_${grupo.id}`;

      let subfilasHtml = "";
      grupo.historialCompleto.forEach((subReg, subIdx) => {
        const iterNum = subIdx + 1;
        const esElUltimo = subIdx === (cant - 1);
        const sAntes = subReg.porcentaje_antes || "-";
        const sDesp = subReg.porcentaje_despues || "-";
        const sDelta = subReg.cambio_delta || "-";
        const sDeltaColor = sDelta.startsWith("+") ? "color: #f09090;" : (sDelta.startsWith("-") ? "color: #5cd8a8;" : "");
        const sBadgePred = subReg.prediccion_posterior === "SPAM" ? "badge-spam-sm" : "badge-ham-sm";
        const sBadgeHumano = subReg.etiqueta_ensenada === "SPAM" ? "badge-spam-sm" : "badge-ham-sm";

        subfilasHtml += `
          <tr>
            <td class="subhistory-badge-iter">#${iterNum} ${esElUltimo ? "(Actual)" : ""}</td>
            <td class="td-timestamp">${subReg.timestamp}</td>
            <td class="td-percent">${sAntes}</td>
            <td class="td-percent" style="color: var(--accent);">${sDesp}</td>
            <td class="td-percent" style="${sDeltaColor}">${sDelta}</td>
            <td><span class="badge-sm ${sBadgePred}">${subReg.prediccion_posterior}</span></td>
            <td><span class="badge-sm ${sBadgeHumano}">${subReg.etiqueta_ensenada}</span></td>
            <td>${subReg.era_correcto ? '<span class="badge-success-sm">Confirmado</span>' : '<span class="badge-corrected-sm">Reentrenado</span>'}</td>
          </tr>
        `;
      });

      trHija.innerHTML = `
        <td colspan="9" class="subhistory-cell">
          <div class="subhistory-container">
            <div class="subhistory-header">
              <span>Evolución cronológica de este mensaje (${cant} iteraciones de entrenamiento)</span>
              <span>Umbral modelo: ${reg.umbral || 0.65}</span>
            </div>
            <table class="subhistory-table">
              <thead>
                <tr>
                  <th>Iteración</th>
                  <th>Fecha / Hora</th>
                  <th>% Antes</th>
                  <th>% Después</th>
                  <th>Variación</th>
                  <th>Predicción Modelo</th>
                  <th>Enseñanza Humana</th>
                  <th>Resultado</th>
                </tr>
              </thead>
              <tbody>
                ${subfilasHtml}
              </tbody>
            </table>
          </div>
        </td>
      `;

      historyTableBody.appendChild(trHija);

      trPadre.addEventListener("click", () => {
        const actualmenteVisible = !trHija.classList.contains("hidden");
        if (actualmenteVisible) {
          trHija.classList.add("hidden");
          trPadre.classList.remove("expanded");
          expandedRows.delete(grupo.id);
        } else {
          trHija.classList.remove("hidden");
          trPadre.classList.add("expanded");
          expandedRows.add(grupo.id);
        }
      });
    }
  });

  // Actualizar metadatos y botones de paginación
  if (historyPaginationInfo) {
    historyPaginationInfo.textContent = `Mostrando ${startIdx + 1}–${endIdx} de ${totalItems} correos`;
  }
  if (paginationPageDetails) {
    paginationPageDetails.textContent = `Página ${currentPage} de ${totalPages}`;
  }

  if (btnPrevPage) btnPrevPage.disabled = (currentPage <= 1);
  if (btnNextPage) btnNextPage.disabled = (currentPage >= totalPages);

  // Renderizar números de página
  if (paginationNumbers) {
    paginationNumbers.innerHTML = "";
    if (totalPages > 1) {
      for (let i = 1; i <= totalPages; i++) {
        const numBtn = document.createElement("button");
        numBtn.className = `btn-page-number ${i === currentPage ? "active" : ""}`;
        numBtn.textContent = i;
        numBtn.addEventListener("click", () => {
          currentPage = i;
          renderPaginatedHistory();
        });
        paginationNumbers.appendChild(numBtn);
      }
    }
  }
}

// Eventos de control de paginación
if (btnPrevPage) {
  btnPrevPage.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      renderPaginatedHistory();
    }
  });
}

if (btnNextPage) {
  btnNextPage.addEventListener("click", () => {
    const totalItems = getFilteredHistoryGroups().length;
    const effectivePageSize = pageSize === "all" ? totalItems : parseInt(pageSize, 10);
    const totalPages = Math.ceil(totalItems / effectivePageSize);
    if (currentPage < totalPages) {
      currentPage++;
      renderPaginatedHistory();
    }
  });
}

if (historyPageSizeSelect) {
  historyPageSizeSelect.addEventListener("change", (e) => {
    pageSize = e.target.value;
    currentPage = 1; // Volver a la primera página al cambiar el tamaño
    renderPaginatedHistory();
  });
}

// Eventos de control de búsqueda en el historial
if (historySearchInput) {
  historySearchInput.addEventListener("input", (e) => {
    searchQuery = e.target.value.trim();
    currentPage = 1; // Volver a la primera página al filtrar
    if (btnClearSearch) {
      if (searchQuery) {
        btnClearSearch.classList.remove("hidden");
      } else {
        btnClearSearch.classList.add("hidden");
      }
    }
    renderPaginatedHistory();
  });
}

if (btnClearSearch) {
  btnClearSearch.addEventListener("click", () => {
    if (historySearchInput) {
      historySearchInput.value = "";
      historySearchInput.focus();
    }
    searchQuery = "";
    btnClearSearch.classList.add("hidden");
    currentPage = 1;
    renderPaginatedHistory();
  });
}

// Cargar casos e historial al iniciar
loadTestCases();
loadHistorial();

