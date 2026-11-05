import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os
from datetime import date

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Attendance Management System",
    page_icon="📚",
    layout="wide"
)

FILE_NAME = "attendance.json"


# ---------------- PROFESSIONAL DESIGN ----------------

st.markdown("""
<style>

.stApp {
    background-color: #F4F7FB;
}

[data-testid="stSidebar"] {
    background-color: #14243A;
}

[data-testid="stSidebar"] * {
    color: white !important;
}

.main-title {
    font-size: 30px;
    font-weight: bold;
    color: #14243A;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #E5EAF0;
    box-shadow: 0 3px 10px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------

def load_data():

    if os.path.exists(FILE_NAME):

        with open(FILE_NAME, "r") as file:
            data = json.load(file)

        data.setdefault("students", [])
        data.setdefault("attendance", {})
        data.setdefault("status", {})

        for name in data["students"]:
            data["status"].setdefault(name, "Active")

        return data

    return {
        "students": [],
        "attendance": {},
        "status": {}
    }


data = load_data()


# ---------------- SAVE DATA ----------------

def save_data():

    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4)


# ---------------- ATTENDANCE SUMMARY ----------------

def attendance_summary(name):

    present = 0
    absent = 0

    for records in data["attendance"].values():

        if records.get(name) == "Present":
            present += 1

        elif records.get(name) == "Absent":
            absent += 1

    total = present + absent

    percentage = (
        present / total * 100 if total > 0 else 0
    )

    return present, absent, total, percentage


# ---------------- SIDEBAR ----------------

st.sidebar.title("📚 AMS")
st.sidebar.caption("ATTENDANCE MANAGEMENT")

menu = st.sidebar.radio(
    "MAIN MENU",
    [
        "Dashboard",
        "Add Student",
        "View Students",
        "Edit Student",
        "Delete Student",
        "Change Student Status",
        "Mark Attendance",
        "Attendance Correction",
        "Attendance Records",
        "Attendance Percentage"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Student Attendance Portal")


# ---------------- HEADER ----------------

st.markdown(
    '<div class="main-title">Attendance Management System</div>',
    unsafe_allow_html=True
)

st.caption("Professional Student Attendance Dashboard")

st.divider()


# ==================================================
# 1. DASHBOARD
# ==================================================

if menu == "Dashboard":

    st.subheader("Dashboard Overview")

    today = str(date.today())

    today_records = data["attendance"].get(today, {})

    total = len(data["students"])

    active = sum(
        data["status"].get(n, "Active") == "Active"
        for n in data["students"]
    )

    inactive = total - active

    present = sum(
        v == "Present" for v in today_records.values()
    )

    absent = sum(
        v == "Absent" for v in today_records.values()
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total Students", total)
    c2.metric("Active", active)
    c3.metric("Inactive", inactive)
    c4.metric("Present Today", present)
    c5.metric("Absent Today", absent)

    st.subheader("Attendance Analytics")

    if present + absent > 0:

        df = pd.DataFrame({
            "Status": ["Present", "Absent"],
            "Students": [present, absent]
        })

        fig = px.pie(
            df,
            names="Status",
            values="Students",
            hole=0.5
        )

        st.plotly_chart(fig, use_container_width=True)

    else:

        st.info("Today's attendance is not marked yet.")


# ==================================================
# 2. ADD STUDENT
# ==================================================

elif menu == "Add Student":

    st.subheader("Add New Student")

    name = st.text_input("Enter Student Name")

    if st.button("Add Student"):

        name = name.strip()

        if not name:

            st.warning("Enter student name.")

        elif any(
            n.lower() == name.lower()
            for n in data["students"]
        ):

            st.warning("Student already exists.")

        else:

            data["students"].append(name)

            data["status"][name] = "Active"

            save_data()

            st.success("Student added successfully!")


# ==================================================
# 3. VIEW STUDENTS
# ==================================================

elif menu == "View Students":

    st.subheader("Student List")

    search = st.text_input("Search Student")

    rows = []

    for i, name in enumerate(data["students"], start=1):

        if search.lower() in name.lower():

            rows.append({
                "S.No": i,
                "Student Name": name,
                "Status": data["status"].get(name, "Active")
            })

    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# 4. EDIT STUDENT
# ==================================================

elif menu == "Edit Student":

    st.subheader("Edit Student Details")

    if data["students"]:

        old_name = st.selectbox(
            "Select Student",
            data["students"]
        )

        new_name = st.text_input(
            "Enter New Name",
            value=old_name
        )

        if st.button("Update Student"):

            new_name = new_name.strip()

            if not new_name:

                st.warning("Name cannot be empty.")

            elif any(
                n.lower() == new_name.lower() and n != old_name
                for n in data["students"]
            ):

                st.warning("Student already exists.")

            else:

                index = data["students"].index(old_name)

                data["students"][index] = new_name

                old_status = data["status"].pop(
                    old_name, "Active"
                )

                data["status"][new_name] = old_status

                for records in data["attendance"].values():

                    if old_name in records:

                        records[new_name] = records.pop(old_name)

                save_data()

                st.success("Student updated successfully!")

    else:

        st.info("No students available.")


# ==================================================
# 5. DELETE STUDENT
# ==================================================

elif menu == "Delete Student":

    st.subheader("Delete Student")

    if data["students"]:

        name = st.selectbox(
            "Select Student",
            data["students"]
        )

        confirm = st.checkbox(
            "Confirm permanent deletion including attendance history"
        )

        if st.button("Delete Student"):

            if confirm:

                data["students"].remove(name)

                data["status"].pop(name, None)

                for records in data["attendance"].values():

                    records.pop(name, None)

                save_data()

                st.success("Student deleted successfully!")

            else:

                st.warning("Please confirm deletion.")

    else:

        st.info("No students available.")


# ==================================================
# 6. CHANGE STUDENT STATUS
# ==================================================

elif menu == "Change Student Status":

    st.subheader("Change Student Status")

    if data["students"]:

        name = st.selectbox(
            "Select Student",
            data["students"]
        )

        current = data["status"].get(name, "Active")

        st.write("Current Status:", current)

        new_status = st.selectbox(
            "Select New Status",
            ["Active", "Inactive"]
        )

        if st.button("Update Status"):

            data["status"][name] = new_status

            save_data()

            st.success("Status updated successfully!")

    else:

        st.info("No students available.")


# ==================================================
# 7. MARK ATTENDANCE
# ==================================================

elif menu == "Mark Attendance":

    st.subheader("Mark Attendance")

    active_students = [
        n for n in data["students"]
        if data["status"].get(n, "Active") == "Active"
    ]

    selected_date = st.date_input(
        "Select Date",
        value=date.today()
    )

    day = str(selected_date)

    if not active_students:

        st.warning("No active students available.")

    elif day in data["attendance"]:

        st.warning(
            "Attendance already marked. "
            "Use Attendance Correction to update it."
        )

    else:

        with st.form("attendance_form"):

            records = {}

            for name in active_students:

                records[name] = st.selectbox(
                    name,
                    ["Present", "Absent"],
                    key="mark_" + name
                )

            submit = st.form_submit_button(
                "Save Attendance"
            )

            if submit:

                data["attendance"][day] = records

                save_data()

                st.success("Attendance saved successfully!")


# ==================================================
# 8. ATTENDANCE CORRECTION
# ==================================================

elif menu == "Attendance Correction":

    st.subheader("Attendance Correction")

    dates = sorted(data["attendance"].keys())

    if dates:

        selected_date = st.selectbox(
            "Select Attendance Date",
            dates
        )

        records = data["attendance"][selected_date]

        names = [
            n for n in data["students"]
            if n in records
        ]

        if names:

            name = st.selectbox(
                "Select Student",
                names
            )

            current = records[name]

            st.write("Current Status:", current)

            new_status = st.selectbox(
                "Correct Status",
                ["Present", "Absent"],
                index=0 if current == "Present" else 1
            )

            if st.button("Save Correction"):

                records[name] = new_status

                save_data()

                st.success("Attendance corrected!")

        else:

            st.info("No student records available.")

    else:

        st.info("No attendance records available.")


# ==================================================
# 9. ATTENDANCE RECORDS
# ==================================================

elif menu == "Attendance Records":

    st.subheader("Attendance Records")

    rows = []

    for i, name in enumerate(data["students"], start=1):

        present, absent, total, percentage = attendance_summary(name)

        rows.append({
            "S.No": i,
            "Student Name": name,
            "Present": present,
            "Absent": absent,
            "Total": total
        })

    if rows:

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode("utf-8"),
            "attendance_records.csv",
            "text/csv"
        )

    else:

        st.info("No students available.")


# ==================================================
# 10. ATTENDANCE PERCENTAGE
# ==================================================

elif menu == "Attendance Percentage":

    st.subheader("Attendance Percentage Report")

    rows = []

    for i, name in enumerate(data["students"], start=1):

        present, absent, total, percentage = attendance_summary(name)

        rows.append({
            "S.No": i,
            "Student Name": name,
            "Present": present,
            "Total": total,
            "Percentage": round(percentage, 2)
        })

    if rows:

        df = pd.DataFrame(rows)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download Excel",
            df.to_csv(index=False).encode("utf-8"),
            "attendance_percentage.csv",
            "text/csv"
        )

    else:

        st.info("No students available.")


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "Attendance Management System | Developed using Python & Streamlit"
)