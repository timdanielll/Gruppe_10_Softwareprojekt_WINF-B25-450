---
version: alpha
name: Kassenpult
description: Designsystem für das WI-Fanshop-Kassenterminal der htw saar — eine Desktop-Kasse, die vom Personal stundenlang mit Maus und Tastatur bedient wird.

colors:
  primary: "#161616"
  secondary: "#6A6459"
  tertiary: "#4CC2EE"
  tertiary-hover: "#26B5EA"
  tertiary-soft: "#D6EFFA"
  neutral: "#EFEDE7"
  surface: "#F3F1ED"
  card: "#FCFBF8"
  field: "#FFFFFF"
  on-surface: "#1C1A17"
  border: "#E2DED6"
  error: "#B23A17"
  success: "#5C6B14"
  discount: "#8A5A05"
  htw-green: "#AFCB05"
  htw-blue: "#00A8E7"
  htw-magenta: "#E82C8A"
  htw-orange: "#F7A600"
  surface-dark: "#171512"
  card-dark: "#221F1A"
  neutral-dark: "#2B2721"
  rail-dark: "#121110"
  field-dark: "#0E0D0C"
  on-surface-dark: "#EDE9E1"
  muted-dark: "#A79E90"
  border-dark: "#34302A"
  tertiary-dark: "#F7A823"
  tertiary-hover-dark: "#D98D0B"
  tertiary-soft-dark: "#3A2E12"
  error-dark: "#E8845F"
  success-dark: "#AFCB34"

typography:
  display:
    fontFamily: Segoe UI
    fontSize: 28px
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Segoe UI
    fontSize: 20px
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Segoe UI
    fontSize: 17px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: 0em
  body-md:
    fontFamily: Segoe UI
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.55
  body-sm:
    fontFamily: Segoe UI
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.5
  caption:
    fontFamily: Segoe UI
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4
  label-caps:
    fontFamily: Segoe UI
    fontSize: 11px
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: 0.12em
  numeric-lg:
    fontFamily: Consolas
    fontSize: 22px
    fontWeight: 700
    lineHeight: 1.15
    letterSpacing: 0em
  numeric-md:
    fontFamily: Consolas
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.45
  numeric-sm:
    fontFamily: Consolas
    fontSize: 12px
    fontWeight: 400
    lineHeight: 1.4

rounded:
  none: 0px
  control: 6px
  card: 8px
  dialog: 12px

spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px

