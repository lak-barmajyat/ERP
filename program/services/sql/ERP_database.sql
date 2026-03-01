/* ==========================================================
   FICHIER SQL COMPLET (MySQL 8+)
   - Supprime la base si elle existe
   - Recrée la base
   - Crée toutes les tables + clés
   - Ajoute référentiels (domaines, types docs, statuts, modes paiement, types tiers)
   - Ajoute audit_log
   ========================================================== */

DROP DATABASE IF EXISTS erp;
CREATE DATABASE IF NOT EXISTS erp
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_general_ci;

USE erp;

SET FOREIGN_KEY_CHECKS = 0;

-- =========================
-- TABLE: informations_societe
-- =========================
DROP TABLE IF EXISTS informations_societe;
CREATE TABLE IF NOT EXISTS informations_societe (
  id_societe            INT AUTO_INCREMENT PRIMARY KEY,
  nom_societe           VARCHAR(150) NOT NULL,
  activite              VARCHAR(150) NULL,
  forme_juridique       VARCHAR(80)  NULL,
  patente               VARCHAR(50)  NULL,
  cnss                  VARCHAR(50)  NULL,
  telephone_fix         VARCHAR(30)  NULL,
  fax                   VARCHAR(30)  NULL,
  site_web              VARCHAR(150) NULL,
  ice                   VARCHAR(30)  NULL,
  if_fiscal             VARCHAR(30)  NULL,
  rc                    VARCHAR(30)  NULL,
  email                 VARCHAR(120) NULL,
  logo_path             VARCHAR(255) NULL,
  adresse               VARCHAR(255) NULL,
  created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =========================
-- TABLE: utilisateurs
-- =========================
DROP TABLE IF EXISTS utilisateurs;
CREATE TABLE IF NOT EXISTS utilisateurs (
  id_utilisateur        INT AUTO_INCREMENT PRIMARY KEY,
  nom_utilisateur       VARCHAR(80) NOT NULL UNIQUE,
  mot_de_passe_hash     VARCHAR(255) NOT NULL,
  role                  VARCHAR(50) NOT NULL DEFAULT 'VENDEUR',
  permissions_json      JSON NULL,
  actif                 TINYINT(1) NOT NULL DEFAULT 1,
  created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =========================
-- REFERENTIELS
-- =========================

-- A) ref_domaines (EDITED: ordre 0/1/2)
DROP TABLE IF EXISTS ref_domaines;
CREATE TABLE IF NOT EXISTS ref_domaines (
  id_domaine       INT AUTO_INCREMENT PRIMARY KEY,
  code_domaine     VARCHAR(20) NOT NULL UNIQUE,     -- VENTE / ACHAT / STOCK
  libelle_domaine  VARCHAR(60) NOT NULL,            -- "Vente", "Achat", "Stock"
  actif            TINYINT(1) NOT NULL DEFAULT 1,
  ordre            INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

INSERT INTO ref_domaines (code_domaine, libelle_domaine, ordre) VALUES
('VENTE','Vente',0), ('ACHAT','Achat',1), ('STOCK','Stock',2);

-- B) ref_statuts_documents
DROP TABLE IF EXISTS ref_statuts_documents;
CREATE TABLE IF NOT EXISTS ref_statuts_documents (
  id_statut        INT AUTO_INCREMENT PRIMARY KEY,
  code_statut      VARCHAR(30) NOT NULL UNIQUE,     -- BROUILLON / VALIDE / ANNULE / PARTIEL / PAYE
  libelle_statut   VARCHAR(60) NOT NULL,
  couleur          VARCHAR(15) NULL,
  actif            TINYINT(1) NOT NULL DEFAULT 1,
  ordre            INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

INSERT INTO ref_statuts_documents (code_statut, libelle_statut, ordre) VALUES
('BROUILLON','Brouillon',1),
('VALIDE','Validé',2),
('ANNULE','Annulé',9),
('PARTIEL','Partiellement payé',5),
('PAYE','Payé',6);

-- C) ref_modes_paiement
DROP TABLE IF EXISTS ref_modes_paiement;
CREATE TABLE IF NOT EXISTS ref_modes_paiement (
  id_mode_paiement    INT AUTO_INCREMENT PRIMARY KEY,
  code_mode           VARCHAR(20) NOT NULL UNIQUE,  -- ESPECES / CHEQUE / VIREMENT / EFFET
  libelle_mode        VARCHAR(60) NOT NULL,
  besoin_reference    TINYINT(1) NOT NULL DEFAULT 0,
  besoin_echeance     TINYINT(1) NOT NULL DEFAULT 0,
  actif               TINYINT(1) NOT NULL DEFAULT 1,
  ordre               INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

INSERT IGNORE INTO ref_modes_paiement (code_mode, libelle_mode, besoin_reference, besoin_echeance, ordre) VALUES
('ESPECES','Espèces',0,0,1),
('CHEQUE','Chèque',1,1,2),
('VIREMENT','Virement',1,0,3),
('EFFET','Effet / Traite',1,1,4);

-- D) ref_types_tiers
DROP TABLE IF EXISTS ref_types_tiers;
CREATE TABLE IF NOT EXISTS ref_types_tiers (
  id_type_tiers     INT AUTO_INCREMENT PRIMARY KEY,
  code_type_tiers   VARCHAR(30) NOT NULL UNIQUE,    -- SOCIETE / PARTICULIER / ADMIN
  libelle_type      VARCHAR(60) NOT NULL,
  actif             TINYINT(1) NOT NULL DEFAULT 1,
  ordre             INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

INSERT IGNORE INTO ref_types_tiers (code_type_tiers, libelle_type, ordre) VALUES
('SOCIETE','Société',1),
('PARTICULIER','Particulier',2),
('ADMIN','Administration',3),
('CLIENT','Client',4),
('FOURNISSEUR','Fournisseur',5);

-- =========================
-- TABLE: familles
-- =========================
DROP TABLE IF EXISTS familles;
CREATE TABLE IF NOT EXISTS familles (
  id_famille            INT AUTO_INCREMENT PRIMARY KEY,
  nom_famille           VARCHAR(120) NOT NULL,
  description           VARCHAR(255) NULL,
  taux_tva              DECIMAL(5,2) NULL,
  suivi_stock           TINYINT(1) NOT NULL DEFAULT 1,
  unite_defaut          VARCHAR(20) NULL,
  created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_familles_nom (nom_famille)
) ENGINE=InnoDB;

-- =========================
-- TABLE: articles
-- =========================
DROP TABLE IF EXISTS articles;
CREATE TABLE IF NOT EXISTS articles (
  id_article            INT AUTO_INCREMENT PRIMARY KEY,
  nom_article           VARCHAR(160) NOT NULL,
  description           VARCHAR(255) NULL,
  prix_vente_ht         DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  prix_achat_ht         DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  id_famille            INT NULL,
  taux_tva              DECIMAL(5,2) NULL,
  suivi_stock           TINYINT(1) NOT NULL DEFAULT 1,
  unite                 VARCHAR(20) NULL,
  reference_interne     VARCHAR(60) NULL,
  code_barres           VARCHAR(60) NULL,
  actif                 TINYINT(1) NOT NULL DEFAULT 1,
  created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_articles_familles
    FOREIGN KEY (id_famille) REFERENCES familles(id_famille)
    ON UPDATE CASCADE ON DELETE SET NULL,
  INDEX idx_articles_nom (nom_article),
  INDEX idx_articles_famille (id_famille)
) ENGINE=InnoDB;

-- =========================
-- TABLE: tiers (clients + fournisseurs)
-- =========================
DROP TABLE IF EXISTS tiers;
CREATE TABLE IF NOT EXISTS tiers (
  id_tiers              INT AUTO_INCREMENT PRIMARY KEY,

  -- Business identification
  code_tiers             VARCHAR(20) NULL,

  -- Tier category (keeps your current logic)
  type_tiers            ENUM('CLIENT','FOURNISSEUR', 'ADMIN', 'PARTICULIER', 'SOCIETE') NOT NULL,

  -- Identity
  nom_tiers             VARCHAR(160) NOT NULL,
  adresse               VARCHAR(255) NULL,
  ice                   VARCHAR(30) NULL,
  telephone             VARCHAR(30) NULL,
  email                 VARCHAR(120) NULL,
  plafond_credit        DECIMAL(12,2) NULL,

  -- Status & timestamps
  actif                 TINYINT(1) NOT NULL DEFAULT 1,
  created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  -- Indexes
  UNIQUE KEY uq_tiers_code (code_tiers),
  INDEX idx_tiers_type (type_tiers),
  INDEX idx_tiers_nom (nom_tiers)

) ENGINE=InnoDB;

-- =========================
-- TABLE: ref_types_documents (depends on ref_domaines)
-- =========================
DROP TABLE IF EXISTS ref_types_documents;
CREATE TABLE IF NOT EXISTS ref_types_documents (
  id_type_document   INT AUTO_INCREMENT PRIMARY KEY,
  code_type          VARCHAR(10) NOT NULL UNIQUE,   -- DV, BC, BL, FA, AV...
  libelle_type       VARCHAR(80) NOT NULL,
  id_domaine         INT NOT NULL,
  impact_stock       TINYINT(1) NOT NULL DEFAULT 0,
  signe_quantite     SMALLINT NOT NULL DEFAULT 0,   -- +1 entree, -1 sortie, 0 none
  actif              TINYINT(1) NOT NULL DEFAULT 1,
  ordre              INT NOT NULL DEFAULT 0,

  CONSTRAINT fk_types_docs_domaines
    FOREIGN KEY (id_domaine) REFERENCES ref_domaines(id_domaine)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  INDEX idx_types_docs_domaine (id_domaine)
) ENGINE=InnoDB;

-- Exemples vente
INSERT INTO ref_types_documents (code_type, libelle_type, id_domaine, impact_stock, signe_quantite, ordre)
SELECT 'DV','Devis', d.id_domaine, 0, 0, 1 FROM ref_domaines d WHERE d.code_domaine='VENTE'
UNION ALL
SELECT 'BC','Bon de commande', d.id_domaine, 0, 0, 2 FROM ref_domaines d WHERE d.code_domaine='VENTE'
UNION ALL
SELECT 'BL','Bon de livraison', d.id_domaine, 1,-1, 3 FROM ref_domaines d WHERE d.code_domaine='VENTE'
UNION ALL
SELECT 'FA','Facture', d.id_domaine, 1,-1, 4 FROM ref_domaines d WHERE d.code_domaine='VENTE'
UNION ALL
SELECT 'AV','Avoir', d.id_domaine, 1,+1, 5 FROM ref_domaines d WHERE d.code_domaine='VENTE';

CREATE TABLE IF NOT EXISTS counters (
  id_counter        BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

  -- Generalization
  categorie         ENUM('DOCUMENT','TIERS', 'ARTICLE') NOT NULL,
  code              VARCHAR(10) NOT NULL,           -- DV/FA/... or CL/FR

  annee             INT NOT NULL,
  valeur_courante   INT NOT NULL DEFAULT 0,
  longueur          INT NOT NULL DEFAULT 3,
  prefixe           VARCHAR(10) NOT NULL,
  suffixe           VARCHAR(20) NULL,
  reset_annuel      TINYINT(1) NOT NULL DEFAULT 0,
  created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  PRIMARY KEY (id_counter),
  UNIQUE KEY uq_counter_cat_code_year (categorie, code, annee),
  KEY idx_counter_cat (categorie),
  KEY idx_counter_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT IGNORE INTO counters
(categorie, code, annee, valeur_courante, longueur, prefixe, suffixe, reset_annuel)
VALUES
('DOCUMENT', 'DV', YEAR(CURDATE()), 0, 3, 'DV', NULL, 1),
('DOCUMENT', 'BC', YEAR(CURDATE()), 0, 3, 'BC', NULL, 1),
('DOCUMENT', 'BL', YEAR(CURDATE()), 0, 3, 'BL', NULL, 1),
('DOCUMENT', 'FA', YEAR(CURDATE()), 0, 3, 'FA', NULL, 1),
('DOCUMENT', 'AV', YEAR(CURDATE()), 0, 3, 'AV', NULL, 1);

INSERT IGNORE INTO counters
(categorie, code, annee, valeur_courante, longueur, prefixe, suffixe, reset_annuel)
VALUES
('TIERS', 'CL', YEAR(CURDATE()), 0, 3, 'CL', NULL, 1),
('TIERS', 'FR', YEAR(CURDATE()), 0, 3, 'FR', NULL, 1),
('TIERS', 'AD', YEAR(CURDATE()), 0, 3, 'AD', NULL, 1),
('TIERS', 'PR', YEAR(CURDATE()), 0, 3, 'PR', NULL, 1),
('TIERS', 'SC', YEAR(CURDATE()), 0, 3, 'SC', NULL, 1);

-- =========================
-- TABLE: documents
-- =========================
DROP TABLE IF EXISTS documents;
CREATE TABLE IF NOT EXISTS documents (
  id_document           BIGINT AUTO_INCREMENT PRIMARY KEY,

  id_domaine            INT NOT NULL,                 -- ref_domaines
  id_type_document      INT NOT NULL,                 -- ref_types_documents
  numero_document       VARCHAR(30) NOT NULL,

  id_tiers              INT NULL,                     -- client/fournisseur
  date_document         DATE NOT NULL,
  date_livraison        DATE NULL,

  mode_prix             ENUM('HT','TTC') NOT NULL DEFAULT 'HT',

  total_ht              DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  total_tva             DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  total_ttc             DECIMAL(14,2) NOT NULL DEFAULT 0.00,

  solde                 DECIMAL(14,2) NOT NULL DEFAULT 0.00,

  id_vendeur            INT NOT NULL,
  id_statut             INT NOT NULL,                 -- ref_statuts_documents

  commentaire           VARCHAR(255) NULL,
  created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_documents_domaines
    FOREIGN KEY (id_domaine) REFERENCES ref_domaines(id_domaine)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  CONSTRAINT fk_documents_type
    FOREIGN KEY (id_type_document) REFERENCES ref_types_documents(id_type_document)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  CONSTRAINT fk_documents_tiers
    FOREIGN KEY (id_tiers) REFERENCES tiers(id_tiers)
    ON UPDATE CASCADE ON DELETE SET NULL,

  CONSTRAINT fk_documents_utilisateurs
    FOREIGN KEY (id_vendeur) REFERENCES utilisateurs(id_utilisateur)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  CONSTRAINT fk_documents_statut
    FOREIGN KEY (id_statut) REFERENCES ref_statuts_documents(id_statut)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  UNIQUE KEY uq_documents_numero (id_domaine, id_type_document, numero_document),
  INDEX idx_documents_date (date_document),
  INDEX idx_documents_tiers (id_tiers)
) ENGINE=InnoDB;

-- =========================
-- TABLE: details_documents
-- =========================
DROP TABLE IF EXISTS details_documents;
CREATE TABLE IF NOT EXISTS details_documents (
  id_detail             BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_document           BIGINT NOT NULL,

  id_article            INT NOT NULL,
  description           VARCHAR(255) NULL,

  quantite              DECIMAL(14,3) NOT NULL DEFAULT 1.000,

  prix_unitaire_ht      DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  prix_unitaire_ttc     DECIMAL(14,2) NOT NULL DEFAULT 0.00,

  unite_vente           VARCHAR(20) NULL,
  taux_tva              DECIMAL(5,2) NULL,

  marge_beneficiaire    DECIMAL(14,2) NULL,

  total_ligne_ht        DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  total_ligne_tva       DECIMAL(14,2) NOT NULL DEFAULT 0.00,
  total_ligne_ttc       DECIMAL(14,2) NOT NULL DEFAULT 0.00,

  created_at            DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_details_documents_document
    FOREIGN KEY (id_document) REFERENCES documents(id_document)
    ON UPDATE CASCADE ON DELETE CASCADE,

  CONSTRAINT fk_details_documents_article
    FOREIGN KEY (id_article) REFERENCES articles(id_article)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  INDEX idx_details_doc (id_document),
  INDEX idx_details_article (id_article)
) ENGINE=InnoDB;

-- =========================
-- TABLE: paiements
-- =========================
DROP TABLE IF EXISTS paiements;
CREATE TABLE IF NOT EXISTS paiements (
  id_paiement          BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_document          BIGINT NOT NULL,
  date_paiement        DATE NOT NULL,

  id_mode_paiement     INT NOT NULL,     -- ref_modes_paiement
  montant              DECIMAL(14,2) NOT NULL DEFAULT 0.00,

  reference            VARCHAR(60) NULL,
  date_echeance        DATE NULL,
  banque               VARCHAR(80) NULL,

  statut               ENUM('ENCAISSE','EN_ATTENTE','REJETE') NOT NULL DEFAULT 'ENCAISSE',
  commentaire          VARCHAR(255) NULL,
  created_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_paiements_document
    FOREIGN KEY (id_document) REFERENCES documents(id_document)
    ON UPDATE CASCADE ON DELETE CASCADE,

  CONSTRAINT fk_paiements_mode
    FOREIGN KEY (id_mode_paiement) REFERENCES ref_modes_paiement(id_mode_paiement)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  INDEX idx_paiements_doc (id_document),
  INDEX idx_paiements_date (date_paiement)
) ENGINE=InnoDB;

-- =========================
-- TABLE: mouvements_stock (optionnel mais recommandé)
-- =========================
DROP TABLE IF EXISTS mouvements_stock;
CREATE TABLE IF NOT EXISTS mouvements_stock (
  id_mouvement          BIGINT AUTO_INCREMENT PRIMARY KEY,
  id_article            INT NOT NULL,
  date_mouvement        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  type_mouvement        ENUM('ENTREE','SORTIE','AJUSTEMENT') NOT NULL,
  quantite              DECIMAL(14,3) NOT NULL,
  id_document           BIGINT NULL,
  commentaire           VARCHAR(255) NULL,

  CONSTRAINT fk_mvt_stock_article
    FOREIGN KEY (id_article) REFERENCES articles(id_article)
    ON UPDATE CASCADE ON DELETE RESTRICT,

  CONSTRAINT fk_mvt_stock_document
    FOREIGN KEY (id_document) REFERENCES documents(id_document)
    ON UPDATE CASCADE ON DELETE SET NULL,

  INDEX idx_mvt_article_date (id_article, date_mouvement)
) ENGINE=InnoDB;

-- =========================
-- TABLE: audit_log (historique des changements)
-- =========================
DROP TABLE IF EXISTS audit_log;
CREATE TABLE IF NOT EXISTS audit_log (
  id_audit          BIGINT AUTO_INCREMENT PRIMARY KEY,
  date_action       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_utilisateur    INT NULL,

  table_name        VARCHAR(64) NOT NULL,
  record_id         VARCHAR(64) NOT NULL,
  action            ENUM('INSERT','UPDATE','DELETE','STATUS_CHANGE') NOT NULL,

  old_values_json   JSON NULL,
  new_values_json   JSON NULL,
  commentaire       VARCHAR(255) NULL,
  ip_client         VARCHAR(45) NULL,

  CONSTRAINT fk_audit_user
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateurs(id_utilisateur)
    ON UPDATE CASCADE ON DELETE SET NULL,

  INDEX idx_audit_table_record (table_name, record_id),
  INDEX idx_audit_date (date_action)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

-- =========================
-- (OPTIONNEL) Triggers pour mise à jour automatique du solde
-- =========================
DELIMITER $$

DROP TRIGGER IF EXISTS trg_update_solde_after_paiement_insert $$
CREATE TRIGGER trg_update_solde_after_paiement_insert
AFTER INSERT ON paiements
FOR EACH ROW
BEGIN
  UPDATE documents d
  SET d.solde = GREATEST(d.total_ttc - (
      SELECT IFNULL(SUM(p.montant),0) FROM paiements p WHERE p.id_document = d.id_document
  ), 0)
  WHERE d.id_document = NEW.id_document;
END $$

DROP TRIGGER IF EXISTS trg_update_solde_after_paiement_delete $$
CREATE TRIGGER trg_update_solde_after_paiement_delete
AFTER DELETE ON paiements
FOR EACH ROW
BEGIN
  UPDATE documents d
  SET d.solde = GREATEST(d.total_ttc - (
      SELECT IFNULL(SUM(p.montant),0) FROM paiements p WHERE p.id_document = d.id_document
  ), 0)
  WHERE d.id_document = OLD.id_document;
END $$

DELIMITER ;
