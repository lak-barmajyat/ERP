from __future__ import annotations
from program.services import Tiers, select, with_db_session, generate_document_number
from PyQt5.QtWidgets import QDialog, QCompleter, QComboBox
from PyQt5.QtCore import QStringListModel, Qt, QSortFilterProxyModel, QTimer


def setup_doc_num_entry(nouveau_doc_window):
    selected_doc_type = nouveau_doc_window.doc_type_window.get_selected_doc_type()
    if not selected_doc_type:
        return

    nouveau_doc_window.selected_doc_type = selected_doc_type
    nouveau_doc_window.setWindowTitle(f"Nouveau document - {selected_doc_type}")
    nouveau_doc_window.show()
    nouveau_doc_window.n_piece_editline.setText(generate_document_number(nouveau_doc_window.selected_doc_type))
    nouveau_doc_window.n_piece_editline.setReadOnly(True)
    nouveau_doc_window.n_piece_editline.setStyleSheet("color: gray;")



def _normalize_client_names(client_names: list[str]) -> list[str]:
    unique_names: list[str] = []
    seen = set()

    for raw_name in client_names:
        if raw_name is None:
            continue

        normalized_name = str(raw_name).strip()
        if not normalized_name:
            continue

        key = normalized_name.casefold()
        if key in seen:
            continue

        seen.add(key)
        unique_names.append(normalized_name)

    unique_names.sort(key=str.casefold)
    return unique_names


def _safe_disconnect(signal, handler):
    try:
        signal.disconnect(handler)
    except Exception:
        pass


def setup_clients_combo(combo: QComboBox, session=None, *, allow_free_text: bool = True):
    """
    Enhanced searchable QComboBox for clients:
    - Editable with placeholder
    - Contains-based filtering via proxy model (stable)
    - No weird coupling with combo.view()
    - Prevents duplicate signal connections
    - Optional: forbid free text (allow_free_text=False) => only existing clients
    """

    if session is None:
        raise ValueError("session is required")

    # ✅ أفضل من fetchall: يرجع list[str] مباشرة
    query = (
        select(Tiers.nom_tiers)
        .where(Tiers.type_tiers == "CLIENT")
        .order_by(Tiers.nom_tiers)
    )
    client_names = session.execute(query).scalars().all()
    normalized_clients = _normalize_client_names(client_names)

    combo.blockSignals(True)

    combo.setEditable(True)
    combo.setInsertPolicy(QComboBox.NoInsert)  # لا تضيف عنصر جديد تلقائيًا
    combo.clear()
    combo.addItems(normalized_clients)
    combo.setCurrentIndex(-1)

    le = combo.lineEdit()
    if le is None:
        combo.blockSignals(False)
        return None, None

    # Placeholder رمادي + تجربة كتابة نظيفة
    le.clear()
    le.setPlaceholderText("Client")
    le.setClearButtonEnabled(True)

    # ---------------------------------------
    # Models: base model + proxy for contains
    # ---------------------------------------
    base_model = QStringListModel(normalized_clients, combo)

    proxy = QSortFilterProxyModel(combo)
    proxy.setSourceModel(base_model)
    proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)
    proxy.setFilterKeyColumn(0)

    # ---------------------------------------
    # Completer
    # ---------------------------------------
    completer = QCompleter(proxy, combo)
    completer.setCaseSensitivity(Qt.CaseInsensitive)
    completer.setCompletionMode(QCompleter.PopupCompletion)

    # ✅ هنا أهم نقطة:
    # - نستخدم proxy + setFilterFixedString (contains behavior سنفعله عبر filterRegExp)
    # - MatchContains أحياناً لا يكفي لوحده حسب Qt version
    # نترك filterMode على MatchContains لكن نعتمد أساساً على proxy filter
    completer.setFilterMode(Qt.MatchContains)

    # اربطه على lineEdit
    le.setCompleter(completer)

    # ---------------------------------------
    # Disconnect old handlers if exist
    # ---------------------------------------
    prev_text_handler = getattr(combo, "_clients_on_text_edited", None)
    if prev_text_handler:
        _safe_disconnect(le.textEdited, prev_text_handler)

    prev_press_handler = getattr(combo, "_clients_on_return", None)
    if prev_press_handler:
        _safe_disconnect(le.returnPressed, prev_press_handler)

    prev_activated_handler = getattr(combo, "_clients_on_activated", None)
    prev_completer = getattr(combo, "_clients_completer", None)
    if prev_completer and prev_activated_handler:
        try:
            prev_completer.activated[str].disconnect(prev_activated_handler)
        except Exception:
            pass

    # ---------------------------------------
    # Behavior: filter as user types + open popup
    # ---------------------------------------
    def on_text_edited(text: str):
        t = (text or "").strip()

        if not t:
            proxy.setFilterFixedString("")   # show all internally
            if completer.popup():
                completer.popup().hide()
            # optional: لو بغيت تفتح dropdown لكل العملاء عند الفراغ:
            # combo.showPopup()
            return

        # ✅ فلترة contains بطريقة مستقرة:
        # استخدم regexp contains مع escaping بسيط
        # (بدون regex خاص، لكن لو النص فيه رموز، نحتاج escaping)
        import re
        pattern = re.escape(t)
        # contains => .*pattern.*
        proxy.setFilterRegularExpression(f".*{pattern}.*")

        # افتح اقتراحات completer
        completer.setCompletionPrefix(t)
        completer.complete()

    # عند اختيار اقتراح
    def on_activated(value: str):
        combo.setCurrentText(value)
        # اختياري: إغلاق popup بعد الاختيار
        if completer.popup():
            completer.popup().hide()

    # Enter: إذا المستخدم ضغط Enter وما اختارش من القائمة
    # نختار أول اقتراح إن وجد (لتحسين UX)
    def on_return_pressed():
        current_text = (le.text() or "").strip()
        if not current_text:
            return

        # إذا allow_free_text=False نمنع قيم خارج القائمة
        if not allow_free_text:
            # تحقق من وجود الاسم في القائمة (case-insensitive)
            lookup = {n.casefold(): n for n in normalized_clients}
            if current_text.casefold() in lookup:
                combo.setCurrentText(lookup[current_text.casefold()])
            else:
                # امسح النص أو رجّعه للـ placeholder
                le.clear()
            return

        # allow_free_text=True:
        # لو فيه اقتراحات، اختار أول واحد إذا كان مطابق جزئيًا
        # (proxy rowCount > 0)
        if proxy.rowCount() > 0:
            first = proxy.index(0, 0).data()
            if isinstance(first, str) and first:
                combo.setCurrentText(first)

    # Connect
    le.textEdited.connect(on_text_edited)
    completer.activated[str].connect(on_activated)
    le.returnPressed.connect(on_return_pressed)

    # Store refs to avoid GC + for safe disconnect later
    combo._clients_base_model = base_model
    combo._clients_proxy = proxy
    combo._clients_completer = completer
    combo._clients_on_text_edited = on_text_edited
    combo._clients_on_activated = on_activated
    combo._clients_on_return = on_return_pressed

    combo.blockSignals(False)
    return base_model, completer


@with_db_session
def nouveau_doc_setup(nouveau_doc_window, session):
    result = nouveau_doc_window.doc_type_window.exec_()
    if result != QDialog.Accepted:
        return

    setup_doc_num_entry(nouveau_doc_window)
    
    setup_clients_combo(nouveau_doc_window.clients_combobox, session=session)
