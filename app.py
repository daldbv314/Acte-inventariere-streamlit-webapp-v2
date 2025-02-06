import os
import io
import datetime
import streamlit as st
from zipfile import ZipFile
from pathlib import Path
from docxtpl import DocxTemplate
#from dotenv import load_dotenv
from io import BytesIO
import locale
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import threading

# Set Romanian locale for formatting
locale.setlocale(locale.LC_ALL, 'ro_RO')

# Configure Streamlit page settings
st.set_page_config(
    page_title='Inventariere', 
    layout='wide',
)
st.title('Întocmire acte pentru inventariere anuală:')

##--- HIDE STREAMLIT STYLE ---
#hide_st_style = """
#            <style>
#            #MainMenu {visibility: hidden;}
#            footer {visibility: hidden;}
#            header {visibility: hidden;}
#            </style>
#            """
#st.markdown(hide_st_style, unsafe_allow_html=True)



DEFAULT_VALUES = {
    "selected_company": "",
    "companie": "",
    "cui": "",
    "nr_inreg": "",
    "adr_sed": "",
    "jud_sed": "",
    "administrator": "",
    "nr_decz": "",
    "data_decz": "",
    "membru1_com": "",
    "data_inv": "",
    "data_predare_pv": "",
    "an_inv": "",
    "tip_inv": "",
    "tip_doc_in_gest": "",
    "nr_doc_in_gest": "",
    "data_doc_in_gest": "",
    "tip_doc_out_gest": "",
    "nr_doc_out_gest": "",
    "data_doc_out_gest": "",
    
    "tip_doc_in_casier": "",
    "nr_doc_in_casier": "",
    "data_doc_in_casier": "",
    "tip_doc_out_casier": "",
    "nr_doc_out_casier": "",
    "data_doc_out_casier": "",
    
    "tip_doc_in_casier_cb": "",
    "nr_doc_in_casier_cb": "",
    "data_doc_in_casier_cb": "",
    "data_incasare_doc_in_cb": "",
    "tip_doc_out_casier_cb": "",
    "nr_doc_out_casier_cb": "",
    "data_doc_out_casier_cb": "",
    "data_plata_doc_out_cb": "",
    "furnizor_plata_out_cb": "",
    
    "ultima_zi_reg_casa": "",
    "sold_casa_lei": "",

    "lei500": "",
    "lei200": "",
    "lei100": "",
    "lei50": "",
    "lei20": "",
    "lei10": "",
    "lei5": "",
    "leu1": "",
    "bani50": "",
    "bani10": "",
    "bani5": "",
    "ban1": "",

    "totlei500": "",
    "totlei200": "",
    "totlei100": "",
    "totlei50": "",
    "totlei20": "",
    "totlei10": "",
    "totlei5": "",
    "totleu1": "",
    "totbani50": "",
    "totbani10": "",
    "totbani5": "",
    "totban1": "",

    "banca1lei": "",
    "cont_banca1lei": "",
    "sold_banca1lei": "",
    "banca2lei": "",
    "cont_banca2lei": "",
    "sold_banca2lei": "",
    "banca3lei": "",
    "cont_banca3lei": "",
    "sold_banca3lei": "",

    "banca1euro": "",
    "cont_banca1euro": "",
    "sold_banca1euro": "",
    "banca2euro": "",
    "cont_banca2euro": "",
    "sold_banca2euro": "",
    "banca3euro": "",
    "cont_banca3euro": "",
    "sold_banca3euro": "",

    "banca1usd": "",
    "cont_banca1usd": "",
    "sold_banca1usd": "",
    "banca2usd": "",
    "cont_banca2usd": "",
    "sold_banca2usd": "",
    "banca3usd": "",
    "cont_banca3usd": "",
    "sold_banca3usd": "",

    "cont1_ap": "",
    "den_cont1_ap": "",
    "val1_ap": "",
    "cont2_ap": "",
    "den_cont2_ap": "",
    "val2_ap": "",
    "cont3_ap": "",
    "den_cont3_ap": "",
    "val3_ap": "",
    "cont4_ap": "",
    "den_cont4_ap": "",
    "val4_ap": "",
    "cont5_ap": "",
    "den_cont5_ap": "",
    "val5_ap": "",
    "cont6_ap": "",
    "den_cont6_ap": "",
    "val6_ap": "",
    "cont7_ap": "",
    "den_cont7_ap": "",
    "val7_ap": "",
    "cont8_ap": "",
    "den_cont8_ap": "",
    "val8_ap": "",
    "cont9_ap": "",
    "den_cont9_ap": "",
    "val9_ap": "",
    "cont10_ap": "",
    "den_cont10_ap": "",
    "val10_ap": "",
}

def reset_all_fields():
    # Reset individual fields to default values
    for key, default in DEFAULT_VALUES.items():
        st.session_state[key] = default
    # No explicit rerun call here; the state update will trigger a re-run

col1, col2 = st.columns([7, 1])
buton_sterg = col2.button("Resetează toate câmpurile ⚠️", 
                type="secondary", 
                help="Resetează toate câmpurile la valorile implicite")

if buton_sterg:
    reset_all_fields()

# Creates a dictionary of all variables needed for document templates.
# Returns: Dictionary mapping template variables to their values

