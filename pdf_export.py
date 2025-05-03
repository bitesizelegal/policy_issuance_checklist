from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

class PDFExporter:
    def __init__(self, filename):
        self.filename = filename
        self.doc = SimpleDocTemplate(filename, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.elements = []

        # Configuration for styles
        self.title_style = self.styles['Title']
        self.heading_style = self.styles['Heading2']
        self.body_style = ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12
        )
        self.table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

    def add_title(self, file_number):
        self.elements.append(Paragraph(f"Title Policy Checklist - File Number: {file_number}", self.title_style))
        self.elements.append(Spacer(1, 12))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
        self.elements.append(Spacer(1, 12))

    def add_section(self, title, data, headers):
        if data:
            self.elements.append(Paragraph(title, self.heading_style))
            self.elements.append(Spacer(1, 12))
            table_data = [headers] + data
            table = Table(table_data)
            table.setStyle(self.table_style)
            self.elements.append(table)
            self.elements.append(Spacer(1, 24))
            self.elements.append(HRFlowable(width="100%", thickness=1, color=colors.black))
            self.elements.append(Spacer(1, 12))

    def add_text(self, text):
        self.elements.append(Paragraph(text, self.body_style))
        self.elements.append(Spacer(1, 12))

    def export(self, data):
        # Extract data
        file_number = data["file_number"]
        state = data["state"]
        deal_type = data["deal_type"]
        lender = data["lender"]
        documents = data["documents"]
        riders = data["riders"]
        title_endorsements = data["title_endorsements"]
        second_position = data["second_position"]
        general_checks = data["general_checks"]
        timestamp = data["timestamp"]

        # Add title
        self.add_title(file_number)

        # Add basic info
        self.add_text(f"State: {state}")
        self.add_text(f"Deal Type: {deal_type}")
        self.add_text(f"Lender: {lender if lender else 'None'}")
        self.add_text(f"Timestamp: {timestamp}")

        # Documents
        doc_headers = [
            "Type", "Names Correct", "Signatures Present", "Correct Notary Block",
            "Legal Attached", "Exh B Attached", "Other Exhs Attached",
            "Exec Date Correct", "Rec Date Correct", "Book-Page Correct",
            "Rec Time Correct", "Tax Parcel Correct", "Marital Status Correct",
            "SSN Redacted", "Cover Page Attached"
        ]
        doc_data = []
        for doc in documents:
            doc_type = doc["type"]
            checks = doc["checks"]
            row = [
                doc_type,
                "Yes" if checks["names_correct"] else "No",
                "Yes" if checks["signatures_present"] else "No",
                "Yes" if checks["correct_notary_block"] else "No",
                "Yes" if checks["legal_attached"] else "No",
                "Yes" if checks["exhibit_b_attached"] else "N/A",
                "Yes" if checks["other_exhibits_attached"] else "N/A",
                "Yes" if checks["execution_date_correct"] else "No",
                "Yes" if checks["recording_date_correct"] else "No",
                "Yes" if checks["recording_book_page_correct"] else "No",
                "Yes" if checks["recording_date_time_correct"] else "No",
                "Yes" if checks["tax_parcel_number_correct"] else ("No" if state == "GA" and doc_type == "Deed" else "N/A"),
                "Yes" if checks["marital_status_correct"] else ("No" if state == "AL" and doc_type in ["Deed", "Mortgage"] else "N/A"),
                "Yes" if checks["ssn_redacted"] else ("No" if doc_type in ["POA", "Affidavit"] else "N/A"),
                "Yes" if checks["cover_page_attached"] else ("No" if state == "GA" and doc_type == "SD" else "N/A")
            ]
            doc_data.append(row)
        self.add_section("Documents", doc_data, doc_headers)

        # Riders
        rider_headers = ["Type", "Custom Name", "Correct"]
        rider_data = [
            [
                rider["type"],
                rider["custom_name"],
                "Yes" if rider["correct"] else "No"
            ] for rider in riders
        ]
        self.add_section("Riders", rider_data, rider_headers)

        # Title Endorsements
        endorsement_headers = ["Type", "Custom Name", "Correct"]
        endorsement_data = [
            [
                endorsement["type"],
                endorsement["custom_name"],
                "Yes" if endorsement["correct"] else "No"
            ] for endorsement in title_endorsements
        ]
        self.add_section("Title Endorsements", endorsement_data, endorsement_headers)

        # Second Position Check
        second_position_headers = ["Second Position", "Reflected in Policy Exceptions"]
        second_position_data = [[
            "Yes" if second_position["is_second_position"] else "No",
            "Yes" if second_position["reflected_in_policy_exceptions"] else ("No" if second_position["is_second_position"] else "N/A")
        ]]
        self.add_section("Second Position Check", second_position_data, second_position_headers)

        # General Checks
        general_headers = ["Check", "Status"]
        general_data = [
            [key.replace("_", " ").title(), "Yes" if value else "No"]
            for key, value in general_checks.items()
        ]
        self.add_section("General Checks", general_data, general_headers)

        # Build the PDF
        self.doc.build(self.elements)
