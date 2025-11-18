// --- Interfaces para Filtros e Dados ---

export interface FilterOption {
  id: number;
  nome: string;
}

export interface FilterMap {
  [key: string]: FilterOption[];
}

export interface SelectedFilters {
  [key: string]: number | string | null;
  score_min: number | null;
  score_max: number | null;
  participanteId: number | null;
}

export interface RouteConfig {
  name: string;
  path: string;
  requiredPathParams?: string[];
  requiredQueryParams?: string[];
  description: string;
}

// Interfaces para os dados de retorno do FastAPI
export interface StatsBasic {
  mean: number;
  std_dev: number;
  min: number;
  max: number;
  count: number;
}

export interface CountResult {
  area_id?: number;
  descricao?: string; // Para tenure
  area_nome?: string; // Para employees_per_area
  count: number;
}

export interface FeedbackStats {
  [scoreField: string]: StatsBasic;
}

export interface PNDSummary {
  count: number;
  pct: number;
}

export interface ENPSDistributionResult {
  histogram_by_score: { [score: number]: number };
  total: number;
  detratores: PNDSummary;
  neutros: PNDSummary;
  promotores: PNDSummary;
}

export interface Comment {
  comment: string;
  score: number;
  participante_id: number;
  area_id: number;
}

export interface CommentsDistributionResult {
  topic: string;
  count: number;
  comments: Comment[];
}

export interface SentimentItem {
  comment: string;
  sentiment: { label: 'positive' | 'negative' | 'neutral', score: number };
  area_id: number;
  cargo_id: number;
}

export interface SentimentSummary {
  positive: number;
  negative: number;
  neutral: number;
  positive_pct: number;
  negative_pct: number;
  neutral_pct: number;
}

export interface SentimentRanking {
  [id: number]: { positive: number, negative: number, neutral: number };
}

export interface SentimentDistributionResult {
  topic: string;
  count: number;
  sentiment_summary: SentimentSummary;
  ranking: { by_area: SentimentRanking, by_cargo: SentimentRanking };
  themes: { top_positive_terms: string[], top_negative_terms: string[] };
  comments: SentimentItem[];
}

export interface AreaSummary {
  area_id: number;
  area_nome: string;
  total_respostas: number;
  averages: { [scoreField: string]: number };
}

export interface EmployeeProfile {
  participante: { id: number, nome: string, email_corporativo: string };
  responses_count: number;
  demographics: {
    area_nome: string | null;
    cargo_nome: string | null;
    tempo_empresa_descricao: string | null;
    data_ultima_resposta: string;
  };
  scores_stats: { [scoreField: string]: StatsBasic };
}

export interface EmployeeComparisonResult {
  participante_id: number;
  employee_avgs: { [scoreField: string]: number };
  area_id: number;
  area_avgs: { [scoreField: string]: number };
  company_avgs: { [scoreField: string]: number };
}
