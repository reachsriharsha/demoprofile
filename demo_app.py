import gradio as gr

# Global variables to store state
user_email = ""
current_page = "login"

def handle_email_submit(email):
    """Handle email submission and show home page"""
    global user_email, current_page
    if email and "@" in email:
        user_email = email
        current_page = "home"
        return (
            gr.update(visible=False),  # Hide login page
            gr.update(visible=True),   # Show home page
            gr.update(visible=False),  # Hide app pages
            f"Welcome, {email}!"
        )
    else:
        return (
            gr.update(visible=True),   # Keep login page visible
            gr.update(visible=False),  # Keep home page hidden
            gr.update(visible=False),  # Keep app pages hidden
            "Please enter a valid email address"
        )

def show_app(app_name):
    """Show specific app page"""
    global current_page
    current_page = f"app_{app_name.lower()}"
    return (
        gr.update(visible=False),  # Hide login page
        gr.update(visible=False),  # Hide home page
        gr.update(visible=True),   # Show app page
        f"Welcome to {app_name}",
        f"This is the {app_name} application page. Here you can add specific functionality for {app_name}."
    )

def go_home():
    """Return to home page"""
    global current_page
    current_page = "home"
    return (
        gr.update(visible=False),  # Hide login page
        gr.update(visible=False),  # Hide app pages
        gr.update(visible=True),   # Show home page
    )

def toggle_theme():
    """Toggle between light and dark theme"""
    # Note: In a real implementation, you'd need to handle theme switching
    # This is a placeholder for the functionality
    return "Theme toggled!"

# Custom CSS for modern design
css = """
/* Light theme (default) */
:root {
    --bg-primary: #f8fafc;
    --bg-secondary: #ffffff;
    --bg-tertiary: #f1f5f9;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --accent: #3b82f6;
    --accent-hover: #2563eb;
    --border: #e2e8f0;
    --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Dark theme */
[data-theme="dark"] {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-tertiary: #334155;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --accent: #60a5fa;
    --accent-hover: #3b82f6;
    --border: #475569;
    --gradient: linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%);
}

.gradio-container {
    background: var(--bg-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Header styling */
.header-container {
    background: var(--gradient);
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-radius: 0 0 20px 20px;
    box-shadow: var(--shadow);
}

.header-title {
    color: white;
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

/* Login page styling */
.login-container {
    max-width: 400px;
    margin: 2rem auto;
    padding: 2rem;
    background: var(--bg-secondary);
    border-radius: 16px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
}

.login-title {
    color: var(--text-primary);
    font-size: 1.5rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* Home page styling */
.home-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
}

.welcome-text {
    color: var(--text-primary);
    font-size: 1.25rem;
    font-weight: 500;
    text-align: center;
    margin-bottom: 2rem;
}

.apps-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin: 2rem 0;
}

.app-button {
    background: var(--bg-secondary) !important;
    border: 2px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: all 0.3s ease !important;
    box-shadow: var(--shadow) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

.app-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 15px -3px rgba(0, 0, 0, 0.15) !important;
    border-color: var(--accent) !important;
    background: var(--accent) !important;
    color: white !important;
}

/* App page styling */
.app-page-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 2rem;
    background: var(--bg-secondary);
    border-radius: 16px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
}

.app-title {
    color: var(--text-primary);
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 1rem;
}

.app-description {
    color: var(--text-secondary);
    font-size: 1rem;
    text-align: center;
    line-height: 1.6;
    margin-bottom: 2rem;
}

/* Theme toggle button */
.theme-toggle {
    position: absolute;
    top: 1rem;
    right: 1rem;
    background: rgba(255, 255, 255, 0.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 500 !important;
    backdrop-filter: blur(10px);
}

.theme-toggle:hover {
    background: rgba(255, 255, 255, 0.3) !important;
}

/* Back button */
.back-button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    margin-bottom: 1rem !important;
}

.back-button:hover {
    background: var(--accent-hover) !important;
}

/* Input styling */
.gradio-textbox {
    border-radius: 8px !important;
    border: 2px solid var(--border) !important;
    padding: 0.75rem !important;
    font-size: 1rem !important;
    transition: border-color 0.3s ease !important;
}

.gradio-textbox:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
}

/* Button styling */
.gradio-button {
    background: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
}

.gradio-button:hover {
    background: var(--accent-hover) !important;
    transform: translateY(-1px);
}
"""

