import io
import os
import datetime
import locale
import threading
from zipfile import ZipFile
from pathlib import Path

from docxtpl import DocxTemplate
from nicegui import ui

from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Set Romanian locale for formatting
locale.setlocale(locale.LC_ALL, 'ro_RO')

# --------------------------
# Database Configuration
# --------------------------
DB_PATH = 'nicegui_company_data.db'
Base = declarative_base()

def get_engine():
    return create_engine(f'sqlite:///{DB_PATH}', connect_args={'check_same_thread': False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Company(Base):
    __tablename__ = 'companies'
    cui = Column(String, primary_key=True, unique=True, index=True)
    companie = Column(String, nullable=True)
    nr_inreg = Column(String, nullable=True)
    adr_sed = Column(String, nullable=True)
    jud_sed = Column(String, nullable=True)
    adr_pl1 = Column(String, nullable=True)
    jud_pl1 = Column(String, nullable=True)
    administrator = Column(String, nullable=True)

Base.metadata.create_all(bind=engine)

def get_all_companies():
    session = SessionLocal()
    companies = session.query(Company.companie).all()
    session.close()
    return [company[0] for company in companies]

def load_company_data_by_name(company_name: str):
    session = SessionLocal()
    company = session.query(Company).filter(Company.companie == company_name).first()
    session.close()
    return company

def save_or_update_company(data: dict):
    session = SessionLocal()
    company = session.query(Company).filter(Company.cui == data['cui']).first()
    if company:
        for key, value in data.items():
            setattr(company, key, value if value else None)
        print(f"Data updated for CUI: {data['cui']}")
    else:
        new_company = Company(**{k: v or 'Unknown' for k, v in data.items()})
        session.add(new_company)
        print(f"New data saved for CUI: {data['cui']}")
    session.commit()
    session.close()

# --------------------------
# Document Generation Functions
# --------------------------
# Global dictionary that will hold all form values.
form_data = {}

def var_dictionary():
    # Determine conditional values
    operatiuni_cash = form_data.get('optiuni_decl_casier') == "S-au realizat operațiuni cu numerar."
    operatiuni_terti = form_data.get('optiuni_decl_gestionar') == "S-au realizat operațiuni cu terți."
    return {
        'companie' : form_data.get('companie', ''),
        'cui' : form_data.get('cui', ''),
        'nr_inreg' : form_data.get('nr_inreg', ''),
        'adr_sed' : form_data.get('adr_sed', ''),
        'jud_sed' : form_data.get('jud_sed', ''),
        'adr_pl1' : form_data.get('adr_pl1', ''),
        'jud_pl1' : form_data.get('jud_pl1', ''),
        'nr_decz' : form_data.get('nr_decz', ''),
        'data_decz' : form_data.get('data_decz', ''),
        'administrator' : form_data.get('administrator', ''),
        'membru1_com': form_data.get('membru1_com', ''),
        'data_inv' : form_data.get('data_inv', ''),
        'data_predare_pv' : form_data.get('data_predare_pv', ''),
        'an_inv' : form_data.get('an_inv', ''),
        'operatiuni_cash': operatiuni_cash,
        'tip_doc_in_casier' : form_data.get('tip_doc_in_casier', ''),
        'nr_doc_in_casier' : form_data.get('nr_doc_in_casier', ''),
        'data_doc_in_casier' : form_data.get('data_doc_in_casier', ''),
        'tip_doc_out_casier' : form_data.get('tip_doc_out_casier', ''),
        'nr_doc_out_casier' : form_data.get('nr_doc_out_casier', ''),
        'data_doc_out_casier' : form_data.get('data_doc_out_casier', ''),
        'operatiuni_terti' : operatiuni_terti,
        'tip_doc_in_gest' : form_data.get('tip_doc_in_gest', ''),
        'nr_doc_in_gest' : form_data.get('nr_doc_in_gest', ''),
        'data_doc_in_gest' : form_data.get('data_doc_in_gest', ''),
        'tip_doc_out_gest' : form_data.get('tip_doc_out_gest', ''),
        'nr_doc_out_gest' : form_data.get('nr_doc_out_gest', ''),
        'data_doc_out_gest' : form_data.get('data_doc_out_gest', ''),
        'tip_doc_in_casier_cb' : form_data.get('tip_doc_in_casier_cb', ''),
        'nr_doc_in_casier_cb' : form_data.get('nr_doc_in_casier_cb', ''),
        'data_doc_in_casier_cb' : form_data.get('data_doc_in_casier_cb', ''),
        'data_incasare_doc_in_cb' : form_data.get('data_incasare_doc_in_cb', ''),
        'tip_doc_out_casier_cb' : form_data.get('tip_doc_out_casier_cb', ''),
        'nr_doc_out_casier_cb' : form_data.get('nr_doc_out_casier_cb', ''),
        'data_doc_out_casier_cb' : form_data.get('data_doc_out_casier_cb', ''),
        'data_plata_doc_out_cb' : form_data.get('data_plata_doc_out_cb', ''),
        'furnizor_plata_out_cb' : form_data.get('furnizor_plata_out_cb', ''),
        'ultima_zi_reg_casa' : form_data.get('ultima_zi_reg_casa', ''),
        'sold_casa_lei' : form_data.get('sold_casa_lei', ''),
        'lei500' : form_data.get('lei500', 0),
        'lei200' : form_data.get('lei200', 0),
        'lei100' : form_data.get('lei100', 0),
        'lei50' : form_data.get('lei50', 0),
        'lei20' : form_data.get('lei20', 0),
        'lei10' : form_data.get('lei10', 0),
        'lei5' : form_data.get('lei5', 0),
        'leu1' : form_data.get('leu1', 0),
        'bani50' : form_data.get('bani50', 0),
        'bani10' : form_data.get('bani10', 0),
        'bani5' : form_data.get('bani5', 0),
        'ban1' : form_data.get('ban1', 0),
        'totlei500' : form_data.get('totlei500', 0),
        'totlei200' : form_data.get('totlei200', 0),
        'totlei100' : form_data.get('totlei100', 0),
        'totlei50' : form_data.get('totlei50', 0),
        'totlei20' : form_data.get('totlei20', 0),
        'totlei10' : form_data.get('totlei10', 0),
        'totlei5' : form_data.get('totlei5', 0),
        'totleu1' : form_data.get('totleu1', 0),
        'totbani50' : form_data.get('totbani50', 0),
        'totbani10' : form_data.get('totbani10', 0),
        'totbani5' : form_data.get('totbani5', 0),
        'totban1' : form_data.get('totban1', 0),
        'banca1lei' : form_data.get('banca1lei', ''),
        'cont_banca1lei' : form_data.get('cont_banca1lei', ''),
        'sold_banca1lei' : form_data.get('sold_banca1lei', 0),
        'banca2lei' : form_data.get('banca2lei', ''),
        'cont_banca2lei' : form_data.get('cont_banca2lei', ''),
        'sold_banca2lei' : form_data.get('sold_banca2lei', 0),
        'banca3lei' : form_data.get('banca3lei', ''),
        'cont_banca3lei' : form_data.get('cont_banca3lei', ''),
        'sold_banca3lei' : form_data.get('sold_banca3lei', 0),
        'banca1euro' : form_data.get('banca1euro', ''),
        'cont_banca1euro' : form_data.get('cont_banca1euro', ''),
        'sold_banca1euro' : form_data.get('sold_banca1euro', 0),
        'banca2euro' : form_data.get('banca2euro', ''),
        'cont_banca2euro' : form_data.get('cont_banca2euro', ''),
        'sold_banca2euro' : form_data.get('sold_banca2euro', 0),
        'banca3euro' : form_data.get('banca3euro', ''),
        'cont_banca3euro' : form_data.get('cont_banca3euro', ''),
        'sold_banca3euro' : form_data.get('sold_banca3euro', 0),
        'banca1usd' : form_data.get('banca1usd', ''),
        'cont_banca1usd' : form_data.get('cont_banca1usd', ''),
        'sold_banca1usd' : form_data.get('sold_banca1usd', 0),
        'banca2usd' : form_data.get('banca2usd', ''),
        'cont_banca2usd' : form_data.get('cont_banca2usd', ''),
        'sold_banca2usd' : form_data.get('sold_banca2usd', 0),
        'banca3usd' : form_data.get('banca3usd', ''),
        'cont_banca3usd' : form_data.get('cont_banca3usd', ''),
        'sold_banca3usd' : form_data.get('sold_banca3usd', 0),
        'propuneri_pvi' : form_data.get('propuneri_pvi', ''),
    }

def doc01():
    doc01_path = Path.cwd() / "Templates" / "01.Decizie-de-inventariere-v2.0.docx"
    doc = DocxTemplate(doc01_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def doc02():
    doc02_path = Path.cwd() / "Templates" / "02.Grafic-de-desfasurare-inventariere-v1.1.docx"
    doc = DocxTemplate(doc02_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def doc03():
    doc03_path = Path.cwd() / "Templates" / "03.Proceduri-privind-inventarierea-v1.1.docx"
    doc = DocxTemplate(doc03_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def doc04():
    doc04_path = Path.cwd() / "Templates" / "04.Declaratie-casier-v1.1.docx"
    doc = DocxTemplate(doc04_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def doc05():
    doc05_path = Path.cwd() / "Templates" / "05.Declaratie-gestionar-inainte-inv-v1.1.docx"
    doc = DocxTemplate(doc05_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def doc06():
    doc06_path = Path.cwd() / "Templates" / "06.Declaratie-gestionar-sfarsit-inv-v1.1.docx"
    doc = DocxTemplate(doc06_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def doc07():
    doc07_path = Path.cwd() / "Templates" / "07.Declaratie-responsabil-conturi-bancare-v1.1.docx"
    doc = DocxTemplate(doc07_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def doc08():
    doc08_path = Path.cwd() / "Templates" / "08.Proces-verbal-inventariere-numerar-si-conturi-banci-v1.1.docx"
    doc = DocxTemplate(doc08_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def doc09():
    doc09_path = Path.cwd() / "Templates" / "09.Proces-verbal-inventariere-v1.1.docx"
    doc = DocxTemplate(doc09_path)
    doc.render(var_dictionary())
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def create_zip_archive():
    # Generate all document bytes
    contents = {
        f"{form_data.get('companie')}-Decizie-inventariere-{form_data.get('data_decz')}.docx": doc01(),
        f"{form_data.get('companie')}-Grafic-de-desfasurare-inventariere-{form_data.get('data_decz')}.docx": doc02(),
        f"{form_data.get('companie')}-Proceduri-privind-inventarierea-{form_data.get('data_decz')}.docx": doc03(),
        f"{form_data.get('companie')}-Declaratie-casier-{form_data.get('data_inv')}.docx": doc04(),
        f"{form_data.get('companie')}-Declaratie-gestionar-inainte-inv-{form_data.get('data_inv')}.docx": doc05(),
        f"{form_data.get('companie')}-Declaratie-gestionar-sfarsit-inv-{form_data.get('data_inv')}.docx": doc06(),
        f"{form_data.get('companie')}-Declaratie-responsabil-conturi-bancare-{form_data.get('data_inv')}.docx": doc07(),
        f"{form_data.get('companie')}-Proces-verbal-inventariere-numerar-si-conturi-banci-{form_data.get('data_inv')}.docx": doc08(),
        f"{form_data.get('companie')}-Proces-verbal-inventariere-{form_data.get('data_inv')}.docx": doc09(),
    }
    zip_buffer = io.BytesIO()
    with ZipFile(zip_buffer, 'w') as zipf:
        for filename, content in contents.items():
            zipf.writestr(filename, content)
    return zip_buffer.getvalue()

# --------------------------
# UI Creation with NiceGUI
# --------------------------
ui.label("Întocmire acte pentru inventariere:").classes("text-h4")

# --- Database File Upload/Download Section ---
with ui.row():
    # Download company_data.db button
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "rb") as f:
            db_bytes = f.read()
        ui.download("Download nicegui_company_data.db",
            db_bytes,
            "nicegui_company_data.db")

    # File uploader for company_data.db
    def on_file_upload(event):
        for file in event['files']:
            with open(DB_PATH, "wb") as f:
                f.write(file['content'])
            ui.notify("nicegui_company_data.db file uploaded and replaced successfully!", color="green")
    ui.upload(label="Upload new nicegui_company_data.db file", on_upload=on_file_upload).props("accept=.db")


ui.markdown("<hr>")

# Dictionary to store input widgets for later access
inputs = {}

# --- Company Selection ---
company_names = get_all_companies()
with ui.row():
    inputs['selected_company'] = ui.select(
        label="Selectează Compania",
        options=[""] + company_names,
        value="",
    )

def on_company_change():
    selected = inputs['selected_company'].value
    if selected:
        company = load_company_data_by_name(selected)
        if company:
            inputs['cui'].value = company.cui or ""
            inputs['companie'].value = company.companie or ""
            inputs['nr_inreg'].value = company.nr_inreg or ""
            inputs['adr_sed'].value = company.adr_sed or ""
            inputs['jud_sed'].value = company.jud_sed or ""
            inputs['adr_pl1'].value = company.adr_pl1 or ""
            inputs['jud_pl1'].value = company.jud_pl1 or ""
            inputs['administrator'].value = company.administrator or ""

inputs['selected_company'].on('change', on_company_change)

ui.markdown("<br>")

# --- Main Form ---
with ui.column():
    with ui.row():
        inputs['companie'] = ui.input(label="Companie", placeholder="e.g. ADAKRON SRL")
        inputs['cui'] = ui.input(label="CUI", placeholder="e.g. 112233")
        inputs['nr_inreg'] = ui.input(label="Nr. înregistrare", placeholder="JX/XXXX/XX.XX.XXXX")
    with ui.row():
        inputs['adr_sed'] = ui.input(label="Adresa Sediu", placeholder="e.g. Oraș Brașov, Bd-ul Muncii, nr. 11, bl. A, sc. 1, et. 1, ap. 13, Birou 10")
        inputs['jud_sed'] = ui.input(label="Județ sediu", placeholder="e.g. BRAȘOV")
    with ui.row():
        inputs['adr_pl1'] = ui.input(label="Adresa punct de lucru", placeholder="e.g. Oraș Ploiești, Str. Găgeni, nr. 13")
        inputs['jud_pl1'] = ui.input(label="Județ punct de lucru", placeholder="e.g. PRAHOVA")
    with ui.row():
        inputs['administrator'] = ui.input(label="Administrator", placeholder="e.g. POPESCU ANDREI")
        inputs['membru1_com'] = ui.input(label="Membru Comisie", placeholder="e.g. POPESCU ȘTEFAN")

    ui.markdown("<hr>")
    ui.label("Decizie inventariere:").classes("text-h6")
    with ui.row():
        inputs['nr_decz'] = ui.input(label="Nr. decizie", placeholder="xx")
        inputs['data_decz'] = ui.input(
                                        label="Data decizie",
                                        value=datetime.date.today().isoformat()
                                    ).props("type=date")

        inputs['data_inv'] = ui.input(
                                        label="Data inventar",
                                        value=datetime.date.today().isoformat()
                                    ).props("type=date")

    # an_inv and data_predare_pv will be computed on submission

    ui.markdown("<hr>")
    ui.label("Declaratie casier:").classes("text-h6")
    with ui.row():
        inputs['optiuni_decl_casier'] = ui.select(
            label="Va rugăm să selectați una dintre opțiuni",
            options=["S-au realizat operațiuni cu numerar.", "NU s-au realizat operațiuni cu numerar."],
            value="S-au realizat operațiuni cu numerar."
        )
    ui.markdown('<p style="color: #FF7F7F;">Dacă ați selectat "NU s-au realizat operațiuni cu numerar", nu este nevoie să completați aici:</p>')
    with ui.row():
        inputs['tip_doc_in_casier'] = ui.select(
            label="Tip document intrare",
            options=["Factura", "Bon fiscal", "Dispozițe de încasare"],
            value="Factura"
        )
        inputs['nr_doc_in_casier'] = ui.input(label="Nr.", placeholder="xx")
        inputs['data_doc_in_casier'] = ui.input(label="Data document", value=datetime.date.today().isoformat())
    with ui.row():
        inputs['tip_doc_out_casier'] = ui.select(
            label="Tip document ieșire",
            options=["Factura", "Bon fiscal", "Dispoziție de plată", "Chitanță"],
            value="Factura"
        )
        inputs['nr_doc_out_casier'] = ui.input(label="Nr.", placeholder="xx")
        inputs['data_doc_out_casier'] = ui.input(label="Data document", value=datetime.date.today().isoformat())

    def on_change_decl_casier():
        if inputs['optiuni_decl_casier'].value == "NU s-au realizat operațiuni cu numerar.":
            inputs['tip_doc_in_casier'].value = ""
            inputs['nr_doc_in_casier'].value = ""
            inputs['data_doc_in_casier'].value = ""
            inputs['tip_doc_out_casier'].value = ""
            inputs['nr_doc_out_casier'].value = ""
            inputs['data_doc_out_casier'].value = ""
    inputs['optiuni_decl_casier'].on('change', on_change_decl_casier)

    ui.markdown("<hr>")
    ui.label("Declaratie gestionar:").classes("text-h6")
    with ui.row():
        inputs['optiuni_decl_gestionar'] = ui.select(
            label="Va rugăm să selectați una dintre opțiuni",
            options=["S-au realizat operațiuni cu terți.", "NU s-au realizat operațiuni cu terți."],
            value="S-au realizat operațiuni cu terți."
        )
    with ui.row():
        inputs['tip_doc_in_gest'] = ui.select(
            label="Tip document intrare",
            options=["Factura", "Bon fiscal"],
            value="Factura"
        )
        inputs['nr_doc_in_gest'] = ui.input(label="Nr.", placeholder="xx")
        inputs['data_doc_in_gest'] = ui.input(label="Data document", value=datetime.date.today().isoformat())
    with ui.row():
        inputs['tip_doc_out_gest'] = ui.select(
            label="Tip document iesire",
            options=["Factura", "Raport Z"],
            value="Factura"
        )
        inputs['nr_doc_out_gest'] = ui.input(label="Nr.", placeholder="xx")
        inputs['data_doc_out_gest'] = ui.input(label="Data document", value=datetime.date.today().isoformat())
    def on_change_decl_gestionar():
        if inputs['optiuni_decl_gestionar'].value == "NU s-au realizat operațiuni cu terți.":
            inputs['tip_doc_in_gest'].value = ""
            inputs['nr_doc_in_gest'].value = ""
            inputs['data_doc_in_gest'].value = ""
            inputs['tip_doc_out_gest'].value = ""
            inputs['nr_doc_out_gest'].value = ""
            inputs['data_doc_out_gest'].value = ""
    inputs['optiuni_decl_gestionar'].on('change', on_change_decl_gestionar)

    ui.markdown("<hr>")
    ui.label("Declarație responsabil conturi bancare:").classes("text-h6")
    with ui.row():
        inputs['tip_doc_in_casier_cb'] = ui.select(
            label="Tip document intrare",
            options=["Factura", "Bon fiscal"],
            value="Factura"
        )
        inputs['nr_doc_in_casier_cb'] = ui.input(label="Nr.", placeholder="xx")
        inputs['data_doc_in_casier_cb'] = ui.input(label="Data document", value=datetime.date.today().isoformat())
        inputs['data_incasare_doc_in_cb'] = ui.input(label="Data încasare", value=datetime.date.today().isoformat())
    with ui.row():
        inputs['tip_doc_out_casier_cb'] = ui.select(
            label="Tip document ieșire",
            options=["Factura", "Bon fiscal"],
            value="Factura"
        )
        inputs['nr_doc_out_casier_cb'] = ui.input(label="Nr.", placeholder="xx")
        inputs['data_doc_out_casier_cb'] = ui.input(label="Data document", value=datetime.date.today().isoformat())
        inputs['data_plata_doc_out_cb'] = ui.input(label="Data plata", value=datetime.date.today().isoformat())
        inputs['furnizor_plata_out_cb'] = ui.input(label="Furnizor", placeholder="S.C. ADAKRON S.R.L.")

    ui.markdown("<hr>")
    ui.label("Proces verbal de inventariere numerar si conturi bancare:").classes("text-h6")
    with ui.row():
        inputs['ultima_zi_reg_casa'] = ui.input(label="Ultima zi registru casa", value=datetime.date.today().isoformat())
    ui.label("Nr si tip bancnote și monede:")
    with ui.row():
        inputs['lei500'] = ui.number(label="Nr. bancnote 500 lei", value=0)
        inputs['lei200'] = ui.number(label="Nr. bancnote 200 lei", value=0)
        inputs['lei100'] = ui.number(label="Nr. bancnote 100 lei", value=0)
        inputs['lei50'] = ui.number(label="Nr. bancnote 50 lei", value=0)
        inputs['lei20'] = ui.number(label="Nr. bancnote 20 lei", value=0)
        inputs['lei10'] = ui.number(label="Nr. bancnote 10 lei", value=0)
        inputs['lei5'] = ui.number(label="Nr. bancnote 5 lei", value=0)
        inputs['leu1'] = ui.number(label="Nr. bancnote 1 leu", value=0)
        inputs['bani50'] = ui.number(label="Nr. monede 50 bani", value=0)
        inputs['bani10'] = ui.number(label="Nr. monede 10 bani", value=0)
        inputs['bani5'] = ui.number(label="Nr. monede 5 bani", value=0)
        inputs['ban1'] = ui.number(label="Nr. monede 1 ban", value=0)
    ui.label("Detalii conturi bancare in LEI:")
    with ui.row():
        inputs['banca1lei'] = ui.input(label="Banca", placeholder="ING BANK S.A.")
        inputs['cont_banca1lei'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000")
        inputs['sold_banca1lei'] = ui.number(label="Sold LEI", value=0)
    with ui.row():
        inputs['banca2lei'] = ui.input(label="Banca", placeholder="ING BANK S.A.").classes("hidden")
        inputs['cont_banca2lei'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000").classes("hidden")
        inputs['sold_banca2lei'] = ui.number(label="Sold LEI", value=0).classes("hidden")
        inputs['banca3lei'] = ui.input(label="Banca", placeholder="ING BANK S.A.").classes("hidden")
        inputs['cont_banca3lei'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000").classes("hidden")
        inputs['sold_banca3lei'] = ui.number(label="Sold LEI", value=0).classes("hidden")
    ui.label("Detalii conturi bancare in EURO:")
    with ui.row():
        inputs['banca1euro'] = ui.input(label="Banca", placeholder="ING BANK S.A.")
        inputs['cont_banca1euro'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000")
        inputs['sold_banca1euro'] = ui.number(label="Sold EURO", value=0)
    with ui.row():
        inputs['banca2euro'] = ui.input(label="Banca", placeholder="ING BANK S.A.").classes("hidden")
        inputs['cont_banca2euro'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000").classes("hidden")
        inputs['sold_banca2euro'] = ui.number(label="Sold EURO", value=0).classes("hidden")
        inputs['banca3euro'] = ui.input(label="Banca", placeholder="ING BANK S.A.").classes("hidden")
        inputs['cont_banca3euro'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000").classes("hidden")
        inputs['sold_banca3euro'] = ui.number(label="Sold EURO", value=0).classes("hidden")
    ui.label("Detalii conturi bancare in USD:")
    with ui.row():
        inputs['banca1usd'] = ui.input(label="Banca", placeholder="ING BANK S.A.")
        inputs['cont_banca1usd'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000")
        inputs['sold_banca1usd'] = ui.number(label="Sold USD", value=0)
    with ui.row():
        inputs['banca2usd'] = ui.input(label="Banca", placeholder="ING BANK S.A.").classes("hidden")
        inputs['cont_banca2usd'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000").classes("hidden")
        inputs['sold_banca2usd'] = ui.number(label="Sold USD", value=0).classes("hidden")
        inputs['banca3usd'] = ui.input(label="Banca", placeholder="ING BANK S.A.").classes("hidden")
        inputs['cont_banca3usd'] = ui.input(label="Nr. cont", placeholder="RO62INGB00009999100000000").classes("hidden")
        inputs['sold_banca3usd'] = ui.number(label="Sold USD", value=0).classes("hidden")
    ui.markdown("<hr>")
    ui.label("Proces verbal privind rezultatele inventarierii:").classes("text-h6")
    inputs['propuneri_pvi'] = ui.textarea(
        label="Propuneri:",
        placeholder="1. Lorem ipsum odor amet, consectetuer adipiscing elit.\n2. Risus himenaeos potenti mollis; augue facilisi suscipit cras.\n3. Facilisi, dictumst vivamus, semper nibh inceptos."
    )
    ui.markdown("<hr>")

    # Submit button and its callback
    def on_submit():
        # Update global form_data with current input values
        for key, widget in inputs.items():
            form_data[key] = widget.value

        # Process date fields (convert from ISO to DD.MM.YYYY format)
        try:
            dd = datetime.datetime.strptime(form_data.get('data_decz', ''), '%Y-%m-%d').date() if form_data.get('data_decz', '') else datetime.date.today()
        except:
            dd = datetime.date.today()
        form_data['data_decz'] = dd.strftime("%d.%m.%Y")
        try:
            di = datetime.datetime.strptime(form_data.get('data_inv', ''), '%Y-%m-%d').date() if form_data.get('data_inv', '') else datetime.date.today()
        except:
            di = datetime.date.today()
        form_data['data_inv'] = di.strftime("%d.%m.%Y")
        form_data['an_inv'] = di.year
        dp = di + datetime.timedelta(days=7)
        form_data['data_predare_pv'] = dp.strftime("%d.%m.%Y")

        # Process other date fields similarly
        for field in ['data_doc_in_casier', 'data_doc_out_casier', 'data_doc_in_gest',
                      'data_doc_out_gest', 'data_doc_in_casier_cb', 'data_incasare_doc_in_cb',
                      'data_doc_out_casier_cb', 'data_plata_doc_out_cb', 'ultima_zi_reg_casa']:
            try:
                dtemp = datetime.datetime.strptime(form_data.get(field, ''), '%Y-%m-%d').date() if form_data.get(field, '') else datetime.date.today()
            except:
                dtemp = datetime.date.today()
            form_data[field] = dtemp.strftime("%d.%m.%Y")

        # Validate required select fields
        if not form_data.get('optiuni_decl_casier') or not form_data.get('optiuni_decl_gestionar'):
            ui.notify("Vă rugăm să selectați opțiuni pentru operațiuni.", color="red")
            return

        # Calculate totals for cash
        totlei500 = 500 * float(form_data.get('lei500', 0))
        totlei200 = 200 * float(form_data.get('lei200', 0))
        totlei100 = 100 * float(form_data.get('lei100', 0))
        totlei50 = 50 * float(form_data.get('lei50', 0))
        totlei20 = 20 * float(form_data.get('lei20', 0))
        totlei10 = 10 * float(form_data.get('lei10', 0))
        totlei5  = 5 * float(form_data.get('lei5', 0))
        totleu1  = 1 * float(form_data.get('leu1', 0))
        totbani50 = 0.5 * float(form_data.get('bani50', 0))
        totbani10 = 0.1 * float(form_data.get('bani10', 0))
        totbani5 = 0.05 * float(form_data.get('bani5', 0))
        totban1  = 0.01 * float(form_data.get('ban1', 0))
        form_data['totlei500'] = totlei500
        form_data['totlei200'] = totlei200
        form_data['totlei100'] = totlei100
        form_data['totlei50'] = totlei50
        form_data['totlei20'] = totlei20
        form_data['totlei10'] = totlei10
        form_data['totlei5'] = totlei5
        form_data['totleu1'] = totleu1
        form_data['totbani50'] = totbani50
        form_data['totbani10'] = totbani10
        form_data['totbani5'] = totbani5
        form_data['totban1'] = totban1
        sold_casa_lei_tmp = (totlei500 + totlei200 + totlei100 + totlei50 +
                            totlei20 + totlei10 + totlei5 + totleu1 +
                            totbani50 + totbani10 + totbani5 + totban1)
        form_data['sold_casa_lei'] = locale.format_string("%.2f", sold_casa_lei_tmp, grouping=True)

        # Save or update company data in background thread
        data_to_save = {
            'cui': form_data.get('cui'),
            'companie': form_data.get('companie'),
            'nr_inreg': form_data.get('nr_inreg'),
            'adr_sed': form_data.get('adr_sed'),
            'jud_sed': form_data.get('jud_sed'),
            'adr_pl1': form_data.get('adr_pl1'),
            'jud_pl1': form_data.get('jud_pl1'),
            'administrator': form_data.get('administrator'),
        }
        threading.Thread(target=save_or_update_company, args=(data_to_save,)).start()

        # Generate ZIP archive with all documents
        zip_archive = create_zip_archive()
        ui.notify("Succes! The documents have been generated.", color="green")
        ui.download("Download documents",
            file=zip_archive,
            filename=f"{form_data.get('companie')}-acte-inventariere-{datetime.date.today().isoformat()}.zip",
            mime="application/zip")


    ui.button("Step 1: Save data and generate documents", on_click=on_submit)

ui.run()
