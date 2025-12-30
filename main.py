import pandas as pd
import os

# --- I TUOI LINK CORRETTI (Convertiti in CSV) ---
URL_ACQUIRENTI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZIA9jfHfgbBCBoxygzrz54_KABSBO8uLIVBnWIPpBNoIx9xmWLR-nuTx7sknVd95TYhueH5pETdR_/pub?gid=1947365306&single=true&output=csv"
URL_IMMOBILI = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQZIA9jfHfgbBCBoxygzrz54_KABSBO8uLIVBnWIPpBNoIx9xmWLR-nuTx7sknVd95TYhueH5pETdR_/pub?gid=835643388&single=true&output=csv"

OUTPUT_DIR = "pagine_clienti"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print("1. Scarico i dati...")
try:
    acquirenti = pd.read_csv(URL_ACQUIRENTI)
    immobili = pd.read_csv(URL_IMMOBILI)
    
    # Pulizia Prezzi (toglie € e spazi)
    acquirenti['Budget Max'] = pd.to_numeric(acquirenti['Budget Max'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    immobili['prezzo'] = pd.to_numeric(immobili['prezzo'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')
    
    print(f"✅ Dati scaricati! Trovati {len(acquirenti)} acquirenti e {len(immobili)} immobili.")
except Exception as e:
    print(f"❌ Errore lettura dati: {e}")
    exit()

# Template HTML
html_template = """
<!DOCTYPE html>
<html>
<head><title>Proposte</title></head>
<body><h1>Ciao {nome}, ecco le case a {citta}:</h1>{contenuto}</body>
</html>
"""

print("2. Cerco corrispondenze...")
count = 0
for index, cliente in acquirenti.iterrows():
    nome = str(cliente['Nome'])
    citta = str(cliente['Città'])
    budget = cliente['Budget Max']
    
    # Cerca immobili: Zona contiene Città Cliente (es. 'Favara') E Prezzo <= Budget
    match = immobili[
        (immobili['zona'].str.contains(citta, case=False, na=False)) & 
        (immobili['prezzo'] <= budget)
    ]
    
    if not match.empty:
        schede = ""
        for idx, casa in match.iterrows():
            schede += f"<p>🏠 {casa['zona']} - € {casa['prezzo']}</p>"
        
        pagina = html_template.format(nome=nome, citta=citta, contenuto=schede)
        filename = f"proposte_{cliente['id']}_{nome.replace(' ', '_')}.html"
        
        with open(f"{OUTPUT_DIR}/{filename}", "w") as f:
            f.write(pagina)
        print(f"✅ Pagina creata per {nome}")
        count += 1

if count == 0:
    print("⚠️ Nessuna pagina generata. Nessun immobile soddisfa i requisiti.")
