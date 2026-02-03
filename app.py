import streamlit as st
import mysql.connector
from datetime import date, datetime
import base64, os

def set_right_bg(image_path):
    """
    Sets a translucent wallpaper covering the entire background.
    """
    import base64
    if not os.path.exists(image_path):
        st.warning(f"Image not found at: {image_path}")
        return
    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{encoded_image}");
            background-attachment: fixed;
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
        }}
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(255, 255, 255, 0.10);
            pointer-events: none;
            z-index: 0;
        }}
        [data-testid="stAppViewContainer"] .main .block-container {{
            background: white;
            padding: 2rem;
            border-radius: 5px;
            position: relative;
            z-index: 1;
        }}
        [data-testid="stSidebar"] {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            z-index: 10;
        }}
        [data-testid="stHeader"] {{
            background: transparent !important;
            z-index: 11;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="KnowledgeVault1"
    )

# Helper Functions
def run_query(query, params=None, fetch=False):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    data = None
    if fetch:
        data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return data

# Streamlit Page Setup
st.set_page_config(page_title="Personal Knowledge Vault", layout="wide")
st.title("Personal Knowledge-Graph Vault")

if "active_page" not in st.session_state:
    st.session_state.active_page = "View Concepts"

# Sidebar menu buttons
st.sidebar.title("Menu")
if st.sidebar.button("View Concepts"):
    st.session_state.active_page = "View Concepts"
if st.sidebar.button("Add Concept"):
    st.session_state.active_page = "Add Concept"
if st.sidebar.button("Add Note"):
    st.session_state.active_page = "Add Note"
if st.sidebar.button("View Notes"):
    st.session_state.active_page = "View Notes"
if st.sidebar.button("Add Task"):
    st.session_state.active_page = "Add Task"
if st.sidebar.button("View Tasks"):
    st.session_state.active_page = "View Tasks"
if st.sidebar.button("Manage Users"):
    st.session_state.active_page = "Manage Users"

menu = st.session_state.active_page

# BACKGROUND WALLPAPER SWITCHER
if menu in ["View Concepts", "Add Concept"]:
    set_right_bg("static/books.jpg")
elif menu in ["Add Note", "View Notes"]:
    set_right_bg("static/books.jpg")
elif menu in ["Add Task", "View Tasks"]:
    set_right_bg("static/books.jpg")
else:
    set_right_bg("static/books.jpg")


# MANAGE USERS SECTION (with trigger demo)
if menu == "Manage Users":
    st.header("Manage Users")
    users = run_query("SELECT * FROM Users", fetch=True)
    for u in users:
        st.write(f"👤 {u['name']} ({u['role']})")
        if st.button(f"Delete {u['name']}", key=f"del_user_{u['user_id']}"):
            run_query("DELETE FROM Users WHERE user_id = %s", (u['user_id'],))
            st.warning(f"User {u['name']} deleted — their collaborations removed automatically.")
            st.rerun()


# ADD / VIEW CONCEPTS
if menu == "Add Concept":
    st.header("Add New Concept")
    ctype = st.text_input("Concept Type (e.g. Project, Idea, Paper)")
    title = st.text_input("Concept Title")
    categories = run_query("SELECT category_id, name FROM Categories", fetch=True)
    category_map = {c['name']: c['category_id'] for c in categories} if categories else {}
    if category_map:
        category_name = st.selectbox("Select Category", list(category_map.keys()))
        category_id = category_map[category_name]
    else:
        st.warning("No categories found! Please add a category first.")
        category_id = None
    if st.button("Add Concept"):
        if ctype and title:
            query = "INSERT INTO Concepts (type, title, created_on, category_id) VALUES (%s, %s, CURDATE(), %s)"
            run_query(query, (ctype, title, category_id))
            st.success("Concept added successfully!")
        else:
            st.error("Please fill all required fields.")

elif menu == "View Concepts":
    st.header("All Concepts")
    data = run_query("SELECT * FROM Concepts", fetch=True)
    if data:
        for d in data:
            st.subheader(f"{d['title']} ({d['type']})")
            st.write(f"Created on: {d['created_on']}")
            if st.button(f"Delete Concept {d['entity_id']}", key=f"del_{d['entity_id']}"):
                run_query("DELETE FROM Concepts WHERE entity_id = %s", (d['entity_id'],))
                st.warning(f"Concept '{d['title']}' deleted along with its notes, tasks, and attachments!")
                st.rerun()
            st.markdown("---")
    else:
        st.warning("No concepts found.")


# ADD / VIEW NOTES
elif menu == "Add Note":
    st.header("Add a Note")
    concept_id = st.number_input("Concept ID", min_value=1, step=1)
    body = st.text_area("Note Content")
    if st.button("Add Note"):
        if concept_id and body:
            query = "INSERT INTO Notes (entity_id, body, created_on) VALUES (%s, %s, CURDATE())"
            run_query(query, (concept_id, body))
            st.success("Note added successfully!")
        else:
            st.error("Please fill all fields.")

elif menu == "View Notes":
    st.header("All Notes")
    notes = run_query("SELECT * FROM Notes", fetch=True)
    if notes:
        for n in notes:
            st.subheader(f"Note ID: {n['note_id']}")
            st.write(f"Concept ID: {n['entity_id']}")
            st.write(n["body"])
            st.write(f"Created on: {n['created_on']}")
            st.markdown("---")
    else:
        st.warning("No notes found.")

# ADD / VIEW TASKS
elif menu == "Add Task":
    st.header("Add Task")
    concept_id = st.number_input("Concept ID", min_value=1, step=1)
    desc = st.text_input("Task Description")
    due_on = st.date_input("Due Date")
    remind_on = st.date_input("Reminder Date (optional)", value=date.today())
    if st.button("Add Task"):
        if concept_id and desc:
            query = "INSERT INTO Tasks (entity_id, description, due_on, status, remind_on) VALUES (%s, %s, %s, %s, %s)"
            run_query(query, (concept_id, desc, due_on, "Pending", remind_on))
            st.success("Task added successfully!")
        else:
            st.error("Please fill all fields.")

elif menu == "View Tasks":
    st.header("All Tasks")
    tasks = run_query("SELECT * FROM Tasks", fetch=True)
    if tasks:
        for t in tasks:
            st.subheader(f"{t['description']}")
            st.write(f"Concept ID: {t['entity_id']}")
            st.write(f"Due: {t['due_on']} | Status: {t['status']}")
            st.write(f"Reminder: {t['remind_on']}")
            new_status = st.selectbox(
                f"Update status for Task ID {t['task_id']}",
                ["Pending", "In Progress", "Completed"],
                index=["Pending", "In Progress", "Completed"].index(t['status']),
                key=f"status_{t['task_id']}"
            )
            if st.button(f"Save Task {t['task_id']}", key=f"save_{t['task_id']}"):
                run_query("UPDATE Tasks SET status = %s WHERE task_id = %s", (new_status, t['task_id']))
                st.success(f"Task {t['task_id']} updated to {new_status}")
                st.rerun()
            st.markdown("---")
    else:
        st.warning("No tasks found.")


# STORED PROCEDURES / FUNCTIONS / VIEWS (ONLY EXISTING ONES)
st.header("Database Procedures & Views")

proc_choice = st.selectbox(
    "Choose an operation",
    ["Select one", "GetConceptDetails", "GetLinkedConcepts", "MarkTaskCompleted", "DaysRemaining", "View: Concept_Summary"]
)

#  GetConceptDetails 
if proc_choice == "GetConceptDetails":
    concept_id = st.number_input("Enter Concept ID", min_value=1, step=1)
    if st.button("Run GetConceptDetails"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("GetConceptDetails", [concept_id])
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    st.dataframe(rows)
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Error: {e}")

# GetLinkedConcepts 
elif proc_choice == "GetLinkedConcepts":
    concept_id = st.number_input("Enter Concept ID", min_value=1, step=1, key="link_proc")
    if st.button("Run GetLinkedConcepts"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.callproc("GetLinkedConcepts", [concept_id])
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    st.dataframe(rows)
                else:
                    st.info("No linked concepts found.")
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Error: {e}")

#  MarkTaskCompleted
elif proc_choice == "MarkTaskCompleted":
    task_id = st.number_input("Enter Task ID", min_value=1, step=1, key="task_proc")
    if st.button("Run MarkTaskCompleted"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.callproc("MarkTaskCompleted", [task_id])
            conn.commit()
            st.success(f"Task {task_id} marked as Completed (trigger auto-creates a note).")
            cursor.close()
            conn.close()
        except Exception as e:
            st.error(f"Error: {e}")

# DaysRemaining (function)
elif proc_choice == "DaysRemaining":
    task_id = st.number_input("Enter Task ID", min_value=1, step=1, key="days_func")
    if st.button("Run DaysRemaining Function"):
        try:
            query = "SELECT DaysRemaining(%s) AS days_left"
            data = run_query(query, (task_id,), fetch=True)
            if data:
                st.info(f"Days Remaining for Task {task_id}: {data[0]['days_left']}")
            else:
                st.warning("No result returned.")
        except Exception as e:
            st.error(f"Error: {e}")

#  View: Concept_Summary 
elif proc_choice == "View: Concept_Summary":
    if st.button("Show Concept Summary"):
        try:
            data = run_query("SELECT * FROM Concept_Summary", fetch=True)
            st.dataframe(data)
        except Exception as e:
            st.error(f"Error: {e}")

# LINKING CONCEPTS SECTION
st.subheader("Link Concepts")
concepts = run_query("SELECT entity_id, title FROM Concepts", fetch=True)
if concepts:
    concept_options = {c['title']: c['entity_id'] for c in concepts}
    col1, col2 = st.columns(2)
    with col1:
        src = st.selectbox("Source Concept", list(concept_options.keys()))
    with col2:
        dst = st.selectbox("Destination Concept", list(concept_options.keys()))
    relation_type = st.text_input("Relation Type (e.g., builds on, related to)")
    if st.button("Create Link"):
        if src == dst:
            st.warning("You can’t link a concept to itself.")
        else:
            run_query(
                "INSERT INTO Links (src_concept_id, dst_concept_id, relation_type) VALUES (%s, %s, %s)",
                (concept_options[src], concept_options[dst], relation_type),
                fetch=False
            )
            st.success(f"Linked '{src}' → '{dst}' as '{relation_type}'")
    st.write("### Existing Links")
    links = run_query("""
        SELECT l.link_id, c1.title AS source, c2.title AS destination, l.relation_type
        FROM Links l
        JOIN Concepts c1 ON l.src_concept_id = c1.entity_id
        JOIN Concepts c2 ON l.dst_concept_id = c2.entity_id
    """, fetch=True)
    st.dataframe(links)
else:
    st.info("Add some concepts first before creating links.")

# COLLABORATORS SECTION
st.subheader("Manage Collaborators")
users = run_query("SELECT user_id, name FROM Users", fetch=True)
concepts = run_query("SELECT entity_id, title FROM Concepts", fetch=True)
if users and concepts:
    user_options = {u['name']: u['user_id'] for u in users}
    concept_options = {c['title']: c['entity_id'] for c in concepts}
    col1, col2 = st.columns(2)
    with col1:
        user = st.selectbox("Select User", list(user_options.keys()))
    with col2:
        concept = st.selectbox("Assign to Concept", list(concept_options.keys()))
    role = st.selectbox("Role", ["Contributor", "Editor", "Viewer"])
    if st.button("Add Collaborator"):
        run_query(
            "INSERT INTO Collaborators (user_id, concept_id, role) VALUES (%s, %s, %s)",
            (user_options[user], concept_options[concept], role),
            fetch=False
        )
        st.success(f"Added {user} as {role} to {concept}")
    st.write("### Current Collaborations")
    collabs = run_query("""
        SELECT u.name AS user, c.title AS concept, co.role
        FROM Collaborators co
        JOIN Users u ON co.user_id = u.user_id
        JOIN Concepts c ON co.concept_id = c.entity_id
    """, fetch=True)
    st.dataframe(collabs)
else:
    st.info("Add users and concepts first.")

# TAGGING SYSTEM
st.subheader("🏷 Add Tags to Concepts")
tags = run_query("SELECT tag_id, tag FROM Tags", fetch=True)
concepts = run_query("SELECT entity_id, title FROM Concepts", fetch=True)
if tags and concepts:
    tag_options = {t['tag']: t['tag_id'] for t in tags}
    concept_options = {c['title']: c['entity_id'] for c in concepts}
    col1, col2 = st.columns(2)
    with col1:
        tag = st.selectbox("Select Tag", list(tag_options.keys()))
    with col2:
        concept = st.selectbox("Select Concept", list(concept_options.keys()))
    if st.button("Assign Tag"):
        run_query(
            "INSERT INTO Concept_Tags (entity_id, tag_id) VALUES (%s, %s)",
            (concept_options[concept], tag_options[tag]),
            fetch=False
        )
        st.success(f"Added tag '{tag}' to concept '{concept}'")
    st.write("### Tagged Concepts")
    tagged = run_query("""
        SELECT c.title AS concept, t.tag
        FROM Concept_Tags ct
        JOIN Concepts c ON ct.entity_id = c.entity_id
        JOIN Tags t ON ct.tag_id = t.tag_id
    """, fetch=True)
    st.dataframe(tagged)
else:
    st.info("Add tags and concepts first.")

# ATTACHMENTS SECTION
st.subheader("Attachments")
concepts = run_query("SELECT entity_id, title FROM Concepts", fetch=True)

if concepts:
    concept_options = {c['title']: c['entity_id'] for c in concepts}
    concept_name = st.selectbox("Select Concept", list(concept_options.keys()), key="attachment_concept")
    uploaded_file = st.file_uploader("Upload a file (PDF, Image, etc.)", key="attachment_upload")
    if uploaded_file and st.button("Upload Attachment", key="upload_btn"):
        file_path = f"static/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        run_query(
            "INSERT INTO Attachments (entity_id, file_path, file_type) VALUES (%s, %s, %s)",
            (concept_options[concept_name], file_path, uploaded_file.type)
        )
        st.success(f"File '{uploaded_file.name}' uploaded for concept '{concept_name}'")
    st.write("### Existing Attachments")
    files = run_query("""
        SELECT a.attachment_id, c.title AS concept, a.file_path, a.file_type
        FROM Attachments a
        JOIN Concepts c ON a.entity_id = c.entity_id
    """, fetch=True)
    deleted_any = False
    for f in files:
        if not os.path.exists(f['file_path']):
            st.warning(f"Removed missing file record: {f['file_path']}")
            run_query("DELETE FROM Attachments WHERE attachment_id = %s", (f['attachment_id'],))
            deleted_any = True
    if deleted_any:
        st.rerun()  # only rerun if something was actually deleted
    if files:
        for f in files:
            file_path = f['file_path']
            concept = f['concept']
            file_type = f['file_type']
            attachment_id = f['attachment_id']

            col1, col2 = st.columns([3, 1])  # side-by-side layout
            with col1:
                try:
                    with open(file_path, "rb") as file:
                        st.download_button(
                            label=f"Download {os.path.basename(file_path)} for {concept}",
                            data=file,
                            file_name=os.path.basename(file_path),
                            mime=file_type,
                            key=f"download_{attachment_id}"
                        )
                except FileNotFoundError:
                    st.error(f"File not found: {file_path}")

            with col2:
                # Delete button
                if st.button(" Delete", key=f"delete_{attachment_id}"):
                    try:
                        if os.path.exists(file_path):
                            os.remove(file_path)  # remove the actual file
                        run_query("DELETE FROM Attachments WHERE attachment_id = %s", (attachment_id,))
                        st.success(f"Deleted '{os.path.basename(file_path)}'")
                        st.rerun()  # refresh after delete
                    except Exception as e:
                        st.error(f"Error deleting file: {e}")
    else:
        st.info("No attachments found.")
else:
    st.info("Add some concepts first.")

# ANALYTICS & REPORTS
st.subheader("Analytics Dashboard")
col1, col2 = st.columns(2)
with col1:
    st.write("### Number of Notes per Concept")
    data = run_query("""
        SELECT c.title, COUNT(n.note_id) AS note_count
        FROM Concepts c
        LEFT JOIN Notes n ON c.entity_id = n.entity_id
        GROUP BY c.title;
    """, fetch=True)
    st.dataframe(data)
with col2:
    st.write("### Pending Tasks by Concept")
    tasks = run_query("""
        SELECT c.title, COUNT(t.task_id) AS pending_tasks
        FROM Concepts c
        LEFT JOIN Tasks t ON c.entity_id = t.entity_id
        WHERE t.status = 'Pending'
        GROUP BY c.title;
    """, fetch=True)
    st.dataframe(tasks)

st.markdown("---")
st.header("Queries Showcase")

# Aggregate Query
st.subheader("Aggregate Query: Average Tasks per Concept")
avg_data = run_query("""
    SELECT c.title, AVG(t.task_id IS NOT NULL) AS avg_tasks
    FROM Concepts c
    LEFT JOIN Tasks t ON c.entity_id = t.entity_id
    GROUP BY c.title;
""", fetch=True)
st.dataframe(avg_data)

# Nested Query
st.subheader("Nested Query: Concepts with More Than 1 Note")
nested = run_query("""
    SELECT title FROM Concepts
    WHERE entity_id IN (
        SELECT entity_id FROM Notes GROUP BY entity_id HAVING COUNT(note_id) > 1
    );
""", fetch=True)
st.dataframe(nested)

# Join Query
st.subheader("Join Query: Tasks with Concept and User Info")
joined = run_query("""
    SELECT t.description, t.status, c.title AS concept, u.name AS owner
    FROM Tasks t
    JOIN Concepts c ON t.entity_id = c.entity_id
    JOIN Users u ON c.user_id = u.user_id;
""", fetch=True)
st.dataframe(joined)
