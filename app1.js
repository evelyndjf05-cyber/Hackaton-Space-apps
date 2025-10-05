// Elementos DOM
const btn = document.getElementById('btn-process');
const btnReset = document.getElementById('btn-reset');
const fileLut = document.getElementById('file-lut');
const fileData = document.getElementById('file-data');
const output = document.getElementById('output');

// Configuración del mapa
const map = L.map('map').setView([19.4326, -99.1332], 10); // Centro en CDMX
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Evento del botón procesar
btn.onclick = async () => {
    if (!fileLut.files[0] || !fileData.files[0]) {
        showMessage('❌ Selecciona archivo LUT XML y archivo .npz con datos.', 'error');
        return;
    }
    
    try {
        showMessage('🌺 Procesando datos de floración...', 'processing');
        
        const form = new FormData();
        form.append('lut', fileLut.files[0]);
        form.append('data', fileData.files[0]);
        
        const res = await fetch('http://localhost:8000/process', {
            method: 'POST',
            body: form
        });
        
        if (!res.ok) {
            throw new Error(Error del servidor: ${res.status});
        }
        
        const result = await res.json();
        displayResults(result);
        
    } catch (error) {
        console.error('Error:', error);
        showMessage(❌ Error: ${error.message}, 'error');
    }
};

// Evento del botón reset
btnReset.onclick = () => {
    fileLut.value = '';
    fileData.value = '';
    output.innerHTML = '<div class="placeholder"><p>Los resultados aparecerán aquí después del análisis...</p></div>';
    clearChart();
};

// Función para mostrar mensajes
function showMessage(message, type = 'info') {
    const colors = {
        error: '#ff4444',
        processing: '#00d1ff',
        success: '#00ff88',
        info: '#8b5cff'
    };
    
    output.innerHTML = `
        <div style="color: ${colors[type]}; text-align: center; padding: 40px 20px;">
            <div style="font-size: 2rem; margin-bottom: 10px;">${getIcon(type)}</div>
            <div>${message}</div>
        </div>
    `;
}

function getIcon(type) {
    const icons = {
        error: '❌',
        processing: '⏳',
        success: '✅',
        info: 'ℹ'
    };
    return icons[type] || 'ℹ';
}

