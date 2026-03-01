from datetime import datetime
from sqlalchemy import select, update
from program.services import Counter, RefTypeDocument, with_db_session


@with_db_session
def generate_document_number(code_type: str, session=None) -> str:
    """
    Generate next document number like FA001 safely.
    """

    current_year = datetime.now().year

    type_stmt = select(RefTypeDocument).where(
        RefTypeDocument.code_type == code_type
    )

    type_obj = session.execute(type_stmt).scalar_one_or_none()

    if not type_obj:
        raise ValueError(f"Type document '{code_type}' not found")

    counter_stmt = (
        select(Counter)
        .where(
            Counter.id_counter == type_obj.id_type_document,
            Counter.annee == current_year,
        )
        .with_for_update()
    )

    counter = session.execute(counter_stmt).scalar_one_or_none()

    if not counter:
        counter = Counter(
            id_type_document=type_obj.id_type_document,
            annee=current_year,
            valeur_courante=0,
            longueur=3,
            prefixe=code_type,
            reset_annuel=True,
        )
        session.add(counter)
        session.flush()

    counter.valeur_courante += 1

    formatted_number = str(counter.valeur_courante).zfill(counter.longueur)
    numero = f"{counter.prefixe}{formatted_number}"

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
                Counter.id_type_document == type_obj.id_type_document,
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