import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    full_name = Column(String(128), nullable=False)
    role = Column(String(32), default="INVESTIGATOR")  # ADMIN, INVESTIGATOR, ANALYST
    badge_number = Column(String(64), nullable=True)
    department = Column(String(128), default="Special Investigations Division")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(256), nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(String(32), default="ACTIVE")  # ACTIVE, UNDER_REVIEW, CLOSED, COLD
    priority = Column(String(32), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    jurisdiction = Column(String(128), default="Federal / Multi-Agency")
    lead_investigator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    tags = Column(JSON, default=list)  # e.g. ["narcotics", "crypto", "shell-corp"]
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    entities = relationship("Entity", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("EvidenceDocument", back_populates="case", cascade="all, delete-orphan")

class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True, index=True)
    name = Column(String(256), index=True, nullable=False)
    entity_type = Column(String(64), index=True, nullable=False)  # PERSON, ORGANIZATION, PHONE_NUMBER, DEVICE, VEHICLE, FINANCIAL_ACCOUNT, LOCATION, CASE_ANCHOR
    canonical_name = Column(String(256), nullable=True)
    aliases = Column(JSON, default=list)
    identifiers = Column(JSON, default=dict)  # {"ssn": "...", "vin": "...", "iban": "...", "imei": "..."}
    risk_level = Column(String(32), default="ELEVATED")  # LOW, ELEVATED, HIGH, CRITICAL
    attributes = Column(JSON, default=dict)  # {"role": "logistics coordinator", "nationality": "..."}
    verification_status = Column(String(32), default="UNVERIFIED")  # UNVERIFIED, VERIFIED, FLAGGED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="entities")
    outgoing_relations = relationship("Relationship", foreign_keys="Relationship.source_id", back_populates="source_entity", cascade="all, delete-orphan")
    incoming_relations = relationship("Relationship", foreign_keys="Relationship.target_id", back_populates="target_entity", cascade="all, delete-orphan")

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True, index=True)
    relation_type = Column(String(64), index=True, nullable=False)  # ASSOCIATE_OF, COMMUNICATED_WITH, TRANSFERRED_FUNDS_TO, OWNER_OF, LOCATED_AT, SUSPECTED_HANDLER_OF, MEMBER_OF, OPERATES_VEHICLE
    confidence_score = Column(Float, default=0.85)  # 0.0 to 1.0
    temporal_start = Column(DateTime, nullable=True)
    temporal_end = Column(DateTime, nullable=True)
    verification_status = Column(String(32), default="PENDING_REVIEW")  # PENDING_REVIEW, VERIFIED, REJECTED, FLAGGED
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    weight = Column(Float, default=1.0)
    is_bidirectional = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    source_entity = relationship("Entity", foreign_keys=[source_id], back_populates="outgoing_relations")
    target_entity = relationship("Entity", foreign_keys=[target_id], back_populates="incoming_relations")
    evidence_references = relationship("EvidenceReference", back_populates="relationship", cascade="all, delete-orphan")

class EvidenceDocument(Base):
    __tablename__ = "evidence_documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    file_name = Column(String(256), nullable=False)
    file_type = Column(String(32), default="txt")  # txt, pdf, docx, json
    file_path = Column(String(512), nullable=True)
    file_size = Column(Integer, default=0)
    raw_text = Column(Text, nullable=False)
    mime_type = Column(String(128), default="text/plain")
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    metadata_info = Column(JSON, default=dict)  # extraction stats, source dept, classification
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="documents")
    references = relationship("EvidenceReference", back_populates="document", cascade="all, delete-orphan")

class EvidenceReference(Base):
    """
    Evidence Provenance Engine:
    Maintains exact source, timestamp, document reference, char offsets, and verification status of every extracted fact.
    """
    __tablename__ = "evidence_references"

    id = Column(Integer, primary_key=True, index=True)
    evidence_document_id = Column(Integer, ForeignKey("evidence_documents.id"), nullable=False, index=True)
    relationship_id = Column(Integer, ForeignKey("relationships.id"), nullable=True, index=True)
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True)
    excerpt = Column(Text, nullable=False)  # Exact quote from evidence document
    page_number = Column(Integer, default=1)
    line_number = Column(Integer, nullable=True)
    char_offset_start = Column(Integer, nullable=True)
    char_offset_end = Column(Integer, nullable=True)
    extraction_confidence = Column(Float, default=0.90)
    provenance_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    document = relationship("EvidenceDocument", back_populates="references")
    relationship = relationship("Relationship", back_populates="evidence_references")

class EntityMatchSuggestion(Base):
    """
    Uncertainty-Aware Entity Matching:
    Detects possible duplicates or multi-case entities with explicit reasons and confidence.
    """
    __tablename__ = "entity_match_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    primary_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    candidate_entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)  # e.g. 0.88
    match_reasons = Column(JSON, default=list)  # ["Shared phone number +1-555-0192", "High Levenshtein name match 'Dmitri V.' vs 'Dmitry Voronov'"]
    status = Column(String(32), default="PENDING")  # PENDING, APPROVED_MERGE, REJECTED
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    review_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    primary_entity = relationship("Entity", foreign_keys=[primary_entity_id])
    candidate_entity = relationship("Entity", foreign_keys=[candidate_entity_id])

class NetworkPatternAlert(Base):
    """
    Explainable Anomaly & Network Pattern Alerts:
    Surfaces high-risk anomalies (cross-case bridges, sudden contact surges, shell company cycles).
    """
    __tablename__ = "network_pattern_alerts"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=True, index=True)
    alert_type = Column(String(64), index=True, nullable=False)  # CROSS_CASE_OVERLAP, HIGH_CENTRALITY_UNVERIFIED, ANOMALOUS_BURST, MULTI_ORGANIZATION_BRIDGE, CYCLIC_TRANSACTION
    severity = Column(String(32), default="HIGH")  # CRITICAL, HIGH, MEDIUM, LOW
    title = Column(String(256), nullable=False)
    explanation = Column(Text, nullable=False)  # Natural language explanation why this is flagged
    confidence = Column(Float, default=0.85)
    affected_entities = Column(JSON, default=list)  # list of entity ids
    affected_relationships = Column(JSON, default=list)  # list of relationship ids
    status = Column(String(32), default="NEW")  # NEW, UNDER_INVESTIGATION, RESOLVED, FALSE_POSITIVE
    resolved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    """
    Tamper-evident Audit Logging for all investigative actions.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(64), nullable=False, index=True)  # LOGIN, VERIFY_RELATIONSHIP, REJECT_RELATIONSHIP, MERGE_ENTITIES, CREATE_CASE, UPLOAD_EVIDENCE, EXPORT_REPORT, AI_QUERY
    entity_type = Column(String(64), nullable=True)
    entity_id = Column(Integer, nullable=True)
    case_id = Column(Integer, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(64), default="127.0.0.1")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
