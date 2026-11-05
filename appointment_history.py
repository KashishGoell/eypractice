import pandas as pd

from ecommerce import HospitalManagementSystem


def get_patient_appointment_history(
    hospital: HospitalManagementSystem, patient_id: int
) -> pd.DataFrame:
    if patient_id not in hospital.patients["patient_id"].values:
        raise ValueError("Patient ID does not exist.")

    history = hospital.appointments.loc[
        hospital.appointments["patient_id"] == patient_id
    ]
    doctors = hospital.doctors[["doctor_id", "name", "specialty"]].rename(
        columns={"name": "doctor"}
    )
    return history.merge(doctors, on="doctor_id", how="left").reset_index(drop=True)
