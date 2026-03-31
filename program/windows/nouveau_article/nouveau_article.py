from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from program.services import Article, Famille, LineEditAutoComplete, MessageBox, log_audit_event, select, with_db_session
from program.themes.shared_input_popup_style import apply_input_styles_to_window


NOUVEAU_ARTICLE_STYLE_MAP = {
    "__window__": ["QWidget", "global_font"],
    "__all_lineedits__": ["QLineEdit", "entry"],
    "__all_comboboxes__": ["QComboBox", "combobox"],
    "__all_combobox_popups__": ["QComboBox", "popup_list", {"row_height": 36}],
    "__all_completer_popups__": ["QLineEdit", "completer_popup", {"row_height": 36}],
    "btnSave": ["QPushButton", "primary"],
    "btnCancel": ["QPushButton", "secondary"],
}


def _safe_float(value_text) -> float:
    text = str(value_text or "").strip().replace(" ", "")
    if text in ("", "-"):
        return 0.0

    if "," in text and "." in text:
        text = text.replace(",", "")
    elif "," in text:
        if text.count(",") == 1 and len(text.split(",", 1)[1]) <= 2:
            text = text.replace(",", ".")
        else:
            text = text.replace(",", "")

    try:
        return float(text)
    except ValueError:
        return 0.0


def _parse_optional_float(text: str | None):
    value = (text or "").strip()
    if value == "":
        return None
    return _safe_float(value)


