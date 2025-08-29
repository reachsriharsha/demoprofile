import gradio as gr
import os
import shutil
import uuid
import camelot
import re
import io
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import logging
import traceback

# --- State Management ---
# Using a dictionary for a more structured state
app_state = {
    "user_email": "",
    "current_page": "login"
}

# --- Event Handlers ---

def handle_email_submit(email):
    """Handle email submission and navigate to the home page."""
    if email and "@" in email and "." in email:
        app_state["user_email"] = email
        app_state["current_page"] = "home"
        # Hide login, show home
        return (
            gr.update(visible=False),
            gr.update(visible=True),
            f"Welcome, {email}!"
        )
    else:
        # Stay on login, show error
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            "Please enter a valid email address."
        )

def show_app_page(app_name):
    """Navigate from home to a specific application page."""
    app_state["current_page"] = f"app_{app_name}"
    # Hide home, show the generic app page with updated content
    return (
        gr.update(visible=False), # home_page
        gr.update(visible=True),  # app_page
        f"📱 {app_name}",
        f"This is the placeholder for the '{app_name}' application. You can build its specific UI here."
    )

def go_home():
    """Navigate back to the home page from an app page."""
    app_state["current_page"] = "home"
    # Hide app page, show home
    return (
        gr.update(visible=False), # app_page
        gr.update(visible=True)   # home_page
    )

