"""
PDF Generator Script for PropValue AI Comprehensive Documentation.
Uses ReportLab to produce a clean, professional multi-page project report.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "PropValue_AI_Project_Documentation.pdf")

class NumberedCanvas(canvas.Canvas):
    """Custom canvas that computes total page count dynamically."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#757684"))

        # Suppress headers/footers on page 1 (cover)
        if self._pageNumber > 1:
            # Header
            self.drawString(54, 11 * inch - 36, "PropValue AI — System Architecture & Technical Specification")
            self.setStrokeColor(colors.HexColor("#c4c5d5"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(8.5 * inch - 54, 36, page_text)
            self.drawString(54, 36, "PropValue AI Technical Report • Author: Prabhat Dubey")
            self.line(54, 46, 8.5 * inch - 54, 46)

        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Palette
    COLOR_PRIMARY = colors.HexColor("#00288e")
    COLOR_SECONDARY = colors.HexColor("#006a61")
    COLOR_DARK = colors.HexColor("#131b2e")
    COLOR_MUTED = colors.HexColor("#444653")
    COLOR_BG_LIGHT = colors.HexColor("#f2f3ff")
    COLOR_ACCENT = colors.HexColor("#ffa929")
    COLOR_BORDER = colors.HexColor("#c4c5d5")

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=COLOR_PRIMARY,
        spaceAfter=8
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=COLOR_SECONDARY,
        spaceAfter=18
    )
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=COLOR_MUTED
    )
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=COLOR_SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=COLOR_DARK,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=COLOR_DARK,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )
    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=COLOR_DARK
    )
    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )
    code_box = ParagraphStyle(
        'CodeBox',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=COLOR_PRIMARY,
        backColor=COLOR_BG_LIGHT,
        borderPadding=6,
        spaceAfter=6
    )

    story = []

    # ==================== COVER SECTION ====================
    story.append(Spacer(1, 15))
    story.append(Paragraph("PROPVALUE AI", ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=10, textColor=COLOR_SECONDARY, spaceAfter=4)))
    story.append(Paragraph("Real Estate Valuation & Financial Analytics Platform", title_style))
    story.append(Paragraph("Technical Architecture, Machine Learning Pipeline, UI Design System, and REST API Specification", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_PRIMARY, spaceBefore=4, spaceAfter=14))

    meta_text = """
    <b>Author:</b> Prabhat Dubey<br/>
    <b>Version:</b> 1.0 (Scikit-Learn Pipeline & FastAPI Backend)<br/>
    <b>Frontend:</b> Modern Web UI (Inter & JetBrains Mono design tokens)<br/>
    <b>Security:</b> JWT Session Authentication & PBKDF2 Password Hashing (SQLite)<br/>
    <b>Document Date:</b> August 2026 • Technical Report
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 12))

    # Executive Overview Box
    exec_summary_html = """
    <b>Overview:</b> PropValue AI is a real estate valuation and property analytics web platform. It integrates a Scikit-Learn regression pipeline (Random Forest regressor with 98.0% R² on test data), an asynchronous FastAPI backend service (<15ms latency), a responsive modern web interface, seven core valuation and investment tools (What-If sensitivity modeling, mortgage amortization & rental yield analysis, geospatial Leaflet.js mapping, multi-property comparison, vectorized bulk CSV valuations, and NLP listing parser), and a secure JWT/SQLite user authentication system.
    """
    exec_table = Table([[Paragraph(exec_summary_html, body_style)]], colWidths=[504])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, COLOR_PRIMARY),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 11),
        ('RIGHTPADDING', (0, 0), (-1, -1), 11),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 14))

    # ==================== SECTION 1: SYSTEM ARCHITECTURE ====================
    story.append(Paragraph("1. System Architecture", h1_style))
    story.append(Paragraph(
        "PropValue AI is organized into modular layers spanning data management, model training, FastAPI service endpoints, and a Single Page Application (SPA) client interface.",
        body_style
    ))

    arch_data = [
        [Paragraph("Tier", table_header), Paragraph("Component", table_header), Paragraph("Technologies & Responsibilities", table_header)],
        [Paragraph("<b>Presentation Tier</b>", table_cell), Paragraph("Modern Web Frontend", table_cell), Paragraph("Single Page Application (SPA) built with clean design tokens, Tailwind CSS, Chart.js for 5-year projections, Leaflet.js for interactive maps, and print stylesheets for PDF valuation reports.", table_cell)],
        [Paragraph("<b>Application Tier</b>", table_cell), Paragraph("FastAPI REST Service", table_cell), Paragraph("Asynchronous Python backend handling valuation routing, What-If perturbation deltas, mortgage calculations, NLP listing parsing, CSV batch processing, and CORS management.", table_cell)],
        [Paragraph("<b>Machine Learning</b>", table_cell), Paragraph("Scikit-Learn Pipeline", table_cell), Paragraph("ColumnTransformer preprocessor with SimpleImputer, StandardScaler, and OneHotEncoder paired with an optimized RandomForestRegressor. Serialized via Joblib.", table_cell)],
        [Paragraph("<b>Security & Storage</b>", table_cell), Paragraph("SQLite + JWT Auth", table_cell), Paragraph("Zero-dependency PBKDF2-SHA256 password hashing (100k iterations), HMAC-SHA256 signed JWT session tokens, and SQLite database for users and saved property portfolios.", table_cell)],
    ]
    t_arch = Table(arch_data, colWidths=[110, 124, 270])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG_LIGHT]),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 14))

    # ==================== SECTION 2: MACHINE LEARNING PIPELINE ====================
    story.append(Paragraph("2. Machine Learning Pipeline & Model Performance", h1_style))
    story.append(Paragraph(
        "The valuation engine is trained on a 6,000-sample housing dataset spanning 12 US metropolitan regions. The data pipeline handles continuous and categorical features with strict train-test separation to avoid data leakage.",
        body_style
    ))

    story.append(Paragraph("Feature Representation & Preprocessing:", h2_style))
    story.append(Paragraph("• <b>Numerical Features:</b> <code>square_footage</code>, <code>bedrooms</code>, <code>bathrooms</code>, <code>year_built</code>, <code>lot_size_acres</code>, <code>garage_spaces</code>. Processed through median imputation followed by z-score standardization (<code>StandardScaler</code>).", bullet_style))
    story.append(Paragraph("• <b>Categorical Features:</b> <code>zip_code</code> (12 metros), <code>property_type</code> (Single Family, Condo, Townhouse, Multi-Family), <code>renovation_status</code> (None, Minor, Major, Full Gut Rehab). Processed through most-frequent imputation and <code>OneHotEncoder(handle_unknown='ignore')</code>.", bullet_style))

    story.append(Spacer(1, 4))
    story.append(Paragraph("Evaluation Metrics:", h2_style))

    metrics_data = [
        [Paragraph("Metric", table_header), Paragraph("Formula / Description", table_header), Paragraph("Test Score", table_header), Paragraph("Status", table_header)],
        [Paragraph("<b>Coefficient of Determination (R²)</b>", table_cell), Paragraph("Proportion of variance explained by model", table_cell), Paragraph("<b>0.9799 (98.0%)</b>", table_cell), Paragraph("Strong Fit", table_cell)],
        [Paragraph("<b>Mean Absolute Error (MAE)</b>", table_cell), Paragraph("Average absolute dollar deviation", table_cell), Paragraph("<b>$67,836.70</b>", table_cell), Paragraph("High Precision", table_cell)],
        [Paragraph("<b>Root Mean Squared Error (RMSE)</b>", table_cell), Paragraph("Square root of mean squared error", table_cell), Paragraph("<b>$104,064.56</b>", table_cell), Paragraph("Robust", table_cell)],
        [Paragraph("<b>Mean Absolute Percentage Error (MAPE)</b>", table_cell), Paragraph("Percentage error relative to actual valuation", table_cell), Paragraph("<b>6.08%</b>", table_cell), Paragraph("High Accuracy", table_cell)],
        [Paragraph("<b>Inference Latency</b>", table_cell), Paragraph("End-to-end REST API execution time", table_cell), Paragraph("<b>< 15 ms</b>", table_cell), Paragraph("Real-Time", table_cell)],
    ]
    t_metrics = Table(metrics_data, colWidths=[140, 174, 95, 95])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_SECONDARY),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG_LIGHT]),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 14))

    # ==================== SECTION 3: CORE APPLICATION FEATURES ====================
    story.append(Paragraph("3. Core Application Features", h1_style))
    story.append(Paragraph(
        "PropValue AI includes seven core modules designed for comprehensive property valuation and investment analysis:",
        body_style
    ))

    features = [
        ("1. What-If Sensitivity Simulator", "Provides interactive sliders for square footage, bedroom/bathroom counts, and garage capacity with renovation toggles. Calls <code>POST /predict-whatif</code> to dynamically calculate marginal value differences ($Δ) and feature contributions."),
        ("2. Mortgage & Investor ROI Calculator", "Computes comprehensive loan amortization schedules (Principal & Interest, Property Taxes, Home Insurance, and HOA fees). Renders an interactive Chart.js Donut chart alongside investor metrics: Gross Rental Yield %, Net Cap Rate %, and 10-Year Projected Cash-on-Cash Return."),
        ("3. Geospatial Mapping & Amenity Scoring", "Integrates Leaflet.js with OpenStreetMap to map the Subject Property and nearby Comparables with custom pins and popups. Calculates Walk Score (0-100), Transit Score (0-100), School District Rating (0-10), and Price Density ($/sqft)."),
        ("4. Side-by-Side Property Comparison", "Side-by-side comparison table supporting 2 to 4 saved property valuations simultaneously. Compares price, price/sqft, living area, bed/bath ratio, confidence, and 5-year projected appreciation."),
        ("5. Property Valuation Report (PDF / Print)", "Generates a clean property valuation summary formatted with property specifications, comparable sales table, valuation range, and analyst notes. Styled for 1-click printing and PDF download via <code>@media print</code>."),
        ("6. Bulk CSV Valuation Engine", "Allows users to upload batches of properties via CSV. Runs vectorized Scikit-Learn pipeline predictions and displays an interactive preview table with an 'Export Enriched CSV' download option."),
        ("7. Listing Description Parser (NLP)", "Enables users to paste raw listing descriptions into a text input. A pattern parser extracts ZIP code, living area, beds, baths, build year, and renovation condition, auto-filling the valuation form.")
    ]

    for f_title, f_desc in features:
        story.append(Paragraph(f"<b>{f_title}</b>", h2_style))
        story.append(Paragraph(f_desc, body_style))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 10))

    # ==================== SECTION 4: UI/UX DESIGN SYSTEM ====================
    story.append(Paragraph("4. UI/UX Design System", h1_style))
    story.append(Paragraph(
        "The frontend follows a clean, modern design system documented in <code>DESIGN.md</code>:",
        body_style
    ))

    story.append(Paragraph("• <b>Color Palette:</b> Deep Navy (<code>primary: #00288e</code>), Emerald Teal (<code>secondary: #006a61</code>), Warm Amber (<code>tertiary: #ffa929</code>), and Soft Neutral Surfaces (<code>surface: #faf8ff</code>).", bullet_style))
    story.append(Paragraph("• <b>Typography:</b> Dual-font hierarchy using Google Fonts <code>Inter</code> for interface labels and headings, paired with <code>JetBrains Mono</code> for financial numbers, dollar amounts, and metrics.", bullet_style))
    story.append(Paragraph("• <b>Modular Layout:</b> Structured cards grouping inputs, real-time calculations, maps, and charts into an organized workspace.", bullet_style))
    story.append(Paragraph("• <b>Modals & Drawers:</b> Slide-out navigation drawer for mobile viewports and clean modals for user authentication, saved properties, and ML model details.", bullet_style))

    story.append(Spacer(1, 12))

    # ==================== SECTION 5: AUTHENTICATION & DATA PERSISTENCE ====================
    story.append(Paragraph("5. User Authentication & Data Persistence", h1_style))
    story.append(Paragraph(
        "PropValue AI includes a lightweight authentication system built with standard Python libraries:",
        body_style
    ))

    auth_data = [
        [Paragraph("Feature", table_header), Paragraph("Implementation Details", table_header)],
        [Paragraph("<b>Password Security</b>", table_cell), Paragraph("<code>PBKDF2-SHA256</code> password hashing with 100,000 iterations and per-user unique 16-byte cryptographic salts. Passwords are never stored in plain text.", table_cell)],
        [Paragraph("<b>Session Tokens</b>", table_cell), Paragraph("<code>HMAC-SHA256</code> signed JSON Web Tokens (JWT) with 7-day expiration. Verified on protected routes via <code>Authorization: Bearer &lt;token&gt;</code> headers.", table_cell)],
        [Paragraph("<b>Database Storage</b>", table_cell), Paragraph("SQLite database (<code>backend/data/users.db</code>) with foreign key constraints, cascading deletions, and indexed lookups for user accounts and saved valuations.", table_cell)],
        [Paragraph("<b>Report Personalization</b>", table_cell), Paragraph("When authenticated, the printable Valuation Report automatically displays the logged-in user's name, title, and organization.", table_cell)],
        [Paragraph("<b>Guest Access</b>", table_cell), Paragraph("Users can immediately calculate property valuations without signing in, with optional 1-click demo login (<code>prabhat@propvalue.ai</code>).", table_cell)],
    ]
    t_auth = Table(auth_data, colWidths=[150, 354])
    t_auth.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG_LIGHT]),
    ]))
    story.append(t_auth)
    story.append(Spacer(1, 14))

    # ==================== SECTION 6: REST API SPECIFICATION ====================
    story.append(Paragraph("6. REST API Endpoints", h1_style))
    story.append(Paragraph("The FastAPI backend provides 10 REST endpoints:", body_style))

    api_data = [
        [Paragraph("Method", table_header), Paragraph("Endpoint", table_header), Paragraph("Purpose / Description", table_header)],
        [Paragraph("<code>GET</code>", table_cell), Paragraph("<code>/health</code>", table_cell), Paragraph("Health check & active model metadata ($R^2$, version).", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/predict</code>", table_cell), Paragraph("Single property valuation, error range, comps, & amenity scores.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/predict-whatif</code>", table_cell), Paragraph("Simulates marginal price delta ($Δ) and feature drivers.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/mortgage-calc</code>", table_cell), Paragraph("Calculates PITI monthly breakdown, rental yield, and cap rate.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/predict-batch</code>", table_cell), Paragraph("Vectorized multi-row CSV upload valuation engine.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/parse-listing</code>", table_cell), Paragraph("Listing parser extracting structured fields from raw text.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/auth/register</code>", table_cell), Paragraph("Creates a new user account and issues a signed JWT.", table_cell)],
        [Paragraph("<code>POST</code>", table_cell), Paragraph("<code>/auth/login</code>", table_cell), Paragraph("Authenticates credentials and returns user profile + JWT.", table_cell)],
        [Paragraph("<code>GET</code>", table_cell), Paragraph("<code>/auth/me</code>", table_cell), Paragraph("Validates active JWT token session.", table_cell)],
        [Paragraph("<code>GET/POST</code>", table_cell), Paragraph("<code>/auth/saved</code>", table_cell), Paragraph("Manages saved valuation portfolios.", table_cell)],
    ]
    t_api = Table(api_data, colWidths=[55, 140, 309])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_SECONDARY),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, COLOR_BG_LIGHT]),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 14))

    # ==================== SECTION 7: HOW TO RUN & VERIFY ====================
    story.append(Paragraph("7. Getting Started & Testing", h1_style))
    story.append(Paragraph(
        "Application features and endpoints are covered by automated tests in <code>test_e2e.py</code>. The suite tests endpoint health, regression inference, What-If deltas, mortgage amortization, listing parsing, CSV batch processing, and JWT authentication flows.",
        body_style
    ))

    story.append(Paragraph("Commands to Run & Verify:", h2_style))
    quickstart_code = """# 1. Install Dependencies
pip install -r backend/requirements.txt

# 2. Train Model Pipeline (generates backend/model/model.joblib)
python backend/train.py

# 3. Start FastAPI Server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload

# 4. Execute Automated End-to-End Tests
python test_e2e.py"""
    story.append(Paragraph(quickstart_code.replace('\n', '<br/>'), code_box))
    story.append(Spacer(1, 10))

    # Signoff Block
    signoff_text = """
    <b>Project Status:</b> Ready (All Tests Passing)<br/>
    <b>Access URL:</b> <a href="http://127.0.0.1:8001" color="#00288e">http://127.0.0.1:8001</a><br/>
    <b>Author:</b> Prabhat Dubey
    """
    story.append(Paragraph(signoff_text, meta_style))

    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF generated at: {PDF_OUTPUT_PATH}")

if __name__ == "__main__":
    build_pdf()
