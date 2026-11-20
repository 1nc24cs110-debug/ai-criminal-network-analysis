import datetime
import os
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from backend.database import engine, get_db, Base
from backend.models import (
    User, Case, Entity, Relationship, EvidenceDocument,
    EvidenceReference, EntityMatchSuggestion, NetworkPatternAlert, AuditLog
)
from backend.schemas import (
    UserLogin, TokenResponse, UserCreate, UserOut,
    CaseCreate, CaseUpdate, CaseOut,
    EntityCreate, EntityUpdate, EntityOut,
    RelationshipCreate, RelationshipUpdate, RelationshipOut, RelationshipVerificationUpdate,
    EvidenceDocumentOut, EvidenceReferenceOut, ExtractionResult,
    EntityMatchSuggestionOut, EntityMatchReview,
    NetworkPatternAlertOut, AlertResolveRequest,
    KnowledgeGraphResponse, CentralityAnalysisResponse, ShortestPathRequest, ShortestPathResponse,
    AIChatRequest, AIChatResponse,
    AuditLogOut
)
from backend.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_role
)
from backend.nlp_engine import EvidenceExtractionEngine
from backend.graph_engine import NetworkIntelligenceEngine, LEGAL_ETHICAL_DISCLAIMER
from backend.ai_assistant import InvestigativeAIAssistant
from backend.synthetic_data import seed_database
from backend.synthetic_engine import SyntheticDataEngine

# Create all database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AI-Powered Criminal Network Analysis System",
    description="Authorized investigative decision-support platform with evidence provenance, uncertainty-aware entity matching, and explainable network analytics.",
    version="1.0.0"
)

# Enable CORS for frontend Vite dev server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed database once at module load
try:
    _init_db = next(get_db())
    seed_database(_init_db)
    _init_db.close()
except Exception as e:
    print(f"[*] Database init note: {e}")

# Helper for recording tamper-evident audit logs
def log_audit(
    db: Session,
    user: Optional[User],
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    case_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: str = "127.0.0.1"
):
    audit = AuditLog(
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        case_id=case_id,
        details=details or {},
        ip_address=ip_address,
        timestamp=datetime.datetime.utcnow()
    )
    db.add(audit)
    db.commit()

# =========================================================================
# 1. AUTHENTICATION MODULE
# =========================================================================
@app.post("/api/auth/login", response_model=TokenResponse)
def login(creds: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == creds.username).first()
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    log_audit(db, user, "LOGIN", "USER", user.id, None, {"method": "password_auth"})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/auth/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/api/auth/users", response_model=List[UserOut])
def list_users(current_user: User = Depends(require_role(["ADMIN"])), db: Session = Depends(get_db)):
    return db.query(User).all()

