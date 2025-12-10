# Chatbot Conversation Examples

Here are example conversations demonstrating the updated chatbot functionality:

## Example 1: Simple Greeting
```
User: Hello
Chatbot: Hello! How can I help you today? I can assist with appointments, doctor availability, patient information, or answer questions about our services.
```

## Example 2: Check Doctor Availability
```
User: Is Dr. Mohamed Tajmouati available tomorrow?
Chatbot: I can check Dr. Mohamed Tajmouati's availability. Could you please specify which date you're interested in? (Format: DD-MM-YYYY)
```

## Example 3: Patient Information Request
```
User: Get my patient information
Chatbot: Patient ID: 3
Name: Karim Alami
Email: karim.alami@email.com
Phone: +212600112233
Birth Date: 1978-12-03
Gender: M
Address: 78 Boulevard Moulay Youssef, Casablanca
```

## Example 4: Check Specific Time Slot
```
User: Is Dr. Adil Tajmouati available on 05-12-2025 at 09:00?
Chatbot: Dr. Adil Tajmouati is available at 05-12-2025 09:00.
```

## Example 5: FAQ Question
```
User: What are your services?
Chatbot: We offer dental services including Orthodontie, Prothèse et Implants, Parodontologie et Esthétique. Our specialists provide comprehensive dental care with modern equipment.
```

## Example 6: Create New Patient
```
User: I want to create a new patient record
Chatbot: I can help you create a new patient record. I'll need the following information:
- Full name
- Email address
- Phone number (8-15 digits)
- Birth date (DD-MM-YYYY)
- Gender (M or F)
- Address

Could you please provide these details?
```

## Example 7: Check Availability by Specialization
```
User: Which orthodontists are available next week?
Chatbot: Available Orthodontie doctors for 04-12-2025:

Dr. Mohamed Tajmouati:
  - 08:00
  - 08:30
  - 09:00
  - 09:30
  - 10:30
  - 11:00
  - 12:00
  Total available slots: 7
```

## Example 8: Book Appointment
```
User: Book an appointment with Dr. Hanane Louizi on 05-12-2025 at 10:30
Chatbot: I need your patient ID number to book the appointment. Could you please provide your ID number?
```

## Example 9: Update Patient Information
```
User: Update my phone number to +212611223344
Chatbot: I can help you update your patient information. I'll need your patient ID and which information you'd like to update. Could you please provide your patient ID?
```

## Example 10: Check Patient ID
```
User: Check if patient ID 5 exists
Chatbot: Patient ID 5 exists: True
```

## How to Test:

1. **Start the server:**
   ```bash
   python -m uvicorn main:app --host 127.0.0.1 --port 8003
   ```

2. **Run the example tests:**
   ```bash
   python test_chatbot_examples.py
   ```

3. **Use the Streamlit frontend:**
   ```bash
   streamlit run frontend/app.py
   ```
   Then open http://localhost:8501 in your browser.

## Key Features Demonstrated:

✅ **Patient Management**: Create, read, update patient records  
✅ **Availability Checking**: Daily and hourly time slots  
✅ **Multi-Agent Routing**: Different agents handle different types of requests  
✅ **Error Handling**: User-friendly error messages  
✅ **Data Validation**: Proper validation of inputs  
✅ **Modern UI**: Streamlit chat interface with dynamic patient ID input

The chatbot now handles a wide range of requests and provides helpful, context-aware responses based on the multi-agent architecture.