components:
  page:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    padding: "{spacing.xl}"
  page-title:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    typography: "{typography.display}"
  card:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.card}"
    padding: "{spacing.lg}"
  card-title:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    typography: "{typography.headline-md}"
    padding: "{spacing.sm}"
  rail:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.none}"
    padding: "{spacing.md}"
    width: 232px
  rail-item-active:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
  rule:
    backgroundColor: "{colors.border}"
    height: 1px
  htw-bar-green:
    backgroundColor: "{colors.htw-green}"
    rounded: "{rounded.none}"
    height: 4px
  htw-bar-blue:
    backgroundColor: "{colors.htw-blue}"
    rounded: "{rounded.none}"
    height: 4px
  htw-bar-magenta:
    backgroundColor: "{colors.htw-magenta}"
    rounded: "{rounded.none}"
    height: 4px
  htw-bar-orange:
    backgroundColor: "{colors.htw-orange}"
    rounded: "{rounded.none}"
    height: 4px
  table-header:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.secondary}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.none}"
    padding: "{spacing.sm}"
    height: 30px
  table-row:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.none}"
    padding: "{spacing.sm}"
    height: 30px
  table-row-selected:
    backgroundColor: "{colors.tertiary-soft}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
  table-cell-numeric:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    typography: "{typography.numeric-md}"
    padding: "{spacing.xs}"
  table-cell-id:
    backgroundColor: "{colors.card}"
    textColor: "{colors.secondary}"
    typography: "{typography.numeric-sm}"
    padding: "{spacing.xs}"
  total-line:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    typography: "{typography.numeric-lg}"
    padding: "{spacing.md}"
  step-active:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.primary}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.control}"
    height: 38px
  step-done:
    backgroundColor: "{colors.tertiary-soft}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.control}"
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
    padding: "{spacing.md}"
    height: 44px
  button-primary-hover:
    backgroundColor: "{colors.tertiary-hover}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
  button-secondary:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
    padding: "{spacing.md}"
    height: 36px
  button-danger:
    backgroundColor: "{colors.error}"
    textColor: "{colors.card}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
    padding: "{spacing.md}"
    height: 36px
  input:
    backgroundColor: "{colors.field}"
    textColor: "{colors.on-surface}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
    padding: "{spacing.sm}"
    height: 36px
  input-error:
    backgroundColor: "{colors.field}"
    textColor: "{colors.error}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.control}"
  hint:
    backgroundColor: "{colors.card}"
    textColor: "{colors.secondary}"
    typography: "{typography.caption}"
  status-line:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.secondary}"
    typography: "{typography.body-sm}"
  chip-stock-ok:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.success}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.control}"
    padding: "{spacing.xs}"
  chip-discount:
    backgroundColor: "{colors.neutral}"
    textColor: "{colors.discount}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.control}"
    padding: "{spacing.xs}"
  dialog:
    backgroundColor: "{colors.card}"
    textColor: "{colors.on-surface}"
    typography: "{typography.headline-lg}"
    rounded: "{rounded.dialog}"
    padding: "{spacing.lg}"
  page-dark:
    backgroundColor: "{colors.surface-dark}"
    textColor: "{colors.on-surface-dark}"
    typography: "{typography.body-md}"
    padding: "{spacing.xl}"
  card-dark:
    backgroundColor: "{colors.card-dark}"
    textColor: "{colors.on-surface-dark}"
    typography: "{typography.body-md}"
    rounded: "{rounded.card}"
    padding: "{spacing.lg}"
  rail-dark:
    backgroundColor: "{colors.rail-dark}"
    textColor: "{colors.on-surface-dark}"
    typography: "{typography.body-md}"
    rounded: "{rounded.none}"
    padding: "{spacing.md}"
  table-header-dark:
    backgroundColor: "{colors.neutral-dark}"
    textColor: "{colors.muted-dark}"
    typography: "{typography.label-caps}"
  table-row-selected-dark:
    backgroundColor: "{colors.tertiary-soft-dark}"
    textColor: "{colors.on-surface-dark}"
    typography: "{typography.body-md}"
  rule-dark:
    backgroundColor: "{colors.border-dark}"
    height: 1px
  input-dark:
    backgroundColor: "{colors.field-dark}"
    textColor: "{colors.on-surface-dark}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
    padding: "{spacing.sm}"
    height: 36px
  input-error-dark:
    backgroundColor: "{colors.card-dark}"
    textColor: "{colors.error-dark}"
    typography: "{typography.body-sm}"
  button-primary-dark:
    backgroundColor: "{colors.tertiary-dark}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
    padding: "{spacing.md}"
    height: 44px
  button-primary-hover-dark:
    backgroundColor: "{colors.tertiary-hover-dark}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
  rail-item-active-dark:
    backgroundColor: "{colors.tertiary-dark}"
    textColor: "{colors.primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.control}"
  chip-stock-ok-dark:
    backgroundColor: "{colors.card-dark}"
    textColor: "{colors.success-dark}"
    typography: "{typography.label-caps}"
    rounded: "{rounded.control}"
    padding: "{spacing.xs}"
---

# Kassenpult

## Overview

Das WI-Fanshop-Kassenterminal ist kein Webshop. Es ist vor allem ein Arbeitsgerät, das während der Öffnungszeiten dauerhaft offen steht und von Kassenpersonal mit Maus und Tastatur bedient wird. Vor dem Arbeitsbereich wählt eine kompakte Startansicht jedoch die Zugangsart: Kunden gelangen nur zur Kasse, Kassierer in alle Fachbereiche. Alles in diesem System folgt daraus: Der Bildschirm muss über Stunden ermüdungsfrei lesbar sein, Zahlen müssen sich beim Überfliegen einer Spalte vergleichen lassen, und die eine Schaltfläche, die Geld und Lagerbestand verändert, muss auch dann sofort auffindbar sein, wenn jemand danebensteht und wartet.

Die Richtung heißt **institutionelles Schweizer Raster in Kassenpult-Dichte**. Sie ist nicht frei gewählt, sondern aus der Hausmarke der htw saar abgeleitet: schwarze Wortmarke, eine einzige Fakultätsfarbe als Signal, viel Weißraum, Haarlinien statt Rahmen, Akkurat als Grotesk. Die Hochschule macht damit bereits Schweizer Typografie — dieses System führt sie nur in eine höhere Informationsdichte weiter, wie sie ein Kassenterminal braucht.

**Was das System dafür aufgibt:** Freundlichkeit. Es gibt keine abgerundeten Pillen-Buttons, keine Farbkodierung der sieben Warenkategorien, keine Schatten, keine Illustrationen, keine Animation außer dem Fokuswechsel. Ein Nutzer, der die Anwendung zum ersten Mal sieht, findet sie nüchtern. Ein Nutzer, der sie in der vierten Stunde bedient, findet jede Zahl ohne hinzusehen. Für ein Gerät, das dauerhaft läuft, ist der zweite Fall der wichtigere — das ist der Tausch, den dieses System bewusst eingeht.

