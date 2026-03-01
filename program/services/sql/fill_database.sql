/* ==========================================================
   SEED DATA — Development / Fake Data
   Run AFTER ERP_database.sql
   ========================================================== */

USE erp;
SET FOREIGN_KEY_CHECKS = 0;

-- =========================
-- informations_societe
-- =========================
INSERT IGNORE INTO informations_societe (
  nom_societe, activite, forme_juridique, patente, cnss,
  telephone_fix, fax, site_web, ice, if_fiscal, rc,
  email, adresse
) VALUES (
  'TechMaroc SARL',
  'Commerce de matériel informatique et bureautique',
  'SARL',
  'PAT-2024-00123',
  'CNSS-456789',
  '0522-123456',
  '0522-123457',
  'www.techmaroc.ma',
  '002345678901234',
  'IF-78901',
  'RC-CASA-12345',
  'contact@techmaroc.ma',
  '25 Bd Zerktouni, Casablanca 20000'
);

-- =========================
-- 5 utilisateurs (password = 1234)
-- bcrypt hash of "1234"
-- "admin" / "password"
-- "admin2" / ""
-- =========================
INSERT IGNORE INTO utilisateurs (nom_utilisateur, mot_de_passe_hash, role, actif) VALUES
('karim',    '$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK', 'VENDEUR',      1),
('sara',     '$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK', 'VENDEUR',      1),
('youssef',  '$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK', 'VENDEUR',      1),
('fatima',   '$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK', 'GESTIONNAIRE', 1),
('hamid',    '$2b$12$T8lg6f.17E.1vvAJg6Z0kut1FBFnH9zFlRX2wmblh9xZ92hmqvEfK', 'GESTIONNAIRE', 1),
('admin',    '$2b$12$wXYP3T8npdFM52DqzU2izO2cOZq./F9gVicytcXd6Ei4gBsPggUvS', 'ADMIN',        1),
('admin2',   '$2b$12$TH5ytK6Z/AtDFpFkCnnEcuuqHHyyeRUNFfacBamCmlHoHQJYUhk3K', 'ADMIN',        1);

-- NOTE: Replace hashes above with real bcrypt("1234") before sharing.
-- Generate with Python: import bcrypt; bcrypt.hashpw(b"1234", bcrypt.gensalt(12))

-- =========================
-- 10 familles
-- =========================
INSERT IGNORE INTO familles (nom_famille, description, taux_tva, suivi_stock, unite_defaut) VALUES
('Informatique',         'Matériel et équipements informatiques',        20.00, 1, 'PCS'),
('Bureautique',          'Fournitures et équipements de bureau',         20.00, 1, 'PCS'),
('Réseau',               'Équipements réseau et télécommunications',     20.00, 1, 'PCS'),
('Consommables',         'Encres, toners, papier et consommables',       20.00, 1, 'PCS'),
('Mobilier Bureau',      'Tables, chaises et rangements de bureau',      20.00, 1, 'PCS'),
('Logiciels',            'Licences et logiciels professionnels',         20.00, 0, 'LIC'),
('Électroménager Pro',   'Équipements électroménagers professionnels',   20.00, 1, 'PCS'),
('Sécurité',             'Caméras, alarmes et systèmes de sécurité',     20.00, 1, 'PCS'),
('Téléphonie',           'Téléphones fixes et mobiles professionnels',   20.00, 1, 'PCS'),
('Imprimerie',           'Imprimantes, photocopieurs et scanners',       20.00, 1, 'PCS');

-- =========================
-- 20 articles (2 per famille)
-- =========================
INSERT IGNORE INTO articles
  (nom_article, description, prix_vente_ht, prix_achat_ht, id_famille, taux_tva, suivi_stock, unite, reference_interne)
VALUES
-- Informatique (id_famille=1)
('Ordinateur Portable HP 15',     'HP 15s, Intel i5, 8Go RAM, 512Go SSD',       5500.00, 4200.00, 1, 20.00, 1, 'PCS', 'INFO-001'),
('PC Bureau Dell OptiPlex',       'Dell OptiPlex 3090, i5, 8Go, 256Go SSD',     4800.00, 3600.00, 1, 20.00, 1, 'PCS', 'INFO-002'),

-- Bureautique (id_famille=2)
('Bureau Directeur 160cm',        'Bureau en bois massif 160x80cm',             2200.00, 1600.00, 2, 20.00, 1, 'PCS', 'BUR-001'),
('Chaise Ergonomique Pro',        'Chaise de bureau ergonomique avec accoudoirs',980.00,  700.00, 2, 20.00, 1, 'PCS', 'BUR-002'),

-- Réseau (id_famille=3)
('Switch 24 ports TP-Link',       'Switch manageable 24 ports Gigabit',         1850.00, 1300.00, 3, 20.00, 1, 'PCS', 'NET-001'),
('Routeur WiFi 6 Asus',           'Routeur dual-band AX3000 WiFi 6',            1200.00,  850.00, 3, 20.00, 1, 'PCS', 'NET-002'),

-- Consommables (id_famille=4)
('Toner HP LaserJet 85A',         'Cartouche toner noir HP CE285A',              320.00,  210.00, 4, 20.00, 1, 'PCS', 'CONS-001'),
('Ramette Papier A4 80g',         'Ramette 500 feuilles A4 blanc 80g/m²',        45.00,   28.00, 4, 20.00, 1, 'RAM', 'CONS-002'),

-- Mobilier Bureau (id_famille=5)
('Armoire Métallique 4 tiroirs',  'Armoire de classement 4 tiroirs verrouillable',1450.00,1050.00, 5, 20.00, 1, 'PCS', 'MOB-001'),
('Table de Réunion 8 places',     'Table ovale de conférence 240x120cm',         3200.00, 2400.00, 5, 20.00, 1, 'PCS', 'MOB-002'),

-- Logiciels (id_famille=6)
('Microsoft Office 365 Business', 'Licence annuelle Office 365 Business',        1800.00, 1400.00, 6, 20.00, 0, 'LIC', 'LOG-001'),
('Antivirus Kaspersky 1an',       'Licence Kaspersky Endpoint Security 1 an',     650.00,  480.00, 6, 20.00, 0, 'LIC', 'LOG-002'),

-- Électroménager Pro (id_famille=7)
('Climatiseur Gree 18000 BTU',    'Climatiseur split inverter 18000 BTU',        4500.00, 3200.00, 7, 20.00, 1, 'PCS', 'ELEC-001'),
('Réfrigérateur Professionnel',   'Réfrigérateur inox 350L pour bureau',         3800.00, 2800.00, 7, 20.00, 1, 'PCS', 'ELEC-002'),

-- Sécurité (id_famille=8)
('Caméra IP Hikvision 4MP',       'Caméra de surveillance IP PoE 4 mégapixels', 1100.00,  780.00, 8, 20.00, 1, 'PCS', 'SEC-001'),
('Alarme Intrusion GSM',          'Système alarme sans fil GSM avec sirène',      850.00,  600.00, 8, 20.00, 1, 'KIT', 'SEC-002'),

-- Téléphonie (id_famille=9)
('Téléphone IP Yealink T31P',     'Téléphone IP 2 lignes SIP ecran LCD',          780.00,  550.00, 9, 20.00, 1, 'PCS', 'TEL-001'),
('Casque Bluetooth Jabra',        'Casque professionnel Bluetooth Jabra Evolve',   920.00,  680.00, 9, 20.00, 1, 'PCS', 'TEL-002'),

