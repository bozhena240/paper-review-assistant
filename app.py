import hashlib
import re

import streamlit as st

from extract_pdf import extract_text


st.title("Paper Review Assistant")
st.write("Upload a PDF to extract and view its text.")

uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    try:
        file_id = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
        if st.session_state.get("file_id") != file_id:
            st.session_state.file_id = file_id
            st.session_state.extracted_text = extract_text(uploaded_file)
            st.session_state.paragraphs = []
            st.session_state.paragraph_version = 0

        st.subheader("Extracted text")
        st.caption("Check the text and separate paragraphs with a blank line.")
        text = st.text_area(
            "Paper contents", key="extracted_text", height=350
        )

        if st.button("Split into paragraphs"):
            st.session_state.paragraphs = [
                part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()
            ]
            st.session_state.paragraph_version += 1

        if st.session_state.paragraphs:
            st.subheader("Paragraphs and prompts")
            st.caption("Edit each paragraph and give it its own review instruction.")
            version = st.session_state.paragraph_version
            for index, paragraph in enumerate(st.session_state.paragraphs, start=1):
                st.text_area(
                    f"Paragraph {index}",
                    value=paragraph,
                    key=f"paragraph_{version}_{index}",
                )
                st.text_area(
                    f"Prompt for paragraph {index}",
                    key=f"prompt_{version}_{index}",
                    placeholder="For example: Check whether the argument is clear.",
                )
    except Exception as error:
        st.error(f"Could not process this PDF: {error}")
