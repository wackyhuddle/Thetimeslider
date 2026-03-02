import sqlite3

conn   = sqlite3.connect("history.db")
cursor = conn.cursor()

# ─── GREECE ───────────────────────────────────────────────────────────────────

GREECE_RULERS = [

    # --- MYCENAEAN / LEGENDARY ---
    ("Agamemnon (Mycenaean King, legendary)",   -1250, -1200),

    # --- ARCHAIC ATHENS (Archons) ---
    ("Draco (Archon of Athens)",                 -621,  -620),
    ("Solon (Archon of Athens)",                 -594,  -593),
    ("Peisistratos (Tyrant of Athens)",          -561,  -527),
    ("Hippias (Tyrant of Athens)",               -527,  -510),
    ("Cleisthenes (Archon of Athens)",           -508,  -507),

    # --- CLASSICAL ATHENS ---
    ("Themistocles",                             -493,  -471),
    ("Pericles",                                 -461,  -429),
    ("Cleon",                                    -429,  -422),
    ("Alcibiades",                               -420,  -404),
    ("Critias (Thirty Tyrants)",                 -404,  -403),

    # --- SPARTA ---
    ("Leonidas I (King of Sparta)",              -489,  -480),
    ("Lysander (Spartan commander)",             -405,  -395),
    ("Agesilaus II (King of Sparta)",            -400,  -360),

    # --- MACEDONIAN EMPIRE ---
    ("Philip II of Macedon",                     -359,  -336),
    ("Alexander the Great",                      -336,  -323),
    ("Cassander (Macedonia)",                    -305,  -297),
    ("Demetrius I (Macedonia)",                  -294,  -288),
    ("Antigonus II Gonatas (Macedonia)",         -276,  -239),
    ("Philip V of Macedon",                      -221,  -179),
    ("Perseus of Macedon",                       -179,  -168),

    # --- ROMAN PROVINCE ---
    ("Roman Province of Macedonia/Achaea",       -146,   284),

    # --- BYZANTINE (Eastern Roman) ---
    ("Constantine I (Byzantine)",                 284,   337),
    ("Constantius II",                            337,   361),
    ("Julian the Apostate",                       361,   363),
    ("Theodosius I",                              379,   395),
    ("Arcadius",                                  395,   408),
    ("Theodosius II",                             408,   450),
    ("Marcian",                                   450,   457),
    ("Leo I",                                     457,   474),
    ("Zeno",                                      474,   491),
    ("Anastasius I",                              491,   518),
    ("Justin I",                                  518,   527),
    ("Justinian I (the Great)",                   527,   565),
    ("Justin II",                                 565,   578),
    ("Tiberius II",                               578,   582),
    ("Maurice",                                   582,   602),
    ("Phocas",                                    602,   610),
    ("Heraclius",                                 610,   641),
    ("Constans II",                               641,   668),
    ("Constantine IV",                            668,   685),
    ("Justinian II",                              685,   695),
    ("Leontios",                                  695,   698),
    ("Tiberius III",                              698,   705),
    ("Justinian II (restored)",                   705,   711),
    ("Philippicus",                               711,   713),
    ("Anastasius II",                             713,   715),
    ("Theodosius III",                            715,   717),
    ("Leo III the Isaurian",                      717,   741),
    ("Constantine V",                             741,   775),
    ("Leo IV",                                    775,   780),
    ("Constantine VI",                            780,   797),
    ("Irene of Athens (Empress)",                 797,   802),
    ("Nikephoros I",                              802,   811),
    ("Michael I",                                 811,   813),
    ("Leo V the Armenian",                        813,   820),
    ("Michael II",                                820,   829),
    ("Theophilos",                                829,   842),
    ("Michael III",                               842,   867),
    ("Basil I the Macedonian",                    867,   886),
    ("Leo VI the Wise",                           886,   912),
    ("Constantine VII",                           913,   959),
    ("Romanos II",                                959,   963),
    ("Nikephoros II Phokas",                      963,   969),
    ("John I Tzimiskes",                          969,   976),
    ("Basil II (the Bulgar Slayer)",              976,  1025),
    ("Constantine VIII",                         1025,  1028),
    ("Romanos III Argyros",                      1028,  1034),
    ("Michael IV",                               1034,  1041),
    ("Constantine IX Monomachos",                1042,  1055),
    ("Theodora (Empress)",                       1055,  1056),
    ("Michael VI",                               1056,  1057),
    ("Isaac I Komnenos",                         1057,  1059),
    ("Constantine X Doukas",                     1059,  1067),
    ("Romanos IV Diogenes",                      1068,  1071),
    ("Michael VII Doukas",                       1071,  1078),
    ("Nikephoros III",                           1078,  1081),
    ("Alexios I Komnenos",                       1081,  1118),
    ("John II Komnenos",                         1118,  1143),
    ("Manuel I Komnenos",                        1143,  1180),
    ("Alexios II Komnenos",                      1180,  1183),
    ("Andronikos I Komnenos",                    1183,  1185),
    ("Isaac II Angelos",                         1185,  1195),
    ("Alexios III Angelos",                      1195,  1203),
    ("Alexios IV Angelos",                       1203,  1204),

    # --- LATIN EMPIRE / FRAGMENTATION ---
    ("Baldwin I (Latin Emperor)",                1204,  1205),
    ("Henry of Flanders",                        1206,  1216),

    # --- OTTOMAN RULE ---
    ("Mehmed II (Ottoman)",                      1453,  1481),
    ("Ottoman Empire (Greece)",                  1481,  1821),

    # --- MODERN GREECE ---
    ("Ioannis Kapodistrias (First Governor)",    1827,  1831),
    ("Otto I (King of Greece)",                  1832,  1862),
    ("George I (King of Greece)",                1863,  1913),
    ("Constantine I (King of Greece)",           1913,  1917),
    ("Alexander (King of Greece)",               1917,  1920),
    ("Constantine I (restored)",                 1920,  1922),
    ("George II (King of Greece)",               1922,  1924),
    ("Pavlos Kountouriotis (President)",         1924,  1929),
    ("Eleftherios Venizelos (PM)",               1928,  1932),
    ("George II (restored)",                     1935,  1941),
    ("Axis Occupation of Greece",                1941,  1944),
    ("George II (restored again)",               1944,  1947),
    ("Paul I (King of Greece)",                  1947,  1964),
    ("Constantine II (King of Greece)",          1964,  1967),
    ("Military Junta (Papadopoulos)",            1967,  1974),
    ("Konstantinos Karamanlis (PM)",             1974,  1980),
    ("Georgios Rallis (PM)",                     1980,  1981),
    ("Andreas Papandreou (PM)",                  1981,  1989),
    ("Konstantinos Mitsotakis (PM)",             1990,  1993),
    ("Andreas Papandreou (PM, 2nd term)",        1993,  1996),
    ("Kostas Simitis (PM)",                      1996,  2004),
    ("Kostas Karamanlis (PM)",                   2004,  2009),
    ("George Papandreou (PM)",                   2009,  2011),
    ("Lucas Papademos (PM)",                     2011,  2012),
    ("Antonis Samaras (PM)",                     2012,  2015),
    ("Alexis Tsipras (PM)",                      2015,  2019),
    ("Kyriakos Mitsotakis (PM)",                 2019,  2029),
]

