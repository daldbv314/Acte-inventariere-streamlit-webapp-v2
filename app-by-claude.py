import os
import io
import datetime
import streamlit as st
from zipfile import ZipFile
from pathlib import Path
from docxtpl import DocxTemplate
from dotenv import load_dotenv
from io import BytesIO
import locale
from db_models import init_db, DatabaseOps

locale.setlocale(locale.LC_ALL, 'ro_RO')

# Initialize database
Session = init_db()
db = DatabaseOps(Session)

st.set_page_config(
    page_title='Inventariere', 
    layout='wide',
)
st.title('Creează actele pentru inventariere:')

# Hide Streamlit style
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Sidebar for company selection
with st.sidebar:
    st.header("Companii salvate")
    companies = db.get_all_companies()
    
    if companies:
        selected_company = st.selectbox(
            "Selectează o companie existentă:",
            options=[""] + [c['cui'] for c in companies],
            format_func=lambda x: next((c['companie'] for c in companies if c['cui'] == x), "") if x else "Selectează..."
        )
        
        if selected_company:
            st.info("Datele companiei selectate vor fi populate automat în formular.")
    else:
        st.info("Nu există companii salvate în baza de date.")

# Main form
with st.form("inventar", clear_on_submit=False):
    col1, col2, col3 = st.columns(3, gap="small")
    
    # Get company data if CUI exists
    cui = col2.text_input('CUI', value="", key='cui', placeholder='e.g. 112233')
    if cui:
        company_data = db.get_company(cui)
    else:
        company_data = None
    
    # Populate form fields with existing data or empty values
    companie = col1.text_input('Companie', 
                              value=company_data.get('companie', "") if company_data else "",
                              key='companie', 
                              placeholder='e.g. ADAKRON',
                              help='nu adaugati "SRL"')
    
    nr_inreg = col3.text_input('Nr. înregistrare',
                              value=company_data.get('nr_inreg', "") if company_data else "",
                              key='nr_inreg',
                              placeholder='JX/XXXX/XX.XX.XXXX')

    # Address fields
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.25, 0.25, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08], gap="small")
    
    loc_sed = col1.text_input('Localitate sediu',
                             value=company_data.get('loc_sed', "") if company_data else "",
                             key='loc_sed',
                             placeholder='e.g. BRAȘOV')
    
    str_sed = col2.text_input('Strada',
                             value=company_data.get('str_sed', "") if company_data else "",
                             key='str_sed',
                             placeholder='e.g. NICOLAE LABIȘ')
    
    nr_sed = col3.text_input('Nr.',
                            value=company_data.get('nr_sed', "") if company_data else "",
                            key='nr_sed',
                            placeholder='xx')
    
    bl_sed = col4.text_input('Bl.',
                            value=company_data.get('bl_sed', "") if company_data else "",
                            key='bl_sed',
                            placeholder='xx')
    
    sc_sed = col5.text_input('Sc.',
                            value=company_data.get('sc_sed', "") if company_data else "",
                            key='sc_sed',
                            placeholder='xx')
    
    et_sed = col6.text_input('Et.',
                            value=company_data.get('et_sed', "") if company_data else "",
                            key='et_sed',
                            placeholder='xx')
    
    ap_sed = col7.text_input('Ap.',
                            value=company_data.get('ap_sed', "") if company_data else "",
                            key='ap_sed',
                            placeholder='xx')
    
    cam_sed = col8.text_input('Camera/birou',
                             value=company_data.get('cam_sed', "") if company_data else "",
                             key='cam_sed',
                             placeholder='xx')

    col1, col2, col3, col4 = st.columns(4, gap="small")
    jud_sed = col1.text_input('Județ',
                             value=company_data.get('jud_sed', "") if company_data else "",
                             key='jud_sed',
                             placeholder='e.g. BRAȘOV')
    
    administrator = col2.text_input('Administrator',
                                  value=company_data.get('administrator', "") if company_data else "",
                                  key='administrator',
                                  placeholder='e.g. POPESCU ANDREI')

    # [Rest of your existing form fields go here - unchanged]
    
    # Add save data checkbox
    col1, col2 = st.columns([0.2, 0.8])
    save_data = col1.checkbox("Salvează datele companiei", value=True)
    
    submitted = st.form_submit_button("Pas 1: Crează documentele", type="primary")

if submitted:
    # Save company data if checkbox is checked
    if save_data:
        company_data = {
            'cui': cui,
            'companie': companie,
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
        }
        
        try:
            db.save_company(company_data)
            st.success("Datele companiei au fost salvate cu succes!")
        except Exception as e:
            st.error(f"Eroare la salvarea datelor: {str(e)}")
    
    # [Your existing document generation code goes here - unchanged]
    with st.spinner("Se generează documentele..."):
        # [Rest of your document generation code - unchanged]
        pass