# Paper Review Assistant

A Python application that uses a large language model to help review academic papers. Upload a PDF, review the full text or individual sections with custom prompts, and download the feedback as a text file.

## Setup

Requires Python 3.10 or newer, an internet connection, and an API key from either [Gemini](https://aistudio.google.com/api-keys) or [DeepSeek](https://platform.deepseek.com/). Check the provider’s availability and pricing before use.

```bash
git clone https://github.com/bozhena240/paper-review-assistant.git
cd paper-review-assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

On Windows, activate the environment using `.venv\Scripts\activate` instead. Open the local URL shown in the terminal if the app does not open automatically.

## How to use

1. Select Gemini or DeepSeek, enter that provider’s API key in the sidebar, and upload a PDF.
2. Check and, if needed, edit the extracted text.
3. Request a whole-paper review or split the text into sections and enter a prompt for each section.
4. Generate reviews and download the available feedback as a `.txt` file.

## Limitations

- AI-generated feedback can be incorrect and should be checked by a human.
- Text extraction and paragraph detection depend on the PDF layout. Scanned or image-only PDFs require OCR, which is not currently supported.
- Whole-paper reviews are limited to 200,000 characters in this version. The app does not automatically process longer papers in chunks.
- API access depends on the chosen provider, account access, and quota. Mainland China is not on Google’s [Gemini supported-region list](https://ai.google.dev/gemini-api/docs/available-regions). DeepSeek was tested with an API key, but access from mainland China has not been independently verified.
- Reviews are kept in the current session; download them before closing or restarting the app.
