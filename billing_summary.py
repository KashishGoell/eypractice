import pandas as pd

from ecommerce import HospitalManagementSystem


def get_billing_summary(hospital: HospitalManagementSystem) -> pd.DataFrame:
    totals = hospital.bills.groupby("patient_id", as_index=False).agg(
        total_amount=("amount", "sum"),
        bill_count=("bill_id", "count"),
    )
    patients = hospital.patients[["patient_id", "name"]].rename(
        columns={"name": "patient"}
    )
    summary = patients.merge(totals, on="patient_id", how="left")
    summary["total_amount"] = summary["total_amount"].fillna(0.0)
    summary["bill_count"] = summary["bill_count"].fillna(0).astype(int)
    return summary