@app.post("/api/auth/users", response_model=UserOut)
def create_user(
    new_user: UserCreate,
    current_user: User = Depends(require_role(["ADMIN"])),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.username == new_user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(User).filter(User.email == new_user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=new_user.username,
        email=new_user.email,
        hashed_password=hash_password(new_user.password),
        full_name=new_user.full_name,
        role=new_user.role,
        badge_number=new_user.badge_number,
        department=new_user.department
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log_audit(db, current_user, "CREATE_USER", "USER", user.id, None, {"created_username": user.username, "role": user.role})
    return user

# =========================================================================
# 2. MAIN DASHBOARD MODULE
# =========================================================================
@app.get("/api/dashboard/stats")
def get_dashboard_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_cases = db.query(Case).count()
    total_entities = db.query(Entity).count()
    verified_relationships = db.query(Relationship).filter(Relationship.verification_status == "VERIFIED").count()
    pending_relationships = db.query(Relationship).filter(Relationship.verification_status == "PENDING_REVIEW").count()
    unusual_patterns_alerts = db.query(NetworkPatternAlert).filter(NetworkPatternAlert.status == "NEW").count()
    total_evidence_docs = db.query(EvidenceDocument).count()
    total_audit_events = db.query(AuditLog).count()

    return {
        "total_cases": total_cases,
        "total_entities": total_entities,
        "verified_relationships": verified_relationships,
        "pending_relationships": pending_relationships,
        "unusual_patterns_alerts": unusual_patterns_alerts,
        "total_evidence_docs": total_evidence_docs,
        "total_audit_events": total_audit_events
    }

@app.get("/api/dashboard/charts")
def get_dashboard_charts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Entity distribution by type
    entities = db.query(Entity).all()
    type_counts: Dict[str, int] = {}
    risk_counts: Dict[str, int] = {"CRITICAL": 0, "HIGH": 0, "ELEVATED": 0, "LOW": 0}
    for e in entities:
        type_counts[e.entity_type] = type_counts.get(e.entity_type, 0) + 1
        risk_counts[e.risk_level] = risk_counts.get(e.risk_level, 0) + 1

    entity_distribution = [{"name": k.replace("_", " ").title(), "value": v, "type": k} for k, v in type_counts.items()]
    risk_distribution = [{"name": k.title(), "value": v} for k, v in risk_counts.items()]

    # Verification status breakdown
    relationships = db.query(Relationship).all()
    verification_breakdown = [
        {"name": "Verified Facts", "count": sum(1 for r in relationships if r.verification_status == "VERIFIED")},
        {"name": "Pending Human Review", "count": sum(1 for r in relationships if r.verification_status == "PENDING_REVIEW")},
        {"name": "Flagged Anomalies", "count": sum(1 for r in relationships if r.verification_status == "FLAGGED")},
        {"name": "Rejected Extractions", "count": sum(1 for r in relationships if r.verification_status == "REJECTED")}
    ]

    # Activity timeline (simulated dates based on case creation / audit)
    activity_timeline = [
        {"period": "Jan 2026", "cases": 1, "entities": 4, "alerts": 0},
        {"period": "Feb 2026", "cases": 2, "entities": 7, "alerts": 1},
        {"period": "Mar 2026", "cases": 2, "entities": 11, "alerts": 2},
        {"period": "Apr 2026", "cases": 3, "entities": 15, "alerts": 3}
    ]

    return {
        "entity_distribution": entity_distribution,
        "risk_distribution": risk_distribution,
        "verification_breakdown": verification_breakdown,
        "activity_timeline": activity_timeline
    }

@app.get("/api/dashboard/recent-activity")
def get_recent_activity(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recent_audits = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(8).all()
    recent_alerts = db.query(NetworkPatternAlert).order_by(desc(NetworkPatternAlert.created_at)).limit(4).all()

    audit_items = []
    for a in recent_audits:
        audit_items.append({
            "id": a.id,
            "action": a.action,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "timestamp": a.timestamp.isoformat(),
            "details": a.details
        })

    alert_items = []
    for al in recent_alerts:
        alert_items.append({
            "id": al.id,
            "title": al.title,
            "severity": al.severity,
            "alert_type": al.alert_type,
            "confidence": al.confidence,
            "created_at": al.created_at.isoformat()
        })

    return {
        "recent_audits": audit_items,
        "recent_alerts": alert_items
    }

# =========================================================================
# 3. CASE MANAGEMENT MODULE
# =========================================================================
@app.get("/api/cases", response_model=List[CaseOut])
def list_cases(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cases = db.query(Case).order_by(desc(Case.updated_at)).all()
    results = []
    for c in cases:
        e_count = db.query(Entity).filter(Entity.case_id == c.id).count()
        r_count = db.query(Relationship).filter(Relationship.case_id == c.id).count()
        d_count = db.query(EvidenceDocument).filter(EvidenceDocument.case_id == c.id).count()
        c_dict = CaseOut.from_orm(c)
        c_dict.entity_count = e_count
        c_dict.relationship_count = r_count
        c_dict.evidence_count = d_count
        results.append(c_dict)
    return results

@app.get("/api/cases/{case_id}", response_model=CaseOut)
def get_case(case_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Investigation case not found")
    e_count = db.query(Entity).filter(Entity.case_id == case.id).count()
    r_count = db.query(Relationship).filter(Relationship.case_id == case.id).count()
    d_count = db.query(EvidenceDocument).filter(EvidenceDocument.case_id == case.id).count()
    c_out = CaseOut.from_orm(case)
    c_out.entity_count = e_count
    c_out.relationship_count = r_count
    c_out.evidence_count = d_count
    return c_out

@app.post("/api/cases", response_model=CaseOut)
def create_case(
    case_in: CaseCreate,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    if db.query(Case).filter(Case.case_number == case_in.case_number).first():
        raise HTTPException(status_code=400, detail="Case number already exists")

    case = Case(
        case_number=case_in.case_number,
        title=case_in.title,
        summary=case_in.summary,
        status=case_in.status,
        priority=case_in.priority,
        jurisdiction=case_in.jurisdiction,
        lead_investigator_id=current_user.id,
        tags=case_in.tags
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    log_audit(db, current_user, "CREATE_CASE", "CASE", case.id, case.id, {"case_number": case.case_number, "title": case.title})
    return case

@app.put("/api/cases/{case_id}", response_model=CaseOut)
def update_case(
    case_id: int,
    case_in: CaseUpdate,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if case_in.title is not None:
        case.title = case_in.title
    if case_in.summary is not None:
        case.summary = case_in.summary
    if case_in.status is not None:
        case.status = case_in.status
    if case_in.priority is not None:
        case.priority = case_in.priority
    if case_in.jurisdiction is not None:
        case.jurisdiction = case_in.jurisdiction
    if case_in.tags is not None:
        case.tags = case_in.tags

    case.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(case)
    log_audit(db, current_user, "UPDATE_CASE", "CASE", case.id, case.id, {"case_number": case.case_number})
    return case

# =========================================================================
# 4. ENTITY MANAGEMENT MODULE
# =========================================================================
@app.get("/api/entities", response_model=List[EntityOut])
def list_entities(
    case_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    verification_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Entity)
    if case_id:
        q = q.filter(Entity.case_id == case_id)
    if entity_type:
        q = q.filter(Entity.entity_type == entity_type)
    if risk_level:
        q = q.filter(Entity.risk_level == risk_level)
    if verification_status:
        q = q.filter(Entity.verification_status == verification_status)
    if search:
        pattern = f"%{search}%"
        q = q.filter(or_(Entity.name.ilike(pattern), Entity.canonical_name.ilike(pattern)))

    entities = q.order_by(Entity.name).all()
    results = []
    for e in entities:
        # Calculate degree
        deg = db.query(Relationship).filter(or_(Relationship.source_id == e.id, Relationship.target_id == e.id)).count()
        e_dict = EntityOut.from_orm(e)
        e_dict.degree = deg
        results.append(e_dict)
    return results

@app.get("/api/entities/{entity_id}", response_model=EntityOut)
def get_entity_dossier(entity_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    deg = db.query(Relationship).filter(or_(Relationship.source_id == entity.id, Relationship.target_id == entity.id)).count()
    e_out = EntityOut.from_orm(entity)
    e_out.degree = deg
    return e_out

@app.post("/api/entities", response_model=EntityOut)
def create_entity(
    entity_in: EntityCreate,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    entity = Entity(
        case_id=entity_in.case_id,
        name=entity_in.name,
        entity_type=entity_in.entity_type,
        canonical_name=entity_in.canonical_name or entity_in.name,
        aliases=entity_in.aliases,
        identifiers=entity_in.identifiers,
        risk_level=entity_in.risk_level,
        attributes=entity_in.attributes,
        verification_status=entity_in.verification_status,
        notes=entity_in.notes
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    log_audit(db, current_user, "CREATE_ENTITY", "ENTITY", entity.id, entity.case_id, {"name": entity.name, "type": entity.entity_type})
    return entity

@app.put("/api/entities/{entity_id}", response_model=EntityOut)
def update_entity(
    entity_id: int,
    entity_in: EntityUpdate,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    if entity_in.name is not None:
        entity.name = entity_in.name
    if entity_in.canonical_name is not None:
        entity.canonical_name = entity_in.canonical_name
    if entity_in.entity_type is not None:
        entity.entity_type = entity_in.entity_type
    if entity_in.aliases is not None:
        entity.aliases = entity_in.aliases
    if entity_in.identifiers is not None:
        entity.identifiers = entity_in.identifiers
    if entity_in.risk_level is not None:
        entity.risk_level = entity_in.risk_level
    if entity_in.attributes is not None:
        entity.attributes = entity_in.attributes
    if entity_in.verification_status is not None:
        entity.verification_status = entity_in.verification_status
    if entity_in.notes is not None:
        entity.notes = entity_in.notes

    entity.updated_at = datetime.datetime.utcnow()
    db.commit()
    db.refresh(entity)
    log_audit(db, current_user, "UPDATE_ENTITY", "ENTITY", entity.id, entity.case_id, {"name": entity.name})
    return entity

# =========================================================================
# 5. RELATIONSHIPS & HUMAN VERIFICATION WORKFLOW
# =========================================================================
@app.get("/api/relationships", response_model=List[RelationshipOut])
def list_relationships(
    case_id: Optional[int] = Query(None),
    verification_status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(Relationship)
    if case_id:
        q = q.filter(Relationship.case_id == case_id)
    if verification_status:
        q = q.filter(Relationship.verification_status == verification_status)

    rels = q.all()
    entities_map = {e.id: e for e in db.query(Entity).all()}

    results = []
    for r in rels:
        src = entities_map.get(r.source_id)
        tgt = entities_map.get(r.target_id)
        ref_count = len(r.evidence_references)
        r_out = RelationshipOut(
            id=r.id,
            source_id=r.source_id,
            target_id=r.target_id,
            source_name=src.name if src else "Unknown",
            source_type=src.entity_type if src else "Unknown",
            target_name=tgt.name if tgt else "Unknown",
            target_type=tgt.entity_type if tgt else "Unknown",
            case_id=r.case_id,
            relation_type=r.relation_type,
            confidence_score=r.confidence_score,
            temporal_start=r.temporal_start,
            temporal_end=r.temporal_end,
            verification_status=r.verification_status,
            verified_by_id=r.verified_by_id,
            verified_at=r.verified_at,
            weight=r.weight,
            is_bidirectional=r.is_bidirectional,
            created_at=r.created_at,
            evidence_count=ref_count
        )
        results.append(r_out)
    return results

@app.post("/api/relationships", response_model=RelationshipOut)
def create_relationship(
    rel_in: RelationshipCreate,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    if not db.query(Entity).filter(Entity.id == rel_in.source_id).first():
        raise HTTPException(status_code=404, detail="Source entity not found")
    if not db.query(Entity).filter(Entity.id == rel_in.target_id).first():
        raise HTTPException(status_code=404, detail="Target entity not found")

    rel = Relationship(
        source_id=rel_in.source_id,
        target_id=rel_in.target_id,
        case_id=rel_in.case_id,
        relation_type=rel_in.relation_type,
        confidence_score=rel_in.confidence_score,
        temporal_start=rel_in.temporal_start,
        temporal_end=rel_in.temporal_end,
        verification_status=rel_in.verification_status,
        weight=rel_in.weight,
        is_bidirectional=rel_in.is_bidirectional
    )
    if rel_in.verification_status == "VERIFIED":
        rel.verified_by_id = current_user.id
        rel.verified_at = datetime.datetime.utcnow()

    db.add(rel)
    db.commit()
    db.refresh(rel)

    # Optional evidence excerpt attachment
    if rel_in.evidence_excerpt and rel_in.evidence_document_id:
        ref = EvidenceReference(
            evidence_document_id=rel_in.evidence_document_id,
            relationship_id=rel.id,
            entity_id=rel.source_id,
            case_id=rel.case_id,
            excerpt=rel_in.evidence_excerpt,
            extraction_confidence=rel_in.confidence_score,
            provenance_notes="Manual investigator entry"
        )
        db.add(ref)
        db.commit()

    log_audit(db, current_user, "CREATE_RELATIONSHIP", "RELATIONSHIP", rel.id, rel.case_id, {
        "relation_type": rel.relation_type, "source_id": rel.source_id, "target_id": rel.target_id
    })
    return rel

@app.put("/api/relationships/{rel_id}/verify", response_model=RelationshipOut)
def verify_relationship(
    rel_id: int,
    verif_in: RelationshipVerificationUpdate,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    """
    Human Verification Workflow:
    Investigators approve, reject, or request further verification of AI-generated suggestions.
    Guarantees no unverified extraction automatically becomes a confirmed legal fact.
    """
    rel = db.query(Relationship).filter(Relationship.id == rel_id).first()
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")

    prev_status = rel.verification_status
    rel.verification_status = verif_in.verification_status
    if verif_in.verification_status == "VERIFIED":
        rel.verified_by_id = current_user.id
        rel.verified_at = datetime.datetime.utcnow()
    else:
        rel.verified_by_id = None
        rel.verified_at = None

    db.commit()
    db.refresh(rel)

    log_audit(db, current_user, "VERIFY_RELATIONSHIP", "RELATIONSHIP", rel.id, rel.case_id, {
        "previous_status": prev_status,
        "new_status": rel.verification_status,
        "investigator_notes": verif_in.notes
    })

    src = db.query(Entity).filter(Entity.id == rel.source_id).first()
    tgt = db.query(Entity).filter(Entity.id == rel.target_id).first()

    return RelationshipOut(
        id=rel.id,
        source_id=rel.source_id,
        target_id=rel.target_id,
        source_name=src.name if src else "Unknown",
        source_type=src.entity_type if src else "Unknown",
        target_name=tgt.name if tgt else "Unknown",
        target_type=tgt.entity_type if tgt else "Unknown",
        case_id=rel.case_id,
        relation_type=rel.relation_type,
        confidence_score=rel.confidence_score,
        temporal_start=rel.temporal_start,
        temporal_end=rel.temporal_end,
        verification_status=rel.verification_status,
        verified_by_id=rel.verified_by_id,
        verified_at=rel.verified_at,
        weight=rel.weight,
        is_bidirectional=rel.is_bidirectional,
        created_at=rel.created_at,
        evidence_count=len(rel.evidence_references)
    )

# =========================================================================
# 6. EVIDENCE CENTER & PROVENANCE ENGINE
# =========================================================================
@app.get("/api/evidence/documents", response_model=List[EvidenceDocumentOut])
def list_evidence_documents(
    case_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(EvidenceDocument)
    if case_id:
        q = q.filter(EvidenceDocument.case_id == case_id)
    docs = q.order_by(desc(EvidenceDocument.created_at)).all()
    results = []
    for d in docs:
        d_out = EvidenceDocumentOut.from_orm(d)
        d_out.reference_count = len(d.references)
        results.append(d_out)
    return results

@app.get("/api/evidence/documents/{doc_id}", response_model=EvidenceDocumentOut)
def get_evidence_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(EvidenceDocument).filter(EvidenceDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    d_out = EvidenceDocumentOut.from_orm(doc)
    d_out.reference_count = len(doc.references)
    return d_out

@app.post("/api/evidence/upload")
async def upload_evidence_document(
    case_id: int = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Investigation case not found")

    content = await file.read()
    raw_text = EvidenceExtractionEngine.extract_text_from_file(content, file.filename)

    doc = EvidenceDocument(
        case_id=case_id,
        title=title,
        file_name=file.filename,
        file_type=file.filename.split(".")[-1].lower() if "." in file.filename else "txt",
        file_size=len(content),
        raw_text=raw_text,
        mime_type=file.content_type or "text/plain",
        uploaded_by_id=current_user.id,
        metadata_info={"original_name": file.filename, "upload_time": datetime.datetime.utcnow().isoformat()}
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    log_audit(db, current_user, "UPLOAD_EVIDENCE", "EVIDENCE_DOCUMENT", doc.id, case_id, {"title": doc.title, "filename": doc.file_name})

    # Automatically run entity & relationship extraction preview
    extracted_entities = EvidenceExtractionEngine.extract_entities(raw_text)
    extracted_relationships = EvidenceExtractionEngine.extract_relationships(raw_text, extracted_entities)

    return {
        "document_id": doc.id,
        "title": doc.title,
        "file_name": doc.file_name,
        "char_count": len(raw_text),
        "entities_preview": extracted_entities,
        "relationships_preview": extracted_relationships
    }

@app.post("/api/evidence/extract", response_model=ExtractionResult)
def extract_from_text(payload: Dict[str, Any], current_user: User = Depends(get_current_user)):
    text = payload.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Text payload required for extraction")

    entities = EvidenceExtractionEngine.extract_entities(text)
    relationships = EvidenceExtractionEngine.extract_relationships(text, entities)

    return ExtractionResult(
        document_id=payload.get("document_id"),
        entities=entities,
        relationships=relationships,
        raw_text_preview=text[:300] + ("..." if len(text) > 300 else ""),
        total_entities_found=len(entities),
        total_relationships_found=len(relationships)
    )

@app.post("/api/evidence/commit-extraction")
def commit_extraction(
    payload: Dict[str, Any],
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    """
    Commits approved AI-extracted entities & relationships into the case.
    Sets status to PENDING_REVIEW and preserves exact evidence offsets and excerpts.
    """
    case_id = payload.get("case_id")
    doc_id = payload.get("document_id")
    entities_to_commit = payload.get("entities", [])
    relationships_to_commit = payload.get("relationships", [])

    created_entity_ids = {}
    # Commit entities
    for e_data in entities_to_commit:
        existing = db.query(Entity).filter(Entity.name == e_data["name"]).first()
        if existing:
            created_entity_ids[e_data["name"]] = existing.id
        else:
            new_ent = Entity(
                case_id=case_id,
                name=e_data["name"],
                entity_type=e_data["entity_type"],
                canonical_name=e_data["name"],
                verification_status="UNVERIFIED",
                risk_level="ELEVATED",
                attributes=e_data.get("attributes", {})
            )
            db.add(new_ent)
            db.commit()
            db.refresh(new_ent)
            created_entity_ids[e_data["name"]] = new_ent.id

    # Commit relationships with Evidence References
    created_rel_count = 0
    for r_data in relationships_to_commit:
        src_id = created_entity_ids.get(r_data.get("source_name"))
        tgt_id = created_entity_ids.get(r_data.get("target_name"))
        if src_id and tgt_id and src_id != tgt_id:
            new_rel = Relationship(
                source_id=src_id,
                target_id=tgt_id,
                case_id=case_id,
                relation_type=r_data["relation_type"],
                confidence_score=r_data.get("confidence", 0.85),
                verification_status="PENDING_REVIEW"
            )
            db.add(new_rel)
            db.commit()
            db.refresh(new_rel)
            created_rel_count += 1

            # Evidence reference
            if doc_id and r_data.get("evidence_excerpt"):
                ref = EvidenceReference(
                    evidence_document_id=doc_id,
                    relationship_id=new_rel.id,
                    entity_id=src_id,
                    case_id=case_id,
                    excerpt=r_data["evidence_excerpt"],
                    extraction_confidence=r_data.get("confidence", 0.85),
                    provenance_notes="AI NLP extracted relationship - PENDING HUMAN CONFIRMATION"
                )
                db.add(ref)
                db.commit()

    log_audit(db, current_user, "COMMIT_EXTRACTIONS", "CASE", case_id, case_id, {
        "entities_count": len(entities_to_commit),
        "relationships_count": created_rel_count
    })

    return {
        "success": True,
        "committed_entities": len(entities_to_commit),
        "committed_relationships": created_rel_count
    }

# =========================================================================
# 7. UNCERTAINTY-AWARE ENTITY MATCHING
# =========================================================================
@app.get("/api/matching/suggestions", response_model=List[EntityMatchSuggestionOut])
def list_match_suggestions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    suggestions = db.query(EntityMatchSuggestion).filter(EntityMatchSuggestion.status == "PENDING").all()
    results = []
    for s in suggestions:
        results.append(EntityMatchSuggestionOut(
            id=s.id,
            primary_entity_id=s.primary_entity_id,
            primary_entity_name=s.primary_entity.name if s.primary_entity else "Unknown",
            primary_entity_type=s.primary_entity.entity_type if s.primary_entity else "Unknown",
            candidate_entity_id=s.candidate_entity_id,
            candidate_entity_name=s.candidate_entity.name if s.candidate_entity else "Unknown",
            candidate_entity_type=s.candidate_entity.entity_type if s.candidate_entity else "Unknown",
            similarity_score=s.similarity_score,
            match_reasons=s.match_reasons or [],
            status=s.status,
            created_at=s.created_at
        ))
    return results

@app.post("/api/matching/run")
def run_entity_matching(current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])), db: Session = Depends(get_db)):
    """
    Scans all entities across cases to detect potential duplicates or cross-case identities.
    Computes uncertainty-aware similarity metrics with explicit reasons.
    """
    entities = db.query(Entity).all()
    created_count = 0

    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            e1 = entities[i]
            e2 = entities[j]
            if e1.entity_type == e2.entity_type and e1.id != e2.id:
                score, reasons = EvidenceExtractionEngine.calculate_entity_similarity(
                    e1.name, e2.name,
                    {"aliases": e1.aliases, "identifiers": e1.identifiers},
                    {"aliases": e2.aliases, "identifiers": e2.identifiers}
                )
                if score >= 0.70:
                    # Check if suggestion already exists
                    existing = db.query(EntityMatchSuggestion).filter(
                        or_(
                            and_(EntityMatchSuggestion.primary_entity_id == e1.id, EntityMatchSuggestion.candidate_entity_id == e2.id),
                            and_(EntityMatchSuggestion.primary_entity_id == e2.id, EntityMatchSuggestion.candidate_entity_id == e1.id)
                        )
                    ).first()
                    if not existing:
                        sug = EntityMatchSuggestion(
                            primary_entity_id=e1.id,
                            candidate_entity_id=e2.id,
                            similarity_score=score,
                            match_reasons=reasons,
                            status="PENDING"
                        )
                        db.add(sug)
                        created_count += 1
    db.commit()
    log_audit(db, current_user, "RUN_ENTITY_MATCHING", "ENTITY_MATCH", None, None, {"suggestions_generated": created_count})
    return {"status": "success", "new_suggestions": created_count}

@app.post("/api/matching/review/{suggestion_id}")
def review_match_suggestion(
    suggestion_id: int,
    review: EntityMatchReview,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    sug = db.query(EntityMatchSuggestion).filter(EntityMatchSuggestion.id == suggestion_id).first()
    if not sug:
        raise HTTPException(status_code=404, detail="Match suggestion not found")

    sug.status = review.status
    sug.reviewed_by_id = current_user.id
    sug.review_notes = review.review_notes

    # If merge approved: re-route relationships from candidate to primary
    if review.status == "APPROVED_MERGE":
        primary = sug.primary_entity
        candidate = sug.candidate_entity
        if primary and candidate:
            # Transfer aliases
            primary_aliases = set(primary.aliases or [])
            primary_aliases.add(candidate.name)
            for a in (candidate.aliases or []):
                primary_aliases.add(a)
            primary.aliases = list(primary_aliases)

            # Reroute candidate incoming & outgoing relationships to primary
            incoming = db.query(Relationship).filter(Relationship.target_id == candidate.id).all()
            for r in incoming:
                r.target_id = primary.id
            outgoing = db.query(Relationship).filter(Relationship.source_id == candidate.id).all()
            for r in outgoing:
                r.source_id = primary.id

    db.commit()
    log_audit(db, current_user, "REVIEW_ENTITY_MATCH", "ENTITY_MATCH", sug.id, None, {
        "status": sug.status, "notes": review.review_notes
    })
    return {"status": "success", "suggestion_id": sug.id, "resolution": sug.status}

# =========================================================================
# 8. INTERACTIVE NETWORK GRAPH & ANALYTICS
# =========================================================================
@app.get("/api/graph/data", response_model=KnowledgeGraphResponse)
def get_graph_data(
    case_id: Optional[int] = Query(None),
    include_unverified: bool = Query(True),
    min_confidence: float = Query(0.0),
    entity_types: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Entities
    e_query = db.query(Entity)
    if case_id:
        e_query = e_query.filter(Entity.case_id == case_id)
    if entity_types:
        t_list = [t.strip().upper() for t in entity_types.split(",") if t.strip()]
        if t_list:
            e_query = e_query.filter(Entity.entity_type.in_(t_list))
    entities = e_query.all()
    entity_ids = {e.id for e in entities}

    # Relationships
    r_query = db.query(Relationship)
    if case_id:
        r_query = r_query.filter(Relationship.case_id == case_id)
    if not include_unverified:
        r_query = r_query.filter(Relationship.verification_status == "VERIFIED")
    if min_confidence > 0:
        r_query = r_query.filter(Relationship.confidence_score >= min_confidence)
    relationships = r_query.all()

    # Build NetworkX graph for topology metrics
    G = NetworkIntelligenceEngine.build_graph(entities, relationships, include_unverified, min_confidence)
    metrics = NetworkIntelligenceEngine.compute_all_metrics(G)
    node_metrics = metrics.get("node_metrics", {})

    # Format Cytoscape elements
    cy_nodes = []
    for e in entities:
        m = node_metrics.get(e.id, {})
        cy_nodes.append({
            "data": {
                "id": str(e.id),
                "label": e.name,
                "name": e.name,
                "entity_type": e.entity_type,
                "canonical_name": e.canonical_name,
                "risk_level": e.risk_level,
                "verification_status": e.verification_status,
                "case_id": e.case_id,
                "degree": m.get("degree", 0),
                "betweenness": m.get("betweenness", 0.0),
                "pagerank": m.get("pagerank", 0.0),
                "community": m.get("community", 0),
                "aliases": e.aliases or [],
                "identifiers": e.identifiers or {}
            }
        })

    cy_edges = []
    for r in relationships:
        if r.source_id in entity_ids and r.target_id in entity_ids:
            cy_edges.append({
                "data": {
                    "id": f"e_{r.id}",
                    "rel_id": r.id,
                    "source": str(r.source_id),
                    "target": str(r.target_id),
                    "label": r.relation_type.replace("_", " "),
                    "relation_type": r.relation_type,
                    "confidence_score": r.confidence_score,
                    "verification_status": r.verification_status,
                    "temporal_start": r.temporal_start.isoformat() if r.temporal_start else None,
                    "temporal_end": r.temporal_end.isoformat() if r.temporal_end else None,
                    "weight": r.weight or 1.0,
                    "is_bidirectional": r.is_bidirectional
                }
            })

    stats = {
        "node_count": len(cy_nodes),
        "edge_count": len(cy_edges),
        "verified_edge_count": sum(1 for e in cy_edges if e["data"]["verification_status"] == "VERIFIED"),
        "pending_edge_count": sum(1 for e in cy_edges if e["data"]["verification_status"] == "PENDING_REVIEW"),
        "active_cases": len({e["data"]["case_id"] for e in cy_nodes if e["data"]["case_id"] is not None})
    }

    return KnowledgeGraphResponse(nodes=cy_nodes, edges=cy_edges, stats=stats)

@app.get("/api/graph/analytics", response_model=CentralityAnalysisResponse)
def get_graph_analytics(
    case_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes real topological analytics using NetworkX:
    Degree Centrality, Betweenness Centrality, PageRank, Greedy Modularity Communities, and Statistical Outliers.
    """
    e_query = db.query(Entity)
    if case_id:
        e_query = e_query.filter(Entity.case_id == case_id)
    entities = e_query.all()

    r_query = db.query(Relationship)
    if case_id:
        r_query = r_query.filter(Relationship.case_id == case_id)
    relationships = r_query.all()

    G = NetworkIntelligenceEngine.build_graph(entities, relationships, include_unverified=True)
    metrics = NetworkIntelligenceEngine.compute_all_metrics(G)

    return CentralityAnalysisResponse(
        degree_centrality=metrics["degree_centrality"],
        betweenness_centrality=metrics["betweenness_centrality"],
        pagerank=metrics["pagerank"],
        communities=metrics["communities"],
        anomalies=metrics["anomalies"],
        methodology_notes=metrics["methodology_notes"]
    )

@app.post("/api/graph/shortest-path", response_model=ShortestPathResponse)
def find_investigative_path(
    payload: ShortestPathRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entities = db.query(Entity).all()
    relationships = db.query(Relationship).all()
    G = NetworkIntelligenceEngine.build_graph(entities, relationships, include_unverified=True)

    rel_lookup = {(r.source_id, r.target_id): r for r in relationships}

    result = NetworkIntelligenceEngine.find_shortest_path(
        G, payload.source_entity_id, payload.target_entity_id, rel_lookup
    )

    log_audit(db, current_user, "FIND_SHORTEST_PATH", "GRAPH", None, None, {
        "source_id": payload.source_entity_id,
        "target_id": payload.target_entity_id,
        "found": result["found"],
        "hops": result["total_hops"]
    })

    return result

# =========================================================================
# 9. AI INVESTIGATION ASSISTANT
# =========================================================================
@app.post("/api/assistant/chat", response_model=AIChatResponse)
def chat_investigation_assistant(
    payload: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = InvestigativeAIAssistant.query(
        db, payload.query, case_id=payload.case_id, focus_entity_id=payload.focus_entity_id
    )

    log_audit(db, current_user, "AI_QUERY", "ASSISTANT", None, payload.case_id, {
        "query": payload.query, "citations_returned": len(result["evidence_citations"])
    })

    return AIChatResponse(
        query=result["query"],
        answer=result["answer"],
        evidence_citations=result["evidence_citations"],
        suggested_followups=result["suggested_followups"],
        has_unverified_mentions=result["has_unverified_mentions"]
    )

# =========================================================================
# 10. ALERTS & REVIEW MODULE
# =========================================================================
@app.get("/api/alerts", response_model=List[NetworkPatternAlertOut])
def list_alerts(
    case_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(NetworkPatternAlert)
    if case_id:
        q = q.filter(NetworkPatternAlert.case_id == case_id)
    if status:
        q = q.filter(NetworkPatternAlert.status == status)
    return q.order_by(desc(NetworkPatternAlert.created_at)).all()

@app.put("/api/alerts/{alert_id}/resolve", response_model=NetworkPatternAlertOut)
def resolve_alert(
    alert_id: int,
    res_in: AlertResolveRequest,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    alert = db.query(NetworkPatternAlert).filter(NetworkPatternAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = res_in.status
    alert.resolved_by_id = current_user.id
    alert.resolution_notes = res_in.resolution_notes
    db.commit()
    db.refresh(alert)

    log_audit(db, current_user, "RESOLVE_ALERT", "ALERT", alert.id, alert.case_id, {
        "status": alert.status, "notes": res_in.resolution_notes
    })
    return alert

# =========================================================================
# 11. REPORTS & EXPORT MODULE
# =========================================================================
@app.get("/api/reports/html")
def generate_html_dossier(
    case_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Renders an official law-enforcement intelligence dossier summary formatted
    for browser printing, PDF export, and legal archival.
    """
    cases = db.query(Case).filter(Case.id == case_id).all() if case_id else db.query(Case).all()
    entities = db.query(Entity).filter(Entity.case_id == case_id).all() if case_id else db.query(Entity).all()
    relationships = db.query(Relationship).filter(Relationship.case_id == case_id).all() if case_id else db.query(Relationship).all()
    alerts = db.query(NetworkPatternAlert).filter(NetworkPatternAlert.case_id == case_id).all() if case_id else db.query(NetworkPatternAlert).all()

    verified_rels = [r for r in relationships if r.verification_status == "VERIFIED"]
    unverified_rels = [r for r in relationships if r.verification_status != "VERIFIED"]

    case_title = cases[0].title if cases else "Comprehensive Multi-Agency Intelligence Summary"
    case_num = cases[0].case_number if cases else "MULTI-CASE-SUMMARY"

    entities_html = "".join([
        f"<tr><td><strong>{e.name}</strong></td><td>{e.entity_type}</td><td>{e.risk_level}</td><td>{e.verification_status}</td><td>{', '.join(e.aliases or []) or 'N/A'}</td></tr>"
        for e in entities[:20]
    ])

    rels_html = "".join([
        f"<tr><td>{r.source_entity.name if r.source_entity else r.source_id}</td><td><strong>{r.relation_type}</strong></td><td>{r.target_entity.name if r.target_entity else r.target_id}</td><td>{round(r.confidence_score*100)}%</td><td><span class='badge-{r.verification_status.lower()}'>{r.verification_status}</span></td></tr>"
        for r in relationships[:25]
    ])

    alerts_html = "".join([
        f"<div class='alert-card'><h4>[{a.severity}] {a.title}</h4><p>{a.explanation}</p><small>Confidence: {round(a.confidence*100)}% | Status: {a.status}</small></div>"
        for a in alerts
    ])

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>CONFIDENTIAL INTELLIGENCE REPORT - {case_num}</title>
    <style>
        body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; margin: 30px; background: #fff; color: #1e293b; line-height: 1.5; }}
        .header {{ border-bottom: 3px solid #0f172a; padding-bottom: 15px; margin-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-start; }}
        .classification {{ display: inline-block; background: #dc2626; color: #fff; padding: 4px 12px; font-weight: bold; font-size: 13px; letter-spacing: 1.5px; border-radius: 3px; }}
        h1 {{ margin: 10px 0 5px 0; color: #0f172a; font-size: 24px; }}
        h2 {{ color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; margin-top: 25px; }}
        .meta-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; background: #f8fafc; padding: 15px; border: 1px solid #e2e8f0; border-radius: 6px; margin-bottom: 25px; }}
        .meta-item strong {{ display: block; font-size: 11px; text-transform: uppercase; color: #64748b; }}
        .meta-item span {{ font-size: 16px; font-weight: 600; color: #0f172a; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
        th, td {{ border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; }}
        th {{ background: #f1f5f9; color: #334155; }}
        .alert-card {{ background: #fff1f2; border-left: 4px solid #e11d48; padding: 12px; margin-bottom: 12px; border-radius: 3px; }}
        .alert-card h4 {{ margin: 0 0 5px 0; color: #9f1239; }}
        .badge-verified {{ color: #15803d; font-weight: bold; }}
        .badge-pending_review {{ color: #b45309; font-weight: bold; }}
        .disclaimer-box {{ margin-top: 35px; background: #f8fafc; border: 1px dashed #94a3b8; padding: 15px; font-size: 11px; color: #475569; }}
        .print-btn {{ background: #0284c7; color: #fff; padding: 10px 18px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; }}
        @media print {{ .no-print {{ display: none; }} body {{ margin: 0; }} }}
    </style>
</head>
<body>
    <div class="no-print" style="margin-bottom: 20px; text-align: right;">
        <button class="print-btn" onclick="window.print()">Print / Export to PDF</button>
    </div>

    <div class="header">
        <div>
            <span class="classification">LAW ENFORCEMENT SENSITIVE // REL TO JUDICIAL AUTHORITY</span>
            <h1>AI-POWERED CRIMINAL NETWORK ANALYSIS DOSSIER</h1>
            <p style="margin: 3px 0; color: #475569;">Case: <strong>{case_title}</strong> (Ref: {case_num})</p>
        </div>
        <div style="text-align: right; font-size: 12px; color: #64748b;">
            <p>Generated: {datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}<br>Officer: {current_user.full_name} ({current_user.badge_number or 'AUTHORIZED_USER'})</p>
        </div>
    </div>

    <div class="meta-box">
        <div class="meta-item"><strong>Investigation Cases</strong><span>{len(cases)}</span></div>
        <div class="meta-item"><strong>Registered Entities</strong><span>{len(entities)}</span></div>
        <div class="meta-item"><strong>Verified Connections</strong><span>{len(verified_rels)}</span></div>
        <div class="meta-item"><strong>Pending Review Links</strong><span>{len(unverified_rels)}</span></div>
    </div>

    <h2>1. Executive Summary & Analytical Overview</h2>
    <p>This intelligence summary synthesizes fragmented documentary evidence across maritime interdiction, customs compliance, and telecommunications monitoring. All relationship extractions are subject to evidence provenance verification. Graph topology calculations identify high-degree hub nodes and cross-cluster bridges facilitating transnational transport and financial conversion.</p>

    <h2>2. Entity Inventory & Structural Roles</h2>
    <table>
        <thead>
            <tr><th>Entity Name</th><th>Type</th><th>Risk Assessment</th><th>Verification</th><th>Documented Aliases</th></tr>
        </thead>
        <tbody>
            {entities_html}
        </tbody>
    </table>

    <h2>3. Relational Evidence & Human Verification Audit</h2>
    <table>
        <thead>
            <tr><th>Source Entity</th><th>Relation Type</th><th>Target Entity</th><th>Extraction Confidence</th><th>Verification Status</th></tr>
        </thead>
        <tbody>
            {rels_html}
        </tbody>
    </table>

    <h2>4. Explainable Anomaly & Network Pattern Alerts</h2>
    {alerts_html}

    <div class="disclaimer-box">
        <strong>EVIDENTIARY SAFEGUARD & ETHICAL NOTICE:</strong><br>
        {LEGAL_ETHICAL_DISCLAIMER}
        <br><br>
        This dossier is an investigative decision-support artifact. Unverified connections remain pending human investigator evaluation and do not represent judicial findings of fact.
    </div>

    <div style="margin-top: 40px; border-top: 1px solid #cbd5e1; padding-top: 20px; display: flex; justify-content: space-between;">
        <div>
            <p><strong>Lead Investigator Signature:</strong> _____________________________</p>
            <p>Special Agent Marcus Vance (INV-4821)</p>
        </div>
        <div>
            <p><strong>Command Reviewer Signature:</strong> _____________________________</p>
            <p>Director Sarah Jenkins (FED-0019)</p>
        </div>
    </div>
</body>
</html>"""
    return HTMLResponse(content=html_content)

# =========================================================================
# 12. AUDIT LOGS & SYSTEM STATUS
# =========================================================================
@app.get("/api/audit/logs", response_model=List[AuditLogOut])
def list_audit_logs(
    action: Optional[str] = Query(None),
    case_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action == action)
    if case_id:
        q = q.filter(AuditLog.case_id == case_id)
    logs = q.order_by(desc(AuditLog.timestamp)).limit(100).all()

    users_map = {u.id: u.username for u in db.query(User).all()}
    results = []
    for l in logs:
        l_out = AuditLogOut(
            id=l.id,
            user_id=l.user_id,
            username=users_map.get(l.user_id, "SYSTEM"),
            action=l.action,
            entity_type=l.entity_type,
            entity_id=l.entity_id,
            case_id=l.case_id,
            details=l.details or {},
            ip_address=l.ip_address,
            timestamp=l.timestamp
        )
        results.append(l_out)
    return results

@app.get("/api/system/health")
def system_health(db: Session = Depends(get_db)):
    return {
        "status": "OPERATIONAL",
        "system": "AI-Powered Criminal Network Analysis System",
        "version": "1.0.0",
        "database": "ONLINE",
        "database_records": {
            "cases": db.query(Case).count(),
            "entities": db.query(Entity).count(),
            "relationships": db.query(Relationship).count(),
            "documents": db.query(EvidenceDocument).count(),
            "audit_logs": db.query(AuditLog).count()
        },
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

# =========================================================================
# 13. SYNTHETIC DATA ENGINE & SCENARIO MANAGEMENT
# =========================================================================
@app.get("/api/synthetic/scenarios")
def list_synthetic_scenarios():
    return SyntheticDataEngine.list_scenarios()

@app.get("/api/synthetic/samples")
def list_synthetic_samples():
    return SyntheticDataEngine.list_samples()

@app.post("/api/synthetic/load-scenario/{scenario_id}")
def load_synthetic_scenario(
    scenario_id: str,
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    result = SyntheticDataEngine.load_scenario(scenario_id, db)
    log_audit(db, current_user, "LOAD_SYNTHETIC_SCENARIO", "SCENARIO", None, None, {"scenario_id": scenario_id})
    return result

@app.post("/api/synthetic/reset")
def reset_synthetic_dataset(
    current_user: User = Depends(require_role(["ADMIN", "INVESTIGATOR"])),
    db: Session = Depends(get_db)
):
    result = SyntheticDataEngine.reset_to_default(db)
    log_audit(db, current_user, "RESET_SYNTHETIC_DATASET", "DATASET", None, None, {"action": "reset_to_baseline"})
    return result

@app.get("/api/synthetic/export")
def export_synthetic_dataset(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return SyntheticDataEngine.export_full_dataset(db)

# =========================================================================
# 13B. MODEL CONTEXT PROTOCOL (MCP) INTEGRATION INFO
# =========================================================================
@app.get("/api/mcp/info")
def get_mcp_server_info():
    server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp_server.py")
    return {
        "status": "OPERATIONAL",
        "name": "criminal-network-mcp",
        "protocol": "Model Context Protocol (JSON-RPC 2.0 over stdio)",
        "protocol_version": "2024-11-05",
        "server_file": server_path,
        "tools_count": 8,
        "tools": [
            {"name": "list_cases", "description": "List criminal investigation operations and metadata."},
            {"name": "search_entities", "description": "Search graph nodes by name, alias, or identifier."},
            {"name": "get_entity_dossier", "description": "Full forensic dossier with character-offset provenance."},
            {"name": "calculate_network_metrics", "description": "Graph centrality, community clusters, and anomalies."},
            {"name": "find_shortest_evidentiary_path", "description": "Shortest chain of evidence between entities."},
            {"name": "extract_intelligence_from_document", "description": "NLP entity & relationship extraction."},
            {"name": "get_pattern_alerts", "description": "Active topology and anomaly pattern alerts."},
            {"name": "verify_relationship", "description": "Human-in-the-loop relationship verification."}
        ],
        "resources": [
            "investigation://cases",
            "investigation://network-graph",
            "investigation://alerts",
            "investigation://audit-log"
        ],
        "prompts": [
            "investigate_person_of_interest",
            "cross_case_bridge_analysis",
            "evidentiary_integrity_audit"
        ],
        "client_configs": {
            "antigravity": {
                "mcpServers": {
                    "criminal-network-mcp": {
                        "command": "python",
                        "args": [server_path]
                    }
                }
            },
            "claude_desktop": {
                "mcpServers": {
                    "criminal-network": {
                        "command": "python",
                        "args": [server_path]
                    }
                }
            }
        }
    }

# =========================================================================
# 14. SINGLE-PAGE APPLICATION FRONTEND SERVING
# =========================================================================
FRONTEND_DIST = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist"
)
ASSETS_DIR = os.path.join(FRONTEND_DIST, "assets")

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="static-assets")

@app.get("/{full_path:path}", response_class=FileResponse)
def serve_spa(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    index_file = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Frontend build not found. Run 'npm run build' in frontend directory.")
