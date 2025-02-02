import os
import io
import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import streamlit as st
from zipfile import ZipFile
from pathlib import Path
from docxtpl import DocxTemplate
from io import BytesIO
import locale

# Set Romanian locale
locale.setlocale(locale.LC_ALL, 'ro_RO')

# Configure Streamlit page
st.set_page_config(page_title='Inventariere', layout='wide')
st.title('Creează actele pentru inventariere:')

# Hide Streamlit style elements
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

# SQLAlchemy setup
Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    companie = Column(String, nullable=False)
    cui = Column(String, primary_key=True)
    nr_inreg = Column(String)
    loc_sed = Column(String)
    str_sed = Column(String)
    nr_sed = Column(String)
    bl_sed = Column(String)
    sc_sed = Column(String)
    et_sed = Column(String)
    ap_sed = Column(String)
    cam_sed = Column(String)
    jud_sed = Column(String)
    administrator = Column(String)
    nr_decz = Column(String)
    data_decz = Column(String)
    data_inv = Column(String)
    an_inv = Column(Integer)
    data_predare_pv = Column(String)
    tip_inv = Column(String)

# Initialize database
engine = create_engine('sqlite:///data.db', connect_args={'check_same_thread': False})
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# Retrieve data by CUI
def get_company_data(cui):
    return session.query(Company).filter(Company.cui == cui).first()

# Save or update company data
def save_company_data(data):
    existing_company = session.query(Company).filter(Company.cui == data['cui']).first()
    if existing_company:
        for key, value in data.items():
            setattr(existing_company, key, value)
    else:
        new_company = Company(**data)
        session.add(new_company)
    session.commit()

# Dictionary to hold all variables for document generation
def var_dictionary():
    return locals()

# Document generation functions
def generate_document(template_name, context):
    doc_path = Path.cwd() / "Templates" / template_name
    doc = DocxTemplate(doc_path)
    doc.render(context)
    doc_bytes = BytesIO()
    doc.save(doc_bytes)
    return doc_bytes.getvalue()

def create_zip_archive(context):
    doc_files = [
        ("01-Decizie-inventariere-v1.0.docx", generate_document("01-Decizie-inventariere-v1.0.docx", context)),
        ("02-Grafic-de-desfasurare-inventariere-v1.0.docx", generate_document("02-Grafic-de-desfasurare-inventariere-v1.0.docx", context)),
        ("03-Proceduri-privind-inventarierea-v1.0.docx", generate_document("03-Proceduri-privind-inventarierea-v1.0.docx", context)),
        ("04-Declaratie-gestionar-inainte-inv-v1.0.docx", generate_document("04-Declaratie-gestionar-inainte-inv-v1.0.docx", context)),
        ("05-PV-inventariere-numerar-si-conturi-banci-v1.0.docx", generate_document("05-PV-inventariere-numerar-si-conturi-banci-v1.0.docx", context)),
        ("06-Declaratie-casier-v1.0.docx", generate_document("06-Declaratie-casier-v1.0.docx", context)),
        ("07-Declaratie-responsabil-conturi-bancare-v1.0.docx", generate_document("07-Declaratie-responsabil-conturi-bancare-v1.0.docx", context)),
        ("08-Declaratie-gestionar-sfarsit-inv-v1.0.docx", generate_document("08-Declaratie-gestionar-sfarsit-inv-v1.0.docx", context)),
        ("09-Proces-verbal-inventariere-v1.0.docx", generate_document("09-Proces-verbal-inventariere-v1.0.docx", context)),
    ]

    with io.BytesIO() as zip_buffer:
        with ZipFile(zip_buffer, 'w') as zipf:
            for filename, content in doc_files:
                zipf.writestr(f"{context['companie']}-{filename}", content)
        return zip_buffer.getvalue()

