import hashlib
import re

import httpx
import streamlit as st
from google.genai import errors

from extract_pdf import extract_text
from reviewer import review_paragraph


st.title("Paper Review Assistant")
st.write("Upload a PDF to extract and view its text.")

with st.sidebar:
    st.subheader("Gemini API key")
    api_key = st.text_input("API key", type="password")
    st.caption("The key is kept in this app session and is not saved to the project.")
    st.caption("Review requests send the selected text and prompt to Google. "
               "Free-tier content may be used to improve Google products.")

uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

if uploaded_file is not None:
    try:
        file_id = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
        if st.session_state.get("file_id") != file_id:
            st.session_state.extracted_text = extract_text(uploaded_file)
            st.session_state.file_id = file_id
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
                paragraph_text = st.text_area(
                    f"Paragraph {index}",
                    value=paragraph,
                    key=f"paragraph_{file_id}_{version}_{index}",
                )
                prompt_text = st.text_area(
                    f"Prompt for paragraph {index}",
                    key=f"prompt_{file_id}_{version}_{index}",
                    placeholder="For example: Check whether the argument is clear.",
                )
                review_key = f"review_{file_id}_{version}_{index}"
                if st.button(f"Review paragraph {index}", key=f"button_{file_id}_{version}_{index}"):
                    if not api_key.strip():
                        st.warning("Enter a Gemini API key in the sidebar first.")
                    elif not paragraph_text.strip() or not prompt_text.strip():
                        st.warning("Enter both the paragraph text and a review prompt.")
                    else:
                        try:
                            with st.spinner("Generating review..."):
                                result = review_paragraph(api_key.strip(), paragraph_text, prompt_text)
                            st.session_state[review_key] = {
                                "text": result,
                                "paragraph": paragraph_text,
                                "prompt": prompt_text,
                            }
                        except errors.APIError as error:
                            if error.code == 429:
                                st.error("Gemini's rate or usage limit was reached (429). "
                                         "Wait a minute and try again. If it continues, "
                                         "check your quota in Google AI Studio.")
                            elif error.code in (401, 403):
                                st.error(f"Gemini rejected access ({error.code}). "
                                         "Check the API key and model access in Google AI Studio.")
                            elif error.code >= 500:
                                st.error(f"Gemini is temporarily unavailable ({error.code}). "
                                         "Please try again later.")
                            else:
                                st.error(f"Gemini returned an error (code {error.code}). "
                                         "Check the model and request settings.")
                        except httpx.RequestError:
                            st.error("Could not connect to Gemini. Check your internet connection "
                                     "and try again.")
                        except Exception as error:
                            st.error(f"The review failed ({type(error).__name__}). Please try again.")

                if review_key in st.session_state:
                    review = st.session_state[review_key]
                    if review["paragraph"] != paragraph_text or review["prompt"] != prompt_text:
                        st.caption("The text or prompt has changed since this review was generated.")
                    st.markdown("**Review**")
                    st.write(review["text"])
    except Exception as error:
        st.error(f"Could not process this PDF: {error}")
