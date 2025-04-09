import json
import random
from datetime import datetime
from typing import Dict, List, Optional

class HL7Simulator:
    def __init__(self):
        self.patient_data = {}
        self.message_queue = []
        
    def generate_patient_data(self, patient_id: str) -> Dict:
        """Generate simulated patient data in HL7 format"""
        return {
            "MSH": {
                "message_type": "ORU^R01",
                "message_control_id": f"MSG{random.randint(1000, 9999)}",
                "timestamp": datetime.now().isoformat()
            },
            "PID": {
                "patient_id": patient_id,
                "name": f"Patient_{patient_id}",
                "dob": "19700101",
                "gender": random.choice(["M", "F"])
            },
            "PV1": {
                "visit_number": f"VN{random.randint(1000, 9999)}",
                "admission_date": datetime.now().strftime("%Y%m%d"),
                "discharge_date": None
            },
            "OBX": [
                {
                    "observation_id": "8867-4",
                    "value": f"{random.uniform(60, 100):.1f}",
                    "units": "bpm",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "observation_id": "85354-9",
                    "value": f"{random.uniform(90, 140):.1f}",
                    "units": "mmHg",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "observation_id": "59408-5",
                    "value": f"{random.uniform(95, 100):.1f}",
                    "units": "%",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    def parse_hl7_message(self, message: str) -> Optional[Dict]:
        """Parse HL7 message (simulated)"""
        try:
            return json.loads(message)
        except:
            return None
    
    def generate_hl7_message(self, patient_id: str) -> str:
        """Generate HL7 message in JSON format"""
        data = self.generate_patient_data(patient_id)
        return json.dumps(data)
    
    def queue_message(self, message: str):
        """Queue HL7 message for processing"""
        self.message_queue.append({
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        })
    
    def process_queue(self) -> List[Dict]:
        """Process queued messages"""
        processed = []
        for msg in self.message_queue:
            if msg["status"] == "pending":
                parsed = self.parse_hl7_message(msg["message"])
                if parsed:
                    msg["status"] = "processed"
                    msg["parsed_data"] = parsed
                    processed.append(msg)
        return processed
    
    def export_patient_data(self, patient_id: str, format: str = "json") -> str:
        """Export patient data in specified format"""
        data = self.generate_patient_data(patient_id)
        if format.lower() == "json":
            return json.dumps(data, indent=2)
        elif format.lower() == "hl7":
            # Simulate HL7 format conversion
            return f"MSH|^~\&|SkanRay|HOSPITAL|HL7|HOSPITAL|{datetime.now().strftime('%Y%m%d%H%M%S')}||ORU^R01|MSG12345|P|2.5"
        return ""
    
    def import_patient_data(self, data: str, format: str = "json") -> bool:
        """Import patient data from specified format"""
        try:
            if format.lower() == "json":
                parsed = json.loads(data)
                patient_id = parsed.get("PID", {}).get("patient_id")
                if patient_id:
                    self.patient_data[patient_id] = parsed
                    return True
            elif format.lower() == "hl7":
                # Simulate HL7 parsing
                parts = data.split("|")
                if len(parts) > 3:
                    self.queue_message(data)
                    return True
            return False
        except:
            return False 
