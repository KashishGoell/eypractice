import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class HospitalManagementSystem:
    def __init__(self):
        self.patients = pd.DataFrame(
            columns=["patient_id", "name", "age", "phone"]
        )
        self.doctors = pd.DataFrame(
            columns=["doctor_id", "name", "specialty"]
        )
        self.appointments = pd.DataFrame(
            columns=["appointment_id", "patient_id", "doctor_id", "date_time", "reason"]
        )
        self.bills = pd.DataFrame(
            columns=["bill_id", "patient_id", "description", "amount"]
        )

    @staticmethod
    def _next_id(records: pd.DataFrame, id_column: str) -> int:
        if records.empty:
            return 1
        return int(records[id_column].max()) + 1

    def add_patient(self, name: str, age: int, phone: str) -> int:
        name = name.strip()
        if not name:
            raise ValueError("Patient name cannot be empty.")
        if age <= 0:
            raise ValueError("Patient age must be a positive number.")

        patient_id = self._next_id(self.patients, "patient_id")
        self.patients.loc[len(self.patients)] = [patient_id, name, age, phone.strip()]
        return patient_id

    def add_doctor(self, name: str, specialty: str) -> int:
        name = name.strip()
        specialty = specialty.strip()
        if not name or not specialty:
            raise ValueError("Doctor name and specialty are required.")

        doctor_id = self._next_id(self.doctors, "doctor_id")
        self.doctors.loc[len(self.doctors)] = [doctor_id, name, specialty]
        return doctor_id

    def schedule_appointment(
        self, patient_id: int, doctor_id: int, date_time: str, reason: str
    ) -> int:
        if patient_id not in self.patients["patient_id"].values:
            raise ValueError("Patient ID does not exist.")
        if doctor_id not in self.doctors["doctor_id"].values:
            raise ValueError("Doctor ID does not exist.")
        try:
            parsed_date = pd.to_datetime(date_time, format="%Y-%m-%d %H:%M")
        except ValueError as error:
            raise ValueError("Use date and time format YYYY-MM-DD HH:MM.") from error

        appointment_id = self._next_id(self.appointments, "appointment_id")
        self.appointments.loc[len(self.appointments)] = [
            appointment_id,
            patient_id,
            doctor_id,
            parsed_date.strftime("%Y-%m-%d %H:%M"),
            reason.strip(),
        ]
        return appointment_id

    def add_bill(self, patient_id: int, description: str, amount: float) -> int:
        if patient_id not in self.patients["patient_id"].values:
            raise ValueError("Patient ID does not exist.")
        description = description.strip()
        if not description:
            raise ValueError("Bill description cannot be empty.")
        if amount <= 0:
            raise ValueError("Bill amount must be greater than zero.")

        bill_id = self._next_id(self.bills, "bill_id")
        self.bills.loc[len(self.bills)] = [
            bill_id,
            patient_id,
            description,
            round(amount, 2),
        ]
        return bill_id

    @staticmethod
    def _show_records(title: str, records: pd.DataFrame) -> None:
        print(f"\n{title}")
        if records.empty:
            print("No records found.")
        else:
            print(records.to_string(index=False))

    def show_patients(self) -> None:
        self._show_records("Patients", self.patients)

    def show_doctors(self) -> None:
        self._show_records("Doctors", self.doctors)

    def show_appointments(self) -> None:
        if self.appointments.empty:
            self._show_records("Appointments", self.appointments)
            return
        records = self.appointments.merge(
            self.patients[["patient_id", "name"]].rename(
                columns={"name": "patient"}
            ),
            on="patient_id",
        ).merge(
            self.doctors[["doctor_id", "name"]].rename(
                columns={"name": "doctor"}
            ),
            on="doctor_id",
        )
        self._show_records("Appointments", records)

    def show_bills(self) -> None:
        if self.bills.empty:
            self._show_records("Bills", self.bills)
            return
        records = self.bills.merge(
            self.patients[["patient_id", "name"]].rename(
                columns={"name": "patient"}
            ),
            on="patient_id",
        )
        self._show_records("Bills", records)

    def show_analytics(self) -> None:
        revenue = float(np.sum(self.bills["amount"].to_numpy(dtype=float)))
        print(f"\nTotal revenue: ${revenue:,.2f}")
        if self.appointments.empty and self.bills.empty:
            print("Add appointments or bills to see charts.")
            return

        figure, axes = plt.subplots(1, 2, figsize=(12, 5))
        if self.appointments.empty:
            axes[0].set_visible(False)
        else:
            appointment_counts = (
                self.appointments.merge(
                    self.doctors[["doctor_id", "name"]], on="doctor_id"
                )
                .groupby("name", as_index=False)
                .size()
                .rename(columns={"name": "doctor", "size": "appointments"})
            )
            sns.barplot(
                data=appointment_counts,
                x="doctor",
                y="appointments",
                ax=axes[0],
                color="steelblue",
            )
            axes[0].set_title("Appointments by doctor")
            axes[0].tick_params(axis="x", rotation=30)

        if self.bills.empty:
            axes[1].set_visible(False)
        else:
            revenue_by_service = (
                self.bills.groupby("description", as_index=False)["amount"].sum()
            )
            sns.barplot(
                data=revenue_by_service,
                x="description",
                y="amount",
                ax=axes[1],
                color="seagreen",
            )
            axes[1].set_title("Revenue by service")
            axes[1].set_ylabel("Revenue")
            axes[1].tick_params(axis="x", rotation=30)

        figure.tight_layout()
        plt.show()

    def run(self) -> None:
        actions = {
            "1": self._add_patient_from_input,
            "2": self._add_doctor_from_input,
            "3": self._schedule_appointment_from_input,
            "4": self._add_bill_from_input,
            "5": self.show_patients,
            "6": self.show_doctors,
            "7": self.show_appointments,
            "8": self.show_bills,
            "9": self.show_analytics,
        }

        while True:
            print(
                "\n=== Hospital Management System ==="
                "\n1. Add patient"
                "\n2. Add doctor"
                "\n3. Schedule appointment"
                "\n4. Add bill"
                "\n5. View patients"
                "\n6. View doctors"
                "\n7. View appointments"
                "\n8. View bills"
                "\n9. View analytics"
                "\n0. Exit"
            )
            choice = input("Choose an option: ").strip()
            if choice == "0":
                print("Goodbye.")
                break
            action = actions.get(choice)
            if action is None:
                print("Choose a number from 0 to 9.")
                continue
            try:
                action()
            except ValueError as error:
                print(f"Error: {error}")

    def _add_patient_from_input(self) -> None:
        name = input("Patient name: ")
        age = int(input("Patient age: "))
        phone = input("Phone number: ")
        patient_id = self.add_patient(name, age, phone)
        print(f"Patient added with ID {patient_id}.")

    def _add_doctor_from_input(self) -> None:
        name = input("Doctor name: ")
        specialty = input("Specialty: ")
        doctor_id = self.add_doctor(name, specialty)
        print(f"Doctor added with ID {doctor_id}.")

    def _schedule_appointment_from_input(self) -> None:
        self.show_patients()
        patient_id = int(input("Patient ID: "))
        self.show_doctors()
        doctor_id = int(input("Doctor ID: "))
        date_time = input("Appointment date and time (YYYY-MM-DD HH:MM): ")
        reason = input("Appointment reason: ")
        appointment_id = self.schedule_appointment(
            patient_id, doctor_id, date_time, reason
        )
        print(f"Appointment scheduled with ID {appointment_id}.")

    def _add_bill_from_input(self) -> None:
        self.show_patients()
        patient_id = int(input("Patient ID: "))
        description = input("Service or bill description: ")
        amount = float(input("Amount: "))
        bill_id = self.add_bill(patient_id, description, amount)
        print(f"Bill added with ID {bill_id}.")


if __name__ == "__main__":
    HospitalManagementSystem().run()
