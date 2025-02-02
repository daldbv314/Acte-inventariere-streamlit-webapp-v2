import os
import io
import datetime
import sqlite3
import streamlit as st
from zipfile import ZipFile
from pathlib import Path
from docxtpl import DocxTemplate
from io import BytesIO
import locale

# Set locale for formatting
locale.setlocale(locale.LC_ALL, 'ro_RO')

# Streamlit page configuration
st.set_page_config(page_title='Inventariere', layout='wide')
st.title('Creează actele pentru inventariere:')

# Hide Streamlit default UI elements
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_st_style, unsafe_allow_html=True)

# SQLite database setup
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS companies (
                 companie TEXT, 
                 cui TEXT PRIMARY KEY, 
                 nr_inreg TEXT, 
                 loc_sed TEXT, 
                 str_sed TEXT, 
                 nr_sed TEXT, 
                 bl_sed TEXT, 
                 sc_sed TEXT, 
                 et_sed TEXT, 
                 ap_sed TEXT, 
                 cam_sed TEXT, 
                 jud_sed TEXT, 
                 administrator TEXT)''')
    conn.commit()
    conn.close()

# Fetch company data by CUI
def fetch_company_data(cui):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT * FROM companies WHERE cui = ?", (cui,))
    result = c.fetchone()
    conn.close()
    return result

# Save or update company data
def save_company_data(data):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''INSERT INTO companies (companie, cui, nr_inreg, loc_sed, str_sed, nr_sed, bl_sed, sc_sed, et_sed, ap_sed, cam_sed, jud_sed, administrator)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                 ON CONFLICT(cui) DO UPDATE SET 
                 companie=excluded.companie, nr_inreg=excluded.nr_inreg, loc_sed=excluded.loc_sed, str_sed=excluded.str_sed, 
                 nr_sed=excluded.nr_sed, bl_sed=excluded.bl_sed, sc_sed=excluded.sc_sed, et_sed=excluded.et_sed, 
                 ap_sed=excluded.ap_sed, cam_sed=excluded.cam_sed, jud_sed=excluded.jud_sed, administrator=excluded.administrator''', 
              data)
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# Fetch existing data if CUI is entered
cui_input = st.text_input("Introdu CUI pentru a căuta date existente", key='search_cui')
existing_data = fetch_company_data(cui_input) if cui_input else None

# Variables dictionary
def var_dictionary():
    return {
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
        'nr_decz': nr_decz,
        'data_decz': data_decz,
        'administrator': administrator,
        'data_inv': data_inv,
        'data_predare_pv': data_predare_pv,
        'an_inv': an_inv,
        'tip_inv': tip_inv,
        'tip_doc_in_gest': tip_doc_in_gest,
        'nr_doc_in_gest': nr_doc_in_gest,
        'data_doc_in_gest': data_doc_in_gest,
        'tip_doc_out_gest': tip_doc_out_gest,
        'nr_doc_out_gest': nr_doc_out_gest,
        'data_doc_out_gest': data_doc_out_gest,
        'tip_doc_in_casier': tip_doc_in_casier,
        'nr_doc_in_casier': nr_doc_in_casier,
        'data_doc_in_casier': data_doc_in_casier,
        'tip_doc_out_casier': tip_doc_out_casier,
        'nr_doc_out_casier': nr_doc_out_casier,
        'data_doc_out_casier': data_doc_out_casier,
        'tip_doc_in_casier_cb': tip_doc_in_casier_cb,
        'nr_doc_in_casier_cb': nr_doc_in_casier_cb,
        'data_doc_in_casier_cb': data_doc_in_casier_cb,
        'data_incasare_doc_in_cb': data_incasare_doc_in_cb,
        'tip_doc_out_casier_cb': tip_doc_out_casier_cb,
        'nr_doc_out_casier_cb': nr_doc_out_casier_cb,
        'data_doc_out_casier_cb': data_doc_out_casier_cb,
        'data_plata_doc_out_cb': data_plata_doc_out_cb,
        'furnizor_plata_out_cb': furnizor_plata_out_cb,
        'ultima_zi_reg_casa': ultima_zi_reg_casa,
        'sold_casa_lei': sold_casa_lei,
        'lei500': lei500,
        'lei200': lei200,
        'lei100': lei100,
        'lei50': lei50,
        'lei20': lei20,
        'lei10': lei10,
        'lei5': lei5,
        'leu1': leu1,
        'bani50': bani50,
        'bani10': bani10,
        'bani5': bani5,
        'ban1': ban1,
        'totlei500': totlei500,
        'totlei200': totlei200,
        'totlei100': totlei100,
        'totlei50': totlei50,
        'totlei20': totlei20,
        'totlei10': totlei10,
        'totlei5': totlei5,
        'totleu1': totleu1,
        'totbani50': totbani50,
        'totbani10': totbani10,
        'totbani5': totbani5,
        'totban1': totban1,
        'banca1lei': banca1lei,
        'cont_banca1lei': cont_banca1lei,
        'sold_banca1lei': sold_banca1lei,
        'banca2lei': banca2lei,
        'cont_banca2lei': cont_banca2lei,
        'sold_banca2lei': sold_banca2lei,
        'banca3lei': banca3lei,
        'cont_banca3lei': cont_banca3lei,
        'sold_banca3lei': sold_banca3lei,
        'banca1euro': banca1euro,
        'cont_banca1euro': cont_banca1euro,
        'sold_banca1euro': sold_banca1euro,
        'banca2euro': banca2euro,
        'cont_banca2euro': cont_banca2euro,
        'sold_banca2euro': sold_banca2euro,
        'banca3euro': banca3euro,
        'cont_banca3euro': cont_banca3euro,
        'sold_banca3euro': sold_banca3euro,
        'banca1usd': banca1usd,
        'cont_banca1usd': cont_banca1usd,
        'sold_banca1usd': sold_banca1usd,
        'banca2usd': banca2usd,
        'cont_banca2usd': cont_banca2usd,
        'sold_banca2usd': sold_banca2usd,
        'banca3usd': banca3usd,
        'cont_banca3usd': cont_banca3usd,
        'sold_banca3usd': sold_banca3usd,
        'cont1_ap': cont1_ap,
        'den_cont1_ap': den_cont1_ap,
        'val1_ap': val1_ap,
        'cont2_ap': cont2_ap,
        'den_cont2_ap': den_cont2_ap,
        'val2_ap': val2_ap,
        'cont3_ap': cont3_ap,
        'den_cont3_ap': den_cont3_ap,
        'val3_ap': val3_ap,
        'cont4_ap': cont4_ap,
        'den_cont4_ap': den_cont4_ap,
        'val4_ap': val4_ap,
        'cont5_ap': cont5_ap,
        'den_cont5_ap': den_cont5_ap,
        'val5_ap': val5_ap,
        'cont6_ap': cont6_ap,
        'den_cont6_ap': den_cont6_ap,
        'val6_ap': val6_ap,
        'cont7_ap': cont7_ap,
        'den_cont7_ap': den_cont7_ap,
        'val7_ap': val7_ap,
        'cont8_ap': cont8_ap,
        'den_cont8_ap': den_cont8_ap,
        'val8_ap': val8_ap,
        'cont9_ap': cont9_ap,
        'den_cont9_ap': den_cont9_ap,
        'val9_ap': val9_ap,
        'cont10_ap': cont10_ap,
        'den_cont10_ap': den_cont10_ap,
        'val10_ap': val10_ap,
    }

