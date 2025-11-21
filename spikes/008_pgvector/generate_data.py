import math
import os
import random
from datetime import datetime, timedelta

import psycopg2
from faker import Faker
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer

# Configuration
NUM_SENSORS = 20
READINGS_PER_SENSOR = 100
START_TIME = datetime.now() - timedelta(days=7)
MOCK_DATA_DIR = "mock_data"

# Initialize Faker
fake = Faker()

# Connection settings
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_USER = os.environ.get("POSTGRES_USER", "mcp_user")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "mcp_password")
DB_NAME = os.environ.get("POSTGRES_DB", "mcp_db")

class KnowledgeGenerator:
    """Generates realistic technical documentation."""
    
    def __init__(self):
        self.fake = Faker()
        
    def generate_building_doc(self, building_name, building_desc):
        """Generates a complex document about the building."""
        doc_type = random.choice(['safety', 'hvac', 'security', 'structural'])
        
        if doc_type == 'safety':
            return self._generate_safety_manual(building_name, building_desc)
        elif doc_type == 'hvac':
            return self._generate_hvac_spec(building_name, building_desc)
        elif doc_type == 'security':
            return self._generate_security_policy(building_name, building_desc)
        else:
            return self._generate_structural_report(building_name, building_desc)

    def _generate_safety_manual(self, name, desc):
        return f"""EMERGENCY RESPONSE PLAN - {name}
CONFIDENTIAL - INTERNAL USE ONLY
Revision Date: {self.fake.date_this_decade()}
Safety Officer: {self.fake.name()}

FACILITY CONTEXT:
{desc}

1.0 FIRE SAFETY PROTOCOLS
The {name} is equipped with a state-of-the-art {self.fake.company()} fire suppression system.
- Primary Suppression: Wet pipe sprinklers in all common areas.
- Server/Electrical Rooms: FM-200 gas suppression (Do not enter when alarm sounds).
- Manual Pull Stations: Located at every exit door and stairwell landing.

2.0 EVACUATION PROCEDURES
In the event of an alarm:
1. Cease all operations immediately. Secure critical machinery if safe to do so.
2. Proceed to the nearest emergency exit. Do NOT use elevators.
3. Gather at Assembly Point: {random.choice(["North Parking Lot", "Main Gate", "Cafeteria Courtyard"])}.
4. Do not re-enter until "All Clear" is given by the Fire Marshal.

3.0 MEDICAL EMERGENCIES
AEDs are located in the main lobby and the 2nd-floor breakroom.
First Aid kits are available in Room {random.randint(100, 199)} and Room {random.randint(200, 299)}.
Emergency Contact: Ext. {random.randint(1000, 9999)} or 911.
"""

    def _generate_hvac_spec(self, name, desc):
        zones_text = ""
        for i in range(1, random.randint(4, 8)):
            zones_text += f"- Zone {i}: Target {random.randint(18, 24)}°C ±1°C. VAV Box ID: VAV-{random.randint(1000,9999)}\n"
            
        return f"""MECHANICAL SYSTEMS SPECIFICATION - {name}
System: Central HVAC & Climate Control
Contractor: {self.fake.company()} Mechanical Services

FACILITY OVERVIEW:
{desc}

1.0 SYSTEM OVERVIEW
Primary cooling is provided by a {self.fake.company()} {random.randint(100, 500)}-ton centrifugal chiller located on the roof.
Heating is supplied by dual natural gas boilers (Model {self.fake.bothify(text='??-####')}).

2.0 ZONING CONFIGURATION
The building is divided into independent climate zones:
{zones_text}

3.0 FILTRATION
- Pre-filters: MERV 8 (Replace Monthly)
- Final filters: MERV 13 (Replace Quarterly)
- HEPA filters installed in sensitive equipment areas.

4.0 MAINTENANCE SCHEDULE
- Weekly: Check pressure differentials and belt tension.
- Monthly: Filter replacement and coil cleaning.
- Annual: Full system balancing and refrigerant analysis.
"""

    def _generate_security_policy(self, name, desc):
        return f"""SECURITY & ACCESS CONTROL POLICY - {name}
Security Provider: {self.fake.company()}
Security Level: {random.choice(['High', 'Medium', 'Critical'])}

FACILITY PROFILE:
{desc}

1.0 PERIMETER SECURITY
- All exterior doors are monitored 24/7 via magnetic contacts.
- CCTV coverage includes {random.randint(20, 50)} HD cameras with 30-day retention.
- Main gate access requires RFID tag and visual verification.

2.0 INTERIOR ACCESS LEVELS
- Level 1 (General): Lobby, Cafeteria. (Visitor Badge allowed)
- Level 2 (Staff): Offices, Meeting Rooms. (Employee Badge required)
- Level 3 (Restricted): Server Rooms, Mechanical Rooms. (Biometric + PIN required)
- Level 4 (Critical): R&D Labs. (Two-person rule applies).

3.0 VISITOR PROTOCOLS
- All visitors must sign NDA at reception.
- Temporary badges must be worn visibly at all times.
- Escort required for all areas beyond the lobby.
- Photography is strictly prohibited inside {name}.
"""

    def _generate_structural_report(self, name, desc):
        return f"""STRUCTURAL INTEGRITY REPORT - {name}
Engineering Firm: {self.fake.company()} Structural Engineers
Inspection Date: {self.fake.date_this_year()}

BUILDING DESCRIPTION:
{desc}

1.0 FOUNDATION & SUBSTRUCTURE
- Type: Reinforced concrete slab-on-grade with deep pile foundations.
- Condition: Good. No significant settlement observed.
- Groundwater Control: Perimeter drainage system functioning normally.

2.0 SUPERSTRUCTURE
- Frame: Structural steel skeleton with fireproofing.
- Load Bearing Walls: Reinforced masonry.
- Roof System: Steel truss with corrugated metal deck.

3.0 SEISMIC & WIND LOAD
- Seismic Zone: {random.choice(['2A', '3', '4'])}
- Wind Load Rating: {random.randint(100, 150)} mph
- Damping: Viscous dampers installed on floors 2-4.

4.0 RECOMMENDATIONS
- Monitor hairline cracks in North Wing stairwell (non-structural).
- Re-apply weatherproofing sealant to exterior joints within 6 months.
"""

    def generate_sensor_datasheet(self, sensor_type, model_num):
        """Generates a technical datasheet for a sensor."""
        specs = {
            "temperature": f"Range: -40 to 125°C\nAccuracy: ±0.5°C\nResponse Time: <500ms",
            "pressure": f"Range: 0 to 100 bar\nAccuracy: ±0.25% FS\nOverpressure Limit: 200 bar",
            "vibration": f"Frequency Range: 10Hz to 1kHz\nSensitivity: 100mV/g\nShock Limit: 500g",
            "humidity": f"Range: 0 to 100% RH\nAccuracy: ±2% RH\nHysteresis: <1% RH"
        }
        spec_text = specs.get(sensor_type, "Standard industrial specifications apply.")
        
        return f"DATASHEET - Model {model_num}\n\nType: Industrial {sensor_type.title()} Sensor\n\nSpecifications:\n{spec_text}\n\nPower Supply: 24V DC\nOutput: 4-20mA Analog Loop\nCompliance: IP67, CE, RoHS\n\nManufacturer: {self.fake.company()}"

    def generate_position_doc(self, sensor_name, location):
        """Generates a document describing the specific installation position."""
        positions = [
            f"INSTALLATION NOTE - {sensor_name}\n\nMounted on the north wall of {location}, approximately 2.5 meters from the floor. Ensure clear line of sight for maintenance.",
            f"POSITION LOG - {sensor_name}\n\nLocated in {location}, attached to the main intake pipe. Vibration dampeners installed to prevent false readings.",
            f"SETUP CONFIGURATION - {sensor_name}\n\nInstalled in {location} (Zone {random.randint(1, 5)}). Wired to Control Panel {random.randint(100, 999)}. Calibrated for local ambient conditions."
        ]
        return random.choice(positions)

    def generate_maintenance_log(self, sensor_name):
        """Generates a maintenance record."""
        issue = self.fake.sentence(nb_words=10)
        action = self.fake.sentence(nb_words=12)
        technician = self.fake.name()
        date = self.fake.date_this_year()
        
        return f"MAINTENANCE LOG - {sensor_name}\nDate: {date}\nTechnician: {technician}\n\nIssue Reported: {issue}\nAction Taken: {action}\nStatus: Operational"

