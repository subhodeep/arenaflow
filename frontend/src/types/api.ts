export type Confidence = 'low' | 'medium' | 'high';
export type Priority = 'low' | 'medium' | 'high' | 'critical';
export type CarbonImpact = 'low' | 'medium' | 'high' | 'unknown';

export type DataFreshness = {
  generated_at?: string;
  sources?: string[];
  stale_sources?: string[];
};

export type BaseArenaRequest = {
  venue_id: string;
  event_id?: string;
  language: string;
};

export type BaseGeminiResponse = {
  language: string;
  confidence: Confidence;
  data_freshness?: DataFreshness;
  assumptions?: string[];
  safety_notes?: string[];
  grounding_summary?: string[];
};

export type RouteStep = {
  instruction: string;
  distance_meters?: number | null;
  duration_minutes?: number | null;
  accessibility_notes?: string[];
  crowd_notes?: string[];
};

export type TransportOption = {
  mode: string;
  summary: string;
  estimated_minutes?: number | null;
  carbon_impact?: CarbonImpact;
  accessibility_notes?: string[];
};

export type ActionCard = {
  title: string;
  priority?: Priority;
  owner?: string | null;
  steps?: string[];
  escalation_required?: boolean;
};

export type AssistantChatResponse = BaseGeminiResponse & {
  answer: string;
  suggested_actions?: string[];
};

export type NavigationRouteResponse = BaseGeminiResponse & {
  recommendation: string;
  route_steps?: RouteStep[];
  estimated_total_minutes?: number | null;
};

export type AccessibilityPlanResponse = BaseGeminiResponse & {
  recommendation: string;
  assistance_points?: string[];
  route_steps?: RouteStep[];
};

export type TransportationOptionsResponse = BaseGeminiResponse & {
  recommendation: string;
  options?: TransportOption[];
};

export type SustainabilityAdviceResponse = BaseGeminiResponse & {
  recommendation: string;
  actions?: string[];
  estimated_impact?: string | null;
};

export type OpsDecisionSupportResponse = BaseGeminiResponse & {
  recommendation: string;
  priority?: Priority;
  action_cards?: ActionCard[];
  escalation_guidance?: string | null;
  alternatives?: string[];
};
