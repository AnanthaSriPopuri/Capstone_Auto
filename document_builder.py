"""
document_builder.py
Generates the complete capstone output document (matching the PDF structure)
for any randomly selected sector.

Sections:
  1. Project Title
  2. Business Scenario
  3. Dataset Source Overview
  4. Schema Details
  5. Unix Commands (15 story-based)
  6. Unix Shell Scripts (4 story-based)
  7. MongoDB Requirements (6+)
  8. Python Implementation
  9. PySpark Core (cleaning + DataFrame + SQL)
  10. Advanced MySQL (stored functions + procedures)
  11. Power BI (transformations + DAX + visualisations)
"""
import random
from datetime import date

# ── helpers ──────────────────────────────────────────────────────────────────
def hr(char="━", n=65): return char * n
def h1(t): return f"\n{hr('═')}\n  {t}\n{hr('═')}\n"
def h2(t): return f"\n{hr()}\n  {t}\n{hr()}\n"
def h3(t): return f"\n── {t} ──\n"
def req(n, title, body): return f"\n{n}. {title}\n   {body}\n"


# ── SECTION BUILDERS ─────────────────────────────────────────────────────────

def title_page(sector_name, company_name):
    today = date.today().strftime("%d %B %Y")
    return f"""
╔══════════════════════════════════════════════════════════════════╗
║          CAPSTONE PROJECT — DATA ENGINEERING PIPELINE           ║
╚══════════════════════════════════════════════════════════════════╝

Project Title:
"End-to-End {sector_name} Data Engineering Pipeline for
 Scalable Analytics and Reporting"

Organisation : {company_name}
Sector       : {sector_name}
Generated on : {today}
"""


def business_scenario(sector_name, sector_info, company_name, stakeholders):
    desc  = sector_info["description"]
    goal  = sector_info["goal"]
    incs  = sector_info["inconsistencies"]
    entities = list(sector_info["entities"].keys())

    inc_list = "\n".join(f"  • {i}" for i in incs[:10])

    return f"""{h1("BUSINESS SCENARIO")}
{desc}

The organisation ({company_name}) wants to modernise its data infrastructure
using a combination of technologies:

  • Unix        — for file management and automation
  • MongoDB     — for flexible document-based storage
  • Python      — for data preprocessing and file handling
  • PySpark     — for scalable data cleansing and analytics
  • Advanced MySQL — for relational operations and stored procedures
  • Power BI    — for interactive dashboards and business insights

Stakeholders:
  • {stakeholders[0]} — Chief Data Officer
  • {stakeholders[1]} — VP Operations
  • {stakeholders[2]} — Lead Data Engineer

The data is fragmented across multiple formats and files, with
inconsistencies such as:

{inc_list}
  • And so on…

The goal is to build a robust, end-to-end data pipeline that:
  • Cleans and integrates data from multiple sources
  • Performs complex transformations and analytics
  • Enables real-time reporting and decision-making
"""


def dataset_overview(sector_info):
    entities = sector_info["entities"]
    ent_list = list(entities.items())

    rows = []
    rows.append(f"{'Source Type':<20} {'File Name':<30}")
    rows.append("─" * 52)
    for ent_name, ent_info in ent_list:
        rows.append(f"{ent_info['format']:<20} {ent_info['file']:<30}")
    rows.append(f"{'MongoDB':<20} {'mongodb_inserts.txt':<30}")
    rows.append(f"{'Advanced MySQL':<20} {'advanced_mysql.txt':<30}")
    rows.append(f"{'CSV':<20} {'powerbi_dataset.csv':<30}")
    table = "\n".join(rows)

    return f"""{h1("DATASET SOURCE OVERVIEW")}
{table}
"""


def schema_section(sector_info):
    entities = sector_info["entities"]
    out = h1("SCHEMA DETAILS")

    for ent_name, ent_info in entities.items():
        out += h2(f"Schema Details for {ent_name} File")
        out += f"{'SL No':<8} {'Column Name':<25} {'Description':<40} {'Type':<20} {'Notes'}\n"
        out += "─" * 100 + "\n"
        for i, (col, desc, typ, flag) in enumerate(ent_info["columns"], 1):
            out += f"{i:<8} {col:<25} {desc:<40} {typ:<20} {flag}\n"
        out += "\n"

    return out