-- Imprimerie (id_famille=10)
('Imprimante Multifonction HP',   'HP LaserJet Pro MFP M428fdw A4',              3200.00, 2300.00,10, 20.00, 1, 'PCS', 'IMP-001'),
('Photocopieur Ricoh A3',         'Photocopieur Ricoh IM 2702 A3 27ppm',         18500.00,14000.00,10, 20.00, 1, 'PCS', 'IMP-002');

-- =========================
-- tiers: 10 CLIENTS, 10 FOURNISSEURS, 2 SOCIETE, 2 PARTICULIER, 2 ADMIN
-- =========================
INSERT IGNORE INTO tiers (code_tiers, type_tiers, nom_tiers, adresse, telephone, email, plafond_credit, actif) VALUES
-- 10 CLIENTS
('CL-001', 'CLIENT',      'Société Atlas SARL',           '15 Rue Ibn Khaldoun, Casablanca',  '0522-441100', 'contact@atlas.ma',           50000.00, 1),
('CL-002', 'CLIENT',      'Maroc Distribution SA',        '22 Bd Hassan II, Rabat',           '0537-221133', 'info@marocdistrib.ma',       75000.00, 1),
('CL-003', 'CLIENT',      'Bureau Express SARL',          '8 Av Allal Ben Abdellah, Fès',     '0535-441200', 'bureau.express@gmail.com',   30000.00, 1),
('CL-004', 'CLIENT',      'TechSolutions Maroc',          '3 Rue de Fès, Meknès',             '0535-551010', 'tech@solutions.ma',          40000.00, 1),
('CL-005', 'CLIENT',      'Cabinet Conseil RH',           '12 Bd Zerktouni, Casablanca',      '0522-771234', 'rh@cabinet.ma',              20000.00, 1),
('CL-006', 'CLIENT',      'Clinique Al Amal',             '5 Rue Ibn Sina, Agadir',           '0528-221100', 'clinique.amal@ma',           35000.00, 1),
('CL-007', 'CLIENT',      'Hôtel Andalous',               '1 Av Mohammed V, Marrakech',       '0524-441500', 'contact@hotel-andalous.ma',  60000.00, 1),
('CL-008', 'CLIENT',      'Pharmacie Centrale Rabat',     '7 Av Fal Ould Oumeir, Rabat',      '0537-660022', 'pharmacie.centrale@ma',      15000.00, 1),
('CL-009', 'CLIENT',      'École Supérieure de Commerce', '18 Bd Al Massira, Casablanca',     '0522-881234', 'esc@ecole.ma',               25000.00, 1),
('CL-010', 'CLIENT',      'Garage Auto Plus',             '34 Route de Ouarzazate, Marrakech','0524-551234', 'autoplus@garage.ma',         10000.00, 1),

-- 10 FOURNISSEURS
('FR-001', 'FOURNISSEUR', 'Atlas Fournitures SARL',       '11 Zone Industrielle, Casablanca', '0522-301010', 'atlas.four@ma',               0.00, 1),
('FR-002', 'FOURNISSEUR', 'Maroc IT Distribution',        '9 Rue Sidi Belyout, Casablanca',   '0522-401234', 'contact@marocit.ma',          0.00, 1),
('FR-003', 'FOURNISSEUR', 'Global Tech Import',           '3 Bd Bir Anzarane, Rabat',         '0537-501234', 'global@techimport.ma',        0.00, 1),
('FR-004', 'FOURNISSEUR', 'Bureau Partenaire SARL',       '6 Rue du Rif, Fès',                '0535-601111', 'bureau@partenaire.ma',        0.00, 1),
('FR-005', 'FOURNISSEUR', 'ElectroPro Maroc',             '22 Av Hassan II, Kenitra',         '0537-701234', 'electropro@maroc.ma',         0.00, 1),
('FR-006', 'FOURNISSEUR', 'Sécurit Systems SA',           '14 Rue Imam Malik, Casablanca',    '0522-801234', 'securit@systems.ma',          0.00, 1),
('FR-007', 'FOURNISSEUR', 'Ricoh Maroc',                  '5 Bd Prince Moulay Abdellah, Casa','0522-901010', 'ricoh@maroc.ma',              0.00, 1),
('FR-008', 'FOURNISSEUR', 'HP Maroc Distribution',        '2 Av Abi Regreg, Rabat',           '0537-110011', 'hp@distribution.ma',          0.00, 1),
('FR-009', 'FOURNISSEUR', 'Mobilier Pro SARL',            '7 Zone Franche, Tanger',           '0539-221100', 'mobilier.pro@ma',             0.00, 1),
('FR-010', 'FOURNISSEUR', 'Consomma Plus',                '18 Rue Allal El Fassi, Meknès',    '0535-331122', 'consomma.plus@ma',            0.00, 1),

-- 2 SOCIETE
('SOC-001', 'SOCIETE',    'Groupe Holmarcom',             '1 Bd Abdelmoumen, Casablanca',     '0522-221100', 'contact@holmarcom.ma',      200000.00, 1),
('SOC-002', 'SOCIETE',    'OCP Group',                    'Bd Bir Anzarane, Casablanca',      '0522-230000', 'contact@ocpgroup.ma',       500000.00, 1),

-- 2 PARTICULIER
('PAR-001', 'PARTICULIER','M. Rachid Bensouda',           '23 Rue Kettani, Fès',              '0661-112233', 'r.bensouda@gmail.com',        2000.00, 1),
('PAR-002', 'PARTICULIER','Mme Zineb Chraibi',            '9 Rue Atlas, Rabat',               '0662-334455', 'zineb.chraibi@gmail.com',     1500.00, 1),

-- 2 ADMIN
('ADM-001', 'ADMIN',      'Direction Générale TechMaroc', '25 Bd Zerktouni, Casablanca',      '0522-123456', 'dg@techmaroc.ma',                0.00, 1),
('ADM-002', 'ADMIN',      'Service Comptabilité',         '25 Bd Zerktouni, Casablanca',      '0522-123458', 'compta@techmaroc.ma',            0.00, 1);

-- =========================
-- 50 documents (10 per type)
-- DV=1, BC=2, BL=3, FA=4, AV=5  (id_type_document)
-- id_domaine = 1 (VENTE)
-- id_statut: BROUILLON=1, VALIDE=2, ANNULE=3, PARTIEL=4, PAYE=5
-- id_vendeur: 4=admin, 5=admin2, 6=karim, 7=sara, 8=youssef
-- id_tiers: 1..10 clients
-- =========================

