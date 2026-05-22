"""
generator.py — Creates realistic datasets for any sector
Injects all inconsistency types from the PDF
"""
import random, csv, os
from faker import Faker

fake = Faker()
Faker.seed(0)

CITIES = ["Mumbai","Delhi","Chennai","Bangalore","Hyderabad","Pune","Kolkata","Ahmedabad"]
GENDERS_DIRTY = ["Male","Female","Other","male","MALE","female","M","F","m","FEMALE"]
DATE_FORMATS = ["%Y-%m-%d","%d-%m-%Y","%m/%d/%Y","%d/%m/%Y"]

def rand_date(year_start=2022, year_end=2024, dirty=False):
    from datetime import datetime, timedelta
    start = datetime(year_start,1,1)
    end   = datetime(year_end,12,28)
    d = start + timedelta(days=random.randint(0,(end-start).days))
    if dirty:
        fmt = random.choice(DATE_FORMATS)
        return d.strftime(fmt)
    return d.strftime("%Y-%m-%d")

def rand_amount(lo=1000, hi=50000, dirty=False):
    if dirty:
        r = random.random()
        if r < 0.04: return ""
        if r < 0.07: return random.choice(["Ten Thousand","Twenty Five Thousand","Five Hundred"])
        if r < 0.09: return str(-round(random.uniform(100,5000),2))
        if r < 0.11: return "0"
    return str(round(random.uniform(lo,hi),2))

def rand_age(dirty=False):
    if dirty and random.random() < 0.06:
        return random.choice(["Thirty Four","Twenty","Sixty Five",-5,0,150])
    return random.randint(18,80)

def rand_gender(dirty=False):
    if dirty:
        return random.choice(GENDERS_DIRTY)
    return random.choice(["Male","Female","Other"])

def rand_name(dirty=False):
    name = fake.first_name_nonbinary() + " " + fake.last_name()
    if dirty and random.random() < 0.12:
        return "  " + name + "  "   # leading/trailing spaces
    return name

def rand_domain(values, dirty=False):
    v = random.choice(values)
    if dirty and random.random() < 0.10:
        return random.choice([v.upper(), v.lower(), v.capitalize()])
    return v

def rand_status(values, dirty=False):
    v = random.choice(values)
    if dirty and random.random() < 0.10:
        return random.choice([v.upper(), v.lower()])
    return v

def rand_id(prefix, num, dirty=False):
    if dirty and random.random() < 0.03:
        return "INVALID_" + str(random.randint(1,99))
    return f"{prefix}{num:04d}"