def unix_commands(sector_name, sector_info):
    entities = list(sector_info["entities"].keys())
    e0 = entities[0]
    ent_info = sector_info["entities"][e0]
    fname = ent_info["file"]
    domain = ent_info.get("domain_values", ["TypeA","TypeB"])
    domain_field = ent_info.get("domain_field","Category")
    amount_field = ent_info.get("amount_field","Amount") or "BillingAmount"
    id_field = ent_info.get("id_field", "ID")
    inc = sector_info["inconsistencies"]

    stories = [
        (f"{domain_field} Analysis",
         f"The operations team suspects a rise in {domain[0]} cases. They ask the Unix team to "
         f"find out how many records have {domain_field} as '{domain[0]}', regardless of case sensitivity "
         f"in the {domain_field} field.",
         f"grep -i '{domain[0]}' InputFiles/{fname} | wc -l"),

        ("High Value Audit",
         f"The finance department wants to audit high-value cases. They request a list of all "
         f"records where the {amount_field} exceeds 10000, ensuring only valid numeric entries are considered.",
         f"awk -F',' '{{if ($NF+0 > 10000) print}}' InputFiles/{fname}"),

        (f"Top 5 Oldest by {id_field} in Group 3",
         f"The administrator is curious about the top entries in group 3. "
         f"They want the top five records sorted in descending order.",
         f"awk -F',' '$9==\"3\"' InputFiles/{fname} | sort -t',' -k3 -rn | head -5"),

        ("Data Quality Check",
         "The IT team suspects incomplete records. They need to count how many records "
         "have missing information in any field.",
         f"awk -F',' '{{for(i=1;i<=NF;i++) if($i==\"\") {{print NR; break}}}}' InputFiles/{fname} | wc -l"),

        ("Senior / High-Value Filter",
         f"The team is planning a program for high-priority cases. They ask for records "
         f"older than 50 whose {amount_field} is less than 5000.",
         f"awk -F',' '$3>50 && $NF+0<5000 {{print $2}}' InputFiles/{fname}"),

        ("Group Coverage Count",
         "The operations department wants to know how many different groups have "
         "records according to the data in the file.",
         f"awk -F',' 'NR>1 {{print $9}}' InputFiles/{fname} | sort -u | wc -l"),

        ("Missing Field Detection",
         f"The claims team needs to identify records that have both a key field and "
         f"an optional field missing in the same record.",
         f"awk -F',' '$10==\"\" && $11==\"\"' InputFiles/{fname}"),

        ("Duplicate ID Detection",
         f"The data steward needs to find duplicate {id_field} values that may have been "
         "introduced during repeated uploads.",
         f"awk -F',' 'NR>1 {{print $1}}' InputFiles/{fname} | sort | uniq -d"),

        ("Date Range Filter",
         "The analytics team needs to extract all records admitted in a specific year "
         "for time-series analysis.",
         f"grep '2023' InputFiles/{fname} | wc -l"),

        ("Invalid Numeric Detection",
         f"The finance team needs to find all records where {amount_field} is non-numeric "
         "to flag them for correction.",
         f"awk -F',' '$NF !~ /^[0-9.]+$/ && NR>1 {{print NR\": \"$0}}' InputFiles/{fname}"),

        ("Record Count Per Group",
         f"Management needs a quick count of records grouped by {domain_field} "
         "to understand distribution.",
         f"awk -F',' 'NR>1 {{print ${domain_field}}}' InputFiles/{fname} | sort | uniq -c | sort -rn"),

        ("Case-Insensitive Field Extraction",
         f"The reporting team needs all records where {domain_field} matches a value "
         "regardless of how it was entered.",
         f"grep -i '{domain[1] if len(domain)>1 else domain[0]}' InputFiles/{fname}"),

        ("Extract Specific Columns",
         "The data team needs a lightweight file with only the ID and amount columns "
         "for a quick financial summary.",
         f"cut -d',' -f1,12 InputFiles/{fname} > OutputFiles/id_amount_summary.txt"),

        ("Sort by Amount Descending",
         f"The finance team needs the top 10 highest {amount_field} records to prioritise "
         "auditing efforts.",
         f"sort -t',' -k12 -rn InputFiles/{fname} | head -10"),

        ("File-Level Record Count",
         "The ETL team needs a quick count of total records in each input file "
         "before processing begins.",
         f"wc -l InputFiles/*.csv InputFiles/*.txt"),
    ]

    out = h1("IMPLEMENTATION USING UNIX COMMANDS")
    out += f"Data Source: {fname}\n"

    for i, (title, story, cmd) in enumerate(stories, 1):
        out += f"\n{i}. {title}\n"
        out += f"   {story}\n"
        out += f"\n   $ {cmd}\n"

    return out


def shell_scripts(sector_name, sector_info):
    entities = list(sector_info["entities"].keys())
    e0 = entities[0]
    ent_info = sector_info["entities"][e0]
    fname = ent_info["file"]
    amount_field = ent_info.get("amount_field","Amount") or "BillingAmount"
    domain = ent_info.get("domain_values", ["TypeA","TypeB"])

    scripts = [
        ("Senior / High-Priority Count",
         f"The administrator is planning a wellness program. They ask the IT team to find "
         f"out how many records are above a key threshold and save the count in a file "
         f"named senior_count.txt for future reference.",
         f"""#!/bin/bash
awk -F',' '$3>60' InputFiles/{fname} | wc -l > OutputFiles/senior_count.txt
echo "Count saved to OutputFiles/senior_count.txt"
cat OutputFiles/senior_count.txt"""),

        ("Critical Cases Extraction",
         f"The emergency response team needs to prioritise critical cases. They request a list "
         f"of all records diagnosed with either '{domain[0]}' or '{domain[1] if len(domain)>1 else domain[0]}' "
         f"and whose {amount_field} exceeds 7000. These records should be saved in a file called "
         f"critical_cases.txt for immediate review.",
         f"""#!/bin/bash
awk -F',' 'tolower($7)~/{domain[0].lower()}|{(domain[1] if len(domain)>1 else domain[0]).lower()}/ && $12+0>7000' \\
    InputFiles/{fname} > OutputFiles/critical_cases.txt
echo "Critical cases: $(wc -l < OutputFiles/critical_cases.txt)"
head -5 OutputFiles/critical_cases.txt"""),

        ("Average Amount Calculation",
         f"The finance department wants to analyse treatment costs. They ask the IT team "
         f"to calculate the average {amount_field} of all records, rounded to two decimal places, "
         f"ignoring any missing or invalid entries. The result should be printed for their analysis.",
         f"""#!/bin/bash
awk -F',' 'NR>1 && $12~/^[0-9]+/ {{sum+=$12; count++}}
END {{
  if (count>0) printf "Average {amount_field}: %.2f\\n", sum/count
  else print "No valid entries found"
}}' InputFiles/{fname}"""),

        ("Data Cleaning and Standardisation",
         f"The data governance team is preparing for a compliance audit. They need a cleaned "
         f"version of {fname} where names have no leading or trailing spaces, missing values are "
         f"replaced with 'Unknown', {amount_field} values are set to 0 if missing, and all dates are "
         f"converted to YYYY-MM-DD format. This cleaned file should be saved as "
         f"{fname.replace('.','_cleaned.')} inside the InputFiles folder.",
         f"""#!/bin/bash
awk -F',' 'BEGIN{{OFS=","}}
NR==1 {{print; next}}
{{
  gsub(/^[ \\t]+|[ \\t]+$/, "", $2)  # trim name
  if ($11=="") $11="Unknown"          # fill missing
  if ($12=="" || $12+0==0) $12="0"   # fix amount
  print
}}' InputFiles/{fname} > InputFiles/{fname.replace('.','_cleaned.')}
echo "Cleaned file saved: InputFiles/{fname.replace('.','_cleaned.')}"
wc -l InputFiles/{fname.replace('.','_cleaned.')}"""),
    ]

    out = h1("IMPLEMENTATION USING UNIX SHELL SCRIPTS")
    out += f"Data Source: {fname}\n"

    for i, (title, story, script) in enumerate(scripts, 1):
        out += f"\n{i}. {title}\n"
        out += f"   {story}\n"
        out += f"\nScript:\n"
        for line in script.strip().split("\n"):
            out += f"   {line}\n"

    return out


