from __future__ import annotations

import os
import sys
from datetime import datetime

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from PyQt5.uic import loadUi

from program.services import Counter, MessageBox, Tiers, log_audit_event, select, with_db_session
from program.themes.shared_input_popup_style import (
    apply_input_styles_to_window,
    apply_textedit_style_to_window,
    BORDER_SIZE,
    BUTTON_PRIMARY_BG,
    COLOR_BG,
    COLOR_BG_SOFT,
    COLOR_BORDER,
    COLOR_TEXT_MUTED,
    RADIUS_ITEM,
)


NOUVEAU_CLIENT_STYLE_MAP = {
    "btnEnregistrer": ["QPushButton", "primary"],
    "btnAnnuler": ["QPushButton", "secondary"],
}


def resource_path(relative_path: str) -> str:
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


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


class NouveauClientWindow(QDialog):
    def __init__(self, parent: QWidget | None = None, *, tiers_id: int | None = None):
        super().__init__(parent)

        self._tiers_id = int(tiers_id) if tiers_id else None

        loadUi(resource_path("nouveau_client.ui"), self)
        self._setup_input_styles()

        # Frameless window hint for custom title bar design
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._dragging = False
        self._drag_position = None
        if hasattr(self, "headerFrame") and self.headerFrame is not None:
            self.headerFrame.mousePressEvent = self.header_mousePressEvent
            self.headerFrame.mouseMoveEvent = self.header_mouseMoveEvent
            self.headerFrame.mouseReleaseEvent = self.header_mouseReleaseEvent

        self._wire_signals()
        self._setup_toggle_behavior()

        if self._tiers_id:
            self._load_tiers(self._tiers_id)

    def _setup_input_styles(self) -> None:
        # Drop the .ui-level hardcoded stylesheet so token styles drive the UI.
        try:
            self.setStyleSheet("")
        except Exception:
            pass

        apply_input_styles_to_window(self, row_height=36, widget_styles_map=NOUVEAU_CLIENT_STYLE_MAP)
        apply_textedit_style_to_window(self)

        self._apply_container_styles()
        self._apply_toggle_button_styles()

    def _apply_container_styles(self) -> None:
        # Keep the window structure (frames + rounded corners) but use token colors.
        main_frame = getattr(self, "mainFrame", None)
        if main_frame is not None:
            main_frame.setStyleSheet(
                f"""
#mainFrame {{
    background-color: {COLOR_BG_SOFT};
    border-radius: 12px;
    border: {BORDER_SIZE}px solid {COLOR_BORDER};
}}
"""
            )

        header_frame = getattr(self, "headerFrame", None)
        if header_frame is not None:
            header_frame.setStyleSheet(
                f"""
#headerFrame {{
    background-color: {COLOR_BG};
    border-bottom: {BORDER_SIZE}px solid {COLOR_BORDER};
    border-top-left-radius: 12px;
    border-top-right-radius: 12px;
}}
"""
            )

        footer_frame = getattr(self, "frameFooter", None)
        if footer_frame is not None:
            footer_frame.setStyleSheet(
                f"""
#frameFooter {{
    background-color: {COLOR_BG};
    border-top: {BORDER_SIZE}px solid {COLOR_BORDER};
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}}
"""
            )

        toggle_frame = getattr(self, "frameToggle", None)
        if toggle_frame is not None:
            toggle_frame.setStyleSheet(
                f"""
#frameToggle {{
    background-color: {COLOR_BG_SOFT};
    border-radius: 8px;
}}
"""
            )

        coord_frame = getattr(self, "frameCoord", None)
        if coord_frame is not None:
            coord_frame.setStyleSheet(
                f"""
#frameCoord {{
    background-color: {COLOR_BG};
    border-radius: 12px;
    border: {BORDER_SIZE}px solid {COLOR_BORDER};
}}
"""
            )

    def _apply_toggle_button_styles(self) -> None:
        btn_ent = getattr(self, "btnEntreprise", None)
        btn_part = getattr(self, "btnParticulier", None)
        if btn_ent is None or btn_part is None:
            return

        radius = max(2, int(RADIUS_ITEM) - 2)
        toggle_qss = f"""
QPushButton {{
    background-color: transparent;
    color: {COLOR_TEXT_MUTED};
    border: {BORDER_SIZE}px solid transparent;
    border-radius: {radius}px;
    padding: 8px 24px;
}}

QPushButton:hover:!checked {{
    background-color: {COLOR_BG};
    border-color: {COLOR_BORDER};
}}

QPushButton:checked {{
    background-color: {COLOR_BG};
    color: {BUTTON_PRIMARY_BG};
    border-color: {COLOR_BORDER};
}}
"""

        try:
            btn_ent.setStyleSheet(toggle_qss)
        except RuntimeError:
            pass
        try:
            btn_part.setStyleSheet(toggle_qss)
        except RuntimeError:
            pass

    def _wire_signals(self) -> None:
        if hasattr(self, "btnAnnuler"):
            self.btnAnnuler.clicked.connect(self.reject)
        if hasattr(self, "btnEnregistrer"):
            self.btnEnregistrer.clicked.connect(self._on_save_clicked)

    def _setup_toggle_behavior(self) -> None:
        btn_ent = getattr(self, "btnEntreprise", None)
        btn_part = getattr(self, "btnParticulier", None)
        if btn_ent is None or btn_part is None:
            return

        def select_ent():
            btn_ent.setChecked(True)
            btn_part.setChecked(False)

        def select_part():
            btn_part.setChecked(True)
            btn_ent.setChecked(False)

        btn_ent.clicked.connect(select_ent)
        btn_part.clicked.connect(select_part)

        if not btn_ent.isChecked() and not btn_part.isChecked():
            btn_ent.setChecked(True)

    @with_db_session
    def _fetch_tiers_row(self, tiers_id: int, session=None):
        return session.execute(
            select(
                Tiers.type_tiers,
                Tiers.nom_tiers,
                Tiers.ice,
                Tiers.adresse,
                Tiers.telephone,
                Tiers.email,
                Tiers.plafond_credit,
            )
            .where(Tiers.id_tiers == int(tiers_id))
            .limit(1)
        ).one_or_none()

    def _load_tiers(self, tiers_id: int) -> None:
        row = self._fetch_tiers_row(tiers_id)
        if row is None:
            MessageBox(
                variant="attention",
                title="Client",
                message="Client introuvable.",
                parent=self,
            ).exec_()
            self.reject()
            return

        if hasattr(self, "lblHeaderTitle"):
            self.lblHeaderTitle.setText("Modifier Client")
        self.setWindowTitle("Modifier Client")

        type_value = (row.type_tiers or "").strip().upper()
        if type_value == "PARTICULIER":
            if hasattr(self, "btnParticulier"):
                self.btnParticulier.setChecked(True)
            if hasattr(self, "btnEntreprise"):
                self.btnEntreprise.setChecked(False)
        else:
            if hasattr(self, "btnEntreprise"):
                self.btnEntreprise.setChecked(True)
            if hasattr(self, "btnParticulier"):
                self.btnParticulier.setChecked(False)

        if hasattr(self, "editNom"):
            self.editNom.setText((row.nom_tiers or "").strip())
        if hasattr(self, "editICE"):
            self.editICE.setText((row.ice or "").strip())
        if hasattr(self, "editAdresse"):
            self.editAdresse.setPlainText((row.adresse or "").strip())
        if hasattr(self, "editTelPrincipal"):
            self.editTelPrincipal.setText((row.telephone or "").strip())
        if hasattr(self, "editEmail"):
            self.editEmail.setText((row.email or "").strip())
        if hasattr(self, "editCreditPlafond"):
            self.editCreditPlafond.setText("" if row.plafond_credit is None else str(row.plafond_credit))

    def _selected_type_tiers(self) -> str:
        if hasattr(self, "btnParticulier") and self.btnParticulier.isChecked():
            return "PARTICULIER"
        return "CLIENT"

    @staticmethod
    def _counter_code_for_type(type_tiers: str) -> str:
        mapping = {
            "CLIENT": "CL",
            "FOURNISSEUR": "FR",
            "SOCIETE": "SOC",
            "PARTICULIER": "PAR",
            "ADMIN": "ADM",
        }
        code = mapping.get((type_tiers or "").strip().upper())
        if not code:
            raise ValueError("Type de tiers invalide.")
        return code

    def _generate_code_tiers(self, session, type_tiers: str) -> str:
        """Generate a tiers code using counters, without burning numbers."""

        current_year = datetime.now().year
        code = self._counter_code_for_type(type_tiers)

        counter = session.execute(
            select(Counter)
            .where(
                Counter.categorie == "TIERS",
                Counter.code == code,
                Counter.annee == current_year,
            )
            .with_for_update()
        ).scalar_one_or_none()

        if not counter:
            counter = Counter(
                categorie="TIERS",
                code=code,
                annee=current_year,
                valeur_courante=1,
                longueur=3,
                prefixe=code,
                suffixe=None,
                reset_annuel=True,
            )
            session.add(counter)
            session.flush()

        if counter.longueur is None or int(counter.longueur) <= 0:
            counter.longueur = 3
        if counter.valeur_courante is None or int(counter.valeur_courante) <= 0:
            counter.valeur_courante = 1

        prefix = (counter.prefixe or code).strip() or code

        while True:
            candidate = f"{prefix}-{str(int(counter.valeur_courante)).zfill(int(counter.longueur))}"
            exists = session.execute(
                select(Tiers.id_tiers).where(Tiers.code_tiers == candidate)
            ).scalar_one_or_none()
            if exists:
                counter.valeur_courante = int(counter.valeur_courante) + 1
                continue
            return candidate

    @with_db_session
    def _save_to_db(self, session=None) -> None:
        nom_tiers = (self.editNom.text() if hasattr(self, "editNom") else "").strip()
        if not nom_tiers:
            raise ValueError("Le nom du client est obligatoire.")

        type_tiers = self._selected_type_tiers()

        ice = (self.editICE.text() if hasattr(self, "editICE") else "").strip() or None
        adresse = (self.editAdresse.toPlainText() if hasattr(self, "editAdresse") else "").strip() or None

        telephone = (self.editTelPrincipal.text() if hasattr(self, "editTelPrincipal") else "").strip() or None
        email = (self.editEmail.text() if hasattr(self, "editEmail") else "").strip() or None

        plafond_credit_raw = (self.editCreditPlafond.text() if hasattr(self, "editCreditPlafond") else "")
        plafond_credit = _safe_float(plafond_credit_raw)

        is_new = not bool(self._tiers_id)
        old_values = None

        if self._tiers_id:
            tiers = session.execute(
                select(Tiers).where(Tiers.id_tiers == int(self._tiers_id))
            ).scalar_one_or_none()
            if tiers is None:
                raise ValueError("Client introuvable.")

            old_values = {
                "code_tiers": (tiers.code_tiers or "").strip() or None,
                "nom_tiers": (tiers.nom_tiers or "").strip() or None,
                "type_tiers": (tiers.type_tiers or "").strip() or None,
                "actif": int(tiers.actif or 0),
            }
        else:
            tiers = Tiers(
                type_tiers=type_tiers,
                nom_tiers=nom_tiers,
                actif=1,
            )
            session.add(tiers)

        if not (tiers.code_tiers or "").strip():
            tiers.code_tiers = self._generate_code_tiers(session, type_tiers)

        tiers.type_tiers = type_tiers
        tiers.nom_tiers = nom_tiers
        tiers.ice = ice
        tiers.adresse = adresse
        tiers.telephone = telephone
        tiers.email = email
        tiers.plafond_credit = plafond_credit
        if not self._tiers_id:
            tiers.actif = 1

        session.flush()

        new_values = {
            "code_tiers": (tiers.code_tiers or "").strip() or None,
            "nom_tiers": (tiers.nom_tiers or "").strip() or None,
            "type_tiers": (tiers.type_tiers or "").strip() or None,
            "actif": int(tiers.actif or 0),
        }
        action = "INSERT" if is_new else "UPDATE"
        comment = "Création client" if is_new else "Modification client"
        log_audit_event(
            session,
            table_name=Tiers.__tablename__,
            record_id=int(tiers.id_tiers),
            action=action,
            old_values=old_values,
            new_values=new_values,
            comment=f"{comment}: {(tiers.code_tiers or '').strip()} {(tiers.nom_tiers or '').strip()}".strip(),
        )

    def _on_save_clicked(self) -> None:
        try:
            self._save_to_db()
        except ValueError as exc:
            MessageBox(variant="attention", title="Validation", message=str(exc), parent=self).exec_()
            return
        except Exception as exc:
            MessageBox(variant="attention", title="Erreur", message=str(exc), parent=self).exec_()
            return

        self.accept()

    # Draggable title bar logic
    def header_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPos() - self.pos()
            event.accept()

    def header_mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._dragging:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def header_mouseReleaseEvent(self, event):
        self._dragging = False


def main() -> None:
    app = QApplication(sys.argv)
    window = NouveauClientWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
