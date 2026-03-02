import sqlite3

conn   = sqlite3.connect("history.db")
cursor = conn.cursor()

# All 47 US Presidents with their term start and end years
PRESIDENTS = [
    ("George Washington",       1789, 1797),
    ("John Adams",              1797, 1801),
    ("Thomas Jefferson",        1801, 1809),
    ("James Madison",           1809, 1817),
    ("James Monroe",            1817, 1825),
    ("John Quincy Adams",       1825, 1829),
    ("Andrew Jackson",          1829, 1837),
    ("Martin Van Buren",        1837, 1841),
    ("William Henry Harrison",  1841, 1841),
    ("John Tyler",              1841, 1845),
    ("James K. Polk",           1845, 1849),
    ("Zachary Taylor",          1849, 1850),
    ("Millard Fillmore",        1850, 1853),
    ("Franklin Pierce",         1853, 1857),
    ("James Buchanan",          1857, 1861),
    ("Abraham Lincoln",         1861, 1865),
    ("Andrew Johnson",          1865, 1869),
    ("Ulysses S. Grant",        1869, 1877),
    ("Rutherford B. Hayes",     1877, 1881),
    ("James A. Garfield",       1881, 1881),
    ("Chester A. Arthur",       1881, 1885),
    ("Grover Cleveland",        1885, 1889),
    ("Benjamin Harrison",       1889, 1893),
    ("Grover Cleveland",        1893, 1897),
    ("William McKinley",        1897, 1901),
    ("Theodore Roosevelt",      1901, 1909),
    ("William Howard Taft",     1909, 1913),
    ("Woodrow Wilson",          1913, 1921),
    ("Warren G. Harding",       1921, 1923),
    ("Calvin Coolidge",         1923, 1929),
    ("Herbert Hoover",          1929, 1933),
    ("Franklin D. Roosevelt",   1933, 1945),
    ("Harry S. Truman",         1945, 1953),
    ("Dwight D. Eisenhower",    1953, 1961),
    ("John F. Kennedy",         1961, 1963),
    ("Lyndon B. Johnson",       1963, 1969),
    ("Richard Nixon",           1969, 1974),
    ("Gerald Ford",             1974, 1977),
    ("Jimmy Carter",            1977, 1981),
    ("Ronald Reagan",           1981, 1989),
    ("George H.W. Bush",        1989, 1993),
    ("Bill Clinton",            1993, 2001),
    ("George W. Bush",          2001, 2009),
    ("Barack Obama",            2009, 2017),
    ("Donald Trump",            2017, 2021),
    ("Joe Biden",               2021, 2025),
    ("Donald Trump",            2025, 2029),
]

# Get the United States location ID
cursor.execute("SELECT id FROM locations WHERE name = 'United States'")
row = cursor.fetchone()
if not row:
    print("ERROR: 'United States' not found in locations table.")
    print("Available locations:")
    cursor.execute("SELECT name FROM locations WHERE name LIKE '%United%'")
    for r in cursor.fetchall():
        print(f"  {r[0]}")
    conn.close()
    exit()

us_id = row[0]
print(f"Found United States (id={us_id})")

# Insert a row for every year of every presidency
inserted = 0
for name, start, end in PRESIDENTS:
    for year in range(start, end + 1):
        cursor.execute(
            "SELECT id FROM history WHERE location_id=? AND year=?",
            (us_id, year)
        )
        if cursor.fetchone():
            cursor.execute(
                "UPDATE history SET ruler=? WHERE location_id=? AND year=?",
                (name, us_id, year)
            )
        else:
            cursor.execute(
                "INSERT INTO history (location_id, year, ruler) VALUES (?,?,?)",
                (us_id, year, name)
            )
        inserted += 1

conn.commit()

# Verify
print(f"\nInserted/updated {inserted} year entries.")
print("\nSpot checks:")
for test_year in [1789, 1865, 1933, 1963, 2001, 2020, 2025]:
    cursor.execute("""
        SELECT h.ruler FROM history h
        WHERE h.location_id=? AND h.year=?
    """, (us_id, test_year))
    r = cursor.fetchone()
    print(f"  {test_year}: {r[0] if r else 'Not found'}")

conn.close()
print("\nDone! All US presidents added to the database.")