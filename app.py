from __future__ import annotations

from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd
import streamlit as st

from appointment_cancellation import cancel_appointment
from appointment_history import get_patient_appointment_history
from billing_summary import get_billing_summary
from data_export import export_hospital_data
from doctor_search import search_doctors
from ecommerce import HospitalManagementSystem
from medical_records import MedicalRecordBook
from patient_profiles import update_patient_profile


st.set_page_config(
    page_title="Carepoint | Hospital Management",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#172b43"
BEIGE = "#f4efe4"

st.markdown(
    f"""
    <style>
    :root {{
        --navy: {NAVY};
        --beige: {BEIGE};
        --ink: #172b43;
        --muted: #788493;
        --line: #e8e5de;
        --green: #496d58;
    }}
    html, body, [class*="css"] {{
        font-family: 'Segoe UI', sans-serif;
    }}
    .stApp {{
        background: #f7f6f2;
        color: var(--ink);
    }}
    [data-testid="stSidebar"] {{
        background: var(--navy);
        border-right: 1px solid rgba(255,255,255,.08);
    }}
    [data-testid="stSidebar"] * {{
        color: #f5f0e7;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label {{
        padding: .55rem .65rem;
        border-radius: 9px;
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {{
        background: rgba(255,255,255,.08);
    }}
    [data-testid="stSidebar"] [data-testid="stRadio"] label p {{
        font-size: .92rem;
        font-weight: 500;
    }}
    h1, h2, h3 {{
        font-family: 'Segoe UI', sans-serif !important;
        color: var(--ink);
        letter-spacing: -.035em;
    }}
    h1 {{ font-size: 2rem !important; }}
    h2 {{ font-size: 1.3rem !important; }}
    .brand {{
        font: 800 1.5rem 'Segoe UI', sans-serif;
        letter-spacing: -.06em;
        padding: .55rem .15rem 1.2rem;
        color: #f4efe4;
    }}
    .brand span {{ color: #d7bd91; }}
    .eyebrow {{
        color: #8a7353;
        font: 700 .7rem 'Segoe UI', sans-serif;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }}
    .hero {{
        background: var(--navy);
        color: #f7f3eb;
        padding: 1.65rem 1.8rem;
        border-radius: 16px;
        margin: .25rem 0 1.35rem;
    }}
    .hero h1 {{ color: #f7f3eb !important; margin: .1rem 0 .45rem; }}
    .hero p {{ color: #c9d0d5; margin: 0; }}
    .hero .eyebrow {{ color: #d7bd91; }}
    [data-testid="stMetric"] {{
        background: #fff;
        border: 1px solid var(--line);
        padding: 1rem 1.1rem;
        border-radius: 13px;
    }}
    [data-testid="stMetricLabel"] p {{ color: var(--muted); font-size: .82rem; }}
    [data-testid="stMetricValue"] {{ color: var(--ink); font-family: 'Segoe UI', sans-serif; }}
    [data-testid="stForm"] {{
        background: #fff;
        border: 1px solid var(--line);
        padding: 1rem 1.1rem;
        border-radius: 13px;
    }}
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }}
    .stButton > button, .stDownloadButton > button {{
        border-radius: 9px;
        font-weight: 600;
    }}
    .stButton > button[kind="primary"], .stDownloadButton > button {{
        background: var(--navy);
        border-color: var(--navy);
        color: #fff;
    }}
    div[data-testid="stTabs"] button {{
        color: var(--ink);
    }}
    hr {{ border-color: var(--line); }}
    </style>
    """,
    unsafe_allow_html=True,
)


def get_hospital() -> HospitalManagementSystem:
    if "hospital" not in st.session_state:
        hospital = HospitalManagementSystem()
        hospital.add_doctor("Dr. Maya Chen", "Cardiology")
        hospital.add_doctor("Dr. Elias Morgan", "Family Medicine")
        hospital.add_doctor("Dr. Sofia Patel", "Dermatology")
        st.session_state.hospital = hospital
        st.session_state.medical_records = MedicalRecordBook(hospital)
    return st.session_state.hospital


def show_result(action, success_message: str) -> None:
    try:
        action()
    except (ValueError, TypeError) as error:
        st.error(str(error))
    else:
        st.success(success_message)


def patient_options(hospital: HospitalManagementSystem) -> list[int]:
    return hospital.patients["patient_id"].astype(int).tolist()


def patient_label(hospital: HospitalManagementSystem, patient_id: int) -> str:
    return f"Patient #{patient_id}"


def doctor_label(hospital: HospitalManagementSystem, doctor_id: int) -> str:
    matches = hospital.doctors.loc[
        hospital.doctors["doctor_id"] == doctor_id, ["name", "specialty"]
    ]
    doctor = matches.iloc[0]
    return f"#{doctor_id} · {doctor['name']} — {doctor['specialty']}"


def appointment_table(hospital: HospitalManagementSystem) -> pd.DataFrame:
    appointments = hospital.appointments
    if appointments.empty:
        return appointments.copy()
    patients = hospital.patients[["patient_id", "name"]].rename(
        columns={"name": "Patient"}
    )
    doctors = hospital.doctors[["doctor_id", "name", "specialty"]].rename(
        columns={"name": "Doctor", "specialty": "Specialty"}
    )
    return (
        appointments.merge(patients, on="patient_id")
        .merge(doctors, on="doctor_id")
        .rename(
            columns={
                "appointment_id": "ID",
                "date_time": "Date & time",
                "reason": "Reason",
            }
        )[["ID", "Patient", "Doctor", "Specialty", "Date & time", "Reason"]]
        .sort_values("Date & time", ascending=False)
    )


def page_header(title: str, subtitle: str) -> None:
    st.markdown(f'<div class="eyebrow">Carepoint / {title}</div>', unsafe_allow_html=True)
    st.title(title)
    st.caption(subtitle)


def navigate(page: str) -> None:
    st.session_state.page = page


def dashboard(hospital: HospitalManagementSystem) -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Your practice, in good hands</div>
            <h1>A clearer view of care.</h1>
            <p>Manage your people, appointments, and billing — all in one place.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total_revenue = float(hospital.bills["amount"].sum())
    stats = st.columns(4)
    stats[0].metric("Patients", len(hospital.patients))
    stats[1].metric("Care team", len(hospital.doctors))
    stats[2].metric("Appointments", len(hospital.appointments))
    stats[3].metric("Total billed", f"${total_revenue:,.2f}")

    left, right = st.columns([1.35, 1])
    with left:
        st.subheader("Appointment schedule")
        rows = appointment_table(hospital)
        if rows.empty:
            st.info("Your schedule is clear. Add an appointment to get started.")
        else:
            st.dataframe(rows.head(6), width="stretch", hide_index=True)
    with right:
        st.subheader("Quick actions")
        st.caption("Jump straight into the tasks you use most.")
        for label, page in [
            ("Add a patient", "Patients"),
            ("Schedule an appointment", "Appointments"),
            ("Record a bill", "Billing"),
        ]:
            st.button(
                label,
                width="stretch",
                key=f"quick_{page}",
                on_click=navigate,
                args=(page,),
            )
        if hospital.bills.empty:
            st.markdown(
                '<div class="eyebrow" style="margin-top:1.2rem">Getting started</div>',
                unsafe_allow_html=True,
            )
            st.caption("Add patients and doctors, then schedule visits and keep billing up to date.")

    st.divider()
    st.subheader("Appointments by doctor")
    if hospital.appointments.empty:
        st.caption("Appointment analytics will appear here once visits are scheduled.")
    else:
        counts = (
            hospital.appointments.merge(
                hospital.doctors[["doctor_id", "name"]], on="doctor_id"
            )
            .groupby("name", as_index=False)
            .size()
            .rename(columns={"name": "Doctor", "size": "Appointments"})
            .set_index("Doctor")
        )
        st.bar_chart(counts, color="#496d58")


def patients_page(
    hospital: HospitalManagementSystem, records: MedicalRecordBook
) -> None:
    page_header("Patients", "Keep patient profiles and clinical notes up to date.")
    add_tab, profile_tab, notes_tab = st.tabs(
        ["Add patient", "Patient profiles", "Medical records"]
    )

    with add_tab:
        st.subheader("New patient")
        with st.form("add_patient_form", clear_on_submit=True):
            name = st.text_input("Full name")
            age = st.number_input("Age", min_value=1, max_value=130, value=30)
            phone = st.text_input("Phone number")
            submitted = st.form_submit_button("Add patient", type="primary")
        if submitted:
            show_result(
                lambda: hospital.add_patient(name, int(age), phone),
                "Patient added successfully.",
            )

    with profile_tab:
        if hospital.patients.empty:
            st.info("Add a patient first to view and edit profiles.")
        else:
            st.subheader("Patient directory")
            st.dataframe(
                hospital.patients.rename(
                    columns={
                        "patient_id": "ID",
                        "name": "Name",
                        "age": "Age",
                        "phone": "Phone",
                    }
                ),
                width="stretch",
                hide_index=True,
            )
            st.subheader("Update a profile")
            patient_id = st.selectbox(
                "Select patient",
                patient_options(hospital),
                format_func=lambda value: patient_label(hospital, value),
                key="profile_patient",
            )
            current = hospital.patients.loc[
                hospital.patients["patient_id"] == patient_id
            ].iloc[0]
            with st.form("update_patient_form"):
                name = st.text_input("Name", value=str(current["name"]))
                age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=130,
                    value=int(current["age"]),
                )
                phone = st.text_input("Phone", value=str(current["phone"]))
                submitted = st.form_submit_button("Save changes", type="primary")
            if submitted:
                show_result(
                    lambda: update_patient_profile(
                        hospital,
                        patient_id,
                        name=name,
                        age=int(age),
                        phone=phone,
                    ),
                    "Patient profile updated.",
                )

    with notes_tab:
        if hospital.patients.empty:
            st.info("Add a patient first to create medical records.")
        else:
            st.subheader("Add a clinical note")
            patient_id = st.selectbox(
                "Patient",
                patient_options(hospital),
                format_func=lambda value: patient_label(hospital, value),
                key="note_patient",
            )
            with st.form("add_note_form", clear_on_submit=True):
                note = st.text_area("Medical note", placeholder="Enter a visit note or care update")
                submitted = st.form_submit_button("Save note", type="primary")
            if submitted:
                show_result(
                    lambda: records.add_note(patient_id, note),
                    "Medical note saved.",
                )
            patient_records = records.get_patient_records(patient_id)
            st.subheader("Record history")
            if patient_records.empty:
                st.caption("No notes have been added for this patient.")
            else:
                st.dataframe(
                    patient_records.rename(
                        columns={"record_id": "ID", "note": "Note"}
                    )[["ID", "Note"]],
                    width="stretch",
                    hide_index=True,
                )