# This extensive dictionary maps all template variables to their corresponding values
# Used by DocxTemplate for document generation
def var_dictionary ():
    var_dict = {
        'companie' : companie,
        'cui' : cui,
        'nr_inreg' : nr_inreg,
        'adr_sed' : adr_sed,
        #'loc_sed' : loc_sed,
        #'str_sed' : str_sed,
        #'nr_sed' : nr_sed,
        #'bl_sed' : bl_sed,
        #'sc_sed' : sc_sed,
        #'et_sed' : et_sed,
        #'ap_sed' : ap_sed,
        #'cam_sed' : cam_sed,
        'jud_sed' : jud_sed,
        'nr_decz' : nr_decz,
        'data_decz' : data_decz,
        'administrator' : administrator,
        'membru1_com': membru1_com,
        'data_inv' : data_inv,
        'data_predare_pv' : data_predare_pv,
        'an_inv' : an_inv,
        'tip_inv' : tip_inv,
        'tip_doc_in_gest' : tip_doc_in_gest,
        'nr_doc_in_gest' : nr_doc_in_gest,
        'data_doc_in_gest' : data_doc_in_gest,
        'tip_doc_out_gest' : tip_doc_out_gest,
        'nr_doc_out_gest' : nr_doc_out_gest,
        'data_doc_out_gest' : data_doc_out_gest,

        'tip_doc_in_casier' : tip_doc_in_casier,
        'nr_doc_in_casier' : nr_doc_in_casier,
        'data_doc_in_casier' : data_doc_in_casier,
        'tip_doc_out_casier' : tip_doc_out_casier,
        'nr_doc_out_casier' : nr_doc_out_casier,
        'data_doc_out_casier' : data_doc_out_casier,

        'tip_doc_in_casier_cb' : tip_doc_in_casier_cb,
        'nr_doc_in_casier_cb' : nr_doc_in_casier_cb,
        'data_doc_in_casier_cb' : data_doc_in_casier_cb,
        'data_incasare_doc_in_cb' : data_incasare_doc_in_cb,
        'tip_doc_out_casier_cb' : tip_doc_out_casier_cb,
        'nr_doc_out_casier_cb' : nr_doc_out_casier_cb,
        'data_doc_out_casier_cb' : data_doc_out_casier_cb,
        'data_plata_doc_out_cb' : data_plata_doc_out_cb,
        'furnizor_plata_out_cb' : furnizor_plata_out_cb,

        'ultima_zi_reg_casa' : ultima_zi_reg_casa,
        'sold_casa_lei' : sold_casa_lei,

        'lei500' : lei500,
        'lei200' : lei200,
        'lei100' : lei100,
        'lei50' : lei50,
        'lei20' : lei20,
        'lei10' : lei10,
        'lei5' : lei5,
        'leu1' : leu1,
        'bani50' : bani50,
        'bani10' : bani10,
        'bani5' : bani5,
        'ban1' : ban1,

        'totlei500' : totlei500,
        'totlei200' : totlei200,
        'totlei100' : totlei100,
        'totlei50' : totlei50,
        'totlei20' : totlei20,
        'totlei10' : totlei10,
        'totlei5' : totlei5,
        'totleu1' : totleu1,
        'totbani50' : totbani50,
        'totbani10' : totbani10,
        'totbani5' : totbani5,
        'totban1' : totban1,

        'banca1lei' : banca1lei,
        'cont_banca1lei' : cont_banca1lei,
        'sold_banca1lei' : sold_banca1lei,
        'banca2lei' : banca2lei,
        'cont_banca2lei' : cont_banca2lei,
        'sold_banca2lei' : sold_banca2lei,
        'banca3lei' : banca3lei,
        'cont_banca3lei' : cont_banca3lei,
        'sold_banca3lei' : sold_banca3lei,

        'banca1euro' : banca1euro,
        'cont_banca1euro' : cont_banca1euro,
        'sold_banca1euro' : sold_banca1euro,
        'banca2euro' : banca2euro,
        'cont_banca2euro' : cont_banca2euro,
        'sold_banca2euro' : sold_banca2euro,
        'banca3euro' : banca3euro,
        'cont_banca3euro' : cont_banca3euro,
        'sold_banca3euro' : sold_banca3euro,

        'banca1usd' : banca1usd,
        'cont_banca1usd' : cont_banca1usd,
        'sold_banca1usd' : sold_banca1usd,
        'banca2usd' : banca2usd,
        'cont_banca2usd' : cont_banca2usd,
        'sold_banca2usd' : sold_banca2usd,
        'banca3usd' : banca3usd,
        'cont_banca3usd' : cont_banca3usd,
        'sold_banca3usd' : sold_banca3usd,

        'cont1_ap' : cont1_ap,
        'den_cont1_ap' : den_cont1_ap,
        'val1_ap' : val1_ap,
        'cont2_ap' : cont2_ap,
        'den_cont2_ap' : den_cont2_ap,
        'val2_ap' : val2_ap,
        'cont3_ap' : cont3_ap,
        'den_cont3_ap' : den_cont3_ap,
        'val3_ap' : val3_ap,
        'cont4_ap' : cont4_ap,
        'den_cont4_ap' : den_cont4_ap,
        'val4_ap' : val4_ap,
        'cont5_ap' : cont5_ap,
        'den_cont5_ap' : den_cont5_ap,
        'val5_ap' : val5_ap,
        'cont6_ap' : cont6_ap,
        'den_cont6_ap' : den_cont6_ap,
        'val6_ap' : val6_ap,
        'cont7_ap' : cont7_ap,
        'den_cont7_ap' : den_cont7_ap,
        'val7_ap' : val7_ap,
        'cont8_ap' : cont8_ap,
        'den_cont8_ap' : den_cont8_ap,
        'val8_ap' : val8_ap,
        'cont9_ap' : cont9_ap,
        'den_cont9_ap' : den_cont9_ap,
        'val9_ap' : val9_ap,
        'cont10_ap' : cont10_ap,
        'den_cont10_ap' : den_cont10_ap,
        'val10_ap' : val10_ap,

        
    }
    return var_dict

