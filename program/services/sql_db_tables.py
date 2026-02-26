# models.py — SQLAlchemy 2.0 ORM mappings for ERP_database.sql (MySQL 8+)

from __future__ import annotations

from datetime import date, datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    DECIMAL,
    Enum,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    TIMESTAMP,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.mysql import BIGINT, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ---------------------------
# Tables
# ---------------------------

class InformationsSociete(Base):
    __tablename__ = "informations_societe"

    id_societe: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_societe: Mapped[str] = mapped_column(String(150), nullable=False)
    activite: Mapped[Optional[str]] = mapped_column(String(150))
    forme_juridique: Mapped[Optional[str]] = mapped_column(String(80))
    patente: Mapped[Optional[str]] = mapped_column(String(50))
    cnss: Mapped[Optional[str]] = mapped_column(String(50))
    telephone_fix: Mapped[Optional[str]] = mapped_column(String(30))
    fax: Mapped[Optional[str]] = mapped_column(String(30))
    site_web: Mapped[Optional[str]] = mapped_column(String(150))
    ice: Mapped[Optional[str]] = mapped_column(String(30))
    if_fiscal: Mapped[Optional[str]] = mapped_column(String(30))
    rc: Mapped[Optional[str]] = mapped_column(String(30))
    email: Mapped[Optional[str]] = mapped_column(String(120))
    logo_path: Mapped[Optional[str]] = mapped_column(String(255))
    adresse: Mapped[Optional[str]] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id_utilisateur: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_utilisateur: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, server_default=text("'VENDEUR'"))
    permissions_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    documents: Mapped[List["Document"]] = relationship(back_populates="vendeur")
    audits: Mapped[List["AuditLog"]] = relationship(back_populates="utilisateur")


class RefDomaine(Base):
    __tablename__ = "ref_domaines"

    id_domaine: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code_domaine: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    libelle_domaine: Mapped[str] = mapped_column(String(60), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    documents: Mapped[List["Document"]] = relationship(back_populates="domaine")
    types_documents: Mapped[List["RefTypeDocument"]] = relationship(back_populates="domaine")


class RefStatutDocument(Base):
    __tablename__ = "ref_statuts_documents"

    id_statut: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code_statut: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    libelle_statut: Mapped[str] = mapped_column(String(60), nullable=False)
    couleur: Mapped[Optional[str]] = mapped_column(String(15))
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    documents: Mapped[List["Document"]] = relationship(back_populates="statut")


class RefModePaiement(Base):
    __tablename__ = "ref_modes_paiement"

    id_mode_paiement: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code_mode: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    libelle_mode: Mapped[str] = mapped_column(String(60), nullable=False)
    besoin_reference: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    besoin_echeance: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    paiements: Mapped[List["Paiement"]] = relationship(back_populates="mode_paiement")


class RefTypeTiers(Base):
    __tablename__ = "ref_types_tiers"

    id_type_tiers: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code_type_tiers: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    libelle_type: Mapped[str] = mapped_column(String(60), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    tiers: Mapped[List["Tiers"]] = relationship(back_populates="type_tiers_ref")


class Famille(Base):
    __tablename__ = "familles"

    id_famille: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_famille: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    taux_tva: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    suivi_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    unite_defaut: Mapped[Optional[str]] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    articles: Mapped[List["Article"]] = relationship(back_populates="famille")


class Article(Base):
    __tablename__ = "articles"

    id_article: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nom_article: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))

    prix_vente_ht: Mapped[float] = mapped_column(
        DECIMAL(12, 2), nullable=False, server_default=text("0.00")
    )
    prix_achat_ht: Mapped[float] = mapped_column(
        DECIMAL(12, 2), nullable=False, server_default=text("0.00")
    )

    id_famille: Mapped[Optional[int]] = mapped_column(
        ForeignKey("familles.id_famille", onupdate="CASCADE", ondelete="SET NULL")
    )
    taux_tva: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    suivi_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    unite: Mapped[Optional[str]] = mapped_column(String(20))
    reference_interne: Mapped[Optional[str]] = mapped_column(String(60))
    code_barres: Mapped[Optional[str]] = mapped_column(String(60))
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    famille: Mapped[Optional["Famille"]] = relationship(back_populates="articles")
    details: Mapped[List["DetailDocument"]] = relationship(back_populates="article")
    mouvements_stock: Mapped[List["MouvementStock"]] = relationship(back_populates="article")