-- ---- 10 DEVIS (code DV, id_type_document=1) ----
INSERT IGNORE INTO documents (id_domaine, id_type_document, numero_document, id_tiers, date_document, date_livraison, mode_prix, total_ht, total_tva, total_ttc, solde, id_vendeur, id_statut, commentaire) VALUES
(1,1,'DV-001',1, '2026-01-05',NULL,       'HT', 5500.00, 1100.00, 6600.00, 6600.00, 4,2, 'Devis matériel informatique'),
(1,1,'DV-002',2, '2026-01-08',NULL,       'HT', 3800.00,  760.00, 4560.00, 4560.00, 6,2, 'Devis bureautique'),
(1,1,'DV-003',3, '2026-01-12',NULL,       'HT', 2200.00,  440.00, 2640.00, 2640.00, 7,1, 'Devis mobilier'),
(1,1,'DV-004',4, '2026-01-15',NULL,       'HT', 9600.00, 1920.00,11520.00,11520.00, 6,2, 'Devis réseau complet'),
(1,1,'DV-005',5, '2026-01-20',NULL,       'HT', 1300.00,  260.00, 1560.00, 1560.00, 8,1, 'Devis consommables trimestriel'),
(1,1,'DV-006',6, '2026-01-25',NULL,       'HT', 4500.00,  900.00, 5400.00, 5400.00, 4,2, 'Devis climatisation bureau'),
(1,1,'DV-007',7, '2026-02-01',NULL,       'HT', 1950.00,  390.00, 2340.00, 2340.00, 7,3, 'Devis téléphonie annulé'),
(1,1,'DV-008',8, '2026-02-05',NULL,       'HT', 6400.00, 1280.00, 7680.00, 7680.00, 6,2, 'Devis sécurité caméras'),
(1,1,'DV-009',9, '2026-02-10',NULL,       'HT', 3600.00,  720.00, 4320.00, 4320.00, 5,1, 'Devis logiciels entreprise'),
(1,1,'DV-010',10,'2026-02-15',NULL,       'HT',18500.00, 3700.00,22200.00,22200.00, 4,2, 'Devis photocopieur A3');

-- ---- 10 BON DE COMMANDE (BC, id_type_document=2) ----
INSERT IGNORE INTO documents (id_domaine, id_type_document, numero_document, id_tiers, date_document, date_livraison, mode_prix, total_ht, total_tva, total_ttc, solde, id_vendeur, id_statut, commentaire) VALUES
(1,2,'BC-001',1, '2026-01-06','2026-01-20','HT', 5500.00, 1100.00, 6600.00, 6600.00, 4,2, 'Commande PC portable'),
(1,2,'BC-002',2, '2026-01-09','2026-01-25','HT', 3800.00,  760.00, 4560.00, 4560.00, 6,2, 'Commande fournitures bureau'),
(1,2,'BC-003',3, '2026-01-13','2026-01-28','HT', 4400.00,  880.00, 5280.00, 5280.00, 7,2, 'Commande mobilier salle réunion'),
(1,2,'BC-004',4, '2026-01-16','2026-02-01','HT', 9600.00, 1920.00,11520.00,11520.00, 6,2, 'Commande infrastructure réseau'),
(1,2,'BC-005',5, '2026-01-21','2026-02-05','HT', 1300.00,  260.00, 1560.00, 1560.00, 8,2, 'Commande consommables'),
(1,2,'BC-006',6, '2026-01-26','2026-02-10','HT', 9000.00, 1800.00,10800.00,10800.00, 4,2, 'Commande climatiseurs x2'),
(1,2,'BC-007',7, '2026-02-02','2026-02-15','HT', 1560.00,  312.00, 1872.00, 1872.00, 7,2, 'Commande téléphones IP'),
(1,2,'BC-008',8, '2026-02-06','2026-02-20','HT', 6400.00, 1280.00, 7680.00, 7680.00, 6,2, 'Commande système sécurité'),
(1,2,'BC-009',9, '2026-02-11','2026-02-25','HT', 3600.00,  720.00, 4320.00, 4320.00, 5,2, 'Commande licences logiciels'),
(1,2,'BC-010',10,'2026-02-16','2026-03-01','HT',18500.00, 3700.00,22200.00,22200.00, 4,2, 'Commande photocopieur');

-- ---- 10 BON DE LIVRAISON (BL, id_type_document=3) ----
INSERT IGNORE INTO documents (id_domaine, id_type_document, numero_document, id_tiers, date_document, date_livraison, mode_prix, total_ht, total_tva, total_ttc, solde, id_vendeur, id_statut, commentaire) VALUES
(1,3,'BL-001',1, '2026-01-20','2026-01-20','HT', 5500.00, 1100.00, 6600.00, 6600.00, 4,2, 'Livraison PC portable'),
(1,3,'BL-002',2, '2026-01-25','2026-01-25','HT', 3800.00,  760.00, 4560.00, 4560.00, 6,2, 'Livraison fournitures bureau'),
(1,3,'BL-003',3, '2026-01-28','2026-01-28','HT', 4400.00,  880.00, 5280.00, 5280.00, 7,2, 'Livraison mobilier'),
(1,3,'BL-004',4, '2026-02-01','2026-02-01','HT', 9600.00, 1920.00,11520.00,11520.00, 6,2, 'Livraison réseau'),
(1,3,'BL-005',5, '2026-02-05','2026-02-05','HT', 1300.00,  260.00, 1560.00, 1560.00, 8,2, 'Livraison consommables'),
(1,3,'BL-006',6, '2026-02-10','2026-02-10','HT', 9000.00, 1800.00,10800.00,10800.00, 4,2, 'Livraison climatiseurs'),
(1,3,'BL-007',7, '2026-02-15','2026-02-15','HT', 1560.00,  312.00, 1872.00, 1872.00, 7,2, 'Livraison téléphones IP'),
(1,3,'BL-008',8, '2026-02-20','2026-02-20','HT', 6400.00, 1280.00, 7680.00, 7680.00, 6,2, 'Livraison sécurité'),
(1,3,'BL-009',9, '2026-02-25','2026-02-25','HT', 3600.00,  720.00, 4320.00, 4320.00, 5,2, 'Livraison logiciels'),
(1,3,'BL-010',10,'2026-03-01','2026-03-01','HT',18500.00, 3700.00,22200.00,22200.00, 4,2, 'Livraison photocopieur');

-- ---- 10 FACTURES (FA, id_type_document=4) ----
INSERT IGNORE INTO documents (id_domaine, id_type_document, numero_document, id_tiers, date_document, date_livraison, mode_prix, total_ht, total_tva, total_ttc, solde, id_vendeur, id_statut, commentaire) VALUES
(1,4,'FA-001',1, '2026-01-21',NULL,'HT', 5500.00, 1100.00, 6600.00,    0.00, 4,5, 'Facture PC portable - payée'),
(1,4,'FA-002',2, '2026-01-26',NULL,'HT', 3800.00,  760.00, 4560.00,    0.00, 6,5, 'Facture fournitures - payée'),
(1,4,'FA-003',3, '2026-01-29',NULL,'HT', 4400.00,  880.00, 5280.00, 2640.00, 7,4, 'Facture mobilier - paiement partiel'),
(1,4,'FA-004',4, '2026-02-02',NULL,'HT', 9600.00, 1920.00,11520.00,    0.00, 6,5, 'Facture réseau - payée'),
(1,4,'FA-005',5, '2026-02-06',NULL,'HT', 1300.00,  260.00, 1560.00, 1560.00, 8,2, 'Facture consommables - en attente'),
(1,4,'FA-006',6, '2026-02-11',NULL,'HT', 9000.00, 1800.00,10800.00, 5400.00, 4,4, 'Facture climatiseurs - paiement partiel'),
(1,4,'FA-007',7, '2026-02-16',NULL,'HT', 1560.00,  312.00, 1872.00,    0.00, 7,5, 'Facture téléphonie - payée'),
(1,4,'FA-008',8, '2026-02-21',NULL,'HT', 6400.00, 1280.00, 7680.00, 7680.00, 6,2, 'Facture sécurité - validée'),
(1,4,'FA-009',9, '2026-02-26',NULL,'HT', 3600.00,  720.00, 4320.00, 4320.00, 5,2, 'Facture logiciels - validée'),
(1,4,'FA-010',10,'2026-03-02',NULL,'HT',18500.00, 3700.00,22200.00,11100.00, 4,4, 'Facture photocopieur - paiement partiel');

