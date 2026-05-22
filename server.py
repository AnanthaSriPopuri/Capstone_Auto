from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import os
from datetime import datetime

# Import document generator
from document_builder import generate_docx

app = Flask(__name__)
CORS(app)

# Store latest generated files
LATEST_REQUIREMENTS = ""
LATEST_SOLUTIONS = ""

# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# GET SECTORS
# ============================================================

@app.route("/api/sectors", methods=["GET"])
def get_sectors():

    sectors = [
        "Healthcare",
        "Finance & Banking",
        "Education & EdTech",
        "Retail & E-Commerce",
        "Manufacturing",
        "Transportation & Logistics",
        "Energy & Utilities",
        "Telecom",
        "Government & Public Services",
        "Agriculture",
        "Insurance",
        "Travel & Hospitality",
        "Food & Beverage",
        "Automotive",
        "Cybersecurity",
        "Gaming & Esports",
        "Pharmaceuticals",
        "Real Estate",
        "Legal & Compliance",
        "Human Resources"
    ]

    return jsonify({
        "ok": True,
        "sectors": sectors
    })


# ============================================================
# GENERATE OUTPUT
# ============================================================

@app.route("/api/generate", methods=["POST"])
def generate():

    global LATEST_REQUIREMENTS
    global LATEST_SOLUTIONS

    data = request.json

    sector = data.get("sector", "General")
    complexity = data.get("complexity", "medium")

    # ========================================================
    # REQUIREMENTS CONTENT
    # ========================================================

    requirements = f"""
CAPSTONE PROJECT REQUIREMENTS
=============================

Sector: {sector}
Complexity: {complexity.upper()}

1. Build data ingestion pipelines.
2. Process CSV, JSON, XML, and Excel files.
3. Create MongoDB collections.
4. Build MySQL stored procedures.
5. Implement PySpark transformations.
6. Create Power BI dashboards.
7. Generate automated reports.
8. Build Unix shell automation scripts.
9. Handle duplicate and null records.
10. Create analytical dashboards.
"""

    # ========================================================
    # SOLUTIONS CONTENT
    # ========================================================

    solutions = f"""
CAPSTONE PROJECT SOLUTIONS
==========================

Sector: {sector}
Complexity: {complexity.upper()}

PYTHON:
--------
import pandas as pd

df = pd.read_csv("data.csv")
print(df.head())


MONGODB:
---------
db.users.find()


MYSQL:
-------
SELECT * FROM customers;


PYSPARK:
---------
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("Capstone").getOrCreate()


POWER BI:
----------
Create KPI cards, charts, and dashboards.
"""

    # Save latest
    LATEST_REQUIREMENTS = requirements
    LATEST_SOLUTIONS = solutions

    # ========================================================
    # GENERATE DOCX FILES
    # ========================================================

    os.makedirs("output", exist_ok=True)

    req_path = "output/requirements.docx"
    sol_path = "output/solutions.docx"

    generate_docx(
        title="Capstone Requirements",
        content=requirements,
        filename=req_path
    )

    generate_docx(
        title="Capstone Solutions",
        content=solutions,
        filename=sol_path
    )

    return jsonify({
        "ok": True,
        "requirements": requirements,
        "solutions": solutions
    })


# ============================================================
# DOWNLOAD REQUIREMENTS
# ============================================================

@app.route("/api/download/requirements", methods=["GET"])
def download_requirements():

    path = "output/requirements.docx"

    if os.path.exists(path):
        return send_file(
            path,
            as_attachment=True
        )

    return jsonify({
        "ok": False,
        "error": "Requirements file not found"
    })


# ============================================================
# DOWNLOAD SOLUTIONS
# ============================================================

@app.route("/api/download/solutions", methods=["GET"])
def download_solutions():

    path = "output/solutions.docx"

    if os.path.exists(path):
        return send_file(
            path,
            as_attachment=True
        )

    return jsonify({
        "ok": False,
        "error": "Solutions file not found"
    })


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("   CapstoneStudio — Professional Edition")
    print("   Open: http://localhost:5000")
    print("   Stop: Ctrl + C")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )