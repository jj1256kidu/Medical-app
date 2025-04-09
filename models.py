from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True)
    bed_id = Column(Integer, unique=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    admission_date = Column(DateTime, default=datetime.now)
    condition = Column(String)
    is_active = Column(Boolean, default=True)
    
    vitals = relationship("VitalSign", back_populates="patient")
    alarms = relationship("Alarm", back_populates="patient")

class VitalSign(Base):
    __tablename__ = 'vitals'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    timestamp = Column(DateTime, default=datetime.now)
    heart_rate = Column(Float)
    blood_pressure = Column(Float)
    spo2 = Column(Float)
    respiration_rate = Column(Float)
    temperature = Column(Float)
    
    patient = relationship("Patient", back_populates="vitals")

class Alarm(Base):
    __tablename__ = 'alarms'
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    timestamp = Column(DateTime, default=datetime.now)
    vital_type = Column(String)
    value = Column(Float)
    severity = Column(String)  # critical, warning, normal
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    comment = Column(String)
    
    patient = relationship("Patient", back_populates="alarms")

class SystemLog(Base):
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    user = Column(String)
    action = Column(String)
    details = Column(String)

# Database setup
def init_db():
    engine = create_engine('sqlite:///patient_monitoring.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

# Example usage:
# session = init_db()
# new_patient = Patient(bed_id=1, name="John Doe", age=45, gender="Male")
# session.add(new_patient)
# session.commit() 