def handle_pdf_upload(pdf_file, progress=gr.Progress(track_tqdm=True)):
    """Handle PDF file upload, save it, and extract content with progress."""
    progress(0, desc="Starting PDF processing...")
    if not pdf_file:
        # Return an update for the output components to clear and hide them.
        return (
            "Please upload a PDF file first.",
            gr.update(value="", visible=False),  # tables
            gr.update(value=None, visible=False), # images
            gr.update(value="", visible=False),   # contacts
            gr.update(selected=0)                 # tabs
        )

    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)

    try:
        # 1. Save the uploaded file
        progress(0.1, desc="Saving uploaded file...")
        original_filename = os.path.basename(pdf_file.name)
        random_prefix = uuid.uuid4().hex[:8]
        new_filename = f"{random_prefix}_{original_filename}"
        destination_path = os.path.join(upload_dir, new_filename)
        shutil.copy(pdf_file.name, destination_path)

        logging.info(f'File saving completed')
        # 2. Extract text and images with pdfminer.six
        progress(0.2, desc="Extracting text and images...")
        image_output_dir = os.path.join(upload_dir, f"{random_prefix}_images")
        os.makedirs(image_output_dir, exist_ok=True)
        
        text_output = io.BytesIO()
        with open(destination_path, 'rb') as fp:
            extract_text_to_fp(fp, text_output, output_dir=image_output_dir, laparams=LAParams())
        
        full_text = text_output.getvalue().decode(errors="ignore")
        text_output.close()
        logging.info(f'Text extraction completed')

        image_files = [f for f in os.listdir(image_output_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        extracted_images = [os.path.join(image_output_dir, f) for f in image_files]
        num_images = len(extracted_images)


        logging.info(f'Images extraction completed')
        # 3. Extract tables with Camelot
        progress(0.5, desc="Extracting tables (this may take a while)...")
        tables = camelot.read_pdf(destination_path, pages='all', flavor='stream')

        logging.info(f'Tables extraction completed')
        # 4. Extract Emails and Phone Numbers from the text
        progress(0.8, desc="Extracting contact information...")
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        found_emails = sorted(list(set(re.findall(email_regex, full_text))))
        num_emails = len(found_emails)

        phone_regex = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
        found_phones = sorted(list(set(re.findall(phone_regex, full_text))))
        num_phones = len(found_phones)
        # 5. Prepare status message
        logging.info(f'Email and phone extraction completed')

        progress(0.9, desc="Finalizing results...")
        status_parts = [f"✅ File **{original_filename}** uploaded successfully.\n"]
        if tables.n > 0:
            status_parts.append(f"\n- Found **{tables.n}** tables.")
        else:
            status_parts.append(f"\n- ℹ️ No tables found.")

        if num_images > 0:
            status_parts.append(f"\n- Found **{num_images}** images.")
        else:
            status_parts.append(f"\n- ℹ️ No images found.")

        if num_emails > 0:
            status_parts.append(f"\n- Found **{num_emails}** email(s).")

        if num_phones > 0:
            status_parts.append(f"\n- Found **{num_phones}** phone number(s).")

        if tables.n > 0 or num_images > 0 or num_emails > 0 or num_phones > 0:
            status_parts.append("\n\nCheck the other tabs for extracted content.")
        final_status = "".join(status_parts)

        # 6. Prepare HTML output for tables
        if tables.n > 0:
            table_html_parts = []
            for i, table in enumerate(tables):
                table_header = f"<h3>Table {i+1} (from Page {table.page})</h3>"
                table_dataframe_html = table.df.to_html(classes="gradio-dataframe", border=0)
                table_html_parts.append(table_header)
                table_html_parts.append(table_dataframe_html)
            full_html_output = "".join(table_html_parts)
            tables_update = gr.update(value=full_html_output, visible=True)
        else:
            tables_update = gr.update(value="", visible=False)

        # 7. Prepare images for gallery
        images_update = gr.update(value=extracted_images if num_images > 0 else None, visible=num_images > 0)

        # 8. Prepare markdown for contacts
        contacts_md_parts = []
        if num_emails > 0:
            contacts_md_parts.append("### Emails Found\n" + "\n".join(f"- `{email}`" for email in found_emails))
        if num_phones > 0:
            if contacts_md_parts:
                contacts_md_parts.append("\n---\n")
            contacts_md_parts.append("### Phone Numbers Found\n" + "\n".join(f"- `{phone}`" for phone in found_phones))
        
        if not contacts_md_parts:
            contacts_output_str = "ℹ️ No emails or phone numbers found in the document."
        else:
            contacts_output_str = "\n".join(contacts_md_parts)
        contacts_update = gr.update(value=contacts_output_str, visible=True)

        # 9. Return all updates
        # Keep focus on the summary tab after processing.
        return final_status, tables_update, images_update, contacts_update, gr.update(selected=0)
    except Exception as e:
        logging.error(f'An error occurred during processing, try other files: {str(e)}')
        traceback.print_exc()
        error_message = f"❌ An error occurred during processing, try other files"
        return (
            error_message,
            gr.update(value="", visible=False),
            gr.update(value=None, visible=False),
            gr.update(value="", visible=False),
            gr.update(selected=0)
        )

# --- UI Definition ---

# Custom CSS for a modern and clean look
css = """
:root {
    /* Dark Theme Palette */
    --bg-primary: #111827;      /* Darkest Gray */
    --bg-secondary: #1f2937;     /* Dark Gray */
    --text-primary: #f9fafb;     /* Off-White */
    --text-secondary: #9ca3af;   /* Gray */
    --accent: #3b82f6;           /* Blue */
    --accent-hover: #2563eb;     /* Darker Blue */
    --border: #374151;           /* Lighter Dark Gray for borders */
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    --gradient: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
}

.gradio-container {
    background: var(--bg-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.header-container {
    background: var(--gradient);
    padding: 1.5rem 0;
    margin-bottom: 2rem;
    border-radius: 0 0 24px 24px;
    box-shadow: var(--shadow);
}

.header-title {
    color: white;
    font-size: 2.25rem;
    font-weight: 700;
    text-align: center;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.page-container {
    max-width: 900px;
    margin: 2rem auto;
    padding: 2rem;
    background: var(--bg-secondary);
    border-radius: 16px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
}

.page-title {
    color: var(--text-primary);
    font-size: 1.75rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1.5rem;
}

.welcome-text {
    color: var(--text-secondary);
    font-size: 1.125rem;
    text-align: center;
    margin-bottom: 2.5rem;
}

.apps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.app-button {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    text-align: left;
}

.app-button:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow) !important;
    border-color: var(--accent) !important;
}

.back-button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    margin-bottom: 1.5rem !important;
    float: left;
}

.back-button:hover {
    background: var(--accent-hover) !important;
}

.gradio-dataframe {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
    margin-bottom: 1rem;
    color: var(--text-primary) !important;
}

.gradio-dataframe th, .gradio-dataframe td {
    border: 1px solid var(--border);
    padding: 0.75rem;
    text-align: left;
    white-space: normal; /* Allow text to wrap */
}

.gradio-dataframe th {
    background-color: var(--bg-primary);
    font-weight: 600;
}

.gradio-textbox, .gradio-button {
    border-radius: 8px !important;
}
"""

def create_app_button(name):
    """Helper to create a styled button for the apps grid."""
    return gr.Button(name, elem_classes=["app-button"])

with gr.Blocks(css=css, title="AI Projects Portfolio") as demo:
    # Header (visible on all pages)
    gr.HTML("""
    <div class="header-container">
        <h1 class="header-title">🚀 AI Projects Portfolio</h1>
    </div>
    """)

    # --- Login Page ---
    with gr.Column(visible=True) as login_page:
        with gr.Row():
            with gr.Column(elem_classes=["page-container"]):
                gr.HTML('<h2 class="page-title">Welcome</h2>')
                gr.HTML('<p class="welcome-text">Please enter your email to view the portfolio.</p>')
                email_input = gr.Textbox(
                    label="Email Address",
                    placeholder="name@example.com",
                    type="email"
                )
                login_button = gr.Button("Continue", variant="primary")

    # --- Home Page (App Dashboard) ---
    with gr.Column(visible=False) as home_page:
        with gr.Row():
            with gr.Column(elem_classes=["page-container"]):
                welcome_msg = gr.HTML('<h2 class="page-title">Welcome!</h2>')
                gr.HTML('<p class="welcome-text">Select an application below to see a demonstration of my skills.</p>')

                with gr.Group(elem_classes=["apps-grid"]):
                    # Application buttons
                    app_buttons = {
                        "PDF Extraction": create_app_button("📄 PDF Extraction"),
                        "Chat with Files": create_app_button("💬 Chat with Files"),
                        "Voice to Text": create_app_button("🎤 Voice to Text"),
                        "Text to Voice": create_app_button("🗣️ Text to Voice"),
                        "PDF OCR Extraction": create_app_button("🔍 PDF OCR Extraction"),
                        "AI Voice Receptionist": create_app_button("🤖 AI Voice Receptionist"),
                        "Agent Examples": create_app_button("🧠 Agent Examples"),
                    }

    # --- Generic App Page Template ---
    with gr.Column(visible=False) as app_page:
        with gr.Row():
            with gr.Column(elem_classes=["page-container"]):
                back_button = gr.Button("← Back to Home", elem_classes=["back-button"])
                app_title = gr.HTML('<h2 class="page-title">App Name</h2>')
                app_placeholder = gr.HTML("<p>App content goes here.</p>")

    # --- PDF Extraction Page ---
    with gr.Column(visible=False) as pdf_extraction_page:
        with gr.Row():
            with gr.Column(elem_classes=["page-container"]):
                pdf_back_button = gr.Button("← Back to Home", elem_classes=["back-button"])
                gr.HTML('<h2 class="page-title">📄 PDF Extraction</h2>')
                gr.HTML("<p class='welcome-text'>Upload a PDF file. The system will save it and extract any tables found within.</p>")

                pdf_upload_input = gr.File(label="Upload PDF", file_types=[".pdf"])
                
                with gr.Tabs() as results_tabs:
                    with gr.TabItem("Upload Summary", id=0):
                        upload_status_output = gr.Markdown("Upload a file to see its summary here.")
                    with gr.TabItem("Extracted Tables", id=1):
                        tables_output = gr.HTML()
                    with gr.TabItem("Extracted Images", id=2):
                        images_output = gr.Gallery(label="Extracted Images", show_label=False, elem_id="gallery", columns=4, object_fit="contain")
                    with gr.TabItem("Emails & Phone Numbers", id=3):
                        contacts_output = gr.Markdown("No contact information extracted yet.")

    # --- Event Wiring ---

    # Login action
    login_button.click(
        fn=handle_email_submit,
        inputs=[email_input],
        outputs=[login_page, home_page, welcome_msg]
    )
    email_input.submit(
        fn=handle_email_submit,
        inputs=[email_input],
        outputs=[login_page, home_page, welcome_msg]
    )

    # App navigation actions
    for name, button in app_buttons.items():
        if name == "PDF Extraction":
            # Special navigation for PDF Extraction page
            button.click(
                fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
                inputs=[],
                outputs=[home_page, pdf_extraction_page]
            )
        else:
            # Generic navigation for other apps
            button.click(
                fn=lambda app_name=name: show_app_page(app_name),
                inputs=[],
                outputs=[home_page, app_page, app_title, app_placeholder]
            )

    # Back button action from generic page
    back_button.click(
        fn=go_home,
        inputs=[],
        outputs=[app_page, home_page]
    )

    # Back button action from PDF page
    pdf_back_button.click(
        fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
        inputs=[],
        outputs=[pdf_extraction_page, home_page]
    )

    # PDF Upload action
    pdf_upload_input.upload(
        fn=handle_pdf_upload,
        inputs=[pdf_upload_input],
        outputs=[upload_status_output, tables_output, images_output, contacts_output, results_tabs]
    )

# --- App Launch ---
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False, debug=True)