import time as time_module
from datetime import date, datetime
import appointment_manager
import database_conn
import DLL_params
import pool_inventory
import streamlit as st

def is_future(date_obj, time_str):
    full_date_str = f"{date_obj.strftime('%Y-%m-%d')} {time_str}"
    try:
        appt_time = datetime.strptime(full_date_str, "%Y-%m-%d %H:%M")
        return appt_time > datetime.now()
    except ValueError:
        return False

def trigger_reset_and_rerun(success_message):
    st.success(success_message)
    st.session_state["reset_navigation"] = True
    time_module.sleep(3)
    st.rerun()

# --- RTL and Custom CSS Styling ---
st.markdown("""
    <style>
    /* 1. Target the main title of the sidebar radio widget */
    div[data-testid="stSidebar"] div[data-testid="stWidgetLabel"] p {
        font-size: 3rem !important;
        color: #0056b3 !important;
        font-weight: bold !important;
    }

    /* 2. Target ALL text elements (p, span, div) inside radio options */
    div[data-testid="stSidebar"] label[data-baseweb="radio"] * {
        font-size: 3rem !important;
        color: #0056b3 !important;
        font-weight: bold !important;
    }

    /* 3. Ensure hover and active states remain blue */
    div[data-testid="stSidebar"] label[data-baseweb="radio"]: hover * {
        color: #0056b3 !important;
    }

    /* יישור כללי לימין (RTL) */
    .main, div[data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
    }

    div[data-testid="stForm"] {
        direction: rtl;
        text-align: right;
    }
   /* Styling for both standard buttons and form submit buttons */
    .stButton>button, 
    div[data-testid="stFormSubmitButton"]>button {
        width: 100% !important;
        background-color: #99e9ff !important;
        color: black !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        border-radius: 8px !important;
        border: 1px solid #66d9ff !important;
}

    /* Hover state for form submit buttons */
    div[data-testid="stFormSubmitButton"]>button:hover {
    background-color: #80e5ff !important;
    color: black !important;
}
    div[data-testid="stMarkdownContainer"] h1 {
        font-size: 1.8rem !important;
        text-align: right;
        color: #0056b3 !important;
    }
    div[data-testid="stMarkdownContainer"] h3 {
        font-size: 1.3rem !important;
        text-align: right;
        color: #0056b3 !important;
    }

     /* === עיצוב ה-SIDEBAR (גופן מוגדל וכחול + RTL) === */
     /* יישור התפריט הצדדי לימין */
    div[data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
     }

    /* כותרת התפריט הראשי ב-Sidebar */
    div[data-testid="stSidebar"] p {
        font-size: 1.4rem !important;  /* גודל הכותרת */
        color: #003366 !important;     /* כחול כהה */
        font-weight: bold !important;
        text-align: right !important;
    }

    /* טקסט כפתורי הרדיו (האפשרויות בתפריט) */
    div[data-testid="stSidebar"] label[data-baseweb="radio"] div {
        font-size: 1.4rem !important; /* גודל הכתב של האפשרויות */
        color: #0056b3 !important;     /* כחול יפה */
        font-weight: bold !important;
    }

    /* רווח קל בין האפשרויות לנוחות לחיצה */
    div[data-testid="stSidebar"] label[data-baseweb="radio"] {
        margin-bottom: 8px !important;
    }

    </style>
""", unsafe_allow_html=True)

# Ensure database and pool are initialized on startup
database_conn.setup_database()
pool_inventory.populate_availability_pool()



st.set_page_config(
    page_title="קליניקת יופי טופי", page_icon="💆‍♀️", layout="centered"
)

# =========================================================
# 1. RESET LOGIC BEFORE ANY WIDGETS
# =========================================================
if st.session_state.get("reset_navigation", False):
    st.session_state["menu_selection"] = "קביעת תור חדש"
    st.session_state["form_client_name"] = ""
    st.session_state["form_client_phone"] = ""
    st.session_state["reset_navigation"] = False

    if "edit_data" in st.session_state:
        del st.session_state["edit_data"]
    if "edit_appt_id" in st.session_state:
        del st.session_state["edit_appt_id"]

if "menu_selection" not in st.session_state:
    st.session_state["menu_selection"] = "קביעת תור חדש"
if "form_client_name" not in st.session_state:
    st.session_state["form_client_name"] = ""
if "form_client_phone" not in st.session_state:
    st.session_state["form_client_phone"] = ""


# =========================================================
# 2. SINGLE SIDEBAR RADIO INSTANCE
# =========================================================
menu = st.sidebar.radio(
    "תפריט ראשי",
    [
        "קביעת תור חדש",
        "עדכון תור קיים",
        "ביטול תור",
        "צפייה בכל התורים",
        "צפייה בפרטי לקוחות",
    ],
    key="menu_selection",
)


st.markdown("# 💆‍♀️ מערכת ניהול הקליניקה - יופי טופי")

# =========================================================
# 3. VIEWS AND FORMS
# =========================================================

