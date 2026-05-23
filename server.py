import os, io, sys, zipfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from sectors import SECTORS, get_random_sector
from document_builder import build_document

app = Flask(__name__, template_folder="templates")
CORS(app)

# In-memory store
_store = {"req_bytes": b"", "solutions": "", "sector": ""}


# Solutions builder (plain text — stays as .txt)
def _build_solutions(sector_name, sector_info):
    entities = list(sector_info["entities"].keys())
    e0     = entities[0]
    ei     = sector_info["entities"][e0]
    fname  = ei["file"]
    amount = ei.get("amount_field", "BillingAmount") or "BillingAmount"
    domain = ei.get("domain_field", "Category")
    dvals  = ei.get("domain_values", ["TypeA", "TypeB"])
    ncols  = len(ei["columns"])
    db     = sector_name.lower().replace(" ", "_") + "_db"
    jkey   = sector_info.get("join_key", "HospitalID")
    locf   = sector_info.get("location_field", "Location")
    bar    = "\u2501" * 65

    return f"""
{'='*65}
  SOLUTIONS DOCUMENT — {sector_name.upper()}
{'='*65}

{bar}
UNIX SOLUTIONS
{bar}

US-UNX-01  {dvals[0]} Analysis
$ grep -i '{dvals[0]}' InputFiles/{fname} | wc -l

US-UNX-02  High Value Audit
$ awk -F',' '{{if ($NF+0 > 10000) print}}' InputFiles/{fname}

US-UNX-03  Top 5 in Group 3
$ awk -F',' '$9=="3"' InputFiles/{fname} | sort -t',' -k3 -rn | head -5

US-UNX-04  Data Quality Check
$ awk -F',' '{{for(i=1;i<=NF;i++) if($i=="") {{print NR; break}}}}' InputFiles/{fname} | wc -l

US-UNX-05  Senior / High-Priority Filter
$ awk -F',' '$3>50 && $NF+0<5000 {{print $2}}' InputFiles/{fname}

US-UNX-06  Group Coverage Count
$ awk -F',' 'NR>1 {{print $9}}' InputFiles/{fname} | sort -u | wc -l

US-UNX-07  Missing Field Detection
$ awk -F',' '$10=="" && $11==""' InputFiles/{fname}

US-UNX-08  Duplicate ID Detection
$ awk -F',' 'NR>1 {{print $1}}' InputFiles/{fname} | sort | uniq -d

US-UNX-09  Date Range Filter
$ grep '2023' InputFiles/{fname} | wc -l

US-UNX-10  Invalid Numeric Detection
$ awk -F',' '$NF !~ /^[0-9.]+$/ && NR>1 {{print NR": "$0}}' InputFiles/{fname}

US-UNX-11  Record Count Per Category
$ awk -F',' 'NR>1 {{print $7}}' InputFiles/{fname} | sort | uniq -c | sort -rn

US-UNX-12  Case-Insensitive Extraction
$ grep -i '{dvals[1] if len(dvals)>1 else dvals[0]}' InputFiles/{fname}

US-UNX-13  Extract ID + Amount Columns
$ cut -d',' -f1,12 InputFiles/{fname} > OutputFiles/id_amount_summary.txt

US-UNX-14  Sort by Amount Descending
$ sort -t',' -k12 -rn InputFiles/{fname} | head -10

US-UNX-15  File-Level Record Count
$ wc -l InputFiles/*.csv InputFiles/*.txt

{bar}
SHELL SCRIPT SOLUTIONS
{bar}

SH-01  Senior Count:
#!/bin/bash
awk -F',' '$3>60' InputFiles/{fname} | wc -l > OutputFiles/senior_count.txt
cat OutputFiles/senior_count.txt

SH-02  Critical Cases:
#!/bin/bash
awk -F',' 'tolower($7)~/{dvals[0].lower()}/ && $12+0>7000' \\
    InputFiles/{fname} > OutputFiles/critical_cases.txt
echo "Critical: $(wc -l < OutputFiles/critical_cases.txt)"

SH-03  Average Amount:
#!/bin/bash
awk -F',' 'NR>1 && $12~/^[0-9]+/ {{sum+=$12; count++}}
END {{ if (count>0) printf "Average: %.2f\\n", sum/count }}' InputFiles/{fname}

SH-04  Data Cleaning:
#!/bin/bash
awk -F',' 'BEGIN{{OFS=","}} NR==1 {{print; next}}
{{ gsub(/^[ \\t]+|[ \\t]+$/,"", $2); if ($11=="") $11="Unknown";
   if ($12=="" || $12+0==0) $12="0"; print }}' \\
    InputFiles/{fname} > InputFiles/{fname.replace('.','_cleaned.')}
echo "Cleaned: InputFiles/{fname.replace('.','_cleaned.')}"

{bar}
MONGODB SOLUTIONS
{bar}

use {db}

// 1. Update Amount for {dvals[0]}
db.{e0.lower()}.updateMany(
  {{ {domain}: {{ $regex: "^{dvals[0]}$", $options: "i" }} }},
  {{ $set: {{ {amount}: 25000 }} }}
)

// 2. Default Insurance
db.{e0.lower()}.updateMany(
  {{ $or: [{{ InsuranceProvider: "" }}, {{ InsuranceProvider: null }}] }},
  {{ $set: {{ InsuranceProvider: "LIC" }} }}
)

// 3. Update Missing Dates
db.{e0.lower()}.updateMany(
  {{ $or: [{{ DischargeDate: "" }}, {{ DischargeDate: null }}] }},
  {{ $set: {{ DischargeDate: new Date().toISOString().split("T")[0] }} }}
)

// 4. High-Risk Records
db.{e0.lower()}.find(
  {{ Age: {{ $gt: 55 }}, {amount}: {{ $gt: 15000 }} }},
  {{ _id:0, Name:1, Age:1, {domain}:1, {amount}:1 }}
).sort({{ {amount}: -1 }})

// 5. Count in Group 3
db.{e0.lower()}.countDocuments({{
  HospitalID: 3,
  {domain}: {{ $regex: "{dvals[0]}|{dvals[1] if len(dvals)>1 else dvals[0]}", $options: "i" }}
}})

// 6. Export (terminal)
mongoexport --db={db} --collection={e0.lower()} --type=csv \\
  --fields=PatientID,Name,Age,{domain},{amount} --out=InputFiles/{e0.lower()}5.csv

{bar}
PYTHON CLEANING SOLUTION
{bar}

import csv
from datetime import datetime

INPUT  = "InputFiles/{fname}"
OUTPUT = "InputFiles/{fname.replace('.','3_cleaned.')}"

def normalize_date(val):
    for fmt in ["%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"]:
        try: return datetime.strptime(val.strip(), fmt).strftime("%Y-%m-%d")
        except: pass
    return val.strip()

seen, written, skipped = set(), 0, 0
with open(INPUT, encoding="utf-8", errors="replace") as fin, \\
     open(OUTPUT, "w", newline="", encoding="utf-8") as fout:
    reader = csv.reader(fin); writer = csv.writer(fout)
    for i, row in enumerate(reader):
        if i == 0:
            writer.writerow([c for c in row if c.strip().lower() != "extracolumn"]); continue
        if len(row) < {ncols}: skipped += 1; continue
        row = [f.strip() for f in row[:{ncols}]]
        if len(row) > 3:  row[3] = row[3].capitalize()
        if len(row) > 6:  row[6] = row[6].title()
        if len(row) > 4 and row[4]: row[4] = normalize_date(row[4])
        if len(row) > 5 and row[5]: row[5] = normalize_date(row[5])
        if len(row) > 10 and not row[10]: row[10] = "Unknown"
        if len(row) > 11:
            try: float(row[11])
            except: row[11] = "0"
        key = tuple(row)
        if key in seen: skipped += 1; continue
        seen.add(key); writer.writerow(row); written += 1
print(f"Written: {{written:,}}  Skipped: {{skipped:,}}")

{bar}
PYSPARK SOLUTIONS
{bar}

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
spark = SparkSession.builder.appName("Capstone").getOrCreate()

df = spark.read.option("header","true").csv("InputFiles/{fname}")
df = df.dropna(how="all").withColumn("Name", trim(col("Name")))
df = df.withColumn("Gender", initcap(col("Gender"))).dropDuplicates()
if "ExtraColumn" in df.columns: df = df.drop("ExtraColumn")
df = df.withColumn("{amount}",
      when(col("{amount}").isNull(),lit("0")).otherwise(col("{amount}")))

loc = spark.read.option("header","true").csv("InputFiles/hospital.csv")

df.join(loc,"{jkey}","left").groupBy("{locf}").count().orderBy("count",ascending=False).show()

df.withColumn("{amount}",col("{amount}").cast("double")) \\
  .groupBy("{domain}").agg(round(avg("{amount}"),2).alias("avg")).orderBy("avg",ascending=False).show(3)

df.filter((col("AdmissionDate")>="2023-07-01")&(col("AdmissionDate")<="2023-09-30")) \\
  .join(loc,"{jkey}","left").groupBy("{locf}").count().orderBy("count",ascending=False).show()

{bar}
ADVANCED MySQL SOLUTIONS
{bar}

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
         ROUND(AVG({amount}),2) AS AvgBilling
  FROM {e0.lower()}
  GROUP BY AgeGroup, BillingCategory
  ORDER BY AgeGroup, AvgBilling DESC;
END $$

DELIMITER ;

{bar}
POWER BI DAX SOLUTIONS
{bar}

Total Records     = COUNTROWS('{e0}')
Total {amount}    = SUM('{e0}'[{amount}])
Avg {amount}      = AVERAGEX(FILTER('{e0}',[{amount}]>0),[{amount}])
MoM Growth        = DIVIDE([Total {amount}]-CALCULATE([Total {amount}],DATEADD('Calendar'[Date],-1,MONTH)),CALCULATE([Total {amount}],DATEADD('Calendar'[Date],-1,MONTH)),0)
YTD {amount}      = TOTALYTD([Total {amount}],'Calendar'[Date])
Rank By Location  = RANKX(ALL('{e0}'[{locf}]),[Total {amount}],,DESC,DENSE)
AgeBucket         = IF('{e0}'[Age]<=18,"Child",IF('{e0}'[Age]<=40,"Adult",IF('{e0}'[Age]<=60,"Middle-aged","Senior")))

{'='*65}
END OF SOLUTIONS — {sector_name.upper()}
{'='*65}
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/sectors", methods=["GET"])
def get_sectors():
    return jsonify({
        "ok": True,
        "sectors": [
            {"name": name, "color": info.get("color", "#2563eb"), "description": info.get("description", "")}
            for name, info in SECTORS.items()
        ]
    })


@app.route("/api/generate", methods=["POST"])
def generate():
    global _store
    body    = request.get_json(force=True) or {}
    forced  = body.get("sector", "").strip()
    api_key = body.get("api_key", "").strip()

    # 1. Pick sector
    if forced and forced in SECTORS:
        sector_name, sector_info = forced, SECTORS[forced]
    else:
        sector_name, sector_info = get_random_sector()

    _store["sector"] = sector_name

    # 2. Build requirements as .docx bytes
    try:
        req_bytes = build_document(sector_name, sector_info)
        _store["req_bytes"] = req_bytes
    except Exception as e:
        return jsonify({"ok": False, "error": f"Document build failed: {e}"}), 500

    # 3. Build solutions as plain text
    try:
        sol_doc = _build_solutions(sector_name, sector_info)
    except Exception as e:
        sol_doc = f"[Solutions build error: {e}]"

    _store["solutions"] = sol_doc

    # 4. Optional Claude AI enhancement (appended as extra text info)
    llm_note = ""
    if api_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            entities = list(sector_info["entities"].keys())
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2048,
                messages=[{"role": "user", "content": (
                    f"You are a senior data engineering instructor.\n"
                    f"The student is working on a {sector_name} capstone project "
                    f"with entities: {', '.join(entities)}.\n"
                    f"Add 3 additional complex PySpark DataFrame analysis requirements "
                    f"specific to this sector. Each must be a user story with working code.\n"
                    f"Format: numbered list, plain text only."
                )}]
            )
            llm_note = resp.content[0].text
        except Exception as e:
            llm_note = f"[LLM skipped: {e}]"

    entities = list(sector_info["entities"].keys())
    entity_schemas = {
        ename: {
            "file":    einfo["file"],
            "format":  einfo["format"],
            "columns": [{"name": c[0], "desc": c[1], "type": c[2], "flag": c[3]} for c in einfo["columns"]],
        }
        for ename, einfo in sector_info["entities"].items()
    }

    return jsonify({
        "ok":              True,
        "sector":          sector_name,
        "color":           sector_info.get("color", "#2563eb"),
        "description":     sector_info.get("description", ""),
        "entities":        entities,
        "entity_schemas":  entity_schemas,
        "inconsistencies": sector_info.get("inconsistencies", []),
        "doc_length":      len(req_bytes),
        "doc_preview":     f"DOCX generated for {sector_name}. Click Download to get the Word file.",
        "llm_used":        bool(api_key),
        "llm_note":        llm_note,
    })


@app.route("/api/download/requirements", methods=["GET"])
def download_requirements():
    content = _store.get("req_bytes", b"")
    if not content:
        return jsonify({"ok": False, "error": "Generate first"}), 404
    s = _store.get("sector", "output").replace(" ", "_").replace("&", "and")
    buf = io.BytesIO(content)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{s}_Requirements.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.route("/api/download/solutions", methods=["GET"])
def download_solutions():
    content = _store.get("solutions", "")
    if not content:
        return jsonify({"ok": False, "error": "Generate first"}), 404
    s = _store.get("sector", "output").replace(" ", "_").replace("&", "and")
    buf = io.BytesIO(content.encode("utf-8"))
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{s}_Solutions.txt",
        mimetype="text/plain"
    )


@app.route("/api/download/both", methods=["GET"])
def download_both():
    req_bytes = _store.get("req_bytes", b"")
    sol_c     = _store.get("solutions", "")
    if not req_bytes and not sol_c:
        return jsonify({"ok": False, "error": "Generate first"}), 404
    s   = _store.get("sector", "output").replace(" ", "_").replace("&", "and")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{s}_Requirements.docx", req_bytes)
        zf.writestr(f"{s}_Solutions.txt", sol_c)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"{s}_Capstone.zip",
        mimetype="application/zip"
    )


if __name__ == "__main__":
    print("=" * 60)
    print("  CapstoneAuto — Running")
    print("  Open: http://localhost:5000")
    print("  Stop: Ctrl+C")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
    