# ─── ITALY / ROME ─────────────────────────────────────────────────────────────

ITALY_RULERS = [

    # --- ROMAN KINGDOM ---
    ("Romulus (Founder of Rome, legendary)",     -753,  -716),
    ("Numa Pompilius",                           -715,  -673),
    ("Tullus Hostilius",                         -673,  -641),
    ("Ancus Marcius",                            -640,  -616),
    ("Tarquinius Priscus",                       -616,  -578),
    ("Servius Tullius",                          -578,  -534),
    ("Tarquinius Superbus",                      -534,  -509),

    # --- ROMAN REPUBLIC (key figures) ---
    ("Lucius Junius Brutus (1st Consul)",        -509,  -508),
    ("Cincinnatus (Dictator)",                   -458,  -457),
    ("Camillus",                                 -396,  -365),
    ("Scipio Africanus",                         -205,  -183),
    ("Gaius Marius",                             -107,   -86),
    ("Lucius Cornelius Sulla (Dictator)",         -82,   -78),
    ("Gnaeus Pompeius Magnus (Pompey)",           -70,   -48),
    ("Julius Caesar (Dictator)",                  -49,   -44),
    ("Mark Antony & Octavian (Triumvirate)",      -43,   -31),

    # --- ROMAN EMPIRE ---
    ("Augustus (Octavian)",                       -27,    14),
    ("Tiberius",                                   14,    37),
    ("Caligula",                                   37,    41),
    ("Claudius",                                   41,    54),
    ("Nero",                                       54,    68),
    ("Galba",                                      68,    69),
    ("Otho",                                       69,    69),
    ("Vitellius",                                  69,    69),
    ("Vespasian",                                  69,    79),
    ("Titus",                                      79,    81),
    ("Domitian",                                   81,    96),
    ("Nerva",                                      96,    98),
    ("Trajan",                                     98,   117),
    ("Hadrian",                                   117,   138),
    ("Antoninus Pius",                            138,   161),
    ("Marcus Aurelius",                           161,   180),
    ("Commodus",                                  180,   192),
    ("Septimius Severus",                         193,   211),
    ("Caracalla",                                 211,   217),
    ("Elagabalus",                                218,   222),
    ("Alexander Severus",                         222,   235),
    ("Maximinus Thrax",                           235,   238),
    ("Gordian III",                               238,   244),
    ("Philip the Arab",                           244,   249),
    ("Decius",                                    249,   251),
    ("Valerian",                                  253,   260),
    ("Gallienus",                                 260,   268),
    ("Aurelian",                                  270,   275),
    ("Probus",                                    276,   282),
    ("Diocletian",                                284,   305),
    ("Constantine I (the Great)",                 306,   337),
    ("Constantius II",                            337,   361),
    ("Julian the Apostate",                       361,   363),
    ("Valentinian I",                             364,   375),
    ("Theodosius I (the Great)",                  379,   395),
    ("Honorius (Western Roman Emperor)",          395,   423),
    ("Valentinian III",                           423,   455),
    ("Romulus Augustulus (last W. Roman Emperor)", 475,  476),

    # --- OSTROGOTHIC KINGDOM ---
    ("Odoacer (King of Italy)",                   476,   493),
    ("Theodoric the Great (Ostrogoths)",          493,   526),
    ("Amalasuntha (Queen Regent)",                526,   535),

    # --- BYZANTINE RECONQUEST ---
    ("Justinian I (Byzantine Emperor of Italy)",  535,   568),

    # --- LOMBARD KINGDOM ---
    ("Alboin (King of Lombards)",                 568,   572),
    ("Authari (King of Lombards)",                584,   590),
    ("Agilulf (King of Lombards)",                590,   616),
    ("Rothari (King of Lombards)",                636,   652),
    ("Liutprand (King of Lombards)",              712,   744),
    ("Desiderius (Last Lombard King)",            756,   774),

    # --- CAROLINGIAN / FRANKISH ---
    ("Charlemagne (King of Italy)",               774,   814),
    ("Louis the Pious",                           814,   840),
    ("Lothair I",                                 840,   855),
    ("Louis II of Italy",                         855,   875),
    ("Charles II the Bald",                       875,   877),
    ("Berengar I (King of Italy)",                888,   924),

    # --- HOLY ROMAN EMPIRE (Italian campaigns) ---
    ("Otto I (Holy Roman Emperor)",               962,   973),
    ("Otto II",                                   973,   983),
    ("Otto III",                                  983,  1002),
    ("Henry II",                                 1002,  1024),
    ("Conrad II",                                1024,  1039),
    ("Henry III",                                1039,  1056),
    ("Henry IV",                                 1056,  1106),
    ("Henry V",                                  1106,  1125),
    ("Frederick I Barbarossa",                   1155,  1190),
    ("Henry VI",                                 1190,  1197),
    ("Frederick II",                             1220,  1250),

    # --- CITY STATES ERA (representative rulers) ---
    ("Lorenzo de' Medici (Florence)",            1469,  1492),
    ("Ludovico Sforza (Milan)",                  1494,  1499),
    ("Pope Julius II (Papal States)",            1503,  1513),
    ("Pope Leo X (Papal States)",                1513,  1521),

    # --- SPANISH/AUSTRIAN DOMINATION ---
    ("Charles V (Holy Roman Emperor/Spain)",     1516,  1556),
    ("Philip II of Spain",                       1556,  1598),
    ("Philip III of Spain",                      1598,  1621),
    ("Philip IV of Spain",                       1621,  1665),
    ("Charles II of Spain",                      1665,  1700),
    ("Philip V of Spain",                        1700,  1713),
    ("Charles VI (Austrian Habsburgs)",          1713,  1740),
    ("Maria Theresa (Austrian)",                 1740,  1780),
    ("Joseph II (Austrian)",                     1780,  1790),

    # --- NAPOLEONIC ERA ---
    ("Napoleon Bonaparte (King of Italy)",       1805,  1814),
    ("Eugene de Beauharnais (Viceroy)",          1805,  1814),

    # --- RESTORATION / RISORGIMENTO ---
    ("Victor Emmanuel I (Sardinia)",             1814,  1821),
    ("Charles Felix (Sardinia)",                 1821,  1831),
    ("Charles Albert (Sardinia)",                1831,  1849),
    ("Victor Emmanuel II (Sardinia→Italy)",      1849,  1878),

    # --- KINGDOM OF ITALY ---
    ("Victor Emmanuel II (King of Italy)",       1861,  1878),
    ("Umberto I",                                1878,  1900),
    ("Victor Emmanuel III",                      1900,  1946),
    ("Benito Mussolini (Prime Minister/Duce)",   1922,  1943),
    ("Pietro Badoglio (PM)",                     1943,  1944),
    ("Ivanoe Bonomi (PM)",                       1944,  1945),
    ("Ferruccio Parri (PM)",                     1945,  1945),

    # --- ITALIAN REPUBLIC ---
    ("Alcide De Gasperi (PM)",                   1945,  1953),
    ("Giuseppe Pella (PM)",                      1953,  1954),
    ("Amintore Fanfani (PM)",                    1954,  1954),
    ("Mario Scelba (PM)",                        1954,  1955),
    ("Antonio Segni (PM)",                       1955,  1957),
    ("Adone Zoli (PM)",                          1957,  1958),
    ("Amintore Fanfani (PM, 2nd)",               1958,  1959),
    ("Antonio Segni (PM, 2nd)",                  1959,  1960),
    ("Fernando Tambroni (PM)",                   1960,  1960),
    ("Amintore Fanfani (PM, 3rd)",               1960,  1963),
    ("Giovanni Leone (PM)",                      1963,  1963),
    ("Aldo Moro (PM)",                           1963,  1968),
    ("Giovanni Leone (PM, 2nd)",                 1968,  1968),
    ("Mariano Rumor (PM)",                       1968,  1970),
    ("Emilio Colombo (PM)",                      1970,  1972),
    ("Giulio Andreotti (PM)",                    1972,  1973),
    ("Mariano Rumor (PM, 2nd)",                  1973,  1974),
    ("Aldo Moro (PM, 2nd)",                      1974,  1976),
    ("Giulio Andreotti (PM, 2nd)",               1976,  1979),
    ("Francesco Cossiga (PM)",                   1979,  1980),
    ("Arnaldo Forlani (PM)",                     1980,  1981),
    ("Giovanni Spadolini (PM)",                  1981,  1982),
    ("Amintore Fanfani (PM, 4th)",               1982,  1983),
    ("Bettino Craxi (PM)",                       1983,  1987),
    ("Giovanni Goria (PM)",                      1987,  1988),
    ("Ciriaco De Mita (PM)",                     1988,  1989),
    ("Giulio Andreotti (PM, 3rd)",               1989,  1992),
    ("Giuliano Amato (PM)",                      1992,  1993),
    ("Carlo Azeglio Ciampi (PM)",                1993,  1994),
    ("Silvio Berlusconi (PM)",                   1994,  1995),
    ("Lamberto Dini (PM)",                       1995,  1996),
    ("Romano Prodi (PM)",                        1996,  1998),
    ("Massimo D'Alema (PM)",                     1998,  2000),
    ("Giuliano Amato (PM, 2nd)",                 2000,  2001),
    ("Silvio Berlusconi (PM, 2nd)",              2001,  2006),
    ("Romano Prodi (PM, 2nd)",                   2006,  2008),
    ("Silvio Berlusconi (PM, 3rd)",              2008,  2011),
    ("Mario Monti (PM)",                         2011,  2013),
    ("Enrico Letta (PM)",                        2013,  2014),
    ("Matteo Renzi (PM)",                        2014,  2016),
    ("Paolo Gentiloni (PM)",                     2016,  2018),
    ("Giuseppe Conte (PM)",                      2018,  2021),
    ("Mario Draghi (PM)",                        2021,  2022),
    ("Giorgia Meloni (PM)",                      2022,  2029),
]


