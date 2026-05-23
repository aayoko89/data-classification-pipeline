import logging
from dataclasses import dataclass
from typing import Optional

from classifier import ClassificationResult, DataTier

logger = logging.getLogger(__name__)


@dataclass
class MaskingResult:
    column: str
    table: str
    tier: str
    policy_applied: str
    masked_examples: dict


def mask_pii(value: str, role: str) -> str:
    if role == "ADMIN":
        return value
    if role == "ENGINEER":
        if "@" in value:
            parts = value.split("@")
            return "****@" + parts[1]
        if len(value) > 4:
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
        return "****"
    return "**REDACTED**"


def mask_phi(value: str, role: str) -> str:
    if role == "ADMIN":
        return value
    if role == "ENGINEER":
        return "PHI-" + str(abs(hash(value)))[:8]
    return "**PHI-REDACTED**"


def mask_financial(value: str, role: str) -> str:
    if role == "ADMIN":
        return value
    if role == "ENGINEER":
        if len(value) > 4:
            return "****-****-****-" + value[-4:]
        return "****"
    return "**FINANCIAL-REDACTED**"


def apply_mask(result: ClassificationResult) -> Optional[MaskingResult]:
    if result.tier in (DataTier.INTERNAL, DataTier.PUBLIC):
        return None

    col = result.column
    sample = str(col.sample_values[0]) if col.sample_values else "sample_value"

    if result.tier == DataTier.PII:
        policy = "pii_masking_policy"
        examples = {
            "ADMIN":    mask_pii(sample, "ADMIN"),
            "ENGINEER": mask_pii(sample, "ENGINEER"),
            "ANALYST":  mask_pii(sample, "ANALYST"),
        }
    elif result.tier == DataTier.PHI:
        policy = "phi_masking_policy"
        examples = {
            "ADMIN":    mask_phi(sample, "ADMIN"),
            "ENGINEER": mask_phi(sample, "ENGINEER"),
            "ANALYST":  mask_phi(sample, "ANALYST"),
        }
    else:
        policy = "financial_masking_policy"
        examples = {
            "ADMIN":    mask_financial(sample, "ADMIN"),
            "ENGINEER": mask_financial(sample, "ENGINEER"),
            "ANALYST":  mask_financial(sample, "ANALYST"),
        }

    return MaskingResult(
        column=col.column,
        table=col.database + "." + col.schema + "." + col.table,
        tier=result.tier.value,
        policy_applied=policy,
        masked_examples=examples,
    )


def apply_all_masks(results: list) -> list:
    masking_results = []
    skipped = 0

    for result in results:
        masked = apply_mask(result)
        if masked:
            masking_results.append(masked)
        else:
            skipped += 1

    logger.info(
        str(len(masking_results)) + " masking policies applied, " +
        str(skipped) + " columns skipped (not sensitive)"
    )
    return masking_results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    from schema_crawler import crawl_schemas
    from classifier import classify_columns

    columns = crawl_schemas()
    results = classify_columns(columns)
    masking_results = apply_all_masks(results)

    print("\n")
    print("=" * 55)
    print("   MASKING POLICIES APPLIED")
    print("=" * 55)

    for m in masking_results:
        print("\n  Column : " + m.column)
        print("  Table  : " + m.table)
        print("  Tier   : " + m.tier)
        print("  Policy : " + m.policy_applied)
        print("  How it looks by role:")
        for role, masked_value in m.masked_examples.items():
            print("    " + role + " sees: " + masked_value)