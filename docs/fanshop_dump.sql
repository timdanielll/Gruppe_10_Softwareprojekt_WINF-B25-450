-- WI Fanshop: SQL-Dump für die Abgabe
-- Erzeugt mit tools/erstelle_sql_dump.py aus fanshop.db.
-- Import: sqlite3 neue_datenbank.db < docs/fanshop_dump.sql

BEGIN TRANSACTION;
CREATE TABLE artikel (
    artikel_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    kategorie        TEXT    NOT NULL,          -- fester Wert aus konfiguration.KATEGORIEN
    titel            TEXT    NOT NULL,
    beschreibung     TEXT,
    preis            REAL    NOT NULL,          -- Bruttopreis in EUR
    rabattsatz       REAL    NOT NULL DEFAULT 0.0,  -- 0.15 entspricht 15 Prozent
    lagerbestand     INTEGER NOT NULL,
    erstellungsdatum TEXT    NOT NULL,          -- ISO 8601: YYYY-MM-DD
    aktiv            INTEGER NOT NULL DEFAULT 1,-- 1 = sichtbar, 0 = deaktiviert
    bildpfad         TEXT                       -- Dateiname in assets/artikel/
);
INSERT INTO "artikel" VALUES(1,'Herren','Poloshirt htw saar, schwarz','Schwarzes Poloshirt aus Piqué-Baumwolle mit kleinem ''htw saar''-Logo und bunter Streifenlinie auf der Brust.',24.95,0.15,1,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.17(1).jpeg');
INSERT INTO "artikel" VALUES(2,'Accessoires','Regenschirm htw saar, grün','Leuchtend grüner Stockschirm mit schwarzem ''htw saar''-Schriftzug am Schirmrand.',9.9,0.0,5,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.17(2).jpeg');
INSERT INTO "artikel" VALUES(3,'Accessoires','Rucksack htw saar, schwarz','Schwarzer Rolltop-Rucksack mit weißem ''htw saar''-Logo und großem Konturdruck auf der Vordertasche.',25.95,0.0,15,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.17(3).jpeg');
INSERT INTO "artikel" VALUES(4,'Accessoires','Schlüsselband htw saar, bunt','Buntes Schlüsselband mit Karabinerhaken und mehrfach aufgedrucktem ''htw saar''-Schriftzug in Regenbogenfarben.',1.95,0.0,23,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.17(4).jpeg');
INSERT INTO "artikel" VALUES(5,'Accessoires','Sneaker-Socken htw saar, schwarz','Schwarze Sneaker-Socken mit ''htw saar''-Schriftzug und farbigem Streifen am Bund.',7.9,0.0,3,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.17(5).jpeg');
INSERT INTO "artikel" VALUES(6,'Accessoires','Tassen-Set htw saar Fakultäten','Vier bunte Kaffeetassen in Grün, Blau, Pink und Orange mit den Namen verschiedener htw-saar-Fakultäten.',23.85,0.15,14,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.17(6).jpeg');
INSERT INTO "artikel" VALUES(7,'Herren','T-Shirt htw saar, schwarz','Schwarzes Baumwoll-T-Shirt mit kleinem ''htw saar''-Logo und bunter Streifenlinie auf der Brust.',14.95,0.0,21,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.17(7).jpeg');
INSERT INTO "artikel" VALUES(8,'Herren','Poloshirt htw saar, schwarz (Herrenpassform)','Schwarzes Poloshirt mit Knopfleiste und ''htw saar''-Logo mit farbigem Streifen auf der linken Brust.',24.95,0.0,28,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.17.jpeg');
INSERT INTO "artikel" VALUES(9,'Specials','USB-Stick htw saar','USB-Sticks in verschiedenen Farben mit graviertem ''htw saar''-Schriftzug und Klappmechanismus.',9.9,0.0,9,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(1).jpeg');
INSERT INTO "artikel" VALUES(10,'Herren','Fleecejacke htw saar, schwarz','Schwarze Fleecejacke mit durchgehendem Reißverschluss und ''htw saar''-Logo mit buntem Streifen auf der Brust.',32.5,0.0,15,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(10).jpeg');
INSERT INTO "artikel" VALUES(11,'Damen','Sport-Shirt htw saar Hochschulsport, Damen','Schwarzes tailliertes Funktionsshirt mit ''htw saar hochschulsport''-Schriftzug und vier bunten Sport-Icons.',15.0,0.15,23,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(11).jpeg');
INSERT INTO "artikel" VALUES(12,'Herren','Sport-Shirt htw saar Hochschulsport, Herren','Schwarzes Funktionsshirt mit ''htw saar hochschulsport''-Schriftzug und vier bunten Sport-Icons.',15.0,0.0,30,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(12).jpeg');
INSERT INTO "artikel" VALUES(13,'Print','Klappkarte htw saar','Quadratische Klappkarte mit buntem Farbverlauf und dem Schriftzug ''htw saar – Hochschule für Technik und Wirtschaft des Saarlandes''.',2.5,0.0,11,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(13).jpeg');
INSERT INTO "artikel" VALUES(14,'Herren','Hoodie htw saar, schwarz','Schwarzer Kapuzenpullover mit Kängurutasche und ''htw saar''-Logo mit buntem Streifen auf der Brust.',39.95,0.0,18,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(14).jpeg');
INSERT INTO "artikel" VALUES(15,'Accessoires','Trinkflasche htw saar','Durchsichtige Kunststoff-Trinkflasche mit grauem Schraubverschluss und vertikalem ''htw saar''-Schriftzug in Regenbogenfarben.',8.9,0.0,25,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(15).jpeg');
INSERT INTO "artikel" VALUES(16,'Schreibwaren','Kugelschreiber htw saar','Weiße Kugelschreiber mit farbigen Kappen und ''htw saar''-Aufdruck, gebündelt in einem Becher.',0.95,0.15,6,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(16).jpeg');
INSERT INTO "artikel" VALUES(17,'Damen','Regenbogen-Shirt htw saar Hochschulsport, Damen','T-Shirt mit buntem Regenbogen-Farbverlauf, weißem Kontrastkragen und dem Schriftzug ''htw saar hochschulsport''.',25.0,0.0,13,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(17).jpeg');
INSERT INTO "artikel" VALUES(18,'Herren','Regenbogen-Shirt htw saar Hochschulsport, Herren','T-Shirt mit buntem Regenbogen-Farbverlauf, weißem Kontrastkragen und dem Schriftzug ''htw saar hochschulsport''.',25.0,0.0,20,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(18).jpeg');
INSERT INTO "artikel" VALUES(19,'Schreibwaren','Lineal htw saar','30-cm-Lineal mit buntem Farbverlauf und dem Schriftzug ''htw saar studieren.htwsaar.de''.',0.9,0.0,27,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(19).jpeg');
INSERT INTO "artikel" VALUES(20,'Print','Briefpapier htw saar','Weißes Briefpapier mit ''htw saar''-Logo oben und buntem Halbkreis-Muster am unteren Rand.',4.9,0.0,7,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(2).jpeg');
INSERT INTO "artikel" VALUES(21,'Accessoires','Multifunktionstuch htw saar, grün','Grünes Multifunktionstuch (Schlauchschal) mit weißem Aufdruck ''architektur und bauingenieurwesen htw saar''.',2.0,0.15,15,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(20).jpeg');
INSERT INTO "artikel" VALUES(22,'Accessoires','Kartenetui htw saar, weiß','Weißes Kartenetui mit ''htw saar''-Schriftzug und mehreren durchsichtigen Kartenfächern.',6.9,0.0,22,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(21).jpeg');
INSERT INTO "artikel" VALUES(23,'Damen','Poloshirt htw saar, schwarz, Damen','Schwarzes tailliertes Damen-Poloshirt mit Knopfleiste und ''htw saar''-Logo mit buntem Streifen.',24.95,0.0,29,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(22).jpeg');
INSERT INTO "artikel" VALUES(24,'Specials','Baby-Body htw saar','Weißer Baby-Body mit ''htw saar''-Logo und vier bunten Feldern zum Thema ''Team Bauklotz, Entwicklung, Wachstum''.',11.9,0.0,10,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(3).jpeg');
INSERT INTO "artikel" VALUES(25,'Accessoires','Stofftasche DFHI-EFARES, natur','Naturfarbene Stoff-Tragetasche mit Fuchs-Logo und Schriftzug ''DFHI-EFARES'' sowie bunten Punkten.',3.9,0.0,17,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(4).jpeg');
INSERT INTO "artikel" VALUES(26,'Accessoires','Stofftasche htw saar, schwarz','Schwarze Stoff-Tragetasche mit weißem ''htw saar''-Logo und großem Konturdruck.',3.9,0.15,24,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(5).jpeg');
INSERT INTO "artikel" VALUES(27,'Accessoires','Stofftaschen htw saar Fakultäten, bunt','Mehrere naturfarbene Stofftaschen mit bunten Farbfeldern und Namen unterschiedlicher htw-saar-Fakultäten.',4.0,0.0,5,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(6).jpeg');
INSERT INTO "artikel" VALUES(28,'Schreibwaren','Kugelschreiber htw saar, Set','Schwarze Kugelschreiber mit bunten Kappen und ''htw saar''-Aufdruck, aufgestellt in einer weißen Tasse.',0.95,0.0,12,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(7).jpeg');
INSERT INTO "artikel" VALUES(29,'Schreibwaren','Stiftemäppchen htw saar, bunt','Stiftemäppchen in verschiedenen Farben mit schwarzem Reißverschluss und ''htw saar''-Aufdruck.',6.9,0.0,19,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(8).jpeg');
INSERT INTO "artikel" VALUES(30,'Herren','Fleecejacke htw saar, schwarz (Ansicht 2)','Schwarze Fleecejacke mit durchgehendem Reißverschluss und ''htw saar''-Logo mit buntem Streifen auf der Brust.',32.5,0.0,26,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18(9).jpeg');
INSERT INTO "artikel" VALUES(31,'Herren','T-Shirt htw saar, schwarz (Rundhals)','Schwarzes Rundhals-T-Shirt mit kleinem ''htw saar''-Logo und bunter Streifenlinie auf der Brust.',14.95,0.15,7,'2026-08-24',1,'WhatsApp Image 2026-08-20 at 17.26.18.jpeg');
CREATE TABLE bestellposition (
    position_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    bestellnummer      INTEGER NOT NULL,
    artikel_id         INTEGER NOT NULL,
    menge              INTEGER NOT NULL,
    historischer_preis REAL    NOT NULL, groesse TEXT,        -- tatsaechlich gezahlter Einzelpreis
    FOREIGN KEY (bestellnummer) REFERENCES bestellung (bestellnummer) ON DELETE CASCADE,
    FOREIGN KEY (artikel_id)    REFERENCES artikel (artikel_id)
);
INSERT INTO "bestellposition" VALUES(1,1,1,1,21.21,NULL);
INSERT INTO "bestellposition" VALUES(2,1,2,2,9.9,NULL);
INSERT INTO "bestellposition" VALUES(3,2,3,1,25.95,NULL);
INSERT INTO "bestellposition" VALUES(4,3,1,2,21.21,NULL);
INSERT INTO "bestellposition" VALUES(5,3,4,1,1.95,NULL);
INSERT INTO "bestellposition" VALUES(6,4,2,1,9.9,NULL);
INSERT INTO "bestellposition" VALUES(7,4,3,1,25.95,NULL);
INSERT INTO "bestellposition" VALUES(8,4,4,1,1.95,NULL);
INSERT INTO "bestellposition" VALUES(9,5,5,3,7.9,NULL);
INSERT INTO "bestellposition" VALUES(10,6,1,1,21.21,NULL);
INSERT INTO "bestellposition" VALUES(11,6,5,1,7.9,NULL);
INSERT INTO "bestellposition" VALUES(12,7,3,2,25.95,NULL);
INSERT INTO "bestellposition" VALUES(13,7,4,1,1.95,NULL);
INSERT INTO "bestellposition" VALUES(14,8,2,4,9.9,NULL);
INSERT INTO "bestellposition" VALUES(15,9,10,1,32.5,'M');
INSERT INTO "bestellposition" VALUES(16,9,20,1,4.9,NULL);
CREATE TABLE bestellung (
    bestellnummer                INTEGER PRIMARY KEY AUTOINCREMENT,
    kundennummer                 INTEGER,       -- NULL = Kunde wurde geloescht
    zeitstempel                  INTEGER NOT NULL,  -- Unix-Zeit in Sekunden
    gesamtbetrag                 REAL    NOT NULL,  -- Endpreis nach allen Rabatten
    newsletter_rabatt_angewendet INTEGER NOT NULL DEFAULT 0,
    sticker_ausgegeben           INTEGER NOT NULL DEFAULT 3, starterset_ausgegeben INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (kundennummer) REFERENCES kunde (kundennummer) ON DELETE SET NULL
);
INSERT INTO "bestellung" VALUES(1,1,1785852260,41.01,0,3,0);
INSERT INTO "bestellung" VALUES(2,2,1786111460,25.95,0,3,0);
INSERT INTO "bestellung" VALUES(3,3,1786370660,44.37,0,3,0);
INSERT INTO "bestellung" VALUES(4,4,1786716260,37.8,0,3,0);
INSERT INTO "bestellung" VALUES(5,5,1786975460,23.7,0,3,0);
INSERT INTO "bestellung" VALUES(6,1,1787234660,29.11,0,3,0);
INSERT INTO "bestellung" VALUES(7,2,1787407460,53.85,0,3,0);
INSERT INTO "bestellung" VALUES(8,3,1787493860,39.6,0,3,0);
INSERT INTO "bestellung" VALUES(9,3,1787645317,37.4,0,0,1);
CREATE TABLE kunde (
    kundennummer                 INTEGER PRIMARY KEY AUTOINCREMENT,
    name                         TEXT    NOT NULL,
    strasse                      TEXT    NOT NULL,
    plz                          INTEGER NOT NULL,
    ort                          TEXT    NOT NULL,
    newsletter_aktiv             INTEGER NOT NULL DEFAULT 0,  -- 0 = nein, 1 = ja
    newsletter_rabatt_verfuegbar INTEGER NOT NULL DEFAULT 0,  -- 1 = 10% noch offen
    sticker_kontostand           INTEGER NOT NULL DEFAULT 0
, starterset_erhalten INTEGER NOT NULL DEFAULT 0);
INSERT INTO "kunde" VALUES(1,'Anna Becker','Waldhausweg 14',66123,'Saarbrücken',1,1,6,0);
INSERT INTO "kunde" VALUES(2,'Ben Hoffmann','Goebenstraße 40',66117,'Saarbrücken',0,0,6,0);
INSERT INTO "kunde" VALUES(3,'Clara Schmitt','Malstatter Straße 7',66115,'Saarbrücken',1,1,6,1);
INSERT INTO "kunde" VALUES(4,'David Wagner','Am Markt 3',66663,'Merzig',0,0,3,0);
INSERT INTO "kunde" VALUES(5,'Elif Yildirim','Bahnhofstraße 22',66538,'Neunkirchen',0,0,3,0);
CREATE TABLE kunde_sticker (
    kundennummer INTEGER NOT NULL,
    motiv        TEXT    NOT NULL,        -- Schluessel aus modelle/sticker.py
    anzahl       INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (kundennummer, motiv),
    FOREIGN KEY (kundennummer) REFERENCES kunde (kundennummer) ON DELETE CASCADE
);
INSERT INTO "kunde_sticker" VALUES(1,'campus',1);
INSERT INTO "kunde_sticker" VALUES(1,'htwsaar',1);
INSERT INTO "kunde_sticker" VALUES(1,'kneipe',1);
INSERT INTO "kunde_sticker" VALUES(2,'campus',1);
INSERT INTO "kunde_sticker" VALUES(2,'htwsaar',1);
INSERT INTO "kunde_sticker" VALUES(2,'kneipe',1);
INSERT INTO "kunde_sticker" VALUES(3,'campus',1);
INSERT INTO "kunde_sticker" VALUES(3,'htwsaar',1);
INSERT INTO "kunde_sticker" VALUES(3,'kneipe',1);
INSERT INTO "kunde_sticker" VALUES(4,'campus',1);
INSERT INTO "kunde_sticker" VALUES(4,'htwsaar',1);
INSERT INTO "kunde_sticker" VALUES(4,'kneipe',1);
INSERT INTO "kunde_sticker" VALUES(5,'campus',1);
INSERT INTO "kunde_sticker" VALUES(5,'htwsaar',1);
INSERT INTO "kunde_sticker" VALUES(5,'kneipe',1);
INSERT INTO "kunde_sticker" VALUES(1,'liebt',1);
INSERT INTO "kunde_sticker" VALUES(1,'mensen',1);
INSERT INTO "kunde_sticker" VALUES(1,'vier',1);
INSERT INTO "kunde_sticker" VALUES(2,'liebt',1);
INSERT INTO "kunde_sticker" VALUES(2,'mensen',1);
INSERT INTO "kunde_sticker" VALUES(2,'vier',1);
INSERT INTO "kunde_sticker" VALUES(3,'liebt',1);
INSERT INTO "kunde_sticker" VALUES(3,'mensen',1);
INSERT INTO "kunde_sticker" VALUES(3,'vier',1);
CREATE TABLE retoure (
    retouren_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    bestellnummer     INTEGER NOT NULL,
    artikel_id        INTEGER NOT NULL,
    menge             INTEGER NOT NULL,
    retouren_datum    TEXT    NOT NULL,         -- ISO 8601: YYYY-MM-DD HH:MM:SS
    erstattungsbetrag REAL    NOT NULL, position_id INTEGER,         -- menge * historischer_preis
    FOREIGN KEY (bestellnummer) REFERENCES bestellung (bestellnummer),
    FOREIGN KEY (artikel_id)    REFERENCES artikel (artikel_id)
);
CREATE TABLE sonderaktion (
    aktions_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    titel              TEXT    NOT NULL,
    art                TEXT    NOT NULL,        -- 'kategorie' oder 'mindestwert'
    zielkategorie      TEXT,                    -- nur bei art = 'kategorie'
    mindestbestellwert REAL    NOT NULL DEFAULT 0.0,  -- nur bei art = 'mindestwert'
    rabattsatz         REAL    NOT NULL,        -- 0.20 entspricht 20 Prozent
    aktiv              INTEGER NOT NULL DEFAULT 0
);
INSERT INTO "sonderaktion" VALUES(1,'Semesterstart: 20 % auf Schreibwaren','kategorie','Schreibwaren',0.0,0.2,1);
INSERT INTO "sonderaktion" VALUES(2,'Ab 50 € Einkaufswert: 10 % auf alles','mindestwert',NULL,50.0,0.1,0);
CREATE INDEX idx_artikel_kategorie      ON artikel (kategorie);
CREATE INDEX idx_bestellung_zeit        ON bestellung (zeitstempel);
CREATE INDEX idx_position_bestellnummer ON bestellposition (bestellnummer);
CREATE INDEX idx_position_artikel       ON bestellposition (artikel_id);
CREATE INDEX idx_retoure_position ON retoure (position_id);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('artikel',31);
INSERT INTO "sqlite_sequence" VALUES('kunde',5);
INSERT INTO "sqlite_sequence" VALUES('sonderaktion',2);
INSERT INTO "sqlite_sequence" VALUES('bestellung',9);
INSERT INTO "sqlite_sequence" VALUES('bestellposition',16);
COMMIT;
