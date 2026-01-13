import streamlit as st

# IMPORTANT: set_page_config must be called before any other Streamlit commands
# This must come before importing modules that might use Streamlit
st.set_page_config(page_title="MedAssist AI", layout="wide")

# Now safe to import other modules
from llm import LLMClient, LLMError
from ocr import pdf_to_text, image_to_text, OCRError
from workflow import suggest_icd10, suggest_cpt
from pdf_builder import build_claim_pdf, PDFError
from PIL import Image
import tempfile
import os
import datetime

# Initialize LLM client with error handling
@st.cache_resource
def get_llm_client():
    """Get cached LLM client instance."""
    try:
        return LLMClient()
    except LLMError as e:
        st.error(f"LLM initialization failed: {e}")
        return None

llm = get_llm_client()

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("MedAssist AI – Medical Coding Assistant")
st.markdown("AI-powered medical document processing, coding, and claim generation.")

page = st.sidebar.radio("Navigation", ["Chat", "Upload & OCR", "Code Suggestion", "Claim Generator", "About"])


# ==========================================================================================
# CHAT PAGE
# ==========================================================================================
if page == "Chat":
    st.header("Chat with the AI")

    mode = st.selectbox(
        "AI Mode",
        ["General Assistant", "Medical Assistant", "Coding Assistant", "Clinical Summarizer"]
    )

    SYSTEM_PROMPTS = {
        "General Assistant": "You are a helpful, balanced AI assistant.",
        "Medical Assistant": "You are a medical assistant. Explain medically, clearly, and avoid hallucinations.",
        "Coding Assistant": "You are a coding mentor. Explain with examples, avoid hallucinating code.",
        "Clinical Summarizer": "You summarize clinical documents, extract diagnoses, procedures, and clinical intent."
    }

    GLOBAL_BEHAVIOR = """
    Always follow the selected assistant role.
    Use the chat history to answer follow-up questions naturally.
    Do NOT reset context unless the user starts a new chat.
    """

    system_prompt = SYSTEM_PROMPTS[mode]

    if st.button("New Chat 🧹"):
        st.session_state.messages = []
        st.rerun()

    theme = st.get_option("theme.base")
    is_dark = theme == "dark"

    USER_BG = "#A3BE8C" if is_dark else "#DFF0FF"
    AI_BG = "#4C566A" if is_dark else "#F0F0F0"
    TEXT_COLOR = "#ECEFF4" if is_dark else "#000000"

    # Space for sticky footer
    st.markdown("<div style='height:70px;'></div>", unsafe_allow_html=True)


    # --------------------- DISPLAY CHAT HISTORY ---------------------
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        align = "flex-end" if is_user else "flex-start"
        bubble_color = USER_BG if is_user else AI_BG

        st.markdown(
            f"""
            <div style="display:flex; justify-content:{align}; margin:8px 0; width:100%;">
                <div style="
                    max-width:65%;
                    display: inline-block;
                    background-color:{bubble_color};
                    padding:14px 18px;
                    border-radius:14px;
                    color:{TEXT_COLOR};
                    font-size:15.5px;
                    line-height:1.45;
                    word-wrap:break-word;
                    overflow-wrap:break-word;
                ">
                    <b>{'You' if is_user else 'AI'}:</b><br>{msg['text']}
                    <div style="font-size:10.5px; opacity:0.65; margin-top:6px; text-align:right;">
                        {msg['time']}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")


    # --------------------- STICKY INPUT BAR ---------------------
    st.markdown(
        """
        <style>
        .sticky-input {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 14px 22px;
            background: rgba(250,250,250,1);
            border-top: 1px solid #ccc;
            z-index: 9999;
        }
        .sticky-input-dark {
            background: rgba(20,20,20,1);
            border-top: 1px solid #444;
        }
        .main-container { padding-bottom: 120px !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<script>document.body.classList.add('main-container')</script>",
                unsafe_allow_html=True)

    input_class = "sticky-input-dark" if is_dark else "sticky-input"
    st.markdown(f"<div class='{input_class}'>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            "",
            placeholder="Ask something, for example: What is pneumonia?"
        )
        submitted = st.form_submit_button("Send")

    st.markdown("</div>", unsafe_allow_html=True)


    # --------------------- PROCESS USER MESSAGE ---------------------
    if submitted and user_input.strip():

        # Save user's message
        st.session_state.messages.append({
            "role": "user",
            "text": user_input,
            "time": datetime.datetime.now().strftime("%H:%M")
        })

        # Build full conversation for LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": GLOBAL_BEHAVIOR}
        ]

        # Add history
        for msg in st.session_state.messages:
            messages.append({
                "role": msg["role"],
                "content": msg["text"]
            })

        # Call LLM with error handling
        with st.spinner("Thinking..."):
            if llm is None:
                reply = "LLM is not configured. Please set GROQ_API_KEY in your environment or .env file."
            else:
                try:
                    reply = llm.ask(messages)
                except LLMError as e:
                    reply = f"Sorry, I encountered an error: {e}"

        # Save assistant reply
        st.session_state.messages.append({
            "role": "assistant",
            "text": reply,
            "time": datetime.datetime.now().strftime("%H:%M")
        })

        st.rerun()