def doctors_page(hospital: HospitalManagementSystem) -> None:
    page_header("Care team", "Find a specialist or add a doctor to your practice.")
    search, add = st.tabs(["Find a doctor", "Add a doctor"])
    with search:
        query = st.text_input("Search by doctor or specialty", placeholder="e.g. cardiology")
        if hospital.doctors.empty:
            st.info("No doctors yet. Add a doctor to build your care team.")
        elif query.strip():
            matches = search_doctors(hospital, query)
            if matches.empty:
                st.info("No doctors match that search.")
            else:
                st.dataframe(
                    matches.rename(
                        columns={
                            "doctor_id": "ID",
                            "name": "Name",
                            "specialty": "Specialty",
                        }
                    ),
                    width="stretch",
                    hide_index=True,
                )
        else:
            st.caption("Search by name or specialty to find a doctor.")
            st.dataframe(
                hospital.doctors.rename(
                    columns={
                        "doctor_id": "ID",
                        "name": "Name",
                        "specialty": "Specialty",
                    }
                ),
                width="stretch",
                hide_index=True,
            )
    with add:
        with st.form("add_doctor_form", clear_on_submit=True):
            name = st.text_input("Doctor name")
            specialty = st.text_input("Specialty")
            submitted = st.form_submit_button("Add doctor", type="primary")
        if submitted:
            show_result(
                lambda: hospital.add_doctor(name, specialty),
                "Doctor added to the care team.",
            )


