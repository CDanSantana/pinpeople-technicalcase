import { CommonModule } from '@angular/common';
import { Component, computed, effect, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';
import { CountResult, ENPSDistributionResult, FeedbackStats, FilterMap, RouteConfig, SelectedFilters, SentimentRanking } from './interfaces';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
  standalone: true
})
export class App implements OnInit {
  protected readonly title = signal('front');
  private readonly apiUrl = 'http://localhost:8080/api';

  isLoading = signal(false);
  errorMsg = signal<string | null>(null);
  apiResult = signal<any>(null);

  filterOptions = signal<FilterMap>({});
  selectedFilters = signal<SelectedFilters>({
    cargo_id: null,
    area_id: null,
    localidade_id: null,
    geracao_id: null,
    tempo_empresa_id: null,
    topic: 'ENPS', // Default for comments/sentiment
    score_min: null,
    score_max: null,
    participanteId: null, // For employee profile/comparison
  });

  availableRoutes: RouteConfig[] = [
    { name: 'Colaboradores por Área', path: '/company/employees_per_area', description: 'Contagem de colaboradores por área, com filtros demográficos.' },
    { name: 'Média de Feedback', path: '/company/average_feedback', description: 'Média e estatísticas dos scores de feedback por campo.' },
    { name: 'Distribuição ENPS', path: '/company/enps_distribution', description: 'Distribuição Promotores/Neutros/Detratores e histograma de scores.' },
    { name: 'Distribuição por Tempo', path: '/company/tenure_distribution', description: 'Distribuição da força de trabalho por tempo de empresa (tenure).' },
    { name: 'Comentários Abertos', path: '/company/comments', description: 'Visualização de comentários abertos com filtro por tópico e range de score.' },
    { name: 'Análise de Sentimento', path: '/company/sentiments', description: 'Resumo de sentimento (P/N/N), temas (tags) e ranking por área.' },
    { name: 'Resumo Executivo das Áreas', path: '/areas/summary', description: 'Tabela de benchmarking comparando scores médios de todas as áreas (Heatmap).' },
    { name: 'Scores por Área', path: '/area/{area_id}/scores', requiredPathParams: ['area_id'], description: 'Estatísticas de scores para uma área específica.' },
    { name: 'ENPS por Área', path: '/area/{area_id}/enps', requiredPathParams: ['area_id'], description: 'Distribuição PND e ENPS Score para uma área específica.' },
    { name: 'Perfil do Colaborador', path: '/employee/{participante_id}/profile', requiredPathParams: ['participanteId'], description: 'Visualização do perfil, demografia e scores de um colaborador.' },
    { name: 'Comparação Individual', path: '/employee/{participante_id}/comparison', requiredPathParams: ['participanteId'], description: 'Benchmarking de scores do colaborador vs. Área e Empresa.' },
  ];

  selectedRoute = signal<RouteConfig>(this.availableRoutes[0]);

  filterKeys = ['cargo_id', 'area_id', 'localidade_id', 'geracao_id', 'tempo_empresa_id'];
  scoreFields = ['q01_satisfacao', 'q02_ambiente', 'q03_lideranca', 'q04_crescimento', 'q05_remuneracao', 'enps_score'];

  constructor() {
    // Efeito para resetar os resultados ao trocar de rota
    effect(() => {
      this.selectedRoute();
      this.apiResult.set(null);
      this.errorMsg.set(null);
    });
  }

  ngOnInit() {
    this.fetchFilterOptions();
  }

  // --- Funções de Estado e Navegação ---

  selectRoute(route: RouteConfig) {
    this.selectedRoute.set(route);
  }

  applyFilter(key: string, event: Event) {
    let value: number | string | null = null;
    if (event && 'target' in event) {
        if ((event.target as HTMLSelectElement).value === 'null') {
            value = null;
        } else if (key === 'participanteId' || key.includes('score_')) {
            value = parseInt((event.target as HTMLInputElement).value) || null;
        } else {
            value = (event.target as HTMLSelectElement).value;
        }
    } else if (event) {
        value = (event as any).detail; // Para casos de componentes customizados
    }

    this.selectedFilters.update(filters => ({
      ...filters,
      [key]: value
    }));
  }


  // --- Lógica de Chamada à API (Simulada) ---