Zweite bewusste Beschränkung: **Farbe trägt in diesem System keine Information, außer bei Fehlern.** Bestände, Kategorien, Kundenzustände werden über Position, Schriftschnitt und Text unterschieden. Grund ist der Einsatzort — ein Kassenrechner steht unter wechselndem Licht, oft mit schlechtem Blickwinkel, und die Anwendung muss auch dann funktionieren, wenn Farbtöne kippen.

## Colors

Die Palette hat genau eine Quelle: das Corporate Design der htw saar. Das Gold ist die Farbe der **Fakultät für Wirtschaftswissenschaften** — derselbe Wert, den die Hochschule auf htwsaar.de für WiWi-Seiten verwendet und den das Fakultätslogo im Repository trägt. Das Schwarz ist das Schwarz der Wortmarke. Beides ist gesetzt und nicht verhandelbar; die gestalterische Arbeit steckt deshalb in den Neutraltönen.

Dazu kommt der **Vierfarbbalken** der Hochschule — Grün, Blau, Magenta, Orange, entnommen aus `assets/favicon.png`. Er ist die Klammer, die alle vier Fakultäten verbindet, und er hat in diesem System genau einen Platz: als 4 px hoher Streifen unter der Wortmarke in der Navigationsleiste. Er ist Herkunftszeichen, nicht Dekoration, und taucht deshalb an keiner zweiten Stelle auf.

**Zwei Identitäten, ein System.** Im Hellmodus trägt die Leiste die reine schwarze Wortmarke plus den Vierfarbbalken — so tritt die Hochschule nach außen auf. Bewusst die Wortmarke allein und nicht die Kompaktvariante mit Zusatzzeile: In einer 232 Pixel breiten Leiste wäre der Zusatztext unleserlich klein und würde der Wortmarke die Größe nehmen. Im Dunkelmodus wechselt sie auf das goldene Fakultätslogo, das auf dunklem Grund von selbst leuchtet und den Balken überflüssig macht. Beide Varianten liegen als Datei bei; keine wird nachgebaut.

Und dort gibt es eine Abweichung vom Original, die begründet werden muss: Die Website der Hochschule steht auf reinem Weiß. Dieses System nicht. Alle Neutraltöne sind **warm getönt** (Gelb-Rot-Achse, dieselbe Achse, auf der das Gold liegt) — Papierweiß statt Bildschirmweiß, Karton statt Grau. Über eine Achtstundenschicht auf einem Kassenmonitor ist reines Weiß neben reinem Schwarz die anstrengendste Kombination, die man wählen kann. Die warme Tönung kostet nichts an Markenwiedererkennung und nimmt dem Bildschirm die Härte.

