# Vodovod Obavestenja

MVP servis koji prati JKP Naissus servisne informacije i salje email kada nova objava sadrzi lokaciju iz `config.yml`.

## Kako radi

1. Skida listu objava sa `https://jkpnaissus.co.rs/servisne-informacije/`.
2. Otvara nove objave koje nisu u `data/state.json`.
3. Normalizuje tekst tako da se lakse porede cirilica, latinica i dijakritici.
4. Ako tekst sadrzi neku lokaciju iz `config.yml`, salje email.
5. Upisuje obradjene linkove u `data/state.json`, da ne salje duplikate.

`data/state.json` ne sadrzi tajne podatke. U njemu su samo linkovi vec obradjenih objava.

## Lokalno pokretanje

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Popuni `.env` SMTP podacima, pa pokreni:

```powershell
python -m water_alerts.app --dry-run
```

Dry run ne salje email i ne menja `data/state.json`.

Za stvarno slanje:

```powershell
python -m water_alerts.app
```

## GitHub Actions podesavanje

1. Napravi GitHub repository i pushuj projekat.
2. U repository idi na `Settings -> Secrets and variables -> Actions`.
3. Dodaj ove `Repository secrets`:
   - `SMTP_HOST`
   - `SMTP_PORT`
   - `SMTP_USE_TLS`
   - `SMTP_USERNAME`
   - `SMTP_PASSWORD`
   - `EMAIL_FROM`
   - `EMAIL_TO`
4. U `Settings -> Actions -> General` proveri da workflow permissions imaju `Read and write permissions`.
5. Workflow `.github/workflows/water-alerts.yml` se pokrece na svakih 15 minuta i moze rucno iz `Actions -> Water Alerts -> Run workflow`.

Za Gmail se obicno koristi:

```text
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=tvoj-email@gmail.com
SMTP_PASSWORD=google-app-password
EMAIL_FROM=tvoj-email@gmail.com
EMAIL_TO=email-na-koji-stizu-obavestenja@example.com
```

Ne koristi glavnu Gmail lozinku. Koristi Google App Password.

## Lokacije

Lokacije se menjaju u `config.yml`. Kod je na engleskom, a email poruke su na srpskom bez dijakritika radi stabilnosti kroz razlicite mail klijente.

Ako je repository javni, `config.yml` javno otkriva lokacije koje pratis. Ako to ne zelis, drzi repository private ili ukloni licne ulice iz konfiguracije.

