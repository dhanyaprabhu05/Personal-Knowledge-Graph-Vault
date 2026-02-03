# Personal Knowledge Graph Vault

A database-driven web application that helps users organize interconnected knowledge such as concepts, notes, tasks, collaborators, and tags using a well-normalized relational database and an interactive GUI.

This project was developed as part of a **Database Management Systems (DBMS)** course and demonstrates the practical application of core DBMS concepts using **MySQL** and **Streamlit (Python)**.

---

## Project Overview

Managing ideas, notes, and related work across multiple platforms can become disorganized and inefficient.  
The **Personal Knowledge Graph Vault** addresses this problem by storing all information in a centralized, relational structure and linking related data intelligently.

The system allows users to:
- Create and manage concepts and notes
- Track tasks and deadlines
- Link related concepts to form a knowledge graph
- Manage collaborators and roles
- Automatically maintain data integrity using triggers

---

## Objectives

- Design a **normalized relational database** (3NF)
- Implement **CRUD operations** through a GUI
- Demonstrate **triggers, stored procedures, and functions**
- Use **aggregate, join, and nested SQL queries**
- Integrate a MySQL backend with a **Streamlit-based frontend**

---

## System Design and Tech Stack

- **Backend:** MySQL (Relational Database)
- **Frontend:** Streamlit (Python)
- **Architecture:** Modular and normalized
- **Key Entities:** Users, Concepts, Notes, Tasks, Tags, Collaborators, Links, Attachments
- **Database Concepts Used:**
  - ER Modeling
  - Normalization (3NF)
  - Triggers
  - Stored Procedures
  - Functions
  - Views
  - SQL Queries

---

## How to Run the Project
### Prerequisites
- Python 3.x
- MySQL Server
- Streamlit
### Steps to run
**Step 1:** Run the Database fiile in mysql. It will create a database called KnowledgeVault 

**Step 2:** Update the database connection details in app.py

**Step 3:** Run app.py 
```
streamlit run app.py
```
> Note: The files you download will get saved in the static folder 