# Database Configuration
DB_PATH = 'company_data.db'
Base = declarative_base()

def get_engine():
    return create_engine(f'sqlite:///{DB_PATH}', connect_args={'check_same_thread': False})

engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Company(Base):
    __tablename__ = 'companies'
    # Primary key is the company's unique tax ID (CUI)
    cui = Column(String, primary_key=True, unique=True, index=True)

    # Company details
    companie = Column(String, nullable=True)
    nr_inreg = Column(String, nullable=True)

    # Address fields
    adr_sed = Column(String, nullable=True)
    #loc_sed = Column(String, nullable=True)
    #str_sed = Column(String, nullable=True)
    #nr_sed = Column(String, nullable=True)
    #bl_sed = Column(String, nullable=True)
    #sc_sed = Column(String, nullable=True)
    #et_sed = Column(String, nullable=True)
    #ap_sed = Column(String, nullable=True)
    #cam_sed = Column(String, nullable=True)
    jud_sed = Column(String, nullable=True)

    # Administrative contact
    administrator = Column(String, nullable=True)

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

# Function to load data based on company name
def load_company_data_by_name(company_name):
    session = SessionLocal()
    company = session.query(Company).filter(Company.companie == company_name).first()
    session.close()
    if company:
        print(f"Data retrieved for Company: {company_name}")
        return company
    return None

# Function to get all companies
def get_all_companies():
    """
    Retrieves a list of all company names from the database.
    Returns: List of company names (strings)
    """
    session = SessionLocal()
    companies = session.query(Company.companie).all()
    session.close()
    # Extract company names from Row objects
    return [company[0] for company in companies]

# Function to save or update company data
def save_or_update_company(data):
    """
    Saves new company data or updates existing company records in the database.
    
    Args: 
        data (dict): Dictionary containing company information
    """
    session = SessionLocal()
    company = session.query(Company).filter(Company.cui == data['cui']).first()

    if company:
        # Update existing company record
        for key, value in data.items():
            setattr(company, key, value if value else None)
        print(f"Data updated for CUI: {data['cui']}")
    else:
        # Create new company record
        new_company = Company(**{k: v or 'Unknown' for k, v in data.items()})
        session.add(new_company)
        print(f"New data saved for CUI: {data['cui']}")
    session.commit()
    session.close()

# Auto-populate fields when CUI changes
def company_selection_change():
    """
    Callback function triggered when a company is selected from the dropdown.
    Updates all form fields with the selected company's data.
    """
    selected_company = st.session_state.get('selected_company', '')
    if selected_company:
        session = SessionLocal()
        company = session.query(Company).filter(Company.companie == selected_company).first()
        session.close()
        
        if company:
            # Update session state with company details
            st.session_state.update({
                'cui': company.cui or '',
                'companie': company.companie or '',
                'nr_inreg': company.nr_inreg or '',
                'adr_sed': company.adr_sed or '',
                #'loc_sed': company.loc_sed or '',
                #'str_sed': company.str_sed or '',
                #'nr_sed': company.nr_sed or '',
                #'bl_sed': company.bl_sed or '',
                #'sc_sed': company.sc_sed or '',
                #'et_sed': company.et_sed or '',
                #'ap_sed': company.ap_sed or '',
                #'cam_sed': company.cam_sed or '',
                'jud_sed': company.jud_sed or '',
                'administrator': company.administrator or ''
            })

# Document Generation Functions
def doc01():
    doc01_path = Path.cwd() / "Templates" / "Decizie-de-inventariere-v2.0.docx"
    doc01_doc = DocxTemplate(doc01_path)
    context = var_dictionary()
    doc01_doc.render(context)
    doc01_bytes = BytesIO()
    doc01_doc.save(doc01_bytes)
    return doc01_bytes.getvalue()

def doc02():
    doc02_path = Path.cwd() / "Templates" / "Grafic-de-desfasurare-inventariere-v1.1.docx"
    doc02_doc = DocxTemplate(doc02_path)
    context = var_dictionary()
    doc02_doc.render(context)
    doc02_bytes = BytesIO()
    doc02_doc.save(doc02_bytes)
    return doc02_bytes.getvalue()