# ─── INSERT FUNCTION ──────────────────────────────────────────────────────────

def insert_rulers(location_name, rulers):
    cursor.execute("SELECT id FROM locations WHERE name = ?", (location_name,))
    row = cursor.fetchone()
    if not row:
        print(f"ERROR: '{location_name}' not found in locations table.")
        return 0

    loc_id   = row[0]
    inserted = 0

    for name, start, end in rulers:
        for year in range(start, end + 1):
            cursor.execute(
                "SELECT id FROM history WHERE location_id=? AND year=?",
                (loc_id, year)
            )
            if cursor.fetchone():
                cursor.execute(
                    "UPDATE history SET ruler=? WHERE location_id=? AND year=?",
                    (name, loc_id, year)
                )
            else:
                cursor.execute(
                    "INSERT INTO history (location_id, year, ruler) VALUES (?,?,?)",
                    (loc_id, year, name)
                )
            inserted += 1

    conn.commit()
    return loc_id, inserted


# ─── RUN GREECE ───────────────────────────────────────────────────────────────

print("Adding Greece rulers...")
result = insert_rulers("Greece", GREECE_RULERS)
if result:
    greece_id, count = result
    print(f"  Inserted/updated {count} entries for Greece")

    print("\n  Spot checks (Greece):")
    for year, expected in [
        (-430, "Pericles"),
        (-334, "Alexander the Great"),
        (530,  "Justinian I"),
        (1000, "Basil II"),
        (1460, "Ottoman Empire"),
        (1850, "Otto I"),
        (1940, "George II"),
        (2020, "Kyriakos Mitsotakis"),
    ]:
        cursor.execute(
            "SELECT ruler FROM history WHERE location_id=? AND year=?",
            (greece_id, year)
        )
        r = cursor.fetchone()
        result_name = r[0] if r else "Not found"
        status = "✓" if expected in (result_name or "") else "?"
        print(f"    {status} {year}: {result_name}")


# ─── RUN ITALY ────────────────────────────────────────────────────────────────

print("\nAdding Italy rulers...")
result = insert_rulers("Italy", ITALY_RULERS)
if result:
    italy_id, count = result
    print(f"  Inserted/updated {count} entries for Italy")

    print("\n  Spot checks (Italy):")
    for year, expected in [
        (-44,  "Julius Caesar"),
        (14,   "Augustus"),
        (100,  "Trajan"),
        (500,  "Theodoric"),
        (800,  "Charlemagne"),
        (1480, "Lorenzo de' Medici"),
        (1810, "Napoleon"),
        (1935, "Benito Mussolini"),
        (1960, "Amintore Fanfani"),
        (2023, "Giorgia Meloni"),
    ]:
        cursor.execute(
            "SELECT ruler FROM history WHERE location_id=? AND year=?",
            (italy_id, year)
        )
        r = cursor.fetchone()
        result_name = r[0] if r else "Not found"
        status = "✓" if expected in (result_name or "") else "?"
        print(f"    {status} {year}: {result_name}")

conn.close()
print("\nDone! Greece and Italy rulers added to the database.")