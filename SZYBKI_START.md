# ⚡ Szybki Start - MIFARE Classic Tool

## 🚀 5-minutowa instalacja

### 1. Wymagania
- ✅ Czytnik ACR1252U
- ✅ Python 3.8+
- ✅ Karta MIFARE Classic (testowa!)

### 2. Instalacja
```bash
# Pobierz projekt
cd /Users/mk/Desktop/NFC-tool

# Utwórz środowisko
python -m venv venv

# Aktywuj środowisko
source venv/bin/activate  # macOS/Linux
# lub
venv\Scripts\activate     # Windows

# Zainstaluj biblioteki
pip install -r requirements.txt
```

### 3. Uruchomienie
```bash
python main.py
```

### 4. Pierwsze kroki
1. **Podłącz czytnik** → Kliknij "Connect"
2. **Połóż kartę** → Sprawdź "Card Information"
3. **Autoryzuj sektor 0** → Zaznacz "Use default key" → "Authenticate"
4. **Odczytaj blok 1** → Wybierz blok 1 → "Read Block"

### 5. ⚠️ UWAGI BEZPIECZEŃSTWA
- 🚫 **NIE testuj na ważnych kartach!**
- 🚫 **NIE zmieniaj kluczy bez wiedzy!**
- ✅ **Używaj tylko kart testowych**
- ✅ **Przeczytaj pełną instrukcję** (`INSTRUKCJA_OBSLUGI.md`)

### 6. Pomoc
- 📖 Pełna instrukcja: `INSTRUKCJA_OBSLUGI.md`
- 🐛 Problemy? Sprawdź sekcję "Rozwiązywanie problemów"
- 📝 Logi: `~/.mifare_classic_tool/logs/`

**Gotowe! Możesz rozpocząć bezpieczne eksperymenty! 🎯**