# ==========================================================================================
# UPLOAD AND OCR PAGE
# ==========================================================================================
elif page == "Upload & OCR":
    st.header("Extract Text from PDF or Image")
    
    # Check if running on Streamlit Cloud
    import os
    is_streamlit_cloud = os.environ.get("STREAMLIT_SERVER_ENVIRONMENT") == "cloud"
    
    if is_streamlit_cloud:
        st.warning("⚠️ **OCR features are not available on Streamlit Cloud.**\n\n"
                  "OCR requires local installation of Tesseract and Poppler. "
                  "Please run the app locally to use OCR features. "
                  "All other features (Chat, Code Suggestion, Claim Generator) work on Streamlit Cloud.")
        st.info("💡 **Tip:** You can still use the Chat feature to analyze text you paste manually.")
    else:
        st.caption("Upload a scanned document to extract text using OCR.")

    uploaded = st.file_uploader("Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"], disabled=is_streamlit_cloud)
    if uploaded and not is_streamlit_cloud:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded.name)[1]) as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        with st.spinner("Running OCR..."):
            try:
                if uploaded.type == "application/pdf":
                    text = pdf_to_text(tmp_path)
                else:
                    img = Image.open(tmp_path)
                    text = image_to_text(img)
                
                if text:
                    st.subheader("Extracted Text")
                    st.text_area("OCR Output", text, height=250)
                    
                    st.subheader("AI Summary")
                    if llm is None:
                        st.warning("LLM not configured. Set GROQ_API_KEY to enable AI summaries.")
                    else:
                        with st.spinner("Summarizing..."):
                            try:
                                summary = llm.ask([
                                    {"role": "system", "content": "You are a clinical summarizer. Extract key diagnoses, procedures, and clinical findings."},
                                    {"role": "user", "content": f"Summarize and extract diagnoses from this OCR text:\n{text[:4000]}"},
                                ])
                                st.write(summary)
                            except LLMError as e:
                                st.error(f"Failed to generate summary: {e}")
                else:
                    st.warning("No text could be extracted from the document.")
                    
            except OCRError as e:
                st.error(f"OCR failed: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
# ==========================================================================================
# CODE SUGGESTION PAGE
# ==========================================================================================
elif page == "Code Suggestion":
    st.header("ICD-10 / CPT-4 Code Suggestions")
    st.caption("Enter a clinical description to find matching medical codes.")

    query = st.text_input("Describe diagnosis or procedure:", placeholder="e.g., fever, chest pain, appendectomy")

    col1, col2 = st.columns(2)
    with col1:
        method = st.selectbox("Search method", ["hybrid (semantic + fuzzy)", "semantic only", "fuzzy only"])
    with col2:
        topk = st.slider("Top K", 1, 10, 5)

    def format_score(score, method_type):
        """Format score for display with confidence indicator."""
        if method_type == "semantic":
            # Cosine similarity: 0-1 range
            pct = score * 100
            if score >= 0.5:
                return f"{pct:.1f}% (High)"
            elif score >= 0.35:
                return f"{pct:.1f}% (Medium)"
            else:
                return f"{pct:.1f}% (Low)"
        else:
            # Fuzzy score: 0-100 range
            if score >= 80:
                return f"{score}% (High)"
            elif score >= 60:
                return f"{score}% (Medium)"
            else:
                return f"{score}% (Low)"

    col_icd, col_cpt = st.columns(2)
    
    with col_icd:
        if st.button("Suggest ICD-10", use_container_width=True):
            if not query.strip():
                st.warning("Please enter a description or clinical text.")
            else:
                with st.spinner("Searching ICD-10..."):
                    try:
                        m = "hybrid" if method.startswith("hybrid") else \
                            ("semantic" if method.startswith("semantic") else "fuzzy")
                        icd_results = suggest_icd10(query, limit=topk, method=m)
                        
                        if icd_results:
                            st.subheader("ICD-10 suggestions")
                            for code, desc, score in icd_results:
                                score_display = format_score(score, "semantic" if m != "fuzzy" else "fuzzy")
                                st.markdown(f"**{code}** - {desc}")
                                st.caption(f"Confidence: {score_display}")
                        else:
                            st.info("No matching ICD-10 codes found.")
                    except Exception as e:
                        st.error(f"Search failed: {e}")

    with col_cpt:
        if st.button("Suggest CPT-4", use_container_width=True):
            if not query.strip():
                st.warning("Please enter a description or clinical text.")
            else:
                with st.spinner("Searching CPT-4..."):
                    try:
                        m = "hybrid" if method.startswith("hybrid") else \
                            ("semantic" if method.startswith("semantic") else "fuzzy")
                        cpt_results = suggest_cpt(query, limit=topk, method=m)
                        
                        if cpt_results:
                            st.subheader("CPT-4 suggestions")
                            for code, desc, score in cpt_results:
                                score_display = format_score(score, "semantic" if m != "fuzzy" else "fuzzy")
                                st.markdown(f"**{code}** - {desc}")
                                st.caption(f"Confidence: {score_display}")
                        else:
                            st.info("No matching CPT-4 codes found.")
                    except Exception as e:
                        st.error(f"Search failed: {e}")


# ==========================================================================================
# CLAIM GENERATOR PAGE
# ==========================================================================================
elif page == "Claim Generator":
    st.header("Generate Claim PDF")
    st.caption("Create a PDF summary with patient info and medical codes.")

    with st.form("claim_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Patient Name")
            dob = st.date_input("DOB", datetime.date(1990, 1, 1))
        with col2:
            insurance = st.text_input("Insurance Provider")
            policy = st.text_input("Policy Number")
        
        diag = st.text_area("ICD-10 Codes (comma separated)", placeholder="e.g., R50.9, J06.9")
        proc = st.text_area("CPT-4 Codes (comma separated)", placeholder="e.g., 99213, 99214")
        submit = st.form_submit_button("Generate PDF")

    if submit:
        if not name.strip():
            st.warning("Please enter a patient name.")
        else:
            patient = {
                "name": name,
                "dob": dob.strftime("%Y-%m-%d"),
                "insurance": insurance,
                "policy": policy
            }
            diagnoses = [d.strip() for d in diag.split(",") if d.strip()]
            procedures = [p.strip() for p in proc.split(",") if p.strip()]

            try:
                output_path = os.path.join(
                    tempfile.gettempdir(), 
                    f"claim_{int(datetime.datetime.now().timestamp())}.pdf"
                )
                build_claim_pdf(output_path, patient, diagnoses, procedures)

                st.success("Claim PDF generated successfully!")
                with open(output_path, "rb") as f:
                    st.download_button(
                        "Download PDF", 
                        f, 
                        file_name=f"claim_{name.replace(' ', '_')}.pdf", 
                        mime="application/pdf"
                    )
            except PDFError as e:
                st.error(f"Failed to generate PDF: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


# ==========================================================================================
# ABOUT PAGE
# ==========================================================================================
elif page == "About":
    st.header("About MedAssist AI")
    
    st.markdown("""
### Overview
MedAssist AI is a medical automation prototype that helps healthcare professionals with:

- **Document Processing**: Extract text from scanned medical documents using OCR
- **Medical Coding**: Find ICD-10 and CPT-4 codes using AI-powered semantic search
- **Clinical Summaries**: Generate AI summaries of clinical documents
- **Claim Generation**: Create PDF claim summaries

### Technology Stack
| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| LLM | Groq (Llama 3.3 70B) |
| Embeddings | Bio_ClinicalBERT |
| OCR | Tesseract + Poppler |
| Search | Semantic + Fuzzy hybrid |

### How Code Search Works
1. **Semantic Search**: Uses Bio_ClinicalBERT embeddings to find codes based on clinical meaning
2. **Fuzzy Matching**: Falls back to text similarity when semantic confidence is low
3. **Hybrid Mode**: Combines both approaches for best results

### Data Sources
- **ICD-10**: International Classification of Diseases, 10th Revision
- **CPT-4**: Current Procedural Terminology codes

---
*Built as a portfolio demonstration project.*
    """)