def appointments_page(hospital: HospitalManagementSystem) -> None:
    page_header("Appointments", "Schedule visits, review patient history, and manage your calendar.")
    schedule_tab, manage_tab, history_tab = st.tabs(
        ["Schedule", "Manage appointments", "Patient history"]
    )
    with schedule_tab:
        if hospital.patients.empty or hospital.doctors.empty:
            st.info("Add at least one patient and one doctor before scheduling a visit.")
        else:
            st.subheader("Book a visit")
            with st.form("schedule_appointment_form", clear_on_submit=True):
                patient_id = st.selectbox(
                    "Patient",
                    patient_options(hospital),
                    format_func=lambda value: patient_label(hospital, value),
                )
                doctor_ids = hospital.doctors["doctor_id"].astype(int).tolist()
                doctor_id = st.selectbox(
                    "Doctor",
                    doctor_ids,
                    format_func=lambda value: doctor_label(hospital, value),
                )
                date_col, time_col = st.columns(2)
                date_value = date_col.date_input("Date")
                time_value = time_col.time_input("Time")
                reason = st.text_input("Reason for visit")
                submitted = st.form_submit_button("Schedule appointment", type="primary")
            if submitted:
                date_time = f"{date_value:%Y-%m-%d} {time_value:%H:%M}"
                show_result(
                    lambda: hospital.schedule_appointment(
                        patient_id, doctor_id, date_time, reason
                    ),
                    "Appointment scheduled.",
                )

    with manage_tab:
        st.subheader("All appointments")
        rows = appointment_table(hospital)
        if rows.empty:
            st.info("No appointments have been scheduled.")
        else:
            st.dataframe(rows, width="stretch", hide_index=True)
            appointment_ids = hospital.appointments["appointment_id"].astype(int).tolist()
            selected = st.selectbox(
                "Appointment to cancel",
                appointment_ids,
                format_func=lambda value: f"#{value} · {rows.loc[rows['ID'] == value, 'Patient'].iloc[0]} — {rows.loc[rows['ID'] == value, 'Date & time'].iloc[0]}",
            )
            if st.button("Cancel selected appointment", type="primary"):
                show_result(
                    lambda: cancel_appointment(hospital, selected),
                    "Appointment cancelled.",
                )

    with history_tab:
        if hospital.patients.empty:
            st.info("Add a patient first to view appointment history.")
        else:
            patient_id = st.selectbox(
                "Patient",
                patient_options(hospital),
                format_func=lambda value: patient_label(hospital, value),
                key="history_patient",
            )
            history = get_patient_appointment_history(hospital, patient_id)
            if history.empty:
                st.caption("This patient has no appointment history.")
            else:
                st.dataframe(
                    history.rename(
                        columns={
                            "appointment_id": "ID",
                            "date_time": "Date & time",
                            "reason": "Reason",
                            "doctor": "Doctor",
                            "specialty": "Specialty",
                        }
                    )[["ID", "Date & time", "Doctor", "Specialty", "Reason"]],
                    width="stretch",
                    hide_index=True,
                )