def mongodb_section(sector_name, sector_info):
    entities = list(sector_info["entities"].keys())
    e0 = entities[0]
    ent_info = sector_info["entities"][e0]
    domain = ent_info.get("domain_values", ["TypeA","TypeB"])
    domain_field = ent_info.get("domain_field","Category")
    amount_field = ent_info.get("amount_field","Amount") or "BillingAmount"
    db_name = sector_name.lower().replace(" ","_") + "_db"

    requirements = [
        ("Update Amount for Domain-Specific Records",
         f"The finance department has identified that records with {domain_field} = '{domain[0]}' "
         f"require a special billing adjustment. Update the {amount_field} to 25000 for all "
         f"such records.",
         f"""db.{e0.lower()}.updateMany(
  {{ {domain_field}: {{ $regex: "^{domain[0]}$", $options: "i" }} }},
  {{ $set: {{ {amount_field}: 25000 }} }}
)"""),
        ("Add Default Value for Missing Field",
         f"The operations team has partnered with a default provider. Update the insurance/provider "
         f"field to 'LIC' for all records that currently have no value listed.",
         f"""db.{e0.lower()}.updateMany(
  {{ $or: [ {{ InsuranceProvider: "" }}, {{ InsuranceProvider: null }}, {{ InsuranceProvider: {{ $exists: false }} }} ] }},
  {{ $set: {{ InsuranceProvider: "LIC" }} }}
)"""),
        ("Update Missing Date Fields",
         "The administration wants accurate records for compliance. Update the discharge/end date "
         "to today's date for all records where it is missing.",
         f"""db.{e0.lower()}.updateMany(
  {{ $or: [ {{ DischargeDate: "" }}, {{ DischargeDate: null }} ] }},
  {{ $set: {{ DischargeDate: new Date().toISOString().split("T")[0] }} }}
)"""),
        ("Find High-Risk Records",
         f"The research team is analysing high-risk cases. Find all records older than 55 "
         f"with {amount_field} greater than 15000.",
         f"""db.{e0.lower()}.find(
  {{ Age: {{ $gt: 55 }}, {amount_field}: {{ $gt: 15000 }} }},
  {{ _id: 0, Name: 1, Age: 1, {domain_field}: 1, {amount_field}: 1 }}
).sort({{ {amount_field}: -1 }})"""),
        (f"Count Cases by {domain_field} in Group 3",
         f"The operations team is monitoring trends. Count records with {domain_field} as "
         f"'{domain[0]}' or '{domain[1] if len(domain)>1 else domain[0]}', regardless of case sensitivity.",
         f"""db.{e0.lower()}.countDocuments({{
  HospitalID: 3,
  {domain_field}: {{ $regex: "{domain[0]}|{domain[1] if len(domain)>1 else domain[0]}", $options: "i" }}
}})"""),
        ("Export Updated Records",
         "The data migration team needs all updated records exported for integration "
         "with the reporting system.",
         f"""// Run from terminal:
mongoexport --db={db_name} --collection={e0.lower()} \\
  --type=csv --fields=PatientID,Name,Age,{domain_field},{amount_field} \\
  --out=InputFiles/patients5.csv"""),
    ]

    out = h1("IMPLEMENTATION USING MONGODB")
    out += f"Data Source: mongodb_inserts.txt\nDatabase: {db_name}\n"

    for i, (title, story, code) in enumerate(requirements, 1):
        out += f"\n{i}. {title}\n"
        out += f"   {story}\n"
        out += f"\nMongoDB Shell:\n"
        for line in code.strip().split("\n"):
            out += f"   {line}\n"

    return out


def python_section(sector_name, sector_info):
    entities = list(sector_info["entities"].keys())
    e0 = entities[0]
    ent_info = sector_info["entities"][e0]
    fname = ent_info["file"]
    amount_field = ent_info.get("amount_field","BillingAmount") or "BillingAmount"
    domain_field = ent_info.get("domain_field","Category")
    n_cols = len(ent_info["columns"])

    code = f'''import csv, os
from datetime import datetime

INPUT  = "InputFiles/{fname}"
OUTPUT = "InputFiles/{fname.replace(".","3_cleaned.")}"

def normalize_date(val):
    for fmt in ["%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d"]:
        try: return datetime.strptime(val.strip(), fmt).strftime("%Y-%m-%d")
        except: pass
    return val.strip()

seen_rows = set()
skipped = written = 0

with open(INPUT, encoding="utf-8", errors="replace") as fin, \\
     open(OUTPUT, "w", newline="", encoding="utf-8") as fout:

    reader = csv.reader(fin)
    writer = csv.writer(fout)

    for i, row in enumerate(reader):
        # Header row
        if i == 0:
            # Remove ExtraColumn if present
            header = [c for c in row if c.strip().lower() != "extracolumn"]
            writer.writerow(header); continue

        # Skip short rows (fewer than {n_cols} fields)
        if len(row) < {n_cols}: skipped += 1; continue

        row = row[:{n_cols}]  # trim extra columns

        # Trim all fields
        row = [f.strip() for f in row]

        # Normalise Gender / {domain_field}
        row[3] = row[3].capitalize()
        row[6] = row[6].title()

        # Convert dates to YYYY-MM-DD
        row[4] = normalize_date(row[4])
        if row[5]: row[5] = normalize_date(row[5])

        # Fill missing InsuranceProvider
        if not row[10]: row[10] = "Unknown"

        # Fix BillingAmount
        try: float(row[11])
        except: row[11] = "0"

        # Remove exact duplicate rows
        key = tuple(row)
        if key in seen_rows: skipped += 1; continue
        seen_rows.add(key)

        writer.writerow(row)
        written += 1

print(f"Written: {{written:,}}  Skipped: {{skipped:,}}")
print(f"Saved → {{OUTPUT}}")
'''

    story = (
        f"The analytics rollout is blocked because {fname} is messy and inconsistent. "
        "The CIO has asked you to write one Python program that will:\n\n"
        f"  • Read the file safely and trim leading/trailing spaces in every field\n"
        f"  • Normalise Gender and {domain_field} to proper capitalisation for consistent reporting\n"
        f"  • Convert AdmissionDate and DischargeDate to the standard YYYY-MM-DD format\n"
        f"  • Fill missing InsuranceProvider with 'Unknown' and missing {amount_field} with '0'\n"
        f"  • Skip any row that has fewer than {n_cols} fields to avoid schema issues\n"
        f"  • Remove exact duplicate rows caused by repeated uploads\n"
        f"  • Save the fully cleansed dataset so PySpark jobs can run without manual fixes\n\n"
        "Deliver this as a single, production-ready Python script that completes the "
        "end-to-end cleansing in one pass."
    )

    out = h1("IMPLEMENTATION USING PYTHON")
    out += f"Data Source: {fname}\n\n"
    out += f"1. {story}\n"
    out += "\nPython Script:\n"
    out += "\n".join(f"   {l}" for l in code.strip().split("\n"))
    return out


def pyspark_core_section(sector_name, sector_info):
    entities = list(sector_info["entities"].keys())
    e0 = entities[0]
    ent_info = sector_info["entities"][e0]
    fname = ent_info["file"]
    amount_field = ent_info.get("amount_field","BillingAmount") or "BillingAmount"
    domain_field = ent_info.get("domain_field","Category")

    reqs = [
        ("Remove Empty Lines for Data Integrity",
         f"The ETL team noticed blank rows in {fname} that cause schema mismatches during "
         "Spark ingestion. Ensure all empty lines are removed before processing begins.",
         f"""df = spark.read.option("header","true").option("mode","DROPMALFORMED")\\
       .csv("InputFiles/{fname}")
df = df.dropna(how="all")
print(f"Rows after removing empty lines: {{df.count():,}}")"""),

        (f"Clean Up Name and {domain_field} Fields",
         f"The analytics dashboard is showing inconsistent entries due to extra spaces. "
         f"Trim all leading and trailing spaces from the Name and {domain_field} columns.",
         f"""from pyspark.sql.functions import trim, col
df = df.withColumn("Name", trim(col("Name"))) \\
       .withColumn("{domain_field}", trim(col("{domain_field}")))"""),

        ("Normalise Gender for Consistent Grouping",
         f"Reports are failing to group records correctly because Gender values appear as "
         "'male', 'Male', and 'MALE'. Standardise Gender by capitalising properly.",
         """from pyspark.sql.functions import initcap
df = df.withColumn("Gender", initcap(col("Gender")))"""),

        ("Drop Unnecessary Column",
         "The ingestion pipeline includes an ExtraColumn that is not part of the schema "
         "and is causing confusion in downstream joins. Drop this column entirely.",
         """if "ExtraColumn" in df.columns:
    df = df.drop("ExtraColumn")
    print("ExtraColumn dropped")"""),

        ("Remove Duplicate Records",
         "Duplicate rows have been identified due to multiple uploads. "
         "Remove all exact duplicates to prevent inflated counts in reports.",
         """before = df.count()
df = df.dropDuplicates()
print(f"Duplicates removed: {before - df.count():,}")"""),

        (f"Handle Missing Insurance and {amount_field} Values",
         f"The finance department needs accurate billing data for reconciliation. "
         f"Replace missing InsuranceProvider values with 'LIC' and missing {amount_field} "
         f"values with 0 so that aggregations don't fail.",
         f"""from pyspark.sql.functions import when, lit
df = df.withColumn("InsuranceProvider",
       when(col("InsuranceProvider").isNull() | (col("InsuranceProvider")==""),
            lit("LIC")).otherwise(col("InsuranceProvider"))) \\
       .withColumn("{amount_field}",
           when(col("{amount_field}").isNull(), lit("0")).otherwise(col("{amount_field}")))"""),
    ]

    out = h1("IMPLEMENT REQUIREMENTS USING PYSPARK CORE")
    out += f"Data Source: {fname}\n\n"
    out += "# Spark Session Setup\n"
    out += """from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("CapstoneETL").getOrCreate()
spark.sparkContext.setLogLevel("WARN")
"""
    for i, (title, story, code) in enumerate(reqs, 1):
        out += f"\n{i}. {title}\n   {story}\n\nCode:\n"
        for l in code.strip().split("\n"):
            out += f"   {l}\n"

    return out


def pyspark_analysis_section(sector_name, sector_info):
    entities = list(sector_info["entities"].keys())
    e0, e1, e2, e3 = (entities + entities)[:4]
    ent0 = sector_info["entities"][e0]
    amount_field = ent0.get("amount_field","BillingAmount") or "BillingAmount"
    domain_field = ent0.get("domain_field","Category")
    loc_field    = sector_info.get("location_field","Location")
    spec_field   = sector_info.get("spec_field","Specialization")
    join_note    = sector_info.get("analysis_join","Join entities on shared keys")

    reqs = [
        ("City-wise Admissions for Capacity Planning",
         f"The operations team wants to understand load across locations to optimise "
         f"allocation. Combine all patient files into a unified dataset, join with "
         f"the location file to fetch each location's city, and count records per city.",
         f"""# Combine all source files
df1 = spark.read.option("header","true").csv("InputFiles/{ent0['file']}")
df2 = spark.read.option("header","true").option("sep","|").csv("InputFiles/{sector_info['entities'].get(e1,ent0)['file']}")
df_all = df1.unionByName(df2, allowMissingColumns=True)

# Join with location reference
loc_df = spark.read.option("header","true").csv("InputFiles/hospital.csv")
result = df_all.join(loc_df, on="{sector_info['join_key']}", how="left")
result.groupBy("{loc_field}").count().orderBy("count", ascending=False).show()"""),

        ("Top Groups by Average Billing for Revenue Insights",
         f"Finance leadership is reviewing performance. Calculate the average {amount_field} "
         f"per group, and show the top 3 with the highest average.",
         f"""from pyspark.sql.functions import avg, round as spark_round
df_all.groupBy("{spec_field if spec_field else domain_field}") \\
      .agg(spark_round(avg("{amount_field}"),2).alias("avg_billing")) \\
      .orderBy("avg_billing", ascending=False) \\
      .show(3)"""),

        (f"{domain_field} Cases Treated by {spec_field} Specialists",
         f"Clinical governance is assessing whether specialist departments are adequately staffed. "
         f"Count records diagnosed with a specific {domain_field} treated by {spec_field} specialists.",
         f"""from pyspark.sql.functions import lower
spec_df = spark.read.option("header","true").csv("InputFiles/doctors.csv")
joined = df_all.join(spec_df, on="DoctorID", how="inner")
joined.filter(
    lower(joined["{domain_field}"]).contains("{ent0.get('domain_values',['x'])[0].lower()}") &
    lower(joined["{spec_field}"]).contains("general")
).count()"""),

        (f"{domain_field}-wise Aggregates for Disease Burden Analysis",
         f"Public health analysts want to understand the financial and demographic burden. "
         f"Group records by {domain_field} and compute total {amount_field} and average Age.",
         f"""from pyspark.sql.functions import sum as spark_sum, avg, round as r
df_all.withColumn("{amount_field}", df_all["{amount_field}"].cast("double")) \\
      .groupBy("{domain_field}") \\
      .agg(r(spark_sum("{amount_field}"),2).alias("total_billing"),
           r(avg("Age"),1).alias("avg_age")) \\
      .orderBy("total_billing", ascending=False) \\
      .show()"""),

        ("Seasonal Admissions in 2023 (Monsoon Window)",
         "The epidemiology team is examining monsoon season trends. Filter records admitted "
         "between July and September 2023 and count the number per location.",
         f"""df_all.filter(
    (df_all["AdmissionDate"] >= "2023-07-01") &
    (df_all["AdmissionDate"] <= "2023-09-30")
).join(loc_df, on="{sector_info['join_key']}", how="left") \\
 .groupBy("{loc_field}").count() \\
 .orderBy("count", ascending=False) \\
 .show()"""),

        ("Top Earning Specialists for Incentive Programs",
         f"HR and Finance are designing incentive schemes. Compute total {amount_field} per "
         f"specialist by aggregating records on DoctorID, join to show specialisation, and "
         f"show the top 5 earners.",
         f"""spec_billing = df_all \\
    .withColumn("{amount_field}", df_all["{amount_field}"].cast("double")) \\
    .groupBy("DoctorID") \\
    .agg(spark_sum("{amount_field}").alias("total_billing"))

spec_billing.join(spec_df, on="DoctorID", how="inner") \\
    .orderBy("total_billing", ascending=False) \\
    .select("DoctorID","Name","Specialization","total_billing") \\
    .show(5)"""),

        ("Senior Admissions Snapshot",
         "The operations team wants a quick snapshot: among locations with capacity ≥ 100, "
         "how many senior records (Age ≥ 60) were admitted per city-specialisation combination.",
         f"""senior = df_all.filter(df_all["Age"].cast("int") >= 60)
large_loc = loc_df.filter(loc_df["Capacity"].cast("int") >= 100)
snap = senior.join(large_loc, on="{sector_info['join_key']}", how="inner") \\
             .join(spec_df, on="DoctorID", how="inner") \\
             .groupBy("{loc_field}","Specialization") \\
             .count().orderBy("count", ascending=False)
snap.show(5)"""),
    ]

    out = h1("IMPLEMENT REQUIREMENTS USING PYSPARK CORE, DATAFRAME AND SQL")
    out += (f"Data Sources: {ent0['file']} (cleansed using PySpark core), "
            f"and other entity files\n\n"
            f"Note: Before solving any requirement that uses data, first combine all "
            f"files into a unified dataset.\n")

    for i, (title, story, code) in enumerate(reqs, 1):
        out += f"\n{i}. {title}\n   {story}\n\nCode:\n"
        for l in code.strip().split("\n"):
            out += f"   {l}\n"

    return out


def mysql_section(sector_name, sector_info):
    entities = list(sector_info["entities"].keys())
    e0 = entities[0]
    ent_info = sector_info["entities"][e0]
    amount_field = ent_info.get("amount_field","BillingAmount") or "BillingAmount"
    domain_field = ent_info.get("domain_field","Category")
    spec_field   = sector_info.get("spec_field","Specialization")
    loc_field    = sector_info.get("location_field","Location")
    domain       = ent_info.get("domain_values",["TypeA","TypeB","TypeC"])

    reqs = [
        ("Billing Category Function for Finance Review",
         f"The finance team needs a way to classify bills for tiered analysis. "
         f"Create a stored function named Get{amount_field.replace('Amount','')}Category that accepts a "
         f"{amount_field} and returns Low/Medium/High based on strict rules.",
         f"""DELIMITER $$
CREATE FUNCTION GetBillingCategory(p_amount DECIMAL(10,2))
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
  IF p_amount < 10000 THEN RETURN 'Low';
  ELSEIF p_amount BETWEEN 10000 AND 15000 THEN RETURN 'Medium';
  ELSE RETURN 'High';
  END IF;
END $$
DELIMITER ;
-- Usage: SELECT Name, {amount_field}, GetBillingCategory({amount_field}) AS Category FROM {e0.lower()};"""),

        ("Age Group Function for Program Planning",
         "The outreach team is designing age-specific programs and needs a reusable function. "
         "Create a stored function named GetAgeGroup that accepts Age and returns "
         "Young/Middle-aged/Senior.",
         f"""DELIMITER $$
CREATE FUNCTION GetAgeGroup(p_age INT)
RETURNS VARCHAR(15)
DETERMINISTIC
BEGIN
  IF p_age < 30 THEN RETURN 'Young';
  ELSEIF p_age BETWEEN 30 AND 50 THEN RETURN 'Middle-aged';
  ELSE RETURN 'Senior';
  END IF;
END $$
DELIMITER ;
-- Usage: SELECT Name, Age, GetAgeGroup(Age) AS AgeGroup FROM {e0.lower()};"""),

        ("Procedure to List Records by Billing Category",
         "Auditors often request lists of records by billing tier for compliance checks. "
         "Build a stored procedure named ListByBillingCategory that accepts a billing "
         "category (Low/Medium/High) and displays matching records.",
         f"""DELIMITER $$
CREATE PROCEDURE ListByBillingCategory(IN p_category VARCHAR(10))
BEGIN
  SELECT PatientID, Name, {amount_field},
         GetBillingCategory({amount_field}) AS BillingCategory
  FROM {e0.lower()}
  WHERE GetBillingCategory({amount_field}) = p_category;
END $$
DELIMITER ;
-- Usage: CALL ListByBillingCategory('High');"""),

        ("Summary by Age and Billing Category",
         "Executives want a combined view of demographics and spending patterns. "
         "Create a stored procedure named SummaryByAgeAndBilling that groups "
         "by AgeGroup and BillingCategory, shows TotalPatients and AverageBillingAmount.",
         f"""DELIMITER $$
CREATE PROCEDURE SummaryByAgeAndBilling()
BEGIN
  SELECT GetAgeGroup(Age) AS AgeGroup,
         GetBillingCategory({amount_field}) AS BillingCategory,
         COUNT(*) AS TotalPatients,
         ROUND(AVG({amount_field}),2) AS AverageBillingAmount
  FROM {e0.lower()}
  GROUP BY AgeGroup, BillingCategory
  ORDER BY AgeGroup, AverageBillingAmount DESC;
END $$
DELIMITER ;
-- Usage: CALL SummaryByAgeAndBilling();"""),

        (f"Billing by {spec_field}",
         f"Finance and HR need to identify which {spec_field} groups generate the most revenue. "
         f"Develop a stored procedure named BillingBySpecialisation that calculates "
         f"total {amount_field} per {spec_field} across all groups, sorted descending.",
         f"""DELIMITER $$
CREATE PROCEDURE BillingBySpecialisation()
BEGIN
  SELECT d.Specialization,
         ROUND(SUM(p.{amount_field}),2) AS TotalBillingAmount
  FROM {e0.lower()} p
  JOIN doctors d ON p.DoctorID = d.DoctorID
  GROUP BY d.Specialization
  ORDER BY TotalBillingAmount DESC;
END $$
DELIMITER ;
-- Usage: CALL BillingBySpecialisation();"""),

        ("Dynamic Group Statistics",
         f"The COO wants a dynamic report for every group in the network. "
         f"Create a stored procedure named GroupStats that iterates through all groups, "
         f"calculates total records and average {amount_field} for each, and displays results.",
         f"""DELIMITER $$
CREATE PROCEDURE GroupStats()
BEGIN
  DECLARE v_id INT DEFAULT 1;
  DECLARE v_max INT;
  SELECT MAX(HospitalID) INTO v_max FROM {e0.lower()};
  WHILE v_id <= v_max DO
    SELECT HospitalID,
           COUNT(*) AS PatientCount,
           ROUND(AVG({amount_field}),2) AS AvgBilling
    FROM {e0.lower()}
    WHERE HospitalID = v_id;
    SET v_id = v_id + 1;
  END WHILE;
END $$
DELIMITER ;
-- Usage: CALL GroupStats();"""),
    ]

    out = h1("IMPLEMENT REQUIREMENTS USING DATABASE PROGRAMMING IN MYSQL")
    out += "Data Source: advanced_mysql.txt\n\n"

    for i, (title, story, code) in enumerate(reqs, 1):
        out += f"\n{i}. {title}\n   {story}\n\nSQL:\n"
        for l in code.strip().split("\n"):
            out += f"   {l}\n"

    return out


