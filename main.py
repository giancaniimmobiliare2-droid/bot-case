import pandas as pd
import os

# --- I TUOI LINK CORRETTI (LI HO SISTEMATI IO) ---
URL_ACQUIRENTI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZIA9jfHfgbBCBoxygzrz54_KABSBO8uLIVBnWIPpBNoIx9xmWLR-nuTx7sknVd95TYhueH5pETdR_/pub?gid=1947365306&single=true&output=csv"
URL_IMMOBILI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZIA9jfHfgbBCBoxygzrz54_KABSBO8uLIVBnWIPpBNoIx9xmWLR-nuTx7sknVd95TYhueH5pETdR_/pub?gid=835643388&single=true&output=csv"

OUTPUT_DIR = "pagine_clienti"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("SCARICO DATI...")
try:
    acquirenti = pd.read_csv(URL_ACQUIRENTI)
    immobili = pd.read_csv(URL_IMMOBILI)
    
    # Pulisco i numeri (tolgo € e spazi)
    acquirenti['Budget Max'] = pd.to_numeric(acquirenti['Budget Max'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    immobili['prezzo'] = pd.to_numeric(immobili['prezzo'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    print("✅ Dati scaricati!")
except Exception as e:
    print(f"❌ Errore lettura dati: {e}")
    exit()

# Template semplice
html_template = """
<!DOCTYPE html>
<html><body><h1>Ciao {nome}</h1><p>Ecco case a {citta}:</p>{contenuto}</body></html>
"""

print("CERCO MATCH...")
count = 0
for index, cliente in acquirenti.iterrows():
    nome = str(cliente['Nome'])
    citta = str(cliente['Città'])
    budget = cliente['Budget Max']
    
    match = immobili[
        (immobili['zona'].str.contains(citta, case=False, na=False)) & 
        (immobili['prezzo'] <= budget)
    ]
    
    if not match.empty:
        schede = ""
        for idx, casa in match.iterrows():
            schede += f"<p>🏠 {casa['zona']} - € {casa['prezzo']}</p>"
        
        # Salva il file
        with open(f"{OUTPUT_DIR}/proposte_{cliente['id']}.html", "w") as f:
            f.write(html_template.format(nome=nome, citta=citta, contenuto=schede))
        print(f"✅ Pagina creata per {nome}")
        count += 1

if count == 0:
    print("⚠️ Nessuna pagina creata (nessun match), ma il codice funziona.")
