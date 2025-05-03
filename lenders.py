class LenderManager:
    def __init__(self):
        # Dictionary mapping lenders to their required endorsements
        self.lender_endorsements = {
            "Bank of America": ["ALTA 8.1", "ALTA 9", "ALTA 6"],
            "Wells Fargo": ["ALTA 4", "ALTA 5", "ALTA 6"],
            "Chase": ["ALTA 8.1", "ALTA 9"],
	    "Banksouth": ["ALTA 8.1", "ALTA 9", "ALTA 4", "ALTA 5", "ALTA 6"],
            "": []  # Default for no lender selected
        }

    def get_lender_list(self):
        return list(self.lender_endorsements.keys())

    def get_lender_endorsements(self, lender):
        return self.lender_endorsements.get(lender, [])