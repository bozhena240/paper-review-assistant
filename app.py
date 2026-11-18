import hashlib

import httpx
import streamlit as st
from google.genai import errors

from extract_pdf import extract_text
from reviewer import review_text
from split_text import split_into_paragraphs, split_into_sections


# This app limit keeps requests manageable; it is not the model's token limit.
MAX_PAPER_CHARACTERS = 200_000


def generate_review(api_key: str, text: str, prompt: str) -> str | None:
    try:
        with st.spinner("Generating review..."):
            return review_text(api_key.strip(), text, prompt)
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
    return None


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
        st.caption("Suggested paragraph breaks are marked with blank lines. "
                   "Check and edit them before splitting; PDF layouts vary.")
        text = st.text_area(
            "Paper contents", key="extracted_text", height=350
        )

        st.subheader("Whole-paper review")
        st.caption("Reviews the current text above, including any edits. "
                   "Check that all pages were extracted before reviewing.")
        if "[No text found]" in text:
            st.warning("Some pages may have no extractable text. Check the paper contents "
                       "above; image-based pages may need OCR.")
        whole_prompt = st.text_area(
            "Instruction for the whole paper",
            value=("Summarize the paper, identify its strengths and potential weaknesses, "
                   "and suggest specific improvements. Acknowledge any uncertainty."),
            key=f"whole_prompt_{file_id}",
        )
        whole_review_key = f"whole_review_{file_id}"
        if st.button("Review full paper"):
            if not api_key.strip():
                st.warning("Enter a Gemini API key in the sidebar first.")
            elif not text.strip() or not whole_prompt.strip():
                st.warning("Enter both the paper text and a review instruction.")
            elif len(text) > MAX_PAPER_CHARACTERS:
                st.warning(f"This version supports up to {MAX_PAPER_CHARACTERS:,} characters "
                           "for a whole-paper review. The text was not sent. "
                           "Review shorter sections instead.")
            else:
                result = generate_review(api_key, text, whole_prompt)
                if result is not None:
                    st.session_state[whole_review_key] = {
                        "text": result, "paper": text, "prompt": whole_prompt
                    }
        if whole_review_key in st.session_state:
            review = st.session_state[whole_review_key]
            if review["paper"] != text or review["prompt"] != whole_prompt:
                st.caption("The paper text or instruction has changed since this review was generated.")
            st.markdown("**Whole-paper review**")
            st.write(review["text"])

        st.subheader("Split paper for individual reviews")
        split_mode = st.radio(
            "How would you like to split the text?",
            ("Choose the number of sections", "Use detected paragraphs"),
        )
        section_count = 2
        if split_mode == "Choose the number of sections":
            section_count = st.number_input(
                "Number of sections", min_value=1, max_value=20, value=2, step=1
            )
            st.caption("Nearby paragraphs are grouped into roughly balanced sections.")
        st.caption("Splitting again resets the existing section edits, prompts, and reviews.")
        if st.button("Split text"):
            try:
                if split_mode == "Use detected paragraphs":
                    parts = split_into_paragraphs(text)
                    part_label = "Paragraph"
                else:
                    parts = split_into_sections(text, section_count)
                    part_label = "Section"
                if parts:
                    st.session_state.paragraphs = parts
                    st.session_state.part_label = part_label
                    st.session_state.paragraph_version += 1
                else:
                    st.warning("There is no text to split.")
            except ValueError as error:
                st.warning(str(error))

        if st.session_state.paragraphs:
            st.subheader("Sections and prompts")
            st.caption("Edit each section and give it its own review instruction.")
            version = st.session_state.paragraph_version
            part_label = st.session_state.part_label
            for index, paragraph in enumerate(st.session_state.paragraphs, start=1):
                paragraph_text = st.text_area(
                    f"{part_label} {index}",
                    value=paragraph,
                    key=f"paragraph_{file_id}_{version}_{index}",
                )
                prompt_text = st.text_area(
                    f"Prompt for {part_label.lower()} {index}",
                    key=f"prompt_{file_id}_{version}_{index}",
                    placeholder="For example: Check whether the argument is clear.",
                )
                review_key = f"review_{file_id}_{version}_{index}"
                if st.button(f"Review {part_label.lower()} {index}", key=f"button_{file_id}_{version}_{index}"):
                    if not api_key.strip():
                        st.warning("Enter a Gemini API key in the sidebar first.")
                    elif not paragraph_text.strip() or not prompt_text.strip():
                        st.warning("Enter both the paragraph text and a review prompt.")
                    else:
                        result = generate_review(api_key, paragraph_text, prompt_text)
                        if result is not None:
                            st.session_state[review_key] = {
                                "text": result,
                                "paragraph": paragraph_text,
                                "prompt": prompt_text,
                            }

                if review_key in st.session_state:
                    review = st.session_state[review_key]
                    if review["paragraph"] != paragraph_text or review["prompt"] != prompt_text:
                        st.caption("The text or prompt has changed since this review was generated.")
                    st.markdown("**Review**")
                    st.write(review["text"])
    except Exception as error:
        st.error(f"Could not process this PDF: {error}")
