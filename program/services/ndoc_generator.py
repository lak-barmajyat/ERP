from datetime import datetime
from sqlalchemy import select, update
from program.services import Counter, RefTypeDocument, Document, with_db_session


@with_db_session
def generate_document_number(code_type: str, session=None) -> str:
    """
    Return a document number without burning numbers:
    - keep current counter value if number is not used yet
    - increment only when that number already exists in documents
    """

    current_year = datetime.now().year

    type_obj = session.execute(
        select(RefTypeDocument).where(RefTypeDocument.code_type == code_type)
    ).scalar_one_or_none()

    if not type_obj:
        raise ValueError(f"Type document '{code_type}' not found")

    counter = session.execute(
        select(Counter)
        .where(
            Counter.id_counter == type_obj.id_type_document,  # fixed column
            Counter.annee == current_year,
        )
        .with_for_update()
    ).scalar_one_or_none()

    if not counter:
        counter = Counter(
            id_counter=type_obj.id_type_document,
            annee=current_year,
            valeur_courante=1,   # first candidate = 001
            longueur=3,
            prefixe=code_type,
            reset_annuel=True,
        )
        session.add(counter)
        session.flush()

    if counter.valeur_courante <= 0:
        counter.valeur_courante = 1

    while True:
        numero = f"{counter.prefixe}{str(counter.valeur_courante).zfill(counter.longueur)}"

        exists = session.execute(
            select(Document.id_document).where(
                Document.id_type_document == type_obj.id_type_document,
                Document.numero_document == numero,
            )
        ).scalar_one_or_none()

        if exists:
            counter.valeur_courante += 1
            continue

        return numero


@with_db_session
def reset_document_counter(code_type: str = None, year: int = None, session=None):
    """
    Reset counter for:
    - specific type (FA, DV...)
    - or all types if code_type=None
    - optional specific year (default: current year)
    """

    target_year = year or datetime.now().year

    if code_type:
        # جلب id_type_document
        type_obj = session.execute(
            select(RefTypeDocument).where(
                RefTypeDocument.code_type == code_type
            )
        ).scalar_one_or_none()

        if not type_obj:
            raise ValueError(f"Type document '{code_type}' not found")

        stmt = (
            update(Counter)
            .where(
                Counter.id_counter == type_obj.id_type_document,
                Counter.annee == target_year,
            )
            .values(valeur_courante=0)
        )
    else:
        # Reset all types
        stmt = (
            update(Counter)
            .where(Counter.annee == target_year)
            .values(valeur_courante=0)
        )

    session.execute(stmt)