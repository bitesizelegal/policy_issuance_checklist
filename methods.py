import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ChecklistMethods:
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            file_num = self.file_number.get().strip()
            if not file_num:
                messagebox.showerror("Error", "Please enter a file number.")
                return
            self.path_var.set(f"{folder}/{file_num}_checklist.json")

    def update_form(self, event=None):
        deal = self.deal_type.get()
        if deal == "Refinance" and self.documents:
            self.documents[0]["type"].set("Mortgage")
        elif deal == "Cash" and self.documents:
            self.documents[0]["type"].set("Deed")
        self.update_document_fields()
        self.update_rider_fields()
        self.update_endorsement_fields()

        # Conditionally show/hide SD Riders section
        deal_type_condition = deal in ["Loan", "Refinance"]
        doc_type_condition = any(doc["type"].get() in ["Mortgage", "SD"] for doc in self.documents)
        should_show_riders = deal_type_condition or doc_type_condition

        if should_show_riders and not self.rider_section_visible:
            self.rider_label.pack()
            self.rider_frame.pack()
            self.add_rider_button.pack()
            self.rider_section_visible = True
        elif not should_show_riders and self.rider_section_visible:
            self.rider_label.pack_forget()
            self.rider_frame.pack_forget()
            self.add_rider_button.pack_forget()
            self.rider_section_visible = False

        self.update_progress()

    def update_progress(self):
        state = self.state.get()
        total_fields = 0
        checked_fields = 0

        # Document Checkboxes
        for doc in self.documents:
            doc_type = doc["type"].get()
            # Mandatory fields for all document types
            mandatory_fields = [
                doc["names_correct"],
                doc["signatures_present"],
                doc["correct_notary_block"],
                doc["legal_attached"],
                doc["execution_date_correct"],
                doc["recording_date_correct"],
                doc["recording_book_page_correct"],
                doc["recording_date_time_correct"]
            ]

            # Conditional mandatory fields
            if state == "GA" and doc_type == "Deed":
                mandatory_fields.append(doc["tax_parcel_number_correct"])
            if state == "AL" and doc_type in ["Deed", "Mortgage"]:
                mandatory_fields.append(doc["marital_status_correct"])
            if doc_type in ["POA", "Affidavit"]:
                mandatory_fields.append(doc["ssn_redacted"])

            # Count mandatory fields
            total_fields += len(mandatory_fields)
            checked_fields += sum(1 for field in mandatory_fields if field.get())

            # Non-mandatory fields (Exhibit B, Other Exhibits) - count only if checked
            non_mandatory_fields = [
                doc["exhibit_b_attached"],
                doc["other_exhibits_attached"]
            ]
            for field in non_mandatory_fields:
                if field.get():  # Only count if the user has checked it (indicating it applies)
                    total_fields += 1
                    checked_fields += 1

        # Riders Checkboxes
        for rider in self.riders:
            total_fields += 1  # "Correct" is mandatory
            if rider["correct"].get():
                checked_fields += 1
            if state == "GA":
                total_fields += 1  # "Cover Page" is mandatory in GA
                if rider["cover_page"].get():
                    checked_fields += 1

        # Endorsements Checkboxes
        for endorsement in self.endorsements:
            total_fields += 1  # "Correct" is mandatory
            if endorsement["correct"].get():
                checked_fields += 1

        # Lender 2nd Position Check
        if self.lender.get():
            total_fields += 1  # "2nd Position" radio button (always counts as it's a required choice)
            checked_fields += 1  # Always checked since radio buttons enforce a selection
            if self.lender_2nd.get() == "Yes":
                total_fields += 1  # "Reflected in Policy Exceptions" is mandatory if "Yes"
                if self.lender_exceptions.get():
                    checked_fields += 1

        # General Checkboxes
        total_fields += len(self.checks)
        checked_fields += sum(1 for var in self.checks.values() if var.get())

        # Calculate progress
        remaining_fields = total_fields - checked_fields
        percentage_complete = (checked_fields / total_fields * 100) if total_fields > 0 else 0
        self.progress_label.config(text=f"Progress: {percentage_complete:.1f}% Complete ({remaining_fields} fields remaining)")

    def update_document_fields(self):
        state = self.state.get()
        for doc in self.documents:
            doc_type = doc["type"].get()
            if state == "GA" and doc_type == "Deed":
                doc["tax_parcel_frame"].pack(side=tk.LEFT)
            else:
                doc["tax_parcel_frame"].pack_forget()
            if state == "AL" and doc_type in ["Deed", "Mortgage"]:
                doc["marital_frame"].pack(side=tk.LEFT)
            else:
                doc["marital_frame"].pack_forget()
            if doc_type in ["POA", "Affidavit"]:
                doc["ssn_frame"].pack(side=tk.LEFT)
            else:
                doc["ssn_frame"].pack_forget()

    def update_rider_fields(self):
        state = self.state.get()
        for rider in self.riders:
            rider_type = rider["type"].get()
            if rider_type == "Custom":
                rider["custom_frame"].pack(side=tk.LEFT)
            else:
                rider["custom_frame"].pack_forget()
            if state == "GA":
                rider["cover_frame"].pack(side=tk.LEFT)
            else:
                rider["cover_frame"].pack_forget()

    def update_endorsement_fields(self):
        state = self.state.get()
        for endorsement in self.endorsements:
            endorsement_type = endorsement["type"].get()
            if endorsement_type == "Custom":
                endorsement["custom_frame"].pack(side=tk.LEFT)
            else:
                endorsement["custom_frame"].pack_forget()
            if state == "GA" and endorsement_type == "GA Usury":
                endorsement["frame"].pack()
            elif state != "GA" and endorsement_type == "GA Usury":
                endorsement["frame"].pack_forget()

    def add_document_field(self):
        frame = tk.Frame(self.doc_frame)
        frame.pack(pady=5)
        doc = {}

        tk.Label(frame, text="Type").pack(side=tk.LEFT)
        doc["type"] = ttk.Combobox(frame, values=["Deed", "Mortgage", "SD", "Affidavit", "POA", "Notice"], width=15)
        doc["type"].pack(side=tk.LEFT)
        doc["type"].bind("<<ComboboxSelected>>", lambda e: self.update_form())

        tk.Label(frame, text="Names").pack(side=tk.LEFT)
        doc["names_correct"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Correct", variable=doc["names_correct"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Sigs").pack(side=tk.LEFT)
        doc["signatures_present"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Present", variable=doc["signatures_present"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Notary").pack(side=tk.LEFT)
        doc["correct_notary_block"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Correct", variable=doc["correct_notary_block"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Legal").pack(side=tk.LEFT)
        doc["legal_attached"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Attached", variable=doc["legal_attached"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Exh B").pack(side=tk.LEFT)
        doc["exhibit_b_attached"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Attached", variable=doc["exhibit_b_attached"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Other Exhs").pack(side=tk.LEFT)
        doc["other_exhibits_attached"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Attached", variable=doc["other_exhibits_attached"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Exec Date").pack(side=tk.LEFT)
        doc["execution_date_correct"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Correct", variable=doc["execution_date_correct"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Rec Date").pack(side=tk.LEFT)
        doc["recording_date_correct"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Correct", variable=doc["recording_date_correct"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Book-Page").pack(side=tk.LEFT)
        doc["recording_book_page_correct"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Correct", variable=doc["recording_book_page_correct"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Label(frame, text="Rec Time").pack(side=tk.LEFT)
        doc["recording_date_time_correct"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Correct", variable=doc["recording_date_time_correct"], command=self.update_progress).pack(side=tk.LEFT)

        doc["tax_parcel_frame"] = tk.Frame(frame)
        tk.Label(doc["tax_parcel_frame"], text="Tax Parcel").pack(side=tk.LEFT)
        doc["tax_parcel_number_correct"] = tk.BooleanVar()
        tk.Checkbutton(doc["tax_parcel_frame"], text="Correct", variable=doc["tax_parcel_number_correct"], command=self.update_progress).pack(side=tk.LEFT)

        doc["marital_frame"] = tk.Frame(frame)
        tk.Label(doc["marital_frame"], text="Marital Status").pack(side=tk.LEFT)
        doc["marital_status_correct"] = tk.BooleanVar()
        tk.Checkbutton(doc["marital_frame"], text="Correct", variable=doc["marital_status_correct"], command=self.update_progress).pack(side=tk.LEFT)

        doc["ssn_frame"] = tk.Frame(frame)
        tk.Label(doc["ssn_frame"], text="SSN Redacted").pack(side=tk.LEFT)
        doc["ssn_redacted"] = tk.BooleanVar()
        tk.Checkbutton(doc["ssn_frame"], variable=doc["ssn_redacted"], command=self.update_progress).pack(side=tk.LEFT)

        doc["frame"] = frame
        tk.Button(frame, text="Remove", command=lambda d=doc: self.remove_document(d)).pack(side=tk.LEFT)

        self.documents.append(doc)
        self.update_form()

    def remove_document(self, doc):
        self.documents.remove(doc)
        doc["frame"].destroy()
        self.update_form()

    def add_rider_field(self):
        if len(self.riders) < 5:
            frame = tk.Frame(self.rider_frame)
            frame.pack(pady=5)
            rider = {}

            tk.Label(frame, text="Rider").pack(side=tk.LEFT)
            rider["type"] = ttk.Combobox(frame, values=self.standard_riders, width=20)
            rider["type"].pack(side=tk.LEFT)
            rider["type"].bind("<<ComboboxSelected>>", lambda e: self.update_rider_fields())

            rider["custom_frame"] = tk.Frame(frame)
            tk.Label(rider["custom_frame"], text="Custom Name").pack(side=tk.LEFT)
            rider["custom_name"] = tk.Entry(rider["custom_frame"], width=20)
            rider["custom_name"].pack(side=tk.LEFT)

            tk.Label(frame, text="Rider").pack(side=tk.LEFT)
            rider["correct"] = tk.BooleanVar()
            tk.Checkbutton(frame, text="Correct", variable=rider["correct"], command=self.update_progress).pack(side=tk.LEFT)

            rider["cover_frame"] = tk.Frame(frame)
            rider["cover_page"] = tk.BooleanVar()
            tk.Checkbutton(rider["cover_frame"], text="Cover Page Attached", variable=rider["cover_page"], command=self.update_progress).pack(side=tk.LEFT)

            self.riders.append(rider)
            self.update_rider_fields()
            self.update_progress()
        else:
            messagebox.showwarning("Limit Reached", "Maximum 5 riders allowed.")

    def add_endorsement_field(self):
        frame = tk.Frame(self.endorsement_frame)
        frame.pack(pady=5)
        endorsement = {}
        endorsement["frame"] = frame

        tk.Label(frame, text="Endorsement").pack(side=tk.LEFT)
        endorsement["type"] = ttk.Combobox(frame, values=self.common_endorsements + ["GA Usury"], width=20)
        endorsement["type"].pack(side=tk.LEFT)
        endorsement["type"].bind("<<ComboboxSelected>>", lambda e: self.update_endorsement_fields())

        endorsement["custom_frame"] = tk.Frame(frame)
        tk.Label(endorsement["custom_frame"], text="Custom Name").pack(side=tk.LEFT)
        endorsement["custom_name"] = tk.Entry(endorsement["custom_frame"], width=20)
        endorsement["custom_name"].pack(side=tk.LEFT)

        endorsement["correct"] = tk.BooleanVar()
        tk.Checkbutton(frame, text="Correct", variable=endorsement["correct"], command=self.update_progress).pack(side=tk.LEFT)

        tk.Button(frame, text="Remove", command=lambda e=endorsement: self.remove_endorsement(e)).pack(side=tk.LEFT)

        self.endorsements.append(endorsement)
        self.update_endorsement_fields()
        self.update_progress()

    def remove_endorsement(self, endorsement):
        self.endorsements.remove(endorsement)
        endorsement["frame"].destroy()
        self.update_progress()