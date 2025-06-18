# 📖 MIFARE Classic Tool - Szczegółowa Instrukcja Obsługi

## 🎯 Dla kogo jest ta instrukcja?

Ta instrukcja jest przeznaczona dla początkujących użytkowników, którzy nie mają doświadczenia z:
- Kartami MIFARE Classic
- Czytnikami NFC
- Operacjami na kartach zbliżeniowych
- Narzędziami bezpieczeństwa

## ⚠️ WAŻNE OSTRZEŻENIA PRZED ROZPOCZĘCIEM

🚨 **PRZECZYTAJ TO UWAŻNIE:**

1. **Nigdy nie testuj na ważnych kartach!** 
   - Używaj tylko kart testowych lub jednorazowych
   - Błędne operacje mogą PERMANENTNIE zablokować kartę

2. **Zachowaj ostrożność z kluczami:**
   - Zmiana kluczy bez znajomości może zablokować kartę na zawsze
   - Zawsze zanotuj oryginalne klucze przed zmianami

3. **Legalność:**
   - Używaj tylko na własnych kartach lub za zgodą właściciela
   - Sprawdź lokalne przepisy dotyczące kart RFID

## 🛠️ Wymagania sprzętowe

### Co potrzebujesz:

1. **Komputer:**
   - Windows 10/11, macOS 10.14+, lub Linux Ubuntu 18.04+
   - Port USB
   - Połączenie z internetem (do instalacji)

2. **Czytnik ACR1252U:**
   - Oryginalny czytnik ACS ACR1252U
   - Kabel USB (dołączony do czytnika)

3. **Karty MIFARE Classic:**
   - MIFARE Classic 1K lub 4K
   - Karty testowe (zalecane na początek)

## 📥 Instalacja krok po kroku

### Krok 1: Instalacja sterowników czytnika

#### Windows:
1. Pobierz sterowniki z oficjalnej strony ACS
2. Podłącz czytnik ACR1252U do portu USB
3. Uruchom instalator sterowników jako administrator
4. Postępuj zgodnie z instrukcjami na ekranie
5. Uruchom ponownie komputer

#### macOS:
1. Podłącz czytnik - sterowniki powinny zainstalować się automatycznie
2. Jeśli nie działa, pobierz sterowniki z strony ACS
3. Sprawdź w "Informacje o systemie" → USB, czy czytnik jest widoczny

#### Linux (Ubuntu/Debian):
```bash
# Otwórz terminal i wpisz:
sudo apt update
sudo apt install pcscd pcsc-tools libpcsclite-dev
sudo systemctl start pcscd
sudo systemctl enable pcscd

# Sprawdź, czy działa:
pcsc_scan
```

### Krok 2: Instalacja Python

#### Windows:
1. Idź na https://python.org/downloads/
2. Pobierz Python 3.8 lub nowszy
3. Podczas instalacji **ZAZNACZ "Add Python to PATH"**
4. Uruchom instalator i poczekaj na zakończenie

#### macOS:
```bash
# Jeśli masz Homebrew:
brew install python

# Lub pobierz z python.org
```

#### Linux:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Krok 3: Przygotowanie projektu

1. **Pobierz projekt:**
   - Przejdź do folderu `/Users/mk/Desktop/NFC-tool` (na macOS)
   - Lub skopiuj folder gdzie indziej

2. **Otwórz terminal/wiersz poleceń:**
   - Windows: `Win + R`, wpisz `cmd`, Enter
   - macOS: `Cmd + Space`, wpisz `Terminal`, Enter
   - Linux: `Ctrl + Alt + T`

3. **Przejdź do folderu projektu:**
```bash
cd /ścieżka/do/NFC-tool
# Na przykład:
# Windows: cd C:\Users\Twoje_Imie\Desktop\NFC-tool
# macOS: cd /Users/mk/Desktop/NFC-tool
# Linux: cd ~/Desktop/NFC-tool
```

4. **Utwórz środowisko wirtualne:**
```bash
python -m venv venv
```