def get_connection():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME
    )
    register_vector(conn)
    return conn

def generate_data():
    print("🚀 Starting complex data generation...")
    
    # 1. Load Model
    print("📦 Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    kg = KnowledgeGenerator()
    
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Clear existing data
        print("🧹 Clearing old data...")
        cur.execute("TRUNCATE sensors, sensor_readings, sensor_knowledge CASCADE;")
        
        # Create mock_data directory
        print(f"📂 Creating {MOCK_DATA_DIR} directory...")
        os.makedirs(MOCK_DATA_DIR, exist_ok=True)
        
        # 2. Generate Buildings & Locations
        buildings = [
            {"name": "Building A", "desc": "Main manufacturing plant. Heavy machinery and high vibration zones."},
            {"name": "Building B", "desc": "R&D Laboratory. Climate controlled, sensitive instruments."},
            {"name": "Server Farm", "desc": "Data center. High cooling requirements, backup power systems."},
            {"name": "Warehouse", "desc": "Storage facility. Ambient temperature monitoring, large open spaces."}
        ]
        
        # 3. Generate Sensors
        print(f"Creating {NUM_SENSORS} sensors with rich documentation...")
        sensor_ids = []
        sensors_by_building = {b['name']: [] for b in buildings}
        
        for i in range(NUM_SENSORS):
            s_id = f"s{i:03d}"
            sensor_ids.append(s_id)
            
            building = random.choice(buildings)
            sensors_by_building[building['name']].append(s_id)
            
            s_type = random.choice(["temperature", "pressure", "vibration", "humidity"])
            s_name = f"{building['name']} {s_type.title()} Monitor {i}"
            model_num = f"XG-{random.randint(1000, 9999)}"
            
            # Insert Sensor
            cur.execute(
                "INSERT INTO sensors (id, name, type, location) VALUES (%s, %s, %s, %s)",
                (s_id, s_name, s_type, building['name'])
            )
            
            # --- Generate Sensor-Specific Knowledge ---
            docs = []
            
            # 1. Sensor Datasheet (Technical Specs)
            doc = kg.generate_sensor_datasheet(s_type, model_num)
            docs.append(doc)
            fname = f"{MOCK_DATA_DIR}/{s_id}_datasheet.txt"
            with open(fname, "w") as f:
                f.write(doc)
            
            # 2. Position/Installation Document
            doc = kg.generate_position_doc(s_name, building['name'])
            docs.append(doc)
            fname = f"{MOCK_DATA_DIR}/{s_id}_position.txt"
            with open(fname, "w") as f:
                f.write(doc)
            
            # 3. Maintenance Log (Randomly add 0-2 logs)
            for log_idx in range(random.randint(0, 2)):
                doc = kg.generate_maintenance_log(s_name)
                docs.append(doc)
                fname = f"{MOCK_DATA_DIR}/{s_id}_maintenance_{log_idx}.txt"
                with open(fname, "w") as f:
                    f.write(doc)
            
            # Insert sensor docs
            for content in docs:
                embedding = model.encode(content).tolist()
                cur.execute(
                    "INSERT INTO sensor_knowledge (sensor_id, content, embedding) VALUES (%s, %s, %s)",
                    (s_id, content, embedding)
                )

        # 4. Generate Building Knowledge (Guaranteed Coverage)
        print("Generating comprehensive building documentation...")
        doc_types = ['safety', 'hvac', 'security', 'structural']
        
        for building in buildings:
            b_name = building['name']
            b_desc = building['desc']
            b_sensors = sensors_by_building[b_name]
            
            if not b_sensors:
                print(f"⚠️ Warning: No sensors in {b_name}, skipping docs.")
                continue
                
            for d_type in doc_types:
                # Generate specific doc type
                if d_type == 'safety':
                    doc = kg._generate_safety_manual(b_name, b_desc)
                elif d_type == 'hvac':
                    doc = kg._generate_hvac_spec(b_name, b_desc)
                elif d_type == 'security':
                    doc = kg._generate_security_policy(b_name, b_desc)
                else:
                    doc = kg._generate_structural_report(b_name, b_desc)
                
                # Assign to a random sensor in this building (to satisfy FK)
                target_sensor = random.choice(b_sensors)
                
                # Save file
                safe_b_name = b_name.replace(" ", "_")
                fname = f"{MOCK_DATA_DIR}/{safe_b_name}_{d_type}.txt"
                with open(fname, "w") as f:
                    f.write(doc)
                
                # Insert into DB
                embedding = model.encode(doc).tolist()
                cur.execute(
                    "INSERT INTO sensor_knowledge (sensor_id, content, embedding) VALUES (%s, %s, %s)",
                    (target_sensor, doc, embedding)
                )

        # 5. Generate Readings (Sine waves with noise)
        print(f"Generating {NUM_SENSORS * READINGS_PER_SENSOR} readings...")
        for s_id in sensor_ids:
            # Create a unique pattern for this sensor
            period = random.uniform(10, 50)
            phase = random.uniform(0, 6.28)
            base_val = random.uniform(20, 80)
            
            for j in range(READINGS_PER_SENSOR):
                t = START_TIME + timedelta(hours=j)
                # Sine wave + random noise
                val = base_val + 10 * math.sin((j / period) * 2 * math.pi + phase) + random.uniform(-1, 1)
                
                # Inject anomaly
                if random.random() < 0.01:
                    val += random.uniform(20, 50) # Spike
                
                cur.execute(
                    "INSERT INTO sensor_readings (sensor_id, value, timestamp) VALUES (%s, %s, %s)",
                    (s_id, val, t)
                )

        conn.commit()
        print("✅ Complex data generation complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    generate_data()