def powerbi_section(sector_name, sector_info):
    entities  = list(sector_info["entities"].keys())
    e0        = entities[0]
    ent_info  = sector_info["entities"][e0]
    amount_field = ent_info.get("amount_field","BillingAmount") or "BillingAmount"
    domain_field = ent_info.get("domain_field","Category")
    loc_field    = sector_info.get("location_field","Location")
    spec_field   = sector_info.get("spec_field","Specialization")
    pages        = sector_info.get("powerbi_pages",["Overview","Revenue","Quality"])
    cols         = [c[0] for c in ent_info["columns"]]

    # Schema table
    schema_rows = ["SL No   Column Name            Description                      "]
    schema_rows.append("─" * 70)
    for i, (col, desc, typ, flag) in enumerate(ent_info["columns"], 1):
        schema_rows.append(f"{i:<8} {col:<25} {desc:<35}")
    if loc_field not in cols:
        schema_rows.append(f"{len(ent_info['columns'])+1:<8} {loc_field:<25} Location (from reference file)")
    if spec_field not in cols:
        schema_rows.append(f"{len(ent_info['columns'])+2:<8} {spec_field:<25} Specialization (from reference file)")

    transformations = [
        ("Clean Up Text Fields for Consistency",
         f"The reporting team noticed inconsistent spacing in names, locations, and "
         f"{spec_field}, which breaks slicers and filters. Remove leading and trailing "
         f"spaces from all text fields like Name, {loc_field}, and {spec_field}."),
        (f"Handle Missing {domain_field} Values",
         f"Clinical dashboards show blank entries for {domain_field}, making trend "
         f"analysis unreliable. Replace all blank or null values in {domain_field} with 'NA'."),
        ("Remove Duplicate Records",
         "The data quality team found duplicate rows due to multiple uploads. "
         "Remove all duplicate rows from the dataset to ensure accurate counts and billing totals."),
        ("Standardise Insurance / Provider",
         "The finance team wants uniform data. If InsuranceProvider is 'Unknown', replace it "
         "with 'LIC' to reflect the default provider."),
        (f"Convert {amount_field} to Numeric",
         f"Some {amount_field} values are entered as text like 'Ten Thousand', causing aggregation "
         f"errors. Convert to numeric values and set the {amount_field} column's data type to Decimal Number."),
        ("Fix Non-Numeric Age Entries",
         "Age column contains text values like 'Thirty Four'. Replace these with their numeric "
         "equivalents and set the column's data type to Whole Number."),
        ("Flag Invalid Discharge Dates (DAX)",
         "Compliance checks require identifying incorrect dates. Create a new column "
         "IsInvalidDate using DAX that flags records as TRUE where DischargeDate is earlier "
         "than AdmissionDate, otherwise FALSE."),
        (f"Calculate Average {amount_field} Excluding Zero (DAX)",
         f"Finance wants a KPI for average billing excluding zero-value cases. Use DAX to "
         f"calculate Average {amount_field} where {amount_field} > 0."),
        ("Validate Gender Column (DAX)",
         "Reports are grouping incorrectly because Gender has inconsistent values. Create a "
         "calculated column CleanGender that maps 'M'→'Male', 'F'→'Female', "
         "all others retain their value."),
        ("Create Age Bucket Column",
         "The demographic team needs age-group segmentation. Create a calculated column "
         "AgeBucket with values: 0-18 Child, 19-40 Adult, 41-60 Middle-aged, 60+ Senior."),
    ]

    dax_measures = [
        ("Total Records",       f"Total Records = COUNTROWS('{e0}')"),
        ("Total Billing",       f"Total {amount_field} = SUM('{e0}'[{amount_field}])"),
        (f"Avg {amount_field}", f"Avg {amount_field} = AVERAGEX(FILTER('{e0}','{e0}'[{amount_field}]>0),'{e0}'[{amount_field}])"),
        ("Active Count",        f"Active Count = CALCULATE(COUNTROWS('{e0}'),'{e0}'[Status]=\"Active\")"),
        ("MoM Growth",          f"MoM Growth = DIVIDE([Total {amount_field}]-CALCULATE([Total {amount_field}],DATEADD('Calendar'[Date],-1,MONTH)),CALCULATE([Total {amount_field}],DATEADD('Calendar'[Date],-1,MONTH)),0)"),
        ("YTD Value",           f"YTD {amount_field} = TOTALYTD([Total {amount_field}],'Calendar'[Date])"),
        ("Rank by Location",    f"Rank By Location = RANKX(ALL('{e0}'[{loc_field}]),[Total {amount_field}],,DESC,DENSE)"),
        ("% Share",             f"% Share = DIVIDE([Total Records],CALCULATE([Total Records],ALL('{e0}')))"),
        ("KPI Status",          f"KPI Status = IF([Avg {amount_field}]>20000,\"High\",IF([Avg {amount_field}]>10000,\"Medium\",\"Low\"))"),
        ("Rolling 30-day Avg",  f"Rolling30dAvg = CALCULATE(AVERAGE('{e0}'[{amount_field}]),DATESINPERIOD('Calendar'[Date],LASTDATE('Calendar'[Date]),-30,DAY))"),
    ]

    viz_pages = []
    for page in pages:
        if "Operations" in page or "Enrollment" in page or "Shipment" in page or "Customer" in page or "Subscriber" in page or "Production" in page:
            charts = [
                f"Count of PatientID by {domain_field} where Age > 35 (Clustered Bar)",
                f"Count of PatientID by Month (Line Chart)",
                f"Count of PatientID by {spec_field} (Treemap)",
                f"Count of PatientID by {loc_field} (Bar Chart)",
                f"Average of {amount_field} by {spec_field} (Clustered Bar)",
            ]
        elif "Finance" in page or "Revenue" in page or "Billing" in page or "Cost" in page:
            charts = [
                f"Average of {amount_field} by {spec_field} (Clustered Bar)",
                f"Sum of {amount_field} by {loc_field} (Clustered Bar)",
                f"Total {amount_field} KPI Card",
                f"Sum of {amount_field} by InsuranceProvider (Treemap)",
                f"Sum of {amount_field} by DoctorID and {spec_field} (Clustered Bar)",
            ]
        else:
            charts = [
                f"Count of PatientID by {domain_field} where Age > 55 (Clustered Bar)",
                f"Count of Distinct {domain_field} (KPI Card)",
                f"Average of Days Admitted by {loc_field} (Bar Chart)",
                f"Count of PatientID by Gender (Donut Chart)",
                f"Count of PatientID by {domain_field} (Horizontal Bar)",
            ]
        viz_pages.append((page, charts))

    out = h1("IMPLEMENT REQUIREMENTS USING POWER BI")
    out += "Data Source: powerbi_dataset.csv\n"
    out += "\nSchema Details:\n"
    out += "\n".join(schema_rows)
    out += "\n\nTransformations:\n"

    for i, (title, story) in enumerate(transformations, 1):
        out += f"\n{i}. {title}\n   {story}\n"

    out += h2("DAX Measures (10)")
    for i, (name, formula) in enumerate(dax_measures, 1):
        out += f"\n{i}. {name}\n   {formula}\n"

    out += h2("Visualisations")
    for page, charts in viz_pages:
        out += f"\n{page}:\n"
        for chart in charts:
            out += f"  • {chart}\n"

    return out


