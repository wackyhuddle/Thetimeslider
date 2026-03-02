import sqlite3

conn   = sqlite3.connect("history.db")
cursor = conn.cursor()

# All British/English rulers from Anglo-Saxon era to present
# Format: (ruler name, start year, end year)
UK_RULERS = [

    # --- EARLY ANGLO-SAXON KINGS OF ENGLAND ---
    ("Egbert of Wessex",                    827,  839),
    ("Æthelwulf of Wessex",                 839,  858),
    ("Æthelbald of Wessex",                 858,  860),
    ("Æthelberht of Wessex",                860,  865),
    ("Æthelred I of Wessex",                865,  871),
    ("Alfred the Great",                    871,  899),
    ("Edward the Elder",                    899,  924),
    ("Æthelstan",                           924,  939),
    ("Edmund I",                            939,  946),
    ("Eadred",                              946,  955),
    ("Eadwig",                              955,  959),
    ("Edgar the Peaceful",                  959,  975),
    ("Edward the Martyr",                   975,  978),
    ("Æthelred the Unready",                978, 1013),

    # --- DANISH RULE ---
    ("Sweyn Forkbeard",                    1013, 1014),
    ("Æthelred the Unready (restored)",    1014, 1016),
    ("Edmund Ironside",                    1016, 1016),
    ("Cnut the Great",                     1016, 1035),
    ("Harold Harefoot",                    1035, 1040),
    ("Harthacnut",                         1040, 1042),

    # --- LATE ANGLO-SAXON ---
    ("Edward the Confessor",               1042, 1066),
    ("Harold II",                          1066, 1066),

    # --- NORMANS ---
    ("William I (the Conqueror)",          1066, 1087),
    ("William II (Rufus)",                 1087, 1100),
    ("Henry I",                            1100, 1135),
    ("Stephen",                            1135, 1154),

    # --- PLANTAGENETS ---
    ("Henry II",                           1154, 1189),
    ("Richard I (the Lionheart)",          1189, 1199),
    ("John",                               1199, 1216),
    ("Henry III",                          1216, 1272),
    ("Edward I",                           1272, 1307),
    ("Edward II",                          1307, 1327),
    ("Edward III",                         1327, 1377),
    ("Richard II",                         1377, 1399),

    # --- LANCASTER ---
    ("Henry IV",                           1399, 1413),
    ("Henry V",                            1413, 1422),
    ("Henry VI",                           1422, 1461),

    # --- YORK ---
    ("Edward IV",                          1461, 1483),
    ("Edward V",                           1483, 1483),
    ("Richard III",                        1483, 1485),

    # --- TUDORS ---
    ("Henry VII",                          1485, 1509),
    ("Henry VIII",                         1509, 1547),
    ("Edward VI",                          1547, 1553),
    ("Lady Jane Grey",                     1553, 1553),
    ("Mary I",                             1553, 1558),
    ("Elizabeth I",                        1558, 1603),

    # --- STUARTS ---
    ("James I",                            1603, 1625),
    ("Charles I",                          1625, 1649),

    # --- COMMONWEALTH / INTERREGNUM ---
    ("Oliver Cromwell (Lord Protector)",   1649, 1658),
    ("Richard Cromwell (Lord Protector)",  1658, 1659),

    # --- STUARTS RESTORED ---
    ("Charles II",                         1660, 1685),
    ("James II",                           1685, 1688),
    ("William III & Mary II",              1689, 1694),
    ("William III",                        1694, 1702),
    ("Anne",                               1702, 1714),

    # --- HANOVERIANS ---
    ("George I",                           1714, 1727),
    ("George II",                          1727, 1760),
    ("George III",                         1760, 1820),
    ("George IV",                          1820, 1830),
    ("William IV",                         1830, 1837),
    ("Victoria",                           1837, 1901),

    # --- SAXE-COBURG AND GOTHA ---
    ("Edward VII",                         1901, 1910),

    # --- WINDSORS ---
    ("George V",                           1910, 1936),
    ("Edward VIII",                        1936, 1936),
    ("George VI",                          1936, 1952),
    ("Elizabeth II",                       1952, 2022),
    ("Charles III",                        2022, 2029),
]

# Get UK location ID
cursor.execute("SELECT id FROM locations WHERE name = 'United Kingdom'")
row = cursor.fetchone()
if not row:
    print("ERROR: 'United Kingdom' not found in locations table.")
    cursor.execute("SELECT name FROM locations WHERE name LIKE '%United%' OR name LIKE '%Britain%'")
    for r in cursor.fetchall():
        print(f"  Found: {r[0]}")
    conn.close()
    exit()

uk_id = row[0]
print(f"Found United Kingdom (id={uk_id})")

# Insert a row for every year of every reign
inserted = 0
for name, start, end in UK_RULERS:
    for year in range(start, end + 1):
        cursor.execute(
            "SELECT id FROM history WHERE location_id=? AND year=?",
            (uk_id, year)
        )
        if cursor.fetchone():
            cursor.execute(
                "UPDATE history SET ruler=? WHERE location_id=? AND year=?",
                (name, uk_id, year)
            )
        else:
            cursor.execute(
                "INSERT INTO history (location_id, year, ruler) VALUES (?,?,?)",
                (uk_id, year, name)
            )
        inserted += 1

conn.commit()

# Spot checks
print(f"\nInserted/updated {inserted} year entries.")
print("\nSpot checks:")
for test_year, expected in [
    (871,  "Alfred the Great"),
    (1066, "William I"),
    (1215, "John"),
    (1530, "Henry VIII"),
    (1588, "Elizabeth I"),
    (1805, "George III"),
    (1850, "Victoria"),
    (1940, "George VI"),
    (1990, "Elizabeth II"),
    (2023, "Charles III"),
]:
    cursor.execute(
        "SELECT ruler FROM history WHERE location_id=? AND year=?",
        (uk_id, test_year)
    )
    r = cursor.fetchone()
    result = r[0] if r else "Not found"
    status = "✓" if expected in (result or "") else "?"
    print(f"  {status} {test_year}: {result}")

conn.close()
print("\nDone! All UK rulers added to the database.")