// Función para mostrar resultados
function displayResults(data) {
    if (data.error) {
        showMessage(❌ Error: ${data.error}, 'error');
        return;
    }
    
    let html = `
        <div class="result-section">
            <h3>🌺 FLORABIU - RESULTADOS</h3>
            <p><strong>Proyecto:</strong> ${data.proyecto || 'Monitoreo de Floración'}</p>
            <p><strong>Fecha de procesamiento:</strong> ${data.fecha_procesamiento || 'N/A'}</p>
        </div>
    `;
    
    // Metadatos de la imagen
    if (data.metadatos_imagen) {
        html += `
            <div class="result-section">
                <h3>📊 Metadatos de Imagen</h3>
                <p><strong>Dimensiones:</strong> ${data.metadatos_imagen.dimensiones?.join(' × ') || 'N/A'}</p>
                <p><strong>Tipo LUT:</strong> ${data.metadatos_imagen.tipo_lut || 'N/A'}</p>
                <p><strong>Píxeles totales:</strong> ${data.metadatos_imagen.pixeles_totales?.toLocaleString() || 'N/A'}</p>
            </div>
        `;
    }
    
    // Estadísticas NDVI
    if (data.estadisticas_ndvi) {
        const stats = data.estadisticas_ndvi;
        html += `
            <div class="result-section">
                <h3>📈 Estadísticas NDVI</h3>
                <p><strong>Promedio:</strong> ${stats.promedio?.toFixed(3) || 'N/A'}</p>
                <p><strong>Máximo:</strong> ${stats.maximo?.toFixed(3) || 'N/A'}</p>
                <p><strong>Mínimo:</strong> ${stats.minimo?.toFixed(3) || 'N/A'}</p>
                <p><strong>Desviación estándar:</strong> ${stats.desviacion?.toFixed(3) || 'N/A'}</p>
                <p><strong>Píxeles válidos:</strong> ${stats.pixeles_validos?.toLocaleString() || 'N/A'}</p>
            </div>
        `;
    }
    
    // Análisis de floración
    if (data.analisis_floracion) {
        const flor = data.analisis_floracion;
        const estadoIcon = flor.floracion_detectada ? '🌸' : '🌿';
        const estadoColor = flor.floracion_detectada ? '#00ff88' : '#ffaa00';
        
        html += `
            <div class="result-section">
                <h3>${estadoIcon} Análisis de Floración</h3>
                <p style="color: ${estadoColor};"><strong>Estado:</strong> ${flor.estado?.toUpperCase() || 'N/A'}</p>
                <p><strong>Intensidad:</strong> ${flor.intensidad?.toFixed(3) || 'N/A'}</p>
                <p><strong>Área con floración:</strong> ${flor.area_floracion_pixeles?.toLocaleString() || 'N/A'} píxeles</p>
                <p><strong>Porcentaje de área:</strong> ${flor.porcentaje_area?.toFixed(1) || 'N/A'}%</p>
                <p><strong>Confianza de detección:</strong> ${(flor.confianza_deteccion * 100)?.toFixed(1) || 'N/A'}%</p>
            </div>
        `;
    }
    
    // Recomendaciones
    if (data.recomendaciones) {
        const rec = data.recomendaciones;
        html += `
            <div class="recomendacion">
                <h3>💡 Recomendaciones</h3>
                <p><strong>Mensaje principal:</strong> ${rec.mensaje_principal || 'N/A'}</p>
                <p><strong>Riego:</strong> ${rec.riego || 'N/A'}</p>
                <p><strong>Fertilización:</strong> ${rec.fertilizacion || 'N/A'}</p>
                <p><strong>Cosecha:</strong> ${rec.cosecha || 'N/A'}</p>
                <p><strong>Monitoreo:</strong> ${rec.monitoreo || 'N/A'}</p>
            </div>
        `;
    }
    
    // Alertas
    if (data.alertas && data.alertas.length > 0) {
        html += <div class="result-section"><h3>🚨 Alertas</h3>;
        data.alertas.forEach(alerta => {
            const alertClass = alert-${alerta.nivel};
            html += `
                <div class="alert ${alertClass}">
                    <strong>${alerta.tipo}:</strong> ${alerta.mensaje}
                </div>
            `;
        });
        html += </div>;
    }
    
    // Patrones temporales
    if (data.patrones_temporales) {
        const pat = data.patrones_temporales;
        if (pat.mensaje) {
            html += `
                <div class="result-section">
                    <h3>📅 Análisis Temporal</h3>
                    <p>${pat.mensaje}</p>
                </div>
            `;
        } else {
            html += `
                <div class="result-section">
                    <h3>📅 Análisis Temporal</h3>
                    <p><strong>Tendencia:</strong> ${pat.tendencia || 'N/A'}</p>
                    <p><strong>Pico de floración estimado:</strong> ${pat.pico_floracion_estimado || 'N/A'}</p>
                    <p><strong>Días hasta pico:</strong> ${pat.dias_hasta_pico || 'N/A'} días</p>
                    <p><strong>Comentario:</strong> ${pat.comentario || 'N/A'}</p>
                </div>
            `;
        }
    }
    
    output.innerHTML = html;
    
    // Actualizar gráfico si hay datos temporales
    if (data.estadisticas_ndvi) {
        updateChart(data.estadisticas_ndvi);
    }
}

// Función para actualizar gráfico
function updateChart(stats) {
    // Datos de ejemplo para el gráfico
    const sampleData = [
        stats.minimo,
        stats.promedio - stats.desviacion,
        stats.promedio,
        stats.promedio + stats.desviacion,
        stats.maximo
    ];
    
    plotSeries(sampleData);
}

// Función para dibujar gráfico (existente)
function plotSeries(data) {
    d3.select('#chart').selectAll('*').remove();
    
    const width = 600, height = 240, margin = { t: 10, r: 10, b: 30, l: 40 };
    const svg = d3.select('#chart').append('svg').attr('viewBox', 0 0 ${width} ${height});
    
    const x = d3.scaleLinear().domain([0, data.length - 1]).range([margin.l, width - margin.r]);
    const y = d3.scaleLinear().domain([d3.min(data), d3.max(data)]).range([height - margin.b, margin.t]);
    
    const line = d3.line().x((d, i) => x(i)).y(d => y(d));
    
    svg.append('path')
        .datum(data)
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', 'cyan')
        .attr('stroke-width', 2)
        .attr('opacity', 0.9);
    
    // Añadir puntos
    svg.selectAll('circle')
        .data(data)
        .enter()
        .append('circle')
        .attr('cx', (d, i) => x(i))
        .attr('cy', d => y(d))
        .attr('r', 3)
        .attr('fill', 'cyan');
}

function clearChart() {
    d3.select('#chart').selectAll('*').remove();
}

// Mensaje inicial
showMessage('🌺 Bienvenido a FLORABIU - Sube archivos LUT y datos para comenzar el análisis.', 'info');