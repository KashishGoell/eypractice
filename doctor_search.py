import pandas as pd

from ecommerce import HospitalManagementSystem


def search_doctors(
    hospital: HospitalManagementSystem, query: str
) -> pd.DataFrame:
    query = query.strip()
    if not query:
        raise ValueError("Search query cannot be empty.")

    matches = hospital.doctors["name"].str.contains(
        query, case=False, na=False, regex=False
    ) | hospital.doctors["specialty"].str.contains(
        query, case=False, na=False, regex=False
    )
    return hospital.doctors.loc[matches].copy().reset_index(drop=True)
