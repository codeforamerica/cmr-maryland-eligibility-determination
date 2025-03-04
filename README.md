# Maryland Eligibility Determination

A **Streamlit-based** tool for **automated record clearance** eligibility determination.

## 📌 Overview

The **Maryland Eligibility Determination** processes CSV files containing case records, categorizes charges, and determines eligibility based on predefined criteria.

## 🚀 Features

- **Upload Case Data**: Supports CSV file uploads.
- **Automated Case Analysis**: Categorizes charges as misdemeanors, felonies, non-convictions, and excluded misdemeanors.
- **Eligibility Determination**: Checks cases against rules engines.
- **Structured Case List**: Displays cases in an interactive table with eligibility labels.
- **Detailed Case View**: Allows users to inspect charges and case history.
- **Download Processed Data**: Export results as CSV files.

---

## ⚖️ Eligibility Criteria

| **Case Type**         | **Eligibility**                                 |
| --------------------- | ----------------------------------------------- |
| Non-Convictions       | ✅ Eligible after **3 years**                   |
| Misdemeanors          | ✅ Eligible after **7 years** (unless excluded) |
| Felonies              | ❌ Not Eligible                                 |
| Domestic Violence     | ❌ Not Eligible                                 |
| Excluded Misdemeanors | ❌ Not Eligible                                 |

Cases involving **excluded misdemeanors** (e.g., **Second-degree assault**) are **not eligible** for clearance.

---

## 🛠 Installation & Setup

### Prerequisites

- **Python 3.8+** installed.
- **pip** package manager available.

### Prerequisites

Ensure you have **Python 3.8+** and **pip** installed on your system.

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/code-for-america/cmr-maryland-eligibility-determination.git
   cd cmr-maryland-eligibility-determination
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```
   Additional flags may be required to avoid security-related errors when running locally:
   ```bash
   streamlit run app.py --server.enableCORS false --server.enableXsrfProtection false
   ```

## CSV File Format

The uploaded CSV file should include the following columns:

| **Column Name**    | **Description**                                   |
| ------------------ | ------------------------------------------------- |
| Case Number        | Unique case identifier                            |
| Defendant Name     | Name of the person                                |
| Charge Class       | Classification (Misdemeanor, Felony)              |
| Statute Code       | Statue code                                       |
| Charge Description | Details about the charge                          |
| Case Type          | Category (Domestic Violence)                      |
| Disposition        | Outcome (Dismissed, Acquitted, Probation, Guilty) |
| Disposition Date   | Date when the case was resolved                   |

## Usage Guide

1. **Upload a CSV File**: Click the "📂 Upload CSV" button and select a file.
2. **Process the File**: Click "📩 Submit and Process File" to analyze the case data.
3. **View Case List**: See eligible and ineligible cases.
4. **Check Case Details**: Click the 🔍 button next to any case for more details.
5. **Download Processed Data**: Click "⬇️ Download Processed Cases CSV" to save the results.

## Example Eligibility Outcomes

- ✅ **Eligible**: Case meets eligibility criteria.
- ⏳ **Wait until YYYY-MM-DD**: Case is eligible but requires waiting until the specified date.
- ❌ **Not Eligible - Felony Disposition**: Case is ineligible due to felony conviction.
- ❌ **Not Eligible - Domestic Violence Case**: Domestic violence cases are not eligible.
- ❌ **Not Eligible - Excluded Misdemeanor(s)**: The charge falls under excluded misdemeanors.
