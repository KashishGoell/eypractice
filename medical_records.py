import pandas as pd

from ecommerce import HospitalManagementSystem


class MedicalRecordBook:
    def __init__(self, hospital: HospitalManagementSystem) -> None:
        self.hospital = hospital
        self.records = pd.DataFrame(
            columns=["record_id", "patient_id", "note"]
        )

    def add_note(self, patient_id: int, note: str) -> int:
        if patient_id not in self.hospital.patients["patient_id"].values:
            raise ValueError("Patient ID does not exist.")
        note = note.strip()
        if not note:
            raise ValueError("Medical note cannot be empty.")

        record_id = (
            1
            if self.records.empty
            else int(self.records["record_id"].max()) + 1
        )
        self.records.loc[len(self.records)] = [record_id, patient_id, note]
        return record_id

    def get_patient_records(self, patient_id: int) -> pd.DataFrame:
        if patient_id not in self.hospital.patients["patient_id"].values:
            raise ValueError("Patient ID does not exist.")
        return self.records.loc[
            self.records["patient_id"] == patient_id
        ].copy().reset_index(drop=True)
