export interface User {
  id: number;
  username: str;
  email: str;
  full_name: str;
  role: 'ADMIN' | 'INVESTIGATOR' | 'ANALYST';
  badge_number?: string;
  department?: string;
  is_active: boolean;
  created_at: string;
}

export type str = string;

export interface Case {
  id: number;
  case_number: string;
  title: string;
  summary?: string;
  status: 'ACTIVE' | 'UNDER_REVIEW' | 'CLOSED' | 'COLD';
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  jurisdiction: string;
  lead_investigator_id?: number;
  tags: string[];
  created_at: string;
  updated_at: string;
  entity_count?: number;
  relationship_count?: number;
  evidence_count?: number;
}

export interface Entity {
  id: number;
  case_id?: number;
  name: string;
  entity_type: 'PERSON' | 'ORGANIZATION' | 'PHONE_NUMBER' | 'DEVICE' | 'VEHICLE' | 'FINANCIAL_ACCOUNT' | 'LOCATION' | 'CASE_ANCHOR';
  canonical_name?: string;
  aliases: string[];
  identifiers: Record<string, any>;
  risk_level: 'LOW' | 'ELEVATED' | 'HIGH' | 'CRITICAL';
  attributes: Record<string, any>;
  verification_status: 'UNVERIFIED' | 'VERIFIED' | 'FLAGGED';
  notes?: string;
  created_at: string;
  updated_at: string;
  degree?: number;
}

export interface Relationship {
  id: number;
  source_id: number;
  target_id: number;
  source_name?: string;
  source_type?: string;
  target_name?: string;
  target_type?: string;
  case_id?: number;
  relation_type: string;
  confidence_score: number;
  temporal_start?: string;
  temporal_end?: string;
  verification_status: 'PENDING_REVIEW' | 'VERIFIED' | 'REJECTED' | 'FLAGGED';
  verified_by_id?: number;
  verified_at?: string;
  weight: number;
  is_bidirectional: boolean;
  created_at: string;
  evidence_count?: number;
}

export interface EvidenceDocument {
  id: number;
  case_id: number;
  title: string;
  file_name: string;
  file_type: string;
  file_size: number;
  raw_text: string;
  mime_type: string;
  metadata_info: Record<string, any>;
  created_at: string;
  reference_count?: number;
}

export interface EvidenceReference {
  id: number;
  evidence_document_id: number;
  document_title?: string;
  relationship_id?: number;
  entity_id?: number;
  case_id?: number;
  excerpt: string;
  page_number: number;
  line_number?: number;
  char_offset_start?: number;
  char_offset_end?: number;
  extraction_confidence: number;
  provenance_notes?: string;
  created_at: string;
}

export interface EntityMatchSuggestion {
  id: number;
  primary_entity_id: number;
  primary_entity_name: string;
  primary_entity_type: string;
  candidate_entity_id: number;
  candidate_entity_name: string;
  candidate_entity_type: string;
  similarity_score: number;
  match_reasons: string[];
  status: 'PENDING' | 'APPROVED_MERGE' | 'REJECTED';
  created_at: string;
}

export interface NetworkPatternAlert {
  id: number;
  case_id?: number;
  alert_type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  explanation: string;
  confidence: number;
  affected_entities: number[];
  affected_relationships: number[];
  status: 'NEW' | 'UNDER_INVESTIGATION' | 'RESOLVED' | 'FALSE_POSITIVE';
  created_at: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  username?: string;
  action: string;
  entity_type?: string;
  entity_id?: number;
  case_id?: number;
  details: Record<string, any>;
  ip_address: string;
  timestamp: string;
}

export interface GraphData {
  nodes: Array<{
    data: {
      id: string;
      label: string;
      name: string;
      entity_type: string;
      canonical_name?: string;
      risk_level: string;
      verification_status: string;
      case_id?: number;
      degree: number;
      betweenness: number;
      pagerank: number;
      community: number;
      aliases?: string[];
      identifiers?: Record<string, any>;
    };
  }>;
  edges: Array<{
    data: {
      id: string;
      rel_id: number;
      source: string;
      target: string;
      label: string;
      relation_type: string;
      confidence_score: number;
      verification_status: string;
      temporal_start?: string;
      temporal_end?: string;
      weight: number;
      is_bidirectional: boolean;
    };
  }>;
  stats: {
    node_count: number;
    edge_count: number;
    verified_edge_count: number;
    pending_edge_count: number;
    active_cases: number;
  };
}

export interface CentralityAnalytics {
  degree_centrality: Array<{
    id: number;
    name: string;
    entity_type: string;
    score: number;
    raw_degree: number;
    explanation: string;
  }>;
  betweenness_centrality: Array<{
    id: number;
    name: string;
    entity_type: string;
    score: number;
    explanation: string;
  }>;
  pagerank: Array<{
    id: number;
    name: string;
    entity_type: string;
    score: number;
    explanation: string;
  }>;
  communities: Array<{
    community_id: number;
    label: string;
    size: number;
    members: Array<{ id: number; name: string; type: string }>;
  }>;
  anomalies: Array<{
    entity_id: number;
    entity_name: string;
    entity_type: string;
    anomaly_type: string;
    severity: string;
    confidence: number;
    explanation: string;
  }>;
  methodology_notes: Record<string, string>;
}