5. **Aktywuj środowisko wirtualne:**
```bash
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

Po aktywacji powinieneś zobaczyć `(venv)` na początku linii w terminalu.

6. **Zainstaluj wymagane biblioteki:**
```bash
pip install -r requirements.txt
```

Instalacja może potrwać kilka minut.

## 🚀 Pierwsze uruchomienie

### Krok 1: Sprawdź czytnik

1. **Podłącz czytnik ACR1252U** do portu USB
2. **Sprawdź, czy działa:**
   - Windows: Menedżer urządzeń → Czytniki kart inteligentnych
   - macOS/Linux: `pcsc_scan` w terminalu

### Krok 2: Uruchom aplikację

```bash
# Upewnij się, że jesteś w folderze projektu i środowisko jest aktywne
python main.py
```

Powinna otworzyć się aplikacja z interfejsem graficznym.

## 🖥️ Poznanie interfejsu

### Główne okno aplikacji składa się z:

1. **Lewa strona:**
   - **Panel statusu czytnika** (góra)
   - **Informacje o karcie** (środek)
   - **Panel autoryzacji** (dół)

2. **Prawa strona:**
   - **Operacje na blokach** (góra)
   - **Zaawansowane operacje bezpieczeństwa** (dół)

3. **Pasek menu** (góra okna)
4. **Pasek statusu** (dół okna)

### Panel statusu czytnika:
- **Status:** Pokazuje czy czytnik jest podłączony
- **Reader:** Lista dostępnych czytników
- **Przycisk "Connect":** Łączy z czytnikiem
- **Informacje:** Nazwa i wersja firmware czytnika

### Panel informacji o karcie:
- **Status:** Czy karta jest obecna
- **Type:** Typ karty (MIFARE Classic 1K/4K)
- **UID:** Unikalny identyfikator karty
- **Size:** Rozmiar pamięci karty
- **Sectors:** Liczba sektorów

## 📋 Podstawowe operacje - krok po kroku

### 🔌 Połączenie z czytnikiem

1. **Podłącz czytnik** ACR1252U do USB
2. **Kliknij "Refresh"** w panelu Reader Status
3. **Wybierz czytnik** z listy (powinien zawierać "ACR1252")
4. **Kliknij "Connect"**
5. **Sprawdź status** - powinien pokazać "Connected" na zielono

❌ **Jeśli nie działa:**
- Sprawdź kabel USB
- Spróbuj inny port USB
- Zrestartuj aplikację
- Sprawdź sterowniki czytnika

### 📱 Wykrywanie karty

1. **Połóż kartę MIFARE Classic** na czytniku
2. **Poczekaj 1-2 sekundy** - karta powinna zostać wykryta automatycznie
3. **Sprawdź panel "Card Information":**
   - Status powinien pokazać "Present" na zielono
   - Typ karty (1K lub 4K)
   - UID karty (unikalny numer)

❌ **Jeśli karta nie jest wykrywana:**
- Sprawdź, czy karta jest MIFARE Classic
- Umieść kartę dokładnie na środku czytnika
- Usuń i połóż kartę ponownie
- Sprawdź, czy karta nie jest uszkodzona

### 🔐 Autoryzacja sektora (podstawowe)

**Co to jest autoryzacja?**
Karty MIFARE Classic są podzielone na sektory. Każdy sektor ma swoje klucze dostępu (Key A i Key B). Żeby odczytać lub zapisać dane, musisz się najpierw autoryzować kluczem.

**Autoryzacja z domyślnym kluczem:**

1. **W panelu Authentication:**
   - Wybierz **Sector: 0** (zacznij od sektora 0)
   - Zostaw **Key Type: Key A**
   - **Zaznacz** "Use default key (FF FF FF FF FF FF)"

2. **Kliknij "Authenticate"**

3. **Sprawdź wynik:**
   - ✅ Sukces: "Sector 0 authenticated" na zielono
   - ❌ Błąd: "Authentication failed" na czerwono

**Jeśli domyślny klucz nie działa:**

1. **Kliknij "Try Default Keys"** - aplikacja spróbuje kilku popularnych kluczy
2. **Jeśli nadal nie działa** - karta używa niestandardowych kluczy

### 📖 Odczyt bloku

**Po pomyślnej autoryzacji sektora:**

1. **Przejdź do panelu "Block Operations"**
2. **Wybierz numer bloku:**
   - Sektor 0: bloki 0, 1, 2, 3
   - Sektor 1: bloki 4, 5, 6, 7
   - itd.

3. **Zalecenie:** Zaznacz "Auto-read on block change"

4. **Kliknij "Read Block"**

5. **Wynik pojawi się w polu "Block Data":**
   - Format: HEX | ASCII
   - Przykład: `00 11 22 33 44 55 66 77 88 99 AA BB CC DD EE FF | .."3DUfw....`