def doc03():
    doc03_path = Path.cwd() / "Templates" / "Proceduri-privind-inventarierea-v1.1.docx"
    doc03_doc = DocxTemplate(doc03_path)
    context = var_dictionary()
    doc03_doc.render(context)
    doc03_bytes = BytesIO()
    doc03_doc.save(doc03_bytes)
    return doc03_bytes.getvalue()

def doc04():
    doc04_path = Path.cwd() / "Templates" / "Declaratie-gestionar-inainte-inv-v1.1.docx"
    doc04_doc = DocxTemplate(doc04_path)
    context = var_dictionary()
    doc04_doc.render(context)
    doc04_bytes = BytesIO()
    doc04_doc.save(doc04_bytes)
    return doc04_bytes.getvalue()

def doc05():
    doc05_path = Path.cwd() / "Templates" / "PV-inventariere-numerar-si-conturi-banci-v1.1.docx"
    doc05_doc = DocxTemplate(doc05_path)
    context = var_dictionary()
    doc05_doc.render(context)
    doc05_bytes = BytesIO()
    doc05_doc.save(doc05_bytes)
    return doc05_bytes.getvalue()

def doc06():
    doc06_path = Path.cwd() / "Templates" / "Declaratie-casier-v1.1.docx"
    doc06_doc = DocxTemplate(doc06_path)
    context = var_dictionary()
    doc06_doc.render(context)
    doc06_bytes = BytesIO()
    doc06_doc.save(doc06_bytes)
    return doc06_bytes.getvalue()

def doc07():
    doc07_path = Path.cwd() / "Templates" / "Declaratie-responsabil-conturi-bancare-v1.1.docx"
    doc07_doc = DocxTemplate(doc07_path)
    context = var_dictionary()
    doc07_doc.render(context)
    doc07_bytes = BytesIO()
    doc07_doc.save(doc07_bytes)
    return doc07_bytes.getvalue()

def doc08():
    doc08_path = Path.cwd() / "Templates" / "Declaratie-gestionar-sfarsit-inv-v1.1.docx"
    doc08_doc = DocxTemplate(doc08_path)
    context = var_dictionary()
    doc08_doc.render(context)
    doc08_bytes = BytesIO()
    doc08_doc.save(doc08_bytes)
    return doc08_bytes.getvalue()

def doc09():
    doc09_path = Path.cwd() / "Templates" / "Proces-verbal-inventariere-v1.1.docx"
    doc09_doc = DocxTemplate(doc09_path)
    context = var_dictionary()
    doc09_doc.render(context)
    doc09_bytes = BytesIO()
    doc09_doc.save(doc09_bytes)
    return doc09_bytes.getvalue()

def create_zip_archive():
    """
    Creates a ZIP archive containing all generated documents.
    Returns: Bytes object containing the ZIP archive
    """
    # Generate the content for each document
    doc01_content = doc01()
    doc02_content = doc02()
    doc03_content = doc03()
    doc04_content = doc04()
    doc05_content = doc05()
    doc06_content = doc06()
    doc07_content = doc07()
    doc08_content = doc08()
    doc09_content = doc09()
    # Create ZIP archive in memory
    with io.BytesIO() as zip_buffer:
        with ZipFile(zip_buffer, 'w') as zipf:
            # Add each doc to the archive
            zipf.writestr(f"{companie}-Decizie-inventariere.docx",doc01_content)
            zipf.writestr(f"{companie}-Grafic-de-desfasurare-inventariere.docx",doc02_content)
            zipf.writestr(f"{companie}-Proceduri-privind-inventarierea.docx",doc03_content)
            zipf.writestr(f"{companie}-Declaratie-gestionar-inainte-inv.docx",doc04_content)
            zipf.writestr(f"{companie}-PV-inventariere-numerar-si-conturi-banci.docx",doc05_content)
            zipf.writestr(f"{companie}-Declaratie-casier.docx",doc06_content)
            zipf.writestr(f"{companie}-Declaratie-responsabil-conturi-bancare.docx",doc07_content)
            zipf.writestr(f"{companie}-Declaratie-gestionar-sfarsit-inv.docx",doc08_content)
            zipf.writestr(f"{companie}-Proces-verbal-inventariere.docx",doc09_content)
        # Get the zip archive content as bytes
        zip_bytes = zip_buffer.getvalue()
    return zip_bytes


# UI Components
# Create company selection dropdown
company_names = get_all_companies()
for _ in range(4):  # Number of blank lines
    st.write("")
col1, col2, col3 = st.columns(3, gap="small")
selected_company = col2.selectbox('Selectează Compania', [''] + company_names, 
                                key='selected_company',
                                on_change=company_selection_change)
for _ in range(4):  # Number of blank lines
    st.write("")


