from pathlib import Path
import json
from database_wrapper import Database
import random

def overzicht_attracties():
    # altijd verbinding openen om query's uit te voeren
    db.connect()

    select_query = """
    SELECT id, naam, type, attractie_min_lengte, attractie_max_lengte, attractie_min_leeftijd,
           attractie_max_gewicht, overdekt, geschatte_wachttijd, doorlooptijd, actief, productaanbod
    FROM voorziening
    WHERE type IN ('Achtbaan', 'Water', 'Draaien', 'Familie', 'Simulator', 'Horeca', 'Winkel');  
    """
    results = db.execute_query(select_query)

    # altijd verbinding sluiten met de database als je klaar bent
    db.close()

    return results

# maak zoals gewoonlijk connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark_software")

# navigeer naar het JSON-bestand, let op: er zijn ook andere persoonlijke voorkeuren om te testen! en maak vooral ook je eigen persoonlijke voorkeuren :-)
bestand_pad = Path(__file__).parent / 'persoonlijke_voorkeuren_bezoeker_1.json'

# open het JSON-bestand 
json_bestand = open(bestand_pad)
 
# zet het om naar een Python-dictionary
json_dict = json.load(json_bestand)

# nu kunnen we het gebruiken als een dict! dit is "dataset #1"
print(json_dict["naam"]) 

# en haal alle voorzieningen op, dit is een lijst met dicts. dit is "dataset #2"
list_met_voorzieningen = overzicht_attracties()
print(list_met_voorzieningen)

print("\n")
print(f"Dagprogramma van: {json_dict['naam']} \n")

json_bestand.close() # sluit het bestand indien niet meer nodig

# DE OPDRACHT
# Met die 2 datasets moet je tot een persoonlijke programma komen voor de bezoeker
# Zorg dat je een algoritme ontwikkelt, conform eisen in het ontwerpdocument
# Zorg dat het persoonlijke programma genereert/output naar een .json bestand, dat weer ingelezen kan worden in een webomgeving (zie acceptatieomgeving website folder)
# Hieronder een begin...

# Initialiseer een lege lijst die het dagprogramma zal bevatten

dagprogramma = []

# Variabelen om de totale tijd van het dagprogramma bij te houden
totale_tijd = 0
verblijfsduur = json_dict['verblijfsduur']  # Verblijfsduur van de bezoeker (in minuten)
horeca_moment_interval = 120  # Om de 2 uur wordt een horecagelegenheid toegevoegd 
laatste_horeca_moment = 0  # Houdt bij wanneer de laatste horecagelegenheid was toegevoegd

# Functie om te checken of een bezoeker aan de eisen voldoet van een voorziening
def toegankelijkheid_voorziening(attractie, bezoeker):
    return (
        (attractie['attractie_min_leeftijd'] is None or bezoeker['leeftijd'] >= attractie['attractie_min_leeftijd']) and
        (attractie['attractie_min_lengte'] is None or bezoeker['lengte'] >= attractie['attractie_min_lengte']) and
        (attractie['attractie_max_lengte'] is None or bezoeker['lengte'] <= attractie['attractie_max_lengte']) and  
        (attractie['attractie_max_gewicht'] is None or bezoeker['gewicht'] <= attractie['attractie_max_gewicht'])
    )

def bereken_totale_geschatte_tijd(attractie):
    return attractie['geschatte_wachttijd'] + attractie['doorlooptijd']

def voorkeur_eten_check(horeca):
    voorkeuren = json_dict['voorkeuren_eten']
    return horeca['productaanbod'].capitalize() in voorkeuren

# Functie om te controleren of een voorziening al in het dagprogramma staat
def dagprogramma_controle(dagprogramma, voorziening, max_aantal = 1):
    aantal = sum(1 for item in dagprogramma if item['naam'] == voorziening['naam'])
    
    if voorziening['naam'] in json_dict['lievelings_attracties']:
        return aantal < 2  # Lievelingsattracties kunnen twee keer voorkomen
    else:
        return aantal < max_aantal  # Normale attracties maar één keer

# Functie om horecagelegenheid toe te voegen

def voeg_horecagelegenheid_toe(dagprogramma, totale_tijd, laatste_horeca_moment):
    beschikbare_horecagelegenheden = [horeca for horeca in list_met_voorzieningen if horeca['type'] == 'horeca']
    
    # Willekeurige horecagelegenheid 
    if not json_dict['voorkeuren_eten']:
        random.shuffle(beschikbare_horecagelegenheden)  
    
    for horeca in beschikbare_horecagelegenheden:
            # Controleer of de voorkeur voor eten van toepassing is
            if voorkeur_eten_check(horeca) or not json_dict['voorkeuren_eten']:
                totale_geschatte_tijd_horeca = bereken_totale_geschatte_tijd(horeca)
                if totale_tijd + totale_geschatte_tijd_horeca <= verblijfsduur:
                    dagprogramma.append(horeca)
                    totale_tijd += totale_geschatte_tijd_horeca
                    laatste_horeca_moment = totale_tijd
                    print(f"Horecagelegenheid toegevoegd: {horeca['naam']}, totale tijd: {totale_tijd} minuten")  # Voor overzicht bij het testen
                    break  # Voeg alleen maar één horecagelegenheid om de 2 uur
    return totale_tijd, laatste_horeca_moment

