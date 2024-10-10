from pathlib import Path
import json
from database_wrapper import Database

def overzicht_attracties():
    # altijd verbinding openen om query's uit te voeren
    db.connect()

    select_query = "SELECT naam, type FROM voorziening"
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

print("Eerste rij:")
print(list_met_voorzieningen[0]["naam"])
print(list_met_voorzieningen[0]["type"])

json_bestand.close() # sluit het bestand indien niet meer nodig

# DE OPDRACHT
# Met die 2 datasets moet je tot een persoonlijke programma komen voor de bezoeker
# Zorg dat je een algoritme ontwikkelt, conform eisen in het ontwerpdocument
# Zorg dat het persoonlijke programma genereert/output naar een .json bestand, dat weer ingelezen kan worden in een webomgeving (zie acceptatieomgeving website folder)
# Hieronder een begin...

# Initialiseer een lege lijst die de geselecteerde attracties zal bevatten

attractie_lijst = []

 

# Doorloop de lijst van voorzieningen (attracties) en voeg attracties toe die aan de voorkeuren van de klant voldoen

for voorziening in list_met_voorzieningen:

    # Controleer of het type van de attractie overeenkomt met de voorkeuren van de klant

    # Let op: .capitalize() zorgt ervoor dat de vergelijking ongevoelig is voor hoofdletters/kleine letters

    if voorziening['type'].capitalize() in json_dict['voorkeuren_attractietypes']:

        # Print de naam en het type van de geselecteerde attractie voor testdoeleinden (debugging)

        print(f"{voorziening['naam']} - {voorziening['type']}")

        # Voeg de attractie toe aan de lijst van geselecteerde attracties

        attractie_lijst.append(voorziening)

 

# Genereer het dagprogramma voor de bezoeker

# Dit programma bevat de naam van de bezoeker en een lijst van geselecteerde attracties op basis van zijn/haar voorkeuren

dagprogramma = {

    "voorkeuren": {

        "naam": "Bezoeker de Jong",  # Vervang dit met de daadwerkelijke naam van de bezoeker

        "voorzieningen": attractie_lijst  # Voeg de geselecteerde attracties toe aan het programma

    }

}

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand
with open('persoonlijk_programma_bezoeker_x.json', 'w') as json_bestand:
    json.dump(dagprogramma, json_bestand)