  async fetchFilterOptions() {
    // SIMULAÇÃO: No ambiente real, você faria chamadas para /api/cargo-raw, /api/area-raw, etc.
    const mockFilters: FilterMap = {
      cargo_id: [
        { id: 1, nome: 'Desenvolvedor' },
        { id: 2, nome: 'Analista de Dados' },
        { id: 3, nome: 'Gerente' },
      ],
      area_id: [
        { id: 101, nome: 'Tecnologia' },
        { id: 102, nome: 'Marketing' },
        { id: 103, nome: 'Financeiro' },
      ],
      localidade_id: [
        { id: 201, nome: 'São Paulo' },
        { id: 202, nome: 'Rio de Janeiro' },
      ],
      geracao_id: [
        { id: 301, nome: 'Geração X' },
        { id: 302, nome: 'Millennials' },
        { id: 303, nome: 'Geração Z' },
      ],
      tempo_empresa_id: [
        { id: 401, nome: '0-1 Ano' },
        { id: 402, nome: '1-3 Anos' },
        { id: 403, nome: '3-5 Anos' },
        { id: 404, nome: '+5 Anos' },
      ],
    };

    this.filterOptions.set(mockFilters);
  }

  async fetchData() {
    this.isLoading.set(true);
    this.errorMsg.set(null);
    this.apiResult.set(null);

    const route = this.selectedRoute();
    const filters = this.selectedFilters();

    // 1. Validação de Parâmetros de Path (ID da Área ou Colaborador)
    for (const param of route.requiredPathParams || []) {
      const filterKey = param === 'area_id' ? 'area_id' : 'participanteId';
      if (!filters[filterKey]) {
        this.errorMsg.set(`O filtro '${filterKey.replace('Id', ' ID').replace('_', ' ')}' é obrigatório para esta rota.`);
        this.isLoading.set(false);
        return;
      }
    }

    // 2. Montagem da URL
    let url = `${this.apiUrl}${route.path}`;

    // Substituir Path Parameters
    if (route.requiredPathParams?.includes('area_id')) {
        url = url.replace('{area_id}', String(filters['area_id']));
    }
    if (route.requiredPathParams?.includes('participanteId')) {
        url = url.replace('{participante_id}', String(filters.participanteId));
    }

    // Adicionar Query Parameters
    const queryParams = new URLSearchParams();
    for (const key of this.filterKeys) {
      if (filters[key] !== null) {
        queryParams.append(key, String(filters[key]));
      }
    }
    // Adicionar filtros específicos (score, topic)
    if (filters.score_min !== null) queryParams.append('score_min', String(filters.score_min));
    if (filters.score_max !== null) queryParams.append('score_max', String(filters.score_max));
    if (filters['topic'] !== null) queryParams.append('topic', String(filters['topic']));

    const query = queryParams.toString();
    if (query) {
      url += `?${query}`;
    }

    console.log("Simulando chamada API para:", url);

    // 3. Simulação da Chamada (AQUI VOCÊ COLOCARIA O fetch REAL)
    try {
      // await new Promise(resolve => setTimeout(resolve, 800)); // Simula latência
      const mockData = this.getMockData(route.name, filters);
      this.apiResult.set(mockData);
    } catch (e: any) {
      this.errorMsg.set(`Erro na simulação da API: ${e.message}`);
    } finally {
      this.isLoading.set(false);
    }
  }

  // --- Funções de Suporte para Visualização ---

  getAreaNameById(areaId: number): string {
    const areas = this.filterOptions()['area_id'] ?? [];
    const match = areas.find(a => a.id === areaId);
    return match?.nome ?? `Área ID ${areaId}`;
  }

  getAreaName(areaId: any): string {
    const areas = this.filterOptions()['area_id'] ?? [];
    const found = areas.find(a => a.id === +areaId);
    return found?.nome ?? `Área ID ${areaId}`;
  }

  getEndX(angle: number, radius: number): number {
    return radius * Math.cos(angle * Math.PI / 180);
  }

  getEndY(angle: number, radius: number): number {
    return radius * Math.sin(angle * Math.PI / 180);
  }

  // Calcula o valor máximo para dimensionar as barras nos gráficos de contagem
  maxCount = computed(() => {
    const result = this.apiResult();
    if (Array.isArray(result) && result.length > 0) {
      return Math.max(...result.map(r => r.count));
    }
    return 1;
  });

  // Calcula o valor máximo para o histograma ENPS
  maxHistogramCount = computed(() => {
    const result = this.apiResult() as ENPSDistributionResult;
    if (result && result.histogram_by_score) {
      return Math.max(...Object.values(result.histogram_by_score), 1);
    }
    return 1;
  });