**Interpretacja danych:**
- **Lewa strona:** Dane w formacie szesnastkowym
- **Prawa strona:** Interpretacja ASCII (litery i cyfry)
- **Kropki (.):** Znaki niedrukowalne

### ✏️ Zapis bloku

⚠️ **UWAGA:** Zapis może uszkodzić kartę! Zawsze testuj na kartach do testów!

1. **Autoryzuj sektor** (jak powyżej)
2. **Wybierz blok do zapisu** (NIE trailer block)
3. **W polu "Write Data" wpisz 32 znaki hex:**
   - Przykład: `00112233445566778899AABBCCDDEEFF`
   - To oznacza 16 bajtów danych

4. **Sprawdź walidację:**
   - ✅ Pole białe = dane prawidłowe
   - ❌ Pole czerwone = błędny format

5. **Kliknij "Write Block"**

6. **Potwierdź operację** w dialogu

7. **Sprawdź wynik** - odczytaj blok ponownie

## 🎓 Zaawansowane operacje

### 🔍 Praca z trailer blokami

**Co to są trailer bloki?**
Każdy sektor ma specjalny blok zwany "trailer block", który zawiera:
- Key A (klucz A) 
- Access Conditions (warunki dostępu)
- Key B (klucz B)

**Dla sektora 0:** trailer block = blok 3
**Dla sektora 1:** trailer block = blok 7
**itd.**

**Odczyt trailer bloku:**

1. **Autoryzuj sektor**
2. **Przejdź do "Security Operations" → "Trailer Blocks"**
3. **Wybierz sektor**
4. **Kliknij "Read Trailer Block"**

**Zobaczysz:**
- Raw Data (surowe dane)
- Masked (dane z ukrytymi kluczami)
- Klucze są pokazane jako [MASKED] dla bezpieczeństwa

### 🔑 Zmiana kluczy (BARDZO NIEBEZPIECZNE!)

⚠️ **OSTRZEŻENIE:** Ta operacja może PERMANENTNIE zablokować kartę!

**Tylko dla doświadczonych użytkowników!**

1. **Przejdź do "Security Operations" → "Key Management"**
2. **Wybierz sektor**
3. **Wpisz nowe klucze:**
   - New Key A: np. `A0A1A2A3A4A5`
   - New Key B: np. `B0B1B2B3B4B5`
   - Access Conditions: np. `FF0780`

4. **Kliknij "Update Sector Keys"**
5. **Przejdź przez WSZYSTKIE dialogi potwierdzenia**
6. **Sektor będzie wymagał re-autoryzacji nowymi kluczami**

## 🔧 Rozwiązywanie problemów

### Problem: Aplikacja się nie uruchamia

**Sprawdź:**
```bash
# Czy jesteś w dobrym folderze?
ls  # (Linux/macOS) lub dir (Windows)
# Powinieneś zobaczyć main.py

# Czy środowisko jest aktywne?
# Szukaj (venv) na początku linii

# Czy biblioteki są zainstalowane?
pip list
# Powinieneś zobaczyć PyQt5, pyscard, itp.
```

**Rozwiązanie:**
```bash
# Reinstaluj biblioteki
pip install --upgrade -r requirements.txt
```

### Problem: Czytnik nie jest wykrywany

**Windows:**
1. Menedżer urządzeń → Sprawdź "Czytniki kart inteligentnych"
2. Jeśli żółty wykrzyknik = reinstaluj sterowniki
3. Spróbuj inny port USB

**macOS/Linux:**
```bash
# Sprawdź czy PC/SC działa
pcsc_scan

# Sprawdź USB
lsusb | grep ACS
```

