import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from methods import ChecklistMethods
from save import ChecklistSave
from lenders import LenderManager
from pdf_export import PDFExporter

class ChecklistApp(ChecklistMethods, ChecklistSave):
    def __init__(self, root):
        self.root = root
        self.root.title("Title Policy Checklist")
        self.documents = []
        self.riders = []
        self.endorsements = []
        self.rider_section_visible = False
        self.standard_riders = [
            "PUD Rider", "Adjustable Rate Rider", "1-4 Family Rider",
            "Condominium Rider", "Second Home Rider", "Revocable Trust Rider",
            "MERS Rider", "Custom"
        ]
        self.common_endorsements = [
            "ALTA 8.1", "ALTA 9", "ALTA 4", "ALTA 5", "ALTA 6", "Custom"
        ]
        self.lender_manager = LenderManager()

        # File Number
        tk.Label(root, text="File Number").pack()
        self.file_number = tk.Entry(root, width=20)
        self.file_number.pack()

        # Progress Tracking
        self.progress_label = tk.Label(root, text="Progress: 0% Complete (0 fields remaining)")
        self.progress_label.pack()

        # Matter Folder Path
        tk.Label(root, text="Matter Folder Path").pack()
        self.path_var = tk.StringVar()
        tk.Entry(root, textvariable=self.path_var, width=50).pack()
        tk.Button(root, text="Browse", command=self.browse_folder).pack()

        # State
        tk.Label(root, text="State").pack()
        self.state = ttk.Combobox(root, values=["AL", "GA"], width=10)
        self.state.pack()
        self.state.bind("<<ComboboxSelected>>", self.update_form)

        # Deal Type
        tk.Label(root, text="Deal Type").pack()
        self.deal_type = ttk.Combobox(root, values=["Loan", "Refinance", "Cash", "Other"])
        self.deal_type.pack()
        self.deal_type.bind("<<ComboboxSelected>>", self.update_form)

        # Lender Selection
        tk.Label(root, text="Lender").pack()
        self.lender = ttk.Combobox(root, values=self.lender_manager.get_lender_list(), width=20)
        self.lender.pack()
        self.lender.bind("<<ComboboxSelected>>", lambda e: [self.update_lender_endorsements(), self.update_lender_2nd_position()])

        # 2nd Position Check (Radio Button)
        self.lender_2nd_frame = tk.Frame(root)
        tk.Label(self.lender_2nd_frame, text="2nd Position Loan?").pack(side=tk.LEFT)
        self.lender_2nd = tk.StringVar(value="No")
        tk.Radiobutton(self.lender_2nd_frame, text="Yes", value="Yes", variable=self.lender_2nd, command=lambda: [self.update_lender_2nd_position(), self.update_progress()]).pack(side=tk.LEFT)
        tk.Radiobutton(self.lender_2nd_frame, text="No", value="No", variable=self.lender_2nd, command=lambda: [self.update_lender_2nd_position(), self.update_progress()]).pack(side=tk.LEFT)

        self.lender_exceptions_frame = tk.Frame(self.lender_2nd_frame)
        self.lender_exceptions = tk.BooleanVar()
        tk.Checkbutton(self.lender_exceptions_frame, text="Reflected in Policy Exceptions", variable=self.lender_exceptions, command=self.update_progress).pack()

        # General Checks
        tk.Label(root, text="General Checks").pack()
        self.checks = {
            "title_search": tk.BooleanVar(),
            "signatures_verified": tk.BooleanVar(),
        }
        for check, var in self.checks.items():
            tk.Checkbutton(root, text=check.replace("_", " ").title(), variable=var, command=self.update_progress).pack()

        # Document Section
        tk.Label(root, text="Documents").pack()
        self.doc_frame = tk.Frame(root)
        self.doc_frame.pack()
        self.add_document_field()
        tk.Button(root, text="Add Document", command=self.add_document_field).pack()

        # Rider Section (initially hidden)
        self.rider_label = tk.Label(root, text="SD Riders")
        self.rider_frame = tk.Frame(root)
        self.add_rider_button = tk.Button(root, text="Add Rider", command=self.add_rider_field)

        # Title Endorsements Section
        tk.Label(root, text="Title Endorsements").pack()
        self.endorsement_frame = tk.Frame(root)
        self.endorsement_frame.pack()
        tk.Button(root, text="Add Endorsement", command=self.add_endorsement_field).pack()

        # Save Buttons
        tk.Button(root, text="Save to JSON", command=self.save_to_json).pack()
        tk.Button(root, text="Save to PDF", command=self.save_to_pdf).pack()

    def update_lender_endorsements(self):
        # Preserve manually added endorsements
        manual_endorsements = [e for e in self.endorsements if e["type"].get() not in self.lender_manager.get_lender_endorsements(self.lender.get())]

        # Clear existing endorsements
        for widget in self.endorsement_frame.winfo_children():
            widget.destroy()
        self.endorsements.clear()

        # Add lender-specific endorsements
        selected_lender = self.lender.get()
        if selected_lender:
            lender_endorsements = self.lender_manager.get_lender_endorsements(selected_lender)
            for endorsement in lender_endorsements:
                frame = tk.Frame(self.endorsement_frame)
                frame.pack(pady=5)
                e = {}
                e["frame"] = frame
                tk.Label(frame, text=endorsement).pack(side=tk.LEFT)
                e["type"] = tk.StringVar(value=endorsement)
                e["custom_name"] = tk.StringVar(value="")
                e["correct"] = tk.BooleanVar()
                tk.Checkbutton(frame, text="Correct", variable=e["correct"], command=self.update_progress).pack(side=tk.LEFT)
                tk.Button(frame, text="Remove", command=lambda f=e: self.remove_endorsement(f)).pack(side=tk.LEFT)
                self.endorsements.append(e)

        # Re-add manual endorsements
        for e in manual_endorsements:
            frame = tk.Frame(self.endorsement_frame)
            frame.pack(pady=5)
            new_e = {}
            new_e["frame"] = frame
            tk.Label(frame, text=e["type"].get()).pack(side=tk.LEFT)
            new_e["type"] = tk.StringVar(value=e["type"].get())
            new_e["custom_name"] = tk.StringVar(value=e["custom_name"].get())
            new_e["correct"] = tk.BooleanVar(value=e["correct"].get())
            tk.Checkbutton(frame, text="Correct", variable=new_e["correct"], command=self.update_progress).pack(side=tk.LEFT)
            tk.Button(frame, text="Remove", command=lambda f=new_e: self.remove_endorsement(f)).pack(side=tk.LEFT)
            self.endorsements.append(new_e)

        self.update_progress()

    def update_lender_2nd_position(self):
        if self.lender.get():
            self.lender_2nd_frame.pack()
            if self.lender_2nd.get() == "Yes":
                self.lender_exceptions_frame.pack()
            else:
                self.lender_exceptions_frame.pack_forget()
        else:
            self.lender_2nd_frame.pack_forget()
            self.lender_exceptions_frame.pack_forget()
        self.update_progress()

    def save_to_pdf(self):
        file_path = self.path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please specify a folder path.")
            return

        # Prepare data for PDF (similar to save_to_json)
        state = self.state.get()
        file_num = self.file_number.get().strip()
        if not file_num:
            messagebox.showerror("Error", "File number is required.")
            return

        # Validate required fields (same as save_to_json)
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

        for rider in self.riders:
            if rider["type"].get() == "Custom" and not rider["custom_name"].get():
                messagebox.showerror("Error", "Custom rider name required. Please correct and restart.")
                return
            if not rider["correct"].get():
                messagebox.showerror("Error", f"Rider {rider['type'].get()} must be verified. Please correct and restart.")
                return

        for endorsement in self.endorsements:
            if endorsement["type"].get() == "Custom" and not endorsement["custom_name"].get():
                messagebox.showerror("Error", "Custom endorsement name required. Please correct and restart.")
                return
            if not endorsement["correct"].get():
                messagebox.showerror("Error", f"Endorsement {endorsement['type'].get()} must be verified. Please correct and restart.")
                return

        if self.lender.get() and self.lender_2nd.get() == "Yes" and not self.lender_exceptions.get():
            messagebox.showerror("Error", "2nd position loan must be reflected in policy exceptions. Please correct and restart.")
            return

        # Prepare data for PDF
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
                        "ssn_redacted": doc["ssn_redacted"].get() if doc["type"].get() in ["POA", "Affidavit"] else False
                    }
                } for doc in self.documents
            ],
            "riders": [
                {
                    "type": rider["type"].get(),
                    "custom_name": rider["custom_name"].get() if rider["type"].get() == "Custom" else "",
                    "correct": rider["correct"].get(),
                    "cover_page_attached": rider["cover_page"].get() if self.state.get() == "GA" else False
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

        # Generate PDF
        pdf_path = file_path.replace(".json", ".pdf")
        exporter = PDFExporter(pdf_path)
        exporter.export(data)
        messagebox.showinfo("Success", f"Checklist saved to {pdf_path}")