import streamlit as st
import sqlite3
import hashlib
import json
from datetime import datetime

# Database setup
def init_db():
    conn = sqlite3.connect('roadmap.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, 
                  password TEXT, 
                  progress TEXT,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Authentication functions
def make_hashes(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    conn = sqlite3.connect('roadmap.db')
    c = conn.cursor()
    c.execute('INSERT INTO users VALUES (?,?,?,?)',
              (email, make_hashes(password), json.dumps({}), datetime.now()))
    conn.commit()
    conn.close()

def login_user(email, password):
    conn = sqlite3.connect('roadmap.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ? AND password = ?',
              (email, make_hashes(password)))
    data = c.fetchone()
    conn.close()
    return data

# Progress management
def save_progress(email, progress):
    conn = sqlite3.connect('roadmap.db')
    c = conn.cursor()
    c.execute('UPDATE users SET progress = ? WHERE email = ?',
              (json.dumps(progress), email))
    conn.commit()
    conn.close()

def load_progress(email):
    conn = sqlite3.connect('roadmap.db')
    c = conn.cursor()
    c.execute('SELECT progress FROM users WHERE email = ?', (email,))
    data = c.fetchone()
    conn.close()
    return json.loads(data[0]) if data else {}

# Progress calculation
def calculate_progress(roadmap, progress):
    metrics = {
        "total": {"hours": 0, "completed": 0},
        "stages": {}
    }
    
    for stage, data in roadmap.items():
        stage_hours = sum(t["time"] for t in data["topics"])
        completed_hours = sum(t["time"] for t in data["topics"] 
                              if t["name"] in progress.get(stage, []))
        
        metrics["stages"][stage] = {
            "total": stage_hours,
            "completed": completed_hours,
            "percent": (completed_hours / stage_hours * 100) if stage_hours > 0 else 0
        }
        
        metrics["total"]["hours"] += stage_hours
        metrics["total"]["completed"] += completed_hours
    
    metrics["total"]["percent"] = (metrics["total"]["completed"] / metrics["total"]["hours"] * 100 
                                   if metrics["total"]["hours"] > 0 else 0)
    metrics["total"]["remaining"] = metrics["total"]["hours"] - metrics["total"]["completed"]
    
    return metrics

# Roadmap data structure
ROADMAP = {
    # Stage 1: Python for Data Science
    "Stage 1: Python for Data Science": {
        "topics": [
            {"name": "Python Basics (variables, data types, loops, conditionals)", "time": 15},
            {"name": "Functions & Modules", "time": 10},
            {"name": "Data Structures: Lists, Tuples, Sets, Dictionaries", "time": 15},
            {"name": "File Handling (open/read/write)", "time": 8},
            {"name": "Error Handling (try-except)", "time": 6},
            {"name": "Object-Oriented Programming (OOP)", "time": 20},
            {"name": "Working with Libraries (math, os, datetime)", "time": 12},
            {"name": "Lambda, List Comprehensions", "time": 10},
            {"name": "Basic Unit Testing with assert or pytest", "time": 14},
            {"name": "Decorators and Generators", "time": 10}
        ],
        "resources": {
            "books": [
                "Python for Data Analysis - Wes McKinney",
                "Fluent Python - Luciano Ramalho",
                "Effective Python - Brett Slatkin"
            ],
            "documentation": [
                "https://docs.python.org/3/",
                "https://pandas.pydata.org/docs/",
                "https://numpy.org/doc/stable/"
            ],
            "youtube": [
                "https://youtu.be/_uQrJ0TkZlc (Python Full Course)",
                "https://youtu.be/rfscVS0vtbw (Learn Python)",
                "https://youtu.be/Z1Yd7upQsXY (Python OOP)"
            ],
            "practice_sites": [
                "https://exercism.org/tracks/python",
                "https://www.codewars.com/kata/search/python",
                "https://leetcode.com/problemset/all/?topicSlugs=python"
            ],
            "research_papers": [
                "https://doi.org/10.5555/1953048.2078195 (Scikit-learn Paper)",
                "https://doi.org/10.25080/Majora-92bf1922-011 (Pandas Whitepaper)",
                "https://peps.python.org/pep-0020/ (Zen of Python)"
            ],
            "time": "80-120 hours",
            "difficulty": "4/10 → 6/10"
        }
    },

    # Stage 2: SQL for Data Science
    "Stage 2: SQL for Data Science": {
        "topics": [
            {"name": "SELECT, WHERE, ORDER BY", "time": 10},
            {"name": "JOINs (INNER, LEFT, RIGHT)", "time": 12},
            {"name": "GROUP BY, Aggregation", "time": 8},
            {"name": "Subqueries & Nested SELECT", "time": 10},
            {"name": "Window Functions", "time": 12},
            {"name": "CTEs (WITH clause)", "time": 8},
            {"name": "Date/time functions", "time": 6},
            {"name": "CASE Statements", "time": 6}
        ],
        "resources": {
            "books": [
                "SQL Cookbook - Anthony Molinaro",
                "Learning SQL - Alan Beaulieu",
                "SQL Performance Explained - Markus Winand"
            ],
            "documentation": [
                "https://www.postgresql.org/docs/current/",
                "https://docs.snowflake.com/",
                "https://duckdb.org/docs/"
            ],
            "youtube": [
                "https://youtu.be/p3qvj9hO_Bo (SQL Basics)",
                "https://youtu.be/7S_tz1z_5bA (Advanced SQL)",
                "https://youtu.be/HXV3zeQKqGY (SQL Full Course)"
            ],
            "practice_sites": [
                "https://datalemur.com/sql-interview-questions",
                "https://www.stratascratch.com/sql-questions",
                "https://www.hackerrank.com/domains/sql"
            ],
            "research_papers": [
                "https://doi.org/10.1145/362384.362685 (Relational Model)",
                "https://doi.org/10.1145/2723372.2742797 (Spark SQL)",
                "https://doi.org/10.48550/arXiv.2304.06178 (DuckDB)"
            ],
            "time": "40-60 hours",
            "difficulty": "5/10 → 8/10"
        }
    },

    # Stage 3: Exploratory Data Analysis (EDA)
    "Stage 3: Exploratory Data Analysis (EDA)": {
        "topics": [
            {"name": "Pandas: loading, indexing, filtering, sorting", "time": 10},
            {"name": "Handling missing values", "time": 8},
            {"name": "Duplicates, renaming, reindexing", "time": 6},
            {"name": "String operations, datetime operations", "time": 10},
            {"name": "Data profiling (ydata-profiling)", "time": 8},
            {"name": "Outlier detection (IQR, Z-score)", "time": 10},
            {"name": "Descriptive statistics", "time": 8}
        ],
        "resources": {
            "books": [
                "Python Data Science Handbook - Jake VanderPlas",
                "Storytelling with Data - Cole Nussbaumer Knaflic",
                "Pandas in Action - Boris Paskhaver"
            ],
            "documentation": [
                "https://pandas.pydata.org/docs/",
                "https://seaborn.pydata.org/",
                "https://ydata-profiling.ydata.ai/"
            ],
            "youtube": [
                "https://youtu.be/0hs6_K1Ni4s (Pandas EDA)",
                "https://youtu.be/ZyhVh-qRZPA (EDA Techniques)",
                "https://youtu.be/xi0vhXFPegw (Advanced EDA)"
            ],
            "practice_sites": [
                "https://www.kaggle.com/learn/data-visualization",
                "https://app.datacamp.com/learn/courses/foundations-of-exploratory-data-analysis-with-python",
                "https://www.kaggle.com/datasets?search=EDA"
            ],
            "research_papers": [
                "https://doi.org/10.1109/TVCG.2006.143 (Visualization Layers)",
                "https://doi.org/10.1007/978-3-540-73545-8_6 (Outlier Detection)",
                "https://doi.org/10.48550/arXiv.2301.02028 (AutoEDA)"
            ],
            "time": "60-80 hours",
            "difficulty": "6/10"
        }
    },

    # Stage 4: Data Wrangling & Manipulation
    "Stage 4: Data Wrangling & Manipulation": {
        "topics": [
            {"name": "Merging, joining, concatenation", "time": 10},
            {"name": "Melting, pivoting, reshaping", "time": 8},
            {"name": "Mapping & replacing values", "time": 6},
            {"name": "Datetime parsing/manipulation", "time": 10},
            {"name": "Memory optimization techniques", "time": 8}
        ],
        "resources": {
            "books": [
                "Data Wrangling with Python - Jacqueline Kazil",
                "Python Data Cleaning Cookbook - Michael Walker",
                "Fluent Python - Luciano Ramalho"
            ],
            "documentation": [
                "https://pandas.pydata.org/docs/user_guide/merging.html",
                "https://arrow.apache.org/docs/python/",
                "https://pola-rs.github.io/polars/py-polars/html/"
            ],
            "youtube": [
                "https://youtu.be/KdmPqFGJRL0 (Data Cleaning)",
                "https://youtu.be/0uBirYFhizE (Pandas Transformations)",
                "https://youtu.be/5rNu16O3YNE (Memory Optimization)"
            ],
            "practice_sites": [
                "https://www.codewars.com/kata/search/python?q=data+manipulation",
                "https://www.kaggle.com/learn/data-cleaning",
                "https://www.hackerrank.com/domains/data-processing"
            ],
            "research_papers": [
                "https://doi.org/10.18637/jss.v059.i10 (Tidy Data)",
                "https://doi.org/10.1145/2882903.2903721 (Apache Arrow)",
                "https://doi.org/10.48550/arXiv.2209.15089 (Polars)"
            ],
            "time": "70-90 hours",
            "difficulty": "7/10"
        }
    },

    # Stage 5: Data Visualization
    "Stage 5: Data Visualization": {
        "topics": [
            {"name": "Matplotlib & Seaborn Fundamentals", "time": 10},
            {"name": "Plotly/Altair Interactive Charts", "time": 12},
            {"name": "Tableau/Power BI Dashboards", "time": 15},
            {"name": "Visual Storytelling Techniques", "time": 8},
            {"name": "Color Theory & Layout Design", "time": 6}
        ],
        "resources": {
            "books": [
                "Interactive Data Visualization with Python - Abigail Mosca",
                "Storytelling with Data - Cole Nussbaumer Knaflic",
                "The Visual Display... - Edward Tufte"
            ],
            "documentation": [
                "https://matplotlib.org/stable/",
                "https://plotly.com/python-api-reference/",
                "https://altair-viz.github.io/"
            ],
            "youtube": [
                "https://youtu.be/DAQNHzOcO5A (Matplotlib)",
                "https://youtu.be/6GUZXDef2U0 (Plotly Dash)",
                "https://youtu.be/pJ1kpd_0G7I (Seaborn)"
            ],
            "practice_sites": [
                "https://www.codewars.com/kata/search/python?q=data+visualization",
                "https://app.datacamp.com/learn/courses/introduction-to-data-visualization-with-python",
                "https://www.kaggle.com/learn/data-visualization"
            ],
            "research_papers": [
                "https://doi.org/10.1002/wics.147 (Grammar of Graphics)",
                "https://doi.org/10.1109/TVCG.2011.185 (D3.js)",
                "https://doi.org/10.1145/3411764.3445605 (AI Visualization)"
            ],
            "time": "50-70 hours",
            "difficulty": "6/10 → 9/10"
        }
    },

    # Stage 6: Statistics & Probability
    "Stage 6: Statistics & Probability": {
        "topics": [
            {"name": "Sampling & Distributions", "time": 10},
            {"name": "Hypothesis Testing", "time": 12},
            {"name": "Confidence Intervals", "time": 8},
            {"name": "Regression Analysis", "time": 10},
            {"name": "Bayesian Methods", "time": 12},
            {"name": "Causal Inference", "time": 8}
        ],
        "resources": {
            "books": [
                "Practical Statistics... - Peter Bruce",
                "Statistical Rethinking - Richard McElreath",
                "Introduction to... Learning - James et al."
            ],
            "documentation": [
                "https://docs.scipy.org/doc/scipy/reference/stats.html",
                "https://www.statsmodels.org/stable/index.html",
                "https://pymc.io/"
            ],
            "youtube": [
                "https://youtu.be/xxpc-HPKN28 (StatQuest)",
                "https://youtu.be/9FtHB7V14Fo (Khan Academy)",
                "https://youtu.be/zRUliXuwJCQ (Stanford)"
            ],
            "practice_sites": [
                "https://brilliant.org/courses/probability-fundamentals/",
                "https://leetcode.com/problemset/all/?topicSlugs=math-statistics",
                "https://www.kaggle.com/learn/statistical-experimental-design"
            ],
            "research_papers": [
                "https://doi.org/10.2307/2333958 (Fisher's Exact Test)",
                "https://doi.org/10.1214/aos/1176347963 (Bayesian Data Analysis)",
                "https://doi.org/10.1162/0899766053729669 (Causal Inference)"
            ],
            "time": "90-120 hours",
            "difficulty": "8/10"
        }
    },

    # Stage 7: Feature Engineering
    "Stage 7: Feature Engineering": {
        "topics": [
            {"name": "Categorical Encoding Techniques", "time": 10},
            {"name": "Feature Scaling Methods", "time": 8},
            {"name": "Polynomial Feature Creation", "time": 6},
            {"name": "Text Feature Extraction", "time": 10},
            {"name": "Automated Feature Selection", "time": 8}
        ],
        "resources": {
            "books": [
                "Feature Engineering... - Max Kuhn",
                "Designing ML Systems - Chip Huyen",
                "Applied Predictive Modeling - Kuhn"
            ],
            "documentation": [
                "https://scikit-learn.org/stable/modules/preprocessing.html",
                "https://feature-engine.readthedocs.io/",
                "https://featuretools.alteryx.com/"
            ],
            "youtube": [
                "https://youtu.be/ZiKMIuYidY0 (Abhishek Thakur)",
                "https://youtu.be/0HOqOcln3Z4 (Kaggle)",
                "https://youtu.be/5QDJL2KX7EQ (Data School)"
            ],
            "practice_sites": [
                "https://www.kaggle.com/learn/feature-engineering",
                "https://www.hackerearth.com/practice/machine-learning/feature-engineering/problems/",
                "https://www.openml.org/search?type=data"
            ],
            "research_papers": [
                "https://doi.org/10.1145/2783258.2788615 (Feature Tools)",
                "https://doi.org/10.1109/DSAA.2015.7344872 (Deep Feature Synthesis)",
                "https://doi.org/10.1145/3371158.3371164 (Neural Feature Selection)"
            ],
            "time": "80-100 hours",
            "difficulty": "8/10"
        }
    },

    # Stage 8: ETL (Extract, Transform, Load)
    "Stage 8: ETL (Extract, Transform, Load)": {
        "topics": [
            {"name": "File Format Handling (CSV/JSON/Excel)", "time": 10},
            {"name": "Database Ingestion", "time": 12},
            {"name": "Workflow Automation", "time": 8},
            {"name": "CLI Application Development", "time": 10},
            {"name": "Data Pipeline Orchestration", "time": 12}
        ],
        "resources": {
            "books": [
                "Data Pipelines... - Bas Harenslak",
                "Python for DevOps - Noah Gift",
                "Effective Python - Brett Slatkin"
            ],
            "documentation": [
                "https://airflow.apache.org/docs/",
                "https://docs.prefect.io/",
                "https://docs.sqlalchemy.org/"
            ],
            "youtube": [
                "https://youtu.be/ahSvcpg_PBM (Airflow)",
                "https://youtu.be/LTDAja0q_bo (ETL Python)",
                "https://youtu.be/8Xri8B9tn_s (PyData)"
            ],
            "practice_sites": [
                "https://www.hackerrank.com/domains/data-processing",
                "https://www.kaggle.com/learn/data-pipelines",
                "https://www.codewars.com/kata/search/sql?q=ETL"
            ],
            "research_papers": [
                "https://doi.org/10.1145/3299869.3314041 (Apache Airflow)",
                "https://doi.org/10.14778/3157794.3157797 (Data Pipelines)",
                "https://doi.org/10.1145/3448016.3452830 (ETL Optimization)"
            ],
            "time": "70-90 hours",
            "difficulty": "7/10"
        }
    },

    # Stage 9: Machine Learning (Core)
    "Stage 9: Machine Learning (Core)": {
        "topics": [
            {"name": "Supervised Learning Algorithms", "time": 15},
            {"name": "Model Evaluation Metrics", "time": 10},
            {"name": "Cross-Validation Strategies", "time": 8},
            {"name": "Hyperparameter Tuning", "time": 10},
            {"name": "ML Pipeline Design", "time": 12}
        ],
        "resources": {
            "books": [
                "Hands-On ML... - Aurélien Géron",
                "Pattern Recognition... - Bishop",
                "Machine Learning... - Andrew Ng"
            ],
            "documentation": [
                "https://scikit-learn.org/stable/",
                "https://www.tensorflow.org/",
                "https://xgboost.readthedocs.io/"
            ],
            "youtube": [
                "https://youtu.be/pqNCD_5r0IU (Scikit-learn)",
                "https://youtu.be/aircAruvnKk (Neural Nets)",
                "https://youtu.be/nKW8Ndu7Mjw (Google ML)"
            ],
            "practice_sites": [
                "https://www.kaggle.com/learn/machine-learning",
                "https://www.openml.org/search?type=task&sort=runs",
                "https://www.hackerearth.com/practice/machine-learning/"
            ],
            "research_papers": [
                "https://doi.org/10.1038/nature14539 (Deep Learning)",
                "https://doi.org/10.1145/2783258.2788613 (ML Pipelines)",
                "https://doi.org/10.1109/TPAMI.2016.2572683 (Supervised Learning)"
            ],
            "time": "120-150 hours",
            "difficulty": "9/10"
        }
    },

    # Stage 10: Communication & Git
    "Stage 10: Communication & Git": {
        "topics": [
            {"name": "Git Version Control", "time": 8},
            {"name": "Technical Documentation", "time": 6},
            {"name": "Data Storytelling", "time": 10},
            {"name": "Notebook Versioning", "time": 6}
        ],
        "resources": {
            "books": [
                "Data Science... - Provost & Fawcett",
                "The Pragmatic Programmer - Hunt",
                "Effective Python - Slatkin"
            ],
            "documentation": [
                "https://git-scm.com/doc",
                "https://dvc.org/doc",
                "https://www.markdownguide.org/"
            ],
            "youtube": [
                "https://youtu.be/USjZcfj8yxE (Git for DS)",
                "https://youtu.be/RGOj5yH7evk (Git Tutorial)",
                "https://youtu.be/pJ1kpd_0G7I (Storytelling)"
            ],
            "practice_sites": [
                "https://lab.github.com/",
                "https://app.datacamp.com/learn/courses/reporting-in-sql",
                "https://www.kaggle.com/learn/data-visualization"
            ],
            "research_papers": [
                "https://doi.org/10.1145/3377811.3381725 (Version Control Systems)",
                "https://doi.org/10.1145/319583.319594 (Collaborative Software Development)",
                "https://doi.org/10.1109/TVCG.2019.2934267 (Data Storytelling)"
            ],
            "time": "30-50 hours",
            "difficulty": "5/10"
        }
    }
}
    # Add other stages here...


# UI Components
def progress_sidebar(metrics):
    with st.sidebar:
        st.header("Overall Progress")
        st.metric("Total Hours", f"{metrics['total']['hours']}h")
        st.metric("Completed", f"{metrics['total']['completed']}h")
        st.metric("Remaining", f"{metrics['total']['remaining']}h")
        st.progress(metrics["total"]["percent"]/100)
        
        st.header("Quick Navigation")
        for stage in ROADMAP.keys():
            st.button(f"{stage} ({metrics['stages'][stage]['percent']:.1f}%)")

def stage_section(stage, data, progress, metrics):
    with st.expander(f"{stage} - {metrics['stages'][stage]['percent']:.1f}% Complete"):
        # Progress bar
        st.progress(metrics['stages'][stage]['percent'] / 100)
        
        # Metrics columns
        cols = st.columns(3)
        cols[0].metric("Total Hours", f"{metrics['stages'][stage]['total']}h")
        cols[1].metric("Completed", f"{metrics['stages'][stage]['completed']}h")
        cols[2].metric("Remaining", 
                      f"{metrics['stages'][stage]['total'] - metrics['stages'][stage]['completed']}h")
        
        # Checklist for topics
        stage_progress = progress.get(stage, [])
        for topic in data["topics"]:
            cols = st.columns([1, 4])
            checked = cols[0].checkbox(
                " ", 
                value=topic["name"] in stage_progress,
                key=f"{stage}_{topic['name']}"
            )
            cols[1].markdown(f"**{topic['name']}** ({topic['time']}h)")
            
            # Update progress based on checkbox state
            if checked and topic["name"] not in stage_progress:
                stage_progress.append(topic["name"])
            elif not checked and topic["name"] in stage_progress:
                stage_progress.remove(topic["name"])
            st.session_state.progress[stage] = stage_progress
            save_progress(st.session_state.user, st.session_state.progress)
        
        # Resources
        st.subheader("Learning Resources")
        tabs = st.tabs(["Books", "Documentation", "Videos", "Practice", "Research"])
        with tabs[0]:
            st.markdown("\n".join([f"- {book}" for book in data["resources"]["books"]]))
        with tabs[1]:
            st.markdown("\n".join([f"- [{link.split(' ')[0]}]({link})" for link in data["resources"]["documentation"]]))
        with tabs[2]:
            for video in data["resources"]["youtube"]:
                st.video(video.split(" ")[0])
        with tabs[3]:
            st.markdown("\n".join([f"- [{site}]({site})" for site in data["resources"]["practice_sites"]]))
        with tabs[4]:
            st.markdown("\n".join([f"- {paper}" for paper in data["resources"].get("research_papers", [])]))

def edit_roadmap():
    st.title("Edit Data Science Roadmap ✏️")
    
    # Select stage to edit
    stage = st.selectbox("Select Stage to Edit", list(ROADMAP.keys()))
    if stage:
        data = ROADMAP[stage]
        
        # Edit topics
        st.subheader("Edit Topics")
        for i, topic in enumerate(data["topics"]):
            with st.expander(f"Topic {i+1}: {topic['name']}"):
                new_name = st.text_input(f"Edit Name for Topic {i+1}", topic["name"], key=f"{stage}_topic_{i}_name")
                new_time = st.number_input(f"Edit Time (hours) for Topic {i+1}", value=topic["time"], key=f"{stage}_topic_{i}_time")
                if st.button(f"Save Changes to Topic {i+1}", key=f"{stage}_topic_{i}_save"):
                    if new_name.strip():
                        topic["name"] = new_name
                        topic["time"] = new_time
                        st.success(f"Updated Topic {i+1}")
                    else:
                        st.error("Topic name cannot be empty")
        
        # Add a new topic
        st.subheader("Add New Topic")
        new_topic_name = st.text_input("New Topic Name", key=f"{stage}_new_topic_name")
        new_topic_time = st.number_input("New Topic Time (hours)", min_value=1, key=f"{stage}_new_topic_time")
        if st.button("Add Topic", key=f"{stage}_add_topic"):
            if new_topic_name.strip():
                data["topics"].append({"name": new_topic_name, "time": new_topic_time})
                st.success(f"Added New Topic: {new_topic_name}")
            else:
                st.error("Topic name cannot be empty")
        
        # Edit resources
        st.subheader("Edit Resources")
        for resource_type, resources in data["resources"].items():
            with st.expander(f"Edit {resource_type.capitalize()}"):
                for i, resource in enumerate(resources):
                    new_resource = st.text_input(f"Edit {resource_type.capitalize()} {i+1}", resource, key=f"{stage}_{resource_type}_{i}")
                    if st.button(f"Save Changes to {resource_type.capitalize()} {i+1}", key=f"{stage}_{resource_type}_{i}_save"):
                        if new_resource.strip():
                            resources[i] = new_resource
                            st.success(f"Updated {resource_type.capitalize()} {i+1}")
                        else:
                            st.error(f"{resource_type.capitalize()} cannot be empty")
                
                # Add a new resource
                new_resource = st.text_input(f"Add New {resource_type.capitalize()}", key=f"{stage}_new_{resource_type}")
                if st.button(f"Add {resource_type.capitalize()}", key=f"{stage}_add_{resource_type}"):
                    if new_resource.strip():
                        resources.append(new_resource)
                        st.success(f"Added New {resource_type.capitalize()}: {new_resource}")
                    else:
                        st.error(f"{resource_type.capitalize()} cannot be empty")
        
        # Save changes to ROADMAP
        if st.button("Save All Changes", key=f"{stage}_save_all"):
            ROADMAP[stage] = data
            st.success(f"All changes saved for {stage}")

def main_app():
    st.title("🚀 Data Science Roadmap Tracker")
    st.markdown("### Track your progress and achieve your data science goals!")

    # Sidebar with progress metrics
    with st.sidebar:
        st.header("📊 Progress Overview")
        metrics = calculate_progress(ROADMAP, st.session_state.progress)
        st.metric("Total Hours", f"{metrics['total']['hours']}h")
        st.metric("Completed", f"{metrics['total']['completed']}h")
        st.metric("Remaining", f"{metrics['total']['remaining']}h")
        st.progress(metrics["total"]["percent"] / 100)

        st.markdown("---")
        st.header("🔍 Quick Navigation")
        for stage in ROADMAP.keys():
            if st.button(f"{stage} ({metrics['stages'][stage]['percent']:.1f}%)"):
                st.session_state.selected_stage = stage

    # Main content
    selected_stage = st.session_state.get("selected_stage", list(ROADMAP.keys())[0])
    data = ROADMAP[selected_stage]
    metrics = calculate_progress(ROADMAP, st.session_state.progress)

    # Tabs for stage details
    st.markdown(f"## {selected_stage} - {metrics['stages'][selected_stage]['percent']:.1f}% Complete")
    tabs = st.tabs(["Overview", "Topics", "Resources", "Progress"])
    
    # Overview Tab
    with tabs[0]:
        st.markdown("### Overview")
        st.write(f"**Total Hours:** {metrics['stages'][selected_stage]['total']}h")
        st.write(f"**Completed Hours:** {metrics['stages'][selected_stage]['completed']}h")
        st.write(f"**Remaining Hours:** {metrics['stages'][selected_stage]['total'] - metrics['stages'][selected_stage]['completed']}h")
        st.progress(metrics['stages'][selected_stage]['percent'] / 100)

    # Topics Tab
    with tabs[1]:
        st.markdown("### Topics")
        for topic in data["topics"]:
            cols = st.columns([1, 4])
            checked = cols[0].checkbox(
                " ", 
                value=topic["name"] in st.session_state.progress.get(selected_stage, []),
                key=f"{selected_stage}_{topic['name']}"
            )
            cols[1].markdown(f"**{topic['name']}** ({topic['time']}h)")
            if checked:
                st.session_state.progress[selected_stage] = st.session_state.progress.get(selected_stage, []) + [topic["name"]]
            else:
                st.session_state.progress[selected_stage] = [t for t in st.session_state.progress.get(selected_stage, []) if t != topic["name"]]
        save_progress(st.session_state.user, st.session_state.progress)

    # Resources Tab
    with tabs[2]:
        st.markdown("### Resources")
        resource_tabs = st.tabs(["Books", "Documentation", "Videos", "Practice", "Research"])
        with resource_tabs[0]:
            st.markdown("\n".join([f"- {book}" for book in data["resources"]["books"]]))
        with resource_tabs[1]:
            st.markdown("\n".join([f"- [{link.split(' ')[0]}]({link})" for link in data["resources"]["documentation"]]))
        with resource_tabs[2]:
            for video in data["resources"]["youtube"]:
                st.video(video.split(" ")[0])
        with resource_tabs[3]:
            st.markdown("\n".join([f"- [{site}]({site})" for site in data["resources"]["practice_sites"]]))
        with resource_tabs[4]:
            st.markdown("\n".join([f"- {paper}" for paper in data["resources"].get("research_papers", [])]))

    # Progress Tab
    with tabs[3]:
        st.markdown("### Progress")
        st.write("Track your progress for each topic in this stage.")
        for topic in data["topics"]:
            st.write(f"- **{topic['name']}**: {'✅ Completed' if topic['name'] in st.session_state.progress.get(selected_stage, []) else '❌ Not Completed'}")

    # Edit Roadmap Button
    if st.button("Edit Roadmap"):
        edit_roadmap()

# Authentication UI
def auth_page():
    st.title("🔐 Data Science Roadmap Login")
    menu = st.selectbox("Menu", ["Login", "Sign Up"])  # Initialize the menu variable

    if menu == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user = login_user(email, password)
            if user:
                st.session_state.user = email
                st.session_state.progress = load_progress(email)  # Load user progress
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

    elif menu == "Sign Up":
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        confirm = st.text_input("Confirm Password", type='password')
        if st.button("Create Account"):
            if password == confirm:
                try:
                    create_user(email, password)
                    st.success("Account created successfully! Please login.")
                except sqlite3.IntegrityError:  # Handle duplicate email error
                    st.error("An account with this email already exists.")
                except Exception as e:  # Catch other exceptions
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Passwords do not match. Please try again.")

# App flow
def main():
    # Initialize session state variables
    if 'progress' not in st.session_state:
        st.session_state.progress = {}
    if 'user' not in st.session_state:
        auth_page()
    else:
        main_app()
        if st.sidebar.button("Logout"):  # Move Logout button to the sidebar
            del st.session_state.user
            del st.session_state.progress
            st.success("Logged out successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
