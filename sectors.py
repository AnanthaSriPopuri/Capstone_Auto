"""
sectors.py  — Master sector registry
Each sector has: 4 entities, schemas, file formats,
diagnoses/domain-values, column descriptions
"""
import random

SECTORS = {

    "Healthcare": {
        "color": "#2563eb",
        "description": "A mid-sized hospital network facing challenges managing patient records, doctor assignments, and hospital operations due to outdated legacy systems.",
        "goal": "Build a robust end-to-end data pipeline that cleans and integrates patient data, performs complex transformations and analytics, and enables real-time reporting.",
        "entities": {
            "Patients":  {
                "file": "patients.csv", "format": "CSV",
                "columns": [
                    ("PatientID","Unique identifier for each patient","VARCHAR(10)","PK"),
                    ("Name","Full name of the patient","VARCHAR(100)",""),
                    ("Age","Age of the patient","INT",""),
                    ("Gender","Male/Female/Other","VARCHAR(10)",""),
                    ("AdmissionDate","Date of hospital admission","DATE",""),
                    ("DischargeDate","Date of discharge (can be null)","DATE","NULLABLE"),
                    ("Diagnosis","Primary diagnosis","VARCHAR(100)",""),
                    ("TreatmentPlan","Summary of treatment plan","VARCHAR(200)",""),
                    ("DoctorID","ID of assigned doctor","VARCHAR(10)","FK→Doctors"),
                    ("HospitalID","ID of hospital where admitted","INT","FK→Hospitals"),
                    ("InsuranceProvider","Name of insurance company (can be null)","VARCHAR(100)","NULLABLE"),
                    ("BillingAmount","Total billing amount for treatment","DECIMAL(10,2)",""),
                ],
                "domain_values": ["Covid-19","Malaria","TB","Diabetes","Asthma","Hypertension","Dengue","Typhoid","Pneumonia","Fracture"],
                "domain_field": "Diagnosis",
                "amount_field": "BillingAmount",
                "date_field": "AdmissionDate",
                "id_field": "PatientID",
                "name_field": "Name",
            },
            "Doctors":   {
                "file": "doctors.csv", "format": "CSV",
                "columns": [
                    ("DoctorID","Unique identifier for each doctor","VARCHAR(10)","PK"),
                    ("Name","Full name of the doctor","VARCHAR(100)",""),
                    ("Specialization","Medical specialty","VARCHAR(80)",""),
                    ("HospitalID","Hospital the doctor is affiliated with","INT","FK→Hospitals"),
                ],
                "domain_values": ["General Medicine","Cardiology","Orthopedics","Neurology","Pediatrics","Oncology"],
                "domain_field": "Specialization",
            },
            "Hospitals":  {
                "file": "hospital.csv", "format": "CSV",
                "columns": [
                    ("HospitalID","Unique identifier for each hospital","INT","PK"),
                    ("HospitalName","Name of the hospital","VARCHAR(100)",""),
                    ("Location","City where the hospital is located","VARCHAR(80)",""),
                    ("Capacity","Number of beds available","INT",""),
                ],
                "domain_values": ["Mumbai","Delhi","Chennai","Bangalore","Hyderabad"],
                "domain_field": "Location",
            },
            "Billing":   {
                "file": "billing.csv", "format": "CSV",
                "columns": [
                    ("BillID","Unique bill identifier","VARCHAR(10)","PK"),
                    ("PatientID","Reference to patient","VARCHAR(10)","FK→Patients"),
                    ("BillingDate","Date of bill generation","DATE",""),
                    ("Amount","Bill amount","DECIMAL(10,2)",""),
                    ("PaymentStatus","Paid/Unpaid/Pending","VARCHAR(20)",""),
                    ("InsuranceClaim","Amount claimed from insurance","DECIMAL(10,2)","NULLABLE"),
                ],
                "domain_values": ["Paid","Unpaid","Pending"],
                "domain_field": "PaymentStatus",
                "amount_field": "Amount",
            },
        },
        "inconsistencies": [
            "Missing values in InsuranceProvider and DischargeDate",
            "Repeated patient records from multiple uploads",
            "Irregular date formats (DD-MM-YYYY vs YYYY-MM-DD vs MM/DD/YYYY)",
            "Trailing/leading spaces in patient Name field",
            "Inconsistent Gender values (male/MALE/Male/M)",
            "Non-numeric BillingAmount entries (e.g. 'Ten Thousand')",
            "Negative BillingAmount values",
            "Future dates in AdmissionDate",
            "Age stored as text ('Thirty Four')",
            "Inconsistent Diagnosis casing (covid-19/COVID-19/Covid-19)",
            "Extra column 'ExtraColumn' not in schema",
            "Duplicate PatientID values",
            "Missing DoctorID references (orphaned FK)",
            "Empty rows / rows with fewer than 12 fields",
            "Inconsistent InsuranceProvider spelling",
        ],
        "powerbi_pages": [
            "Operations & Capacity Planning",
            "Finance & Revenue Insights",
            "Clinical & Quality Overview",
        ],
        "join_key": "HospitalID",
        "analysis_join": "Join Patients with Hospitals on HospitalID, Doctors on DoctorID",
        "kpi_metric": "BillingAmount",
        "group_field": "Diagnosis",
        "location_field": "Location",
        "spec_field": "Specialization",
    },

    "Banking": {
        "color": "#0891b2",
        "description": "A large commercial bank struggling to unify fragmented customer, account, and transaction data spread across legacy core-banking systems.",
        "goal": "Build an end-to-end banking data pipeline that consolidates customer records, cleans transaction data, and enables real-time fraud detection and revenue reporting.",
        "entities": {
            "Customers":     {"file":"customers.csv","format":"CSV","columns":[("CustomerID","Unique customer ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("Age","Customer age","INT",""),("Gender","Male/Female/Other","VARCHAR(10)",""),("City","City of residence","VARCHAR(80)",""),("AccountType","Savings/Current/Fixed","VARCHAR(20)",""),("KYCStatus","Verified/Pending/Rejected","VARCHAR(20)",""),("JoinDate","Date of account opening","DATE",""),],"domain_values":["Savings","Current","Fixed","NRI"],"domain_field":"AccountType","amount_field":None,"date_field":"JoinDate","id_field":"CustomerID","name_field":"Name"},
            "Accounts":      {"file":"accounts.csv","format":"CSV","columns":[("AccountID","Unique account ID","VARCHAR(10)","PK"),("CustomerID","Reference to customer","VARCHAR(10)","FK→Customers"),("Balance","Current balance","DECIMAL(14,2)",""),("AccountType","Type of account","VARCHAR(20)",""),("OpenDate","Date opened","DATE",""),("Status","Active/Inactive/Frozen","VARCHAR(20)",""),],"domain_values":["Active","Inactive","Frozen"],"domain_field":"Status","amount_field":"Balance"},
            "Transactions":  {"file":"transactions.txt","format":"TXT","columns":[("TxnID","Unique transaction ID","VARCHAR(10)","PK"),("AccountID","Reference to account","VARCHAR(10)","FK→Accounts"),("TxnDate","Date of transaction","DATE",""),("Amount","Transaction amount","DECIMAL(14,2)",""),("TxnType","Credit/Debit/Transfer","VARCHAR(20)",""),("Channel","ATM/Online/Branch/Mobile","VARCHAR(20)",""),("Status","Success/Failed/Pending","VARCHAR(20)",""),],"domain_values":["Credit","Debit","Transfer","Withdrawal"],"domain_field":"TxnType","amount_field":"Amount","date_field":"TxnDate"},
            "Loans":         {"file":"loans.csv","format":"CSV","columns":[("LoanID","Unique loan ID","VARCHAR(10)","PK"),("CustomerID","Reference to customer","VARCHAR(10)","FK→Customers"),("LoanType","Home/Car/Personal/Education","VARCHAR(30)",""),("LoanAmount","Principal amount","DECIMAL(14,2)",""),("InterestRate","Annual interest rate","DECIMAL(5,2)",""),("StartDate","Loan start date","DATE",""),("Status","Active/Closed/Defaulted","VARCHAR(20)",""),],"domain_values":["Home","Car","Personal","Education"],"domain_field":"LoanType","amount_field":"LoanAmount"},
        },
        "inconsistencies":["Missing KYCStatus values","Duplicate transaction records","Irregular date formats","Negative Balance values","Inconsistent Gender casing","Non-numeric Amount entries","Extra columns not in schema","Missing AccountID references","Empty rows","Inconsistent TxnType spelling","Future dates in TxnDate","Age stored as text","Inconsistent Status casing","Duplicate CustomerID values","Missing LoanAmount values"],
        "powerbi_pages":["Customer & Account Overview","Transaction & Revenue Analysis","Loan Portfolio Insights"],
        "join_key":"CustomerID","analysis_join":"Join Transactions with Accounts on AccountID, Customers on CustomerID","kpi_metric":"Amount","group_field":"TxnType","location_field":"City","spec_field":"AccountType",
    },

    "Retail": {
        "color": "#d97706",
        "description": "A national retail chain struggling with fragmented inventory, order, and customer data spread across multiple store systems and e-commerce platforms.",
        "goal": "Build a unified retail data pipeline that integrates product, order, and customer data to enable inventory optimisation, sales analytics, and demand forecasting.",
        "entities": {
            "Products":   {"file":"products.csv","format":"CSV","columns":[("ProductID","Unique product ID","VARCHAR(10)","PK"),("ProductName","Name of the product","VARCHAR(150)",""),("Category","Product category","VARCHAR(60)",""),("Price","Unit price","DECIMAL(10,2)",""),("StockQty","Units in stock","INT",""),("SupplierID","Reference to supplier","VARCHAR(10)","FK→Suppliers"),("Status","Active/Discontinued","VARCHAR(20)",""),],"domain_values":["Electronics","Clothing","Grocery","Furniture","Sports","Books"],"domain_field":"Category","amount_field":"Price","id_field":"ProductID","name_field":"ProductName"},
            "Orders":     {"file":"orders.txt","format":"TXT","columns":[("OrderID","Unique order ID","VARCHAR(10)","PK"),("CustomerID","Reference to customer","VARCHAR(10)","FK→Customers"),("ProductID","Reference to product","VARCHAR(10)","FK→Products"),("OrderDate","Date of order","DATE",""),("Quantity","Units ordered","INT",""),("TotalAmount","Total order value","DECIMAL(12,2)",""),("Status","Delivered/Pending/Cancelled/Returned","VARCHAR(20)",""),],"domain_values":["Delivered","Pending","Cancelled","Returned"],"domain_field":"Status","amount_field":"TotalAmount","date_field":"OrderDate"},
            "Customers":  {"file":"customers.csv","format":"CSV","columns":[("CustomerID","Unique customer ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("Email","Email address","VARCHAR(150)",""),("City","City of residence","VARCHAR(80)",""),("JoinDate","Date of first purchase","DATE",""),("LoyaltyTier","Gold/Silver/Bronze","VARCHAR(20)",""),],"domain_values":["Gold","Silver","Bronze"],"domain_field":"LoyaltyTier","id_field":"CustomerID","name_field":"Name"},
            "Suppliers":  {"file":"suppliers.csv","format":"CSV","columns":[("SupplierID","Unique supplier ID","VARCHAR(10)","PK"),("SupplierName","Name of supplier","VARCHAR(100)",""),("Country","Country of origin","VARCHAR(80)",""),("Rating","Quality rating 1-5","INT",""),("LeadTimeDays","Average lead time","INT",""),],"domain_values":["India","China","USA","Germany","UK"],"domain_field":"Country"},
        },
        "inconsistencies":["Missing Email values in Customers","Duplicate order records","Irregular date formats in OrderDate","Negative TotalAmount values","Inconsistent Status casing","Non-numeric Price entries","Extra columns not in schema","Missing ProductID references","Empty rows","Inconsistent Category spelling","Future dates in OrderDate","StockQty stored as text","Inconsistent LoyaltyTier casing","Duplicate OrderID values","Missing SupplierID references"],
        "powerbi_pages":["Sales & Revenue Overview","Inventory & Stock Analysis","Customer & Loyalty Insights"],
        "join_key":"CustomerID","analysis_join":"Join Orders with Products on ProductID, Customers on CustomerID, Suppliers on SupplierID","kpi_metric":"TotalAmount","group_field":"Category","location_field":"City","spec_field":"LoyaltyTier",
    },

    "Education": {
        "color": "#7c3aed",
        "description": "A university network struggling with fragmented student records, course enrollments, and exam results spread across multiple campuses and legacy systems.",
        "goal": "Build a unified academic data pipeline that integrates student, course, and performance data to enable analytics, reporting, and early-warning systems.",
        "entities": {
            "Students":    {"file":"students.csv","format":"CSV","columns":[("StudentID","Unique student ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("Age","Student age","INT",""),("Gender","Male/Female/Other","VARCHAR(10)",""),("EnrollmentDate","Date of enrollment","DATE",""),("CourseID","Reference to enrolled course","VARCHAR(10)","FK→Courses"),("HospitalID","Campus ID","INT","FK→Campuses"),("Status","Active/Graduated/Dropped","VARCHAR(20)",""),],"domain_values":["Active","Graduated","Dropped","Suspended"],"domain_field":"Status","amount_field":None,"date_field":"EnrollmentDate","id_field":"StudentID","name_field":"Name"},
            "Courses":     {"file":"courses.csv","format":"CSV","columns":[("CourseID","Unique course ID","VARCHAR(10)","PK"),("CourseName","Name of the course","VARCHAR(150)",""),("Department","Department offering the course","VARCHAR(80)",""),("Credits","Number of credits","INT",""),("FacultyID","Reference to faculty","VARCHAR(10)","FK→Faculty"),],"domain_values":["Computer Science","Mathematics","Physics","Business","Arts","Engineering"],"domain_field":"Department"},
            "Exams":       {"file":"exams.txt","format":"TXT","columns":[("ExamID","Unique exam ID","VARCHAR(10)","PK"),("StudentID","Reference to student","VARCHAR(10)","FK→Students"),("CourseID","Reference to course","VARCHAR(10)","FK→Courses"),("ExamDate","Date of exam","DATE",""),("Score","Score obtained (0-100)","DECIMAL(5,2)",""),("Grade","A/B/C/D/F","VARCHAR(5)",""),("Status","Pass/Fail/Absent","VARCHAR(20)",""),],"domain_values":["A","B","C","D","F"],"domain_field":"Grade","amount_field":"Score","date_field":"ExamDate"},
            "Faculty":     {"file":"faculty.csv","format":"CSV","columns":[("FacultyID","Unique faculty ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("Specialization","Area of expertise","VARCHAR(80)",""),("CampusID","Campus the faculty belongs to","INT","FK→Campuses"),("JoinDate","Date of joining","DATE",""),],"domain_values":["Professor","Associate Professor","Assistant Professor","Lecturer"],"domain_field":"Specialization"},
        },
        "inconsistencies":["Missing Grade values","Duplicate exam records","Irregular date formats in ExamDate","Negative Score values","Inconsistent Gender casing","Non-numeric Score entries","Extra columns not in schema","Missing CourseID references","Empty rows","Inconsistent Department spelling","Future dates in ExamDate","Age stored as text","Inconsistent Status casing","Duplicate StudentID values","Missing FacultyID references"],
        "powerbi_pages":["Student Enrollment Overview","Academic Performance Analysis","Course & Faculty Insights"],
        "join_key":"CourseID","analysis_join":"Join Exams with Students on StudentID, Courses on CourseID, Faculty on FacultyID","kpi_metric":"Score","group_field":"Department","location_field":"CampusID","spec_field":"Specialization",
    },

    "Insurance": {
        "color": "#059669",
        "description": "A large insurance company dealing with fragmented policy, claims, and customer data across multiple product lines and regional offices.",
        "goal": "Build an end-to-end insurance data pipeline to consolidate policy records, automate claims processing, detect fraud, and enable regulatory reporting.",
        "entities": {
            "Customers":  {"file":"customers.csv","format":"CSV","columns":[("CustomerID","Unique customer ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("Age","Customer age","INT",""),("Gender","Male/Female/Other","VARCHAR(10)",""),("City","City of residence","VARCHAR(80)",""),("JoinDate","Date of first policy","DATE",""),],"domain_values":["Mumbai","Delhi","Chennai","Bangalore","Hyderabad"],"domain_field":"City","id_field":"CustomerID","name_field":"Name","date_field":"JoinDate"},
            "Policies":   {"file":"policies.csv","format":"CSV","columns":[("PolicyID","Unique policy ID","VARCHAR(10)","PK"),("CustomerID","Reference to customer","VARCHAR(10)","FK→Customers"),("PolicyType","Life/Health/Motor/Property","VARCHAR(30)",""),("PremiumAmount","Annual premium","DECIMAL(12,2)",""),("StartDate","Policy start date","DATE",""),("EndDate","Policy end date","DATE",""),("Status","Active/Expired/Cancelled","VARCHAR(20)",""),],"domain_values":["Life","Health","Motor","Property"],"domain_field":"PolicyType","amount_field":"PremiumAmount","date_field":"StartDate"},
            "Claims":     {"file":"claims.txt","format":"TXT","columns":[("ClaimID","Unique claim ID","VARCHAR(10)","PK"),("PolicyID","Reference to policy","VARCHAR(10)","FK→Policies"),("ClaimDate","Date of claim filed","DATE",""),("ClaimAmount","Amount claimed","DECIMAL(12,2)",""),("ApprovedAmount","Amount approved (can be null)","DECIMAL(12,2)","NULLABLE"),("Status","Approved/Rejected/Pending","VARCHAR(20)",""),("Reason","Reason for claim","VARCHAR(200)",""),],"domain_values":["Accident","Illness","Property Damage","Death","Theft"],"domain_field":"Reason","amount_field":"ClaimAmount","date_field":"ClaimDate"},
            "Agents":     {"file":"agents.csv","format":"CSV","columns":[("AgentID","Unique agent ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("Region","Operating region","VARCHAR(80)",""),("Specialization","Policy type expertise","VARCHAR(30)",""),("HireDate","Date of hiring","DATE",""),("TotalPoliciesSold","Total policies sold","INT",""),],"domain_values":["North","South","East","West","Central"],"domain_field":"Region"},
        },
        "inconsistencies":["Missing ApprovedAmount values","Duplicate claim records","Irregular date formats","Negative ClaimAmount values","Inconsistent Gender casing","Non-numeric PremiumAmount entries","Extra columns not in schema","Missing PolicyID references","Empty rows","Inconsistent PolicyType spelling","Future dates in ClaimDate","Age stored as text","Inconsistent Status casing","Duplicate PolicyID values","Missing AgentID references"],
        "powerbi_pages":["Policy & Premium Overview","Claims & Settlement Analysis","Agent & Regional Performance"],
        "join_key":"CustomerID","analysis_join":"Join Claims with Policies on PolicyID, Customers on CustomerID, Agents on AgentID","kpi_metric":"ClaimAmount","group_field":"PolicyType","location_field":"Region","spec_field":"Specialization",
    },

    "Telecom": {
        "color": "#0284c7",
        "description": "A telecommunications provider struggling to unify subscriber, network, and billing data across prepaid, postpaid, and broadband service lines.",
        "goal": "Build a unified telecom data pipeline that consolidates subscriber records, cleans call data records, and enables churn prediction and revenue analytics.",
        "entities": {
            "Subscribers":  {"file":"subscribers.csv","format":"CSV","columns":[("SubscriberID","Unique subscriber ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("Age","Subscriber age","INT",""),("Gender","Male/Female/Other","VARCHAR(10)",""),("City","City of residence","VARCHAR(80)",""),("PlanID","Reference to plan","VARCHAR(10)","FK→Plans"),("JoinDate","Date of subscription","DATE",""),("Status","Active/Inactive/Churned","VARCHAR(20)",""),],"domain_values":["Active","Inactive","Churned"],"domain_field":"Status","id_field":"SubscriberID","name_field":"Name","date_field":"JoinDate"},
            "Plans":        {"file":"plans.csv","format":"CSV","columns":[("PlanID","Unique plan ID","VARCHAR(10)","PK"),("PlanName","Name of the plan","VARCHAR(80)",""),("PlanType","Prepaid/Postpaid/Broadband","VARCHAR(20)",""),("MonthlyCost","Monthly charge","DECIMAL(8,2)",""),("DataLimitGB","Data limit in GB","DECIMAL(6,2)",""),("ValidityDays","Plan validity","INT",""),],"domain_values":["Prepaid","Postpaid","Broadband"],"domain_field":"PlanType","amount_field":"MonthlyCost"},
            "CallRecords":  {"file":"callrecords.txt","format":"TXT","columns":[("CallID","Unique call record ID","VARCHAR(10)","PK"),("SubscriberID","Reference to subscriber","VARCHAR(10)","FK→Subscribers"),("CallDate","Date of call","DATE",""),("Duration","Duration in seconds","INT",""),("CallType","Voice/SMS/Data","VARCHAR(20)",""),("Charges","Amount charged","DECIMAL(8,2)",""),("Status","Completed/Failed/Dropped","VARCHAR(20)",""),],"domain_values":["Voice","SMS","Data"],"domain_field":"CallType","amount_field":"Charges","date_field":"CallDate"},
            "Invoices":     {"file":"invoices.csv","format":"CSV","columns":[("InvoiceID","Unique invoice ID","VARCHAR(10)","PK"),("SubscriberID","Reference to subscriber","VARCHAR(10)","FK→Subscribers"),("InvoiceDate","Date of invoice","DATE",""),("AmountDue","Amount to be paid","DECIMAL(10,2)",""),("AmountPaid","Amount paid","DECIMAL(10,2)","NULLABLE"),("PaymentStatus","Paid/Unpaid/Partial","VARCHAR(20)",""),],"domain_values":["Paid","Unpaid","Partial"],"domain_field":"PaymentStatus","amount_field":"AmountDue","date_field":"InvoiceDate"},
        },
        "inconsistencies":["Missing AmountPaid values","Duplicate call records","Irregular date formats","Negative Charges values","Inconsistent Gender casing","Non-numeric Duration entries","Extra columns not in schema","Missing SubscriberID references","Empty rows","Inconsistent CallType spelling","Future dates in CallDate","Age stored as text","Inconsistent Status casing","Duplicate SubscriberID values","Missing PlanID references"],
        "powerbi_pages":["Subscriber & Plan Overview","Revenue & Billing Analysis","Network & Call Quality Insights"],
        "join_key":"SubscriberID","analysis_join":"Join CallRecords with Subscribers on SubscriberID, Plans on PlanID, Invoices on SubscriberID","kpi_metric":"Charges","group_field":"PlanType","location_field":"City","spec_field":"CallType",
    },

    "Logistics": {
        "color": "#b45309",
        "description": "A logistics company struggling with fragmented shipment, driver, and warehouse data spread across regional hubs and partner systems.",
        "goal": "Build an end-to-end logistics data pipeline to unify shipment tracking, driver performance, and warehouse inventory for real-time operational analytics.",
        "entities": {
            "Shipments":   {"file":"shipments.csv","format":"CSV","columns":[("ShipmentID","Unique shipment ID","VARCHAR(10)","PK"),("DriverID","Reference to driver","VARCHAR(10)","FK→Drivers"),("WarehouseID","Reference to warehouse","VARCHAR(10)","FK→Warehouses"),("Origin","City of origin","VARCHAR(80)",""),("Destination","City of destination","VARCHAR(80)",""),("ShipmentDate","Date of dispatch","DATE",""),("DeliveryDate","Date of delivery (nullable)","DATE","NULLABLE"),("Weight","Weight in kg","DECIMAL(8,2)",""),("Cost","Shipment cost","DECIMAL(10,2)",""),("Status","Delivered/In-Transit/Delayed/Cancelled","VARCHAR(20)",""),],"domain_values":["Delivered","In-Transit","Delayed","Cancelled"],"domain_field":"Status","amount_field":"Cost","date_field":"ShipmentDate","id_field":"ShipmentID","name_field":"ShipmentID"},
            "Drivers":     {"file":"drivers.csv","format":"CSV","columns":[("DriverID","Unique driver ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("LicenseNo","Driving license number","VARCHAR(20)",""),("VehicleType","Truck/Van/Bike","VARCHAR(20)",""),("Region","Operating region","VARCHAR(80)",""),("JoinDate","Date of joining","DATE",""),],"domain_values":["Truck","Van","Bike","Container"],"domain_field":"VehicleType"},
            "Routes":      {"file":"routes.txt","format":"TXT","columns":[("RouteID","Unique route ID","VARCHAR(10)","PK"),("Origin","Start location","VARCHAR(80)",""),("Destination","End location","VARCHAR(80)",""),("DistanceKM","Distance in km","DECIMAL(8,2)",""),("EstimatedHrs","Estimated travel hours","DECIMAL(5,2)",""),("RouteType","Highway/City/Mixed","VARCHAR(20)",""),],"domain_values":["Highway","City","Mixed"],"domain_field":"RouteType","amount_field":"DistanceKM"},
            "Warehouses":  {"file":"warehouses.csv","format":"CSV","columns":[("WarehouseID","Unique warehouse ID","VARCHAR(10)","PK"),("Location","City location","VARCHAR(80)",""),("Capacity","Total storage capacity","INT",""),("CurrentStock","Current stock units","INT",""),("Manager","Warehouse manager name","VARCHAR(100)",""),],"domain_values":["Mumbai","Delhi","Chennai","Bangalore","Hyderabad"],"domain_field":"Location"},
        },
        "inconsistencies":["Missing DeliveryDate values","Duplicate shipment records","Irregular date formats","Negative Cost values","Inconsistent Status casing","Non-numeric Weight entries","Extra columns not in schema","Missing DriverID references","Empty rows","Inconsistent VehicleType spelling","Future dates in ShipmentDate","Weight stored as text","Inconsistent RouteType casing","Duplicate ShipmentID values","Missing WarehouseID references"],
        "powerbi_pages":["Shipment & Delivery Overview","Cost & Route Analysis","Driver & Warehouse Performance"],
        "join_key":"WarehouseID","analysis_join":"Join Shipments with Drivers on DriverID, Warehouses on WarehouseID, Routes on RouteID","kpi_metric":"Cost","group_field":"Status","location_field":"Destination","spec_field":"VehicleType",
    },

    "Manufacturing": {
        "color": "#6366f1",
        "description": "A manufacturing plant struggling with fragmented production, machine, worker, and inventory data across multiple production lines.",
        "goal": "Build an integrated manufacturing data pipeline to unify production records, machine maintenance logs, and inventory data for quality control and efficiency analytics.",
        "entities": {
            "Products":    {"file":"products.csv","format":"CSV","columns":[("ProductID","Unique product ID","VARCHAR(10)","PK"),("ProductName","Name of the product","VARCHAR(150)",""),("Category","Product category","VARCHAR(60)",""),("UnitCost","Cost per unit","DECIMAL(10,2)",""),("TargetQty","Target production quantity","INT",""),("ActualQty","Actual quantity produced","INT",""),("QualityScore","Quality score 0-100","DECIMAL(5,2)",""),("Status","Pass/Fail/Rework","VARCHAR(20)",""),],"domain_values":["Electronics","Automotive Parts","Textiles","Chemicals","Food"],"domain_field":"Category","amount_field":"UnitCost","id_field":"ProductID","name_field":"ProductName"},
            "Machines":    {"file":"machines.csv","format":"CSV","columns":[("MachineID","Unique machine ID","VARCHAR(10)","PK"),("MachineName","Name/model of machine","VARCHAR(100)",""),("LineID","Production line ID","VARCHAR(10)",""),("LastMaintenanceDate","Date of last maintenance","DATE",""),("Status","Operational/Under Maintenance/Faulty","VARCHAR(30)",""),("OperatingHrs","Total operating hours","DECIMAL(10,2)",""),],"domain_values":["Operational","Under Maintenance","Faulty"],"domain_field":"Status"},
            "Workers":     {"file":"workers.txt","format":"TXT","columns":[("WorkerID","Unique worker ID","VARCHAR(10)","PK"),("Name","Full name","VARCHAR(100)",""),("Shift","Morning/Evening/Night","VARCHAR(20)",""),("LineID","Assigned production line","VARCHAR(10)",""),("JoinDate","Date of joining","DATE",""),("HourlyWage","Wage per hour","DECIMAL(8,2)",""),("AttendancePct","Attendance percentage","DECIMAL(5,2)",""),],"domain_values":["Morning","Evening","Night"],"domain_field":"Shift","amount_field":"HourlyWage","id_field":"WorkerID","name_field":"Name"},
            "Inventory":   {"file":"inventory.csv","format":"CSV","columns":[("ItemID","Unique item ID","VARCHAR(10)","PK"),("ItemName","Name of raw material/component","VARCHAR(150)",""),("SupplierID","Reference to supplier","VARCHAR(10)",""),("StockQty","Current stock quantity","INT",""),("ReorderLevel","Level at which to reorder","INT",""),("UnitPrice","Price per unit","DECIMAL(10,2)",""),("LastRestockedDate","Date of last restock","DATE",""),],"domain_values":["Steel","Plastic","Rubber","Electronics","Chemicals"],"domain_field":"ItemName","amount_field":"UnitPrice"},
        },
        "inconsistencies":["Missing QualityScore values","Duplicate production records","Irregular date formats","Negative UnitCost values","Inconsistent Status casing","Non-numeric QualityScore entries","Extra columns not in schema","Missing MachineID references","Empty rows","Inconsistent Category spelling","Future dates in LastMaintenanceDate","HourlyWage stored as text","Inconsistent Shift casing","Duplicate ProductID values","Missing SupplierID references"],
        "powerbi_pages":["Production & Quality Overview","Machine & Maintenance Analysis","Worker & Inventory Insights"],
        "join_key":"LineID","analysis_join":"Join Products with Machines on LineID, Workers on LineID, Inventory on SupplierID","kpi_metric":"UnitCost","group_field":"Category","location_field":"LineID","spec_field":"Shift",
    },
}


def get_random_sector():
    name = random.choice(list(SECTORS.keys()))
    return name, SECTORS[name]

def get_sector(name):
    return SECTORS.get(name)

def list_sectors():
    return list(SECTORS.keys())