### Problem: Karta nie jest wykrywana

1. **Sprawdź typ karty:**
   - Musi być MIFARE Classic 1K lub 4K
   - NIE MIFARE Ultralight, NIE DESFire

2. **Pozycja karty:**
   - Połóż kartę dokładnie na środku czytnika
   - Odległość 0-5mm od powierzchni

3. **Stan karty:**
   - Sprawdź czy karta nie jest uszkodzona
   - Przetestuj z inną kartą

### Problem: Autoryzacja zawsze kończy się błędem

1. **Sprawdź typ klucza:**
   - Spróbuj Key A i Key B

2. **Popularne klucze do testowania:**
   - `FFFFFFFFFFFF` (domyślny)
   - `A0A1A2A3A4A5` (transport)
   - `000000000000` (zerowy)
   - `123456789ABC` (popularny)

3. **Użyj "Try Default Keys"** - aplikacja spróbuje automatycznie

### Problem: Nie mogę zapisać danych

1. **Sprawdź autoryzację** - sektor musi być autoryzowany
2. **Sprawdź blok** - czy to nie trailer block?
3. **Sprawdź format danych** - dokładnie 32 znaki hex
4. **Sprawdź warunki dostępu** - niektóre bloki mogą być tylko do odczytu

## 📚 Przydatne informacje

### Struktura kart MIFARE Classic

**MIFARE Classic 1K:**
- 16 sektorów (0-15)
- Każdy sektor: 4 bloki
- Łącznie: 64 bloki (0-63)
- Trailer bloki: 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63

**MIFARE Classic 4K:**
- 40 sektorów (0-39)
- Pierwsze 32 sektory: 4 bloki każdy
- Ostatnie 8 sektorów: 16 bloków każdy
- Łącznie: 256 bloków

### Popularne domyślne klucze

```
FFFFFFFFFFFF - Fabryczny klucz domyślny
A0A1A2A3A4A5 - Klucz transportowy
000000000000 - Klucz zerowy
123456789ABC - Popularny testowy
B0B1B2B3B4B5 - Inny popularny
AABBCCDDEEFF - Wzorzec hex
```

### Bezpieczne praktyki

1. **Zawsze testuj na kartach jednorazowych**
2. **Rób backup danych przed zmianami**
3. **Zapisuj oryginalne klucze**
4. **Nie używaj na ważnych kartach (ID, płatności)**
5. **Sprawdź lokalne przepisy prawne**

## 🆘 Potrzebujesz pomocy?

### Logi aplikacji

Aplikacja zapisuje logi w:
- Windows: `C:\Users\[TwojeImie]\.mifare_classic_tool\logs\`
- macOS: `/Users/[TwojeImie]/.mifare_classic_tool/logs/`
- Linux: `/home/[TwojeImie]/.mifare_classic_tool/logs/`

### Zgłaszanie problemów

Gdy zgłaszasz problem, dołącz:
1. **System operacyjny** i wersję
2. **Wersję Python** (`python --version`)
3. **Model czytnika**
4. **Typ karty**
5. **Dokładny opis błędu**
6. **Kroki do odtworzenia problemu**
7. **Fragmenty logów** (jeśli dostępne)

## ✅ Lista kontrolna przed rozpoczęciem

- [ ] Czytnik ACR1252U podłączony i wykrywany
- [ ] Sterowniki zainstalowane
- [ ] Python 3.8+ zainstalowany
- [ ] Środowisko wirtualne utworzone i aktywne
- [ ] Biblioteki zainstalowane (`pip install -r requirements.txt`)
- [ ] Aplikacja uruchamia się (`python main.py`)
- [ ] Mam karty testowe (NIE ważne karty)
- [ ] Przeczytałem ostrzeżenia bezpieczeństwa
- [ ] Zrozumiałem ryzyko związane z modyfikacją kart

## 🎉 Gratulacje!

Jeśli dotarłeś do tego punktu, jesteś gotowy do bezpiecznego korzystania z MIFARE Classic Tool!

Pamiętaj: **Praktyka czyni mistrza** - zacznij od prostych operacji odczytu, a dopiero później przejdź do modyfikacji.

**Miłego hakowania! 🔓**
