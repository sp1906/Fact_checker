import streamlit as st
import pdfplumber
from groq import Groq
import re

st.set_page_config(page_title="PDF Fact Checker", layout="wide")
st.title("PDF Fact Checker")

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception as e:
    st.error(f"Error loading Groq API key: {e}")
    st.stop()

MODEL_ID = "llama-3.1-8b-instant"
st.success(f"Using model: {MODEL_ID}")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def split_into_claims(text):
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    return [s.strip() for s in sentences if s.strip()]

if uploaded_file:
    st.info("Extracting text from PDF...")
    pdf_text = extract_text_from_pdf(uploaded_file)
    st.success("Text extracted!")

    st.subheader("PDF Text Preview")
    st.text(pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text)

    
    claims = split_into_claims(pdf_text)

    st.subheader("Verifying each claim:")

    for i, claim in enumerate(claims, 1):
        st.markdown(f"**Claim {i}:** {claim}")
        try:
            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": "You are a fact-checker. Verify the following claim and reply with TRUE, FALSE, or UNCERTAIN, and a short explanation."},
                    {"role": "user", "content": claim}
                ]
            )
            answer = response.choices[0].message.content
            st.write(f"**Fact-Check:** {answer}")
        except Exception as e:
            st.error(f"Error verifying claim: {e}")

else:
    st.info("Please upload a PDF file to start fact-checking.")
