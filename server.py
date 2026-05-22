"""
server.py — Flask backend for CapstoneAuto
Endpoints:
  GET  /                        → serves index.html
  GET  /api/sectors             → list all sectors
  POST /api/generate            → randomly pick sector, generate files + document
  GET  /api/download/<type>     → download requirements or solutions txt
  POST /api/generate-with-llm  → same but calls Claude API for enhanced text
"""
import os, sys, json, random, io, zipfile
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, send_file, send_from_directory
from sectors import get_random_sector, get_sector, list_sectors, SECTORS
from generator import generate_all_files
from document_builder import build_document

app = Flask(__name__, static_folder=".", static_url_path="")

BASE = os.path.dirname(os.path.abspath(__file__))

# ── In-memory session storage ─────────────────────────────────────────────────
session = {}

# ── Static files ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(BASE, "index.html")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(BASE, filename)

# ── API ───────────────────────────────────────────────────────────────────────
@app.route("/api/sectors")
def api_sectors():
    return jsonify([
        {"name": k, "color": v["color"], "description": v["description"]}
        for k, v in SECTORS.items()
    ])

@app.route("/api/generate", methods=["POST"])
def api_generate():
    body = request.get_json(force=True) or {}
    forced = body.get("sector")          # optional: force a specific sector
    n_rows = int(body.get("rows", 500))  # rows per entity
    api_key = body.get("api_key", "").strip()

    # Select sector
    if forced and forced in SECTORS:
        sector_name = forced
        sector_info = SECTORS[forced]
    else:
        sector_name, sector_info = get_random_sector()

    session["sector_name"] = sector_name
    session["sector_info"] = sector_info

    # Generate data files
    try:
        file_map = generate_all_files(
            sector_name, sector_info,
            base_path=os.path.join(BASE, "OutputFiles", sector_name.replace(" ","_")),
            n_per_entity=n_rows
        )
    except Exception as e:
        file_map = {}
        print(f"[generator] WARNING: {e}")

    # Build document
    doc = build_document(sector_name, sector_info)

    # Optionally enhance with LLM
    if api_key:
        try:
            doc = _enhance_with_llm(api_key, sector_name, sector_info, doc)
        except Exception as e:
            print(f"[LLM] WARNING: {e} — using built-in document")

    session["requirements_doc"] = doc
    session["solutions_doc"]    = _build_solutions(sector_name, sector_info)

    entities   = list(sector_info["entities"].keys())
    entity_schemas = {}
    for ename, einfo in sector_info["entities"].items():
        entity_schemas[ename] = {
            "file":    einfo["file"],
            "format":  einfo["format"],
            "columns": [{"name":c[0],"desc":c[1],"type":c[2],"flag":c[3]}
                        for c in einfo["columns"]],
        }

    return jsonify({
        "sector":           sector_name,
        "color":            sector_info["color"],
        "description":      sector_info["description"],
        "entities":         entities,
        "entity_schemas":   entity_schemas,
        "inconsistencies":  sector_info["inconsistencies"],
        "files_generated":  list(file_map.values()) if file_map else [],
        "doc_length":       len(doc),
        "doc_preview":      doc[:1500],
    })


@app.route("/api/download/<doctype>")
def api_download(doctype):
    if doctype == "requirements":
        content = session.get("requirements_doc","")
        fname   = f"{session.get('sector_name','output').replace(' ','_')}_requirements.txt"
    elif doctype == "solutions":
        content = session.get("solutions_doc","")
        fname   = f"{session.get('sector_name','output').replace(' ','_')}_solutions.txt"
    elif doctype == "both":
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            sn = session.get("sector_name","output").replace(" ","_")
            zf.writestr(f"{sn}_requirements.txt", session.get("requirements_doc",""))
            zf.writestr(f"{sn}_solutions.txt",    session.get("solutions_doc",""))
        buf.seek(0)
        return send_file(buf, as_attachment=True,
                         download_name=f"{session.get('sector_name','capstone')}_capstone.zip",
                         mimetype="application/zip")
    else:
        return jsonify({"error":"Unknown type"}), 400

    buf = io.BytesIO(content.encode("utf-8"))
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=fname,
                     mimetype="text/plain")


# ── LLM ENHANCEMENT ───────────────────────────────────────────────────────────
def _enhance_with_llm(api_key, sector_name, sector_info, existing_doc):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    entities = list(sector_info["entities"].keys())
    prompt = f"""You are a senior data engineering instructor.
The student has been assigned the sector: {sector_name}
Entities: {', '.join(entities)}

The following capstone document has been auto-generated. 
Your job is to review and improve the Unix commands section and the 
Python/PySpark sections to make them more specific, realistic, and complex.

Keep the full document structure intact. Only enhance the technical sections.
Return the full improved document text.

DOCUMENT:
{existing_doc[:6000]}
"""
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role":"user","content":prompt}]
    )
    return resp.content[0].text