class Tiers(Base):
    __tablename__ = "tiers"

    id_tiers: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    type_tiers: Mapped[str] = mapped_column(
        Enum("CLIENT", "FOURNISSEUR", name="tiers_type_enum"),
        nullable=False,
    )

    id_type_tiers: Mapped[Optional[int]] = mapped_column(
        ForeignKey("ref_types_tiers.id_type_tiers", onupdate="CASCADE", ondelete="SET NULL")
    )

    nom_tiers: Mapped[str] = mapped_column(String(160), nullable=False)
    adresse: Mapped[Optional[str]] = mapped_column(String(255))
    ice: Mapped[Optional[str]] = mapped_column(String(30))
    telephone: Mapped[Optional[str]] = mapped_column(String(30))
    email: Mapped[Optional[str]] = mapped_column(String(120))
    plafond_credit: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2))
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    type_tiers_ref: Mapped[Optional["RefTypeTiers"]] = relationship(back_populates="tiers")
    documents: Mapped[List["Document"]] = relationship(back_populates="tiers")


class RefTypeDocument(Base):
    __tablename__ = "ref_types_documents"

    id_type_document: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code_type: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    libelle_type: Mapped[str] = mapped_column(String(80), nullable=False)

    id_domaine: Mapped[int] = mapped_column(
        ForeignKey("ref_domaines.id_domaine", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )

    impact_stock: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("0"))
    signe_quantite: Mapped[int] = mapped_column(SmallInteger, nullable=False, server_default=text("0"))
    actif: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    ordre: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    domaine: Mapped["RefDomaine"] = relationship(back_populates="types_documents")
    documents: Mapped[List["Document"]] = relationship(back_populates="type_document")


class DocumentCounter(Base):
    __tablename__ = "document_counters"
    __table_args__ = (
        UniqueConstraint("id_type_document", "annee", name="uq_counter_type_year"),
        Index("idx_counter_type", "id_type_document"),
    )

    id_counter: Mapped[int] = mapped_column(BIGINT(unsigned=True), primary_key=True, autoincrement=True)
    id_type_document: Mapped[int] = mapped_column(Integer, nullable=False)
    annee: Mapped[int] = mapped_column(Integer, nullable=False)
    valeur_courante: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    longueur: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("3"))
    prefixe: Mapped[str] = mapped_column(String(10), nullable=False)
    suffixe: Mapped[Optional[str]] = mapped_column(String(20))
    reset_annuel: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )


class Document(Base):
    __tablename__ = "documents"

    id_document: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_domaine: Mapped[int] = mapped_column(
        ForeignKey("ref_domaines.id_domaine", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    id_type_document: Mapped[int] = mapped_column(
        ForeignKey("ref_types_documents.id_type_document", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    numero_document: Mapped[str] = mapped_column(String(30), nullable=False)

    id_tiers: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tiers.id_tiers", onupdate="CASCADE", ondelete="SET NULL")
    )

    date_document: Mapped[date] = mapped_column(Date, nullable=False)
    date_livraison: Mapped[Optional[date]] = mapped_column(Date)

    mode_prix: Mapped[str] = mapped_column(
        Enum("HT", "TTC", name="mode_prix_enum"),
        nullable=False,
        server_default=text("'HT'"),
    )

    total_ht: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))
    total_tva: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))
    total_ttc: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))
    solde: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))

    id_vendeur: Mapped[int] = mapped_column(
        ForeignKey("utilisateurs.id_utilisateur", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )

    id_statut: Mapped[int] = mapped_column(
        ForeignKey("ref_statuts_documents.id_statut", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )

    commentaire: Mapped[Optional[str]] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
    )

    domaine: Mapped["RefDomaine"] = relationship(back_populates="documents")
    type_document: Mapped["RefTypeDocument"] = relationship(back_populates="documents")
    tiers: Mapped[Optional["Tiers"]] = relationship(back_populates="documents")
    vendeur: Mapped["Utilisateur"] = relationship(back_populates="documents")
    statut: Mapped["RefStatutDocument"] = relationship(back_populates="documents")

    details: Mapped[List["DetailDocument"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    paiements: Mapped[List["Paiement"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
    )
    mouvements_stock: Mapped[List["MouvementStock"]] = relationship(back_populates="document")


class DetailDocument(Base):
    __tablename__ = "details_documents"

    id_detail: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_document: Mapped[int] = mapped_column(
        ForeignKey("documents.id_document", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    id_article: Mapped[int] = mapped_column(
        ForeignKey("articles.id_article", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(String(255))

    quantite: Mapped[float] = mapped_column(DECIMAL(14, 3), nullable=False, server_default=text("1.000"))

    prix_unitaire_ht: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))
    prix_unitaire_ttc: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))

    unite_vente: Mapped[Optional[str]] = mapped_column(String(20))
    taux_tva: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    marge_beneficiaire: Mapped[Optional[float]] = mapped_column(DECIMAL(14, 2))

    total_ligne_ht: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))
    total_ligne_tva: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))
    total_ligne_ttc: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    document: Mapped["Document"] = relationship(back_populates="details")
    article: Mapped["Article"] = relationship(back_populates="details")


