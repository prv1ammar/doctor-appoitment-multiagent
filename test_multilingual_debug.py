"""
Debug multilingual keyword detection
"""

def test_keyword_detection():
    """Test if Arabic and French keywords are being detected"""
    print("=" * 60)
    print("DEBUGGING MULTILINGUAL KEYWORD DETECTION")
    print("=" * 60)
    
    # Test messages
    test_messages = [
        ("réserver un rendez-vous", "French booking"),
        ("حجز موعد", "Arabic booking"),
        ("Dr. Mohamed disponible?", "French availability"),
        ("هل الدكتور محمد متاح؟", "Arabic availability"),
        ("معلومات المريض", "Arabic patient info"),
        ("Informations du patient", "French patient info"),
        ("Quels sont vos services?", "French services"),
        ("ما هي خدماتكم؟", "Arabic services"),
    ]
    
    # Keywords from the code
    french_keywords = {
        'appointment': ['rendez-vous', 'réserver', 'prendre rdv', 'annuler', 'reporter'],
        'availability': ['disponible', 'disponibilité', 'horaire', 'créneau'],
        'patient': ['patient', 'créer patient', 'mes informations', 'profil', 'mettre à jour'],
        'faq': ['service', 'question', 'aide', 'quoi', 'comment', 'quand', 'où', 'prix']
    }
    
    arabic_keywords = {
        'appointment': ['موعد', 'حجز', 'تأجيل', 'إلغاء'],
        'availability': ['متاح', 'توفر', 'جدول', 'وقت'],
        'patient': ['مريض', 'معلومات', 'تحديث', 'ملف'],
        'faq': ['خدمة', 'سؤال', 'مساعدة', 'ماذا', 'كيف', 'متى', 'أين', 'سعر']
    }
    
    for message, description in test_messages:
        print(f"\n📝 Test: {description}")
        print(f"   Message: '{message}'")
        print(f"   Lowercase: '{message.lower()}'")
        
        # Check French keywords
        for category, keywords in french_keywords.items():
            for keyword in keywords:
                if keyword in message.lower():
                    print(f"   ✅ French '{category}' keyword found: '{keyword}'")
        
        # Check Arabic keywords
        for category, keywords in arabic_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    print(f"   ✅ Arabic '{category}' keyword found: '{keyword}'")
        
        # Check combined keywords
        appointment_keywords = (french_keywords['appointment'] + arabic_keywords['appointment'])
        if any(keyword in message.lower() for keyword in appointment_keywords):
            print(f"   🎯 Should route to: APPOINTMENT AGENT")
        
        availability_keywords = (french_keywords['availability'] + arabic_keywords['availability'])
        if any(keyword in message.lower() for keyword in availability_keywords):
            print(f"   🎯 Should route to: AVAILABILITY AGENT")
        
        patient_keywords = (french_keywords['patient'] + arabic_keywords['patient'])
        if any(keyword in message.lower() for keyword in patient_keywords):
            print(f"   🎯 Should route to: PATIENT AGENT")
        
        faq_keywords = (french_keywords['faq'] + arabic_keywords['faq'])
        if any(keyword in message.lower() for keyword in faq_keywords):
            print(f"   🎯 Should route to: FAQ AGENT")
    
    print("\n" + "=" * 60)
    print("DEBUGGING COMPLETE")
    print("=" * 60)
    
    # Test the actual routing logic
    print("\n" + "=" * 60)
    print("TESTING ACTUAL ROUTING LOGIC")
    print("=" * 60)
    
    for message, description in test_messages:
        print(f"\n📝 {description}: '{message}'")
        user_message_lower = message.lower()
        
        # Simulate the routing logic from the code
        english_keywords = {
            'appointment': ['appointment', 'book', 'reschedule', 'cancel', 'schedule', 'rdv'],
            'availability': ['available', 'availability', 'schedule', 'time', 'slot'],
            'patient': ['patient', 'create patient', 'my info', 'information', 'update', 'profile'],
            'faq': ['service', 'faq', 'question', 'help', 'what', 'how', 'when', 'where']
        }
        
        # Check appointment keywords
        appointment_keywords = (english_keywords['appointment'] + 
                              french_keywords['appointment'] + 
                              arabic_keywords['appointment'])
        if any(keyword in user_message_lower for keyword in appointment_keywords):
            print(f"   ✅ Would route to: APPOINTMENT AGENT")
            continue
        
        # Check availability keywords
        availability_keywords = (english_keywords['availability'] + 
                               french_keywords['availability'] + 
                               arabic_keywords['availability'])
        if any(keyword in user_message_lower for keyword in availability_keywords):
            print(f"   ✅ Would route to: AVAILABILITY AGENT")
            continue
        
        # Check patient keywords
        patient_keywords = (english_keywords['patient'] + 
                          french_keywords['patient'] + 
                          arabic_keywords['patient'])
        if any(keyword in user_message_lower for keyword in patient_keywords):
            print(f"   ✅ Would route to: PATIENT AGENT")
            continue
        
        # Check FAQ keywords
        faq_keywords = (english_keywords['faq'] + 
                       french_keywords['faq'] + 
                       arabic_keywords['faq'])
        if any(keyword in user_message_lower for keyword in faq_keywords):
            print(f"   ✅ Would route to: FAQ AGENT")
            continue
        
        print(f"   ❌ Would route to: DEFAULT FAQ AGENT")

if __name__ == "__main__":
    test_keyword_detection()
