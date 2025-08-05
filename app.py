import streamlit as st
import pandas as pd
import numpy as np
import whisper
import torch
import json
import os
import tempfile
import io
import base64
from datetime import datetime
from fuzzywuzzy import process
import plotly.graph_objects as go
import plotly.express as px

# Optional imports with error handling
try:
    from pyannote.audio import Pipeline
    PYANNOTE_AVAILABLE = True
except ImportError:
    PYANNOTE_AVAILABLE = False
    st.warning("⚠️ Pyannote.audio not available. Speaker diarization will be disabled.")

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    st.warning("⚠️ Librosa not available. Audio visualization will be disabled.")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

import streamlit.components.v1 as components

# Page configuration
st.set_page_config(
    page_title="Speech-to-Code AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .code-table {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .transcription-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .doctor-text {
        border-left: 4px solid #28a745;
        padding-left: 1rem;
    }
    .patient-text {
        border-left: 4px solid #dc3545;
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transcription_data' not in st.session_state:
    st.session_state.transcription_data = None
if 'icd_codes' not in st.session_state:
    st.session_state.icd_codes = []
if 'cpt_codes' not in st.session_state:
    st.session_state.cpt_codes = []
if 'audio_file' not in st.session_state:
    st.session_state.audio_file = None
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'audio_sample_rate' not in st.session_state:
    st.session_state.audio_sample_rate = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

@st.cache_resource
def load_models():
    """Load Whisper and diarization models"""
    try:
        # Load Whisper model
        whisper_model = whisper.load_model("base")
        
        # Load diarization pipeline (requires HF token and pyannote)
        diarization_pipeline = None
        if PYANNOTE_AVAILABLE:
            hf_token = st.secrets.get("HUGGINGFACE_TOKEN", "")
            if hf_token and hf_token != "your_huggingface_token_here":
                try:
                    diarization_pipeline = Pipeline.from_pretrained(
                        "pyannote/speaker-diarization-3.1",
                        use_auth_token=hf_token
                    )
                    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                    diarization_pipeline.to(device)
                except Exception as e:
                    st.warning(f"⚠️ Could not load diarization model: {e}")
            else:
                st.info("ℹ️ Hugging Face token not configured. Speaker diarization will be disabled.")
        else:
            st.info("ℹ️ Pyannote.audio not available. Speaker diarization will be disabled.")
            
        return whisper_model, diarization_pipeline
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return None, None

@st.cache_data
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
        st.error(f"Error loading code databases: {e}")
        return None, None

def find_speaker(segment_start, segment_end, diarization_result):
    """Find speaker for a given time segment based on diarization"""
    if diarization_result is None:
        return "Unknown Speaker"
    
    for turn, _, speaker in diarization_result.itertracks(yield_label=True):
        if max(segment_start, turn.start) < min(segment_end, turn.end):
            return speaker
    return "Unknown Speaker"

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

def process_audio_file(audio_file, whisper_model, diarization_pipeline):
    """Process audio file for transcription and diarization"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_file.read())
            tmp_path = tmp_file.name
        
        # Transcribe with Whisper
        with st.spinner("Transcribing audio..."):
            result = whisper_model.transcribe(tmp_path)
        
        # Run diarization if available
        diarization_result = None
        if diarization_pipeline:
            with st.spinner("Performing speaker diarization..."):
                diarization_result = diarization_pipeline(tmp_path)
        
        # Process segments
        segments = result["segments"]
        processed_segments = []
        
        for segment in segments:
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()
            
            # Find speaker using diarization or fallback to alternating
            if diarization_result:
                speaker_label = find_speaker(start, end, diarization_result)
            else:
                # Fallback to alternating speakers
                speaker_label = "SPEAKER_00"  # Simplified for demo
            
            processed_segments.append({
                "start": start,
                "end": end,
                "text": text,
                "speaker": speaker_label
            })
        
        # Clean up temporary file
        os.unlink(tmp_path)
        
        return processed_segments, result["text"]
        
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None, None

def create_waveform_plot(audio_data, sample_rate):
    """Create waveform visualization"""
    if not LIBROSA_AVAILABLE:
        st.warning("⚠️ Librosa not available. Cannot create waveform visualization.")
        return None
        
    try:
        # Create time axis
        time = np.linspace(0, len(audio_data) / sample_rate, len(audio_data))
        
        # Create waveform plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time,
            y=audio_data,
            mode='lines',
            name='Waveform',
            line=dict(color='#1f77b4', width=1)
        ))
        
        fig.update_layout(
            title="Audio Waveform",
            xaxis_title="Time (seconds)",
            yaxis_title="Amplitude",
            height=200,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False
        )
        
        return fig
    except Exception as e:
        st.error(f"Error creating waveform: {e}")
        return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🏥 Real-Time ICD/CPT Code Generation</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #666;">Speech-to-Code AI for Doctor-Patient Conversations</p>', unsafe_allow_html=True)
    
    # Load models and databases
    whisper_model, diarization_pipeline = load_models()
    icd_df, cpt_df = load_code_databases()
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header">📁 Audio Input</div>', unsafe_allow_html=True)
        
        # Audio upload
        uploaded_file = st.file_uploader(
            "Upload Audio File",
            type=['wav', 'mp3', 'm4a'],
            help="Upload a doctor-patient conversation audio file"
        )
        
        # Live recording option
        st.markdown("---")
        st.markdown('<div class="sidebar-header">🎤 Live Recording</div>', unsafe_allow_html=True)
        
        # Note: Streamlit doesn't have built-in audio recording, so we'll use a placeholder
        if st.button("🎙️ Start Recording", type="primary"):
            st.info("Live recording feature requires additional setup with microphone access. For now, please upload an audio file.")
        
        # Processing controls
        st.markdown("---")
        st.markdown('<div class="sidebar-header">⚙️ Processing Options</div>', unsafe_allow_html=True)
        
        use_diarization = st.checkbox("Use Speaker Diarization", value=PYANNOTE_AVAILABLE, 
                                    disabled=not PYANNOTE_AVAILABLE,
                                    help="Separate doctor and patient voices (requires HF token)")
        
        confidence_threshold = st.slider("Code Confidence Threshold", 0, 100, 70,
                                       help="Minimum confidence score for code suggestions")
        
        # Process button
        if st.button("🚀 Process Audio", type="primary", disabled=not uploaded_file):
            if uploaded_file is not None:
                st.session_state.audio_file = uploaded_file
                st.session_state.processing_complete = False
                
                # Store audio data for waveform visualization
                if LIBROSA_AVAILABLE:
                    try:
                        # Save uploaded file to temporary file for librosa to read
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name
                        
                        # Load audio data using the temporary file
                        audio_data, sample_rate = librosa.load(tmp_path, sr=None)
                        
                        # Clean up temporary file
                        os.unlink(tmp_path)
                        
                        # Store in session state
                        st.session_state.audio_data = audio_data
                        st.session_state.audio_sample_rate = sample_rate
                        
                        # Reset file pointer for processing
                        uploaded_file.seek(0)
                    except Exception as e:
                        st.warning(f"Could not load audio for visualization: {e}")
                        st.session_state.audio_data = None
                        st.session_state.audio_sample_rate = None
                
                st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Audio processing and transcription
        if st.session_state.audio_file is not None and not st.session_state.processing_complete:
            with st.spinner("Processing audio file..."):
                # Process the audio
                segments, full_text = process_audio_file(
                    st.session_state.audio_file, 
                    whisper_model, 
                    diarization_pipeline if use_diarization else None
                )
                
                if segments:
                    st.session_state.transcription_data = segments
                    
                    # Extract medical keywords
                    medical_terms = extract_medical_keywords(full_text)
                    
                    # Generate codes
                    all_icd_codes = []
                    all_cpt_codes = []
                    
                    for term in medical_terms:
                        icd_matches, cpt_matches = get_codes_from_symptom(
                            term["term"], icd_df, cpt_df, top_n=3
                        )
                        
                        for match in icd_matches:
                            if match["confidence"] >= confidence_threshold:
                                all_icd_codes.append({
                                    **match,
                                    "source_term": term["term"],
                                    "category": term["category"]
                                })
                        
                        for match in cpt_matches:
                            if match["confidence"] >= confidence_threshold:
                                all_cpt_codes.append({
                                    **match,
                                    "source_term": term["term"],
                                    "category": term["category"]
                                })
                    
                    st.session_state.icd_codes = all_icd_codes
                    st.session_state.cpt_codes = all_cpt_codes
                    st.session_state.processing_complete = True
                    st.success("✅ Audio processing completed!")
                    st.rerun()
        
        # Display results
        if st.session_state.processing_complete and st.session_state.transcription_data:
            # Waveform visualization
            if (st.session_state.audio_data is not None and 
                st.session_state.audio_sample_rate is not None and 
                LIBROSA_AVAILABLE):
                st.markdown("### 📊 Audio Waveform")
                waveform_fig = create_waveform_plot(st.session_state.audio_data, st.session_state.audio_sample_rate)
                if waveform_fig:
                    st.plotly_chart(waveform_fig, use_container_width=True)
            
            # Transcription
            st.markdown("### 📝 Conversation Transcription")
            
            doctor_text = []
            patient_text = []
            
            for segment in st.session_state.transcription_data:
                text = segment["text"]
                speaker = segment["speaker"]
                
                if "SPEAKER_00" in speaker or speaker == "doctor":
                    doctor_text.append(text)
                else:
                    patient_text.append(text)
            
            # Doctor transcription
            if doctor_text:
                st.markdown('<div class="transcription-box doctor-text">', unsafe_allow_html=True)
                st.markdown("**👨‍⚕️ Doctor:**")
                st.write(" ".join(doctor_text))
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Patient transcription
            if patient_text:
                st.markdown('<div class="transcription-box patient-text">', unsafe_allow_html=True)
                st.markdown("**👤 Patient:**")
                st.write(" ".join(patient_text))
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed transcription with timestamps
            with st.expander("📋 Detailed Transcription with Timestamps"):
                for segment in st.session_state.transcription_data:
                    speaker_icon = "👨‍⚕️" if "SPEAKER_00" in segment["speaker"] else "👤"
                    st.write(f"[{segment['start']:.1f}s - {segment['end']:.1f}s] {speaker_icon} {segment['text']}")
    
    with col2:
        # Metrics
        st.markdown("### 📊 Processing Metrics")
        
        if st.session_state.transcription_data:
            total_segments = len(st.session_state.transcription_data)
            total_duration = sum([seg["end"] - seg["start"] for seg in st.session_state.transcription_data])
            
            col_metric1, col_metric2 = st.columns(2)
            with col_metric1:
                st.metric("Segments", total_segments)
            with col_metric2:
                st.metric("Duration", f"{total_duration:.1f}s")
        
        # ICD-10 Codes
        if st.session_state.icd_codes:
            st.markdown("### 🩺 ICD-10 Codes")
            
            icd_df_display = pd.DataFrame(st.session_state.icd_codes)
            if not icd_df_display.empty:
                icd_df_display = icd_df_display.sort_values('confidence', ascending=False)
                
                for _, row in icd_df_display.head(6).iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="code-table">
                            <strong>Code:</strong> {row['code']}<br>
                            <strong>Description:</strong> {row['description']}<br>
                            <strong>Confidence:</strong> {row['confidence']}%<br>
                            <strong>Source:</strong> {row['source_term']} ({row['category']})
                        </div>
                        """, unsafe_allow_html=True)
                        st.write("")
        
        # CPT Codes
        if st.session_state.cpt_codes:
            st.markdown("### 🛠️ CPT Codes")
            
            cpt_df_display = pd.DataFrame(st.session_state.cpt_codes)
            if not cpt_df_display.empty:
                cpt_df_display = cpt_df_display.sort_values('confidence', ascending=False)
                
                for _, row in cpt_df_display.head(6).iterrows():
                    with st.container():
                        st.markdown(f"""
                        <div class="code-table">
                            <strong>Code:</strong> {row['code']}<br>
                            <strong>Description:</strong> {row['description']}<br>
                            <strong>Confidence:</strong> {row['confidence']}%<br>
                            <strong>Source:</strong> {row['source_term']} ({row['category']})
                        </div>
                        """, unsafe_allow_html=True)
                        st.write("")
    
    # Bottom section for downloads and actions
    if st.session_state.processing_complete:
        st.markdown("---")
        col_download1, col_download2, col_download3 = st.columns(3)
        
        with col_download1:
            if st.session_state.icd_codes or st.session_state.cpt_codes:
                # Prepare data for download
                results_data = {
                    "timestamp": datetime.now().isoformat(),
                    "icd_codes": st.session_state.icd_codes,
                    "cpt_codes": st.session_state.cpt_codes,
                    "transcription": st.session_state.transcription_data
                }
                
                json_str = json.dumps(results_data, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"medical_codes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col_download2:
            if st.session_state.icd_codes or st.session_state.cpt_codes:
                # Create CSV for codes
                all_codes = []
                for code in st.session_state.icd_codes:
                    all_codes.append({
                        "Type": "ICD-10",
                        "Code": code["code"],
                        "Description": code["description"],
                        "Confidence": code["confidence"],
                        "Source_Term": code["source_term"],
                        "Category": code["category"]
                    })
                
                for code in st.session_state.cpt_codes:
                    all_codes.append({
                        "Type": "CPT",
                        "Code": code["code"],
                        "Description": code["description"],
                        "Confidence": code["confidence"],
                        "Source_Term": code["source_term"],
                        "Category": code["category"]
                    })
                
                if all_codes:
                    df_codes = pd.DataFrame(all_codes)
                    csv = df_codes.to_csv(index=False)
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv,
                        file_name=f"medical_codes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with col_download3:
            if st.button("☁️ Submit to Database", type="secondary"):
                st.info("Database submission feature would be implemented here. This is a placeholder for cloud storage integration.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🔬 Speech-to-Code AI | Real-Time Medical Code Generation</p>
        <p>Built with Streamlit, Whisper, and Pyannote.audio</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 