# Form to collect data with auto-population based on CUI
with st.form("inventar", clear_on_submit=False):
    col1, col2, col3 = st.columns(3, gap="small")
    companie = col1.text_input('Companie', value="", key='companie', placeholder='e.g. ADAKRON')
    cui = col2.text_input('CUI', value="", key='cui', placeholder='e.g. 112233')
    nr_inreg = col3.text_input('Nr. înregistrare', value="", key='nr_inreg', placeholder='JX/XXXX/XX.XX.XXXX')

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.25, 0.25, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08], gap="small")
    loc_sed = col1.text_input('Localitate sediu', key='loc_sed', placeholder='e.g. BRAȘOV')
    str_sed = col2.text_input('Strada', key='str_sed', placeholder='e.g. NICOLAE LABIȘ')
    nr_sed = col3.text_input('Nr.', key='nr_sed', placeholder='xx')
    bl_sed = col4.text_input('Bl.', key='bl_sed', placeholder='xx')
    sc_sed = col5.text_input('Sc.', key='sc_sed', placeholder='xx')
    et_sed = col6.text_input('Et.', key='et_sed', placeholder='xx')
    ap_sed = col7.text_input('Ap.', key='ap_sed', placeholder='xx')
    cam_sed = col8.text_input('Camera/birou', key='cam_sed', placeholder='xx')

    col1, col2 = st.columns(2, gap="small")
    jud_sed = col1.text_input('Județ', key='jud_sed', placeholder='e.g. BRAȘOV')
    administrator = col2.text_input('Administrator', key='administrator', placeholder='e.g. POPESCU ANDREI')

    st.divider()

    st.write('Decizie inventariere:')
    col1, col2, col3 = st.columns(3, gap="small")
    nr_decz = col1.text_input('Nr. decizie', key='nr_decz', placeholder='xx')
    data_decz_tmp = col2.date_input('Data decizie', datetime.date.today(), key='data_decz_tmp', format="DD.MM.YYYY")
    data_decz = data_decz_tmp.strftime("%d.%m.%Y")
    data_inv_tmp = col3.date_input('Data inventar', datetime.date.today(), key='data_inv_tmp', format="DD.MM.YYYY")
    data_inv = data_inv_tmp.strftime("%d.%m.%Y")
    an_inv = data_inv_tmp.year
    data_predare_pv_tmp = data_inv_tmp + datetime.timedelta(days=7)
    data_predare_pv = data_predare_pv_tmp.strftime("%d.%m.%Y")
    tip_inv = col1.selectbox('Situațiile financiare', 
        (f"anuale întocmite pentru anul {an_inv}", f"interimare întocmite pentru trimestrul I al anului {an_inv}", 
         f"interimare întocmite pentru trimestrul II al anului {an_inv}", f"interimare întocmite pentru trimestrul III al anului {an_inv}"),
        key='tip_inv', index=0)

    submitted = st.form_submit_button("Pas 1: Crează documentele", type="primary")

# Auto-populate fields if CUI exists in database
if cui:
    company_data = get_company_data(cui)
    if company_data and not submitted:
        companie = company_data.companie
        nr_inreg = company_data.nr_inreg
        loc_sed = company_data.loc_sed
        str_sed = company_data.str_sed
        nr_sed = company_data.nr_sed
        bl_sed = company_data.bl_sed
        sc_sed = company_data.sc_sed
        et_sed = company_data.et_sed
        ap_sed = company_data.ap_sed
        cam_sed = company_data.cam_sed
        jud_sed = company_data.jud_sed
        administrator = company_data.administrator
        nr_decz = company_data.nr_decz
        data_decz = company_data.data_decz
        data_inv = company_data.data_inv
        an_inv = company_data.an_inv
        data_predare_pv = company_data.data_predare_pv
        tip_inv = company_data.tip_inv
        st.experimental_rerun()

# Save or update data upon form submission
if submitted:
    with st.spinner("Se generează documentele..."):
        data = {
            'companie': companie,
            'cui': cui,
            'nr_inreg': nr_inreg,
            'loc_sed': loc_sed,
            'str_sed': str_sed,
            'nr_sed': nr_sed,
            'bl_sed': bl_sed,
            'sc_sed': sc_sed,
            'et_sed': et_sed,
            'ap_sed': ap_sed,
            'cam_sed': cam_sed,
            'jud_sed': jud_sed,
            'administrator': administrator,
            'nr_decz': nr_decz,
            'data_decz': data_decz,
            'data_inv': data_inv,
            'an_inv': an_inv,
            'data_predare_pv': data_predare_pv,
            'tip_inv': tip_inv
        }
        save_company_data(data)

        # Generate documents and create zip archive
        context = var_dictionary()
        zip_archive = create_zip_archive(context)

        st.success("Datele au fost salvate și documentele pot fi descărcate acum!")
        st.download_button(label="Pas 2: Downloadează", data=zip_archive, file_name=f"{companie}-acte-inventariere-{datetime.date.today()}.zip", mime="application/zip")