# Voeg eerst een lievelingsattracties toe
for lievelings_attractie in list_met_voorzieningen:
    if lievelings_attractie['naam'] in json_dict['lievelings_attracties'] and toegankelijkheid_voorziening(lievelings_attractie, json_dict):
        totale_geschatte_tijd_attractie = bereken_totale_geschatte_tijd(lievelings_attractie)
        if totale_tijd + totale_geschatte_tijd_attractie <= verblijfsduur:
            if dagprogramma_controle(dagprogramma, lievelings_attractie):  
                dagprogramma.append(lievelings_attractie)
                totale_tijd += totale_geschatte_tijd_attractie
                print(f"Lievelingsattractie toegevoegd: {lievelings_attractie['naam']}, totale tijd: {totale_tijd} minuten") # Voor overzicht bij het testen

# Doorloop de lijst van voorzieningen en voeg horecagelegenheden en souvenirwinkel toe
for voorziening in list_met_voorzieningen:
    # Voeg een souvenirwinkel toe als er 30 minuten of minder over zijn
    if verblijfsduur - totale_tijd <= 30 and voorziening['type'] == 'winkel': 
        totale_geschatte_tijd_winkel = bereken_totale_geschatte_tijd(voorziening)
        totale_tijd += totale_geschatte_tijd_winkel
        dagprogramma.append(voorziening)
        print(f"Souvenirwinkel toegevoegd: {voorziening['naam']}, totale tijd: {totale_tijd} minuten")  # Voor overzicht bij het testen

        break  # Voeg alleen maar één souvenirwinkel toe

    # Controleer of het tijd is om een horecagelegenheid toe te voegen
    if verblijfsduur > 120 and totale_tijd - laatste_horeca_moment >= horeca_moment_interval:
        totale_tijd, laatste_horeca_moment = voeg_horecagelegenheid_toe(dagprogramma, totale_tijd, laatste_horeca_moment)

    # Voeg voorkeursattracties toe als er genoeg tijd is, maar alleen als ze nog niet op het dagprogramma staan
    if voorziening['type'].capitalize() in json_dict['voorkeuren_attractietypes'] and toegankelijkheid_voorziening(voorziening, json_dict) or not json_dict["voorkeuren_attractietypes"]:
        if dagprogramma_controle(dagprogramma, voorziening):  # Voorkeur attractietypes maar één keer toevoegen
            totale_geschatte_tijd_attractie = bereken_totale_geschatte_tijd(voorziening)
            if totale_tijd + totale_geschatte_tijd_attractie <= verblijfsduur:
                dagprogramma.append(voorziening)
                totale_tijd += totale_geschatte_tijd_attractie
                print(f"Toegevoegd: {voorziening['naam']}, totale tijd: {totale_tijd} minuten") # Voor overzicht bij het testen
            else:
                print(f"Niet genoeg tijd voor: {voorziening['naam']}") # Voor overzicht bij het testen

# Dit programma bevat de naam van de bezoeker en een lijst van geselecteerde attracties op basis van zijn/haar voorkeuren

dagprogramma = {
    "voorkeuren": {
        "naam": json_dict["naam"],  # Naam van de bezoeker uit JSON  
        "gender": json_dict["gender"],  # Geslacht van de bezoeker uit JSON  
        "leeftijd": json_dict["leeftijd"],  # Leeftijd van de bezoeker uit JSON  
        "lengte": json_dict["lengte"],  # Lengte van de bezoeker uit JSON  
        "gewicht": json_dict["gewicht"],  # Gewicht van de bezoeker uit JSON  
        "verblijfsduur": json_dict["verblijfsduur"],  # Verblijfsduur van de bezoeker uit JSON  
        "voorkeuren_attractietypes": json_dict["voorkeuren_attractietypes"],  # Voorkeuren attractietypes van de bezoeker uit JSON  
        "lievelings_attracties": json_dict["lievelings_attracties"],  # Lieveling attracties van de bezoeker uit JSON  
        "rekening_houden_met_weer": json_dict["rekening_houden_met_weer"],  # Rekening houden met het weer (ja/nee) uit JSON  
    },
    "voorzieningen": dagprogramma  # Voeg de geselecteerde attracties en horeca toe aan het programma
}

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand
with open('persoonlijk_programma_bezoeker_x.json', 'w') as json_bestand:
    json.dump(dagprogramma, json_bestand, indent=4)