# Create the Gradio interface
with gr.Blocks(css=css, title="Application Portfolio", theme=gr.themes.Soft()) as demo:
    # JavaScript for theme toggle (loaded first)
    gr.HTML("""
    <script>
    function toggleTheme() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        body.setAttribute('data-theme', newTheme);
        
        // Store theme preference
        localStorage.setItem('theme', newTheme);
    }
    
    // Load saved theme on page load
    document.addEventListener('DOMContentLoaded', function() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
    });
    </script>
    """)
    
    # Header
    with gr.Row():
        with gr.Column():
            gr.HTML("""
            <div class="header-container">
                <h1 class="header-title">🚀 Application Portfolio</h1>
                <!-- <button class="theme-toggle" onclick="toggleTheme()">🌓 Toggle Theme</button> -->
            </div>
            """)
    
    # Login Page
    with gr.Column(visible=True) as login_page:
        with gr.Row():
            with gr.Column():
                gr.HTML('<div class="login-container">')
                gr.HTML('<h2 class="login-title">Welcome! Please enter your email to continue</h2>')
                email_input = gr.Textbox(
                    label="Email Address",
                    placeholder="Enter your email...",
                    elem_classes=["gradio-textbox"]
                )
                email_submit_btn = gr.Button("Continue", elem_classes=["gradio-button"])
                login_message = gr.Textbox(visible=False)
                gr.HTML('</div>')
    
    # Home Page
    with gr.Column(visible=False) as home_page:
        with gr.Row():
            with gr.Column():
                gr.HTML('<div class="home-container">')
                welcome_msg = gr.HTML('<p class="welcome-text">Welcome to your app dashboard!</p>')
                
                gr.HTML('<div class="apps-grid">')
                with gr.Row():
                    pdf_extraction_btn = gr.Button("📱 PDF Data Extraction", elem_classes=["app-button"])
                    app2_btn = gr.Button("🔧 Chat with files", elem_classes=["app-button"])
                    app3_btn = gr.Button("📊 Chat with Database", elem_classes=["app-button"])
                with gr.Row():
                    app4_btn = gr.Button("🎨 Speech to Text", elem_classes=["app-button"])
                    app5_btn = gr.Button("🌟 Text to Speech", elem_classes=["app-button"])
                    app6_btn = gr.Button("🌟 Image to Text", elem_classes=["app-button"])
                gr.HTML('</div>')
                gr.HTML('</div>')
    
    # App Pages
    with gr.Column(visible=False) as app_pages:
        with gr.Row():
            with gr.Column():
                gr.HTML('<div class="app-page-container">')
                back_btn = gr.Button("← Back to Home", elem_classes=["back-button"])
                app_title = gr.HTML('<h2 class="app-title">App Name</h2>')
                app_description = gr.HTML('<p class="app-description">App description goes here.</p>')
                gr.HTML('</div>')
    
    # Event handlers
    email_submit_btn.click(
        handle_email_submit,
        inputs=[email_input],
        outputs=[login_page, home_page, app_pages, welcome_msg]
    )

    # Add submit event for Enter key press on email input
    email_input.submit(
        handle_email_submit,
        inputs=[email_input],
        outputs=[login_page, home_page, app_pages, welcome_msg]
    )
    
    # App button events
    pdf_extraction_btn.click(
        lambda: show_app("PDF Data Extraction"),
        outputs=[login_page, home_page, app_pages, app_title, app_description]
    )
    
    app2_btn.click(
        lambda: show_app("Chat With Files"),
        outputs=[login_page, home_page, app_pages, app_title, app_description]
    )
    
    app3_btn.click(
        lambda: show_app("Chat with Database"),
        outputs=[login_page, home_page, app_pages, app_title, app_description]
    )
    
    app4_btn.click(
        lambda: show_app("Speech to Text"),
        outputs=[login_page, home_page, app_pages, app_title, app_description]
    )
    
    app5_btn.click(
        lambda: show_app("Text to Speech"),
        outputs=[login_page, home_page, app_pages, app_title, app_description]
    )

    app6_btn.click(
        lambda: show_app("Image to Text"),
        outputs=[login_page, home_page, app_pages, app_title, app_description]
    )

    back_btn.click(
        go_home,
        outputs=[login_page, app_pages, home_page]
    )
    
    # JavaScript for theme toggle
    gr.HTML("""
    <script>
    function toggleTheme() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        body.setAttribute('data-theme', newTheme);
        
        // Store theme preference
        localStorage.setItem('theme', newTheme);
    }
    
    // Load saved theme on page load
    document.addEventListener('DOMContentLoaded', function() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.body.setAttribute('data-theme', savedTheme);
    });
    </script>
    """)

# Launch the app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0",share=False, debug=True)