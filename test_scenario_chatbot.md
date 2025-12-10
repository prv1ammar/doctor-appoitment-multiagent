# 📋 Scénario de Test Complet pour le Chatbot Médical

## 🎯 **Objectif du Test**
Vérifier que le système multi-agent de prise de rendez-vous médicaux fonctionne correctement avec tous les agents et outils.

## 👤 **Profil du Patient de Test**
- **ID Patient**: 2 (Youssef - données existantes)
- **Email**: youssef@example.com
- **Téléphone**: 0612345678
- **Médecin préféré**: Dr. Mohamed Tajmouati

## 🏥 **Contexte de la Clinique**
- **Services**: Orthodontie, Prothèses et implants, Parodontologie et esthétique
- **Horaires**: Lundi-Vendredi 8:00-18:00, Samedi 9:00-13:00
- **Médecins**: 
  - Dr. Mohamed Tajmouati (Orthodontie)
  - Dr. Adil Tajmouati (Prothèses)
  - Dr. Hanane Louizi (Parodontologie)

## 🔄 **Scénario de Test Complet**

### **Étape 1: Initialisation et Salutation**
```
Utilisateur: "Bonjour"
Chatbot: "Bonjour! Je peux vous aider avec des questions sur nos services, médecins, ou procédures hospitalières."
✅ Agent: FAQ Support (Level 3bis)
✅ Test: Réponse de salutation appropriée
```

### **Étape 2: Information sur les Services**
```
Utilisateur: "Quels sont vos services?"
Chatbot: "Nous offrons des services dentaires incluant orthodontie, prothèses et implants, parodontologie et esthétique."
✅ Agent: FAQ Support (Level 3bis)
✅ Test: Liste des services correcte
```

### **Étape 3: Vérification des Informations Patient**
```
Utilisateur: "Get my patient information"
Chatbot: Affiche les informations du patient ID 2 (nom, email, téléphone, etc.)
✅ Agent: Patient Management (Level 3)
✅ Test: Récupération des données patient depuis CSV
```

### **Étape 4: Vérification de Disponibilité**
```
Utilisateur: "Is Dr. Mohamed Tajmouati available tomorrow?"
Chatbot: Vérifie la disponibilité et affiche les créneaux disponibles
✅ Agent: Availability Checker (Level 4)
✅ Test: Consultation du fichier doctor_availability.csv
```

### **Étape 5: Début de Prise de Rendez-vous**
```
Utilisateur: "book appointment"
Chatbot: "Je peux vous aider à prendre un rendez-vous. J'ai besoin: 1) Nom du médecin, 2) Date souhaitée (JJ-MM-AAAA), 3) Heure souhaitée (HH:MM)."
✅ Agent: Appointment Operations (Level 5)
✅ Test: Lancement du processus multi-étapes
```

### **Étape 6: Spécification du Médecin**
```
Utilisateur: "Dr. Mohamed Tajmouati"
Chatbot: "Médecin: Dr. Mohamed Tajmouati. Maintenant, quelle date souhaitez-vous? (format: JJ-MM-AAAA)"
✅ Agent: Appointment Operations (Level 5)
✅ Test: Capture du nom du médecin
```

### **Étape 7: Spécification de la Date**
```
Utilisateur: "15-12-2024"
Chatbot: "Date: 15-12-2024. Maintenant, quelle heure souhaitez-vous? (format: HH:MM)"
✅ Agent: Appointment Operations (Level 5)
✅ Test: Validation du format de date
```

### **Étape 8: Spécification de l'Heure**
```
Utilisateur: "14:30"
Chatbot: "Rendez-vous confirmé! [Détails du rendez-vous]"
✅ Agent: Appointment Operations (Level 5)
✅ Test: Création du rendez-vous dans rendez_vous.csv
```

### **Étape 9: Vérification des Rendez-vous Existants**
```
Utilisateur: "Get my appointments"
Chatbot: Affiche tous les rendez-vous du patient ID 2
✅ Agent: Appointment Operations (Level 5)
✅ Test: Lecture du fichier rendez_vous.csv
```

### **Étape 10: Question sur les Horaires**
```
Utilisateur: "Quels sont vos horaires d'ouverture?"
Chatbot: "Notre clinique est ouverte du lundi au vendredi de 8:00 à 18:00, et le samedi de 9:00 à 13:00."
✅ Agent: FAQ Support (Level 3bis)
✅ Test: Information sur les horaires
```

### **Étape 11: Question sur les Tarifs**
```
Utilisateur: "Combien coûte une consultation?"
Chatbot: "Les prix varient selon le traitement. Veuillez nous contacter pour un devis personnalisé."
✅ Agent: FAQ Support (Level 3bis)
✅ Test: Réponse appropriée sur les tarifs
```

