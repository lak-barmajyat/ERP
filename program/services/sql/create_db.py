import os
import sys
import subprocess
import getpass
import random
from datetime import date, timedelta

import sqlalchemy
from sqlalchemy import text

# ── paths ──────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
SCHEMA_FILE   = os.path.join(BASE_DIR, "ERP_database.sql")
SEED_FILE     = os.path.join(BASE_DIR, "fill_database.sql")


# ── seed targets ─────────────────────────────────────────────────────────
NUM_CLIENTS = 1000
NUM_SUPPLIERS = 20
NUM_FAMILIES = 30
NUM_ARTICLES = 1000
NUM_SALES_DOCUMENTS = 1000
NUM_PURCHASE_DOCUMENTS = 200
NUM_PAYMENTS = 156
NUM_AUDIT_LOGS = 200


# ── helpers ────────────────────────────────────────────────────────────────
def separator():
    print("=" * 55)

def run_sql_file(host, port, user, password, filepath):
    """Execute a .sql file using the mysql CLI."""
    cmd = [
        "mysql",
        f"-h{host}",
        f"-P{port}",
        f"-u{user}",
        f"-p{password}",
        "--default-character-set=utf8mb4",
    ]
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            result = subprocess.run(
                cmd,
                stdin=f,
                capture_output=True,
                text=True,
            )
        if result.returncode != 0:
            print(f"\n[ERROR] MySQL returned an error:")
            print(result.stderr)
            return False
        return True
    except FileNotFoundError:
        print("\n[ERROR] 'mysql' command not found.")
        print("  Make sure MySQL client is installed and added to PATH.")
        return False
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        return False

def verify_connection(host, port, user, password):
    """Verify DB was created successfully using SQLAlchemy."""
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/erp"
    try:
        engine = sqlalchemy.create_engine(url)
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        engine.dispose()
        return True
    except Exception as e:
        print(f"\n[ERROR] Could not connect after setup: {e}")
        return False


def _chunked(iterable, chunk_size):
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i:i + chunk_size]