-- ---- 10 AVOIRS (AV, id_type_document=5) ----
INSERT IGNORE INTO documents (id_domaine, id_type_document, numero_document, id_tiers, date_document, date_livraison, mode_prix, total_ht, total_tva, total_ttc, solde, id_vendeur, id_statut, commentaire) VALUES
(1,5,'AV-001',1, '2026-01-28',NULL,'HT',  550.00,  110.00,  660.00,  660.00, 4,2, 'Avoir retour article défectueux'),
(1,5,'AV-002',2, '2026-02-01',NULL,'HT',  380.00,   76.00,  456.00,  456.00, 6,2, 'Avoir remise commerciale'),
(1,5,'AV-003',3, '2026-02-03',NULL,'HT',  440.00,   88.00,  528.00,  528.00, 7,2, 'Avoir retour mobilier endommagé'),
(1,5,'AV-004',4, '2026-02-05',NULL,'HT',  960.00,  192.00, 1152.00, 1152.00, 6,2, 'Avoir erreur de facturation réseau'),
(1,5,'AV-005',5, '2026-02-07',NULL,'HT',  130.00,   26.00,  156.00,  156.00, 8,2, 'Avoir consommables non conformes'),
(1,5,'AV-006',6, '2026-02-12',NULL,'HT',  900.00,  180.00, 1080.00, 1080.00, 4,2, 'Avoir climatiseur retourné en panne'),
(1,5,'AV-007',7, '2026-02-17',NULL,'HT',  156.00,   31.20,  187.20,  187.20, 7,2, 'Avoir téléphone retourné'),
(1,5,'AV-008',8, '2026-02-22',NULL,'HT',  640.00,  128.00,  768.00,  768.00, 6,2, 'Avoir caméra défectueuse'),
(1,5,'AV-009',9, '2026-02-27',NULL,'HT',  360.00,   72.00,  432.00,  432.00, 5,2, 'Avoir licence annulée'),
(1,5,'AV-010',10,'2026-03-03',NULL,'HT', 1850.00,  370.00, 2220.00, 2220.00, 4,2, 'Avoir remise sur photocopieur');

-- =========================
-- details_documents
-- Each document gets 2-3 lines
-- document IDs: DV=1..10, BC=11..20, BL=21..30, FA=31..40, AV=41..50
-- article IDs: 1..20
-- =========================

-- DEVIS details
INSERT IGNORE INTO details_documents (id_document, id_article, description, quantite, prix_unitaire_ht, prix_unitaire_ttc, unite_vente, taux_tva, marge_beneficiaire, total_ligne_ht, total_ligne_tva, total_ligne_ttc) VALUES
(1,  1, 'Ordinateur Portable HP 15',    1, 5500.00, 6600.00, 'PCS', 20.00, 1300.00,  5500.00, 1100.00,  6600.00),
(2,  3, 'Bureau Directeur 160cm',        1, 2200.00, 2640.00, 'PCS', 20.00,  600.00,  2200.00,  440.00,  2640.00),
(2,  4, 'Chaise Ergonomique Pro',        2,  980.00, 1176.00, 'PCS', 20.00,  280.00,  1960.00,  392.00,  2352.00),
(3,  9, 'Armoire Métallique 4 tiroirs',  1, 1450.00, 1740.00, 'PCS', 20.00,  400.00,  1450.00,  290.00,  1740.00),
(3, 10, 'Table de Réunion 8 places',     1, 3200.00, 3840.00, 'PCS', 20.00,  800.00,  3200.00,  640.00,  3840.00),
(4,  5, 'Switch 24 ports TP-Link',       2, 1850.00, 2220.00, 'PCS', 20.00,  550.00,  3700.00,  740.00,  4440.00),
(4,  6, 'Routeur WiFi 6 Asus',           2, 1200.00, 1440.00, 'PCS', 20.00,  350.00,  2400.00,  480.00,  2880.00),
(5,  7, 'Toner HP LaserJet 85A',         2,  320.00,  384.00, 'PCS', 20.00,  110.00,   640.00,  128.00,   768.00),
(5,  8, 'Ramette Papier A4 80g',        15,   45.00,   54.00, 'RAM', 20.00,   17.00,   675.00,  135.00,   810.00),
(6, 13, 'Climatiseur Gree 18000 BTU',    1, 4500.00, 5400.00, 'PCS', 20.00, 1300.00,  4500.00,  900.00,  5400.00),
(7, 17, 'Téléphone IP Yealink T31P',     2,  780.00,  936.00, 'PCS', 20.00,  230.00,  1560.00,  312.00,  1872.00),
(8, 15, 'Caméra IP Hikvision 4MP',       4, 1100.00, 1320.00, 'PCS', 20.00,  320.00,  4400.00,  880.00,  5280.00),
(8, 16, 'Alarme Intrusion GSM',          1,  850.00, 1020.00, 'KIT', 20.00,  250.00,   850.00,  170.00,  1020.00),
(9, 11, 'Microsoft Office 365',          2, 1800.00, 2160.00, 'LIC', 20.00,  400.00,  3600.00,  720.00,  4320.00),
(10,19, 'Imprimante Multifonction HP',   1, 3200.00, 3840.00, 'PCS', 20.00,  900.00,  3200.00,  640.00,  3840.00),
(10,20, 'Photocopieur Ricoh A3',         1,18500.00,22200.00, 'PCS', 20.00, 4500.00, 18500.00, 3700.00, 22200.00);

-- BON DE COMMANDE details (doc 11..20)
INSERT IGNORE INTO details_documents (id_document, id_article, description, quantite, prix_unitaire_ht, prix_unitaire_ttc, unite_vente, taux_tva, marge_beneficiaire, total_ligne_ht, total_ligne_tva, total_ligne_ttc) VALUES
(11, 1, 'Ordinateur Portable HP 15',   1, 5500.00, 6600.00, 'PCS', 20.00, 1300.00,  5500.00, 1100.00,  6600.00),
(12, 3, 'Bureau Directeur 160cm',       1, 2200.00, 2640.00, 'PCS', 20.00,  600.00,  2200.00,  440.00,  2640.00),
(12, 4, 'Chaise Ergonomique Pro',       2,  980.00, 1176.00, 'PCS', 20.00,  280.00,  1960.00,  392.00,  2352.00),
(13, 9, 'Armoire Métallique 4 tiroirs', 2, 1450.00, 1740.00, 'PCS', 20.00,  400.00,  2900.00,  580.00,  3480.00),
(13,10, 'Table de Réunion 8 places',    1, 3200.00, 3840.00, 'PCS', 20.00,  800.00,  3200.00,  640.00,  3840.00),
(14, 5, 'Switch 24 ports TP-Link',      2, 1850.00, 2220.00, 'PCS', 20.00,  550.00,  3700.00,  740.00,  4440.00),
(14, 6, 'Routeur WiFi 6 Asus',          2, 1200.00, 1440.00, 'PCS', 20.00,  350.00,  2400.00,  480.00,  2880.00),
(15, 7, 'Toner HP LaserJet 85A',        2,  320.00,  384.00, 'PCS', 20.00,  110.00,   640.00,  128.00,   768.00),
(15, 8, 'Ramette Papier A4 80g',       15,   45.00,   54.00, 'RAM', 20.00,   17.00,   675.00,  135.00,   810.00),
(16,13, 'Climatiseur Gree 18000 BTU',   2, 4500.00, 5400.00, 'PCS', 20.00, 1300.00,  9000.00, 1800.00, 10800.00),
(17,17, 'Téléphone IP Yealink T31P',    2,  780.00,  936.00, 'PCS', 20.00,  230.00,  1560.00,  312.00,  1872.00),
(18,15, 'Caméra IP Hikvision 4MP',      4, 1100.00, 1320.00, 'PCS', 20.00,  320.00,  4400.00,  880.00,  5280.00),
(18,16, 'Alarme Intrusion GSM',         1,  850.00, 1020.00, 'KIT', 20.00,  250.00,   850.00,  170.00,  1020.00),
(19,11, 'Microsoft Office 365',         2, 1800.00, 2160.00, 'LIC', 20.00,  400.00,  3600.00,  720.00,  4320.00),
(20,20, 'Photocopieur Ricoh A3',        1,18500.00,22200.00, 'PCS', 20.00, 4500.00, 18500.00, 3700.00, 22200.00);