- **Primary (#161616):** *Wortmarken-Schwarz* — die Farbe der Marke, eingesetzt als Fläche: Navigationsleiste, Schrift auf goldenen Flächen. Nicht als Fließtextfarbe.
- **On-Surface (#1C1A17):** *Druckerschwärze* — dasselbe Schwarz, minimal ins Warme gezogen, damit es auf dem warmen Papierton nicht bläulich absticht. Das ist die Farbe, in der man liest.
- **Secondary (#5B554E):** *Bleistift* — Spaltenköpfe, Hilfetexte, Datensatznummern. Alles, was da sein muss, aber nicht gelesen werden will.
- **Tertiary — der Akzent, je Modus ein anderer.** Er hat genau eine Aufgabe: **er markiert, was Geld oder Lagerbestand verändert.** Der Button „Kauf abschließen", der Button „Retoure buchen", der aktive Navigationseintrag, der aktuelle Schritt der Strecke. Sonst nirgends, auf weniger als 5 % der Fläche.
  - **Hell: htw-Blau (#4CC2EE)** — das Blau des Vierfarbbalkens, um 30 % aufgehellt. Der Balkenton selbst (#00A8E7) war als Buttonfläche zu dunkel: Die schwarze Schrift darauf kam auf 6,7:1 und wirkte stumpf. Aufgehellt sind es 8,8:1 — praktisch derselbe Wert wie beim Gold.
  - **Dunkel: WiWi-Gold (#F7A823)** — die Farbe der Fakultät, 9,1:1.

  Der reine Balkenton bleibt dem Vierfarbbalken vorbehalten. Der Akzent ist seine hellere Schwester, nicht derselbe Wert — eine Fläche von 200 px Breite verträgt einen anderen Ton als ein 4 px hoher Streifen.

  Warum zwei? Weil die Leiste dieselbe Trennung schon trägt: Im Hellmodus steht dort die allgemeine htw-saar-Wortmarke, im Dunkelmodus das Fakultätslogo. Der Akzent folgt dem Logo, statt ihm zu widersprechen. Beide tragen schwarze Schrift und erfüllen WCAG AA (8,84 bzw. 9,12).
- **Tertiary-Hover (#26B5EA / #D98D0B):** je eine Stufe dunkler. Beim Gold ist die dunklere Stufe leicht ins Rote gedreht statt einfach abgedunkelt — ein rein abgedunkeltes Gold wirkt schmutzig.
- **Neutral (#F2F0EC):** *Karton* — die Fläche von Panels, Tabellenköpfen und Dialogen. Trennt Bereiche voneinander, ohne eine Linie zu ziehen.
- **Surface (#FBFAF8):** *Papier* — der Hintergrund der Anwendung und der Tabellenzeilen.
- **Border (#DCD7CF):** *Falzlinie* — Haarlinien. Dieses System hat keine Schatten, Trennung passiert hier.
- **Error (#B23A17):** *Stempelrot* — aus der Gold-Familie gewonnen, nicht importiert: gleicher Farbwinkel-Bereich, Sättigung hoch, Helligkeit weit heruntergezogen. Steht neben dem Gold wie ein Stempel neben einem Formular und nicht wie eine Warnleuchte aus einem anderen System. Einziger Fall, in dem Farbe Information trägt.
- **Success (#5C6B14):** *AuB-Grün, gedeckt* — abgeleitet aus dem Fakultätsgrün für Architektur und Bauingenieurwesen (#AFCB34), so weit abgedunkelt, bis es auf Karton AA erreicht. Bleibt damit im Farbraum der Hochschule. Sehr sparsam: nur „Bestand ausreichend".
- **Discount (#8A5A05):** *Gold als Schrift* — für Rabattzeilen, in **beiden** Modi bernsteinfarben. Das ist Absicht: Der Akzent bedeutet „hier kann ich klicken", Bernstein bedeutet „hier geht Geld ab". Zwei Bedeutungen, zwei Farben — auch dort, wo der Akzent selbst blau ist. Nebenbei existiert `discount`, damit niemand in Versuchung gerät, `tertiary` als Schriftfarbe zu benutzen; als Text wäre es unlesbar.

**Dunkelmodus** (Kann-Kriterium /F54/). Der Dunkelmodus ist keine Invertierung, sondern dieselbe Palette auf der anderen Seite: Der warme Ton bleibt warm (#1A1815 ist braunstichiges Anthrazit, kein blaustichiges Marineblau), das Gold bleibt exakt gleich — es hält auf beiden Untergründen —, und der Text wird nie reinweiß, sondern gebrochenes Warmweiß (#EDE9E1). Eingabefelder sind im Dunkelmodus **dunkler** als ihre Umgebung (#141210), im Hellmodus **heller** — in beiden Fällen ist das Feld die Vertiefung, in die geschrieben wird.

## Typography

Die Hausschrift der htw saar ist **Akkurat** (Lineto). Sie ist kommerziell lizenziert und darf in diesem Projekt nicht mitgeliefert werden. Das System benennt deshalb eine Grotesk, die auf allen geforderten Betriebssystemen vorhanden ist, und beschreibt die Ersatzkette in der Prosa statt sie in die Tokens zu pressen.

**Zwei Schriften, unterschiedlicher Klassifikation** — und die Trennung verläuft hier nicht nach Wichtigkeit, sondern nach Datentyp:

1. **Grotesk (Token: `Segoe UI`)** für alles, was Sprache ist: Bezeichnungen, Titel, Beschreibungen, Buttons. Ersatzkette: `Segoe UI` (Windows) → `Helvetica Neue` (macOS) → `DejaVu Sans` (Linux). Alle drei sind neutrale Grotesken derselben Familie wie Akkurat; keine ist eine Auffälligkeit.
2. **Monospace (Token: `Consolas`)** für alles, was Zahl ist: Preise, Summen, Mengen, Kunden- und Artikelnummern, Zeitstempel. Ersatzkette: `Consolas` → `Menlo` → `DejaVu Sans Mono`.

Der zweite Punkt ist die eigentliche typografische Entscheidung des Systems und der Grund, warum es sich beim Benutzen anders anfühlt als ein Standard-Tkinter-Programm. In einer Kasse liest niemand Zeilen, man vergleicht Spalten: Passt die Summe? Ist der Bestand kleiner als die Menge? Mit einer Proportionalschrift stehen die Ziffern nicht untereinander und diese Frage kostet jedes Mal einen bewussten Blick. Mit Dickengleichheit steht sie fest. Deshalb gibt es die drei Stufen `numeric-sm`, `numeric-md` und `numeric-lg` — und deshalb ist die Gesamtsumme des Warenkorbs mit 22 px dickengleich fett das größte Element auf dem ganzen Bildschirm. Sie ist die Zahl, die der Kunde gleich hört.

**Genau zwei Schriftschnitte: 400 und 700.** Das ist zur Hälfte Haltung — 400/700 ist eine Entscheidung, 400/500/600 ist eine Voreinstellung — und zur Hälfte Plattformrealität: Tkinter kann Zwischenschnitte auf keinem der drei Betriebssysteme verlässlich auflösen und fällt still auf `normal` zurück. Ein System, das hier drei Schnitte verspricht, lügt.

Die Skala ist mit Verhältnis ≈1,2 aufgebaut (11 → 12 → 14 → 17 → 20 → 28) und damit dichter als eine redaktionelle Skala. Die Zeilenhöhe läuft gegen die Schriftgröße: 1,55 bei 14 px Fließtext, 1,05 bei 28 px Titel. Laufweite gegenläufig: −0,02 em auf Display, +0,12 em auf den 11-px-Versallabels. **Einschränkung:** Tkinter kennt keine Laufweite. Die Werte sind für die Berichts- und Belegausgabe normativ; in der Oberfläche werden Versallabels statt dessen durch zusätzlichen Innenabstand geöffnet. Fließtext darf 14 px nicht unterschreiten, Zahlen nicht 12 px.

## Layout

Beim Start zeigt die Anwendung zunächst eine **kompakte Auswahlkarte** ohne Navigation. Sie fragt nach der Zugangsart und bietet zwei gleichwertige sekundäre Schaltflächen. Erst nach dieser Wahl erscheint die feste Zweiteilung: eine **232 px breite Navigationsleiste links** über die volle Höhe, rechts daneben der Arbeitsbereich. Die Leiste ist die einzige Konstante der Fachansicht. Sie trägt oben das Logo der htw saar und ist im Hellmodus hell — durch eine Haarlinie von der Seite getrennt —, im Dunkelmodus die dunkelste Fläche des Fensters. Der aktive Eintrag ist die einzige Stelle, an der dort Gold vorkommt.

Der Arbeitsbereich ist **asymmetrisch geteilt und zwar immer in dieselbe Richtung**: Links die Auswahl (Suchen, Filtern, Finden), rechts das Ergebnis der Auswahl (Warenkorb, Kundendetails, Bestellpositionen). Das Verhältnis ist ungefähr 3:2 zugunsten links. Diese Aufteilung gilt auf allen fünf Fachseiten, auch dort, wo sie nicht zwingend wäre — der Bediener soll nach der zweiten Schicht nicht mehr suchen müssen, wo etwas steht. Im Kundenzugang wird davon ausschließlich die Kassenseite angezeigt.

Raster: 4-px-Basis, alle Abstände sind Vielfache. Der Seitenrand ist 40 px, Panels sind innen 24 px gepolstert, zusammengehörige Steuerelemente stehen 8 px auseinander, unabhängige Gruppen 24 px. Tabellenzeilen sind 26 px hoch — dicht genug, dass 18 Artikel ohne Scrollen sichtbar sind, hoch genug zum sicheren Treffen mit der Maus.

Fließtext (Artikelbeschreibungen) wird auf etwa 70 Zeichen begrenzt; alles darüber wird umbrochen, nicht in die Breite gezogen. Die Mindestfenstergröße ist 1280 × 800. Darunter wird nichts umsortiert — die Anwendung läuft auf einem Kassenrechner mit bekanntem Bildschirm, nicht auf beliebigen Geräten; ein responsives Umbruchverhalten wäre hier erfundene Komplexität.

## Elevation & Depth

**Dieses System benutzt keine Schatten.** Nicht abgeschwächt, nicht farbig — gar nicht. Es gibt in einer Kasse nichts, was über etwas anderem schwebt, außer dem einen modalen Dialog.

Tiefe entsteht aus drei Mitteln, in dieser Reihenfolge:

1. **Tonwert.** Die Seite ist leicht abgetönt (`surface`), die Karten darauf sind fast weiß (`card`). Das ist die Umkehrung der ersten Fassung und der Grund, warum die Oberfläche jetzt nach Arbeitsfläche aussieht statt nach Formular: Inhalt liegt sichtbar auf dem Untergrund. Im Dunkelmodus gilt dasselbe seitenverkehrt — die Karte ist heller als die Seite. Mehr als zwei Ebenen gibt es nicht.
2. **Haarlinie.** 1 px in `border`, nie dicker. Tabellen bekommen ausschließlich waagerechte Linien, keine senkrechten — die Spalten werden durch Ausrichtung getrennt, und dickengleiche Zahlen brauchen kein Gitter.
3. **Weißraum.** Der Standardweg, Gruppen zu trennen. Eine Linie wird erst gezogen, wenn der Abstand allein nicht reicht.

Einzige Ausnahme ist der modale Dialog (Fehlermeldung nach /NF11/, Sticker-Bestätigung nach /F53/): Er liegt tatsächlich über der Anwendung, ist deshalb das einzige Element mit 8 px Radius, und der Hintergrund wird nicht abgedunkelt, sondern der Dialog wird schlicht mittig gesetzt und nimmt den Fokus. Er hat immer eine sichtbare Schaltfläche zum Schließen und lässt sich immer mit Escape verlassen.

Fokus ist die einzige Stelle mit sichtbarer Zustandsänderung: 2 px Rahmen in `tertiary` um das fokussierte Element. Er wird nie entfernt — die Anwendung wird zu großen Teilen mit der Tastatur bedient.

## Shapes

**Der Radius sagt, ob man klicken kann.**

- `none` (0 px) für Flächen, die randlos an etwas anstoßen: Navigationsleiste, Tabellenkopf und Tabellenzeilen, der Vierfarbbalken.
- `control` (6 px) für alles, was auf Eingabe reagiert: Buttons, Eingabefelder, Auswahllisten, Chips, die Schritte der Strecke.
- `card` (8 px) für Karten — die Flächen, die auf der Seite liegen.
- `dialog` (12 px) ausschließlich für das modale Fenster, das wirklich über allem liegt.

Vier Stufen, und jede sagt etwas anderes: 0 heißt „gehört zur Fläche", 6 heißt „reagiert auf Klick", 8 heißt „liegt auf der Seite", 12 heißt „liegt über der Seite". Ein einheitlicher Radius würde diese Information wegwerfen.

Rahmen: 1 px `border` auf Eingabefeldern und Sekundärbuttons. Der Primärbutton hat keinen Rahmen — er ist Fläche. Der Gefahrenbutton hat keinen Rahmen — er ist Fläche. Keine gestrichelten Linien, keine doppelten Rahmen, keine Verläufe. Es gibt im ganzen System keinen einzigen Farbverlauf. Der Vierfarbbalken der Hochschule ist kein Verlauf, sondern vier harte Flächen nebeneinander — und er steht ausschließlich unter der Wortmarke.

Bilder: Artikelfotos sind rechteckig, ohne Radius, ohne Rahmen, auf `neutral` gesetzt und auf maximal 160 px Kantenlänge skaliert. Ein Produktfoto ist Information, kein Schmuck.

## Components

**Navigationsleiste (`rail`).** Im Kassiererzugang hat sie fünf Einträge, Reihenfolge fest und identisch mit dem Arbeitsablauf: Kasse, Sortiment, Kunden, Retouren, Berichte. Im Kundenzugang besteht sie ausschließlich aus Kasse. Kasse steht oben, weil sie in 90 % der Fälle gemeint ist. Der aktive Eintrag bekommt Goldfläche mit schwarzer Schrift; inaktive Einträge sind Papierweiß auf Schwarz. Unten in der Leiste steht der Schalter für den Dunkelmodus, weil er zur Anwendung gehört und nicht zur Aufgabe.

**Tabellen.** Kopfzeile in `table-header`: Versallabel, Kartonfläche, unten eine Haarlinie. Zahlenspalten sind **rechtsbündig** und benutzen `table-cell-numeric`, Textspalten linksbündig, Identifikationsnummern `table-cell-id`. Keine Zebrastreifen — bei 30 px Zeilenhöhe und ausgerichteten Zahlen sind sie überflüssig und machen die Fläche unruhig. Die ausgewählte Zeile bekommt `tertiary-soft`, also stark aufgehelltes Gold, und behält ihre normale Schriftfarbe. Volltongold auf der Auswahl war die erste Fassung; es zog bei jedem Klick den Blick vom Inhalt weg.

**Buttons.** Pro Fachseite gibt es **genau einen** `button-primary`. Er trägt die Aktion, die etwas Unwiderrufliches tut: „Kauf abschließen", „Retoure buchen", „Artikel anlegen". Alles andere ist `button-secondary`. Die beiden Knöpfe der Zugangsart sind ebenfalls `button-secondary`, weil sie nur die Ansicht wählen. `button-danger` ist Stempelrot und ausschließlich für Löschen und Deaktivieren reserviert. Ein Button ist immer beschriftet, niemals nur ein Symbol — die Kasse wird auch von Aushilfen bedient, die das Programm nicht kennen.

Beschriftungen stehen in **normaler Schreibweise**, nicht in Versalien. Versalien bleiben den 11-px-Labels über den Eingabefeldern vorbehalten, wo sie Struktur markieren; auf einem Button lesen sie sich als Anschrei.

**Eingabefelder (`input`).** Jedes Feld hat ein **sichtbares Label darüber**. Platzhaltertext ersetzt niemals ein Label: Er verschwindet beim Tippen, und dann weiß niemand mehr, was in dem Feld steht. Validiert wird **beim Verlassen des Feldes und beim Absenden**, nicht bei jedem Tastendruck. Fehlerhafte Felder bekommen `input-error` als Text unter dem Feld — zusätzlich zum Dialog aus /NF11/, denn ein Dialog verschwindet und der Fehler bleibt.

**Summenzeile (`summenzeile`).** Steht immer unten rechts, immer an derselben Stelle, immer in `numeric-lg`. Zwischensumme, Rabattzeilen und Endbetrag stehen untereinander und rechtsbündig; die Rabattzeilen benutzen `chip-rabatt` als Text. Der Endbetrag ist das größte Element der Seite.

**Erledigte Zeilen.** Eine Tabellenzeile, deren Vorgang abgeschlossen ist — etwa eine Retourenposition, die vollständig zurückgegeben wurde — bekommt graue Schrift auf gedämpfter Fläche und zeigt „zurück" statt einer 0. Das ist eine Gestaltungsentscheidung mit Konsequenz: **Zustand wird gezeigt, nicht erklärt.** Vorher öffnete ein Klick auf so eine Zeile einen Fehlerdialog; jetzt sieht man schon vor dem Klick, dass dort nichts mehr zu holen ist, und bekommt höchstens eine Zeile in der Statusleiste.

**Chips.** `chip-bestand-ok` und `chip-rabatt` sind kleine Versallabels auf Kartonfläche. Sie sind Beiwerk und dürfen nie die einzige Quelle einer Information sein — die Menge steht immer auch als Zahl daneben.

**Dialoge (`dialog`).** Drei Anlässe, mehr nicht: Fehler (/NF11/), Sicherheitsabfrage vor unwiderruflichen Aktionen, Bestätigung der Stickerausgabe (/F53/). Ein Dialog stellt eine Frage und hat höchstens zwei Antworten. Der Sticker-Dialog zeigt die Anzahl groß in `numeric-lg` und ein Stickerbild aus `assets/sticker/`; er ist die einzige Stelle im ganzen System, an der etwas Freundliches passieren darf.

**Strecke (`step-active` / `step-done`).** Mehrstufige Vorgänge — im Moment nur die Kasse — bekommen oben eine Strecke aus nummerierten Schritten. Der aktuelle Schritt ist golden gefüllt, erledigte sind golden umrandet und anklickbar, spätere sind grau und gesperrt. Vorwärts springt man nur über „Weiter", damit kein Schritt übersprungen wird. Unten links steht immer „Zurück", unten rechts „Weiter" — an derselben Stelle wie in jedem Formular, das der Bediener sonst kennt.

**Statuszeile (`status-line`).** Ganz unten auf jeder Seite, eine Zeile hoch. Nach jeder Aktion steht dort, was passiert ist („2 × Lineal htw saar in den Warenkorb."), nach vier Sekunden fällt sie auf „Bereit." zurück. Sie ist der Grund, warum geglückte Aktionen **keinen** Dialog mehr öffnen: Ein Dialog, den man wegklicken muss, um weiterzuarbeiten, ist für eine Kasse die falsche Rückmeldung.

**Artikelkarte.** Wo ein Artikel ausgewählt wird, steht rechts seine Karte: Produktfoto, Titel, Kategorie und Größe, Beschreibung, Preis in `numeric-lg` und der Lagerbestand — grün, solange mehr als drei Stück da sind, sonst rot. Das Foto ist Information: Der Bediener dreht den Bildschirm zum Kunden, statt das Produkt zu beschreiben.

**Sammelalbum.** Die sechs Stickermotive stehen nebeneinander; vorhandene in Farbe, fehlende grau und aufgehellt. Darüber „Sammlung · 4 von 6 Motiven". Aus dem Zähler wird dadurch eine Sammlung — das ist der ganze Zweck des Gamification-Moduls.

**Spaltenbreiten rechnet die Tabelle selbst.** Die Breiten im Quelltext sind ein *Vorschlag*, kein Versprechen. Bei jeder Größenänderung verteilt `Tabelle._breiten_anpassen()` den tatsächlich vorhandenen Platz neu:

1. Jede Spalte bekommt mindestens die gemessene Breite ihrer eigenen Überschrift — gemessen, nicht geschätzt.
2. Bleibt Platz übrig, geht er an die breiteste Spalte (in der Regel der Titel).
3. Fehlt Platz, werden alle Spalten anteilig gekürzt, aber keine unter ihr Minimum.
4. Reicht selbst die Summe der Minima nicht — sehr kleines Fenster, hohe Windows-Skalierung —, werden alle gleichmäßig gestaucht.

Der Grund für den ganzen Aufwand: `ttk` hat keine waagerechte Bildlaufleiste. Was nicht passt, wird **abgeschnitten**, und zwar rechts — die letzte Spalte verschwindet ganz. Eine Spalte, die aus dem Bild fällt, ist schlimmer als sechs, die etwas schmaler sind.

**Formulare mit fester Knopfleiste.** Ist ein Formular länger als die Karte hoch ist, scrollt das **Formular** — nie die Knopfleiste. Sie wird zuerst und mit `side="bottom"` gesetzt, damit `pack` ihren Platz reserviert, bevor der Rest gefüllt wird. Ein „Speichern", das man nur durch Scrollen erreicht, ist auf einem Kassenterminal ein Fehler.

**Zustände.** Jede Liste hat einen definierten Leerzustand mit einem Satz, der sagt, was zu tun ist („Keine Artikel gefunden. Filter zurücksetzen?") — nie eine leere Fläche. Beim Wechsel zwischen Seiten bleiben Suchtext, Filter und Auswahl erhalten; eine Seite wird nicht zurückgesetzt, nur weil man kurz woanders war.

## Do's and Don'ts

- **Do** den Akzent ausschließlich für die eine Aktion pro Bildschirm verwenden, die Geld oder Lagerbestand verändert, und für den aktiven Navigationseintrag.
- **Do** den Akzent immer über `farbe("akzent")` holen, nie als Hexwert hinschreiben — sonst bleibt er im falschen Modus stehen.
- **Don't** den Akzent als Schriftfarbe verwenden. Dafür existiert `discount`.
- **Don't** eine dritte Akzentfarbe einführen. Zwei gibt es nur, weil Hell- und Dunkelmodus zwei verschiedene Logos tragen; innerhalb eines Modus ist es genau eine.
- **Do** jede Geldsumme, jede Menge und jede laufende Nummer in einer der drei `numeric`-Stufen setzen und rechtsbündig ausrichten.
- **Don't** Geldbeträge in `body-md` setzen, auch nicht „nur kurz" in einem Label. Sobald eine Zahl in einer Spalte steht, ist sie dickengleich.
- **Do** Beträge über `hilfsmittel.euro()` formatieren — deutsches Format mit Komma und Tausenderpunkt, Währungszeichen hinten.
- **Do** Trennung durch Abstand lösen; eine Haarlinie erst ziehen, wenn 24 px Abstand nicht reichen.
- **Don't** Schatten hinzufügen, auch keine „ganz dezenten". Das System hat keine Schattenfarbe, weil es keine Schatten hat.
- **Do** den Radius nach Funktion vergeben: 0 für randlose Flächen, 6 für Bedienelemente, 8 für Karten, 12 nur für den Dialog.
- **Don't** die sieben Warenkategorien einfärben. Kategorien werden durch den Filter und die Spalte unterschieden, nicht durch Farbe.
- **Do** jedem Eingabefeld ein sichtbares Label geben und beim Verlassen des Feldes validieren.
- **Don't** Platzhaltertext als Label missbrauchen und nicht bei jedem Tastendruck validieren.
- **Do** jede Liste mit einem formulierten Leerzustand versehen.
- **Do** abgeschlossene Zeilen grau markieren, statt beim Klick zu erklären, warum nichts passiert.
- **Do** Felder, die nebeneinander stehen, oben ausrichten — eine Fehlerzeile unter einem Feld darf die Nachbarn nicht nach unten schieben.
- **Don't** einen zweiten Akzentton einführen. Braucht etwas mehr Gewicht, bekommt es Schriftschnitt 700 oder mehr Abstand — keine neue Farbe.
- **Do** jeden mehrstufigen Vorgang als Strecke zeigen und pro Schritt nur das, was dort gebraucht wird.
- **Do** nach jeder Aktion in die Statuszeile schreiben, was passiert ist — auch wenn nichts schiefging.
- **Don't** einen Dialog öffnen, um eine geglückte Aktion zu bestätigen. Dialoge sind für Fehler, Rückfragen und den Kaufabschluss.
- **Do** Schaltflächen, die etwas speichern oder löschen, unten in der Karte verankern und den Rest scrollen lassen.
- **Do** Spaltenüberschriften vollständig zeigen — lieber eine Spalte streichen als sechs abschneiden.
- **Do** den Fokusrahmen im Akzent sichtbar lassen; die Kasse wird mit der Tastatur bedient.
- **Do** den Vierfarbbalken genau einmal zeigen: unter der Wortmarke in der Navigationsleiste.
- **Don't** die vier htw-Farben irgendwo sonst verwenden — nicht für Kategorien, nicht für Diagramme, nicht als Schriftfarbe.
- **Do** im Dunkelmodus dieselben warmen Töne benutzen; Eingabefelder werden dunkler als ihre Umgebung, nicht heller.
- **Don't** im Dunkelmodus reinweißen Text (#FFFFFF) oder blaustichiges Anthrazit verwenden.
