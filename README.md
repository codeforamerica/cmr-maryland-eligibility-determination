# Maryland Eligibility Determination

A **Streamlit-based** tool for **automated record clearance** eligibility determination.

## 📌 Overview

The **Maryland Eligibility Determination** tool processes CSV files containing case records, categorizes charges, and determines eligibility based on predefined criteria.

## 🚀 Features

- **Upload Case Data**: Supports CSV file uploads.
- **Automated Case Analysis**: Categorizes charges as misdemeanors, felonies, non-convictions, and excluded misdemeanors.
- **Eligibility Determination**: Checks cases against rules engines.
- **Structured Case List**: Displays cases in an interactive table with eligibility labels.
- **Detailed Case View**: Allows users to inspect charges and case history.
- **Download Processed Data**: Export results as CSV files.

---

## ℹ️ Example Data Notice

This tool provides **synthetic example data** specific to **Maryland**, but the methodology can be applied to other state datasets.

- The **example dataset** includes **randomized case data** that follows Maryland eligibility laws.
- **We do not collect or store** any personally identifiable information (**PII**).
- Users can **upload their own data** for eligibility determination.

---

## ⚖️ Eligibility Criteria

| **Case Type**             | **Eligibility**                                 |
| ------------------------- | ----------------------------------------------- |
| **Non-Convictions**       | ✅ Eligible after **3 years**                   |
| **Misdemeanors**          | ✅ Eligible after **7 years** (unless excluded) |
| **Felonies**              | ❌ Not Eligible                                 |
| **Domestic Violence**     | ❌ Not Eligible                                 |
| **Excluded Misdemeanors** | ❌ Not Eligible                                 |

> Cases involving **excluded misdemeanors** (e.g., **Second-degree assault**) are **not eligible** for clearance.

---

## 🚨 Excluded Misdemeanors

Some misdemeanors are **excluded** from eligibility, meaning they **cannot** be cleared.

| **Statute Code** | **Charge Description** |
| ---------------- | ---------------------- |
| **CR.3.203**     | Second-degree assault  |
| **27.342**       | Second-degree assault  |

---

## 🔄 Non-Conviction Terms

Cases with the following dispositions are classified as **non-convictions**:

- **DISMISSED**
- **ACQUITTED**
- **NOLLE PROSEQUI**
- **NOT GUILTY**

> **Non-convictions** become **eligible after 3 years**.

---

## ⏳ Waiting Periods

| **Charge Type**    | **Waiting Period** |
| ------------------ | ------------------ |
| **Misdemeanor**    | **7 years**        |
| **Non-Conviction** | **3 years**        |

---

## 🛠 Installation & Setup

### Prerequisites

- **Python 3.8+** installed.
- **pip** package manager available.

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

---

## 📂 CSV File Format

The uploaded CSV file should include the following **required columns**:

### **1️⃣ Parties CSV**

| **Column Name** | **Description**             |
| --------------- | --------------------------- |
| **PartyID**     | Unique ID for each party    |
| **Name**        | Full name of the individual |
| **Race**        | Race of the individual      |
| **Sex**         | Gender                      |
| **DOB**         | Date of birth               |
| **Address**     | Residential address         |
| **City**        | City of residence           |
| **State**       | State of residence          |
| **Zip Code**    | ZIP code                    |
| **Aliases**     | Known aliases               |

### **2️⃣ Cases CSV**

| **Column Name**      | **Description**                        |
| -------------------- | -------------------------------------- |
| **CaseID**           | Unique identifier for the case         |
| **PartyID**          | Foreign key linking to Parties CSV     |
| **Case Title**       | Title of the case                      |
| **Case Number**      | Unique case number                     |
| **Court System**     | District or Circuit court              |
| **Location**         | Court location                         |
| **Case Type**        | Type of case (e.g., Domestic Violence) |
| **Filing Date**      | Date the case was filed                |
| **Case Status**      | Open, Closed, or Dismissed             |
| **Judicial Officer** | Name of the judge                      |

### **3️⃣ Charges CSV**

| **Column Name**        | **Description**                       |
| ---------------------- | ------------------------------------- |
| **ChargeID**           | Unique identifier for each charge     |
| **CaseID**             | Foreign key linking to Cases CSV      |
| **Charge No**          | Charge number                         |
| **CJIS Code**          | Maryland CJIS charge code             |
| **Statute Code**       | Legal statute reference               |
| **Charge Description** | Description of the charge             |
| **Charge Class**       | Classification (Misdemeanor/Felony)   |
| **Offense Date**       | Date when the offense occurred        |
| **Agency Name**        | Law enforcement agency involved       |
| **Plea**               | Plea entered by the defendant         |
| **Plea Date**          | Date when the plea was entered        |
| **Disposition**        | Final outcome of the charge           |
| **Disposition Date**   | Date when the disposition was entered |

---

### **📌 Important Notes**

- Ensure that the uploaded files **match the expected format**.
- All **CSV files must include the required column names**.
- **Foreign key relationships**:
  - `PartyID` in **Cases CSV** must match `PartyID` in **Parties CSV**.
  - `CaseID` in **Charges CSV** must match `CaseID` in **Cases CSV**.

---

## 🗂 Usage Guide

1. **Select Data Source**: Choose between **"Use example data"** or **"Upload your own data"**.
2. **Upload CSV Files**: If using your own data, upload the required files:
   - **Parties CSV**
   - **Cases CSV**
   - **Charges CSV**
3. **Process the File**: Click **"📩 Submit and Process File"** to analyze the case data.
4. **Process the File**: Click **"📩 Submit and Process File"** to analyze the case data.
5. **View Case List**: Cases will be categorized into:
   - ✅ **Eligible Cases**
   - ❌ **Ineligible Cases**
6. **Check Case Details**: Click the **🔍 button** next to any case for a detailed breakdown.
7. **Download Processed Data**: Click **"⬇️ Download Processed Cases CSV"** to save the results.

> **Note:** The eligibility determination is based on Maryland expungement laws and predefined rules. Ensure your CSV files meet the expected format for accurate results.

---

## 📊 Example Eligibility Outcomes

- ✅ **Eligible**: Case meets eligibility criteria.
- ⏳ **Wait until YYYY-MM-DD**: Case is eligible but requires waiting until the specified date.
- ❌ **Not Eligible - Felony Disposition**: Case is ineligible due to felony conviction.
- ❌ **Not Eligible - Domestic Violence Case**: Domestic violence cases are not eligible.
- ❌ **Not Eligible - Excluded Misdemeanor(s)**: The charge falls under excluded misdemeanors.
