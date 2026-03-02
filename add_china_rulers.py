import sqlite3

conn   = sqlite3.connect("history.db")
cursor = conn.cursor()

# All major Chinese rulers organized by dynasty
# Format: (ruler name, start year, end year)
# Negative years = BC
CHINA_RULERS = [

    # --- LEGENDARY / XIA DYNASTY ---
    ("Emperor Yao (Legendary)",         -2356, -2255),
    ("Emperor Shun (Legendary)",        -2255, -2205),
    ("Yu the Great (Xia Dynasty)",      -2205, -2197),

    # --- SHANG DYNASTY ---
    ("Tang of Shang",                   -1600, -1588),
    ("Emperor Zhòu (Shang)",            -1075, -1046),

    # --- ZHOU DYNASTY ---
    ("King Wu of Zhou",                 -1046, -1043),
    ("King Cheng of Zhou",              -1042,  -1021),
    ("King Xuan of Zhou",                -827,   -782),
    ("King You of Zhou",                 -781,   -771),

    # --- QIN DYNASTY ---
    ("Qin Shi Huang (First Emperor)",    -221,   -210),
    ("Qin Er Shi",                       -210,   -207),

    # --- HAN DYNASTY ---
    ("Emperor Gaozu (Liu Bang)",         -206,   -195),
    ("Emperor Hui of Han",               -195,   -188),
    ("Emperor Wen of Han",               -180,   -157),
    ("Emperor Jing of Han",              -157,   -141),
    ("Emperor Wu of Han",                -141,    -87),
    ("Emperor Xuan of Han",               -74,    -49),
    ("Emperor Yuan of Han",               -49,    -33),
    ("Emperor Cheng of Han",              -33,     -7),
    ("Emperor Ai of Han",                  -7,     -1),

    # --- XIN DYNASTY ---
    ("Wang Mang",                            9,    23),

    # --- EASTERN HAN ---
    ("Emperor Guangwu of Han",              25,    57),
    ("Emperor Ming of Han",                 57,    75),
    ("Emperor Zhang of Han",                75,    88),
    ("Emperor He of Han",                   88,   105),
    ("Emperor Xian of Han",                189,   220),

    # --- THREE KINGDOMS ---
    ("Cao Cao (Wei)",                       220,   226),
    ("Liu Bei (Shu Han)",                   221,   223),
    ("Sun Quan (Wu)",                       222,   252),

    # --- JIN DYNASTY ---
    ("Emperor Wu of Jin",                   265,   290),
    ("Emperor Hui of Jin",                  290,   306),

    # --- SUI DYNASTY ---
    ("Emperor Wen of Sui",                  581,   604),
    ("Emperor Yang of Sui",                 604,   618),

    # --- TANG DYNASTY ---
    ("Emperor Gaozu of Tang",               618,   626),
    ("Emperor Taizong of Tang",             626,   649),
    ("Emperor Gaozong of Tang",             649,   683),
    ("Empress Wu Zetian",                   690,   705),
    ("Emperor Xuanzong of Tang",            712,   756),
    ("Emperor Suzong of Tang",              756,   762),
    ("Emperor Daizong of Tang",             762,   779),
    ("Emperor Dezong of Tang",              779,   805),
    ("Emperor Xuanzong II of Tang",         846,   859),
    ("Emperor Xizong of Tang",              873,   888),
    ("Emperor Zhaozong of Tang",            888,   904),

    # --- FIVE DYNASTIES ---
    ("Emperor Taizu of Later Liang",        907,   912),
    ("Emperor Zhuangzong (Later Tang)",     923,   926),

    # --- SONG DYNASTY ---
    ("Emperor Taizu of Song",               960,   976),
    ("Emperor Taizong of Song",             976,   997),
    ("Emperor Zhenzong of Song",            997,  1022),
    ("Emperor Renzong of Song",            1022,  1063),
    ("Emperor Yingzong of Song",           1063,  1067),
    ("Emperor Shenzong of Song",           1067,  1085),
    ("Emperor Zhezong of Song",            1085,  1100),
    ("Emperor Huizong of Song",            1100,  1125),
    ("Emperor Gaozong of Song",            1127,  1162),
    ("Emperor Xiaozong of Song",           1162,  1189),
    ("Emperor Ningzong of Song",           1194,  1224),
    ("Emperor Lizong of Song",             1224,  1264),

    # --- YUAN DYNASTY (Mongol) ---
    ("Kublai Khan",                        1271,  1294),
    ("Emperor Chengzong of Yuan",          1294,  1307),
    ("Emperor Renzong of Yuan",            1311,  1320),
    ("Emperor Shundi of Yuan",             1333,  1368),

    # --- MING DYNASTY ---
    ("Emperor Hongwu (Zhu Yuanzhang)",     1368,  1398),
    ("Emperor Jianwen",                    1398,  1402),
    ("Emperor Yongle",                     1402,  1424),
    ("Emperor Hongxi",                     1424,  1425),
    ("Emperor Xuande",                     1425,  1435),
    ("Emperor Zhengtong",                  1435,  1449),
    ("Emperor Jingtai",                    1449,  1457),
    ("Emperor Tianshun",                   1457,  1464),
    ("Emperor Chenghua",                   1464,  1487),
    ("Emperor Hongzhi",                    1487,  1505),
    ("Emperor Zhengde",                    1505,  1521),
    ("Emperor Jiajing",                    1521,  1567),
    ("Emperor Longqing",                   1567,  1572),
    ("Emperor Wanli",                      1572,  1620),
    ("Emperor Taichang",                   1620,  1620),
    ("Emperor Tianqi",                     1620,  1627),
    ("Emperor Chongzhen",                  1627,  1644),

    # --- QING DYNASTY ---
    ("Emperor Shunzhi",                    1644,  1661),
    ("Emperor Kangxi",                     1661,  1722),
    ("Emperor Yongzheng",                  1722,  1735),
    ("Emperor Qianlong",                   1735,  1796),
    ("Emperor Jiaqing",                    1796,  1820),
    ("Emperor Daoguang",                   1820,  1850),
    ("Emperor Xianfeng",                   1850,  1861),
    ("Emperor Tongzhi",                    1861,  1875),
    ("Emperor Guangxu",                    1875,  1908),
    ("Emperor Xuantong (Puyi)",            1908,  1912),

    # --- REPUBLIC OF CHINA ---
    ("Sun Yat-sen (Provisional President)", 1912, 1912),
    ("Yuan Shikai",                         1912, 1916),
    ("Li Yuanhong",                         1916, 1917),
    ("Xu Shichang",                         1918, 1922),
    ("Chiang Kai-shek",                     1928, 1949),

    # --- PEOPLE'S REPUBLIC OF CHINA ---
    ("Mao Zedong",                          1949, 1976),
    ("Hua Guofeng",                         1976, 1978),
    ("Deng Xiaoping",                       1978, 1989),
    ("Jiang Zemin",                         1989, 2002),
    ("Hu Jintao",                           2002, 2012),
    ("Xi Jinping",                          2012, 2029),
]

