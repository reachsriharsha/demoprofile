import gradio as gr

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

# --- UI Definition ---

# Custom CSS for a modern and clean look
css = """
:root {
    --bg-primary: #f9fafb;
    --bg-secondary: #ffffff;
    --text-primary: #111827;
    --text-secondary: #6b7280;
    --accent: #3b82f6;
    --accent-hover: #2563eb;
    --border: #e5e7eb;
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
        button.click(
            fn=lambda app_name=name: show_app_page(app_name),
            inputs=[],
            outputs=[home_page, app_page, app_title, app_placeholder]
        )

    # Back button action
    back_button.click(
        fn=go_home,
        inputs=[],
        outputs=[app_page, home_page]
    )

# --- App Launch ---
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", share=False, debug=True)