### **Étape 12: Gestion du Consentement**
```
Utilisateur: "J'accepte le consentement chatbot"
Chatbot: "Consentement chatbot accepté. Merci! Vous pouvez maintenant utiliser tous les services."
✅ Agent: Patient Management (Level 3)
✅ Test: Gestion du consentement RGPD
```

### **Étape 13: Vérification d'Urgence**
```
Utilisateur: "J'ai une urgence dentaire"
Chatbot: "Pour les urgences dentaires, appelez-nous immédiatement au 05 XX XX XX XX."
✅ Agent: FAQ Support (Level 3bis)
✅ Test: Réponse d'urgence appropriée
```

### **Étape 14: Test de Validation des Règles Métier**
```
Utilisateur: "Je veux un rendez-vous dimanche à 20:00"
Chatbot: [Selon l'agent Supervisor] Validation des horaires de travail
✅ Agent: Supervisor (Level 1) → Judge (Level 2)
✅ Test: Application des règles métier
```

## 🧪 **Tests Techniques à Vérifier**

### **Test des Outils (8 outils):**
1. ✅ `check_availability_by_doctor` - Vérification disponibilité
2. ✅ `check_availability_by_specialization` - Vérification par spécialité
3. ✅ `set_appointment` - Prise de rendez-vous
4. ✅ `cancel_appointment` - Annulation rendez-vous
5. ✅ `reschedule_appointment` - Report de rendez-vous
6. ✅ `get_patient` - Récupération patient
7. ✅ `check_patient_id` - Vérification ID patient
8. ✅ `get_patient_appointments` - Liste des rendez-vous patient

### **Test de l'Architecture Hiérarchique:**
- ✅ **Level 0**: Orchestrator - Analyse et routage
- ✅ **Level 1**: Supervisor - Validation règles métier
- ✅ **Level 2**: Judge - Résolution conflits
- ✅ **Level 3**: Patient Management - Données patient
- ✅ **Level 3bis**: FAQ Support - Information
- ✅ **Level 4**: Availability Checker - Gestion planning
- ✅ **Level 5**: Appointment Operations - Opérations RDV

### **Test des Données:**
- ✅ Lecture/écriture CSV
- ✅ Validation des formats de date
- ✅ Gestion des IDs patients
- ✅ Cohérence des données

## 📊 **Résultats Attendus**

### **Pour l'Utilisateur:**
- Réponses rapides et pertinentes
- Processus de prise de RDV fluide
- Informations précises et à jour
- Gestion des erreurs claire

### **Pour le Système:**
- Tous les agents fonctionnent
- Tous les outils exécutés
- Données sauvegardées correctement
- Logs complets générés

### **Pour les Données:**
- Nouvelles entrées dans `rendez_vous.csv`
- Consultation correcte de `doctor_availability.csv`
- Lecture correcte de `patients.csv`
- Mise à jour des logs de conversation

## 🚨 **Scénarios d'Erreur à Tester**

### **1. Patient Inexistant:**
```
Utilisateur: "Get my patient information" (avec ID 9999)
Chatbot: Message d'erreur approprié
```

### **2. Date Invalide:**
```
Utilisateur: "book appointment" → "32-13-2024"
Chatbot: Message de validation de date
```

### **3. Médecin Indisponible:**
```
Utilisateur: "Is Dr. Inconnu available?"
Chatbot: Message "Médecin non trouvé"
```

### **4. Hors Horaires:**
```
Utilisateur: "Rendez-vous à 20:00"
Chatbot: Message sur les horaires d'ouverture
```

## 📝 **Checklist de Validation**

### **Frontend (Streamlit):**
- [ ] Interface charge correctement
- [ ] Champ de chat fonctionnel
- [ ] Patient ID modifiable
- [ ] Bouton "Check My Info" fonctionnel
- [ ] Historique des conversations
- [ ] Effacement de l'historique

### **Backend (FastAPI):**
- [ ] API répond sur port 8006
- [ ] Endpoint `/execute` fonctionnel
- [ ] Réponses JSON valides
- [ ] Gestion des erreurs
- [ ] Logs de débogage

### **Agents:**
- [ ] Orchestrator route correctement
- [ ] Supervisor valide les règles
- [ ] Judge résout les conflits
- [ ] Patient agent gère les données
- [ ] FAQ agent répond aux questions
- [ ] Availability agent vérifie les créneaux
- [ ] Appointment agent gère les RDV

### **Données:**
- [ ] CSV fichiers accessibles
- [ ] Lecture/écriture fonctionnelle
- [ ] Formats de date valides
- [ ] IDs patients uniques
- [ ] Cohérence des données

## 🎉 **Conclusion du Test**

Ce scénario complet permet de tester:
1. **Tous les agents** du système hiérarchique
2. **Tous les outils** disponibles
3. **Tous les flux** de conversation
4. **Toutes les opérations** de données
5. **Tous les cas d'erreur**

**Durée estimée**: 15-20 minutes pour le scénario complet

**Résultat attendu**: Système entièrement fonctionnel avec toutes les fonctionnalités validées.
