# db_models.py
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    cui = Column(String, primary_key=True)
    companie = Column(String)
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
    last_updated = Column(DateTime, default=datetime.utcnow)

# Database initialization function
def init_db():
    # Create db directory if it doesn't exist
    os.makedirs('db', exist_ok=True)
    
    # Create SQLite database in WAL mode for better concurrent access
    engine = create_engine('sqlite:///db/companies.db?check_same_thread=False', 
                         connect_args={'timeout': 15})
    
    # Create tables
    Base.metadata.create_all(engine)
    
    # Create session factory
    Session = sessionmaker(bind=engine)
    return Session

# Database operations class
class DatabaseOps:
    def __init__(self, Session):
        self.Session = Session
    
    def save_company(self, company_data):
        session = self.Session()
        try:
            # Check if company exists
            existing_company = session.query(Company).filter_by(cui=company_data['cui']).first()
            
            if existing_company:
                # Update existing company
                for key, value in company_data.items():
                    setattr(existing_company, key, value)
                existing_company.last_updated = datetime.utcnow()
            else:
                # Create new company
                new_company = Company(**company_data)
                session.add(new_company)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_company(self, cui):
        session = self.Session()
        try:
            company = session.query(Company).filter_by(cui=cui).first()
            if company:
                return {c.name: getattr(company, c.name) for c in company.__table__.columns}
            return None
        finally:
            session.close()
    
    def get_all_companies(self):
        session = self.Session()
        try:
            companies = session.query(Company).all()
            return [{'cui': c.cui, 'companie': c.companie} for c in companies]
        finally:
            session.close()