class NouveauArticleWindow(QDialog):
    def __init__(self, parent: QWidget | None = None, *, article_id: int | None = None):
        super().__init__(parent)
        self.setWindowFlag(Qt.Window, True)

        self._article_id = int(article_id) if article_id else None
        self._familles_by_name: dict[str, int] = {}
        self._famille_autocomplete: LineEditAutoComplete | None = None

        self._build_ui()
        apply_input_styles_to_window(self, row_height=36, widget_styles_map=NOUVEAU_ARTICLE_STYLE_MAP)

        self._load_familles_for_autocomplete()
        if self._article_id:
            self._load_article(self._article_id)

        self._wire_signals()

    def _build_ui(self) -> None:
        self.setMinimumWidth(620)

        self.titleLabel = QLabel("Nouveau Article")
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        form = QFormLayout()
        form.setHorizontalSpacing(18)
        form.setVerticalSpacing(10)

        self.referenceLineEdit = QLineEdit()
        self.referenceLineEdit.setPlaceholderText("Référence interne")

        self.nomLineEdit = QLineEdit()
        self.nomLineEdit.setPlaceholderText("Nom de l'article")

        self.familleLineEdit = QLineEdit()
        self.familleLineEdit.setPlaceholderText("Famille")

        self.prixVenteLineEdit = QLineEdit()
        self.prixVenteLineEdit.setPlaceholderText("0.00")

        self.prixAchatLineEdit = QLineEdit()
        self.prixAchatLineEdit.setPlaceholderText("0.00")

        self.tvaCombo = QComboBox()
        self.tvaCombo.addItems(["20.00%", "10.00%", "5.00%"])
        self.tvaCombo.setCurrentText("20.00%")

        self.quantiteLineEdit = QLineEdit()
        self.quantiteLineEdit.setPlaceholderText("0.00")

        self.quantiteMinLineEdit = QLineEdit()
        self.quantiteMinLineEdit.setPlaceholderText("(optionnel)")

        self.quantiteMaxLineEdit = QLineEdit()
        self.quantiteMaxLineEdit.setPlaceholderText("(optionnel)")

        self.suiviStockCombo = QComboBox()
        self.suiviStockCombo.addItem("CMUP", "CMUP")
        self.suiviStockCombo.addItem("FIFO", "FIFO")
        self.suiviStockCombo.addItem("LIFO", "LIFO")
        self.suiviStockCombo.addItem("Serial numero", "SERIAL_NUMERO")
        self.suiviStockCombo.addItem("Aucun", "AUCUN")
        self.suiviStockCombo.setCurrentIndex(0)

        form.addRow("Référence interne", self.referenceLineEdit)
        form.addRow("Nom article", self.nomLineEdit)
        form.addRow("Famille", self.familleLineEdit)
        form.addRow("Prix vente HT", self.prixVenteLineEdit)
        form.addRow("Prix achat HT", self.prixAchatLineEdit)
        form.addRow("TVA", self.tvaCombo)
        form.addRow("Quantité", self.quantiteLineEdit)
        form.addRow("Quantité min", self.quantiteMinLineEdit)
        form.addRow("Quantité max", self.quantiteMaxLineEdit)
        form.addRow("Suivi stock", self.suiviStockCombo)

        self.btnCancel = QPushButton("Annuler")
        self.btnCancel.setObjectName("btnCancel")
        self.btnSave = QPushButton("Enregistrer")
        self.btnSave.setObjectName("btnSave")
        self.btnSave.setDefault(True)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch(1)
        buttons.addWidget(self.btnCancel)
        buttons.addWidget(self.btnSave)

        root = QVBoxLayout()
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)
        root.addWidget(self.titleLabel)
        root.addLayout(form)
        root.addLayout(buttons)

        self.setLayout(root)

    def _wire_signals(self) -> None:
        self.btnCancel.clicked.connect(self.reject)
        self.btnSave.clicked.connect(self._on_save_clicked)

    @with_db_session
    def _fetch_familles(self, session=None):
        return session.execute(
            select(Famille.id_famille, Famille.nom_famille).order_by(Famille.nom_famille)
        ).all()

    def _load_familles_for_autocomplete(self) -> None:
        familles = self._fetch_familles()
        names: list[str] = []
        self._familles_by_name.clear()

        for fam_id, fam_name in familles:
            name = (fam_name or "").strip()
            if not name:
                continue
            names.append(name)
            self._familles_by_name[name.casefold()] = int(fam_id)

        self._famille_autocomplete = LineEditAutoComplete(self.familleLineEdit, self)
        self._famille_autocomplete.set_items(names)
        self._famille_autocomplete.set_force_show_on_focus(True)

    @with_db_session
    def _fetch_article_row(self, article_id: int, session=None):
        return session.execute(
            select(
                Article.reference_interne,
                Article.nom_article,
                Article.prix_vente_ht,
                Article.prix_achat_ht,
                Article.id_famille,
                Famille.nom_famille,
                Article.taux_tva,
                Article.quantite,
                Article.quantite_min,
                Article.quantite_max,
                Article.suivi_stock,
            )
            .outerjoin(Famille, Article.id_famille == Famille.id_famille)
            .where(Article.id_article == int(article_id))
            .limit(1)
        ).one_or_none()

    def _load_article(self, article_id: int) -> None:
        row = self._fetch_article_row(article_id)
        if row is None:
            MessageBox(
                variant="attention",
                title="Article",
                message="Article introuvable.",
                parent=self,
            ).exec_()
            return

        self.titleLabel.setText("Modifier Article")
        self.setWindowTitle("Modifier Article")

        self.referenceLineEdit.setText((row.reference_interne or "").strip())
        self.nomLineEdit.setText((row.nom_article or "").strip())
        self.familleLineEdit.setText((row.nom_famille or "").strip())

        self.prixVenteLineEdit.setText(str(row.prix_vente_ht or "0.00"))
        self.prixAchatLineEdit.setText(str(row.prix_achat_ht or "0.00"))
        self.quantiteLineEdit.setText(str(row.quantite or "0.00"))

        self.quantiteMinLineEdit.setText("" if row.quantite_min is None else str(row.quantite_min))
        self.quantiteMaxLineEdit.setText("" if row.quantite_max is None else str(row.quantite_max))

        if row.taux_tva is not None:
            wanted = f"{float(row.taux_tva):.2f}%"
            idx = self.tvaCombo.findText(wanted)
            if idx >= 0:
                self.tvaCombo.setCurrentIndex(idx)

        suivi_value = (row.suivi_stock or "").strip()
        if suivi_value:
            for idx in range(self.suiviStockCombo.count()):
                if self.suiviStockCombo.itemData(idx) == suivi_value:
                    self.suiviStockCombo.setCurrentIndex(idx)
                    break

    @with_db_session
    def _save_to_db(self, session=None):
        nom_article = (self.nomLineEdit.text() or "").strip()
        if not nom_article:
            raise ValueError("Le nom de l'article est obligatoire.")

        reference_interne = (self.referenceLineEdit.text() or "").strip() or None
        famille_name = (self.familleLineEdit.text() or "").strip()

        famille_id = None
        if famille_name:
            famille_id = self._familles_by_name.get(famille_name.casefold())
            if famille_id is None:
                raise ValueError("Famille introuvable.")

        prix_vente_ht = _safe_float(self.prixVenteLineEdit.text())
        prix_achat_ht = _safe_float(self.prixAchatLineEdit.text())

        tva_text = (self.tvaCombo.currentText() or "").strip().replace("%", "")
        taux_tva = _safe_float(tva_text) if tva_text else None

        quantite = _safe_float(self.quantiteLineEdit.text())
        quantite_min = _parse_optional_float(self.quantiteMinLineEdit.text())
        quantite_max = _parse_optional_float(self.quantiteMaxLineEdit.text())

        if quantite_min is not None and quantite_max is not None and float(quantite_min) > float(quantite_max):
            raise ValueError("Quantité min doit être <= quantité max.")

        suivi_stock = self.suiviStockCombo.currentData() or "CMUP"

        is_new = not bool(self._article_id)
        old_values = None

        if self._article_id:
            article = session.execute(
                select(Article).where(Article.id_article == int(self._article_id))
            ).scalar_one_or_none()
            if article is None:
                raise ValueError("Article introuvable.")

            old_values = {
                "reference_interne": (article.reference_interne or "").strip() or None,
                "nom_article": (article.nom_article or "").strip() or None,
                "id_famille": int(article.id_famille) if article.id_famille is not None else None,
                "prix_vente_ht": float(article.prix_vente_ht or 0),
                "prix_achat_ht": float(article.prix_achat_ht or 0),
                "taux_tva": float(article.taux_tva or 0) if article.taux_tva is not None else None,
                "quantite": float(article.quantite or 0),
                "actif": int(article.actif or 0),
            }
        else:
            article = Article(nom_article=nom_article, actif=1)
            session.add(article)

        article.reference_interne = reference_interne
        article.nom_article = nom_article
        article.id_famille = famille_id
        article.prix_vente_ht = prix_vente_ht
        article.prix_achat_ht = prix_achat_ht
        article.taux_tva = taux_tva
        article.quantite = quantite
        article.quantite_min = quantite_min
        article.quantite_max = quantite_max
        article.suivi_stock = str(suivi_stock)
        article.actif = 1

        session.flush()

        new_values = {
            "reference_interne": (article.reference_interne or "").strip() or None,
            "nom_article": (article.nom_article or "").strip() or None,
            "id_famille": int(article.id_famille) if article.id_famille is not None else None,
            "prix_vente_ht": float(article.prix_vente_ht or 0),
            "prix_achat_ht": float(article.prix_achat_ht or 0),
            "taux_tva": float(article.taux_tva or 0) if article.taux_tva is not None else None,
            "quantite": float(article.quantite or 0),
            "actif": int(article.actif or 0),
        }
        action = "INSERT" if is_new else "UPDATE"
        comment = "Création article" if is_new else "Modification article"
        log_audit_event(
            session,
            table_name=Article.__tablename__,
            record_id=int(article.id_article),
            action=action,
            old_values=old_values,
            new_values=new_values,
            comment=f"{comment}: {(article.reference_interne or '').strip()} {(article.nom_article or '').strip()}".strip(),
        )

    def _on_save_clicked(self) -> None:
        try:
            self._save_to_db()
        except ValueError as exc:
            MessageBox(
                variant="attention",
                title="Validation",
                message=str(exc),
                parent=self,
            ).exec_()
            return
        except Exception as exc:
            MessageBox(
                variant="attention",
                title="Erreur",
                message=str(exc),
                parent=self,
            ).exec_()
            return

        self.accept()
