#!/usr/bin/env python3
"""
Demo script for testing the Speech-to-Code AI functionality.
This script tests the core components without running the full Streamlit app.
"""

import os
import sys
import whisper
import pandas as pd
from fuzzywuzzy import process
import json
from datetime import datetime

def load_code_databases():
    """Load ICD-10 and CPT code databases"""
    try:
        # Load ICD-10 codes
        icd_df = pd.read_csv('ICD-10.csv', encoding='latin-1', encoding_errors='ignore')
        
        # Load CPT codes
        cpt_df = pd.read_csv('CPT.csv', encoding='latin-1', encoding_errors='ignore')
        
        # Clean and prepare ICD-10 data
        icd_df.columns = ['ICD_Description'] + [f'ICD_Code_{i}' for i in range(1, len(icd_df.columns))]
        icd_code_column = None
        for col in icd_df.columns:
            if 'ICD_Code_' in col:
                icd_code_column = col
                break
        if icd_code_column:
            icd_df = icd_df.rename(columns={icd_code_column: 'ICD_Code'})
        
        # Clean and prepare CPT data
        cpt_df.columns = ['CPT_Data'] + [f'CPT_Extra_{i}' for i in range(1, len(cpt_df.columns))]
        
        # Convert to lowercase for better matching
        icd_df['ICD_Description'] = icd_df['ICD_Description'].astype(str).str.lower()
        cpt_df['CPT_Data'] = cpt_df['CPT_Data'].astype(str).str.lower()
        
        return icd_df, cpt_df
    except Exception as e:
        print(f"Error loading code databases: {e}")
        return None, None

def extract_medical_keywords(text):
    """Extract medical keywords from text"""
    medical_keywords = {
        "symptoms": [
            "pain", "cough", "fever", "shortness of breath", "nausea", "vomiting",
            "stomach ache", "headache", "dizziness", "fatigue", "weakness",
            "sick", "dizzy", "ache", "hurt", "sore", "swelling", "rash",
            "diarrhea", "constipation", "bloating", "gas", "heartburn"
        ],
        "diseases": [
            "indigestion", "flu", "cold", "infection", "inflammation",
            "diabetes", "hypertension", "asthma", "arthritis", "cancer"
        ],
        "procedures": [
            "diagnostic tests", "blood test", "urine sample", "x-ray",
            "mri", "ct scan", "ultrasound", "biopsy", "surgery", "examination"
        ]
    }
    
    text_lower = text.lower()
    identified_terms = []
    
    for category, keywords in medical_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                identified_terms.append({
                    "term": keyword,
                    "category": category,
                    "context": text
                })
    
    return identified_terms

def get_codes_from_symptom(symptom, icd_df, cpt_df, top_n=3):
    """Get ICD-10 and CPT codes for a given symptom"""
    symptom = str(symptom).lower()
    
    icd_matches = []
    cpt_matches = []
    
    # Search ICD-10
    if icd_df is not None and 'ICD_Description' in icd_df.columns and 'ICD_Code' in icd_df.columns:
        choices = icd_df['ICD_Description'].dropna().tolist()
        matches = process.extract(symptom, choices, limit=top_n)
        
        for desc, score in matches:
            codes = icd_df[icd_df['ICD_Description'] == desc]['ICD_Code'].dropna().tolist()
            if codes:
                icd_matches.append({
                    "code": ', '.join(map(str, codes)),
                    "description": desc,
                    "confidence": score
                })
    
    # Search CPT
    if cpt_df is not None and 'CPT_Data' in cpt_df.columns:
        choices = cpt_df['CPT_Data'].dropna().tolist()
        matches = process.extract(symptom, choices, limit=top_n)
        
        for data, score in matches:
            cpt_matches.append({
                "code": data.split(',')[0] if ',' in data else data,
                "description": data,
                "confidence": score
            })
    
    return icd_matches, cpt_matches

def demo_transcription():
    """Demo the transcription functionality"""
    print("🎤 Testing Audio Transcription...")
    
    if not os.path.exists('example_audio.wav'):
        print("❌ example_audio.wav not found")
        return None
    
    try:
        # Load Whisper model
        print("📦 Loading Whisper model...")
        model = whisper.load_model("base")
        
        # Transcribe audio
        print("🔊 Transcribing audio...")
        result = model.transcribe('example_audio.wav')
        
        print("✅ Transcription completed!")
        print(f"📝 Full text: {result['text']}")
        
        return result
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        return None

def demo_code_generation(transcription_result):
    """Demo the code generation functionality"""
    print("\n🏥 Testing Medical Code Generation...")
    
    # Load code databases
    icd_df, cpt_df = load_code_databases()
    
    if transcription_result is None:
        print("❌ No transcription result to process")
        return
    
    # Extract medical keywords
    medical_terms = extract_medical_keywords(transcription_result['text'])
    
    print(f"🔍 Found {len(medical_terms)} medical terms:")
    for term in medical_terms:
        print(f"  - {term['term']} ({term['category']})")
    
    # Generate codes
    all_icd_codes = []
    all_cpt_codes = []
    
    for term in medical_terms:
        icd_matches, cpt_matches = get_codes_from_symptom(
            term["term"], icd_df, cpt_df, top_n=3
        )
        
        for match in icd_matches:
            if match["confidence"] >= 70:  # 70% confidence threshold
                all_icd_codes.append({
                    **match,
                    "source_term": term["term"],
                    "category": term["category"]
                })
        
        for match in cpt_matches:
            if match["confidence"] >= 70:  # 70% confidence threshold
                all_cpt_codes.append({
                    **match,
                    "source_term": term["term"],
                    "category": term["category"]
                })
    
    print(f"\n🩺 Generated {len(all_icd_codes)} ICD-10 codes:")
    for code in all_icd_codes[:5]:  # Show top 5
        print(f"  - {code['code']}: {code['description']} (Confidence: {code['confidence']}%)")
    
    print(f"\n🛠️ Generated {len(all_cpt_codes)} CPT codes:")
    for code in all_cpt_codes[:5]:  # Show top 5
        print(f"  - {code['code']}: {code['description']} (Confidence: {code['confidence']}%)")
    
    return all_icd_codes, all_cpt_codes

def save_demo_results(transcription_result, icd_codes, cpt_codes):
    """Save demo results to JSON file"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "transcription": transcription_result["text"],
        "icd_codes": icd_codes,
        "cpt_codes": cpt_codes,
        "summary": {
            "total_icd_codes": len(icd_codes),
            "total_cpt_codes": len(cpt_codes),
            "audio_duration": transcription_result.get("segments", [{}])[-1].get("end", 0) if transcription_result.get("segments") else 0
        }
    }
    
    with open("demo_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Demo results saved to demo_results.json")

def main():
    """Main demo function"""
    print("🏥 Speech-to-Code AI - Demo Script")
    print("=" * 40)
    
    # Test transcription
    transcription_result = demo_transcription()
    
    if transcription_result:
        # Test code generation
        icd_codes, cpt_codes = demo_code_generation(transcription_result)
        
        # Save results
        save_demo_results(transcription_result, icd_codes, cpt_codes)
        
        print("\n✅ Demo completed successfully!")
        print("You can now run the full Streamlit app with: streamlit run app.py")
    else:
        print("\n❌ Demo failed. Please check the error messages above.")

if __name__ == "__main__":
    main() 