def generate_entity_data(entity_name, schema, n=500, dirty=True):
    """
    Generates n rows matching the entity schema with realistic dirty data.
    Returns list-of-lists [header_row, row1, row2, ...]
    """
    cols = [c[0] for c in schema["columns"]]
    rows = [cols]

    domain_vals = schema.get("domain_values", ["A","B","C"])
    domain_field = schema.get("domain_field")
    amount_field = schema.get("amount_field")
    date_field   = schema.get("date_field")
    id_field     = schema.get("id_field", cols[0])
    name_field   = schema.get("name_field")

    prefix = entity_name[:3].upper()
    used_ids = set()

    for i in range(1, n+1):
        row = []
        for col_name, col_desc, col_type, col_flag in schema["columns"]:
            # ID column
            if col_name == id_field:
                id_val = rand_id(prefix, i, dirty)
                # inject duplicate
                if dirty and random.random() < 0.04 and i > 5:
                    id_val = rand_id(prefix, random.randint(1, i-1), False)
                row.append(id_val)

            # Name column
            elif col_name == (name_field or ""):
                row.append(rand_name(dirty))

            # Age
            elif col_name == "Age":
                row.append(rand_age(dirty))

            # Gender
            elif col_name == "Gender":
                row.append(rand_gender(dirty))

            # Date columns
            elif "Date" in col_name or "date" in col_name:
                val = rand_date(dirty=dirty)
                if "NULLABLE" in col_flag and random.random() < 0.12:
                    val = ""
                row.append(val)

            # Amount / cost / price columns
            elif col_name == (amount_field or ""):
                row.append(rand_amount(dirty=dirty))

            # Domain value columns (Status, Type, Category, etc.)
            elif col_name == domain_field:
                row.append(rand_domain(domain_vals, dirty))

            # Boolean / status-like with NULLABLE
            elif "NULLABLE" in col_flag:
                if random.random() < 0.15:
                    row.append("")
                else:
                    row.append(random.choice(domain_vals))

            # FK columns
            elif col_name.endswith("ID") and col_name != id_field:
                fk_prefix = col_name.replace("ID","")[:3].upper()
                fk_num = random.randint(1, 20)
                if dirty and random.random() < 0.03:
                    row.append(f"{fk_prefix}9999")  # broken FK
                else:
                    row.append(f"{fk_prefix}{fk_num:04d}")

            # Numeric fields
            elif col_type.startswith("INT"):
                val = random.randint(1, 300)
                if dirty and random.random() < 0.04:
                    val = random.choice([-1, 0, 9999])
                row.append(val)

            elif col_type.startswith("DECIMAL"):
                row.append(rand_amount(100, 50000, dirty))

            # Text fallback
            else:
                row.append(fake.word().capitalize())

        rows.append(row)

    # Inject extra column for first entity only
    if dirty and entity_name == list(schema.get("columns",{}))[0] if isinstance(schema.get("columns",{}), dict) else False:
        pass

    # Inject duplicate rows
    if dirty:
        dup_count = max(3, n // 20)
        for _ in range(dup_count):
            src = rows[random.randint(1, len(rows)-1)]
            rows.append(src[:])

    # Inject short/broken rows
    if dirty:
        for _ in range(3):
            rows.append(["BROKEN", "Test"])

    return rows


def write_csv(rows, filepath, delimiter=","):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(rows)

def write_txt(rows, filepath, delimiter="|"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(delimiter.join(str(x) for x in row) + "\n")


def generate_all_files(sector_name, sector_info, base_path, n_per_entity=500):
    """
    Generates all files for a sector into base_path/InputFiles/
    Returns dict of {entity_name: filepath}
    """
    input_path = os.path.join(base_path, "InputFiles")
    os.makedirs(input_path, exist_ok=True)
    file_map = {}

    entities = sector_info["entities"]
    first = True

    for ent_name, ent_schema in entities.items():
        rows = generate_entity_data(ent_name, ent_schema, n=n_per_entity, dirty=True)

        # Add ExtraColumn to first entity to simulate schema inconsistency
        if first:
            rows[0].append("ExtraColumn")
            for row in rows[1:]:
                row.append("EXTRA_DATA" if len(row) > 2 else "")
            first = False

        fmt  = ent_schema.get("format","CSV")
        fname= ent_schema["file"]
        fp   = os.path.join(input_path, fname)

        if fmt == "TXT":
            write_txt(rows, fp, delimiter="|")
        else:
            write_csv(rows, fp)

        file_map[ent_name] = fp
        print(f"  ✓ {ent_name} → {fname}  ({len(rows)-1} rows)")

    # Also create powerbi_dataset.csv (clean sample for Power BI)
    _write_powerbi_sample(sector_name, sector_info, input_path, n=200)

    return file_map


def _write_powerbi_sample(sector_name, sector_info, input_path, n=200):
    entities = sector_info["entities"]
    ent_names = list(entities.keys())
    primary = entities[ent_names[0]]
    cols = [c[0] for c in primary["columns"]]
    extra_cols = ["Location","Specialization"]
    header = cols + extra_cols

    rows = [header]
    for i in range(1, n+1):
        base = generate_entity_data(ent_names[0], primary, n=1, dirty=False)[1]
        base += [random.choice(CITIES), random.choice(primary.get("domain_values",["General"]))]
        rows.append(base)

    write_csv(rows, os.path.join(input_path, "powerbi_dataset.csv"))
    print(f"  ✓ powerbi_dataset.csv  ({n} rows)")