with st.form("inventar", clear_on_submit=False):
        
        col1, col2, col3 = st.columns(3, gap="small")
        companie = col1.text_input('Companie', value="", key='companie', placeholder='e.g. ADAKRON SRL', max_chars=None, help='')
        cui = col2.text_input('CUI', value="", key='cui', placeholder='e.g. 112233', max_chars=None)
        nr_inreg = col3.text_input('Nr. înregistrare', value="", key='nr_inreg', placeholder='JX/XXXX/XX.XX.XXXX', max_chars=None  )
        col1, col2, col3 = st.columns(3, gap="small")
        adr_sed = col1.text_input('Adresa Sediu', value="", key='adr_sed',
                                placeholder='e.g. Oraș Brașov, Bd-ul Muncii, nr. 11, bl. A, sc. 1, et. 1, ap. 13, Birou 10',
                                max_chars=None, help='')
        jud_sed = col2.text_input('Județ', key='jud_sed', placeholder='e.g. BRAȘOV')
        col1, col2, col3 = st.columns(3, gap="small")
        administrator = col1.text_input('Administrator', key='administrator', placeholder='e.g. POPESCU ANDREI')
        membru1_com = col2.text_input('Membru Comisie', key='membru1_com', placeholder='e.g. POPESCU ȘTEFAN')

        #col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.25, 0.25, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08], gap="small")
        #loc_sed = col1.text_input('Localitate sediu', key='loc_sed', placeholder='e.g. BRAȘOV')
        #str_sed = col2.text_input('Strada', key='str_sed', placeholder='e.g. NICOLAE LABIȘ')
        #nr_sed = col3.text_input('Nr.', key='nr_sed', placeholder='xx')
        #bl_sed = col4.text_input('Bl.', key='bl_sed', placeholder='xx')
        #sc_sed = col5.text_input('Sc.', key='sc_sed', placeholder='xx')
        #et_sed = col6.text_input('Et.', key='et_sed', placeholder='xx')
        #ap_sed = col7.text_input('Ap.', key='ap_sed', placeholder='xx')
        #cam_sed = col8.text_input('Camera/birou', key='cam_sed', placeholder='xx')

        #col1, col2, col3, col4 = st.columns(4, gap="small")
        #jud_sed = col1.text_input('Județ', key='jud_sed', placeholder='e.g. BRAȘOV')
        #administrator = col2.text_input('Administrator', key='administrator', placeholder='e.g. POPESCU ANDREI')

        st.divider()

        st.write('Decizie inventariere:')
        col1, col2, col3, col4, col5 = st.columns([0.135, 0.135, 0.135, 0.09, 0.405], gap="small")
        nr_decz = col1.text_input('Nr. decizie', key='nr_decz', placeholder='xx')
        data_decz_tmp = col2.date_input('Data decizie', datetime.date.today(), key='data_decz_tmp', help=None, format="DD.MM.YYYY")
        data_decz = data_decz_tmp.strftime("%d.%m.%Y")
        data_inv_tmp = col3.date_input('Data inventar', datetime.date.today(), key='data_inv_tmp', help=None, format="DD.MM.YYYY")
        data_inv = data_inv_tmp.strftime("%d.%m.%Y")
        an_inv = data_inv_tmp.year
        data_predare_pv_tmp = data_inv_tmp + datetime.timedelta(days=7)
        data_predare_pv = data_predare_pv_tmp.strftime("%d.%m.%Y")
        tip_inv = col5.selectbox('Situatiile financiare', 
                                    (f"anuale întocmite pentru anul {an_inv}", f"interimare întocmite pentru trimestrul I al anului {an_inv}", f"interimare întocmite pentru trimestrul II al anului {an_inv}", f"interimare întocmite pentru trimestrul III al anului {an_inv}"), 
                                    key='tip_inv', index=0)