def _seed_large_fake_data(host, port, user, password):
    """Generate a large and structured fake ERP dataset directly in MySQL."""
    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/erp"
    engine = sqlalchemy.create_engine(url, future=True)
    rng = random.Random(20260327)

    try:
        with engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            for table_name in (
                "audit_log",
                "mouvements_stock",
                "paiements",
                "details_documents",
                "documents",
                "articles",
                "familles",
                "tiers",
                "utilisateurs",
                "informations_societe",
            ):
                conn.execute(text(f"TRUNCATE TABLE {table_name}"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

            conn.execute(
                text(
                    """
                    INSERT INTO informations_societe (
                        nom_societe, activite, forme_juridique, patente, cnss,
                        telephone_fix, fax, site_web, ice, if_fiscal, rc, email, adresse
                    ) VALUES (
                        :nom_societe, :activite, :forme_juridique, :patente, :cnss,
                        :telephone_fix, :fax, :site_web, :ice, :if_fiscal, :rc, :email, :adresse
                    )
                    """
                ),
                {
                    "nom_societe": "LAK Software Solutions",
                    "activite": "Distribution et integration IT",
                    "forme_juridique": "SARL",
                    "patente": "PAT-ERP-2026-01",
                    "cnss": "CNSS-ERP-2026",
                    "telephone_fix": "0522000011",
                    "fax": "0522000012",
                    "site_web": "www.laksoftware-solutions.ma",
                    "ice": "001234567890123",
                    "if_fiscal": "IF-ERP-2026",
                    "rc": "RC-CASA-2026-001",
                    "email": "contact@laksoftware-solutions.ma",
                    "adresse": "25 Bd Zerktouni, Casablanca",
                },
            )

            users = [
                ("abobaker", "$2b$12$wXYP3T8npdFM52DqzU2izO2cOZq./F9gVicytcXd6Ei4gBsPggUvS", "ADMIN"),
                ("mossaab", "$2b$12$TH5ytK6Z/AtDFpFkCnnEcuuqHHyyeRUNFfacBamCmlHoHQJYUhk3K", "ADMIN"),
                ("elhocine", "$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK", "VENDEUR"),
                ("abdelfattah", "$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK", "VENDEUR"),
                ("youssef", "$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK", "VENDEUR"),
                ("fatima", "$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK", "GESTIONNAIRE"),
                ("hamid", "$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK", "GESTIONNAIRE"),
            ]
            conn.execute(
                text(
                    """
                    INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe_hash, role, actif)
                    VALUES (:nom, :pwd, :role, 1)
                    """
                ),
                [{"nom": u[0], "pwd": u[1], "role": u[2]} for u in users],
            )

            family_names = [
                "Informatique", "Bureautique", "Reseau", "Consommables", "Mobilier Bureau",
                "Logiciels", "Electromenager Pro", "Securite", "Telephonie", "Imprimerie",
                "Serveurs", "Cablage", "Stockage", "Video Conference", "Accessoires",
                "Domotique", "Cloud", "DevOps", "Backup", "Batteries",
                "Ecrans", "Peripheriques", "Maintenance", "Audio Pro", "Ergonomie",
                "Nettoyage IT", "Signaletique", "Packaging", "Pieces Detachees", "Gaming Pro",
            ]
            conn.execute(
                text(
                    """
                    INSERT INTO familles (nom_famille, description, taux_tva, suivi_stock, unite_defaut)
                    VALUES (:nom, :description, :taux_tva, :suivi_stock, :unite_defaut)
                    """
                ),
                [
                    {
                        "nom": name,
                        "description": f"Famille {name}",
                        "taux_tva": 20.00,
                        "suivi_stock": 1,
                        "unite_defaut": "PCS",
                    }
                    for name in family_names
                ],
            )

            family_ids = [row[0] for row in conn.execute(text("SELECT id_famille FROM familles ORDER BY id_famille")).all()]

            product_roots = [
                "Ordinateur", "Serveur", "Switch", "Routeur", "Bureau", "Chaise", "Ecran",
                "Imprimante", "Scanner", "Camera", "Casque", "Clavier", "Souris", "Disque SSD",
                "Toner", "Ramette", "Onduleur", "Telephone IP", "Point d acces", "Baie reseau",

                "Ordinateur Portable", "Unite Centrale", "Station de Travail", "Mini PC", "PC Gamer",
                "Moniteur", "Ecran LED", "Ecran LCD", "Ecran 24 pouces", "Ecran 27 pouces",
                "Clavier Sans Fil", "Clavier Mecanique", "Souris Sans Fil", "Souris Optique", "Tapis de Souris",
                "Webcam", "Microphone", "Haut Parleur", "Enceinte Bluetooth", "Barre de Son",
                "Projecteur", "Videoprojecteur", "Television", "Tablette", "Smartphone",
                "Telephone Fixe", "Telephone SIP", "Telephone DECT", "Casque Audio", "Ecouteurs",

                "Disque Dur", "Disque HDD", "Cle USB", "Carte Memoire", "Lecteur DVD",
                "Graveur DVD", "Dock Station", "Hub USB", "Adaptateur HDMI", "Adaptateur VGA",
                "Câble HDMI", "Cable VGA", "Cable DisplayPort", "Cable USB", "Cable USB C",
                "Cable Ethernet", "Cable RJ45", "Cable Fibre Optique", "Rallonge Electrique", "Multiprise",
                "Chargeur Ordinateur", "Chargeur Telephone", "Batterie Externe", "Batterie CMOS", "Pile AA",

                "Carte Mere", "Processeur", "Memoire RAM", "Carte Graphique", "Ventilateur CPU",
                "Alimentation PC", "Boitier PC", "Radiateur", "Pate Thermique", "Carte Son",
                "Carte Reseau", "Lecteur Carte", "Module WiFi", "Module Bluetooth", "Carte Controleur",
                "Onduleur Line Interactive", "Onduleur Online", "Stabilisateur", "Parafoudre", "Transformateur",

                "Serveur Rack", "Serveur Tour", "NAS", "SAN", "Boitier NAS",
                "Rack 42U", "Rack Mural", "Panneau de Brassage", "Patch Panel", "Organisateur de Cables",
                "Prise Reseau", "Connecteur RJ45", "Connecteur Fibre", "Module SFP", "Convertisseur Media",
                "Pare Feu", "Firewall Materiel", "Routeur WiFi", "Modem", "Modem 4G",
                "Repeteur WiFi", "Controleur WiFi", "Antenne WiFi", "Point d acces WiFi", "Pont Sans Fil",

                "Imprimante Laser", "Imprimante Jet d encre", "Imprimante Multifonction", "Photocopieur", "Copieur",
                "Traceur", "Etiqueteuse", "Imprimante Etiquettes", "Massicot", "Destructeur de Documents",
                "Relieuse", "Plastifieuse", "Perforeuse", "Agrafeuse", "Agrafeuse Electrique",
                "Calculatrice", "Horodateur", "Caisse Enregistreuse", "Terminal de Paiement", "Lecteur Code Barre",

                "Scanner a Plat", "Scanner Portable", "Scanner de Documents", "Lecteur QR Code", "Douchette Code Barre",
                "Balance Electronique", "Etiquette Adhesive", "Rouleau Etiquettes", "Ruban Encreur", "Papier Thermique",
                "Cartouche Encre", "Tambour Imprimante", "Unite de Fusion", "Bac Papier", "Chargeur Automatique",

                "Table de Bureau", "Bureau Direction", "Bureau Operateur", "Chaise de Bureau", "Fauteuil Direction",
                "Chaise Visiteur", "Table de Reunion", "Armoire Metallique", "Caisson Mobile", "Bibliotheque",
                "Etagere", "Vestiaire", "Meuble TV", "Comptoir Accueil", "Banque d accueil",
                "Table Basse", "Porte Documents", "Porte Revues", "Support Ecran", "Support Ordinateur Portable",

                "Tableau Blanc", "Tableau Liege", "Paperboard", "Marqueur", "Effaceur",
                "Bloc Notes", "Carnet", "Agenda", "Stylo Bleu", "Stylo Noir",
                "Crayon", "Surligneur", "Correcteur", "Gomme", "Taille Crayon",
                "Regle", "Ciseaux", "Colle", "Ruban Adhesif", "Devidoir",
                "Chemise Carton", "Classeur", "Intercalaire", "Pochette Plastique", "Boite Archives",
                "Corbeille a Papier", "Organiseur Bureau", "Porte Stylos", "Tampon Encreur", "Encre Tampon",

                "Papier A4", "Papier A3", "Papier Photo", "Papier Autocollant", "Papier Continu",
                "Enveloppe", "Etiquette Adresse", "Formulaire", "Facturier", "Bon de Livraison",
                "Registre", "Livre Comptable", "Ticket Caisse", "Papier Brouillon", "Papier Recycle",

                "Camera IP", "Camera Dome", "Camera Bullet", "Enregistreur NVR", "Enregistreur DVR",
                "Disque Surveillance", "Ecran Surveillance", "Moniteur CCTV", "Detecteur Mouvement", "Detecteur Fumee",
                "Sirene Alarme", "Centrale Alarme", "Clavier Alarme", "Badge RFID", "Lecteur Badge",
                "Controle d acces", "Serrure Electrique", "Interphone Video", "Visiophone", "Portier Electronique",

                "Climatiseur", "Ventilateur", "Radiateur Electrique", "Purificateur d air", "Humidificateur",
                "Machine a Cafe", "Bouilloire", "Micro ondes", "Refrigerateur", "Distributeur Eau",
                "Aspirateur", "Nettoyeur Vapeur", "Chariot Menage", "Balai", "Serpillere",
                "Poubelle Bureau", "Poubelle Tri", "Sac Poubelle", "Distributeur Savon", "Seche Mains",

                "Lampe Bureau", "Plafonnier LED", "Spot LED", "Ampoule LED", "Projecteur LED",
                "Horloge Murale", "Prise Electrique", "Interrupteur", "Tableau Electrique", "Disjoncteur",
                "Goulotte", "Chemin de Cables", "Boite de Derivation", "Connecteur Electrique", "Testeur Tension",

                "Valise Ordinateur", "Sac a Dos PC", "Housse Laptop", "Support Telephone", "Support Tablette",
                "Bras Articule Ecran", "Pied Microphone", "Treteau", "Escabeau", "Chariot Transport",
                "Boite Outils", "Tournevis", "Pince", "Perceuse", "Multimetre",
                "Etiqueteuse Industrielle", "Ruban Etiqueteuse", "Souffleur Air", "Kit Nettoyage Ecran", "Lingettes Nettoyantes"
            ]

            article_suffixes = [
                "Pro", "Plus", "Max", "Mini", "Slim", "Ultra", "Lite", "Prime", "Smart", "Flex",
                "Elite", "Office", "Business", "Classic", "Premium", "Compact", "Advanced", "Essential", "Performance", "Express",
                "Power", "Speed", "Vision", "Connect", "Secure", "Eco", "Air", "Core", "One", "X",
                "X2", "X3", "S", "M", "L", "XL", "Pro Max", "Plus Max", "Mini Pro", "Ultra Pro",
                "Series 1", "Series 2", "Series 3", "Series 5", "Series 7", "Series 9", "Edition", "Edition Plus", "Edition Pro", "Edition X",
                "200", "300", "500", "700", "900", "1000", "2000", "3000", "5000", "7000",
                "A", "B", "C", "D", "E", "R", "T", "Z", "Neo", "Nova",
                "Fusion", "Edge", "Pulse", "Wave", "Line", "Flow", "Sync", "Link", "Boost", "Drive",
                "Hub", "Station", "Desk", "Net", "Cloud", "Data", "Control", "Master", "Focus", "Direct",
                "Plus Edition", "Business Edition", "Office Edition", "Smart Edition", "Compact Edition", "Premium Edition", "Advanced Edition", "Eco Edition", "Secure Edition", "Industrial"
            ]
            
            article_rows = []
            for i in range(1, NUM_ARTICLES + 1):
                fam_id = family_ids[(i - 1) % len(family_ids)]
                root = (f"{product_roots[(i - 1) % len(product_roots)]}"
                        f" {article_suffixes[(i * 3) % len(article_suffixes)]}")
                prix_achat = round(80 + (i % 50) * 37 + rng.uniform(5, 150), 2)
                coef = 1.12 + (i % 9) * 0.03
                prix_vente = round(prix_achat * coef, 2)
                ref = f"ART{i:04d}"

                quantite_min = round(rng.uniform(0, 50), 2)
                quantite_max = round(quantite_min + rng.uniform(50, 500), 2)
                quantite = round(rng.uniform(0, 250), 2)
                if quantite_min > 0 and rng.random() < 0.18:
                    quantite = round(rng.uniform(0, max(0.01, quantite_min)), 2)

                article_rows.append(
                    {
                        "nom_article": f"{root}",
                        "description": f"{root} professionnel generation {i:04d}",
                        "prix_vente_ht": prix_vente,
                        "prix_achat_ht": prix_achat,
                        "id_famille": fam_id,
                        "taux_tva": 20.00,
                        "suivi_stock": "CMUP",
                        "quantite": quantite,
                        "quantite_min": quantite_min,
                        "quantite_max": quantite_max,
                        "unite": "PCS",
                        "reference_interne": ref,
                        "actif": 1,
                    }
                )

            conn.execute(
                text(
                    """
                    INSERT INTO articles (
                        nom_article, description, prix_vente_ht, prix_achat_ht, id_famille,
                        taux_tva, suivi_stock, quantite, quantite_min, quantite_max,
                        unite, reference_interne, actif
                    ) VALUES (
                        :nom_article, :description, :prix_vente_ht, :prix_achat_ht, :id_famille,
                        :taux_tva, :suivi_stock, :quantite, :quantite_min, :quantite_max,
                        :unite, :reference_interne, :actif
                    )
                    """
                ),
                article_rows,
            )

            city_list = [
                "Casablanca", "Rabat", "Marrakech", "Fes", "Tanger", "Agadir",
                "Meknes", "Oujda", "Kenitra", "Tetouan", "Zagora", "Errachidia",
                "Nador", "Safi", "Khouribga", "Beni Mellal", "El Jadida", "Taza",
                "Larache", "Ouarzazate", "Settat", "Ksar El Kebir", "Sidi Kacem",
                "Guelmim", "Tiznit", "Tamezmoute", "Tan-Tan", "Dakhla", "Laayoune",
                "Boujdour", "Tamensourt", "Assilah", "Fnideq", "Martil", "Sidi Ifni",
                "Zouagha Moulay Yaacoub", "Azrou", "Midelt", "Ifrane", "Chefchaouen",
                "Al Hoceima", "Sidi Slimane", "Ouazzane", "Sidi Bennour", "Youssoufia",
                "Sidi Qacem", "Berkane",
            ]
            company_stems = [
                "Atlas", "Maghreb", "Sahara", "Rif", "Nour", "Delta", "Neo", "Prime", "Sigma", "Zenith",
                "Pulse", "Alliance", "Horizon", "Prestige", "Excellence", "Elite", "Select", "Concept", "Vision", "Performance",
                "Tech", "Services", "Solutions", "Industrie", "Distribution", "Commerce", "Logistique", "Transport", "Express", "International",
                "Maroc", "Casablanca", "Tanger", "Agadir", "Marrakech", "Fes", "Rabat", "Oriental", "Sud", "Nord",
                "Centre", "Ouest", "Royal", "Imperial", "Majestic", "Capital", "Patrimoine", "Dynamique", "Moderne", "Evolution",
                "Innovation", "Digital", "System", "Informatique", "Bureau", "Gestion", "Conseil", "Expert", "Consulting", "Finance",
                "Invest", "Holding", "Partners", "Group", "Groupe", "Corporation", "Entreprise", "Business", "Trade", "Market",
                "Pro", "Plus", "Max", "Premium", "Universal", "Global", "General", "Centrale", "Union", "Leader",
                "Avenir", "Espoir", "Croissance", "Developpement", "Expansion", "Succes", "Confiance", "Qualite", "Fiabilite", "Energie",
                "Batiment", "Construction", "Immobilier", "Travaux", "Engineering", "Electro", "Meca", "Plast", "Textile", "Agro"
            ]
            company_suffixes = [
                "Distribution", "Services", "Tech", "Industrie", "Com", "Solutions", "Trading", "Supply", "Logistique", "Group",
                "Consulting", "Conseil", "Informatique", "Digital", "System", "Systems", "Express", "Partners", "Holding", "Invest",
                "Finance", "Capital", "Gestion", "Business", "Corporation", "Entreprise", "Market", "International", "Export", "Import",
                "Transit", "Transport", "Cargo", "Freight", "Delivery", "Messagerie", "Maintenance", "Engineering", "Electro", "Meca",
                "Batiment", "Construction", "Travaux", "Immobilier", "Promotion", "Aménagement", "Architecture", "Décoration", "Design", "Renovation",
                "Textile", "Mode", "Confection", "Cuir", "Agro", "Alimentaire", "Food", "Beverage", "Packaging", "Emballage",
                "Plastique", "Plast", "Chimie", "Pharma", "Medical", "Santé", "Hygiène", "Cosmetique", "Beauté", "Parfums",
                "Telecom", "Media", "Communication", "Publicité", "Marketing", "Edition", "Impression", "Papeterie", "Formation", "Education",
                "Assistance", "Sécurité", "Nettoyage", "Facility", "Equipement", "Fournitures", "Outillage", "Materiaux", "Energie", "Environnement",
                "Recyclage", "Automobile", "Pieces", "Accessoires", "Marine", "Voyages", "Tourisme", "Event", "Events", "Academy"
            ]

            supplier_legal_forms = ["SARL", "SA", "SAS", "SARL AU"]
            supplier_specialties = [
                "Informatique",
                "Bureautique",
                "Reseau",
                "Consommables",
                "Mobilier Bureau",
                "Logiciels",
                "Securite",
                "Telephonie",
                "Cablage",
                "Stockage",
            ]

            tier_rows = []
            for i in range(1, NUM_CLIENTS + 1):
                # Enforce uniqueness with explicit numeric suffix in both code and name.
                name = (
                    f"{company_stems[(i - 1) % len(company_stems)]} "
                    f"{company_suffixes[(i * 3) % len(company_suffixes)]}"
                )
                tier_rows.append(
                    {
                        "code_tiers": f"CL{i:04d}",
                        "type_tiers": "CLIENT",
                        "nom_tiers": name,
                        "adresse": f"{i} Avenue {city_list[i % len(city_list)]}",
                        "telephone": f"05{22 + (i % 20):02d}{100000 + i:06d}",
                        "email": f"client{i:03d}@example.ma",
                        "plafond_credit": float(5000 + (i % 15) * 2500),
                        "actif": 1,
                    }
                )

            for i in range(1, NUM_SUPPLIERS + 1):
                specialty = supplier_specialties[(i * 7) % len(supplier_specialties)]
                legal_form = supplier_legal_forms[(i * 3) % len(supplier_legal_forms)]
                name = (
                    f"{company_stems[(i * 2) % len(company_stems)]} "
                    f"{company_suffixes[(i * 5) % len(company_suffixes)]} "
                    f"{specialty} {legal_form}"
                )
                tier_rows.append(
                    {
                        "code_tiers": f"FR{i:03d}",
                        "type_tiers": "FOURNISSEUR",
                        "nom_tiers": name,
                        "adresse": f"ZI Bloc {i} - {city_list[(i * 2) % len(city_list)]}",
                        "telephone": f"05{30 + (i % 10):02d}{200000 + i:06d}",
                        "email": f"fournisseur{i:03d}@example.ma",
                        "plafond_credit": 0.0,
                        "actif": 1,
                    }
                )

            conn.execute(
                text(
                    """
                    INSERT INTO tiers (
                        code_tiers, type_tiers, nom_tiers, adresse, telephone, email, plafond_credit, actif
                    ) VALUES (
                        :code_tiers, :type_tiers, :nom_tiers, :adresse, :telephone, :email, :plafond_credit, :actif
                    )
                    """
                ),
                tier_rows,
            )

            type_map = {
                row[0]: row[1]
                for row in conn.execute(
                    text(
                        "SELECT code_type, id_type_document FROM ref_types_documents WHERE code_type IN ('DV','DA','BC','BL','FA','AV')"
                    )
                ).all()
            }
            status_map = {
                row[0]: row[1]
                for row in conn.execute(
                    text("SELECT code_statut, id_statut FROM ref_statuts_documents")
                ).all()
            }
            mode_map = {
                row[0]: row[1]
                for row in conn.execute(
                    text("SELECT code_mode, id_mode_paiement FROM ref_modes_paiement")
                ).all()
            }

            user_ids = [row[0] for row in conn.execute(text("SELECT id_utilisateur FROM utilisateurs ORDER BY id_utilisateur")).all()]
            client_ids = [
                row[0]
                for row in conn.execute(
                    text("SELECT id_tiers FROM tiers WHERE type_tiers='CLIENT' ORDER BY id_tiers")
                ).all()
            ]

            supplier_ids = [
                row[0]
                for row in conn.execute(
                    text("SELECT id_tiers FROM tiers WHERE type_tiers='FOURNISSEUR' ORDER BY id_tiers")
                ).all()
            ]

            doc_cycle_sales = ["DV", "BC", "BL", "FA", "AV"]
            doc_cycle_purchase = ["DA", "BC", "BL", "FA", "AV"]
            doc_counts = {"DV": 0, "DA": 0, "BC": 0, "BL": 0, "FA": 0, "AV": 0}
            today = date.today()
            start_date = today - timedelta(days=5 * 365)
            date_span_days = (today - start_date).days
            documents = []

            # --------------------------
            # Sales documents (id_domaine = 1)
            # --------------------------
            for i in range(1, NUM_SALES_DOCUMENTS + 1):
                code = doc_cycle_sales[(i - 1) % len(doc_cycle_sales)]
                doc_counts[code] += 1
                sequence = doc_counts[code]
                # Required format example: DV100
                numero = f"{code}{sequence:04d}"
                d_date = start_date + timedelta(days=rng.randint(0, max(date_span_days, 1)))

                if code == "FA":
                    status_code = ["VALIDE", "PARTIEL", "PAYE"][i % 3]
                elif code == "DV":
                    status_code = "BROUILLON" if i % 4 == 0 else "VALIDE"
                elif code == "AV":
                    status_code = "VALIDE"
                else:
                    status_code = "VALIDE"

                documents.append(
                    {
                        "id_domaine": 1,
                        "id_type_document": type_map[code],
                        "numero_document": numero,
                        "id_tiers": client_ids[(i * 7) % len(client_ids)],
                        "date_document": d_date,
                        "date_livraison": d_date if code in ("BC", "BL") else None,
                        "mode_prix": "HT",
                        "total_ht": 0.0,
                        "total_tva": 0.0,
                        "total_ttc": 0.0,
                        "solde": 0.0,
                        "id_vendeur": user_ids[i % len(user_ids)],
                        "id_statut": status_map.get(status_code, status_map.get("VALIDE", 1)),
                        "commentaire": f"Document vente {code} genere automatiquement",
                        "id_precedent_doc": None,
                        "doc_actif": 1,
                    }
                )

            # --------------------------
            # Purchase documents (id_domaine = 2)
            # --------------------------
            if supplier_ids:
                for i in range(1, NUM_PURCHASE_DOCUMENTS + 1):
                    code = doc_cycle_purchase[(i - 1) % len(doc_cycle_purchase)]
                    doc_counts[code] += 1
                    sequence = doc_counts[code]
                    numero = f"{code}{sequence:04d}"
                    d_date = start_date + timedelta(days=rng.randint(0, max(date_span_days, 1)))

                    if code == "FA":
                        status_code = ["VALIDE", "PARTIEL", "PAYE"][i % 3]
                    else:
                        status_code = "VALIDE"

                    documents.append(
                        {
                            "id_domaine": 2,
                            "id_type_document": type_map[code],
                            "numero_document": numero,
                            "id_tiers": supplier_ids[(i * 5) % len(supplier_ids)],
                            "date_document": d_date,
                            "date_livraison": d_date if code in ("BC", "BL") else None,
                            "mode_prix": "HT",
                            "total_ht": 0.0,
                            "total_tva": 0.0,
                            "total_ttc": 0.0,
                            "solde": 0.0,
                            "id_vendeur": user_ids[(i + 3) % len(user_ids)],
                            "id_statut": status_map.get(status_code, status_map.get("VALIDE", 1)),
                            "commentaire": f"Document achat {code} genere automatiquement",
                            "id_precedent_doc": None,
                            "doc_actif": 1,
                        }
                    )

            conn.execute(
                text(
                    """
                    INSERT INTO documents (
                        id_domaine, id_type_document, numero_document, id_tiers, date_document, date_livraison,
                        mode_prix, total_ht, total_tva, total_ttc, solde, id_vendeur, id_statut,
                        commentaire, id_precedent_doc, doc_actif
                    ) VALUES (
                        :id_domaine, :id_type_document, :numero_document, :id_tiers, :date_document, :date_livraison,
                        :mode_prix, :total_ht, :total_tva, :total_ttc, :solde, :id_vendeur, :id_statut,
                        :commentaire, :id_precedent_doc, :doc_actif
                    )
                    """
                ),
                documents,
            )

            article_map = {
                row[0]: {
                    "nom": row[1],
                    "prix_vente": float(row[2] or 0),
                    "prix_achat": float(row[3] or 0),
                    "tva": float(row[4] or 20),
                }
                for row in conn.execute(
                    text("SELECT id_article, nom_article, prix_vente_ht, prix_achat_ht, taux_tva FROM articles ORDER BY id_article")
                ).all()
            }
            article_ids = list(article_map.keys())

            doc_rows = conn.execute(
                text(
                    """
                    SELECT d.id_document, d.id_domaine, r.code_type, d.date_document
                    FROM documents d
                    JOIN ref_types_documents r ON r.id_type_document = d.id_type_document
                    ORDER BY d.id_document
                    """
                )
            ).all()

            detail_rows = []
            for idx, row in enumerate(doc_rows, start=1):
                doc_id, domain_id, code_type, doc_date = row
                domain_id = int(domain_id or 1)
                line_count = 50 if (idx % 40 == 0) else 3
                selected_articles = rng.sample(article_ids, line_count)

                for ln, art_id in enumerate(selected_articles, start=1):
                    art = article_map[art_id]
                    if code_type == "AV":
                        qty = round(rng.uniform(0.1, 2.0), 3)
                    else:
                        qty = round(float(rng.randint(1, 8)), 3)

                    base_price = art["prix_achat"] if domain_id == 2 else art["prix_vente"]
                    if domain_id == 2:
                        unit_ht = round(base_price * rng.uniform(0.95, 1.08), 2)
                    else:
                        unit_ht = round(base_price * rng.uniform(0.92, 1.15), 2)
                    tva = round(art["tva"], 2)
                    unit_ttc = round(unit_ht * (1 + (tva / 100.0)), 2)
                    line_ht = round(unit_ht * qty, 2)
                    line_tva = round(line_ht * (tva / 100.0), 2)
                    line_ttc = round(line_ht + line_tva, 2)

                    margin = 0.0
                    if domain_id != 2:
                        margin = round(max(unit_ht - float(art["prix_achat"] or 0), 0), 2)

                    detail_rows.append(
                        {
                            "id_document": int(doc_id),
                            "id_article": int(art_id),
                            "description": f"{art['nom']} - lot {ln}",
                            "quantite": qty,
                            "prix_unitaire_ht": unit_ht,
                            "prix_unitaire_ttc": unit_ttc,
                            "unite_vente": "PCS",
                            "taux_tva": tva,
                            "marge_beneficiaire": margin,
                            "total_ligne_ht": line_ht,
                            "total_ligne_tva": line_tva,
                            "total_ligne_ttc": line_ttc,
                            "id_precedent_doc": None,
                            "doc_actif": 1,
                        }
                    )

            insert_detail_sql = text(
                """
                INSERT INTO details_documents (
                    id_document, id_article, description, quantite,
                    prix_unitaire_ht, prix_unitaire_ttc, unite_vente, taux_tva,
                    marge_beneficiaire, total_ligne_ht, total_ligne_tva, total_ligne_ttc,
                    id_precedent_doc, doc_actif
                ) VALUES (
                    :id_document, :id_article, :description, :quantite,
                    :prix_unitaire_ht, :prix_unitaire_ttc, :unite_vente, :taux_tva,
                    :marge_beneficiaire, :total_ligne_ht, :total_ligne_tva, :total_ligne_ttc,
                    :id_precedent_doc, :doc_actif
                )
                """
            )
            for chunk in _chunked(detail_rows, 1000):
                conn.execute(insert_detail_sql, chunk)

            conn.execute(
                text(
                    """
                    UPDATE documents d
                    JOIN (
                        SELECT id_document,
                               SUM(total_ligne_ht) AS sum_ht,
                               SUM(total_ligne_tva) AS sum_tva,
                               SUM(total_ligne_ttc) AS sum_ttc
                        FROM details_documents
                        WHERE doc_actif = 1
                        GROUP BY id_document
                    ) x ON x.id_document = d.id_document
                    SET d.total_ht = x.sum_ht,
                        d.total_tva = x.sum_tva,
                        d.total_ttc = x.sum_ttc,
                        d.solde = x.sum_ttc
                    """
                )
            )

            fa_docs = conn.execute(
                text(
                    """
                    SELECT d.id_document, d.date_document, d.total_ttc
                    FROM documents d
                    JOIN ref_types_documents r ON r.id_type_document = d.id_type_document
                    WHERE r.code_type = 'FA'
                    ORDER BY d.id_document
                    """
                )
            ).all()

            mode_ids = list(mode_map.values())
            bank_names = ["Attijariwafa", "Banque Populaire", "CIH", "BMCE", "CFG Bank"]
            paiement_rows = []
            for i, (doc_id, d_date, total_ttc) in enumerate(rng.sample(fa_docs, min(NUM_PAYMENTS, len(fa_docs))), start=1):
                ratio = rng.uniform(0.3, 1.0)
                montant = round(float(total_ttc or 0) * ratio, 2)
                payment_date = d_date + timedelta(days=(i % 60))
                if payment_date > today:
                    payment_date = today
                paiement_rows.append(
                    {
                        "id_document": int(doc_id),
                        "date_paiement": payment_date,
                        "id_mode_paiement": mode_ids[i % len(mode_ids)],
                        "montant": montant,
                        "reference": f"PAY-2026-{i:04d}",
                        "date_echeance": None,
                        "banque": bank_names[i % len(bank_names)],
                        "statut": "ENCAISSE" if i % 7 != 0 else "EN_ATTENTE",
                        "commentaire": "Paiement genere automatiquement",
                    }
                )

            conn.execute(
                text(
                    """
                    INSERT INTO paiements (
                        id_document, date_paiement, id_mode_paiement, montant,
                        reference, date_echeance, banque, statut, commentaire
                    ) VALUES (
                        :id_document, :date_paiement, :id_mode_paiement, :montant,
                        :reference, :date_echeance, :banque, :statut, :commentaire
                    )
                    """
                ),
                paiement_rows,
            )

            conn.execute(
                text(
                    """
                    UPDATE documents d
                    LEFT JOIN (
                        SELECT id_document, SUM(montant) AS total_paid
                        FROM paiements
                        GROUP BY id_document
                    ) p ON p.id_document = d.id_document
                    SET d.solde = GREATEST(d.total_ttc - COALESCE(p.total_paid, 0), 0)
                    """
                )
            )

            paid_status_id = status_map.get("PAYE", status_map.get("VALIDE", 1))
            partiel_status_id = status_map.get("PARTIEL", status_map.get("VALIDE", 1))
            valide_status_id = status_map.get("VALIDE", 1)
            conn.execute(
                text(
                    """
                    UPDATE documents d
                    JOIN ref_types_documents r ON r.id_type_document = d.id_type_document
                    SET d.id_statut = CASE
                        WHEN r.code_type <> 'FA' THEN d.id_statut
                        WHEN d.solde <= 0.01 THEN :paid_status_id
                        WHEN d.solde < d.total_ttc THEN :partiel_status_id
                        ELSE :valide_status_id
                    END
                    """
                ),
                {
                    "paid_status_id": paid_status_id,
                    "partiel_status_id": partiel_status_id,
                    "valide_status_id": valide_status_id,
                },
            )

            doc_ids = [row[0] for row in conn.execute(text("SELECT id_document FROM documents ORDER BY id_document")).all()]
            table_names = ["documents", "details_documents", "paiements", "tiers", "articles", "mouvements_stock"]
            actions = ["INSERT", "UPDATE", "STATUS_CHANGE", "DELETE"]
            audit_rows = []
            for i in range(1, NUM_AUDIT_LOGS + 1):
                table_name = table_names[(i - 1) % len(table_names)]
                action = actions[(i - 1) % len(actions)]
                record_id = str(doc_ids[(i * 11) % len(doc_ids)]) if table_name in ("documents", "details_documents", "paiements") else str(i)
                audit_rows.append(
                    {
                        "date_action": date(2026, 1, 1) + timedelta(days=i % 360),
                        "id_utilisateur": user_ids[i % len(user_ids)],
                        "table_name": table_name,
                        "record_id": record_id,
                        "action": action,
                        "old_values_json": None,
                        "new_values_json": '{"source":"auto-seed"}',
                        "commentaire": f"Audit auto {i:03d}",
                        "ip_client": f"192.168.10.{(i % 200) + 1}",
                    }
                )

            conn.execute(
                text(
                    """
                    INSERT INTO audit_log (
                        date_action, id_utilisateur, table_name, record_id, action,
                        old_values_json, new_values_json, commentaire, ip_client
                    ) VALUES (
                        :date_action, :id_utilisateur, :table_name, :record_id, :action,
                        :old_values_json, :new_values_json, :commentaire, :ip_client
                    )
                    """
                ),
                audit_rows,
            )

            current_year = 2026
            for code, count in doc_counts.items():
                conn.execute(
                    text(
                        """
                        INSERT IGNORE INTO counters (categorie, code, annee, valeur_courante, longueur, prefixe, suffixe, reset_annuel)
                        VALUES ('DOCUMENT', :code, :annee, 0, 4, :code, NULL, 1)
                        """
                    ),
                    {"code": code, "annee": current_year},
                )
                conn.execute(
                    text(
                        """
                        UPDATE counters
                        SET valeur_courante = :count, longueur = 4, prefixe = :code
                        WHERE categorie = 'DOCUMENT' AND code = :code AND annee = :annee
                        """
                    ),
                    {"count": count, "code": code, "annee": current_year},
                )

            for tier_code, tier_count in (("CL", NUM_CLIENTS), ("FR", NUM_SUPPLIERS), ("AD", 0), ("PR", 0), ("SC", 0)):
                conn.execute(
                    text(
                        """
                        INSERT IGNORE INTO counters (categorie, code, annee, valeur_courante, longueur, prefixe, suffixe, reset_annuel)
                        VALUES ('TIERS', :code, :annee, 0, 3, :code, NULL, 1)
                        """
                    ),
                    {"code": tier_code, "annee": current_year},
                )
                conn.execute(
                    text(
                        """
                        UPDATE counters
                        SET valeur_courante = :count, longueur = 3, prefixe = :code
                        WHERE categorie = 'TIERS' AND code = :code AND annee = :annee
                        """
                    ),
                    {"count": tier_count, "code": tier_code, "annee": current_year},
                )

        engine.dispose()
        return True
    except Exception as e:
        engine.dispose()
        print(f"\n[ERROR] Fake data generation failed: {e}")
        return False


# ── main ───────────────────────────────────────────────────────────────────
def main():
    separator()
    print("       ERP — Database Setup Utility")
    separator()

    # ── connection info ────────────────────────────────────────────────────
    print("\nMySQL connection settings (press Enter for defaults):\n")
    host     = input("  Host     [localhost] : ").strip() or "localhost"
    port     = input("  Port     [3306]      : ").strip() or "3306"
    user     = input("  User     [root]      : ").strip() or "root"
    password = getpass.getpass("  Password             : ")

    # ── mode choice ────────────────────────────────────────────────────────
    separator()
    print("\nChoose setup mode:\n")
    print("  [1]  Empty database   — schema only, no data")
    print("  [2]  With fake data   — schema + sample data for development")
    print("  [0]  Cancel\n")

    choice = input("Your choice: ").strip()

    if choice == "0":
        print("\nCancelled. Nothing was done.")
        sys.exit(0)

    if choice not in ("1", "2"):
        print("\n[ERROR] Invalid choice. Exiting.")
        sys.exit(1)

    # ── confirmation ───────────────────────────────────────────────────────
    separator()
    mode_label = "EMPTY database" if choice == "1" else "database WITH FAKE DATA"
    print(f"\n  ⚠  This will DROP and recreate the 'erp' database ({mode_label}).")
    confirm = input("  Type 'yes' to confirm: ").strip().lower()

    if confirm != "yes":
        print("\nCancelled. Nothing was done.")
        sys.exit(0)

    # ── execute ────────────────────────────────────────────────────────────
    separator()
    print(f"\n[1/{'2' if choice == '2' else '1'}] Running schema file...")
    print(f"      → {SCHEMA_FILE}")

    ok = run_sql_file(host, port, user, password, SCHEMA_FILE)
    if not ok:
        print("\n[FAILED] Schema creation failed. Aborting.")
        sys.exit(1)

    print("      ✓ Schema created successfully.")

    # verify connection after schema created
    if verify_connection(host, port, user, password):
        print("      ✓ Connection to 'erp' database verified.")

    if choice == "2":
        print("\n[2/2] Generating structured large fake data...")
        print(f"      → {NUM_CLIENTS} clients uniques, {NUM_SUPPLIERS} fournisseurs, {NUM_FAMILIES} familles, {NUM_ARTICLES} articles")
        print(
            f"      → {NUM_SALES_DOCUMENTS} documents ventes + {NUM_PURCHASE_DOCUMENTS} documents achats "
            f"(format code DV0001), >=3 lignes/doc (+ des docs a 50 lignes)"
        )
        print(f"      → {NUM_PAYMENTS} paiements, {NUM_AUDIT_LOGS} audit logs, counters mis a jour")

        ok = _seed_large_fake_data(host, port, user, password)
        if not ok:
            print("\n[FAILED] Fake data generation failed.")
            sys.exit(1)

        print("      ✓ Large fake dataset inserted successfully.")

    # ── done ───────────────────────────────────────────────────────────────
    separator()
    print("\n  ✓ Database setup complete!\n")
    if choice == "2":
        print("  Users created (password = 1234):")
        print("    admin, admin2, karim, sara, youssef, fatima, hamid\n")
    separator()


if __name__ == "__main__":
    main()