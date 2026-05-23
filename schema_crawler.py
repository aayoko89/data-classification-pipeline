import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ColumnMetadata:
    database: str
    schema: str
    table: str
    column: str
    data_type: str
    sample_values: list
    nullable: bool


SAMPLE_COLUMNS = [
    ColumnMetadata(
        database="LIBERTY_DB",
        schema="CUSTOMERS",
        table="ACCOUNTS",
        column="email_address",
        data_type="VARCHAR",
        sample_values=["john@example.com", "jane@example.com"],
        nullable=False,
    ),
    ColumnMetadata(
        database="LIBERTY_DB",
        schema="CUSTOMERS",
        table="ACCOUNTS",
        column="social_security_number",
        data_type="VARCHAR",
        sample_values=["***-**-****"],
        nullable=False,
    ),
    ColumnMetadata(
        database="LIBERTY_DB",
        schema="CLAIMS",
        table="MEDICAL",
        column="diagnosis_code",
        data_type="VARCHAR",
        sample_values=["ICD-10", "Z00.00"],
        nullable=True,
    ),
    ColumnMetadata(
        database="LIBERTY_DB",
        schema="PAYMENTS",
        table="TRANSACTIONS",
        column="credit_card_number",
        data_type="VARCHAR",
        sample_values=["****-****-****-1234"],
        nullable=False,
    ),
    ColumnMetadata(
        database="LIBERTY_DB",
        schema="PAYMENTS",
        table="TRANSACTIONS",
        column="annual_salary",
        data_type="FLOAT",
        sample_values=["75000.00", "95000.00"],
        nullable=True,
    ),
    ColumnMetadata(
        database="LIBERTY_DB",
        schema="PRODUCTS",
        table="POLICIES",
        column="policy_type",
        data_type="VARCHAR",
        sample_values=["AUTO", "HOME", "LIFE"],
        nullable=False,
    ),
    ColumnMetadata(
        database="LIBERTY_DB",
        schema="PRODUCTS",
        table="POLICIES",
        column="created_at",
        data_type="TIMESTAMP",
        sample_values=["2026-01-01 00:00:00"],
        nullable=False,
    ),
]


def crawl_schemas() -> list:
    logger.info(f"Crawling database schemas...")
    logger.info(f"Found {len(SAMPLE_COLUMNS)} columns")
    return SAMPLE_COLUMNS


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    columns = crawl_schemas()

    print("\n")
    print("=" * 55)
    print("   SCHEMA CRAWLER RESULTS")
    print("=" * 55)

    current_table = ""
    for col in columns:
        table_key = col.database + "." + col.schema + "." + col.table
        if table_key != current_table:
            print("\n  Table: " + table_key)
            print("  " + "-" * 45)
            current_table = table_key
        print("  Column : " + col.column)
        print("  Type   : " + col.data_type)
        print("  Samples: " + str(col.sample_values))
        print()