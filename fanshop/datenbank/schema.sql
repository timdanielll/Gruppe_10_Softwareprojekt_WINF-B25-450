-- ---------------------------------------------------------------------------
-- Datenbankschema des WI Fanshop (Pflichtenheft Kapitel 6)
--
-- Stammdaten   : kunde, artikel, sonderaktion
-- Bewegungsdaten: bestellung, bestellposition, retoure
--
-- Das Schema wird beim Programmstart ausgefuehrt. Durch "IF NOT EXISTS"
-- passiert beim zweiten Start nichts mehr - vorhandene Daten bleiben erhalten.
-- ---------------------------------------------------------------------------


-- 6.1 Stammdaten: Kunde ------------------------------------------------------
CREATE TABLE IF NOT EXISTS kunde (
    kundennummer                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name                         TEXT    NOT NULL,
    strasse                      TEXT    NOT NULL,
    plz                          INTEGER NOT NULL,
    ort                          TEXT    NOT NULL,
    newsletter_aktiv             INTEGER NOT NULL DEFAULT 0,  -- 0 = nein, 1 = ja
    newsletter_rabatt_verfuegbar INTEGER NOT NULL DEFAULT 0,  -- 1 = 10% noch offen
    sticker_kontostand           INTEGER NOT NULL DEFAULT 0,   -- hoechstens 6, jedes Motiv einmal
    starterset_erhalten          INTEGER NOT NULL DEFAULT 0    -- 1 = Sonderangebot schon bekommen
);


-- 6.2 Stammdaten: Artikel ----------------------------------------------------
CREATE TABLE IF NOT EXISTS artikel (
    artikel_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    kategorie        TEXT    NOT NULL,          -- fester Wert aus konfiguration.KATEGORIEN
    titel            TEXT    NOT NULL,
    beschreibung     TEXT,
    preis            REAL    NOT NULL,          -- Bruttopreis in EUR
    rabattsatz       REAL    NOT NULL DEFAULT 0.0,  -- 0.15 entspricht 15 Prozent
    lagerbestand     INTEGER NOT NULL,
    erstellungsdatum TEXT    NOT NULL,          -- ISO 8601: YYYY-MM-DD
    aktiv            INTEGER NOT NULL DEFAULT 1,-- 1 = sichtbar, 0 = deaktiviert
    groesse          TEXT,                      -- nur bei Damen/Herren gefuellt
    bildpfad         TEXT                       -- Dateiname in assets/artikel/
);


-- 6.3 Bewegungsdaten: Bestellung ---------------------------------------------
CREATE TABLE IF NOT EXISTS bestellung (
    bestellnummer                INTEGER PRIMARY KEY AUTOINCREMENT,
    kundennummer                 INTEGER,       -- NULL = Kunde wurde geloescht
    zeitstempel                  INTEGER NOT NULL,  -- Unix-Zeit in Sekunden
    gesamtbetrag                 REAL    NOT NULL,  -- Endpreis nach allen Rabatten
    newsletter_rabatt_angewendet INTEGER NOT NULL DEFAULT 0,
    sticker_ausgegeben           INTEGER NOT NULL DEFAULT 2,   -- 0 bis 2, je nach Sammelstand
    starterset_ausgegeben        INTEGER NOT NULL DEFAULT 0,   -- 1 = Starterset lag bei (/F53/)
    FOREIGN KEY (kundennummer) REFERENCES kunde (kundennummer) ON DELETE SET NULL
);


-- 6.4 Bewegungsdaten: Bestellposition ----------------------------------------
CREATE TABLE IF NOT EXISTS bestellposition (
    position_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    bestellnummer      INTEGER NOT NULL,
    artikel_id         INTEGER NOT NULL,
    menge              INTEGER NOT NULL,
    historischer_preis REAL    NOT NULL,        -- tatsaechlich gezahlter Einzelpreis
    FOREIGN KEY (bestellnummer) REFERENCES bestellung (bestellnummer) ON DELETE CASCADE,
    FOREIGN KEY (artikel_id)    REFERENCES artikel (artikel_id)
);


-- 6.5 Bewegungsdaten: Retoure ------------------------------------------------
CREATE TABLE IF NOT EXISTS retoure (
    retouren_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    bestellnummer     INTEGER NOT NULL,
    artikel_id        INTEGER NOT NULL,
    menge             INTEGER NOT NULL,
    retouren_datum    TEXT    NOT NULL,         -- ISO 8601: YYYY-MM-DD HH:MM:SS
    erstattungsbetrag REAL    NOT NULL,         -- menge * historischer_preis
    FOREIGN KEY (bestellnummer) REFERENCES bestellung (bestellnummer),
    FOREIGN KEY (artikel_id)    REFERENCES artikel (artikel_id)
);


-- Zusatz: Sticker-Sammelalbum ------------------------------------------------
-- Die Spalte kunde.sticker_kontostand zaehlt nur, WIE VIELE Sticker jemand hat.
-- Fuer das Sammelmodul (/F53/) muss man auch wissen, WELCHE - sonst gibt es
-- keine Sammlung, sondern nur eine Zahl. Eine Zeile je Kunde und Motiv.
--
-- Jedes Motiv wird nur einmal vergeben, deshalb ist "anzahl" immer 1: Der
-- Primaerschluessel laesst keine zweite Zeile zu, der CHECK keine zweite
-- Gutschrift. Die Spalte bleibt erhalten, damit die Zaehlung im Album
-- (SUM(anzahl)) weiterhin direkt mit kunde.sticker_kontostand vergleichbar ist.
CREATE TABLE IF NOT EXISTS kunde_sticker (
    kundennummer INTEGER NOT NULL,
    motiv        TEXT    NOT NULL,        -- Schluessel aus modelle/sticker.py
    anzahl       INTEGER NOT NULL DEFAULT 1 CHECK (anzahl = 1),
    PRIMARY KEY (kundennummer, motiv),
    FOREIGN KEY (kundennummer) REFERENCES kunde (kundennummer) ON DELETE CASCADE
);


-- Zusatz: Sonderaktionen -----------------------------------------------------
-- Lastenheft: "Es gibt fest definierte Spezialangebote, die aktiviert werden
-- koennen". Damit der Aktivierungs-Status einen Programmneustart ueberlebt,
-- wird er in einer eigenen kleinen Tabelle gespeichert.
CREATE TABLE IF NOT EXISTS sonderaktion (
    aktions_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    titel              TEXT    NOT NULL,
    art                TEXT    NOT NULL,        -- 'kategorie' oder 'mindestwert'
    zielkategorie      TEXT,                    -- nur bei art = 'kategorie'
    mindestbestellwert REAL    NOT NULL DEFAULT 0.0,  -- nur bei art = 'mindestwert'
    rabattsatz         REAL    NOT NULL,        -- 0.20 entspricht 20 Prozent
    aktiv              INTEGER NOT NULL DEFAULT 0
);


-- Indizes fuer die haeufigsten Abfragen (Suche und Berichte) ------------------
CREATE INDEX IF NOT EXISTS idx_artikel_kategorie      ON artikel (kategorie);
CREATE INDEX IF NOT EXISTS idx_bestellung_zeit        ON bestellung (zeitstempel);
CREATE INDEX IF NOT EXISTS idx_position_bestellnummer ON bestellposition (bestellnummer);
CREATE INDEX IF NOT EXISTS idx_position_artikel       ON bestellposition (artikel_id);