# Get China location ID
cursor.execute("SELECT id FROM locations WHERE name = 'China'")
row = cursor.fetchone()
if not row:
    print("ERROR: 'China' not found in locations table.")
    cursor.execute("SELECT name FROM locations WHERE name LIKE '%China%' OR name LIKE '%chin%'")
    for r in cursor.fetchall():
        print(f"  Found: {r[0]}")
    conn.close()
    exit()

china_id = row[0]
print(f"Found China (id={china_id})")

# Insert a row for every year of every reign
inserted = 0
for name, start, end in CHINA_RULERS:
    for year in range(start, end + 1):
        cursor.execute(
            "SELECT id FROM history WHERE location_id=? AND year=?",
            (china_id, year)
        )
        if cursor.fetchone():
            cursor.execute(
                "UPDATE history SET ruler=? WHERE location_id=? AND year=?",
                (name, china_id, year)
            )
        else:
            cursor.execute(
                "INSERT INTO history (location_id, year, ruler) VALUES (?,?,?)",
                (china_id, year, name)
            )
        inserted += 1

conn.commit()

# Spot checks
print(f"\nInserted/updated {inserted} year entries.")
print("\nSpot checks:")
for test_year, expected in [
    (-221, "Qin Shi Huang"),
    (0,    "Emperor Cheng of Han"),
    (700,  "Empress Wu Zetian"),
    (1280, "Kublai Khan"),
    (1450, "Emperor Zhengtong"),
    (1750, "Emperor Qianlong"),
    (1900, "Emperor Guangxu"),
    (1950, "Mao Zedong"),
    (2020, "Xi Jinping"),
]:
    cursor.execute(
        "SELECT ruler FROM history WHERE location_id=? AND year=?",
        (china_id, test_year)
    )
    r = cursor.fetchone()
    result = r[0] if r else "Not found"
    status = "✓" if expected in (result or "") else "?"
    print(f"  {status} {test_year}: {result}")

conn.close()
print("\nDone! All Chinese rulers added to the database.")