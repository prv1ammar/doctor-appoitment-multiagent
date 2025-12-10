# Doctor Appointment Multi-Agent System

A multi-agent system for managing doctor appointments with a FastAPI backend and Streamlit frontend.

## Features

- **Multi-Agent Architecture**: Supervisor agent routes requests to specialized agents
- **Appointment Management**: Book, cancel, and reschedule appointments
- **Doctor Availability**: Check availability by doctor or specialization with hourly time slots
- **Patient Management**: Create, retrieve, update patient information
- **FAQ System**: Answer questions about services, doctors, and procedures
- **Modern UI**: Streamlit-based frontend with chat interface

## System Architecture

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Streamlit     │    │      FastAPI        │    │   Multi-Agent       │
│     Frontend    │────│      Backend        │────│     System          │
│                 │    │   (main.py)         │    │                     │
└─────────────────┘    └─────────────────────┘    └─────────────────────┘
                                                              │
                                                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Specialized Agents                            │
├─────────────────┬─────────────────┬─────────────────┬───────────────────┤
│ Appointment     │ Availability    │ Patient         │ FAQ Agent         │
│ Management      │ Checking        │ Management      │                   │
│ Agent           │ Agent           │ Agent           │                   │
└─────────────────┴─────────────────┴─────────────────┴───────────────────┘
```

## Recent Updates

Based on the "Plan complet — Département Rendez-vous.pdf" requirements, the following updates have been implemented:

### 1. Patient Management Tools
- **create_patient**: Create new patient records with validation
- **get_patient**: Retrieve patient information by ID
- **update_patient**: Update patient information (partial updates supported)
- **check_patient_id**: Verify if a patient ID exists in the system

### 2. Enhanced Frontend
- Dynamic patient ID input (no longer hardcoded)
- Modern chat interface with message history
- Sidebar with patient information and quick actions
- Improved error handling and user feedback

### 3. Hourly Availability System
- **check_availability_by_doctor**: Now shows hourly time slots
  - Supports specific time checks (DD-MM-YYYY HH:MM)
  - Shows all available slots for a day (DD-MM-YYYY)
- **check_availability_by_specialization**: Shows available doctors with their time slots
- **set_appointment**: Books specific time slots (not just daily)
- **cancel_appointment**: Cancels specific time slots

### 4. Improved Data Validation
- Updated `IdentificationNumberModel` to accept positive integers
- Enhanced `DoctorAvailabilityModel` to handle hourly time slots
- Better error messages for validation failures
- Support for common data entry variations (e.g., "true" vs "True")

## Installation

1. Create and activate virtual environment:
```bash
conda create -p venv python=3.10 -y
conda activate ./venv
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the System

### Option 1: Using run.bat (Windows)
```bash
run.bat
```

### Option 2: Manual Start
1. Start the FastAPI backend:
```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8003
```

2. Start the Streamlit frontend (in a new terminal):
```bash
streamlit run frontend/app.py
```

3. Open your browser to:
   - Frontend: http://localhost:8501
   - Backend API: http://127.0.0.1:8003

## Usage Examples

### Chat Interface
1. Enter your patient ID in the sidebar
2. Type your request in the chat input
3. Examples:
   - "Book an appointment with Dr. Mohamed Tajmouati tomorrow at 10:00"
   - "Check Dr. Adil Tajmouati's availability on 05-12-2025"
   - "Cancel my appointment with Dr. Hanane Louizi"
   - "Create a new patient record"
   - "What are your services?"

### API Endpoints
- `POST /execute`: Main endpoint for agent execution
  ```json
  {
    "id_number": 1234567,
    "messages": "Your message here"
  }
  ```

## Data Structure

### CSV Files
- `data/patients.csv`: Patient information
- `data/doctors.csv`: Doctor information
- `data/doctor_availability.csv`: Hourly availability slots
- `data/rendez_vous.csv`: Appointment records
- `data/faqs.csv`: Frequently asked questions

### Data Models
- `data_models/models.py`: Pydantic models for data validation
- `toolkit/toolkits.py`: Tool implementations for agents
- `agents/agent.py`: Multi-agent system implementation

## Testing

Run the test suite:
```bash
python test_updates.py
```

Run the integration test:
```bash
python test_final.py
```

## Project Structure

```
doctor-appoitment-multiagent-main/
├── agents/
│   └── agent.py              # Multi-agent system
├── data/
│   ├── patients.csv          # Patient data
│   ├── doctors.csv           # Doctor data
│   ├── doctor_availability.csv # Availability data
│   ├── rendez_vous.csv       # Appointment data
│   └── faqs.csv              # FAQ data
├── data_models/
│   └── models.py             # Data validation models
├── frontend/
│   └── app.py                # Streamlit UI
├── toolkit/
│   └── toolkits.py           # Agent tools
├── prompt_library/           # System prompts
├── utils/                    # Utility functions
├── main.py                   # FastAPI application
├── requirements.txt          # Dependencies
├── run.bat                   # Windows startup script
└── README.md                 # This file
```

## License

This project is for educational/demonstration purposes.

## Acknowledgments

- Built with LangGraph for multi-agent orchestration
- FastAPI for REST API backend
- Streamlit for frontend interface
- Pydantic for data validation
