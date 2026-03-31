from program.windows.liste_ventes.liste_ventes import PURCHASE_CONTEXT, DocumentsContext, SalesDocumentsWindow


class PurchaseDocumentsWindow(SalesDocumentsWindow):
    """Liste des documents d'achat (id_domaine = 2).

    This window reuses the same UI/logic as the sales list, but switches the
    context so data is filtered by the purchase domain and the UI shows
    "Fournisseur" instead of "Client".
    """

    def __init__(self, context: DocumentsContext | None = None) -> None:
        super().__init__(context=context or PURCHASE_CONTEXT)
