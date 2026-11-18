import streamlit as st

from extract_pdf import extract_text


st.title("Paper Review Assistant")
st.write("Upload a PDF to extract and view its text.")

uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    try:
        text = extract_text(uploaded_file)
        st.subheader("Extracted text")
        st.text_area("Paper contents", text, height=500)
        st.caption("Check the extracted text: PDF layouts can affect the result.")
    except Exception as error:
        st.error(f"Could not read this PDF: {error}")
