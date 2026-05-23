import logging
import uuid
from datetime import datetime, timezone

from schema_crawler import crawl_schemas
from classifier import classify_columns
from masking_applier import apply_all_masks
from audit_logger import build_audit_log, save_audit_log, print_audit_summary

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def run_pipeline() -> None:
    run_id = str(uuid.uuid4())[:8]
    started_at = datetime.now(timezone.utc)

    print("\n")
    print("=" * 55)
    print("   DATA CLASSIFICATION & MASKING PIPELINE")
    print("=" * 55)
    print("\n  Run ID    : " + run_id)
    print("  Started   : " + started_at.strftime("%Y-%m-%d %H:%M:%S UTC"))

    print("\n  Step 1/4  : Crawling database schemas...")
    columns = crawl_schemas()
    print("  Found " + str(len(columns)) + " columns across all tables")

    print("\n  Step 2/4  : Classifying columns...")
    classification_results = classify_columns(columns)
    sensitive = [r for r in classification_results if r.tier.value != "INTERNAL"]
    print("  Classified " + str(len(classification_results)) + " columns")
    print("  Sensitive columns found: " + str(len(sensitive)))

    print("\n  Step 3/4  : Applying masking policies...")
    masking_results = apply_all_masks(classification_results)
    print("  Masking policies applied: " + str(len(masking_results)))

    print("\n  Step 4/4  : Writing audit log...")
    log = build_audit_log(run_id, classification_results, masking_results)
    filename = save_audit_log(log)
    print("  Audit log saved: " + filename)

    finished_at = datetime.now(timezone.utc)
    duration = (finished_at - started_at).total_seconds()

    print("\n")
    print("=" * 55)
    print("   PIPELINE COMPLETE")
    print("=" * 55)
    print("\n  Status    : SUCCESS")
    print("  Duration  : " + str(round(duration, 2)) + " seconds")
    print("  Columns   : " + str(len(columns)) + " scanned")
    print("  Sensitive : " + str(len(sensitive)) + " columns protected")
    print("  Audit Log : " + filename)

    print("\n  Classification Summary:")
    for tier, count in log.classifications.items():
        bar = "#" * count
        print("    " + tier.ljust(12) + " : " + bar + " (" + str(count) + ")")

    print("\n  Protected Columns:")
    for r in masking_results:
        print("    - " + r.column + " (" + r.tier + ") -> " + r.policy_applied)

    print("\n" + "=" * 55 + "\n")


if __name__ == "__main__":
    run_pipeline()