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

# Initialize Faker
fake = Faker()

# Connection settings (same as main_server.py)
DB_HOST = os.environ.get("POSTGRES_HOST", "localhost")
DB_PORT = os.environ.get("POSTGRES_PORT", "5432")
DB_USER = os.environ.get("POSTGRES_USER", "mcp_user")
DB_PASS = os.environ.get("POSTGRES_PASSWORD", "mcp_password")
DB_NAME = os.environ.get("POSTGRES_DB", "mcp_db")

def get_connection():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS, dbname=DB_NAME
    )
    register_vector(conn)
    return conn

def generate_data():
    print("🚀 Starting data generation...")
    
    # 1. Load Model
    print("📦 Loading embedding model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Clear existing data
        print("🧹 Clearing old data...")
        cur.execute("TRUNCATE sensors, sensor_readings, sensor_knowledge CASCADE;")
        
        # 2. Generate Buildings & Locations
        buildings = [
            {"name": "Building A", "desc": "Main manufacturing plant. Heavy machinery and high vibration zones."},
            {"name": "Building B", "desc": "R&D Laboratory. Climate controlled, sensitive instruments."},
            {"name": "Server Farm", "desc": "Data center. High cooling requirements, backup power systems."},
            {"name": "Warehouse", "desc": "Storage facility. Ambient temperature monitoring, large open spaces."}
        ]
        
        # 3. Generate Sensors
        print(f"Creating {NUM_SENSORS} sensors...")
        sensor_ids = []
        
        for i in range(NUM_SENSORS):
            s_id = f"s{i:03d}"
            sensor_ids.append(s_id)
            
            building = random.choice(buildings)
            s_type = random.choice(["temperature", "pressure", "vibration", "humidity"])
            s_name = f"{building['name']} {s_type.title()} Monitor {i}"
            
            cur.execute(
                "INSERT INTO sensors (id, name, type, location) VALUES (%s, %s, %s, %s)",
                (s_id, s_name, s_type, building['name'])
            )
            
            # 4. Add Knowledge (Building Info + Sensor Manuals)
            # Add building info to the first sensor of that building (or random ones)
            if random.random() < 0.3:
                content = f"Location Info: {building['name']}. {building['desc']}"
                embedding = model.encode(content).tolist()
                cur.execute(
                    "INSERT INTO sensor_knowledge (sensor_id, content, embedding) VALUES (%s, %s, %s)",
                    (s_id, content, embedding)
                )

            # Add specific technical knowledge
            if random.random() < 0.5:
                issue = fake.sentence(nb_words=10)
                action = fake.sentence(nb_words=8)
                content = f"Maintenance Log: {issue} Resolution: {action}"
                embedding = model.encode(content).tolist()
                cur.execute(
                    "INSERT INTO sensor_knowledge (sensor_id, content, embedding) VALUES (%s, %s, %s)",
                    (s_id, content, embedding)
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
        print("✅ Data generation complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    generate_data()