#        st.write('Test:', data_predare_pv)
#        st.write('Test:', an_inv)
#        st.caption('This is a string that explains something above.')
#        st.text('This is regular text')
#        st.write('This is wtire')
#        st.write('<u>Decizie inventariere:<u>',unsafe_allow_html=True)
#        st.header('This is a header')
#        st.subheader('This is a subheader')
#        st.title('This is a title')
        
        st.divider()

        st.write('Declaratie gestionar:')
        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.15, 0.15, 0.15, 0.1, 0.15, 0.15, 0.15], gap="small")
        tip_doc_in_gest = col1.selectbox('Tip document intrare', ("Factura", "Bon fiscal"), key='tip_doc_in_gest', index=0, help=None)
        nr_doc_in_gest = col2.text_input('Nr.', key='nr_doc_in_gest', placeholder='xx')
        data_doc_in_gest_tmp = col3.date_input('Data document', datetime.date.today(), key='data_doc_in_gest_tmp', help=None, format="DD.MM.YYYY")
        data_doc_in_gest = data_doc_in_gest_tmp.strftime("%d.%m.%Y")
        tip_doc_out_gest = col5.selectbox('Tip document iesire', ("Factura", "Raport Z"), key='tip_doc_out_gest', index=0, help=None)
        nr_doc_out_gest =  col6.text_input('Nr.', key='nr_doc_out_gest', placeholder='xx')
        data_doc_out_gest_tmp = col7.date_input('Data document', datetime.date.today(), key='data_doc_out_gest_tmp', help=None, format="DD.MM.YYYY")
        data_doc_out_gest = data_doc_out_gest_tmp.strftime("%d.%m.%Y")
        
        st.divider()

        st.write('Proces verbal de inventariere numerar si conturi bancare:')
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap="small")
        ultima_zi_reg_casa_tmp = col1.date_input('Ultima zi registru casa', datetime.date.today(), key='ultima_zi_reg_casa_tmp', help=None, format="DD.MM.YYYY")
        ultima_zi_reg_casa = ultima_zi_reg_casa_tmp.strftime("%d.%m.%Y")
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8, gap="small")
        col1.write('Nr si tip bancnote și monede:')
        lei500 = col2.number_input('Nr. bancnote 500 lei', key='lei500', min_value=0, label_visibility="visible")
        lei200 = col3.number_input('Nr. bancnote 200 lei', key='lei200', min_value=0, label_visibility="visible")
        lei100 = col4.number_input('Nr. bancnote 100 lei', key='lei100', min_value=0, label_visibility="visible")
        lei50 = col5.number_input('Nr. bancnote 50 lei', key='lei50', min_value=0, label_visibility="visible")
        lei20 = col6.number_input('Nr. bancnote 20 lei', key='lei20', min_value=0, label_visibility="visible")
        lei10 = col7.number_input('Nr. bancnote 10 lei', key='lei10', min_value=0, label_visibility="visible")
        lei5 = col8.number_input('Nr. bancnote 5 lei', key='lei5', min_value=0, label_visibility="visible")
        leu1 = col2.number_input('Nr. bancnote 1 leu', key='leu1', min_value=0, label_visibility="visible")
        bani50 = col3.number_input('Nr. monede 50 bani', key='bani50', min_value=0, label_visibility="visible")
        bani10 = col4.number_input('Nr. monede 10 bani', key='bani10', min_value=0, label_visibility="visible")
        bani5 = col5.number_input('Nr. monede 5 bani', key='bani5', min_value=0, label_visibility="visible")
        ban1 = col6.number_input('Nr. monede 1 ban', key='ban1', min_value=0, label_visibility="visible")
        
        col1, col2, col3, col4, col5 = st.columns([0.125, 0.25, 0.25, 0.125, 0.25], gap="small")
        col1.write('Detalii conturi bancare in LEI:')
        banca1lei = col2.text_input('Banca', key='banca1lei', placeholder='ING BANK S.A.')
        cont_banca1lei = col3.text_input('Nr. cont', key='cont_banca1lei', placeholder='RO62INGB00009999100000000')
        sold_banca1lei = col4.number_input('Sold LEI', key='sold_banca1lei', label_visibility="visible")
        banca2lei = col2.text_input('Banca', key='banca2lei', placeholder='ING BANK S.A.', label_visibility="collapsed")
        cont_banca2lei = col3.text_input('Nr. cont', key='cont_banca2lei', placeholder='RO62INGB00009999100000000', label_visibility="collapsed")
        sold_banca2lei = col4.number_input('Sold LEI', key='sold_banca2lei', label_visibility="collapsed")
        banca3lei = col2.text_input('Banca', key='banca3lei', placeholder='ING BANK S.A.', label_visibility="collapsed")
        cont_banca3lei = col3.text_input('Nr. cont', key='cont_banca3lei', placeholder='RO62INGB00009999100000000', label_visibility="collapsed")
        sold_banca3lei = col4.number_input('Sold LEI', key='sold_banca3lei', label_visibility="collapsed")

        col1, col2, col3, col4, col5 = st.columns([0.125, 0.25, 0.25, 0.125, 0.25], gap="small")
        col1.write('Detalii conturi bancare in EURO:')
        banca1euro = col2.text_input('Banca', key='banca1euro', placeholder='ING BANK S.A.')
        cont_banca1euro = col3.text_input('Nr. cont', key='cont_banca1euro', placeholder='RO62INGB00009999100000000')
        sold_banca1euro = col4.number_input('Sold EURO', key='sold_banca1euro', label_visibility="visible")
        banca2euro = col2.text_input('Banca', key='banca2euro', placeholder='ING BANK S.A.', label_visibility="collapsed")
        cont_banca2euro = col3.text_input('Nr. cont', key='cont_banca2euro', placeholder='RO62INGB00009999100000000', label_visibility="collapsed")
        sold_banca2euro = col4.number_input('Sold EURO', key='sold_banca2euro', label_visibility="collapsed")
        banca3euro = col2.text_input('Banca', key='banca3euro', placeholder='ING BANK S.A.', label_visibility="collapsed")
        cont_banca3euro = col3.text_input('Nr. cont', key='cont_banca3euro', placeholder='RO62INGB00009999100000000', label_visibility="collapsed")
        sold_banca3euro = col4.number_input('Sold EURO', key='sold_banca3euro', label_visibility="collapsed")

        col1, col2, col3, col4, col5 = st.columns([0.125, 0.25, 0.25, 0.125, 0.25], gap="small")
        col1.write('Detalii conturi bancare in USD:')
        banca1usd = col2.text_input('Banca', key='banca1usd', placeholder='ING BANK S.A.')
        cont_banca1usd = col3.text_input('Nr. cont', key='cont_banca1usd', placeholder='RO62INGB00009999100000000')
        sold_banca1usd = col4.number_input('Sold USD', key='sold_banca1usd', label_visibility="visible")
        banca2usd = col2.text_input('Banca', key='banca2usd', placeholder='ING BANK S.A.', label_visibility="collapsed")
        cont_banca2usd = col3.text_input('Nr. cont', key='cont_banca2usd', placeholder='RO62INGB00009999100000000', label_visibility="collapsed")
        sold_banca2usd = col4.number_input('Sold USD', key='sold_banca2usd', label_visibility="collapsed")
        banca3usd = col2.text_input('Banca', key='banca3usd', placeholder='ING BANK S.A.', label_visibility="collapsed")
        cont_banca3usd = col3.text_input('Nr. cont', key='cont_banca3usd', placeholder='RO62INGB00009999100000000', label_visibility="collapsed")
        sold_banca3usd = col4.number_input('Sold USD', key='sold_banca3usd', label_visibility="collapsed")

        st.divider()

        st.write('Declaratie casier:')
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([0.11, 0.10, 0.10, 0.10, 0.028, 0.10, 0.10, 0.10, 0.10, 0.172, ], gap="small")
        tip_doc_in_casier = col1.selectbox('Tip document intrare', ("Factura", "Bon fiscal", "Dispozițe de încasare"), key='tip_doc_in_casier', index=0, help=None)
        nr_doc_in_casier = col2.text_input('Nr.', key='nr_doc_in_casier', placeholder='xx')
        data_doc_in_casier_tmp = col3.date_input('Data document', datetime.date.today(), key='data_doc_in_casier_tmp', help=None, format="DD.MM.YYYY")
        data_doc_in_casier = data_doc_in_casier_tmp.strftime("%d.%m.%Y")
        tip_doc_out_casier = col6.selectbox('Tip document ieșire', ("Factura", "Bon fiscal", "Dispoziție de plată", "Chitanță"), key='tip_doc_out_casier', index=0, help=None)
        nr_doc_out_casier = col7.text_input('Nr.', key='nr_doc_out_casier', placeholder='xx')
        data_doc_out_casier_tmp = col8.date_input('Data document', datetime.date.today(), key='data_doc_out_casier_tmp', help=None, format="DD.MM.YYYY")
        data_doc_out_casier = data_doc_out_casier_tmp.strftime("%d.%m.%Y")

        st.divider()

        st.write('Declaratie gestionar conturi bancare:')
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([0.11, 0.10, 0.10, 0.10, 0.028, 0.10, 0.10, 0.10, 0.10, 0.172, ], gap="small")
        tip_doc_in_casier_cb = col1.selectbox('Tip document intrare', ("Factura", "Bon fiscal"), key='tip_doc_in_casier_cb', index=0, help=None)
        nr_doc_in_casier_cb = col2.text_input('Nr.', key='nr_doc_in_casier_cb', placeholder='xx')
        data_doc_in_casier_cb_tmp = col3.date_input('Data document', datetime.date.today(), key='data_doc_in_casier_cb_tmp', help=None, format="DD.MM.YYYY")
        data_doc_in_casier_cb = data_doc_in_casier_cb_tmp.strftime("%d.%m.%Y")
        data_incasare_doc_in_cb_tmp = col4.date_input('Data încasare', datetime.date.today(), key='data_incasare_doc_in_cb_tmp', help=None, format="DD.MM.YYYY")
        data_incasare_doc_in_cb = data_incasare_doc_in_cb_tmp.strftime("%d.%m.%Y")
        tip_doc_out_casier_cb = col6.selectbox('Tip document ieșire', ("Factura", "Bon fiscal"), key='tip_doc_out_casier_cb', index=0, help=None)
        nr_doc_out_casier_cb = col7.text_input('Nr.', key='nr_doc_out_casier_cb', placeholder='xx')
        data_doc_out_casier_cb_tmp = col8.date_input('Data document', datetime.date.today(), key='data_doc_out_casier_cb_tmp', help=None, format="DD.MM.YYYY")
        data_doc_out_casier_cb = data_doc_out_casier_cb_tmp.strftime("%d.%m.%Y")
        data_plata_doc_out_cb_tmp = col9.date_input('Data plata', datetime.date.today(), key='data_plata_doc_out_cb_tmp', help=None, format="DD.MM.YYYY")
        data_plata_doc_out_cb = data_plata_doc_out_cb_tmp.strftime("%d.%m.%Y")
        furnizor_plata_out_cb = col10.text_input('Furnizor', key='furnizor_plata_out_cb', placeholder='S.C. ADAKRON S.R.L.')

        st.divider()

        st.write('Proces verbal privind rezultatele inventarierii:')
        col1, col2, col3, col4, col5 = st.columns([0.125, 0.125, 0.375, 0.125, 0.25], gap="small")
        cont1_ap = col2.text_input('Cont', key='cont1_ap', placeholder='1038', label_visibility="collapsed")
        den_cont1_ap = col3.text_input('Denumire cont', key='den_cont1_ap', 
                                    placeholder='Diferente din modificarea valorii juste a activelor financiare disponibile in vederea vanzarii si alte elemente de capitaluri proprii (A/P)',
                                    label_visibility="collapsed"
                                    )
        val1_ap = col4.text_input('Valoare', key='val1_ap', placeholder='Valoare', label_visibility="collapsed")
        cont2_ap = col2.text_input('Cont', key='cont2_ap', placeholder='....', label_visibility="collapsed")
        den_cont2_ap = col3.text_input('Denumire cont', key='den_cont2_ap', placeholder='.....', label_visibility="collapsed")
        val2_ap = col4.text_input('Valoare', key='val2_ap', placeholder='Valoare', label_visibility="collapsed")
        cont3_ap = col2.text_input('Cont', key='cont3_ap', placeholder='....', label_visibility="collapsed")
        den_cont3_ap = col3.text_input('Denumire cont', key='den_cont3_ap', placeholder='.....', label_visibility="collapsed")
        val3_ap = col4.text_input('Valoare', key='val3_ap', placeholder='Valoare', label_visibility="collapsed")
        cont4_ap = col2.text_input('Cont', key='cont4_ap', placeholder='....', label_visibility="collapsed")
        den_cont4_ap = col3.text_input('Denumire cont', key='den_cont4_ap', placeholder='.....', label_visibility="collapsed")
        val4_ap = col4.text_input('Valoare', key='val4_ap', placeholder='Valoare', label_visibility="collapsed")
        cont5_ap = col2.text_input('Cont', key='cont5_ap', placeholder='....', label_visibility="collapsed")
        den_cont5_ap = col3.text_input('Denumire cont', key='den_cont5_ap', placeholder='.....', label_visibility="collapsed")
        val5_ap = col4.text_input('Valoare', key='val5_ap', placeholder='Valoare', label_visibility="collapsed")
        cont6_ap = col2.text_input('Cont', key='cont6_ap', placeholder='....', label_visibility="collapsed")
        den_cont6_ap = col3.text_input('Denumire cont', key='den_cont6_ap', placeholder='.....', label_visibility="collapsed")
        val6_ap = col4.text_input('Valoare', key='val6_ap', placeholder='Valoare', label_visibility="collapsed")
        cont7_ap = col2.text_input('Cont', key='cont7_ap', placeholder='....', label_visibility="collapsed")
        den_cont7_ap = col3.text_input('Denumire cont', key='den_cont7_ap', placeholder='.....', label_visibility="collapsed")
        val7_ap = col4.text_input('Valoare', key='val7_ap', placeholder='Valoare', label_visibility="collapsed")
        cont8_ap = col2.text_input('Cont', key='cont8_ap', placeholder='....', label_visibility="collapsed")
        den_cont8_ap = col3.text_input('Denumire cont', key='den_cont8_ap', placeholder='.....', label_visibility="collapsed")
        val8_ap = col4.text_input('Valoare', key='val8_ap', placeholder='Valoare', label_visibility="collapsed")
        cont9_ap = col2.text_input('Cont', key='cont9_ap', placeholder='....', label_visibility="collapsed")
        den_cont9_ap = col3.text_input('Denumire cont', key='den_cont9_ap', placeholder='.....', label_visibility="collapsed")
        val9_ap = col4.text_input('Valoare', key='val9_ap', placeholder='Valoare', label_visibility="collapsed")
        cont10_ap = col2.text_input('Cont', key='cont10_ap', placeholder='....', label_visibility="collapsed")
        den_cont10_ap = col3.text_input('Denumire cont', key='den_cont10_ap', placeholder='.....', label_visibility="collapsed")
        val10_ap = col4.text_input('Valoare', key='val10_ap', placeholder='Valoare', label_visibility="collapsed")

        st.divider()

        st.write(' ')
        # Form submission handling
        submitted = st.form_submit_button("Step 1: Save data and generate documents", type="primary")