class Paiement(Base):
    __tablename__ = "paiements"

    id_paiement: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_document: Mapped[int] = mapped_column(
        ForeignKey("documents.id_document", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    date_paiement: Mapped[date] = mapped_column(Date, nullable=False)

    id_mode_paiement: Mapped[int] = mapped_column(
        ForeignKey("ref_modes_paiement.id_mode_paiement", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    montant: Mapped[float] = mapped_column(DECIMAL(14, 2), nullable=False, server_default=text("0.00"))

    reference: Mapped[Optional[str]] = mapped_column(String(60))
    date_echeance: Mapped[Optional[date]] = mapped_column(Date)
    banque: Mapped[Optional[str]] = mapped_column(String(80))

    statut: Mapped[str] = mapped_column(
        Enum("ENCAISSE", "EN_ATTENTE", "REJETE", name="paiement_statut_enum"),
        nullable=False,
        server_default=text("'ENCAISSE'"),
    )

    commentaire: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    document: Mapped["Document"] = relationship(back_populates="paiements")
    mode_paiement: Mapped["RefModePaiement"] = relationship(back_populates="paiements")


class MouvementStock(Base):
    __tablename__ = "mouvements_stock"

    id_mouvement: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    id_article: Mapped[int] = mapped_column(
        ForeignKey("articles.id_article", onupdate="CASCADE", ondelete="RESTRICT"),
        nullable=False,
    )
    date_mouvement: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    type_mouvement: Mapped[str] = mapped_column(
        Enum("ENTREE", "SORTIE", "AJUSTEMENT", name="mvt_stock_type_enum"),
        nullable=False,
    )
    quantite: Mapped[float] = mapped_column(DECIMAL(14, 3), nullable=False)

    id_document: Mapped[Optional[int]] = mapped_column(
        ForeignKey("documents.id_document", onupdate="CASCADE", ondelete="SET NULL")
    )
    commentaire: Mapped[Optional[str]] = mapped_column(String(255))

    article: Mapped["Article"] = relationship(back_populates="mouvements_stock")
    document: Mapped[Optional["Document"]] = relationship(back_populates="mouvements_stock")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id_audit: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    date_action: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    id_utilisateur: Mapped[Optional[int]] = mapped_column(
        ForeignKey("utilisateurs.id_utilisateur", onupdate="CASCADE", ondelete="SET NULL")
    )

    table_name: Mapped[str] = mapped_column(String(64), nullable=False)
    record_id: Mapped[str] = mapped_column(String(64), nullable=False)

    action: Mapped[str] = mapped_column(
        Enum("INSERT", "UPDATE", "DELETE", "STATUS_CHANGE", name="audit_action_enum"),
        nullable=False,
    )

    old_values_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    new_values_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    commentaire: Mapped[Optional[str]] = mapped_column(String(255))
    ip_client: Mapped[Optional[str]] = mapped_column(String(45))

    utilisateur: Mapped[Optional["Utilisateur"]] = relationship(back_populates="audits")