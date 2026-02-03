import base64
import streamlit as st
import os
import io
from PIL import Image 
import pdf2image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

POPPLER_PATH = r'C:\poppler\Library\bin' 

def get_gemini_response(input_prompt, pdf_content, job_description):
    try:
        # --- AUTO-DETECT MODEL NAME ---
        # Hum saare models check karenge aur jo 'flash' se match karega wo utha lenge
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Flash model dhoondne ki koshish
        model_name = "models/gemini-1.5-flash" # Default
        for m in available_models:
            if "flash" in m.lower():
                model_name = m
                break
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content([input_prompt, pdf_content[0], job_description])
        return response.text
    except Exception as e:
        return f"Google AI Error: {str(e)}"

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            images = pdf2image.convert_from_bytes(uploaded_file.read(), poppler_path=POPPLER_PATH)
            first_page = images[0]
            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [
                {
                    "mime_type": "image/jpeg",
                    "data": base64.b64encode(img_byte_arr).decode() 
                }
            ]
            return pdf_parts
        except Exception as e:
            st.error(f"PDF Error: {e}")
            return None
    return None

## --- Streamlit UI ---
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

submit1 = st.button("Analyze Resume")
submit3 = st.button("Percentage Match")

input_prompt1 = "Review this resume against the JD and highlight strengths/weaknesses."
input_prompt3 = "Give me the match percentage, missing keywords and final summary."

if submit1 or submit3:
    prompt = input_prompt1 if submit1 else input_prompt3
    if uploaded_file and input_text:
        pdf_content = input_pdf_setup(uploaded_file)
        if pdf_content:
            with st.spinner("Processing..."):
                response = get_gemini_response(prompt, pdf_content, input_text)
                st.subheader("Result:")
                st.write(response)
    else:
        st.warning("Please upload PDF and Job Description")