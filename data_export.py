from pathlib import Path
from typing import Dict, Union

from ecommerce import HospitalManagementSystem


def export_hospital_data(
    hospital: HospitalManagementSystem, destination: Union[str, Path]
) -> Dict[str, Path]:
    output_directory = Path(destination)
    output_directory.mkdir(parents=True, exist_ok=True)

    tables = {
        "patients": hospital.patients,
        "doctors": hospital.doctors,
        "appointments": hospital.appointments,
        "bills": hospital.bills,
    }
    exported_files = {}
    for name, records in tables.items():
        file_path = output_directory / f"{name}.csv"
        records.to_csv(file_path, index=False)
        exported_files[name] = file_path
    return exported_files
