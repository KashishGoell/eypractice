from ecommerce import HospitalManagementSystem


def cancel_appointment(
    hospital: HospitalManagementSystem, appointment_id: int
) -> None:
    matches = hospital.appointments["appointment_id"] == appointment_id
    if not matches.any():
        raise ValueError("Appointment ID does not exist.")

    hospital.appointments.drop(
        index=hospital.appointments.index[matches], inplace=True
    )
    hospital.appointments.reset_index(drop=True, inplace=True)
