# quick test script to hit the API with sample notes across all grade ranges.
# run the server first (python main.py), then run this.

# i asedked chat gbt to generate these test cases.

import requests
import json

BASE_URL = "http://localhost:8000"

# Test case 1: Excellent note - Should get A+ (97-100)
test_note_excellent = {
    "note_text": """
CHIEF COMPLAINT: Neck pain following motor vehicle accident

HISTORY OF PRESENT ILLNESS: 
Patient reports being involved in a rear-end motor vehicle collision on 1/10/26 at approximately 3:00 PM. 
Patient was the restrained driver, traveling at approximately 25 mph when struck from behind by another 
vehicle. Patient denied loss of consciousness, no airbag deployment. Patient reported immediate onset of 
posterior neck pain, rated 6/10 at time of accident, currently 7/10. Pain is described as constant, 
achy, with sharp component on movement. Pain is localized to posterior cervical region without radiation 
to shoulders or upper extremities. Patient denies numbness, tingling, or weakness in extremities. 
Patient denies headache, dizziness, nausea, or visual changes.

PAST MEDICAL HISTORY: Hypertension, controlled on medication
MEDICATIONS: Lisinopril 10mg daily
ALLERGIES: No known drug allergies
SOCIAL HISTORY: Non-smoker, occasional alcohol use

PHYSICAL EXAMINATION:
Vitals: BP 128/82, HR 78, RR 16, Temp 98.4°F
General: Alert and oriented x3, no acute distress
Cervical Spine: Tenderness to palpation over C4-C6 paraspinal muscles bilaterally, more prominent on right. 
No midline tenderness. Active ROM: Flexion 40° (limited by pain), Extension 50° (limited by pain), 
Right rotation 60° (limited by pain), Left rotation 70° (WNL). No step-offs or deformities palpated.
Neurological: Upper extremity strength 5/5 bilaterally in all muscle groups. Sensation intact to light 
touch C5-T1 dermatomes bilaterally. Deep tendon reflexes 2+ and symmetric at biceps, triceps, brachioradialis.
Spurling's test negative bilaterally.

ASSESSMENT: Acute cervical strain secondary to motor vehicle accident on 1/10/26

PLAN: 
1. Ibuprofen 600mg PO TID with food for pain and inflammation
2. Ice therapy 20 minutes every 2-3 hours for first 48 hours
3. Gentle cervical range of motion exercises as tolerated
4. Activity modification: avoid heavy lifting, sudden movements
5. Follow-up in 1 week to reassess symptoms and ROM
6. Patient educated on red flag symptoms: fever, severe headache, neurological changes, bowel/bladder 
   dysfunction - instructed to seek immediate care if these develop
7. If symptoms persist beyond 2 weeks, will consider referral to physical therapy

Patient verbalized understanding of treatment plan and agreed to follow-up as scheduled.
    """,
    "note_type": "Initial Evaluation",
    "date_of_service": "2026-01-15",
    "date_of_injury": "2026-01-10"
}

# Test case 2: Good note - Should get A or A- (90-96)
test_note_good = {
    "note_text": """
Patient presents with neck pain following MVA on 1/10/26. Patient states pain is 7/10, 
constant, worse with movement. No radiating symptoms reported. Patient was driver, 
rear-ended at low speed. No loss of consciousness.

PAST MEDICAL HISTORY: Hypertension
MEDICATIONS: Lisinopril 10mg daily

PHYSICAL EXAM: 
Vitals stable
Cervical spine: Tenderness over C4-C6 paraspinals bilaterally. ROM limited by pain - flexion 40°, 
extension 50°. No midline tenderness.
Neuro: Strength 5/5 upper extremities, sensation intact, reflexes 2+ symmetric.

ASSESSMENT: Acute cervical strain post-MVA

PLAN: 
- Ibuprofen 600mg TID with food
- Ice therapy first 48 hours
- ROM exercises as tolerated
- Follow-up 1 week
- Patient instructed on red flag symptoms
    """,
    "note_type": "Initial Evaluation",
    "date_of_service": "2026-01-15",
    "date_of_injury": "2026-01-10"
}

# Test case 3: Average note - Should get B range (80-89)
test_note_average = {
    "note_text": """
Patient presents with neck pain following MVA on 1/10/26. Patient states pain is 8/10, 
constant, worse with movement. No radiating symptoms reported. 

EXAM: Tenderness over C5-C7 paraspinals. ROM limited due to pain.
Strength appears normal. Reflexes intact.

ASSESSMENT: Cervical strain

PLAN: Ibuprofen 800mg TID, ice/heat, f/u 1 week
    """,
    "note_type": "Initial Evaluation",
    "date_of_service": "2026-01-15",
    "date_of_injury": "2026-01-10"
}