# Handle form submission
if submitted:
    with st.spinner("Generating documents..."):

        # Calculate totals and format currency
        totlei500 = 500 * lei500
        totlei200 = 200 * lei200
        totlei100 = 100 * lei100
        totlei50 = 50 * lei50
        totlei20 = 20 * lei20
        totlei10 = 10 * lei10 
        totlei5  = 5 * lei5
        totleu1  = 1 * leu1
        totbani50 = 0.5 * bani50
        totbani10 = 0.1 * bani10
        totbani5 = 0.05 * bani5
        totban1  = 0.01 * ban1

        sold_casa_lei_tmp = totlei500 + totlei200 + totlei100 + totlei50 + totlei20 + totlei10 + totlei5 + totlei10 + totlei5 + totleu1 + totbani50 + totbani10 + totbani5 + totban1
        sold_casa_lei = locale._format("%.2f", sold_casa_lei_tmp, True)

            # Create dictionary with company data for database storage
        data_to_save = {
            'cui': cui,
            'companie': companie,
            'nr_inreg': nr_inreg,
            'adr_sed': adr_sed,
            #'loc_sed': loc_sed,
            #'str_sed': str_sed,
            #'nr_sed': nr_sed,
            #'bl_sed': bl_sed,
            #'sc_sed': sc_sed,
            #'et_sed': et_sed,
            #'ap_sed': ap_sed,
            #'cam_sed': cam_sed,
            'jud_sed': jud_sed,
            'administrator': administrator
        }

        # Save company data in background thread
        threading.Thread(target=save_or_update_company, args=(data_to_save,)).start()

        # Generate documents
        zip_archive = create_zip_archive()

    # Show success message and download button
    st.success("Succes! The documents have been generated.")
    st.download_button(label="Step 2: Download", 
                    data=zip_archive, file_name=f"{companie}-acte-inventariere-{datetime.date.today()}.zip",
                    mime="docx", type="primary"
                    )