# ── MASTER BUILDER ────────────────────────────────────────────────────────────

def build_document(sector_name, sector_info):
    """Builds the complete capstone document string for any sector."""

    # Generate fake but non-Indian stakeholder names
    fake = Faker()
    company_names = [
        "NorthBridge Solutions","Apex DataWorks","Meridian Tech Partners",
        "Crestline Digital","Summit DataOps","Horizon Infosystems",
        "Pinnacle Analytics","Redwood Data Labs","Cascade Intelligence",
    ]
    first_names = ["Oliver","Claire","Thomas","Sofia","James","Emma",
                   "William","Charlotte","Henry","Isabelle","Sebastian","Laura"]
    last_names  = ["Brentwood","Henderson","Ridley","Marchetti","Whitfield",
                   "Larsson","Caldwell","Sinclair","Fletcher","Moreau"]

    def rand_name_western():
        return random.choice(first_names) + " " + random.choice(last_names)

    company    = random.choice(company_names)
    stk        = [rand_name_western() for _ in range(3)]

    doc  = title_page(sector_name, company)
    doc += business_scenario(sector_name, sector_info, company, stk)
    doc += dataset_overview(sector_info)
    doc += schema_section(sector_info)
    doc += unix_commands(sector_name, sector_info)
    doc += shell_scripts(sector_name, sector_info)
    doc += mongodb_section(sector_name, sector_info)
    doc += python_section(sector_name, sector_info)
    doc += pyspark_core_section(sector_name, sector_info)
    doc += pyspark_analysis_section(sector_name, sector_info)
    doc += mysql_section(sector_name, sector_info)
    doc += powerbi_section(sector_name, sector_info)

    doc += f"\n\n{'═'*65}\n  END OF CAPSTONE DOCUMENT — {sector_name.upper()}\n{'═'*65}\n"
    return doc