# Test case 4: Below average - Should get C range (70-79)
test_note_below_average = {
    "note_text": """
Patient has neck pain from car accident on 1/10/26. Pain is 8/10.

Exam shows tenderness in neck. Movement is limited.

Assessment: neck strain

Plan: gave ibuprofen, told to come back in a week
    """,
    "note_type": "Progress Note", 
    "date_of_service": "2026-01-15",
    "date_of_injury": "2026-01-10"
}

# Test case 5: Poor note - Should get D (below 70)
test_note_poor = {
    "note_text": "Patient has neck pain. Looks fine. Gave medication.",
    "note_type": "Progress Note", 
    "date_of_service": "2026-01-20",
    "date_of_injury": "2026-01-10"
}

# Test case 6: Terrible note with editorializing - Should get D
test_note_terrible = {
    "note_text": """
Patient claims neck pain from car accident but honestly seems exaggerated. 
They're probably just trying to get pain meds. Pain is allegedly 9/10.
Exam shows nothing remarkable. I don't think anything is really wrong.

Reluctantly prescribed some ibuprofen.
    """,
    "note_type": "Progress Note",
    "date_of_service": "2026-01-22", 
    "date_of_injury": "2026-01-10"
}

# Test case 7: Note with missing critical info
test_note_missing_info = {
    "note_text": """
Patient reports pain following an accident. Pain is moderate.

Exam: Some tenderness noted.

Plan: Medication prescribed.
    """,
    "note_type": "Initial Evaluation",
    "date_of_service": "2026-01-15",
    "date_of_injury": "2026-01-10"
}

# Test case 8: Note with contradictions
test_note_contradictions = {
    "note_text": """
Patient reports severe 9/10 neck pain following MVA on 1/10/26. States unable to move neck at all.

EXAM: Patient demonstrates full active range of motion of cervical spine without difficulty. 
No tenderness to palpation. Neurological exam normal.

ASSESSMENT: Severe cervical strain

PLAN: Prescribed oxycodone 10mg for severe pain
    """,
    "note_type": "Initial Evaluation",
    "date_of_service": "2026-01-15",
    "date_of_injury": "2026-01-10"
}

def test_note(note_data, test_name, expected_grade_range=""):
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    if expected_grade_range:
        print(f"EXPECTED: {expected_grade_range}")
    print(f"{'='*70}")
    
    response = requests.post(f"{BASE_URL}/analyze-note", json=note_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Score: {result['score']}/100")
        print(f"✓ Grade: {result['grade']}")
        print(f"\n✓ Issues Found: {len(result['flags'])}")
        
        for i, flag in enumerate(result['flags'], 1):
            severity_emoji = {"critical": "🔴", "major": "🟡", "minor": "🟢"}
            emoji = severity_emoji.get(flag['severity'], "⚪")
            print(f"\n  {emoji} {i}. [{flag['severity'].upper()}]")
            print(f"     Issue: {flag['issue']}")
            print(f"     Why it matters: {flag['why_it_matters']}")
            print(f"     Suggested fix: {flag['suggested_edit']}")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    # Check if server is up
    try:
        health = requests.get(f"{BASE_URL}/")
        response_data = health.json()
        print(f"\n{'='*70}")
        print(f"🏥 Clinical QA Engine Status")
        print(f"{'='*70}")
        print(f"Status: {response_data['status'].upper()}")
        print(f"Provider: {response_data.get('provider', 'unknown').upper()}")
        print(f"Model: {response_data.get('model', 'unknown')}")
        print(f"{'='*70}")
    except Exception as e:
        print("❌ ERROR: Server not running. Start it with 'python main.py' first.")
        print(f"Error details: {str(e)}")
        exit(1)
    
    # Run all tests
    test_note(test_note_excellent, "Excellent Documentation", "A+ (97-100)")
    test_note(test_note_good, "Good Documentation", "A/A- (90-96)")
    test_note(test_note_average, "Average Documentation", "B range (80-89)")
    test_note(test_note_below_average, "Below Average Documentation", "C range (70-79)")
    test_note(test_note_poor, "Poor Documentation", "D (below 70)")
    test_note(test_note_terrible, "Terrible Documentation with Bias", "D (below 70)")
    test_note(test_note_missing_info, "Missing Critical Information", "D (below 70)")
    test_note(test_note_contradictions, "Note with Contradictions", "D (below 70)")
    
    print("\n" + "="*70)
    print("✅ All tests complete!")
    print("="*70)