  // Gera um array de 0 a 10 para o histograma ENPS
  getScoreRange(): number[] {
    return Array.from({ length: 11 }, (_, i) => i);
  }

  // Gera a classe de cor para o score (usado em Comentários Abertos)
  getScoreColor(score: number, type: 'bg' | 'text' | 'border' = 'border'): string {
    if (score >= 9) return `${type}-green-500 bg-green-50 text-green-800`; // Promotor
    if (score >= 7) return `${type}-yellow-500 bg-yellow-50 text-yellow-800`; // Neutro
    return `${type}-red-500 bg-red-50 text-red-800`; // Detrator
  }

  // Converte porcentagem em offset/array para Gráfico de Rosca (Donut Chart)
  getArc(percentage: number, radius: number, offsetPct: number = 0): { dasharray: string, dashoffset: string } {
    const circumference = 2 * Math.PI * radius;
    const dasharray = `${(percentage / 100) * circumference} ${circumference}`;
    const offset = (-offsetPct / 100) * circumference;
    return { dasharray, dashoffset: String(offset) };
  }

  // Gera a cor de fundo para o Heatmap (quanto maior o valor, mais escura a cor)
  getHeatmapColor(value: number, color: 'indigo' | 'green' | 'red', invert: boolean = false, max: number = 10): string {
    const normalized = Math.min(1, Math.max(0, value / max));
    let shade;

    if (invert) {
        // Para métricas onde baixo é bom (ex: % Negativo)
        shade = Math.round(normalized * 500); // 0 -> 0 (claro), 100 -> 500 (escuro)
    } else {
        // Para métricas onde alto é bom (ex: Média)
        shade = Math.round((1 - normalized) * 500); // 0 -> 500 (escuro), 100 -> 0 (claro)
        shade = 500 - shade; // Inverte para: 0 -> 50 (claro), 10 -> 500 (escuro)
    }

    // Garante que o shade fique entre 50 e 500 (ou 800 para cores escuras)
    const finalShade = Math.max(50, Math.min(800, shade));
    return `bg-${color}-${finalShade} text-white`;
  }
  
  // Retorna as chaves de objeto para ranking
  getRankingKeys(ranking: SentimentRanking): string[] {
    return Object.keys(ranking);
  }

  // Calcula os pontos para o Gráfico Radar (apenas para demonstração)
  calculateRadarPoints(scores: FeedbackStats): string {
    if (!scores) return "";
    return this.scoreFields.map((field, index) => {
      const avg = scores[field]?.mean || 0;
      // Normaliza o score de 0-10 para um raio de 0-45
      const radius = (avg / 5) * 45; 
      const angle = (index * (360 / this.scoreFields.length)) - 90;
      const x = radius * Math.cos(angle * Math.PI / 180);
      const y = radius * Math.sin(angle * Math.PI / 180);
      return `${x},${y}`;
    }).join(' ');
  }

  // Retorna a classe de cor para a comparação individual (melhor/pior que a média)
  getComparisonColor(employeeAvg: number, benchmarkAvg: number): string {
    if (employeeAvg > benchmarkAvg + 0.1) return 'bg-green-100 text-green-700';
    if (employeeAvg < benchmarkAvg - 0.1) return 'bg-red-100 text-red-700';
    return 'bg-gray-100 text-gray-700';
  }

  // Retorna o ícone para a comparação individual (melhor/pior que a média)
  getComparisonIcon(employeeAvg: number, benchmarkAvg: number): string {
    if (employeeAvg > benchmarkAvg + 0.1) return 'fa-solid fa-up-long text-green-500'; // Seta para cima
    if (employeeAvg < benchmarkAvg - 0.1) return 'fa-solid fa-down-long text-red-500'; // Seta para baixo
    return 'fa-solid fa-equals text-gray-500'; // Igual
  }

  private getMockData(routeName: string, filters: SelectedFilters): any {
    const area = this.filterOptions()['area_id']?.find(a => a.id === filters['area_id'])?.nome || 'Área Selecionada';
    const topics = ['ENPS', 'Cultura', 'Lideranca'];
    const topic = filters['topic'] as string || 'ENPS';
    const participantName = `Colaborador ${filters.participanteId}`;
    alert(`{routeName}, {filters}`);
    return [] as CountResult[];
  }

}
