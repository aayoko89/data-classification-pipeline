import re
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from schema_crawler import ColumnMetadata

logger = logging.getLogger(__name__)


class DataTier(str, Enum):
    PII = "PII"
    PHI = "PHI"
    FINANCIAL = "FINANCIAL"
    INTERNAL = "INTERNAL"
    PUBLIC = "PUBLIC"


@dataclass
class ClassificationResult:
    column: ColumnMetadata
    tier: DataTier
    confidence: float
    reason: str
    method: str


PII_KEYWORDS = [
    "ssn", "social_security", "email", "phone", "mobile",
    "first_name", "last_name", "full_name", "address",
    "zip_code", "postal", "dob", "date_of_birth", "birthday",
    "passport", "driver_license", "ip_address", "gender",
]

PHI_KEYWORDS = [
    "diagnosis", "icd_code", "medical_record", "patient_id",
    "mrn", "prescription", "medication", "treatment",
    "lab_result", "blood_type", "allergy",
]

FINANCIAL_KEYWORDS = [
    "credit_card", "card_number", "bank_account", "account_number",
    "routing_number", "salary", "wage", "payroll", "income", "tax_id",
]


def match_keywords(column_name: str, keywords: list) -> bool:
    col_lower = column_name.lower()
    for keyword in keywords:
        if keyword in col_lower:
            return True
    return False


def classify_by_pattern(col: ColumnMetadata) -> Optional[ClassificationResult]:
    name = col.column

    if match_keywords(name, PHI_KEYWORDS):
        return ClassificationResult(
            column=col,
            tier=DataTier.PHI,
            confidence=0.90,
            reason="Column name matched PHI keyword",
            method="pattern"
        )
    if match_keywords(name, PII_KEYWORDS):
        return ClassificationResult(
            column=col,
            tier=DataTier.PII,
            confidence=0.90,
            reason="Column name matched PII keyword",
            method="pattern"
        )
    if match_keywords(name, FINANCIAL_KEYWORDS):
        return ClassificationResult(
            column=col,
            tier=DataTier.FINANCIAL,
            confidence=0.90,
            reason="Column name matched FINANCIAL keyword",
            method="pattern"
        )
    return None


def classify_columns(columns: list) -> list:
    results = []
    unmatched = []

    for col in columns:
        result = classify_by_pattern(col)
        if result:
            results.append(result)
        else:
            unmatched.append(col)

    for col in unmatched:
        results.append(ClassificationResult(
            column=col,
            tier=DataTier.INTERNAL,
            confidence=0.75,
            reason="No sensitive pattern found",
            method="fallback"
        ))

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from schema_crawler import crawl_schemas

    columns = crawl_schemas()
    results = classify_columns(columns)

    print("\n")
    print("=" * 55)
    print("   CLASSIFICATION RESULTS")
    print("=" * 55)

    for r in results:
        if r.tier == DataTier.PHI:
            icon = "PURPLE - PHI"
        elif r.tier == DataTier.PII:
            icon = "RED - PII"
        elif r.tier == DataTier.FINANCIAL:
            icon = "ORANGE - FINANCIAL"
        else:
            icon = "GREEN - SAFE"

        print("\n  Column    : " + r.column.column)
        print("  Tier      : " + icon)
        print("  Confidence: " + str(int(r.confidence * 100)) + "%")
        print("  Reason    : " + r.reason)
        print("  Method    : " + r.method)