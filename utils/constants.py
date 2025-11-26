
REQUIRED_COLUMNS = {
    "parties": ["PartyID", "Name", "Race", "Sex", "DOB", "Address", "City", "State", "Zip Code", "Aliases"],
    "cases": ["CaseID", "PartyID", "Case Title", "Case Number", "Court System", "Location", "Case Type", "Filing Date", "Case Status", "Judicial Officer"],
    "charges": ["ChargeID", "CaseID", "Charge No", "CJIS Code", "Statute Code", "Charge Description", "Charge Class", "Offense Date", "Agency Name", "Plea", "Plea Date", "Disposition", "Disposition Date"],
}

EXCLUDED_MISDEMEANORS = {
    "CR.3.203": "Second-degree assault",
    "27.342": "Second-degree assault",
}

NON_CONVICTION_TERMS = ["DISMISSED",
                        "ACQUITTED", "NOLLE PROSEQUI", "NOT GUILTY", "STET"]


WAIT_PERIODS = {
    "misdemeanor": 7 * 365,  # 7 years
    "non_conviction": 3 * 365  # 3 years
}
