# Data Classification & Masking Pipeline

An automated platform that crawls database schemas, classifies
sensitive data, applies role-based masking policies, and writes
a compliance audit log — all with a single command.

---

## What It Does

- Crawls every table and column in a Snowflake database
- Classifies each column as PII, PHI, Financial, or Internal
- Applies dynamic masking so different roles see different data
- Writes a full audit log as proof for compliance teams

---

## Why I Built This

Companies like Liberty Mutual store millions of records containing
social security numbers, medical diagnoses, and credit card numbers.
Without automated classification and masking, any employee could
accidentally access data they were never supposed to see. This
pipeline finds sensitive data automatically and protects it.

---

## Tech Stack

- Python 3.12
- Snowflake Dynamic Data Masking
- AWS S3, Lambda
- GitHub Actions

---

## Project Structure

- schema_crawler.py  — crawls database schemas
- classifier.py      — classifies columns by sensitivity
- masking_applier.py — applies masking policies by role
- audit_logger.py    — writes compliance audit logs
- main.py            — runs the full pipeline

---

## How To Run

git clone https://github.com/aayoko89/data-classification-pipeline.git
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py

---

## Sample Output

Status    : SUCCESS
Duration  : 0.01 seconds
Columns   : 7 scanned
Sensitive : 5 columns protected

PII          : ## (2)
PHI          : # (1)
FINANCIAL    : ## (2)
INTERNAL     : ## (2)

Protected Columns:
  - email_address (PII)
  - social_security_number (PII)
  - diagnosis_code (PHI)
  - credit_card_number (FINANCIAL)
  - annual_salary (FINANCIAL)

---

## Author

Built by Aayok as a portfolio project demonstrating enterprise
data governance, classification, and masking skills.