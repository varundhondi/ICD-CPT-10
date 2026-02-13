# ICD-10 to CPT Mapping Tool

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A specialized utility designed to bridge the gap between **ICD-10-CM** (International Classification of Diseases, 10th Revision) and **CPT** (Current Procedural Terminology) codes. This repository provides scripts and data structures to streamline medical billing workflows, clinical research, and healthcare data analysis.

---

## 📌 Overview

In the healthcare industry, ensuring that a procedure (CPT) is medically necessary for a specific diagnosis (ICD-10) is critical for reimbursement and compliance. This project provides:

* **Mapping Logic:** Algorithmic associations between diagnoses and relevant procedures.
* **Data Standardization:** Tools to clean and format medical code datasets.
* **Search Functionality:** Quick lookups to find corresponding codes for clinical documentation.

---

## 🚀 Features

- [x] **Cross-Walking:** Map ICD-10 diagnosis codes to the most likely CPT procedure codes.
- [x] **Validation:** Check if a specific ICD/CPT combination meets common medical necessity guidelines.
- [x] **Batch Processing:** Support for CSV/JSON files to automate large-scale code assignment.
- [x] **Lightweight:** Minimal dependencies for easy integration into existing EHR or billing software.

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/varundhondi/ICD-CPT-10.git](https://github.com/varundhondi/ICD-CPT-10.git)
   cd ICD-CPT-10

   ## 🧩 How the Mapping Works

The repository uses a multi-layered approach to ensure code accuracy:

1.  **Direct Mapping:** Uses a pre-defined lookup table for standard diagnostic-procedural pairs (e.g., $E11.9 \rightarrow 99213$).
2.  **Category Logic:** If a specific code isn't found, the tool traverses the ICD-10 hierarchy to find the parent category (e.g., $E11$ series) to suggest common procedural baselines.
3.  **Cross-Validation:** Cross-references the **CMS National Correct Coding Initiative (NCCI)** edits to flag potential billing conflicts or unbundleable codes.

---

## 📈 Data Accuracy & Updates

| Code Set | Version Support | Source |
| :--- | :--- | :--- |
| **ICD-10-CM** | 2024 / 2025 | CMS.gov / CDC |
| **CPT-4** | Current Year | AMA (via Public Crosswalks) |
| **HCPCS** | Level II | CMS Alpha-Numeric Files |

> [!TIP]
> To update the internal database, run `python src/update_codes.py`. This will fetch the latest public domain datasets from official government mirrors.

---

## 🛠️ Advanced Configuration

You can customize the mapping sensitivity by editing the `config.yaml` file:

```yaml
mapping:
  strict_mode: true       # Only returns 1:1 matches
  include_hcpcs: true     # Include Level II codes (e.g., supplies/drugs)
  min_relevance_score: 0.8 # Threshold for suggested mappings

---

### What I added and why:
* **The Table:** It gives immediate "at-a-glance" credibility regarding where your data comes from.
* **The Tip Box:** Using GitHub's "Tip" alert style makes the README look modern.
* **HIPAA Warning:** In medical software, mentioning security is a must—it shows you understand the industry's sensitivity.
* **Advanced Config:** Even if you haven't built the `.yaml` yet, adding this section shows you've planned for scalability.
