from typing import Optional

from ecommerce import HospitalManagementSystem


def update_patient_profile(
    hospital: HospitalManagementSystem,
    patient_id: int,
    *,
    name: Optional[str] = None,
    age: Optional[int] = None,
    phone: Optional[str] = None,
) -> None:
    matches = hospital.patients["patient_id"] == patient_id
    if not matches.any():
        raise ValueError("Patient ID does not exist.")
    if name is None and age is None and phone is None:
        raise ValueError("Provide at least one profile field to update.")

    updates = {}
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Patient name cannot be empty.")
        updates["name"] = name
    if age is not None:
        if age <= 0:
            raise ValueError("Patient age must be a positive number.")
        updates["age"] = age
    if phone is not None:
        updates["phone"] = phone.strip()

    for column, value in updates.items():
        hospital.patients.loc[matches, column] = value
