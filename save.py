import json
from datetime import datetime
import os
from tkinter import messagebox

class ChecklistSave:
    def save_to_json(self):
        file_path = self.path_var.get()
        if not file_path.endswith(".json"):
            messagebox.showerror("Error", "Please specify a valid JSON file path.")
            return

        state = self.state.get()
        file_num = self.file_number.get().strip()
        if not file_num:
            messagebox.showerror("Error", "File number is required.")
            return

        # Validate required fields
        for doc in self.documents:
            doc_type = doc["type"].get()
            if not doc["names_correct"].get():
                messagebox.showerror("Error", f"Names must be verified for {doc_type}. Please correct and restart.")
                return
            if state == "GA" and doc_type == "Deed" and not doc["tax_parcel_number_correct"].get():
                messagebox.showerror("Error", "Tax Parcel Number must be verified for GA Deeds. Please correct and restart.")
                return
            if state == "AL" and doc_type in ["Deed", "Mortgage"] and not doc["marital_status_correct"].get():
                messagebox.showerror("Error", f"Marital Status must be verified for AL {doc_type}. Please correct and restart.")
                return
            if doc_type in ["POA", "Affidavit"] and not doc["ssn_redacted"].get():
                messagebox.showerror("Error", f"SSN Redaction required for {doc_type}. Please correct and restart.")
                return
            if state == "GA" and doc_type == "SD" and not doc["cover_page_attached"].get():
                messagebox.showerror("Error", f"Cover Page must be attached for GA Security Deeds. Please correct and restart.")
                return

        # Validate riders
        for rider in self.riders:
            if rider["type"].get() == "Custom" and not rider["custom_name"].get():
                messagebox.showerror("Error", "Custom rider name required. Please correct and restart.")
                return
            if not rider["correct"].get():
                messagebox.showerror("Error", f"Rider {rider['type'].get()} must be verified. Please correct and restart.")
                return

        # Validate endorsements
        for endorsement in self.endorsements:
            if endorsement["type"].get() == "Custom" and not endorsement["custom_name"].get():
                messagebox.showerror("Error", "Custom endorsement name required. Please correct and restart.")
                return
            if not endorsement["correct"].get():
                messagebox.showerror("Error", f"Endorsement {endorsement['type'].get()} must be verified. Please correct and restart.")
                return

        # Validate 2nd Position for Lender
        if self.lender.get() and self.lender_2nd.get() == "Yes" and not self.lender_exceptions.get():
            messagebox.showerror("Error", "2nd position loan must be reflected in policy exceptions. Please correct and restart.")
            return

        # Prepare data
        data = {
            "file_number": file_num,
            "state": state,
            "deal_type": self.deal_type.get(),
            "lender": self.lender.get(),
            "documents": [
                {
                    "type": doc["type"].get(),
                    "checks": {
                        "names_correct": doc["names_correct"].get(),
                        "signatures_present": doc["signatures_present"].get(),
                        "correct_notary_block": doc["correct_notary_block"].get(),
                        "legal_attached": doc["legal_attached"].get(),
                        "exhibit_b_attached": doc["exhibit_b_attached"].get(),
                        "other_exhibits_attached": doc["other_exhibits_attached"].get(),
                        "execution_date_correct": doc["execution_date_correct"].get(),
                        "recording_date_correct": doc["recording_date_correct"].get(),
                        "recording_book_page_correct": doc["recording_book_page_correct"].get(),
                        "recording_date_time_correct": doc["recording_date_time_correct"].get(),
                        "tax_parcel_number_correct": doc["tax_parcel_number_correct"].get() if doc["type"].get() == "Deed" and state == "GA" else True,
                        "marital_status_correct": doc["marital_status_correct"].get() if doc["type"].get() in ["Deed", "Mortgage"] and state == "AL" else True,
                        "ssn_redacted": doc["ssn_redacted"].get() if doc["type"].get() in ["POA", "Affidavit"] else False,
                        "cover_page_attached": doc["cover_page_attached"].get() if doc["type"].get() == "SD" and state == "GA" else False
                    }
                } for doc in self.documents
            ],
            "riders": [
                {
                    "type": rider["type"].get(),
                    "custom_name": rider["custom_name"].get() if rider["type"].get() == "Custom" else "",
                    "correct": rider["correct"].get(),
                } for rider in self.riders
            ],
            "title_endorsements": [
                {
                    "type": endorsement["type"].get(),
                    "custom_name": endorsement["custom_name"].get() if endorsement["type"].get() == "Custom" else "",
                    "correct": endorsement["correct"].get()
                } for endorsement in self.endorsements
            ],
            "second_position": {
                "is_second_position": self.lender_2nd.get() == "Yes",
                "reflected_in_policy_exceptions": self.lender_exceptions.get() if self.lender_2nd.get() == "Yes" else False
            },
            "general_checks": {check: var.get() for check, var in self.checks.items()},
            "timestamp": str(datetime.now())
        }

        # Save to JSON
        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", f"Checklist saved to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
