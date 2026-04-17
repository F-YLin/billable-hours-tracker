import streamlit as st
import math
import pandas as pd
from database import initialize_database, get_connection
from auth import register_user, login_user
from datetime import date, timedelta

initialize_database()

st.set_page_config(page_title="Billable Hours Tracker", page_icon="⚖️")

if "user" not in st.session_state:
    st.session_state.user = None

def show_login():
    st.title("⚖️ Billable Hours Tracker")
    tab1, tab2 = st.tabs(["Log In", "Register"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In"):
            success, user = login_user(email, password)
            if success:
                st.session_state.user = user
                st.experimental_rerun()
            else:
                st.error("Invalid email or password.")

    with tab2:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Register"):
            success, msg = register_user(email, password)
            if success:
                st.success(msg + " Please log in.")
            else:
                st.error(msg)

def get_clients(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE user_id = ?", (user_id,))
    clients = cursor.fetchall()
    conn.close()
    return clients

def add_client(user_id, name, email, hourly_rate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clients (user_id, name, email, hourly_rate) VALUES (?, ?, ?, ?)",
        (user_id, name, email, hourly_rate)
    )
    conn.commit()
    conn.close()

def update_client_rate(client_id, hourly_rate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE clients SET hourly_rate = ? WHERE id = ?",
        (hourly_rate, client_id)
    )
    conn.commit()
    conn.close()

def get_time_entries(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT time_entries.id, clients.name as client_name,
               time_entries.description, time_entries.hours, time_entries.date,
               time_entries.client_id
        FROM time_entries
        JOIN clients ON time_entries.client_id = clients.id
        WHERE time_entries.user_id = ?
        ORDER BY time_entries.date DESC
    """, (user_id,))
    entries = cursor.fetchall()
    conn.close()
    return entries

def add_time_entry(user_id, client_id, description, hours, entry_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO time_entries (user_id, client_id, description, hours, date) VALUES (?, ?, ?, ?, ?)",
        (user_id, client_id, description, hours, entry_date)
    )
    conn.commit()
    conn.close()

def update_time_entry(entry_id, client_id, description, hours, entry_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE time_entries SET client_id = ?, description = ?, hours = ?, date = ? WHERE id = ?",
        (client_id, description, hours, entry_date, entry_id)
    )
    conn.commit()
    conn.close()

def delete_time_entry(entry_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

def filter_by_timeframe(df, timeframe):
    today = pd.Timestamp(date.today())
    if timeframe == "Last 24 hours":
        cutoff = today - timedelta(days=1)
    elif timeframe == "Last 48 hours":
        cutoff = today - timedelta(days=2)
    elif timeframe == "Last 72 hours":
        cutoff = today - timedelta(days=3)
    elif timeframe == "Last week":
        cutoff = today - timedelta(weeks=1)
    elif timeframe == "Last 14 days":
        cutoff = today - timedelta(days=14)
    elif timeframe == "Last month":
        cutoff = today - timedelta(days=30)
    elif timeframe == "Last 6 months":
        cutoff = today - timedelta(days=182)
    elif timeframe == "Last year":
        cutoff = today - timedelta(days=365)
    else:
        return df
    return df[pd.to_datetime(df["date"]) >= cutoff]

def show_app():
    user_id = st.session_state.user["id"]

    st.sidebar.title("⚖️ Billable Hours")
    st.sidebar.write(st.session_state.user["email"])
    page = st.sidebar.radio("Navigate", ["Dashboard", "Clients", "Log Time", "Edit Entries", "Analytics"])
    if st.sidebar.button("Log Out"):
        st.session_state.user = None
        st.experimental_rerun()

    if page == "Dashboard":
        st.title("Dashboard")
        clients = get_clients(user_id)
        entries = get_time_entries(user_id)
        total_hours = sum(e["hours"] for e in entries)

        col1, col2 = st.columns(2)
        col1.metric("Total Clients", len(clients))
        col2.metric("Total Hours Logged", f"{total_hours:.1f} hrs")

        if entries:
            st.subheader("Recent Time Entries")
            for e in entries[:5]:
                st.write(f"**{e['client_name']}** — {e['description']} ({e['hours']} hrs) on {e['date']}")

    elif page == "Clients":
        st.title("Clients")

        with st.form("add_client_form"):
            st.subheader("Add a New Client")
            name = st.text_input("Client Name")
            email = st.text_input("Client Email (optional)")
            hourly_rate = st.number_input("Hourly Rate (USD)", min_value=0, value=350, step=50)
            submitted = st.form_submit_button("Add Client")
            if submitted:
                if name.strip() == "":
                    st.error("Client name cannot be empty.")
                else:
                    add_client(user_id, name.strip(), email.strip(), hourly_rate)
                    st.success(f"Client '{name}' added!")
                    st.experimental_rerun()

        st.subheader("Your Clients")
        clients = get_clients(user_id)
        if len(clients) == 0:
            st.info("No clients yet. Add one above.")
        else:
            for client in clients:
                with st.expander(f"{client['name']} — ${client['hourly_rate']}/hr"):
                    st.write(f"Email: {client['email'] or 'Not provided'}")
                    new_rate = st.number_input(
                        "Update hourly rate",
                        min_value=0,
                        value=int(client["hourly_rate"]),
                        step=50,
                        key=f"rate_{client['id']}"
                    )
                    if st.button("Save Rate", key=f"save_{client['id']}"):
                        update_client_rate(client["id"], new_rate)
                        st.success("Rate updated!")
                        st.experimental_rerun()

    elif page == "Log Time":
        st.title("Log Time")
        clients = get_clients(user_id)

        if len(clients) == 0:
            st.warning("You need to add a client first before logging time.")
        else:
            with st.form("log_time_form"):
                client_names = [c["name"] for c in clients]
                selected_client = st.selectbox("Select Client", client_names)

                common_tasks = [
                    "Select a common task or type your own below...",
                    "Drafting document",
                    "Attending client meeting",
                    "Attending court hearing",
                    "Reviewing and revising document",
                    "Legal research",
                    "Phone call with client",
                    "Preparing for trial",
                    "Filing court documents",
                    "Negotiating settlement",
                ]
                selected_task = st.selectbox("Common Tasks", common_tasks)

                if selected_task == "Select a common task or type your own below...":
                    description = st.text_input("Description of work done")
                else:
                    description = st.text_input("Description of work done", value=selected_task)

                col_h, col_m = st.columns(2)
                with col_h:
                    input_hours = st.number_input("Hours", min_value=0, max_value=24, step=1, value=0)
                with col_m:
                    input_minutes = st.number_input("Minutes", min_value=0, max_value=59, step=1, value=0)

                total_minutes = (input_hours * 60) + input_minutes
                increments = math.ceil(total_minutes / 6)
                billable_hours = round(increments * 6 / 60, 1)
                st.info(f"⏱ Billable amount: **{billable_hours} hrs** (rounded to nearest 6-min increment)")

                entry_date = st.date_input("Date", value=date.today())
                submitted = st.form_submit_button("Log Time Entry")

                if submitted:
                    if description.strip() == "":
                        st.error("Please add a description.")
                    elif total_minutes == 0:
                        st.error("Please enter a time greater than 0.")
                    else:
                        client_id = [c["id"] for c in clients if c["name"] == selected_client][0]
                        add_time_entry(user_id, client_id, description.strip(), billable_hours, str(entry_date))
                        st.success(f"Logged {billable_hours} hrs for {selected_client}!")
                        st.experimental_rerun()

            st.subheader("All Time Entries")
            entries = get_time_entries(user_id)
            if len(entries) == 0:
                st.info("No time entries yet.")
            else:
                for e in entries:
                    st.write(f"**{e['client_name']}** — {e['description']} ({e['hours']} hrs) on {e['date']}")

    elif page == "Edit Entries":
        st.title("Edit Entries")
        entries = get_time_entries(user_id)
        clients = get_clients(user_id)
        client_names = [c["name"] for c in clients]

        if len(entries) == 0:
            st.info("No time entries yet.")
        else:
            for e in entries:
                with st.expander(f"{e['date']} — {e['client_name']} — {e['description']} ({e['hours']} hrs)"):
                    with st.form(key=f"edit_form_{e['id']}"):
                        selected_client = st.selectbox(
                            "Client",
                            client_names,
                            index=client_names.index(e["client_name"]),
                            key=f"client_{e['id']}"
                        )
                        new_description = st.text_input("Description", value=e["description"], key=f"desc_{e['id']}")
                        new_hours = st.number_input("Billable Hours", min_value=0.1, value=float(e["hours"]), step=0.1, key=f"hours_{e['id']}")
                        new_date = st.date_input("Date", value=date.fromisoformat(e["date"]), key=f"date_{e['id']}")

                        col1, col2 = st.columns(2)
                        with col1:
                            save = st.form_submit_button("Save Changes")
                        with col2:
                            delete = st.form_submit_button("Delete Entry")

                        if save:
                            client_id = [c["id"] for c in clients if c["name"] == selected_client][0]
                            update_time_entry(e["id"], client_id, new_description, new_hours, str(new_date))
                            st.success("Entry updated!")
                            st.experimental_rerun()

                        if delete:
                            delete_time_entry(e["id"])
                            st.success("Entry deleted.")
                            st.experimental_rerun()

    elif page == "Analytics":
        st.title("Analytics")
        entries = get_time_entries(user_id)
        clients = get_clients(user_id)

        if len(entries) == 0:
            st.info("No time entries yet. Log some hours first.")
        else:
            df = pd.DataFrame(entries, columns=["id", "client_name", "description", "hours", "date", "client_id"])

            # Filters
            col1, col2 = st.columns(2)
            with col1:
                client_options = ["All Clients"] + [c["name"] for c in clients]
                selected_client = st.selectbox("Select Client", client_options)
            with col2:
                timeframe = st.selectbox("Time Frame", [
                    "All Time",
                    "Last 24 hours",
                    "Last 48 hours",
                    "Last 72 hours",
                    "Last week",
                    "Last 14 days",
                    "Last month",
                    "Last 6 months",
                    "Last year"
                ])

            # Apply filters
            if selected_client != "All Clients":
                df = df[df["client_name"] == selected_client]
            df = filter_by_timeframe(df, timeframe)

            if len(df) == 0:
                st.warning("No entries found for the selected filters.")
            else:
                # Bar chart
                st.subheader("Hours per Client")
                hours_by_client = df.groupby("client_name")["hours"].sum().reset_index()
                hours_by_client.columns = ["Client", "Total Hours"]
                st.bar_chart(hours_by_client.set_index("Client"))

                # Line chart
                st.subheader("Hours Logged Over Time")
                hours_by_date = df.groupby("date")["hours"].sum().reset_index()
                hours_by_date.columns = ["Date", "Hours"]
                hours_by_date = hours_by_date.sort_values("Date")
                st.line_chart(hours_by_date.set_index("Date"))

                # Billing summary
                st.subheader("Billing Summary")
                rate_map = {c["name"]: c["hourly_rate"] for c in clients}
                summary = df.groupby("client_name")["hours"].sum().reset_index()
                summary.columns = ["Client", "Total Hours"]
                summary["Hourly Rate"] = summary["Client"].apply(lambda name: f"${rate_map.get(name, 350):,.0f}")
                summary["Estimated Fee"] = summary.apply(
                    lambda row: f"${row['Total Hours'] * rate_map.get(row['Client'], 350):,.2f}", axis=1
                )
                st.dataframe(summary, use_container_width=True)

if st.session_state.user is None:
    show_login()
else:
    show_app()