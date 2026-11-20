import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# ----------------- User & Auth Schemas -----------------
class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    role: str = "INVESTIGATOR"
    badge_number: Optional[str] = None
    department: Optional[str] = "Special Investigations Division"

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    badge_number: Optional[str] = None
    department: Optional[str] = None
    is_active: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True

# ----------------- Case Schemas -----------------
class CaseCreate(BaseModel):
    case_number: str
    title: str
    summary: Optional[str] = None
    status: str = "ACTIVE"
    priority: str = "HIGH"
    jurisdiction: Optional[str] = "Federal / Multi-Agency"
    tags: List[str] = Field(default_factory=list)

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    jurisdiction: Optional[str] = None
    tags: Optional[List[str]] = None

class CaseOut(BaseModel):
    id: int
    case_number: str
    title: str
    summary: Optional[str] = None
    status: str
    priority: str
    jurisdiction: str
    lead_investigator_id: Optional[int] = None
    tags: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    entity_count: Optional[int] = 0
    relationship_count: Optional[int] = 0
    evidence_count: Optional[int] = 0

    class Config:
        from_attributes = True

# ----------------- Entity Schemas -----------------
class EntityCreate(BaseModel):
    case_id: Optional[int] = None
    name: str
    entity_type: str
    canonical_name: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    identifiers: Dict[str, Any] = Field(default_factory=dict)
    risk_level: str = "ELEVATED"
    attributes: Dict[str, Any] = Field(default_factory=dict)
    verification_status: str = "UNVERIFIED"
    notes: Optional[str] = None

class EntityUpdate(BaseModel):
    name: Optional[str] = None
    canonical_name: Optional[str] = None
    entity_type: Optional[str] = None
    aliases: Optional[List[str]] = None
    identifiers: Optional[Dict[str, Any]] = None
    risk_level: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    verification_status: Optional[str] = None
    notes: Optional[str] = None

class EntityOut(BaseModel):
    id: int
    case_id: Optional[int] = None
    name: str
    entity_type: str
    canonical_name: Optional[str] = None
    aliases: List[str]
    identifiers: Dict[str, Any]
    risk_level: str
    attributes: Dict[str, Any]
    verification_status: str
    notes: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    degree: Optional[int] = 0

    class Config:
        from_attributes = True

# ----------------- Relationship Schemas -----------------
class RelationshipCreate(BaseModel):
    source_id: int
    target_id: int
    case_id: Optional[int] = None
    relation_type: str
    confidence_score: float = 0.85
    temporal_start: Optional[datetime.datetime] = None
    temporal_end: Optional[datetime.datetime] = None
    verification_status: str = "PENDING_REVIEW"
    weight: float = 1.0
    is_bidirectional: bool = False
    evidence_excerpt: Optional[str] = None
    evidence_document_id: Optional[int] = None

class RelationshipUpdate(BaseModel):
    relation_type: Optional[str] = None
    confidence_score: Optional[float] = None
    temporal_start: Optional[datetime.datetime] = None
    temporal_end: Optional[datetime.datetime] = None
    verification_status: Optional[str] = None
    weight: Optional[float] = None

class RelationshipVerificationUpdate(BaseModel):
    verification_status: str  # VERIFIED, REJECTED, FLAGGED, PENDING_REVIEW
    notes: Optional[str] = None

class RelationshipOut(BaseModel):
    id: int
    source_id: int
    target_id: int
    source_name: Optional[str] = None
    source_type: Optional[str] = None
    target_name: Optional[str] = None
    target_type: Optional[str] = None
    case_id: Optional[int] = None
    relation_type: str
    confidence_score: float
    temporal_start: Optional[datetime.datetime] = None
    temporal_end: Optional[datetime.datetime] = None
    verification_status: str
    verified_by_id: Optional[int] = None
    verified_at: Optional[datetime.datetime] = None
    weight: float
    is_bidirectional: bool
    created_at: datetime.datetime
    evidence_count: Optional[int] = 0

    class Config:
        from_attributes = True

