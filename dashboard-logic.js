/**
 * CEVA Dashboard - Lógica Principal v2
 * Totalmente funcional com dados dinâmicos, charts e filtros
 */

// ============================================
// ESTADO GLOBAL
// ============================================

const dashboardState = {
    allData: null,
    filteredData: null,
    periodo: 'todos',
    regiao: 'todas',
    transportadora: 'todas',
    currentPage: 'visao-geral',
    charts: {}
};

const ufRegioMap = {
    'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
    'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
    'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
    'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
    'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul'
};

// ============================================
// INICIALIZAÇÃO
// ============================================

async function initDashboard() {
    console.log('🚀 Inicializando dashboard...');
    
    try {
        const response = await fetch('/api/dashboard-data');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        dashboardState.allData = await response.json();
        dashboardState.filteredData = JSON.parse(JSON.stringify(dashboardState.allData));
        
        console.log('✅ Dados:', dashboardState.allData.resumo);
        
        setupEventListeners();
        renderPage('visao-geral');
        
    } catch (error) {
        console.error('❌ Erro:', error);
        alert('Erro ao carregar dados: ' + error.message);
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Filtros
    document.querySelectorAll('.filter-select').forEach((select, i) => {
        select.addEventListener('change', (e) => {
            if (i === 0) dashboardState.periodo = e.target.value;
            if (i === 1) dashboardState.regiao = e.target.value;
            if (i === 2) dashboardState.transportadora = e.target.value;
            applyFilters();
        });
    });
    
    // Upload
    document.getElementById('csvUpload')?.addEventListener('change', handleCSVUpload);
}

// ============================================
// FILTROS
// ============================================

function applyFilters() {
    if (!dashboardState.allData) return;
    
    dashboardState.filteredData = JSON.parse(JSON.stringify(dashboardState.allData));
    
    console.log('🔄 Filtros:', {
        periodo: dashboardState.periodo,
        regiao: dashboardState.regiao,
        transportadora: dashboardState.transportadora
    });
    
    // Filtra por transportadora
    if (dashboardState.transportadora !== 'todas') {
        dashboardState.filteredData.tsp = dashboardState.allData.tsp.filter(
            t => t.tsp === dashboardState.transportadora
        );
    }
    
    // Filtra por região
    if (dashboardState.regiao !== 'todas') {
        dashboardState.filteredData.uf = dashboardState.allData.uf.filter(
            u => ufRegioMap[u.uf] === dashboardState.regiao
        );
        dashboardState.filteredData.dealer = dashboardState.allData.dealer.filter(
            d => ufRegioMap[d.uf] === dashboardState.regiao
        );
    }
    
    // Filtra por período (dia)
    if (dashboardState.periodo !== 'todos') {
        const diaMin = parseInt(dashboardState.periodo.split('-')[0]);
        const diaMax = parseInt(dashboardState.periodo.split('-')[1]) || diaMin;
        dashboardState.filteredData.dia = dashboardState.allData.dia.filter(
            d => d.dia >= diaMin && d.dia <= diaMax
        );
    }
    
    recalculateResume();
    renderPage(dashboardState.currentPage);
}

function recalculateResume() {
    let totalNfs = 0, noPrazo = 0, volumes = 0;
    
    dashboardState.filteredData.tsp?.forEach(t => {
        totalNfs += t.total || 0;
        noPrazo += t.no_prazo || 0;
        volumes += t.volumes || 0;
    });
    
    const otd = totalNfs > 0 ? (noPrazo / totalNfs * 100).toFixed(1) : 0;
    
    dashboardState.filteredData.resumo = {
        total_nfs: totalNfs,
        no_prazo: noPrazo,
        fora_prazo: totalNfs - noPrazo,
        volumes: volumes,
        otd: parseFloat(otd)
    };
}

// ============================================
// RENDERIZAÇÃO DE PÁGINAS
// ============================================

function renderPage(pageName) {
    dashboardState.currentPage = pageName;
    
    // Esconde todas as páginas
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    
    // Mostra página ativa
    const activePage = document.getElementById('page-' + pageName);
    if (activePage) {
        activePage.style.display = 'block';
    }
    
    // Atualiza sidebar
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const navItem = document.querySelector(`[onclick*="'${pageName}'"]`);
    if (navItem) navItem.classList.add('active');
    
    console.log('📄 Renderizando:', pageName);
    
    // Renderiza conteúdo específico (com delay para DOM estar pronto)
    setTimeout(() => {
        switch(pageName) {
            case 'visao-geral':
                renderVisaoGeral();
                break;
            case 'otd-dealer':
                renderOTDDealer();
                break;
            case 'otd-tsp':
                renderOTDTSP();
                break;
            case 'otd-uf':
                renderOTDUF();
                break;
            case 'otd-dia':
                renderOTDDia();
                break;
            case 'drivers':
                renderOcorrencias();
                break;
            case 'network':
                renderNetwork();
                break;
            case 'tsp-geral':
                renderResumoTSP();
                break;
        }
    }, 50);
}

// ============================================
// PÁGINA: VISÃO GERAL
// ============================================

function renderVisaoGeral() {
    const resumo = dashboardState.filteredData.resumo || {};
    const tspData = dashboardState.filteredData.tsp || [];
    
    // KPIs
    const kpiCards = document.querySelectorAll('.kpi-card');
    if (kpiCards.length >= 4) {
        const otdVal = kpiCards[0].querySelector('.kpi-value');
        if (otdVal) otdVal.textContent = resumo.otd ? resumo.otd.toFixed(1) + '%' : '—';
        
        const farVal = kpiCards[1].querySelector('.kpi-value');
        if (farVal) farVal.textContent = resumo.fora_prazo || '—';
        
        const volVal = kpiCards[2].querySelector('.kpi-value');
        if (volVal) volVal.textContent = resumo.volumes ? resumo.volumes.toLocaleString('pt-BR') : '—';
        
        const nfsVal = kpiCards[3].querySelector('.kpi-value');
        if (nfsVal) nfsVal.textContent = resumo.total_nfs || '—';
    }
    
    // Charts
    if (tspData.length > 0) {
        renderChart('otdLineChart', 'line', tspData.map(t => t.tsp), [tspData.map(t => t.otd)], ['OTD %']);
        renderChart('tspBarChart', 'bar', tspData.map(t => t.tsp), [tspData.map(t => t.otd)], ['OTD %']);
    }
}

// ============================================
// PÁGINA: OTD POR DEALER
// ============================================

function renderOTDDealer() {
    const dealerData = dashboardState.filteredData.dealer || [];
    const top10 = dealerData.slice(0, 10);
    
    if (top10.length > 0) {
        renderChart('dealerBarChart', 'bar', 
            top10.map(d => d.dealer_id), 
            [top10.map(d => d.otd)],
            ['OTD %']
        );
    }
}

// ============================================
// PÁGINA: OTD POR TSP
// ============================================

function renderOTDTSP() {
    const tspData = dashboardState.filteredData.tsp || [];
    
    if (tspData.length > 0) {
        renderChart('tspVolChart', 'bar',
            tspData.map(t => t.tsp),
            [tspData.map(t => t.no_prazo), tspData.map(t => t.fora)],
            ['No Prazo', 'Fora do Prazo']
        );
    }
}

// ============================================
// PÁGINA: OTD POR UF
// ============================================

function renderOTDUF() {
    const ufData = dashboardState.filteredData.uf || [];
    
    if (ufData.length > 0) {
        renderChart('ufChart', 'bar',
            ufData.map(u => u.uf),
            [ufData.map(u => u.otd)],
            ['OTD %']
        );
    }
}

// ============================================
// PÁGINA: OTD POR DIA
// ============================================

function renderOTDDia() {
    const diaData = dashboardState.filteredData.dia || [];
    
    if (diaData.length > 0) {
        renderChart('diaChart', 'line',
            diaData.map(d => 'Dia ' + d.dia),
            [diaData.map(d => d.otd)],
            ['OTD %']
        );
    }
}

// ============================================
// PÁGINA: OCORRÊNCIAS
// ============================================

function renderOcorrencias() {
    const ocData = dashboardState.filteredData.ocorrencias || [];
    
    if (ocData.length > 0) {
        const labels = ocData.map(o => o.ocorrencia);
        const data = ocData.map(o => o.count);
        
        renderChart('driversBar', 'bar', labels, [data], ['Quantidade']);
        renderChart('driversPie', 'pie', labels, [data]);
    }
}

// ============================================
// PÁGINA: NETWORK
// ============================================

function renderNetwork() {
    const dealerData = dashboardState.filteredData.dealer || [];
    
    const statusCounts = [
        dealerData.filter(d => d.otd > 90).length,
        dealerData.filter(d => d.otd > 80 && d.otd <= 90).length,
        dealerData.filter(d => d.otd <= 80).length
    ];
    
    renderChart('networkChart', 'doughnut',
        ['Ok', 'Atenção', 'Crítico'],
        [statusCounts]
    );
}

// ============================================
// PÁGINA: RESUMO TSP
// ============================================

function renderResumoTSP() {
    const tspData = dashboardState.filteredData.tsp || [];
    
    if (tspData.length > 0) {
        renderChart('tspGeralChart', 'bar',
            tspData.map(t => t.tsp),
            [tspData.map(t => t.no_prazo), tspData.map(t => t.fora)],
            ['No Prazo', 'Fora do Prazo']
        );
    }
}

// ============================================
// CHARTS
// ============================================

function renderChart(chartId, type, labels, datasets, datasetLabels = null) {
    destroyChart(chartId);
    
    const ctx = document.getElementById(chartId)?.getContext('2d');
    if (!ctx) {
        console.warn('⚠️ Canvas não encontrado:', chartId);
        return;
    }
    
    const colors = ['#e62b2b', '#2463eb', '#22c55e', '#f59e0b', '#38bdf8', '#8b5cf6'];
    const pieColors = ['#e62b2b', '#f59e0b', '#38bdf8', '#8b5cf6', '#22c55e', '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#d946ef'];
    
    const chartData = {
        labels: labels,
        datasets: datasets.map((data, i) => {
            const baseColor = colors[i % colors.length];
            return {
                label: datasetLabels?.[i] || `Dataset ${i + 1}`,
                data: data,
                backgroundColor: type === 'pie' || type === 'doughnut' 
                    ? pieColors.slice(0, data.length)
                    : baseColor,
                borderColor: type === 'bar' ? baseColor : undefined,
                borderRadius: 4,
                fill: type === 'line',
                tension: type === 'line' ? 0.3 : undefined
            };
        })
    };
    
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: { color: '#7a8aaa', font: { family: 'Barlow', size: 11 } }
            }
        }
    };
    
    if (type !== 'pie' && type !== 'doughnut') {
        options.scales = {
            x: { ticks: { color: '#7a8aaa', font: { family: 'Barlow', size: 11 } }, grid: { color: 'rgba(31,45,74,.3)' } },
            y: { ticks: { color: '#7a8aaa', font: { family: 'Barlow', size: 11 } }, grid: { color: 'rgba(31,45,74,.3)' } }
        };
    }
    
    if (type === 'doughnut') {
        options.cutout = '60%';
    }
    
    dashboardState.charts[chartId] = new Chart(ctx, {
        type: type,
        data: chartData,
        options: options
    });
    
    console.log('✅ Chart renderizado:', chartId);
}

function destroyChart(chartId) {
    if (dashboardState.charts[chartId]) {
        dashboardState.charts[chartId].destroy();
        delete dashboardState.charts[chartId];
    }
}

// ============================================
// UPLOAD CSV
// ============================================

async function handleCSVUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload-csv', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`✅ CSV importado!\n${data.message}`);
            
            // Recarrega dados
            const newResp = await fetch('/api/dashboard-data');
            dashboardState.allData = await newResp.json();
            dashboardState.filteredData = JSON.parse(JSON.stringify(dashboardState.allData));
            
            renderPage(dashboardState.currentPage);
        } else {
            alert(`❌ Erro: ${data.error}`);
        }
    } catch (error) {
        alert(`❌ Erro: ${error.message}`);
    }
    
    event.target.value = '';
}

// ============================================
// COMPATIBILIDADE COM HTML
// ============================================

function showPage(pageName, element) {
    renderPage(pageName);
}

// ============================================
// INICIAR
// ============================================

document.addEventListener('DOMContentLoaded', initDashboard);
