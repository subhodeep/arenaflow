import { ActionCard, RouteStep, TransportOption } from '../../types/api';

export type ResultTone = 'fan' | 'ops' | 'green' | 'access';

export type RenderableResult = {
  answer?: string;
  recommendation?: string;
  escalation_guidance?: string | null;
  confidence?: string;
  language?: string;
  estimated_total_minutes?: number | string | null;
  priority?: string;
  route_steps?: RouteStep[];
  options?: TransportOption[];
  action_cards?: ActionCard[];
  suggested_actions?: string[];
  actions?: string[];
  assistance_points?: string[];
  alternatives?: string[];
  assumptions?: string[];
  safety_notes?: string[];
  grounding_summary?: string[];
};

export type ResultCardProps = {
  title: string;
  result?: RenderableResult;
  error?: string | null;
  tone?: ResultTone;
};
