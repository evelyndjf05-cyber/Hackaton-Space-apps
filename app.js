// Referencias a DOM
const btn = document.getElementById('btn-process');
const fileXml = document.getElementById('file-xml');
const outputFiles = document.getElementById('output-files');
const outputResults = document.getElementById('output-results');
const outputExplanation = document.getElementById('output-explanation');

// Inicializar mapa Leaflet
const map = L.map('map').setView([20, -100], 4);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

// Función para graficar series
function plotSeries(data) {
    d3.select('#chart').selectAll('*').remove();
    const width = 600, height = 240, margin = { t: 10, r: 10, b: 30, l: 40 };
    const svg = d3.select('#chart')
        .append('svg')
        .attr('viewBox', `0 0 ${width} ${height}`);
    const x = d3.scaleLinear().domain([0, data.length - 1]).range([margin.l, width - margin.r]);
    const y = d3.scaleLinear().domain([0, Math.max(...data)]).range([height - margin.b, margin.t]);
    const line = d3.line().x((d, i) => x(i)).y(d => y(d));
    svg.append('path')
        .datum(data)
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', 'lime')
        .attr('stroke-width', 2)
        .attr('opacity', 0.9);
}

// Detectar eventos fenológicos simples
function detectEvents(series) {
    const events = [];
    for (let i = 1; i < series.length - 1; i++) {
        if (series[i] > series[i - 1] && series[i] > series[i + 1] && series[i] > 0.5) {
            events.push({
                name: `Evento ${i + 1}`,
                start: `Mes ${i}`,
                peak: `Mes ${i + 1}`,
                end: `Mes ${i + 2}`,
                value: series[i].toFixed(2),
                duration: 30
            });
        }
    }
    return events;
}

// Generar reporte estilo NASA
function generateReport(areaName, series, type) {
    const events = detectEvents(series);
    let report = `ANÁLISIS FENOLÓGICO - ${areaName} (${type})\n=========================================\n`;
    report += `Período analizado: Enero 2020 - Diciembre 2023\n\nEventos detectados:\n`;
    events.forEach((e, i) => {
        report += `${i + 1}. ${e.name}\n`;
        report += `- Inicio: ${e.start}\n`;
        report += `- Pico máximo: ${e.peak} (Valor: ${e.value})\n`;
        report += `- Fin: ${e.end}\n`;
        report += `- Duración: ${e.duration} días\n\n`;
    });
    if (events.length === 0) report += "No se detectaron eventos fenológicos significativos.\n";
    return report;
}

// Detectar tipo de dato automáticamente
function detectDataType(xmlDoc, series) {
    const tags = Array.from(xmlDoc.querySelectorAll("*")).map(el => el.tagName.toLowerCase());
    if (tags.some(t => t.includes("ndvi"))) return "NDVI";
    if (tags.some(t => t.includes("reflect"))) return "Reflectancia";
    if (tags.some(t => t.includes("radiance"))) return "Radiancia";
    const max = Math.max(...series);
    if (max > 1) return "Radiancia";
    if (max <= 1) return "Vegetación/NDVI genérico";
    return "Genérico";
}

// Generar explicación detallada de cada valor
function generateExplanations(series, type) {
    let explanation = `INTERPRETACIÓN DETALLADA (${type})\n===============================\n`;
    series.forEach((v, i) => {
        let desc;
        switch (type) {
            case "NDVI":
                if (v < 0) desc = "Área sin vegetación (agua, suelo desnudo)";
                else if (v < 0.2) desc = "Vegetación muy baja";
                else if (v < 0.5) desc = "Vegetación moderada, crecimiento parcial";
                else if (v < 0.7) desc = "Vegetación activa, fotosíntesis intensa";
                else desc = "Pico de vegetación, máximo crecimiento o frondosidad";
                break;
            case "Reflectancia":
                if (v < 0.1) desc = "Baja reflectancia, suelo oscuro o sombra";
                else if (v < 0.4) desc = "Reflectancia moderada, vegetación dispersa";
                else if (v < 0.7) desc = "Reflectancia alta, vegetación densa o iluminación fuerte";
                else desc = "Reflectancia máxima, área muy brillante o saturación del sensor";
                break;
            case "Radiancia":
                if (v < 0.3) desc = "Radiancia baja, poca emisión detectada";
                else if (v < 0.6) desc = "Radiancia moderada";
                else desc = "Radiancia alta, zona muy brillante o alta energía";
                break;
            default:
                if (v < 0.3) desc = "Valor bajo";
                else if (v < 0.6) desc = "Valor moderado";
                else desc = "Valor alto";
        }
        explanation += `Mes ${i + 1}: Valor ${v.toFixed(2)} → ${desc}\n`;
    });
    return explanation;
}

// Normalización min-max simple
function normalizeSeries(allNumbers) {
    const minVal = Math.min(...allNumbers);
    const maxVal = Math.max(...allNumbers);
    return allNumbers.map(v => (v - minVal) / (maxVal - minVal));
}

// Botón procesar
btn.onclick = async () => {
    if (!fileXml.files[0]) {
        outputFiles.textContent = 'Selecciona un archivo XML.';
        return;
    }
    try {
        const xmlText = await fileXml.files[0].text();
        const parser = new DOMParser();
        const xmlDoc = parser.parseFromString(xmlText, "application/xml");
        const allNumbers = Array.from(xmlDoc.querySelectorAll("*"))
            .map(el => el.textContent.trim())
            .flatMap(text => text.split(/\s+/).map(Number))
            .filter(n => !isNaN(n));

        let series;
        if (allNumbers.length > 0) {
            series = normalizeSeries(allNumbers.slice(0, 24));
            outputFiles.textContent = `Se encontraron ${allNumbers.length} valores numéricos.`;
        } else {
            series = Array.from({ length: 24 }, () => Math.random() * 0.6 + 0.3);
            outputFiles.textContent = "No se encontraron valores numéricos útiles, se generó serie aleatoria.";
        }

        const dataType = detectDataType(xmlDoc, series);
        plotSeries(series);
        outputResults.textContent = generateReport("Área Genérica", series, dataType);
        outputExplanation.textContent = generateExplanations(series, dataType);

    } catch (e) {
        outputResults.textContent = "Error al procesar XML: " + e;
        console.error(e);
    }
};
