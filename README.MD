# SkanRay Real-Time Patient Monitoring System

A comprehensive healthcare monitoring solution built with Streamlit, providing real-time patient monitoring and central nursing system capabilities.

## Features

- 🏥 Real-time patient monitoring for multiple beds
- 📊 Central Nursing System (CNS) dashboard
- 🔒 Role-based access control (Doctor, Nurse, Admin)
- 📈 Real-time vital signs visualization
- 🚨 Alarm system with severity levels
- 💾 Local data storage with SQLite
- 🔄 Data synchronization simulation
- 🖥️ Responsive and intuitive UI

## Installation

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd skanray-monitoring
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
streamlit run app.py
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t skanray-monitoring .
```

2. Run the container:
```bash
docker run -p 8501:8501 skanray-monitoring
```

## Usage

1. Access the application at `http://localhost:8501`
2. Login with your credentials (default roles: Doctor, Nurse, Admin)
3. Navigate between different views using the sidebar
4. Monitor patient vitals in real-time
5. View and acknowledge alarms
6. Access the CNS dashboard for an overview of all patients

## Architecture

- Frontend: Streamlit
- Data Visualization: Plotly
- Database: SQLite
- Authentication: Session-based
- Containerization: Docker

## Security Features

- Role-based access control
- Session management
- Secure credential storage
- Data encryption (simulated)

## Development

To contribute to the project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact the development team or open an issue in the repository. 