# Populate form with existing or new data
with st.form("inventar", clear_on_submit=False):
    col1, col2, col3 = st.columns(3, gap="small")
    companie = col1.text_input('Companie', value=existing_data[0] if existing_data else "", key='companie', placeholder='e.g. ADAKRON')
    cui = col2.text_input('CUI', value=existing_data[1] if existing_data else "", key='cui', placeholder='e.g. 112233')
    nr_inreg = col3.text_input('Nr. înregistrare', value=existing_data[2] if existing_data else "", key='nr_inreg', placeholder='JX/XXXX/XX.XX.XXXX')

    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.25, 0.25, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08], gap="small")
    loc_sed = col1.text_input('Localitate sediu', value=existing_data[3] if existing_data else "", key='loc_sed')
    str_sed = col2.text_input('Strada', value=existing_data[4] if existing_data else "", key='str_sed')
    nr_sed = col3.text_input('Nr.', value=existing_data[5] if existing_data else "", key='nr_sed')
    bl_sed = col4.text_input('Bl.', value=existing_data[6] if existing_data else "", key='bl_sed')
    sc_sed = col5.text_input('Sc.', value=existing_data[7] if existing_data else "", key='sc_sed')
    et_sed = col6.text_input('Et.', value=existing_data[8] if existing_data else "", key='et_sed')
    ap_sed = col7.text_input('Ap.', value=existing_data[9] if existing_data else "", key='ap_sed')
    cam_sed = col8.text_input('Camera/birou', value=existing_data[10] if existing_data else "", key='cam_sed')

    col1, col2 = st.columns(2, gap="small")
    jud_sed = col1.text_input('Județ', value=existing_data[11] if existing_data else "", key='jud_sed')
    administrator = col2.text_input('Administrator', value=existing_data[12] if existing_data else "", key='administrator')

    st.divider()

    # Submit button
    submitted = st.form_submit_button("Salvează datele", type="primary")

if submitted:
    data_to_save = (companie, cui, nr_inreg, loc_sed, str_sed, nr_sed, bl_sed, sc_sed, et_sed, ap_sed, cam_sed, jud_sed, administrator)
    save_company_data(data_to_save)
    st.success(f"Datele pentru compania {companie} au fost salvate/actualizate cu succes!")

# Manual update button
if existing_data and st.button("Actualizează manual datele", key='manual_update'):
    data_to_save = (companie, cui, nr_inreg, loc_sed, str_sed, nr_sed, bl_sed, sc_sed, et_sed, ap_sed, cam_sed, jud_sed, administrator)
    save_company_data(data_to_save)
    st.success(f"Datele pentru compania {companie} au fost actualizate manual!")

# Generate and download documents as before
