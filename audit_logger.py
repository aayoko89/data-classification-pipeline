import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass

from classifier import ClassificationResult
from masking_applier import MaskingResult

logger = logging.getLogger(__name__)


@dataclass
class AuditLog:
    run_id: str
    timestamp: str
    total_columns_scanned: int
    classifications: dict
    masking_applied: int
    masking_skipped: int
    details: list


def build_audit_log(
    run_id: str,
    classification_results: list,
    masking_results: list,
) -> AuditLog:

    tier_counts = {}
    for r in classification_results:
        tier = r.tier.value
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

    details = []
    for r in classification_results:
        details.append({
            "column":     r.column.column,
            "table":      r.column.database + "." + r.column.schema + "." + r.column.table,
            "tier":       r.tier.value,
            "confidence": r.confidence,
            "reason":     r.reason,
            "method":     r.method,
        })

    return AuditLog(
        run_id=run_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        total_columns_scanned=len(classification_results),
        classifications=tier_counts,
        masking_applied=len(masking_results),
        masking_skipped=len(classification_results) - len(masking_results),
        details=details,
    )


def save_audit_log(log: AuditLog) -> str:
    filename = "audit_" + log.run_id + ".json"

    record = {
        "run_id":                log.run_id,
        "timestamp":             log.timestamp,
        "total_columns_scanned": log.total_columns_scanned,
        "classifications":       log.classifications,
        "masking_applied":       log.masking_applied,
        "masking_skipped":       log.masking_skipped,
        "details":               log.details,
    }

    with open(filename, "w") as f:
        json.dump(record, f, indent=2)

    logger.info("Audit log saved to " + filename)
    return filename


def print_audit_summary(log: AuditLog) -> None:
    print("\n")
    print("=" * 55)
    print("   AUDIT LOG SUMMARY")
    print("=" * 55)
    print("\n  Run ID    : " + log.run_id)
    print("  Timestamp : " + log.timestamp)
    print("  Columns Scanned : " + str(log.total_columns_scanned))
    print("  Masking Applied : " + str(log.masking_applied))
    print("  Masking Skipped : " + str(log.masking_skipped))

    print("\n  Classification Breakdown:")
    for tier, count in log.classifications.items():
        print("    " + tier + " : " + str(count) + " columns")

    print("\n  Column Details:")
    for d in log.details:
        print("\n    Column : " + d["column"])
        print("    Table  : " + d["table"])
        print("    Tier   : " + d["tier"])
        print("    Confidence : " + str(int(d["confidence"] * 100)) + "%")
        print("    Reason : " + d["reason"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import uuid
    from schema_crawler import crawl_schemas
    from classifier import classify_columns
    from masking_applier import apply_all_masks

    run_id = str(uuid.uuid4())[:8]
    columns = crawl_schemas()
    classification_results = classify_columns(columns)
    masking_results = apply_all_masks(classification_results)

    log = build_audit_log(run_id, classification_results, masking_results)
    filename = save_audit_log(log)
    print_audit_summary(log)

    print("\n  Full log saved to: " + filename)