# ----------------- Evidence & Provenance Schemas -----------------
class EvidenceReferenceOut(BaseModel):
    id: int
    evidence_document_id: int
    document_title: Optional[str] = None
    relationship_id: Optional[int] = None
    entity_id: Optional[int] = None
    case_id: Optional[int] = None
    excerpt: str
    page_number: int
    line_number: Optional[int] = None
    char_offset_start: Optional[int] = None
    char_offset_end: Optional[int] = None
    extraction_confidence: float
    provenance_notes: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class EvidenceDocumentOut(BaseModel):
    id: int
    case_id: int
    title: str
    file_name: str
    file_type: str
    file_size: int
    raw_text: str
    mime_type: str
    uploaded_by_id: Optional[int] = None
    metadata_info: Dict[str, Any]
    created_at: datetime.datetime
    reference_count: Optional[int] = 0

    class Config:
        from_attributes = True

class ExtractedEntityItem(BaseModel):
    name: str
    entity_type: str
    confidence: float
    char_start: int
    char_end: int
    context_snippet: str
    attributes: Dict[str, Any] = Field(default_factory=dict)

class ExtractedRelationshipItem(BaseModel):
    source_name: str
    source_type: str
    target_name: str
    target_type: str
    relation_type: str
    confidence: float
    evidence_excerpt: str
    temporal_hint: Optional[str] = None

class ExtractionResult(BaseModel):
    document_id: Optional[int] = None
    entities: List[ExtractedEntityItem]
    relationships: List[ExtractedRelationshipItem]
    raw_text_preview: str
    total_entities_found: int
    total_relationships_found: int

# ----------------- Entity Matching Schemas -----------------
class EntityMatchSuggestionOut(BaseModel):
    id: int
    primary_entity_id: int
    primary_entity_name: str
    primary_entity_type: str
    candidate_entity_id: int
    candidate_entity_name: str
    candidate_entity_type: str
    similarity_score: float
    match_reasons: List[str]
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class EntityMatchReview(BaseModel):
    status: str  # APPROVED_MERGE, REJECTED
    review_notes: Optional[str] = None

# ----------------- Alerts & Network Intelligence -----------------
class NetworkPatternAlertOut(BaseModel):
    id: int
    case_id: Optional[int] = None
    alert_type: str
    severity: str
    title: str
    explanation: str
    confidence: float
    affected_entities: List[int]
    affected_relationships: List[int]
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class AlertResolveRequest(BaseModel):
    status: str  # RESOLVED, FALSE_POSITIVE, UNDER_INVESTIGATION
    resolution_notes: Optional[str] = None

# ----------------- Graph & Analytics Schemas -----------------
class GraphNode(BaseModel):
    id: str
    label: str
    name: str
    entity_type: str
    canonical_name: Optional[str] = None
    risk_level: str
    verification_status: str
    case_id: Optional[int] = None
    degree: int = 0
    centrality: Optional[float] = 0.0
    pagerank: Optional[float] = 0.0
    community: Optional[int] = 0
    is_anomaly: Optional[bool] = False
    anomaly_reason: Optional[str] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    relation_type: str
    confidence_score: float
    verification_status: str
    temporal_start: Optional[str] = None
    temporal_end: Optional[str] = None
    is_anomaly: Optional[bool] = False
    evidence_count: int = 0

class KnowledgeGraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    stats: Dict[str, Any]

class CentralityAnalysisResponse(BaseModel):
    degree_centrality: List[Dict[str, Any]]
    betweenness_centrality: List[Dict[str, Any]]
    pagerank: List[Dict[str, Any]]
    communities: List[Dict[str, Any]]
    anomalies: List[Dict[str, Any]]
    methodology_notes: Dict[str, str]

class ShortestPathRequest(BaseModel):
    source_entity_id: int
    target_entity_id: int

class ShortestPathResponse(BaseModel):
    found: bool
    path_nodes: List[Dict[str, Any]]
    path_edges: List[Dict[str, Any]]
    total_hops: int
    evidence_chain: List[str]

# ----------------- AI Assistant -----------------
class AIChatRequest(BaseModel):
    query: str
    case_id: Optional[int] = None
    focus_entity_id: Optional[int] = None

class AIChatResponse(BaseModel):
    query: str
    answer: str
    evidence_citations: List[Dict[str, Any]]
    suggested_followups: List[str]
    has_unverified_mentions: bool = False

# ----------------- Audit Log Schemas -----------------
class AuditLogOut(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    case_id: Optional[int] = None
    details: Dict[str, Any]
    ip_address: str
    timestamp: datetime.datetime

    class Config:
        from_attributes = True

TokenResponse.update_forward_refs()