# ── SOLUTIONS DOC ──────────────────────────────────────────────────────────────
def _build_solutions(sector_name, sector_info):
    """Builds a separate solutions document with all working code."""
    entities = list(sector_info["entities"].keys())
    e0 = entities[0]
    ei = sector_info["entities"][e0]
    fname = ei["file"]
    amount = ei.get("amount_field","BillingAmount") or "BillingAmount"
    domain = ei.get("domain_field","Category")
    domain_vals = ei.get("domain_values",["TypeA","TypeB"])

    sol = f"""
{'═'*65}
  SOLUTIONS DOCUMENT — {sector_name.upper()}
{'═'*65}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UNIX SOLUTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

US-UNX-01  {domain_vals[0]} Analysis
$ grep -i '{domain_vals[0]}' InputFiles/{fname} | wc -l

US-UNX-02  High Value Audit
$ awk -F',' '{{if ($NF+0 > 10000) print}}' InputFiles/{fname}

US-UNX-03  Top 5 Oldest Records (Group 3)
$ awk -F',' '$9=="3"' InputFiles/{fname} | sort -t',' -k3 -rn | head -5

US-UNX-04  Data Quality Check
$ awk -F',' '{{for(i=1;i<=NF;i++) if($i=="") {{print NR; break}}}}' InputFiles/{fname} | wc -l

US-UNX-06  Group Coverage Count
$ awk -F',' 'NR>1 {{print $9}}' InputFiles/{fname} | sort -u | wc -l

US-UNX-07  Missing Field Detection
$ awk -F',' '$10=="" && $11==""' InputFiles/{fname}

US-UNX-13  Extract Specific Columns
$ cut -d',' -f1,12 InputFiles/{fname} > OutputFiles/id_amount_summary.txt

US-UNX-14  Sort by Amount Descending
$ sort -t',' -k12 -rn InputFiles/{fname} | head -10

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHELL SCRIPT SOLUTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SH-01  Senior/High-Priority Count:
#!/bin/bash
awk -F',' '$3>60' InputFiles/{fname} | wc -l > OutputFiles/senior_count.txt
cat OutputFiles/senior_count.txt

SH-02  Critical Cases Extraction:
#!/bin/bash
awk -F',' 'tolower($7)~/{domain_vals[0].lower()}|{(domain_vals[1] if len(domain_vals)>1 else domain_vals[0]).lower()}/ && $12+0>7000' \\
    InputFiles/{fname} > OutputFiles/critical_cases.txt
echo "Critical cases: $(wc -l < OutputFiles/critical_cases.txt)"

SH-03  Average Billing Calculation:
#!/bin/bash
awk -F',' 'NR>1 && $12~/^[0-9]+/ {{sum+=$12; count++}}
END {{ if (count>0) printf "Average: %.2f\\n", sum/count }}' InputFiles/{fname}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MONGODB SOLUTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

// 1. Update Billing for {domain_vals[0]} Records
db.{e0.lower()}.updateMany(
  {{ {domain}: {{ $regex: "^{domain_vals[0]}$", $options: "i" }} }},
  {{ $set: {{ {amount}: 25000 }} }}
)

// 2. Add Default Insurance for Uninsured Records
db.{e0.lower()}.updateMany(
  {{ $or: [{{ InsuranceProvider: "" }}, {{ InsuranceProvider: null }}] }},
  {{ $set: {{ InsuranceProvider: "LIC" }} }}
)

// 3. Find High-Risk Records (Age>55, Billing>15000)
db.{e0.lower()}.find(
  {{ Age: {{ $gt: 55 }}, {amount}: {{ $gt: 15000 }} }},
  {{ _id:0, Name:1, Age:1, {domain}:1, {amount}:1 }}
).sort({{ {amount}: -1 }})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PYTHON CLEANING SOLUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import csv
from datetime import datetime

def normalize_date(val):
    for fmt in ["%d-%m-%Y","%m/%d/%Y","%d/%m/%Y","%Y-%m-%d"]:
        try: return datetime.strptime(val.strip(),fmt).strftime("%Y-%m-%d")
        except: pass
    return val.strip()

seen, written, skipped = set(), 0, 0
with open("InputFiles/{fname}") as fin, open("InputFiles/{fname.replace('.','3_cleaned.')}", "w", newline="") as fout:
    r = csv.reader(fin); w = csv.writer(fout)
    for i, row in enumerate(r):
        if i==0: w.writerow([c for c in row if c.strip().lower()!="extracolumn"]); continue
        if len(row) < {len(ei['columns'])}: skipped+=1; continue
        row = [f.strip() for f in row[:{len(ei['columns'])}]]
        row[3] = row[3].capitalize()
        if len(row)>6: row[6] = row[6].title()
        if len(row)>4: row[4] = normalize_date(row[4])
        if len(row)>10 and not row[10]: row[10]="Unknown"
        key = tuple(row)
        if key in seen: skipped+=1; continue
        seen.add(key); w.writerow(row); written+=1
print(f"Written: {{written:,}}  Skipped: {{skipped:,}}")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PYSPARK SOLUTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
spark = SparkSession.builder.appName("Capstone").getOrCreate()
df = spark.read.option("header","true").csv("InputFiles/{fname}")

# 1. Remove empty lines
df = df.dropna(how="all")

# 2. Trim text fields
df = df.withColumn("Name", trim(col("Name")))

# 3. Normalise Gender
df = df.withColumn("Gender", initcap(col("Gender")))

# 4. Drop ExtraColumn
if "ExtraColumn" in df.columns: df = df.drop("ExtraColumn")

# 5. Remove duplicates
df = df.dropDuplicates()

# 6. Fill missing values
df = df.withColumn("InsuranceProvider",
      when(col("InsuranceProvider").isNull() | (col("InsuranceProvider")==""),
           lit("LIC")).otherwise(col("InsuranceProvider"))) \\
       .withColumn("{amount}",
           when(col("{amount}").isNull(),lit("0")).otherwise(col("{amount}")))

# DF Analysis: City-wise count
loc = spark.read.option("header","true").csv("InputFiles/hospital.csv")
df.join(loc,"HospitalID","left").groupBy("Location").count().orderBy("count",ascending=False).show()

# DF Analysis: Top 3 groups by average billing
df.withColumn("{amount}",col("{amount}").cast("double")) \\
  .groupBy("{domain}").agg(round(avg("{amount}"),2).alias("avg_billing")) \\
  .orderBy("avg_billing",ascending=False).show(3)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADVANCED MySQL SOLUTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DELIMITER $$
CREATE FUNCTION GetBillingCategory(p_amount DECIMAL(10,2))
RETURNS VARCHAR(10) DETERMINISTIC
BEGIN
  IF p_amount < 10000 THEN RETURN 'Low';
  ELSEIF p_amount BETWEEN 10000 AND 15000 THEN RETURN 'Medium';
  ELSE RETURN 'High';
  END IF;
END $$

CREATE FUNCTION GetAgeGroup(p_age INT)
RETURNS VARCHAR(15) DETERMINISTIC
BEGIN
  IF p_age < 30 THEN RETURN 'Young';
  ELSEIF p_age BETWEEN 30 AND 50 THEN RETURN 'Middle-aged';
  ELSE RETURN 'Senior';
  END IF;
END $$

CREATE PROCEDURE SummaryByAgeAndBilling()
BEGIN
  SELECT GetAgeGroup(Age) AS AgeGroup,
         GetBillingCategory({amount}) AS BillingCategory,
         COUNT(*) AS TotalPatients,
         ROUND(AVG({amount}),2) AS AverageBillingAmount
  FROM {e0.lower()}
  GROUP BY AgeGroup, BillingCategory
  ORDER BY AgeGroup, AverageBillingAmount DESC;
END $$
DELIMITER ;

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POWER BI DAX SOLUTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Records    = COUNTROWS('{e0}')
Total {amount}   = SUM('{e0}'[{amount}])
Avg {amount}     = AVERAGEX(FILTER('{e0}','{e0}'[{amount}]>0),'{e0}'[{amount}])
MoM Growth       = DIVIDE([Total {amount}]-CALCULATE([Total {amount}],DATEADD('Calendar'[Date],-1,MONTH)),CALCULATE([Total {amount}],DATEADD('Calendar'[Date],-1,MONTH)),0)
YTD Value        = TOTALYTD([Total {amount}],'Calendar'[Date])
KPI Status       = IF([Avg {amount}]>20000,"High",IF([Avg {amount}]>10000,"Medium","Low"))
IsInvalidDate    = IF('{e0}'[DischargeDate]<'{e0}'[AdmissionDate],TRUE(),FALSE())
AgeBucket        = IF('{e0}'[Age]<=18,"Child",IF('{e0}'[Age]<=40,"Adult",IF('{e0}'[Age]<=60,"Middle-aged","Senior")))

{'═'*65}
END OF SOLUTIONS — {sector_name.upper()}
{'═'*65}
"""
    return sol


if __name__ == "__main__":
    print("=" * 54)
    print("  CapstoneAuto — Auto Sector Document Generator")
    print("  Open:  http://localhost:5000")
    print("  Stop:  Ctrl+C")
    print("=" * 54)
    app.run(debug=True, port=5000)