# --- קביעת תור חדש ---
if menu == "קביעת תור חדש":
    st.subheader("קביעת תור חדש")

    with st.form("add_appt_form"):
        client_name = st.text_input("שם הלקוח/ה", key="form_client_name")
        client_phone = st.text_input("מספר טלפון", key="form_client_phone")
        service = st.selectbox("בחר סוג טיפול", DLL_params.services)

        selected_date = st.date_input("בחר תאריך", min_value=date.today())

        available_times = appointment_manager.get_available_times_for_date(
            selected_date.strftime("%Y-%m-%d")
        )
        selected_time = st.selectbox(
            "שעת טיפול",
            available_times if available_times else ["אין שעות פנויות"],
        )

        submitted = st.form_submit_button("שמור תור חדש")

        if submitted:
            if (
                not client_name
                or not client_phone
                or selected_time == "אין שעות פנויות"
            ):
                st.error("יש למלא את כל השדות ולוודא שנבחרה שעה פנויה.")
            elif not is_future(selected_date, selected_time):
                st.error("לא ניתן לקבוע תור לתאריך או שעה בעבר.")
            else:
                formatted_date = selected_date.strftime("%Y-%m-%d")
                appointment_manager.add_appointment(
                    client_name,
                    service,
                    formatted_date,
                    selected_time,
                    client_phone,
                )
                trigger_reset_and_rerun("התור נשמר בהצלחה במערכת!")


# --- עדכון תור קיים ---
elif menu == "עדכון תור קיים":
    st.subheader("עדכון תור קיים")

    appt_id = st.number_input(
        "הכנס מזהה (ID) של התור לעדכון", min_value=0, step=1
    )

    if st.button("טען פרטי תור"):
        existing_data = appointment_manager.get_appointment_by_id(appt_id)
        if not existing_data:
            st.error("לא נמצא תור עם מזהה זה.")
        else:
            st.session_state["edit_appt_id"] = appt_id
            st.session_state["edit_data"] = existing_data

            exist_date, exist_time = existing_data[2], existing_data[3]
            appointment_manager.release_repository_slot_temporary(
                exist_date, exist_time
            )

    if (
        "edit_data" in st.session_state
        and st.session_state.get("edit_appt_id") == appt_id
    ):
        (
            exist_name,
            exist_service,
            exist_date_str,
            exist_time,
            exist_phone,
        ) = st.session_state["edit_data"]

        with st.form("update_appt_form"):
            st.text_input(
                "שם הלקוח/ה (נעול לעריכה)", value=exist_name, disabled=True
            )
            client_phone = st.text_input("מספר טלפון", value=exist_phone)

            service_idx = (
                DLL_params.services.index(exist_service)
                if exist_service in DLL_params.services
                else 0
            )
            service = st.selectbox(
                "סוג טיפול", DLL_params.services, index=service_idx
            )

            parsed_date = datetime.strptime(exist_date_str, "%Y-%m-%d").date()
            selected_date = st.date_input(
                "תאריך", value=parsed_date, min_value=date.today()
            )

            formatted_date = selected_date.strftime("%Y-%m-%d")
            available_times = appointment_manager.get_available_times_for_date(
                formatted_date
            )

            if exist_time not in available_times:
                available_times.append(exist_time)
                available_times.sort()

            time_idx = (
                available_times.index(exist_time)
                if exist_time in available_times
                else 0
            )
            selected_time = st.selectbox(
                "שעת טיפול", available_times, index=time_idx
            )

            updated = st.form_submit_button("עדכן תור")

            if updated:
                if not client_phone:
                    st.error("יש למלא מספר טלפון.")
                elif not is_future(selected_date, selected_time):
                    st.error("לא ניתן לעדכן תור לתאריך או שעה בעבר.")
                else:
                    appointment_manager.update_appointment(
                        appt_id,
                        exist_name,
                        service,
                        formatted_date,
                        selected_time,
                        client_phone,
                    )
                    trigger_reset_and_rerun("התור עודכן בהצלחה!")


# --- ביטול תור ---
elif menu == "ביטול תור":
    st.subheader("ביטול תור")

    with st.form("delete_form"):
        appt_id = st.number_input(
            "הכנס מזהה (ID) של התור לביטול", min_value=0, step=1
        )
        submitted = st.form_submit_button("בטל תור")

        if submitted:
            existing_data = appointment_manager.get_appointment_by_id(appt_id)
            if not existing_data:
                st.error("לא נמצא תור עם מזהה זה.")
            else:
                appointment_manager.delete_appointment(appt_id)
                trigger_reset_and_rerun(f"תור מספר {appt_id} בוטל בהצלחה!")


# --- צפייה בכל התורים ---
elif menu == "צפייה בכל התורים":
    st.subheader("רשימת כל התורים")
    appointments = appointment_manager.get_all_appointments()

    if not appointments:
        st.info("אין תורים קבועים כרגע.")
    else:
        table_data = [
            {
                "ID": a[0],
                "שם הלקוח": a[1],
                "טיפול": a[2],
                "תאריך": a[3],
                "שעה": a[4],
                "טלפון": a[5] if len(a) > 5 else "",
            }
            for a in appointments
        ]
        st.dataframe(table_data, use_container_width=True)


# --- צפייה בפרטי לקוחות ---
elif menu == "צפייה בפרטי לקוחות":
    st.subheader("רשימת לקוחות")
    customers = appointment_manager.get_all_customers()

    if not customers:
        st.info("אין לקוחות פעילים כרגע.")
    else:
        table_data = [
            {
                "טלפון": c[0],
                "שם": c[1],
                "סה״כ ביקורים": c[3],
                "ביקור עתידי": c[5],
            }
            for c in customers
        ]
        st.dataframe(table_data, use_container_width=True)