#!/user/bin/python3

import bcrypt
import uuid
import sqlite3
import os

# ---- Paths ----
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(SCRIPT_DIR, '..', 'schema.sql')
INITIAL_DATA_PATH = os.path.join(SCRIPT_DIR, 'initial_data.sql')
DB_PATH = os.path.join(SCRIPT_DIR, 'test.db')

# ---- Helper ----
def uid():
    return str(uuid.uuid4())

def section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def show(cursor, query, params=()):
    cursor.execute(query, params)
    rows = cursor.fetchall()
    if not rows:
        print("  (no results)")
    for row in rows:
        print(f"  {row}")

# ================================================================
# SETUP — schema + initial data
# ================================================================
section("SETUP — Creating schema and initial data")

# Generate hashes
admin_hash = bcrypt.hashpw(b'admin1234', bcrypt.gensalt()).decode()
alice_hash = bcrypt.hashpw(b'alice1234', bcrypt.gensalt()).decode()
bob_hash   = bcrypt.hashpw(b'bob1234',   bcrypt.gensalt()).decode()

# Fixed IDs for traceability
ADMIN_ID  = '36c9050e-ddd3-4c3b-9731-9f487208bbc1'
ALICE_ID  = uid()
BOB_ID    = uid()
PLACE1_ID = uid()  # owned by Alice
PLACE2_ID = uid()  # owned by Bob
REVIEW_ID = uid()  # written by Bob on Alice's place
WIFI_ID   = uid()
POOL_ID   = uid()
AC_ID     = uid()

initial_data_sql = f"""
INSERT INTO users (id, first_name, last_name, email, password, is_admin) VALUES
    ('{ADMIN_ID}', 'Admin', 'HBnB', 'admin@hbnb.io', '{admin_hash}', TRUE),
    ('{ALICE_ID}', 'Alice', 'Smith', 'alice@hbnb.io', '{alice_hash}', FALSE),
    ('{BOB_ID}',   'Bob',   'Jones', 'bob@hbnb.io',   '{bob_hash}',   FALSE);

INSERT INTO amenities (id, name) VALUES
    ('{WIFI_ID}', 'WiFi'),
    ('{POOL_ID}', 'Swimming Pool'),
    ('{AC_ID}',   'Air Conditioning');

INSERT INTO places (id, title, description, price, latitude, longitude, owner_id) VALUES
    ('{PLACE1_ID}', 'Alice Cottage',  'A cozy cottage by the sea', 85.00,  48.8566,  2.3522, '{ALICE_ID}'),
    ('{PLACE2_ID}', 'Bob Apartment',  'A modern flat downtown',    120.00, 51.5074, -0.1278, '{BOB_ID}');

-- Alice's place has WiFi + Pool, Bob's place has WiFi + AC
INSERT INTO place_amenity (place_id, amenity_id) VALUES
    ('{PLACE1_ID}', '{WIFI_ID}'),
    ('{PLACE1_ID}', '{POOL_ID}'),
    ('{PLACE2_ID}', '{WIFI_ID}'),
    ('{PLACE2_ID}', '{AC_ID}');

-- Bob reviews Alice's place
INSERT INTO reviews (id, text, rating, user_id, place_id) VALUES
    ('{REVIEW_ID}', 'Lovely place, very peaceful!', 5, '{BOB_ID}', '{PLACE1_ID}');
"""

# Write initial_data.sql
with open(INITIAL_DATA_PATH, 'w') as f:
    f.write(initial_data_sql)
print("✓ initial_data.sql written")

# Create test.db and apply schema
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("✓ Old test.db removed")

conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")  # enable FK constraints in SQLite
cur = conn.cursor()

with open(SCHEMA_PATH, 'r') as f:
    conn.executescript(f.read())
print("✓ schema.sql applied")

conn.executescript(initial_data_sql)
conn.commit()
print("✓ Initial data inserted")

# ================================================================
# READ — verify all data
# ================================================================
section("READ — All users")
show(cur, "SELECT id, first_name, email, is_admin FROM users;")

section("READ — All places")
show(cur, "SELECT id, title, price, owner_id FROM places;")

section("READ — All amenities")
show(cur, "SELECT id, name FROM amenities;")

section("READ — Place/Amenity relationships")
show(cur, """
    SELECT p.title, a.name
    FROM place_amenity pa
    JOIN places p ON pa.place_id = p.id
    JOIN amenities a ON pa.amenity_id = a.id
    ORDER BY p.title;
""")

section("READ — All reviews")
show(cur, """
    SELECT r.text, r.rating, u.first_name AS reviewer, p.title AS place
    FROM reviews r
    JOIN users u ON r.user_id = u.id
    JOIN places p ON r.place_id = p.id;
""")

# ================================================================
# UPDATE
# ================================================================
section("UPDATE — Alice's place price (85 -> 95)")
cur.execute("UPDATE places SET price = 95.00 WHERE id = ?", (PLACE1_ID,))
conn.commit()
show(cur, "SELECT title, price FROM places WHERE id = ?", (PLACE1_ID,))

section("UPDATE — Bob's review rating (5 -> 4) and text")
cur.execute("""
    UPDATE reviews SET rating = 4, text = 'Great place, but a bit noisy.'
    WHERE id = ?
""", (REVIEW_ID,))
conn.commit()
show(cur, "SELECT text, rating FROM reviews WHERE id = ?", (REVIEW_ID,))

section("UPDATE — Alice's last name (Smith -> Dupont)")
cur.execute("UPDATE users SET last_name = 'Dupont' WHERE id = ?", (ALICE_ID,))
conn.commit()
show(cur, "SELECT first_name, last_name, email FROM users WHERE id = ?", (ALICE_ID,))

# ================================================================
# DELETE — Delete Alice, observe cascades
# ================================================================
section("DELETE — Deleting Alice (owner of Place1, which has reviews)")
print("  Before delete:")
print("  Places:")
show(cur, "SELECT title, owner_id FROM places;")
print("  Reviews:")
show(cur, "SELECT text, place_id FROM reviews;")
print("  Place/Amenity links:")
show(cur, "SELECT place_id, amenity_id FROM place_amenity;")

cur.execute("DELETE FROM users WHERE id = ?", (ALICE_ID,))
conn.commit()
print("\n  After delete:")

section("READ — Users (Alice should be gone)")
show(cur, "SELECT first_name, email FROM users;")

section("READ — Places (Alice's cottage should be gone)")
show(cur, "SELECT title, owner_id FROM places;")

section("READ — Reviews (Bob's review on Alice's place should be gone)")
show(cur, "SELECT text, rating FROM reviews;")

section("READ — Place/Amenity links (Alice's place links should be gone)")
show(cur, "SELECT place_id, amenity_id FROM place_amenity;")

section("READ — Amenities (should be untouched)")
show(cur, "SELECT name FROM amenities;")

conn.close()
print("\n✓ All tests completed!")
