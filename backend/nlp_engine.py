import re
import datetime
from typing import List, Dict, Any, Tuple, Optional
import pypdfium2

class EvidenceExtractionEngine:
    """
    Evidence Provenance & NLP Entity/Relationship Extraction Engine.
    Extracts entities and relationships from fragmented intelligence records
    with exact character offsets, context excerpts, and confidence metrics.
    """

    KNOWN_ORGANIZATION_SUFFIXES = [
        "LLC", "LTD", "INC", "CORP", "HOLDINGS", "GROUP", "LOGISTICS", "TRADING",
        "ENTERPRISES", "INVESTMENTS", "MARITIME", "SHIPPING", "FINANCIAL", "CAPITAL",
        "BANK", "NETWORK", "SYNDICATE", "CARTEL", "CONSORTIUM"
    ]

    VEHICLE_MAKES = [
        "Toyota", "Mercedes-Benz", "Mercedes", "BMW", "Audi", "Ford", "Chevrolet",
        "Honda", "Freightliner", "Volvo", "Scania", "Range Rover", "Porsche", "Lexus"
    ]

    KNOWN_LOCATIONS = [
        "Rotterdam", "Antwerp", "Hamburg", "Miami", "Zurich", "Geneva", "Dubai",
        "Panama City", "Bogota", "Medellin", "Cali", "Sinaloa", "Guadalajara",
        "Singapore", "Hong Kong", "London", "Amsterdam", "Algeciras", "Valencia",
        "Santos", "Le Havre", "Frankfurt", "New York", "Los Angeles", "Houston"
    ]

    PHONE_REGEX = re.compile(r'(?:\+?(\d{1,3}))?[-.\s]?(?:\(?(\d{2,4})\)?[-.\s]?)?(\d{3,4})[-.\s]?(\d{3,4})\b')
    CRYPTO_BTC_REGEX = re.compile(r'\b([13][a-km-zA-HJ-NP-Z1-9]{25,34})\b')
    CRYPTO_ETH_REGEX = re.compile(r'\b(0x[a-fA-F0-9]{40})\b')
    BANK_ACCOUNT_REGEX = re.compile(r'\b(?:IBAN\s*[:#]?\s*([A-Z]{2}\d{2}[A-Z0-9]{12,30})|Account\s*#?\s*(\d{8,16}))\b', re.IGNORECASE)
    IMEI_REGEX = re.compile(r'\b(?:IMEI[:\s]+)?(\d{15})\b', re.IGNORECASE)
    PLATE_REGEX = re.compile(r'\b(?:Plate|License Plate|Tag)[:\s]+([A-Z0-9]{2,4}[-\s]?[A-Z0-9]{3,4})\b', re.IGNORECASE)
    VIN_REGEX = re.compile(r'\b(?:VIN[:\s]+)?([A-HJ-NPR-Z0-9]{17})\b', re.IGNORECASE)

    @classmethod
    def extract_text_from_file(cls, file_bytes: bytes, filename: str) -> str:
        """Extracts UTF-8 plain text or extracts text from PDF pages."""
        lower_name = filename.lower()
        if lower_name.endswith(".pdf"):
            try:
                pdf = pypdfium2.PdfDocument(file_bytes)
                text_parts = []
                for i, page in enumerate(pdf):
                    textpage = page.get_textpage()
                    page_text = textpage.get_text_range()
                    text_parts.append(f"--- [PAGE {i+1}] ---\n" + page_text)
                return "\n\n".join(text_parts)
            except Exception as e:
                return f"[PDF Parsing Error: {str(e)}]\n" + file_bytes.decode("utf-8", errors="ignore")
        else:
            return file_bytes.decode("utf-8", errors="ignore")

    @classmethod
    def extract_entities(cls, text: str) -> List[Dict[str, Any]]:
        entities: List[Dict[str, Any]] = []
        seen_spans = set()

        def add_entity(name: str, etype: str, conf: float, start: int, end: int, attrs: dict = None):
            span_key = (start, end)
            if span_key in seen_spans or len(name.strip()) < 2:
                return
            seen_spans.add(span_key)
            snippet_start = max(0, start - 50)
            snippet_end = min(len(text), end + 50)
            snippet = text[snippet_start:snippet_end].replace("\n", " ").strip()

            entities.append({
                "name": name.strip(),
                "entity_type": etype,
                "confidence": round(conf, 2),
                "char_start": start,
                "char_end": end,
                "context_snippet": f"...{snippet}...",
                "attributes": attrs or {}
            })

        # 1. Phone Numbers
        for m in cls.PHONE_REGEX.finditer(text):
            raw = m.group(0).strip()
            # Filter out non-phone digit strings like small dates or numbers
            digits = re.sub(r'\D', '', raw)
            if 7 <= len(digits) <= 15:
                add_entity(raw, "PHONE_NUMBER", 0.94, m.start(), m.end(), {"digits": digits})

        # 2. Crypto & Financial Accounts
        for m in cls.CRYPTO_ETH_REGEX.finditer(text):
            add_entity(m.group(1), "FINANCIAL_ACCOUNT", 0.98, m.start(), m.end(), {"account_type": "Ethereum / EVM Wallet"})

        for m in cls.CRYPTO_BTC_REGEX.finditer(text):
            # Verify length
            val = m.group(1)
            if len(val) >= 26:
                add_entity(val, "FINANCIAL_ACCOUNT", 0.96, m.start(), m.end(), {"account_type": "Bitcoin Wallet"})

        for m in cls.BANK_ACCOUNT_REGEX.finditer(text):
            iban = m.group(1)
            acc = m.group(2)
            val = iban if iban else acc
            add_entity(val, "FINANCIAL_ACCOUNT", 0.95, m.start(), m.end(), {"account_type": "IBAN Bank Account" if iban else "Bank Account"})

        # 3. Devices (IMEI)
        for m in cls.IMEI_REGEX.finditer(text):
            add_entity(m.group(1), "DEVICE", 0.97, m.start(), m.end(), {"device_id_type": "IMEI"})

        # 4. Vehicles (Plates & VINs & Models)
        for m in cls.VIN_REGEX.finditer(text):
            add_entity(m.group(1), "VEHICLE", 0.98, m.start(), m.end(), {"identifier_type": "VIN"})

        for m in cls.PLATE_REGEX.finditer(text):
            add_entity(m.group(1), "VEHICLE", 0.92, m.start(), m.end(), {"identifier_type": "License Plate"})

        for vmake in cls.VEHICLE_MAKES:
            v_pattern = re.compile(rf'\b({vmake}\s+[A-Za-z0-9\-]+(?:\s+[A-Za-z0-9\-]+)?)\b', re.IGNORECASE)
            for m in v_pattern.finditer(text):
                add_entity(m.group(1), "VEHICLE", 0.88, m.start(), m.end(), {"make": vmake})

        # 5. Known Locations
        for loc in cls.KNOWN_LOCATIONS:
            loc_pattern = re.compile(rf'\b({re.escape(loc)}(?:\s+(?:Port|Terminal|Airport|Harbor|Logistics Hub|Customs Warehouse))?)\b', re.IGNORECASE)
            for m in loc_pattern.finditer(text):
                add_entity(m.group(1), "LOCATION", 0.92, m.start(), m.end(), {"city_region": loc})

        # 6. Organizations
        for suffix in cls.KNOWN_ORGANIZATION_SUFFIXES:
            org_pattern = re.compile(rf'\b([A-Z][a-zA-Z0-9&\'\.\-]+(?:\s+[A-Z][a-zA-Z0-9&\'\.\-]+){{0,4}}\s+{suffix}\.?)\b')
            for m in org_pattern.finditer(text):
                org_name = m.group(1).strip()
                add_entity(org_name, "ORGANIZATION", 0.95, m.start(), m.end(), {"org_type": "Corporate Entity / Syndicate"})

        # 7. Person Names with Contextual Cues
        # Matches titles/roles followed by Capitalized names, or patterns like "alias 'Nickname'"
        person_cue_pattern = re.compile(
            r'\b(?:suspect|investigated|handler|courier|director|broker|operative|alias|informant|target|subject|contact)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b',
            re.IGNORECASE
        )
        for m in person_cue_pattern.finditer(text):
            name = m.group(1).strip()
            add_entity(name, "PERSON", 0.91, m.start(1), m.end(1), {"detection_source": "Role-Context Heuristic"})

        # Aliases e.g. 'Dmitri Voronov (alias "The Ghost")'
        alias_pattern = re.compile(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\((?:alias|known as|a\.k\.a\.)\s*["\']([^"\']+)["\']\)', re.IGNORECASE)
        for m in alias_pattern.finditer(text):
            real_name = m.group(1).strip()
            alias = m.group(2).strip()
            add_entity(real_name, "PERSON", 0.96, m.start(1), m.end(1), {"alias": alias})

        # General Proper Noun Pairs for Persons (e.g. "Viktor Vance", "Elena Rostova", "Marcus Chen")
        # Filter out capitalized months, days, places
        non_person_words = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
                            "January", "February", "March", "April", "May", "June", "July", "August", "September",
                            "October", "November", "December", "Federal", "Bureau", "United", "States", "Department",
                            "Special", "Division", "Operation", "Task", "Force", "Central", "North", "South", "East", "West"}

        name_candidate_pattern = re.compile(r'\b([A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,18})\b')
        for m in name_candidate_pattern.finditer(text):
            candidate = m.group(1)
            parts = candidate.split()
            if not any(p in non_person_words for p in parts) and not any(loc.lower() in candidate.lower() for loc in cls.KNOWN_LOCATIONS):
                # Check if not already captured under organization or vehicle
                if not any(s in candidate.upper() for s in cls.KNOWN_ORGANIZATION_SUFFIXES):
                    add_entity(candidate, "PERSON", 0.84, m.start(), m.end(), {"detection_source": "Capitalized Name Sequence"})

        return sorted(entities, key=lambda x: x["char_start"])

    @classmethod
    def extract_relationships(cls, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts relationships between co-occurring entities within sentence boundaries
        using relation triggers (financial transfer, communication, ownership, location, command).
        """
        relationships: List[Dict[str, Any]] = []
        sentences = re.split(r'(?<=[.!?])\s+', text)

        # Triggers and their mapped relationship type
        RELATION_TRIGGERS = [
            (re.compile(r'\b(?:transferred|wired|sent|paid|funneled|disbursed|deposited|laundered)\b', re.IGNORECASE), "TRANSFERRED_FUNDS_TO", 0.93),
            (re.compile(r'\b(?:called|telephoned|messaged|communicated|pinged|contacted|coordinated with)\b', re.IGNORECASE), "COMMUNICATED_WITH", 0.91),
            (re.compile(r'\b(?:owns|registered owner|leased|acquired|purchased|purchasing)\b', re.IGNORECASE), "OWNER_OF", 0.92),
            (re.compile(r'\b(?:drives|operated|driving|transported in|intercepted driving)\b', re.IGNORECASE), "OPERATES_VEHICLE", 0.90),
            (re.compile(r'\b(?:commands|directs|reports to|supervises|handled by|handler for|under the direction of)\b', re.IGNORECASE), "SUSPECTED_HANDLER_OF", 0.89),
            (re.compile(r'\b(?:located at|spotted in|resides at|frequents|met at|intercepted at|stored at)\b', re.IGNORECASE), "LOCATED_AT", 0.91),
            (re.compile(r'\b(?:shareholder|director|founder|member|associate|partner|employed by|officer of)\b', re.IGNORECASE), "MEMBER_OF", 0.90),
            (re.compile(r'\b(?:associated with|collaborates with|connected to|conspired with|met with)\b', re.IGNORECASE), "ASSOCIATE_OF", 0.85),
        ]

        # For each sentence, find all entities located within it
        current_offset = 0
        for sent in sentences:
            sent_start = text.find(sent, current_offset)
            sent_end = sent_start + len(sent) if sent_start != -1 else current_offset + len(sent)
            current_offset = sent_end

            # Entities in this sentence
            sent_entities = [e for e in entities if e["char_start"] >= sent_start and e["char_end"] <= sent_end]
            if len(sent_entities) >= 2:
                # Test relationship triggers in this sentence
                for trigger_regex, rtype, base_conf in RELATION_TRIGGERS:
                    if trigger_regex.search(sent):
                        # Link primary entity pairs in this sentence
                        for i in range(len(sent_entities) - 1):
                            src = sent_entities[i]
                            tgt = sent_entities[i + 1]
                            if src["name"] != tgt["name"]:
                                relationships.append({
                                    "source_name": src["name"],
                                    "source_type": src["entity_type"],
                                    "target_name": tgt["name"],
                                    "target_type": tgt["entity_type"],
                                    "relation_type": rtype,
                                    "confidence": base_conf,
                                    "evidence_excerpt": sent.strip(),
                                    "temporal_hint": None
                                })
                        break  # Match primary trigger per sentence

        return relationships

    @classmethod
    def calculate_entity_similarity(cls, e1_name: str, e2_name: str, e1_attrs: dict, e2_attrs: dict) -> Tuple[float, List[str]]:
        """
        Uncertainty-Aware Entity Matching:
        Evaluates potential duplicate/cross-case entity records using Levenshtein distance,
        token overlap, alias matching, and shared identifiers.
        """
        reasons = []
        score = 0.0

        n1 = e1_name.lower().strip()
        n2 = e2_name.lower().strip()

        # Exact match
        if n1 == n2:
            return 1.0, ["Exact canonical name match"]

        # Token set similarity
        t1 = set(n1.split())
        t2 = set(n2.split())
        intersection = t1.intersection(t2)
        union = t1.union(t2)
        jaccard = len(intersection) / len(union) if union else 0.0

        if jaccard >= 0.5:
            reasons.append(f"Significant token overlap ({round(jaccard*100)}%) between '{e1_name}' and '{e2_name}'")
            score += jaccard * 0.65

        # Substring / Prefix match (e.g. 'D. Voronov' or 'Dmitri V.' vs 'Dmitri Voronov')
        if len(n1) > 3 and len(n2) > 3:
            if n1 in n2 or n2 in n1:
                reasons.append("One name is a direct substring/abbreviation of the other")
                score = max(score, 0.82)

        # Check shared identifiers (Phone, IMEI, Account, VIN)
        e1_id = e1_attrs.get("identifiers", {}) or {}
        e2_id = e2_attrs.get("identifiers", {}) or {}
        for k in ["phone", "vin", "iban", "imei", "crypto"]:
            if k in e1_id and k in e2_id and e1_id[k] and e1_id[k] == e2_id[k]:
                reasons.append(f"Identical {k.upper()} identifier match: {e1_id[k]}")
                score = max(score, 0.98)

        # Check aliases
        a1 = [a.lower() for a in (e1_attrs.get("aliases") or [])]
        a2 = [a.lower() for a in (e2_attrs.get("aliases") or [])]
        shared_aliases = set(a1).intersection(set(a2))
        if shared_aliases:
            reasons.append(f"Shared operational alias: {', '.join(shared_aliases)}")
            score = max(score, 0.94)

        if not reasons:
            return 0.0, []

        return round(min(score, 0.99), 2), reasons