def billing_page(hospital: HospitalManagementSystem) -> None:
    page_header("Billing & reports", "Record services, review balances, and export your practice data.")
    billing_tab, analytics_tab, export_tab = st.tabs(
        ["Billing", "Analytics", "Export data"]
    )
    with billing_tab:
        if hospital.patients.empty:
            st.info("Add a patient before creating a bill.")
        else:
            st.subheader("Add a bill")
            with st.form("add_bill_form", clear_on_submit=True):
                patient_id = st.selectbox(
                    "Patient",
                    patient_options(hospital),
                    format_func=lambda value: patient_label(hospital, value),
                )
                description = st.text_input("Service or description")
                amount = st.number_input(
                    "Amount ($)", min_value=0.01, value=50.00, step=10.00, format="%.2f"
                )
                submitted = st.form_submit_button("Record bill", type="primary")
            if submitted:
                show_result(
                    lambda: hospital.add_bill(patient_id, description, amount),
                    "Bill recorded.",
                )

        st.subheader("Billing summary")
        if hospital.patients.empty:
            st.caption("Billing summaries will appear when patients are added.")
        else:
            summary = get_billing_summary(hospital).rename(
                columns={
                    "patient_id": "Patient ID",
                    "patient": "Patient",
                    "total_amount": "Total billed ($)",
                    "bill_count": "Bills",
                }
            )
            st.dataframe(
                summary,
                width="stretch",
                hide_index=True,
                column_config={"Total billed ($)": st.column_config.NumberColumn(format="$%.2f")},
            )
        if not hospital.bills.empty:
            bills = hospital.bills.merge(
                hospital.patients[["patient_id", "name"]], on="patient_id"
            ).rename(
                columns={
                    "bill_id": "ID",
                    "name": "Patient",
                    "description": "Description",
                    "amount": "Amount ($)",
                }
            )
            st.subheader("Recent bills")
            st.dataframe(
                bills[["ID", "Patient", "Description", "Amount ($)"]],
                width="stretch",
                hide_index=True,
                column_config={"Amount ($)": st.column_config.NumberColumn(format="$%.2f")},
            )

    with analytics_tab:
        st.subheader("Practice analytics")
        amount = float(hospital.bills["amount"].sum())
        metric_cols = st.columns(3)
        metric_cols[0].metric("Total revenue", f"${amount:,.2f}")
        metric_cols[1].metric("Appointments", len(hospital.appointments))
        metric_cols[2].metric("Bills issued", len(hospital.bills))
        chart_col, revenue_col = st.columns(2)
        with chart_col:
            st.markdown("**Appointments by doctor**")
            if hospital.appointments.empty:
                st.caption("No appointment data to chart yet.")
            else:
                chart = (
                    hospital.appointments.merge(
                        hospital.doctors[["doctor_id", "name"]], on="doctor_id"
                    )
                    .groupby("name", as_index=False)
                    .size()
                    .rename(columns={"name": "Doctor", "size": "Appointments"})
                    .set_index("Doctor")
                )
                st.bar_chart(chart, color="#496d58")
        with revenue_col:
            st.markdown("**Revenue by service**")
            if hospital.bills.empty:
                st.caption("No billing data to chart yet.")
            else:
                chart = (
                    hospital.bills.groupby("description", as_index=False)["amount"]
                    .sum()
                    .rename(columns={"description": "Service", "amount": "Revenue ($)"})
                    .set_index("Service")
                )
                st.bar_chart(chart, color="#b3976c")

    with export_tab:
        st.subheader("Download your data")
        st.caption(
            "Download the patient, doctor, appointment, and billing tables together as a ZIP of CSV files."
        )
        if st.button("Prepare CSV export", type="primary"):
            archive = BytesIO()
            with TemporaryDirectory() as directory:
                files = export_hospital_data(hospital, Path(directory))
                with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
                    for name, file_path in files.items():
                        bundle.write(file_path, arcname=f"{name}.csv")
            st.session_state.export_data = archive.getvalue()
        if "export_data" in st.session_state:
            st.download_button(
                "Download carepoint-data.zip",
                data=st.session_state.export_data,
                file_name="carepoint-data.zip",
                mime="application/zip",
            )


def main() -> None:
    hospital = get_hospital()
    records: MedicalRecordBook = st.session_state.medical_records

    with st.sidebar:
        st.markdown('<div class="brand">care<span>point</span>.</div>', unsafe_allow_html=True)
        st.caption("HOSPITAL MANAGEMENT")
        st.radio(
            "Workspace",
            ["Overview", "Patients", "Care team", "Appointments", "Billing & reports"],
            key="page",
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("Data is kept in this app session. Export a backup before restarting.")

    page = st.session_state.page
    if page == "Overview":
        dashboard(hospital)
    elif page == "Patients":
        patients_page(hospital, records)
    elif page == "Care team":
        doctors_page(hospital)
    elif page == "Appointments":
        appointments_page(hospital)
    else:
        billing_page(hospital)


if __name__ == "__main__":
    main()