-- BON DE LIVRAISON details (doc 21..30) — same lines as BC
INSERT IGNORE INTO details_documents (id_document, id_article, description, quantite, prix_unitaire_ht, prix_unitaire_ttc, unite_vente, taux_tva, marge_beneficiaire, total_ligne_ht, total_ligne_tva, total_ligne_ttc) VALUES
(21, 1, 'Ordinateur Portable HP 15',   1, 5500.00, 6600.00, 'PCS', 20.00, 1300.00,  5500.00, 1100.00,  6600.00),
(22, 3, 'Bureau Directeur 160cm',       1, 2200.00, 2640.00, 'PCS', 20.00,  600.00,  2200.00,  440.00,  2640.00),
(22, 4, 'Chaise Ergonomique Pro',       2,  980.00, 1176.00, 'PCS', 20.00,  280.00,  1960.00,  392.00,  2352.00),
(23, 9, 'Armoire Métallique 4 tiroirs', 2, 1450.00, 1740.00, 'PCS', 20.00,  400.00,  2900.00,  580.00,  3480.00),
(23,10, 'Table de Réunion 8 places',    1, 3200.00, 3840.00, 'PCS', 20.00,  800.00,  3200.00,  640.00,  3840.00),
(24, 5, 'Switch 24 ports TP-Link',      2, 1850.00, 2220.00, 'PCS', 20.00,  550.00,  3700.00,  740.00,  4440.00),
(24, 6, 'Routeur WiFi 6 Asus',          2, 1200.00, 1440.00, 'PCS', 20.00,  350.00,  2400.00,  480.00,  2880.00),
(25, 7, 'Toner HP LaserJet 85A',        2,  320.00,  384.00, 'PCS', 20.00,  110.00,   640.00,  128.00,   768.00),
(25, 8, 'Ramette Papier A4 80g',       15,   45.00,   54.00, 'RAM', 20.00,   17.00,   675.00,  135.00,   810.00),
(26,13, 'Climatiseur Gree 18000 BTU',   2, 4500.00, 5400.00, 'PCS', 20.00, 1300.00,  9000.00, 1800.00, 10800.00),
(27,17, 'Téléphone IP Yealink T31P',    2,  780.00,  936.00, 'PCS', 20.00,  230.00,  1560.00,  312.00,  1872.00),
(28,15, 'Caméra IP Hikvision 4MP',      4, 1100.00, 1320.00, 'PCS', 20.00,  320.00,  4400.00,  880.00,  5280.00),
(28,16, 'Alarme Intrusion GSM',         1,  850.00, 1020.00, 'KIT', 20.00,  250.00,   850.00,  170.00,  1020.00),
(29,11, 'Microsoft Office 365',         2, 1800.00, 2160.00, 'LIC', 20.00,  400.00,  3600.00,  720.00,  4320.00),
(30,20, 'Photocopieur Ricoh A3',        1,18500.00,22200.00, 'PCS', 20.00, 4500.00, 18500.00, 3700.00, 22200.00);

-- FACTURES details (doc 31..40)
INSERT IGNORE INTO details_documents (id_document, id_article, description, quantite, prix_unitaire_ht, prix_unitaire_ttc, unite_vente, taux_tva, marge_beneficiaire, total_ligne_ht, total_ligne_tva, total_ligne_ttc) VALUES
(31, 1, 'Ordinateur Portable HP 15',   1, 5500.00, 6600.00, 'PCS', 20.00, 1300.00,  5500.00, 1100.00,  6600.00),
(32, 3, 'Bureau Directeur 160cm',       1, 2200.00, 2640.00, 'PCS', 20.00,  600.00,  2200.00,  440.00,  2640.00),
(32, 4, 'Chaise Ergonomique Pro',       2,  980.00, 1176.00, 'PCS', 20.00,  280.00,  1960.00,  392.00,  2352.00),
(33, 9, 'Armoire Métallique 4 tiroirs', 2, 1450.00, 1740.00, 'PCS', 20.00,  400.00,  2900.00,  580.00,  3480.00),
(33,10, 'Table de Réunion 8 places',    1, 3200.00, 3840.00, 'PCS', 20.00,  800.00,  3200.00,  640.00,  3840.00),
(34, 5, 'Switch 24 ports TP-Link',      2, 1850.00, 2220.00, 'PCS', 20.00,  550.00,  3700.00,  740.00,  4440.00),
(34, 6, 'Routeur WiFi 6 Asus',          2, 1200.00, 1440.00, 'PCS', 20.00,  350.00,  2400.00,  480.00,  2880.00),
(35, 7, 'Toner HP LaserJet 85A',        2,  320.00,  384.00, 'PCS', 20.00,  110.00,   640.00,  128.00,   768.00),
(35, 8, 'Ramette Papier A4 80g',       15,   45.00,   54.00, 'RAM', 20.00,   17.00,   675.00,  135.00,   810.00),
(36,13, 'Climatiseur Gree 18000 BTU',   2, 4500.00, 5400.00, 'PCS', 20.00, 1300.00,  9000.00, 1800.00, 10800.00),
(37,17, 'Téléphone IP Yealink T31P',    2,  780.00,  936.00, 'PCS', 20.00,  230.00,  1560.00,  312.00,  1872.00),
(38,15, 'Caméra IP Hikvision 4MP',      4, 1100.00, 1320.00, 'PCS', 20.00,  320.00,  4400.00,  880.00,  5280.00),
(38,16, 'Alarme Intrusion GSM',         1,  850.00, 1020.00, 'KIT', 20.00,  250.00,   850.00,  170.00,  1020.00),
(39,11, 'Microsoft Office 365',         2, 1800.00, 2160.00, 'LIC', 20.00,  400.00,  3600.00,  720.00,  4320.00),
(40,20, 'Photocopieur Ricoh A3',        1,18500.00,22200.00, 'PCS', 20.00, 4500.00, 18500.00, 3700.00, 22200.00);

-- AVOIRS details (doc 41..50)
INSERT IGNORE INTO details_documents (id_document, id_article, description, quantite, prix_unitaire_ht, prix_unitaire_ttc, unite_vente, taux_tva, marge_beneficiaire, total_ligne_ht, total_ligne_tva, total_ligne_ttc) VALUES
(41, 1, 'Retour Ordinateur Portable HP 15',  0.100, 5500.00, 6600.00, 'PCS', 20.00, 0.00,   550.00,  110.00,   660.00),
(42, 3, 'Remise bureau directeur',            0.100, 2200.00, 2640.00, 'PCS', 20.00, 0.00,   220.00,   44.00,   264.00),
(42, 4, 'Remise chaise ergonomique',          0.100,  980.00, 1176.00, 'PCS', 20.00, 0.00,    98.00,   19.60,   117.60),
(43, 9, 'Retour armoire endommagée',          0.100, 1450.00, 1740.00, 'PCS', 20.00, 0.00,   145.00,   29.00,   174.00),
(43,10, 'Retour table réunion',               0.100, 3200.00, 3840.00, 'PCS', 20.00, 0.00,   320.00,   64.00,   384.00),
(44, 5, 'Avoir erreur facturation switch',    0.100, 1850.00, 2220.00, 'PCS', 20.00, 0.00,   185.00,   37.00,   222.00),
(44, 6, 'Avoir erreur facturation routeur',   0.100, 1200.00, 1440.00, 'PCS', 20.00, 0.00,   120.00,   24.00,   144.00),
(45, 7, 'Retour toner non conforme',          0.100,  320.00,  384.00, 'PCS', 20.00, 0.00,    32.00,    6.40,    38.40),
(45, 8, 'Retour ramettes endommagées',        0.100,   45.00,   54.00, 'RAM', 20.00, 0.00,     4.50,    0.90,     5.40),
(46,13, 'Retour climatiseur en panne',        0.100, 4500.00, 5400.00, 'PCS', 20.00, 0.00,   450.00,   90.00,   540.00),
(47,17, 'Retour téléphone défectueux',        0.100,  780.00,  936.00, 'PCS', 20.00, 0.00,    78.00,   15.60,    93.60),
(48,15, 'Retour caméra défectueuse',          0.100, 1100.00, 1320.00, 'PCS', 20.00, 0.00,   110.00,   22.00,   132.00),
(48,16, 'Retour alarme non conforme',         0.100,  850.00, 1020.00, 'KIT', 20.00, 0.00,    85.00,   17.00,   102.00),
(49,11, 'Avoir licence annulée',              0.100, 1800.00, 2160.00, 'LIC', 20.00, 0.00,   180.00,   36.00,   216.00),
(50,20, 'Remise photocopieur',                0.100,18500.00,22200.00, 'PCS', 20.00, 0.00,  1850.00,  370.00,  2220.00);

-- =========================
-- paiements (for paid/partial FA)
-- =========================
INSERT IGNORE INTO paiements (id_document, date_paiement, id_mode_paiement, montant, reference, banque, statut, commentaire) VALUES
-- FA-2026-001 (doc 31) — fully paid
(31, '2026-01-28', 1,  6600.00, NULL,         NULL,             'ENCAISSE', 'Paiement espèces FA-001'),
-- FA-2026-002 (doc 32) — fully paid
(32, '2026-02-01', 2,  4560.00, 'CHQ-001245', 'Banque Populaire','ENCAISSE','Chèque FA-002'),
-- FA-2026-003 (doc 33) — partial 50%
(33, '2026-02-05', 3,  2640.00, 'VIR-2026-01','Attijariwafa',   'ENCAISSE', 'Virement partiel FA-003'),
-- FA-2026-004 (doc 34) — fully paid
(34, '2026-02-08', 1, 11520.00, NULL,         NULL,             'ENCAISSE', 'Paiement espèces FA-004'),
-- FA-2026-006 (doc 36) — partial 50%
(36, '2026-02-15', 4,  5400.00, 'EFF-2026-03','BMCE',           'EN_ATTENTE','Effet 90 jours FA-006'),
-- FA-2026-007 (doc 37) — fully paid
(37, '2026-02-20', 2,  1872.00, 'CHQ-002100', 'CIH Bank',       'ENCAISSE', 'Chèque FA-007'),
-- FA-2026-010 (doc 40) — partial 50%
(40, '2026-03-05', 3, 11100.00, 'VIR-2026-10','Attijariwafa',   'ENCAISSE', 'Virement partiel FA-010');

-- =========================
-- mouvements_stock
-- Entries for BL (sortie) and initial stock (entree)
-- =========================
INSERT IGNORE INTO mouvements_stock (id_article, date_mouvement, type_mouvement, quantite, id_document, commentaire) VALUES
-- Initial stock entries
(1,  '2025-12-01 08:00:00', 'ENTREE',  20.000, NULL, 'Stock initial ordinateurs HP'),
(2,  '2025-12-01 08:00:00', 'ENTREE',  15.000, NULL, 'Stock initial PC bureau Dell'),
(3,  '2025-12-01 08:00:00', 'ENTREE',  10.000, NULL, 'Stock initial bureaux'),
(4,  '2025-12-01 08:00:00', 'ENTREE',  25.000, NULL, 'Stock initial chaises'),
(5,  '2025-12-01 08:00:00', 'ENTREE',   8.000, NULL, 'Stock initial switchs'),
(6,  '2025-12-01 08:00:00', 'ENTREE',  12.000, NULL, 'Stock initial routeurs'),
(7,  '2025-12-01 08:00:00', 'ENTREE',  50.000, NULL, 'Stock initial toners'),
(8,  '2025-12-01 08:00:00', 'ENTREE', 200.000, NULL, 'Stock initial ramettes papier'),
(9,  '2025-12-01 08:00:00', 'ENTREE',   6.000, NULL, 'Stock initial armoires'),
(10, '2025-12-01 08:00:00', 'ENTREE',   4.000, NULL, 'Stock initial tables réunion'),
(13, '2025-12-01 08:00:00', 'ENTREE',  10.000, NULL, 'Stock initial climatiseurs'),
(15, '2025-12-01 08:00:00', 'ENTREE',  30.000, NULL, 'Stock initial caméras'),
(16, '2025-12-01 08:00:00', 'ENTREE',  12.000, NULL, 'Stock initial kits alarme'),
(17, '2025-12-01 08:00:00', 'ENTREE',  20.000, NULL, 'Stock initial téléphones IP'),
(19, '2025-12-01 08:00:00', 'ENTREE',   5.000, NULL, 'Stock initial imprimantes'),
(20, '2025-12-01 08:00:00', 'ENTREE',   3.000, NULL, 'Stock initial photocopieurs'),
-- Sorties from BL documents
(1,  '2026-01-20 10:00:00', 'SORTIE',   1.000, 21, 'Livraison BL-2026-001'),
(3,  '2026-01-25 10:00:00', 'SORTIE',   1.000, 22, 'Livraison BL-2026-002 bureau'),
(4,  '2026-01-25 10:30:00', 'SORTIE',   2.000, 22, 'Livraison BL-2026-002 chaises'),
(9,  '2026-01-28 09:00:00', 'SORTIE',   2.000, 23, 'Livraison BL-2026-003 armoires'),
(10, '2026-01-28 09:30:00', 'SORTIE',   1.000, 23, 'Livraison BL-2026-003 table'),
(5,  '2026-02-01 10:00:00', 'SORTIE',   2.000, 24, 'Livraison BL-2026-004 switchs'),
(6,  '2026-02-01 10:30:00', 'SORTIE',   2.000, 24, 'Livraison BL-2026-004 routeurs'),
(7,  '2026-02-05 10:00:00', 'SORTIE',   2.000, 25, 'Livraison BL-2026-005 toners'),
(8,  '2026-02-05 10:30:00', 'SORTIE',  15.000, 25, 'Livraison BL-2026-005 papier'),
(13, '2026-02-10 10:00:00', 'SORTIE',   2.000, 26, 'Livraison BL-2026-006 climatiseurs'),
(17, '2026-02-15 10:00:00', 'SORTIE',   2.000, 27, 'Livraison BL-2026-007 téléphones'),
(15, '2026-02-20 10:00:00', 'SORTIE',   4.000, 28, 'Livraison BL-2026-008 caméras'),
(16, '2026-02-20 10:30:00', 'SORTIE',   1.000, 28, 'Livraison BL-2026-008 alarme'),
(20, '2026-03-01 10:00:00', 'SORTIE',   1.000, 30, 'Livraison BL-2026-010 photocopieur'),
-- Retours from AV documents
(1,  '2026-01-28 14:00:00', 'ENTREE',   0.100, 41, 'Retour avoir AV-2026-001'),
(13, '2026-02-12 14:00:00', 'ENTREE',   0.100, 46, 'Retour avoir AV-2026-006 climatiseur'),
(15, '2026-02-22 14:00:00', 'ENTREE',   0.100, 48, 'Retour avoir AV-2026-008 caméra'),
-- Adjustments
(8,  '2026-01-15 08:00:00', 'AJUSTEMENT', 10.000, NULL, 'Réapprovisionnement papier'),
(7,  '2026-01-15 08:30:00', 'AJUSTEMENT', 20.000, NULL, 'Réapprovisionnement toners');

-- =========================
-- audit_log (50 events)
-- =========================
INSERT IGNORE INTO audit_log (date_action, id_utilisateur, table_name, record_id, action, new_values_json, commentaire, ip_client) VALUES
('2025-12-01 08:00:00', 4, 'utilisateurs',      '4',  'INSERT', '{"nom":"admin","role":"admin"}',                          'Création compte admin',                  '192.168.1.1'),
('2025-12-01 08:05:00', 4, 'informations_societe','1', 'INSERT', '{"nom":"TechMaroc SARL"}',                                'Création fiche société',                 '192.168.1.1'),
('2025-12-01 08:10:00', 4, 'familles',           '1',  'INSERT', '{"nom":"Informatique"}',                                  'Création famille Informatique',          '192.168.1.1'),
('2025-12-01 08:15:00', 4, 'familles',           '2',  'INSERT', '{"nom":"Bureautique"}',                                   'Création famille Bureautique',           '192.168.1.1'),
('2025-12-01 08:20:00', 4, 'familles',           '3',  'INSERT', '{"nom":"Réseau"}',                                        'Création famille Réseau',                '192.168.1.1'),
('2025-12-01 09:00:00', 4, 'articles',           '1',  'INSERT', '{"nom":"Ordinateur Portable HP 15","prix":5500}',         'Création article PC portable',           '192.168.1.1'),
('2025-12-01 09:05:00', 4, 'articles',           '2',  'INSERT', '{"nom":"PC Bureau Dell OptiPlex","prix":4800}',           'Création article PC bureau',             '192.168.1.1'),
('2025-12-01 09:10:00', 4, 'articles',           '5',  'INSERT', '{"nom":"Switch 24 ports TP-Link","prix":1850}',           'Création article switch réseau',         '192.168.1.1'),
('2025-12-01 09:15:00', 4, 'articles',          '19',  'INSERT', '{"nom":"Imprimante Multifonction HP","prix":3200}',       'Création article imprimante',            '192.168.1.1'),
('2025-12-01 09:30:00', 4, 'mouvements_stock',   '1',  'INSERT', '{"type":"ENTREE","qte":20,"article_id":1}',               'Stock initial PC portable',              '192.168.1.1'),
('2025-12-01 09:35:00', 4, 'mouvements_stock',   '7',  'INSERT', '{"type":"ENTREE","qte":50,"article_id":7}',               'Stock initial toners',                   '192.168.1.1'),
('2025-12-01 10:00:00', 4, 'tiers',              '1',  'INSERT', '{"nom":"Société Atlas","type":"CLIENT"}',                 'Création client Société Atlas',          '192.168.1.1'),
('2025-12-01 10:05:00', 4, 'tiers',              '2',  'INSERT', '{"nom":"Maroc Distribution","type":"CLIENT"}',            'Création client Maroc Distribution',     '192.168.1.1'),
('2025-12-01 10:10:00', 4, 'tiers',             '11',  'INSERT', '{"nom":"Atlas Fournitures","type":"FOURNISSEUR"}',        'Création fournisseur Atlas Fournitures', '192.168.1.1'),
('2025-12-02 08:00:00', 5, 'utilisateurs',       '5',  'INSERT', '{"nom":"admin2","role":"admin"}',                         'Création compte admin2',                 '192.168.1.2'),
('2026-01-05 09:00:00', 4, 'documents',          '1',  'INSERT', '{"numero":"DV-2026-001","type":"DV","total":6600}',       'Création devis DV-2026-001',             '192.168.1.1'),
('2026-01-06 09:00:00', 4, 'documents',         '11',  'INSERT', '{"numero":"BC-2026-001","type":"BC","total":6600}',       'Création bon de commande BC-2026-001',   '192.168.1.1'),
('2026-01-08 09:30:00', 6, 'documents',          '2',  'INSERT', '{"numero":"DV-2026-002","type":"DV","total":4560}',       'Création devis DV-2026-002',             '192.168.1.3'),
('2026-01-09 10:00:00', 6, 'documents',         '12',  'INSERT', '{"numero":"BC-2026-002","type":"BC","total":4560}',       'Création BC-2026-002',                   '192.168.1.3'),
('2026-01-13 11:00:00', 7, 'documents',         '13',  'INSERT', '{"numero":"BC-2026-003","type":"BC","total":5280}',       'Création BC-2026-003',                   '192.168.1.4'),
('2026-01-20 10:00:00', 4, 'documents',         '21',  'INSERT', '{"numero":"BL-2026-001","type":"BL","total":6600}',       'Création BL-2026-001',                   '192.168.1.1'),
('2026-01-20 10:05:00', 4, 'mouvements_stock',  '17',  'INSERT', '{"type":"SORTIE","qte":1,"article_id":1,"doc":"BL-001"}', 'Sortie stock BL-2026-001',               '192.168.1.1'),
('2026-01-21 08:00:00', 4, 'documents',         '31',  'INSERT', '{"numero":"FA-2026-001","type":"FA","total":6600}',       'Création facture FA-2026-001',           '192.168.1.1'),
('2026-01-28 09:00:00', 4, 'paiements',          '1',  'INSERT', '{"montant":6600,"mode":"ESPECES","doc":"FA-001"}',        'Paiement reçu FA-2026-001',              '192.168.1.1'),
('2026-01-28 09:05:00', 4, 'documents',         '31',  'STATUS_CHANGE', '{"old":"VALIDE","new":"PAYE"}',                    'Facture FA-001 marquée payée',           '192.168.1.1'),
('2026-01-28 14:00:00', 4, 'documents',         '41',  'INSERT', '{"numero":"AV-2026-001","type":"AV","total":660}',        'Création avoir AV-2026-001',             '192.168.1.1'),
('2026-01-28 14:05:00', 4, 'mouvements_stock',  '33',  'INSERT', '{"type":"ENTREE","qte":0.1,"article_id":1,"doc":"AV-001"}','Retour stock AV-2026-001',             '192.168.1.1'),
('2026-01-29 09:00:00', 7, 'documents',         '33',  'INSERT', '{"numero":"FA-2026-003","type":"FA","total":5280}',       'Création facture FA-2026-003',           '192.168.1.4'),
('2026-02-01 10:00:00', 6, 'documents',         '24',  'INSERT', '{"numero":"BL-2026-004","type":"BL","total":11520}',      'Création BL réseau',                     '192.168.1.3'),
('2026-02-01 10:10:00', 6, 'mouvements_stock',  '22',  'INSERT', '{"type":"SORTIE","qte":2,"article_id":5}',               'Sortie switchs BL-004',                  '192.168.1.3'),
('2026-02-02 08:00:00', 6, 'documents',         '34',  'INSERT', '{"numero":"FA-2026-004","type":"FA","total":11520}',      'Création facture FA-2026-004',           '192.168.1.3'),
('2026-02-05 09:00:00', 4, 'paiements',          '3',  'INSERT', '{"montant":2640,"mode":"VIREMENT","doc":"FA-003"}',       'Paiement partiel FA-2026-003',           '192.168.1.1'),
('2026-02-05 09:05:00', 4, 'documents',         '33',  'STATUS_CHANGE', '{"old":"VALIDE","new":"PARTIEL"}',                 'Facture FA-003 partiel',                 '192.168.1.1'),
('2026-02-06 09:00:00', 8, 'documents',         '35',  'INSERT', '{"numero":"FA-2026-005","type":"FA","total":1560}',       'Création facture FA-2026-005',           '192.168.1.5'),
('2026-02-08 10:00:00', 4, 'paiements',          '4',  'INSERT', '{"montant":11520,"mode":"ESPECES","doc":"FA-004"}',       'Paiement reçu FA-2026-004',              '192.168.1.1'),
('2026-02-10 11:00:00', 4, 'documents',         '26',  'INSERT', '{"numero":"BL-2026-006","type":"BL","total":10800}',      'Création BL climatiseurs',               '192.168.1.1'),
('2026-02-10 11:05:00', 4, 'mouvements_stock',  '30',  'INSERT', '{"type":"SORTIE","qte":2,"article_id":13}',              'Sortie climatiseurs BL-006',             '192.168.1.1'),
('2026-02-11 09:00:00', 4, 'documents',         '36',  'INSERT', '{"numero":"FA-2026-006","type":"FA","total":10800}',      'Création facture FA-2026-006',           '192.168.1.1'),
('2026-02-12 14:00:00', 4, 'documents',         '46',  'INSERT', '{"numero":"AV-2026-006","type":"AV","total":1080}',       'Avoir retour climatiseur',               '192.168.1.1'),
('2026-02-15 09:00:00', 4, 'paiements',          '5',  'INSERT', '{"montant":5400,"mode":"EFFET","doc":"FA-006"}',          'Effet 90j FA-2026-006',                  '192.168.1.1'),
('2026-02-15 10:00:00', 7, 'documents',         '27',  'INSERT', '{"numero":"BL-2026-007","type":"BL","total":1872}',       'Livraison téléphones',                   '192.168.1.4'),
('2026-02-16 09:00:00', 7, 'documents',         '37',  'INSERT', '{"numero":"FA-2026-007","type":"FA","total":1872}',       'Facture téléphonie',                     '192.168.1.4'),
('2026-02-17 10:00:00', 7, 'documents',         '47',  'INSERT', '{"numero":"AV-2026-007","type":"AV","total":187.20}',     'Avoir retour téléphone',                 '192.168.1.4'),
('2026-02-20 09:00:00', 7, 'paiements',          '6',  'INSERT', '{"montant":1872,"mode":"CHEQUE","doc":"FA-007"}',         'Paiement FA-007 par chèque',             '192.168.1.4'),
('2026-02-20 09:05:00', 7, 'documents',         '37',  'STATUS_CHANGE', '{"old":"VALIDE","new":"PAYE"}',                    'Facture FA-007 payée',                   '192.168.1.4'),
('2026-02-21 09:00:00', 6, 'documents',         '38',  'INSERT', '{"numero":"FA-2026-008","type":"FA","total":7680}',       'Facture sécurité',                       '192.168.1.3'),
('2026-02-22 10:00:00', 6, 'documents',         '48',  'INSERT', '{"numero":"AV-2026-008","type":"AV","total":768}',        'Avoir caméra défectueuse',               '192.168.1.3'),
('2026-02-25 08:00:00', 8, 'mouvements_stock',  '37',  'AJUSTEMENT', '{"type":"AJUSTEMENT","qte":10,"article_id":8}',      'Réajustement stock papier',              '192.168.1.5'),
('2026-02-26 09:00:00', 5, 'documents',         '39',  'INSERT', '{"numero":"FA-2026-009","type":"FA","total":4320}',       'Facture logiciels',                      '192.168.1.2'),
('2026-03-01 10:00:00', 4, 'documents',         '30',  'INSERT', '{"numero":"BL-2026-010","type":"BL","total":22200}',      'Livraison photocopieur',                 '192.168.1.1'),
('2026-03-02 09:00:00', 4, 'documents',         '40',  'INSERT', '{"numero":"FA-2026-010","type":"FA","total":22200}',      'Facture photocopieur A3',                '192.168.1.1'),
('2026-03-03 10:00:00', 4, 'documents',         '50',  'INSERT', '{"numero":"AV-2026-010","type":"AV","total":2220}',       'Avoir remise photocopieur',              '192.168.1.1'),
('2026-03-05 09:00:00', 4, 'paiements',          '7',  'INSERT', '{"montant":11100,"mode":"VIREMENT","doc":"FA-010"}',      'Paiement partiel FA-2026-010',           '192.168.1.1');

-- =========================
-- Update counters to reflect inserted documents
-- counters table (not document_counters)
-- =========================
UPDATE counters SET valeur_courante = 10 WHERE categorie = 'DOCUMENT' AND code = 'DV' AND annee = 2026;
UPDATE counters SET valeur_courante = 10 WHERE categorie = 'DOCUMENT' AND code = 'BC' AND annee = 2026;
UPDATE counters SET valeur_courante = 10 WHERE categorie = 'DOCUMENT' AND code = 'BL' AND annee = 2026;
UPDATE counters SET valeur_courante = 10 WHERE categorie = 'DOCUMENT' AND code = 'FA' AND annee = 2026;
UPDATE counters SET valeur_courante = 10 WHERE categorie = 'DOCUMENT' AND code = 'AV' AND annee = 2026;
-- tiers counters (10 clients + 10 fournisseurs already in base + extras)
UPDATE counters SET valeur_courante = 16 WHERE categorie = 'TIERS' AND code = 'CL' AND annee = 2026;
UPDATE counters SET valeur_courante = 10 WHERE categorie = 'TIERS' AND code = 'FR' AND annee = 2026;

SET FOREIGN_KEY_CHECKS = 1;