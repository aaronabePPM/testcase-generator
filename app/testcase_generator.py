"""
Test Case Generator - User-Friendly Tool for Manual QA
Generates automated test cases from Azure DevOps work items
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import json
import csv
import os
import sys
import threading
import base64
import io
from pathlib import Path
try:
    from PIL import ImageGrab, Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class TestCaseGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Case Generator for Azure DevOps")
        
        # Set minimum size and initial size
        self.root.minsize(950, 750)
        
        # Center the window and set a good initial size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Use 70% of screen size, but at least 1000x800
        window_width = max(1000, int(screen_width * 0.7))
        window_height = max(800, int(screen_height * 0.75))
        
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)
        
        # Configure modern styling
        self.setup_styles()
        
        # Config file for storing settings
        self.config_file = os.path.join(os.getcwd(), '.testgen_config.json')
        
        # Setup data directories
        self.data_dir = os.path.join(os.getcwd(), 'data')
        self.json_dir = os.path.join(self.data_dir, 'json')
        self.testcases_dir = os.path.join(self.data_dir, 'testcases')
        self.app_dir = os.path.join(os.getcwd(), 'app')
        
        # Ensure data directories exist
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.testcases_dir, exist_ok=True)
        
        # Variables
        self.work_item_id = tk.StringVar()
        self.organization_url = tk.StringVar(value="https://dev.azure.com/hexagonPPMCOL")
        self.workspace_path = tk.StringVar(value=os.getcwd())
        self.api_key = tk.StringVar()
        self.ai_provider = tk.StringVar(value="github")
        self.use_ai = tk.BooleanVar(value=True)
        self.selected_model = "gpt-4o"  # Default model
        self.pasted_screenshot = None
        self.last_analysis_summary = None
        self.current_work_item_data = None  # Store work item JSON for COS mapping
        
        # Load saved settings
        self.load_config()
        
        self.setup_ui()
    
    def setup_styles(self):
        """Configure modern UI styles"""
        style = ttk.Style()
        
        # Use a modern theme
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Configure colors
        bg_color = "#f5f5f5"
        accent_color = "#0078d4"
        success_color = "#107c10"
        
        # Frame styles
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', background=bg_color, font=('Segoe UI', 10, 'bold'), foreground='#333')
        
        # Label styles
        style.configure('TLabel', background=bg_color, font=('Segoe UI', 9), padding=2)
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), foreground=accent_color)
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), foreground='#666')
        
        # Button styles
        style.configure('TButton', font=('Segoe UI', 9), padding=8, relief='flat')
        style.map('TButton',
                  background=[('active', '#e0e0e0'), ('!disabled', '#ffffff')],
                  foreground=[('!disabled', '#333')])
        
        # Accent button
        style.configure('Accent.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       padding=10)
        style.map('Accent.TButton',
                  background=[('active', '#005a9e'), ('!disabled', accent_color)],
                  foreground=[('!disabled', 'white')])
        
        # Entry styles
        style.configure('TEntry', padding=5, font=('Segoe UI', 9))
        
        # Notebook styles
        style.configure('TNotebook', background=bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', 
                       font=('Segoe UI', 9, 'bold'),
                       padding=[15, 8])
        style.map('TNotebook.Tab',
                  background=[('selected', accent_color), ('!selected', '#e0e0e0')],
                  foreground=[('selected', 'white'), ('!selected', '#333')])
        
        self.root.configure(bg=bg_color)
    
    def install_pillow(self):
        """Install Pillow package via pip"""
        try:
            self.log_message("Installing Pillow package...", "INFO")
            
            # Get Python executable path
            python_exe = sys.executable
            
            # Run pip install in a thread
            def run_install():
                try:
                    result = subprocess.run(
                        [python_exe, "-m", "pip", "install", "pillow"],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0:
                        self.log_message("✓ Pillow installed successfully!", "SUCCESS")
                        messagebox.showinfo(
                            "Installation Complete",
                            "Pillow has been installed successfully!\n\n"
                            "Please restart the application to use clipboard functionality."
                        )
                    else:
                        self.log_message(f"Error installing Pillow: {result.stderr}", "ERROR")
                        messagebox.showerror(
                            "Installation Failed",
                            f"Failed to install Pillow:\n{result.stderr}"
                        )
                except subprocess.TimeoutExpired:
                    self.log_message("Installation timed out", "ERROR")
                    messagebox.showerror("Timeout", "Installation took too long and was cancelled.")
                except Exception as e:
                    self.log_message(f"Error during installation: {str(e)}", "ERROR")
                    messagebox.showerror("Error", f"Installation error:\n{str(e)}")
            
            thread = threading.Thread(target=run_install, daemon=True)
            thread.start()
            
        except Exception as e:
            self.log_message(f"Failed to start installation: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Could not start installation:\n{str(e)}")
        
    def setup_ui(self):
        """Create the user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Main tab
        main_tab = ttk.Frame(self.notebook)
        self.notebook.add(main_tab, text="🎯 Generate Test Cases")
        
        # Configure main_tab to allow proper expansion
        main_tab.rowconfigure(6, weight=1)  # Row with log frame (updated from 5 to 6)
        main_tab.columnconfigure(0, weight=1)
        
        # Title with gradient-like effect using frame
        title_frame = ttk.Frame(main_tab, padding="15")
        title_frame.grid(row=0, column=0, sticky=tk.EW)
        
        title_label = ttk.Label(
            title_frame, 
            text="Azure DevOps Test Case Generator",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 5))
        
        subtitle_label = ttk.Label(
            title_frame,
            text="✨ Generate comprehensive manual test cases from work items using AI",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack()
        
        # Quick Start Frame - Simple essentials
        quick_frame = ttk.LabelFrame(main_tab, text="🚀 Quick Start", padding="20")
        quick_frame.grid(row=1, column=0, sticky=tk.EW, padx=15, pady=(10, 10))
        
        # Work Item ID
        ttk.Label(quick_frame, text="Work Item ID:", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky=tk.W, pady=15, padx=(0, 15))
        work_item_entry = ttk.Entry(quick_frame, textvariable=self.work_item_id, width=30, font=("Segoe UI", 11))
        work_item_entry.grid(row=0, column=1, sticky=tk.W, pady=15, padx=5)
        work_item_entry.focus()
        
        # Info label
        info_label = ttk.Label(
            quick_frame,
            text="💡 Enter your Azure DevOps work item ID and click Generate",
            font=("Segoe UI", 9),
            foreground="#666"
        )
        info_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Token warning (shown if no token saved)
        self.token_warning_label = ttk.Label(
            quick_frame,
            text="⚠️ No GitHub token saved! Click 'Show Advanced Settings' below to configure.",
            font=("Segoe UI", 9, "bold"),
            foreground="#d13438",
            background="#ffe6e6",
            padding=10,
            relief="solid",
            borderwidth=1
        )
        # Will be shown/hidden based on token status
        if not self.api_key.get():
            self.token_warning_label.grid(row=2, column=0, columnspan=3, pady=(0, 10), sticky=tk.EW)
        
        # Show/Hide Advanced button
        self.show_advanced = tk.BooleanVar(value=False)
        self.advanced_toggle = ttk.Button(
            quick_frame,
            text="⚙️ Show Advanced Settings",
            command=self.toggle_advanced_settings
        )
        self.advanced_toggle.grid(row=3, column=0, columnspan=3, pady=(10, 5))
        
        quick_frame.columnconfigure(1, weight=1)
        
        # Advanced Settings Frame (hidden by default)
        self.advanced_frame = ttk.LabelFrame(main_tab, text="⚙️ Advanced Settings", padding="15")
        self.advanced_frame.grid(row=2, column=0, sticky=tk.EW, padx=15, pady=(0, 10))
        self.advanced_frame.grid_remove()  # Hide initially
        
        # API Key
        ttk.Label(self.advanced_frame, text="GitHub Token:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=(0, 10))
        api_key_entry = ttk.Entry(self.advanced_frame, textvariable=self.api_key, width=60, show="*")
        api_key_entry.grid(row=0, column=1, sticky=tk.EW, pady=8, padx=5)
        
        help_btn = ttk.Button(self.advanced_frame, text="🔑 Get Token", command=self.show_api_help)
        help_btn.grid(row=0, column=2, padx=5)
        
        save_token_btn = ttk.Button(self.advanced_frame, text="💾 Save Token", command=self.save_config)
        save_token_btn.grid(row=0, column=3, padx=5)
        
        # Token status
        token_status = "✓ Token loaded" if self.api_key.get() else "⚠ No token saved"
        token_color = "#107c10" if self.api_key.get() else "#d13438"
        self.token_status_label = ttk.Label(
            self.advanced_frame,
            text=token_status,
            font=("Segoe UI", 8),
            foreground=token_color
        )
        self.token_status_label.grid(row=1, column=1, sticky=tk.W, pady=(0, 8))
        
        # Organization URL
        ttk.Label(self.advanced_frame, text="Organization URL:").grid(row=2, column=0, sticky=tk.W, pady=8, padx=(0, 10))
        org_entry = ttk.Entry(self.advanced_frame, textvariable=self.organization_url, width=60)
        org_entry.grid(row=2, column=1, sticky=tk.EW, pady=8, padx=5)
        
        # Workspace Path
        ttk.Label(self.advanced_frame, text="Workspace Folder:").grid(row=3, column=0, sticky=tk.W, pady=8, padx=(0, 10))
        workspace_entry = ttk.Entry(self.advanced_frame, textvariable=self.workspace_path, width=60)
        workspace_entry.grid(row=3, column=1, sticky=tk.EW, pady=8, padx=5)
        
        browse_btn = ttk.Button(self.advanced_frame, text="📁 Browse...", command=self.browse_folder)
        browse_btn.grid(row=3, column=2, padx=5)
        
        # AI Provider selection
        ttk.Label(self.advanced_frame, text="AI Provider:").grid(row=4, column=0, sticky=tk.W, pady=8, padx=(0, 10))
        provider_frame = ttk.Frame(self.advanced_frame)
        provider_frame.grid(row=4, column=1, sticky=tk.W, pady=8, padx=5)
        
        ttk.Radiobutton(provider_frame, text="🆓 GitHub Models (FREE)", 
                       variable=self.ai_provider, value="github").pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(provider_frame, text="OpenAI", 
                       variable=self.ai_provider, value="openai").pack(side=tk.LEFT, padx=8)
        ttk.Radiobutton(provider_frame, text="Azure OpenAI", 
                       variable=self.ai_provider, value="azure").pack(side=tk.LEFT, padx=8)
        
        # Check available models button
        check_models_btn = ttk.Button(
            self.advanced_frame,
            text="🔍 Check Available Models",
            command=self.check_available_models
        )
        check_models_btn.grid(row=4, column=2, padx=5)
        
        # Current model label
        ttk.Label(self.advanced_frame, text="Current Model:").grid(row=5, column=0, sticky=tk.W, pady=8, padx=(0, 10))
        self.model_status_label = ttk.Label(
            self.advanced_frame,
            text=f"🤖 {self.selected_model}",
            font=("Segoe UI", 9, "bold"),
            foreground="#0078d4"
        )
        self.model_status_label.grid(row=5, column=1, sticky=tk.W, pady=8, padx=5)
        
        ttk.Label(self.advanced_frame, text="💡 Default: GitHub Models (free) | Change only if using different provider", 
                 font=("Segoe UI", 8), foreground="#666").grid(row=6, column=1, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        self.advanced_frame.columnconfigure(1, weight=1)
        
        # Action Buttons Frame
        button_frame = ttk.Frame(main_tab, padding="10")
        button_frame.grid(row=4, column=0, sticky=tk.EW, padx=15, pady=(0, 5))
        
        # Generate Button
        self.generate_btn = ttk.Button(
            button_frame,
            text="🚀 Generate Test Cases",
            command=self.generate_test_cases,
            style="Accent.TButton"
        )
        self.generate_btn.pack(side=tk.LEFT, padx=8)
        
        # Check Prerequisites Button
        check_btn = ttk.Button(
            button_frame,
            text="✓ Check Prerequisites",
            command=self.check_prerequisites
        )
        check_btn.pack(side=tk.LEFT, padx=8)
        
        # Clear Button
        clear_btn = ttk.Button(
            button_frame,
            text="🗑️ Clear Log",
            command=self.clear_log
        )
        clear_btn.pack(side=tk.LEFT, padx=8)
        
        # Progress Bar
        progress_frame = ttk.Frame(main_tab, padding="5")
        progress_frame.grid(row=5, column=0, sticky=tk.EW, padx=15)
        
        self.progress = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X)
        
        # Log/Output Frame - THIS IS KEY: Must expand to fill remaining space
        log_frame = ttk.LabelFrame(main_tab, text="📝 Activity Log", padding="10")
        log_frame.grid(row=6, column=0, sticky=tk.NSEW, padx=15, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            background="#ffffff",
            relief='flat',
            borderwidth=1
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Status Bar
        self.status_bar = ttk.Label(
            self.root,
            text="✓ Ready",
            relief=tk.FLAT,
            anchor=tk.W,
            padding="8",
            background="#f5f5f5",
            foreground="#333"
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Initialize viewer tab reference
        self.viewer_tab = None
        self.screenshot_tab = None
        self.current_csv_for_screenshot = None
        
    def browse_folder(self):
        """Browse for workspace folder"""
        folder = filedialog.askdirectory(initialdir=self.workspace_path.get())
        if folder:
            self.workspace_path.set(folder)
    
    def load_config(self):
        """Load saved configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                # Load API key if present
                if 'api_key' in config:
                    self.api_key.set(config['api_key'])
                    
                # Load other settings
                if 'organization_url' in config:
                    self.organization_url.set(config['organization_url'])
                if 'workspace_path' in config:
                    self.workspace_path.set(config['workspace_path'])
                if 'ai_provider' in config:
                    self.ai_provider.set(config['ai_provider'])
                if 'selected_model' in config:
                    self.selected_model = config['selected_model']
                    
        except Exception as e:
            # Silently fail - not critical if config doesn't load
            pass
    
    def save_config(self):
        """Save configuration to file"""
        try:
            config = {
                'api_key': self.api_key.get(),
                'organization_url': self.organization_url.get(),
                'workspace_path': self.workspace_path.get(),
                'ai_provider': self.ai_provider.get(),
                'selected_model': self.selected_model
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update token warning visibility
            if hasattr(self, 'token_warning_label'):
                if self.api_key.get():
                    self.token_warning_label.grid_remove()
                else:
                    self.token_warning_label.grid()
            
            # Update status label
            if hasattr(self, 'token_status_label'):
                self.token_status_label.config(
                    text="✓ Settings saved successfully",
                    foreground="#107c10"
                )
            
            messagebox.showinfo("Settings Saved", "Your settings have been saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save settings:\n{str(e)}")
    
    def check_available_models(self):
        """Check which models are available through GitHub Models API"""
        provider = self.ai_provider.get()
        
        if provider != "github":
            messagebox.showinfo("GitHub Models Only", 
                              "Model checking is only available for GitHub Models provider.")
            return
        
        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showwarning("No Token", 
                                 "Please enter your GitHub token first to check available models.")
            return
        
        # Show progress
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Checking Models...")
        progress_window.geometry("400x100")
        progress_window.transient(self.root)
        
        ttk.Label(progress_window, text="Checking available models...", 
                 font=("Segoe UI", 10)).pack(pady=20)
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        progress_bar.start()
        
        def check_models_thread():
            try:
                import openai
                
                # Try a list of known GitHub Models
                test_models = [
                    "gpt-4o",
                    "gpt-4o-mini", 
                    "o1-preview",
                    "o1-mini",
                    "Phi-3.5-MoE-instruct",
                    "Phi-3-medium-128k-instruct",
                    "Meta-Llama-3.1-405B-Instruct",
                    "Meta-Llama-3.1-70B-Instruct",
                    "Meta-Llama-3.1-8B-Instruct",
                    "Mistral-large",
                    "Mistral-large-2407",
                    "Mistral-Nemo",
                    "Mistral-small",
                    "AI21-Jamba-1.5-Large",
                    "AI21-Jamba-1.5-Mini",
                    "Cohere-command-r",
                    "Cohere-command-r-plus"
                ]
                
                client = openai.OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
                
                available = []
                unavailable = []
                
                for model in test_models:
                    try:
                        # Try a minimal completion to test model availability
                        response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": "Hi"}],
                            max_tokens=1,
                            timeout=5
                        )
                        available.append(model)
                    except Exception as e:
                        error_msg = str(e).lower()
                        if "unknown_model" in error_msg or "unknown model" in error_msg:
                            unavailable.append(model)
                        elif "rate_limit" in error_msg or "quota" in error_msg:
                            # If we hit rate limit, model exists but can't test further
                            available.append(f"{model} (rate limited)")
                            break
                        else:
                            # Other errors might mean the model exists but has different issues
                            available.append(f"{model} (?)")
                
                progress_window.destroy()
                
                # Show results with selection capability
                result_window = tk.Toplevel(self.root)
                result_window.title("Select AI Model")
                result_window.geometry("650x550")
                
                ttk.Label(result_window, 
                         text="✅ Select a Model for Test Case Generation",
                         font=("Segoe UI", 12, "bold")).pack(pady=10)
                
                if not available:
                    ttk.Label(result_window, 
                             text="⚠️ No models were confirmed available.\nThis might be due to token permissions or rate limiting.",
                             font=("Segoe UI", 10),
                             foreground="#d13438").pack(pady=20)
                    ttk.Button(result_window, text="Close", 
                              command=result_window.destroy).pack(pady=10)
                    return
                
                # Info label
                ttk.Label(result_window, 
                         text="Select a model below and click 'Use This Model' to update the configuration.",
                         font=("Segoe UI", 9),
                         foreground="#666").pack(pady=5)
                
                # Create scrollable frame for radio buttons
                canvas_frame = ttk.Frame(result_window)
                canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                canvas = tk.Canvas(canvas_frame, highlightthickness=0)
                scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = ttk.Frame(canvas)
                
                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )
                
                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                
                # Variable to store selected model
                selected_model = tk.StringVar(value=available[0] if available else "")
                
                # Create radio buttons for available models
                ttk.Label(scrollable_frame, 
                         text="AVAILABLE MODELS:", 
                         font=("Segoe UI", 10, "bold"),
                         foreground="#107c10").pack(anchor=tk.W, pady=(5, 10))
                
                for model in available:
                    # Clean model name (remove annotations like "(?)" or "(rate limited)")
                    clean_model = model.split(" (")[0] if " (" in model else model
                    display_text = f"✅ {model}"
                    
                    rb = ttk.Radiobutton(
                        scrollable_frame,
                        text=display_text,
                        variable=selected_model,
                        value=clean_model,
                        style="TRadiobutton"
                    )
                    rb.pack(anchor=tk.W, padx=20, pady=3)
                
                # Show unavailable models (not selectable)
                if unavailable:
                    ttk.Separator(scrollable_frame, orient="horizontal").pack(fill=tk.X, pady=15)
                    ttk.Label(scrollable_frame, 
                             text="UNAVAILABLE MODELS:", 
                             font=("Segoe UI", 10, "bold"),
                             foreground="#d13438").pack(anchor=tk.W, pady=(5, 10))
                    
                    for model in unavailable:
                        ttk.Label(
                            scrollable_frame,
                            text=f"❌ {model}",
                            foreground="#999"
                        ).pack(anchor=tk.W, padx=20, pady=2)
                
                # Summary label
                summary = ttk.Label(result_window, 
                                   text=f"📊 Total: {len(available)} available, {len(unavailable)} unavailable",
                                   font=("Segoe UI", 9),
                                   foreground="#666")
                summary.pack(pady=5)
                
                # Buttons frame
                button_frame = ttk.Frame(result_window)
                button_frame.pack(pady=15)
                
                def apply_model_selection():
                    model = selected_model.get()
                    if not model:
                        messagebox.showwarning("No Selection", "Please select a model first.")
                        return
                    
                    # Update the model in the config and code
                    self.selected_model = model
                    self.save_config()
                    
                    # Update the model status label
                    if hasattr(self, 'model_status_label'):
                        self.model_status_label.config(text=f"🤖 {model}")
                    
                    result_window.destroy()
                    messagebox.showinfo(
                        "Model Updated",
                        f"✓ Model updated to: {model}\n\n"
                        "The new model will be used for all test case generation operations."
                    )
                    self.log_message(f"✓ AI Model changed to: {model}", "SUCCESS")
                
                ttk.Button(button_frame, 
                          text="✓ Use This Model", 
                          command=apply_model_selection,
                          style="Accent.TButton").pack(side=tk.LEFT, padx=5)
                
                ttk.Button(button_frame, 
                          text="Cancel", 
                          command=result_window.destroy).pack(side=tk.LEFT, padx=5)
                
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Error", f"Failed to check models:\n{str(e)}")
        
        # Run in thread to not block UI
        thread = threading.Thread(target=check_models_thread, daemon=True)
        thread.start()
    
    def toggle_advanced_settings(self):
        """Show or hide advanced settings"""
        if self.show_advanced.get():
            # Hide advanced settings
            self.advanced_frame.grid_remove()
            self.advanced_toggle.config(text="⚙️ Show Advanced Settings")
            self.show_advanced.set(False)
        else:
            # Show advanced settings
            self.advanced_frame.grid()
            self.advanced_toggle.config(text="⚙️ Hide Advanced Settings")
            self.show_advanced.set(True)
    
    def show_api_help(self):
        """Show help for getting API keys"""
        provider = self.ai_provider.get()
        
        if provider == "github":
            msg = ("GitHub Models (FREE)\n\n"
                   "1. Go to: https://github.com/settings/tokens\n"
                   "2. Click 'Generate new token (classic)'\n"
                   "3. Give it a name like 'Test Case Generator'\n"
                   "4. No special scopes needed for public models\n"
                   "5. Copy the token and paste it here\n\n"
                   "This uses free GitHub-hosted AI models!")
            messagebox.showinfo("GitHub Models Setup", msg)
            import webbrowser
            webbrowser.open("https://github.com/settings/tokens")
        elif provider == "openai":
            msg = ("OpenAI API\n\n"
                   "1. Go to: https://platform.openai.com/api-keys\n"
                   "2. Sign up or log in\n"
                   "3. Click 'Create new secret key'\n"
                   "4. Copy the key and paste it here\n\n"
                   "Note: This is a paid service (pay-as-you-go)")
            messagebox.showinfo("OpenAI Setup", msg)
            import webbrowser
            webbrowser.open("https://platform.openai.com/api-keys")
        else:  # azure
            msg = ("Azure OpenAI\n\n"
                   "1. Contact your Azure administrator\n"
                   "2. Get your Azure OpenAI endpoint and API key\n"
                   "3. Paste the API key here\n\n"
                   "Note: Requires Azure OpenAI resource")
            messagebox.showinfo("Azure OpenAI Setup", msg)
        from tkinter import filedialog
        folder = filedialog.askdirectory(initialdir=self.workspace_path.get())
        if folder:
            self.workspace_path.set(folder)
            self.log_message(f"Workspace folder set to: {folder}")
    
    def log_message(self, message, level="INFO"):
        """Add message to log"""
        timestamp = ""
        self.log_text.insert(tk.END, f"[{level}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the log window"""
        self.log_text.delete(1.0, tk.END)
        
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
        
    def check_prerequisites(self):
        """Check if Azure CLI is installed"""
        self.log_message("Checking prerequisites...")
        self.update_status("Checking prerequisites...")
        
        # On Windows, az is a .cmd file that requires shell=True
        import platform
        use_shell = platform.system() == 'Windows'
        
        try:
            result = subprocess.run(
                ["az", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=use_shell
            )
            
            if result.returncode == 0:
                self.log_message("✓ Azure CLI is installed", "SUCCESS")
                version_line = result.stdout.split('\n')[0]
                self.log_message(f"  {version_line}")
                
                # Check if logged in
                self.log_message("")
                self.log_message("Checking Azure login status...")
                login_result = subprocess.run(
                    ["az", "account", "show"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    shell=use_shell
                )
                
                if login_result.returncode == 0:
                    self.log_message("✓ You are logged in to Azure", "SUCCESS")
                    import json
                    try:
                        account = json.loads(login_result.stdout)
                        self.log_message(f"  Account: {account.get('user', {}).get('name', 'Unknown')}")
                        self.log_message(f"  Subscription: {account.get('name', 'Unknown')}")
                    except:
                        pass
                    messagebox.showinfo("Prerequisites Check", 
                                      "✓ Azure CLI is installed and you are logged in!\n\n"
                                      "Ready to generate test cases.")
                else:
                    self.log_message("⚠ You are NOT logged in to Azure", "WARNING")
                    self.log_message("Please run: az login", "WARNING")
                    messagebox.showwarning("Not Logged In", 
                                         "Azure CLI is installed but you are not logged in.\n\n"
                                         "Please run this command in PowerShell:\n"
                                         "az login\n\n"
                                         "Then try again.")
                
                self.update_status("Prerequisites OK")
            else:
                self.log_message("✗ Azure CLI check failed", "ERROR")
                self.show_install_instructions()
                
        except FileNotFoundError:
            self.log_message("✗ Azure CLI is NOT installed", "ERROR")
            self.show_install_instructions()
        except Exception as e:
            self.log_message(f"Error checking prerequisites: {str(e)}", "ERROR")
            
    def show_install_instructions(self):
        """Show Azure CLI installation instructions"""
        msg = ("Azure CLI is not installed.\n\n"
               "Please install it from:\n"
               "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli\n\n"
               "After installation, restart this application.")
        messagebox.showwarning("Azure CLI Not Found", msg)
        self.update_status("Azure CLI not found")
        
    def generate_test_cases(self):
        """Main function to generate test cases"""
        work_item_id = self.work_item_id.get().strip()
        
        if not work_item_id:
            messagebox.showerror("Error", "Please enter a Work Item ID")
            return
            
        if not work_item_id.isdigit():
            messagebox.showerror("Error", "Work Item ID must be a number")
            return
            
        # Run in separate thread to avoid freezing UI
        thread = threading.Thread(target=self._generate_test_cases_thread, args=(work_item_id,))
        thread.daemon = True
        thread.start()
        
    def _generate_test_cases_thread(self, work_item_id):
        """Thread worker for generating test cases"""
        try:
            self.generate_btn.config(state=tk.DISABLED)
            self.progress.start(10)
            self.update_status("Generating test cases...")
            
            # Step 1: Export work item JSON
            self.log_message(f"Starting test case generation for Work Item {work_item_id}")
            self.log_message("=" * 60)
            
            success = self.export_work_item(work_item_id)
            if not success:
                return
                
            # Step 2: Generate CSV from JSON using AI
            success = self.generate_csv_from_json(work_item_id)
            if not success:
                return
                
            self.log_message("=" * 60)
            self.log_message("✓ Test case generation completed successfully!", "SUCCESS")
            self.update_status("Completed successfully")
            
            messagebox.showinfo(
                "Success",
                f"Test cases generated successfully!\n\n"
                f"Output file: data/testcases/Testcases_PBI_{work_item_id}.csv"
            )
            
        except Exception as e:
            self.log_message(f"Unexpected error: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            self.update_status("Error occurred")
            
        finally:
            self.progress.stop()
            self.generate_btn.config(state=tk.NORMAL)
            
    def export_work_item(self, work_item_id):
        """Export work item from Azure DevOps"""
        self.log_message(f"Step 1: Exporting work item {work_item_id} from Azure DevOps...")
        
        workspace = self.workspace_path.get()
        org_url = self.organization_url.get()
        output_file = os.path.join(self.json_dir, f"PBI-{work_item_id}.json")
        
        # On Windows, az is a .cmd file that requires shell=True
        import platform
        use_shell = platform.system() == 'Windows'
        
        try:
            # Build the command
            cmd = [
                "az", "boards", "work-item", "show",
                "--id", work_item_id,
                "--organization", org_url,
                "--output", "json"
            ]
            
            self.log_message(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=workspace,
                shell=use_shell
            )
            
            if result.returncode != 0:
                self.log_message(f"Error: {result.stderr}", "ERROR")
                messagebox.showerror("Export Failed", f"Failed to export work item:\n{result.stderr}")
                self.update_status("Export failed")
                return False
                
            # Save the JSON output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
                
            self.log_message(f"✓ Work item exported to: {output_file}", "SUCCESS")
            return True
            
        except subprocess.TimeoutExpired:
            self.log_message("Error: Command timed out", "ERROR")
            messagebox.showerror("Timeout", "The Azure CLI command timed out")
            self.update_status("Timeout")
            return False
        except FileNotFoundError:
            self.log_message("✗ Azure CLI (az) not found!", "ERROR")
            self.log_message("Azure CLI must be installed to export work items.", "ERROR")
            msg = ("Azure CLI is not installed or not in PATH.\n\n"
                   "Please install Azure CLI:\n"
                   "https://aka.ms/installazurecliwindows\n\n"
                   "After installation:\n"
                   "1. Restart this application\n"
                   "2. Run: az login\n"
                   "3. Try again")
            messagebox.showerror("Azure CLI Not Found", msg)
            self.update_status("Azure CLI not found")
            return False
        except Exception as e:
            self.log_message(f"Error during export: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
            self.update_status("Export failed")
            return False
            
    def generate_csv_from_json(self, work_item_id):
        """Generate CSV test cases from JSON"""
        self.log_message(f"Step 2: Generating test cases CSV...")
        
        workspace = self.workspace_path.get()
        json_file = os.path.join(self.json_dir, f"PBI-{work_item_id}.json")
        template_file = os.path.join(self.app_dir, "testcase_template.csv")
        output_file = os.path.join(self.testcases_dir, f"Testcases_PBI_{work_item_id}.csv")
        
        # Check if files exist
        if not os.path.exists(json_file):
            self.log_message(f"Error: JSON file not found: {json_file}", "ERROR")
            return False
            
        if not os.path.exists(template_file):
            self.log_message(f"Warning: Template file not found: {template_file}", "WARNING")
            self.log_message("Please ensure testcase_template.csv exists in the app/ folder", "WARNING")
            
        self.log_message("Reading work item JSON...")
        
        # Read the JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            work_item_data = json.load(f)
        
        # Store work item data for COS mapping
        self.current_work_item_data = work_item_data
        
        # Check if AI generation is enabled
        if self.use_ai.get() and self.api_key.get().strip():
            provider = self.ai_provider.get()
            self.log_message(f"Using {provider.upper()} AI to generate test cases...")
            success = self.generate_with_ai(work_item_data, template_file, output_file, work_item_id)
            if success:
                return True
            else:
                self.log_message("AI generation failed, showing manual instructions...", "WARNING")
        
        # Manual generation instructions
        self.log_message("=" * 60)
        self.log_message("Manual Test Case Generation Required", "INFO")
        self.log_message("=" * 60)
        self.log_message("")
        self.log_message("The work item has been exported successfully.")
        self.log_message(f"JSON file: {json_file}")
        self.log_message("")
        self.log_message("To complete the test case generation, you can:")
        self.log_message("1. Use GitHub Copilot in VS Code")
        self.log_message("2. Configure AI API key in the application")
        self.log_message("3. Manually create test cases based on the work item")
        self.log_message("")
        self.log_message("Work Item Summary:", "INFO")
        self.log_message(f"  Title: {work_item_data.get('fields', {}).get('System.Title', 'N/A')}")
        self.log_message(f"  Type: {work_item_data.get('fields', {}).get('System.WorkItemType', 'N/A')}")
        self.log_message(f"  State: {work_item_data.get('fields', {}).get('System.State', 'N/A')}")
        
        self.log_message("")
        self.log_message("💡 TIP: Open the JSON file in VS Code and ask GitHub Copilot:", "INFO")
        self.log_message("   'Generate test cases from this work item using testcase_template.csv'")
        
        return True
    
    def generate_with_ai(self, work_item_data, template_file, output_file, work_item_id):
        """Generate test cases using AI"""
        try:
            # Check if openai package is available
            try:
                import openai
            except ImportError:
                self.log_message("Installing openai package...", "INFO")
                subprocess.run([sys.executable, "-m", "pip", "install", "openai"], 
                             check=True, capture_output=True)
                import openai
            
            # Set API key and client based on provider
            api_key = self.api_key.get().strip()
            provider = self.ai_provider.get()
            
            if provider == "github":
                # Use GitHub Models
                client = openai.OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
                model = self.selected_model
            elif provider == "openai":
                client = openai.OpenAI(api_key=api_key)
                model = self.selected_model
            else:  # azure
                # For Azure OpenAI, user would need to provide endpoint
                client = openai.OpenAI(api_key=api_key)
                model = self.selected_model
            
            # Read template to understand the format
            template_content = ""
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_content = f.read()
            
            # Extract key information from work item
            fields = work_item_data.get('fields', {})
            title = fields.get('System.Title', '')
            description = fields.get('System.Description', '')
            acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
            developer_notes = fields.get('Custom.DeveloperNotes', '') or fields.get('Microsoft.VSTS.TCM.ReproSteps', '')
            work_item_type = fields.get('System.WorkItemType', 'PBI')
            
            # Build the prompt
            prompt = self.build_test_case_prompt(
                work_item_id, title, description, acceptance_criteria, 
                developer_notes, template_content, work_item_type
            )
            
            self.log_message(f"Calling {provider.upper()} API...")
            self.log_message("This may take 30-60 seconds...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert QA test case writer. Generate comprehensive manual test cases in CSV format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            csv_content = response.choices[0].message.content
            
            self.log_message(f"AI Response received (first 200 chars):", "INFO")
            self.log_message(csv_content[:200] if csv_content else "EMPTY", "INFO")
            
            # Clean up the response - remove markdown code blocks if present
            if "```" in csv_content:
                # Extract content between ``` markers
                parts = csv_content.split("```")
                for part in parts:
                    if "Work Item Type" in part or "Title" in part:
                        csv_content = part.strip()
                        # Remove language identifier if present
                        if csv_content.startswith("csv\n"):
                            csv_content = csv_content[4:]
                        break
            
            # Remove any leading text before the CSV header
            header_line = "Work Item Type,Title,Test Step,Step Action,Step Expected,COS Reference"
            if header_line in csv_content:
                header_index = csv_content.find(header_line)
                if header_index > 0:
                    self.log_message(f"Removing {header_index} characters before CSV header", "INFO")
                    csv_content = csv_content[header_index:]
            
            # Remove any trailing notes/text after the last CSV row
            # Split by lines and filter
            lines = csv_content.split('\n')
            csv_lines = []
            found_header = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Check if this is the header
                if line_stripped.startswith('Work Item Type'):
                    csv_lines.append(line)
                    found_header = True
                    continue
                
                # Skip lines before header
                if not found_header:
                    continue
                
                # Check if this looks like explanatory text (not CSV data)
                if line_stripped and not line_stripped.startswith(',') and not line_stripped.startswith('Test Case'):
                    # Lines with "note", "here is", etc. are explanatory
                    lower_line = line_stripped.lower()
                    if any(keyword in lower_line for keyword in ['note that', 'note:', 'i\'ve created', 'here is', 'based on', 'additionally', 'these test cases']):
                        self.log_message(f"Stopping at explanatory text: {line_stripped[:50]}...", "INFO")
                        break
                
                # Keep all other lines (CSV data, empty lines, etc.)
                if line_stripped or csv_lines:  # Keep line if it has content OR if we've already started collecting
                    csv_lines.append(line)
            
            csv_content = '\n'.join(csv_lines).strip()
            
            # Validate CSV content
            if not csv_content or len(csv_content.strip()) < 50:
                self.log_message(f"Error: AI returned empty or invalid CSV content", "ERROR")
                self.log_message(f"Response length: {len(csv_content)}", "ERROR")
                return False
            
            self.log_message(f"Received CSV content ({len(csv_content)} chars)", "INFO")
            
            # Parse and rewrite CSV with proper quoting
            import io
            lines = csv_content.split('\n')
            reader = csv.reader(io.StringIO(csv_content))
            rows = list(reader)
            
            if len(rows) < 2:  # Need at least header + 1 data row
                self.log_message(f"Error: CSV has insufficient rows: {len(rows)}", "ERROR")
                return False
            
            self.log_message(f"Parsed {len(rows)} CSV rows", "INFO")
            
            # Save the CSV with proper quoting
            self.log_message(f"Writing CSV to: {output_file}", "INFO")
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerows(rows)
            
            # Verify file was created
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                self.log_message(f"✓ CSV file created: {file_size} bytes", "SUCCESS")
            else:
                self.log_message(f"Error: CSV file was not created!", "ERROR")
                return False
            
            self.log_message(f"✓ Test cases generated successfully!", "SUCCESS")
            self.log_message(f"Output file: {output_file}", "SUCCESS")
            
            # Schedule viewer creation on main thread (Tkinter requirement)
            self.log_message(f"Scheduling viewer creation on main thread", "INFO")
            self.root.after(0, lambda: self.show_test_case_viewer(output_file))
            
            # Schedule screenshot analysis tab on main thread
            self.log_message(f"Scheduling screenshot tab creation on main thread", "INFO")
            self.root.after(0, lambda: self.show_screenshot_analysis_tab(output_file))
            
            return True
            
        except Exception as e:
            self.log_message(f"Error during AI generation: {str(e)}", "ERROR")
            import traceback
            self.log_message(f"Traceback:\n{traceback.format_exc()}", "ERROR")
            return False
    
    def build_test_case_prompt(self, work_item_id, title, description, acceptance_criteria, 
                               developer_notes, template_content, work_item_type):
        """Build the prompt for AI test case generation"""
        
        prompt = f"""Generate manual test cases for this Azure DevOps work item in CSV format.

WORK ITEM DETAILS:
ID: {work_item_id}
Type: {work_item_type}
Title: {title}

Description:
{description}

Acceptance Criteria:
{acceptance_criteria}

Developer Notes (CRITICAL - must be covered by tests):
{developer_notes}

CSV TEMPLATE FORMAT - FOLLOW THIS EXACTLY:
{template_content}

CRITICAL FORMAT RULES:
1. Header row MUST be: Work Item Type,Title,Test Step,Step Action,Step Expected,COS Reference
2. Each Test Case is ONE row with: "Test Case" in column 1, full title in column 2, empty columns 3-5, COS number/text in column 6
3. Each Step is a SEPARATE row with: empty column 1, empty column 2, step number in column 3, action in column 4, expected result in column 5, empty column 6
4. COS Reference: For each test case, include which Condition of Satisfaction (COS) it addresses. Use "COS 1", "COS 2", etc. based on the numbered/bulleted list in Acceptance Criteria
5. Example structure (EXACTLY 6 columns per row, NO trailing commas):
   Test Case,FUNC-01: Test Name,,,, COS 1
   , ,1,Do action 1,Expected result 1,
   , ,2,Do action 2,Expected result 2,
   Test Case,FUNC-02: Another Test,,,,COS 2
   , ,1,Do action,Expected result,

CONTENT REQUIREMENTS:
1. Test Case Titles: Use prefixes FUNC-XX (Functional), VAL-XX (Validation), UI-XX (UI), NEG-XX (Negative), REG-XX (Regression)
2. Do NOT include the PBI/Bug number in titles
3. NO COMMAS inside any text field (use semicolons or dashes instead)
4. Keep steps clear and actionable
5. Each step must have a specific expected result
6. EVERY test case MUST have a COS Reference indicating which Acceptance Criteria item it addresses
7. Create at least one test case for EACH Condition of Satisfaction in the Acceptance Criteria
8. Cover all aspects: Functional, Validation, UI, Negative, and Regression scenarios
9. Pay special attention to Developer Notes - test what was actually implemented

OUTPUT FORMAT:
IMPORTANT: Return ONLY the CSV data - NO explanatory text, NO markdown formatting, NO notes.
Start directly with the header row: Work Item Type,Title,Test Step,Step Action,Step Expected,COS Reference
Do NOT include phrases like "Here is the CSV" or notes at the end.
Just return pure CSV data that can be parsed directly.
"""
        return prompt
    
    def show_test_case_viewer(self, csv_file):
        """Display generated test cases in a viewer tab"""
        self.log_message(f"show_test_case_viewer called with: {csv_file}", "INFO")
        
        if not os.path.exists(csv_file):
            self.log_message(f"Error: CSV file not found: {csv_file}", "ERROR")
            return
        
        self.log_message(f"CSV file exists, creating viewer...", "INFO")
        
        try:
            # Remove existing viewer tab if present
            if self.viewer_tab:
                try:
                    self.notebook.forget(self.viewer_tab)
                    self.log_message(f"Removed existing viewer tab", "INFO")
                except:
                    pass
            
            # Create new viewer tab
            self.log_message(f"Creating new viewer tab frame...", "INFO")
            self.viewer_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.viewer_tab, text="✏️ Review & Edit Test Cases")
            self.log_message(f"Viewer tab added to notebook", "INFO")
            
            # Store CSV file path for saving
            self.current_csv_file = csv_file
            self.csv_modified = False
            
            # Title
            title_frame = ttk.Frame(self.viewer_tab, padding="10")
            title_frame.pack(fill=tk.X)
            
            ttk.Label(
                title_frame,
                text=f"Test Cases: {os.path.basename(csv_file)}",
                font=("Arial", 14, "bold")
            ).pack(side=tk.LEFT)
            
            # Modified indicator
            self.modified_label = ttk.Label(
                title_frame, 
                text="", 
                font=("Arial", 10, "italic"),
                foreground="orange"
            )
            self.modified_label.pack(side=tk.LEFT, padx=10)
            
            # Stats label
            self.stats_label = ttk.Label(title_frame, text="", font=("Arial", 10))
            self.stats_label.pack(side=tk.RIGHT)
            
            # Create sub-notebook for different views
            viewer_notebook = ttk.Notebook(self.viewer_tab)
            viewer_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Tab 1: Table View (Editable)
            self.log_message(f"Creating Table View tab...", "INFO")
            table_frame = ttk.Frame(viewer_notebook)
            viewer_notebook.add(table_frame, text="📊 Table View")
            self.create_table_view(table_frame, csv_file)
            
            # Tab 2: Test Case List
            self.log_message(f"Creating Summary tab...", "INFO")
            list_frame = ttk.Frame(viewer_notebook)
            viewer_notebook.add(list_frame, text="📝 Summary")
            self.create_summary_view(list_frame, csv_file)
            
            # Tab 3: COS Coverage
            self.log_message(f"Creating COS Coverage tab...", "INFO")
            cos_frame = ttk.Frame(viewer_notebook)
            viewer_notebook.add(cos_frame, text="✅ COS Coverage")
            self.create_cos_coverage_view(cos_frame, csv_file)
            
            # Tab 4: Raw CSV
            self.log_message(f"Creating Raw CSV tab...", "INFO")
            raw_frame = ttk.Frame(viewer_notebook)
            viewer_notebook.add(raw_frame, text="📄 Raw CSV")
            self.create_raw_view(raw_frame, csv_file)
            
            # Switch to the viewer tab
            self.log_message(f"Switching to viewer tab...", "INFO")
            self.notebook.select(self.viewer_tab)
            
            self.log_message("✓ Test case viewer opened successfully", "SUCCESS")
            
        except Exception as e:
            self.log_message(f"Error creating viewer: {str(e)}", "ERROR")
            import traceback
            self.log_message(traceback.format_exc(), "ERROR")
            messagebox.showerror("Viewer Error", f"Failed to create viewer:\n{str(e)}")
    
    def create_table_view(self, parent, csv_file):
        """Create editable table view of test cases"""
        # Button frame at top of table view
        button_frame = ttk.Frame(parent, padding="10")
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="💾 Save Changes", 
                  command=lambda: self.save_csv_changes()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="+ Add Row", 
                  command=lambda: self.add_test_row()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete Row", 
                  command=lambda: self.delete_selected_row()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Open in Editor", 
                  command=lambda: self.open_csv_file(csv_file)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Location", 
                  command=lambda: self.open_file_location(csv_file)).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        info_frame = ttk.Frame(parent, padding="5")
        info_frame.pack(fill=tk.X)
        ttk.Label(
            info_frame,
            text="💡 Double-click any cell to edit | Right-click for options",
            font=("Arial", 9),
            foreground="gray"
        ).pack()
        
        # Create frame with scrollbars
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(container, orient="vertical")
        hsb = ttk.Scrollbar(container, orient="horizontal")
        
        # Create Treeview
        self.tree = ttk.Treeview(container, 
                           yscrollcommand=vsb.set,
                           xscrollcommand=hsb.set,
                           selectmode='browse')
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Read CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            self.csv_headers = next(reader)
            self.csv_rows = list(reader)
        
        # Configure columns
        self.tree['columns'] = self.csv_headers
        self.tree['show'] = 'headings'
        
        # Set column headings and widths
        for col in self.csv_headers:
            self.tree.heading(col, text=col)
            if col == "Title":
                self.tree.column(col, width=300, minwidth=200)
            elif col in ["Step Action", "Step Expected"]:
                self.tree.column(col, width=400, minwidth=200)
            elif col == "Work Item Type":
                self.tree.column(col, width=100, minwidth=80)
            else:
                self.tree.column(col, width=150, minwidth=100)
        
        # Add rows with alternating colors
        for i, row in enumerate(self.csv_rows):
            # Skip empty rows
            if not row or len(row) == 0:
                continue
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            # Highlight test case rows (vs step rows)
            if len(row) > 0 and row[0]:  # If Work Item Type is filled, it's a test case row
                tag = 'testcase'
            self.tree.insert('', 'end', values=row, tags=(tag,))
        
        # Configure tags for colors
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f0f0f0')
        self.tree.tag_configure('testcase', background='#e3f2fd', font=('Arial', 9, 'bold'))
        
        # Bind double-click to edit
        self.tree.bind('<Double-Button-1>', self.on_double_click)
        
        # Bind right-click for context menu
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def on_double_click(self, event):
        """Handle double-click to edit cell"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        
        # Get column and item
        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        
        if not item or not column:
            return
        
        # Get column index (column is like '#1', '#2', etc.)
        col_index = int(column.replace('#', '')) - 1
        col_name = self.csv_headers[col_index]
        
        # Get current value
        values = self.tree.item(item, 'values')
        current_value = values[col_index]
        
        # Open edit dialog
        self.edit_cell(item, col_index, col_name, current_value)
    
    def edit_cell(self, item, col_index, col_name, current_value):
        """Open dialog to edit cell value"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit: {col_name}")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Label
        ttk.Label(dialog, text=f"Editing: {col_name}", font=("Arial", 10, "bold")).pack(pady=10)
        
        # Text widget for editing (multi-line support)
        text_frame = ttk.Frame(dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=10, font=("Arial", 10))
        text.pack(fill=tk.BOTH, expand=True)
        text.insert('1.0', current_value)
        text.focus()
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_edit():
            new_value = text.get('1.0', 'end-1c')
            
            # Update treeview
            values = list(self.tree.item(item, 'values'))
            values[col_index] = new_value
            self.tree.item(item, values=values)
            
            # Update internal data
            row_index = self.tree.index(item)
            self.csv_rows[row_index] = values
            
            # Mark as modified
            self.csv_modified = True
            self.modified_label.config(text="● Modified (unsaved)")
            
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_edit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter with Ctrl to save
        dialog.bind('<Control-Return>', lambda e: save_edit())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Select the row
        self.tree.selection_set(item)
        
        # Create context menu
        menu = tk.Menu(self.tree, tearoff=0)
        menu.add_command(label="Edit Row", command=lambda: self.edit_full_row(item))
        menu.add_command(label="Duplicate Row", command=lambda: self.duplicate_row(item))
        menu.add_separator()
        menu.add_command(label="Delete Row", command=lambda: self.delete_row(item))
        
        # Show menu
        menu.post(event.x_root, event.y_root)
    
    def edit_full_row(self, item):
        """Edit all fields in a row"""
        values = self.tree.item(item, 'values')
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Test Case Row")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create scrollable frame
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create entry widgets for each field
        entries = []
        for i, (header, value) in enumerate(zip(self.csv_headers, values)):
            frame = ttk.Frame(scrollable_frame)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(frame, text=header, width=20, anchor='w').pack(side=tk.LEFT)
            
            if header in ["Step Action", "Step Expected", "Description"]:
                text = scrolledtext.ScrolledText(frame, height=3, width=50)
                text.insert('1.0', value)
                text.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries.append(text)
            else:
                entry = ttk.Entry(frame, width=50)
                entry.insert(0, value)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                entries.append(entry)
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        
        def save_row():
            new_values = []
            for entry in entries:
                if isinstance(entry, scrolledtext.ScrolledText):
                    new_values.append(entry.get('1.0', 'end-1c'))
                else:
                    new_values.append(entry.get())
            
            # Update treeview
            self.tree.item(item, values=new_values)
            
            # Update internal data
            row_index = self.tree.index(item)
            self.csv_rows[row_index] = new_values
            
            # Mark as modified
            self.csv_modified = True
            self.modified_label.config(text="● Modified (unsaved)")
            
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save Changes", command=save_row).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Pack everything
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
    
    def add_test_row(self):
        """Add a new empty row"""
        if not hasattr(self, 'tree'):
            messagebox.showwarning("Not Ready", "Please wait for the table to load.")
            return
        
        # Create empty row with same number of columns
        new_row = [''] * len(self.csv_headers)
        new_row[0] = 'Test Case'  # Set default Work Item Type
        
        # Add to tree
        self.tree.insert('', 'end', values=new_row, tags=('testcase',))
        
        # Add to internal data
        self.csv_rows.append(new_row)
        
        # Mark as modified
        self.csv_modified = True
        self.modified_label.config(text="● Modified (unsaved)")
    
    def duplicate_row(self, item):
        """Duplicate selected row"""
        values = list(self.tree.item(item, 'values'))
        
        # Get tags from original row
        tags = self.tree.item(item, 'tags')
        
        # Insert duplicate after the original
        row_index = self.tree.index(item)
        self.tree.insert('', row_index + 1, values=values, tags=tags)
        
        # Add to internal data
        self.csv_rows.insert(row_index + 1, values)
        
        # Mark as modified
        self.csv_modified = True
        self.modified_label.config(text="● Modified (unsaved)")
    
    def delete_row(self, item):
        """Delete selected row"""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this row?"):
            row_index = self.tree.index(item)
            self.tree.delete(item)
            del self.csv_rows[row_index]
            
            # Mark as modified
            self.csv_modified = True
            self.modified_label.config(text="● Modified (unsaved)")
    
    def delete_selected_row(self):
        """Delete currently selected row"""
        if not hasattr(self, 'tree'):
            return
        
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a row to delete.")
            return
        
        self.delete_row(selected[0])
    
    def save_csv_changes(self):
        """Save changes back to CSV file"""
        if not self.csv_modified:
            messagebox.showinfo("No Changes", "No changes to save.")
            return
        
        try:
            # Write to CSV
            with open(self.current_csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerow(self.csv_headers)
                writer.writerows(self.csv_rows)
            
            self.csv_modified = False
            self.modified_label.config(text="✓ Saved")
            messagebox.showinfo("Success", "Changes saved successfully!")
            
            self.log_message(f"✓ Changes saved to: {self.current_csv_file}", "SUCCESS")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save changes:\n{str(e)}")
    
    def refresh_summary_view(self):
        """Refresh the summary view after edits"""
        # This would require storing references to the summary widgets
        # For now, just inform user to switch tabs to see updates
        pass
    
    def refresh_summary_view(self):
        """Refresh the summary view after edits"""
        # This would require storing references to the summary widgets
        # For now, just inform user to switch tabs to see updates
        pass
    
    def create_summary_view(self, parent, csv_file):
        """Create summary view of test cases"""
        # Create text widget with scrollbar
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        text.pack(fill=tk.BOTH, expand=True)
        
        # Read and parse CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Count test cases by type
        test_cases = {}
        current_test = None
        step_count = 0
        
        for row in rows:
            if row.get('Work Item Type'):  # Test case row
                if current_test:
                    test_cases[current_test]['steps'] = step_count
                current_test = row.get('Title', 'Untitled')
                test_cases[current_test] = {
                    'type': row.get('Work Item Type'),
                    'steps': 0
                }
                step_count = 0
            else:  # Step row
                step_count += 1
        
        if current_test:
            test_cases[current_test]['steps'] = step_count
        
        # Count by prefix
        func_count = sum(1 for t in test_cases.keys() if t.startswith('FUNC-'))
        val_count = sum(1 for t in test_cases.keys() if t.startswith('VAL-'))
        ui_count = sum(1 for t in test_cases.keys() if t.startswith('UI-'))
        neg_count = sum(1 for t in test_cases.keys() if t.startswith('NEG-'))
        reg_count = sum(1 for t in test_cases.keys() if t.startswith('REG-'))
        
        # Display summary
        text.insert(tk.END, "═" * 80 + "\n")
        text.insert(tk.END, "TEST CASE GENERATION SUMMARY\n")
        text.insert(tk.END, "═" * 80 + "\n\n")
        
        text.insert(tk.END, f"Total Test Cases: {len(test_cases)}\n\n")
        
        text.insert(tk.END, "By Type:\n")
        text.insert(tk.END, f"  • Functional (FUNC):   {func_count}\n")
        text.insert(tk.END, f"  • Validation (VAL):    {val_count}\n")
        text.insert(tk.END, f"  • UI Tests (UI):       {ui_count}\n")
        text.insert(tk.END, f"  • Negative (NEG):      {neg_count}\n")
        text.insert(tk.END, f"  • Regression (REG):    {reg_count}\n\n")
        
        text.insert(tk.END, "─" * 80 + "\n\n")
        text.insert(tk.END, "Test Case Details:\n\n")
        
        # List all test cases with steps
        for i, (title, info) in enumerate(test_cases.items(), 1):
            text.insert(tk.END, f"{i}. {title}\n")
            text.insert(tk.END, f"   Steps: {info['steps']}\n\n")
        
        text.insert(tk.END, "─" * 80 + "\n")
        text.insert(tk.END, "\n💡 Review the test cases to ensure:\n")
        text.insert(tk.END, "   ✓ All requirements are covered\n")
        text.insert(tk.END, "   ✓ Steps are clear and actionable\n")
        text.insert(tk.END, "   ✓ Expected results are specific\n")
        text.insert(tk.END, "   ✓ No duplicate test cases\n")
        text.insert(tk.END, "   ✓ Edge cases are included\n")
        
        # Update stats label
        self.stats_label.config(
            text=f"Total: {len(test_cases)} test cases | FUNC: {func_count} | VAL: {val_count} | UI: {ui_count} | NEG: {neg_count} | REG: {reg_count}"
        )
        
        text.config(state=tk.DISABLED)
    
    def create_cos_coverage_view(self, parent, csv_file):
        """Create view showing how test cases map to Conditions of Satisfaction"""
        # Button frame at top
        button_frame = ttk.Frame(parent, padding="10")
        button_frame.pack(fill=tk.X)
        
        self.add_coverage_btn = ttk.Button(
            button_frame,
            text="🤖 Add Missing Coverage with AI",
            command=lambda: self.add_missing_cos_coverage(csv_file),
            state=tk.DISABLED
        )
        self.add_coverage_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            button_frame,
            text="(Generate test cases for COS that aren't covered)",
            font=("Arial", 8),
            foreground="gray"
        ).pack(side=tk.LEFT, padx=5)
        
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        text.pack(fill=tk.BOTH, expand=True)
        
        # Store reference for later updates
        self.cos_coverage_text = text
        
        # Check if we have work item data
        if not self.current_work_item_data:
            text.insert(tk.END, "⚠️ Work item data not available.\n\n")
            text.insert(tk.END, "COS coverage analysis requires the original work item JSON.\n")
            text.insert(tk.END, "Generate test cases from a work item to see COS coverage.\n")
            text.config(state=tk.DISABLED)
            return
        
        # Extract COS from work item
        fields = self.current_work_item_data.get('fields', {})
        acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
        title = fields.get('System.Title', 'Unknown')
        work_item_type = fields.get('System.WorkItemType', 'Work Item')
        
        # Read test cases
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Parse test cases
        test_cases = []
        current_test = None
        
        for row in rows:
            if row.get('Work Item Type'):  # Test case row
                current_test = {
                    'title': row.get('Title', 'Untitled'),
                    'type': row.get('Work Item Type'),
                    'cos_ref': row.get('COS Reference', ''),
                    'steps': []
                }
                test_cases.append(current_test)
            elif current_test and row.get('Test Step'):  # Step row
                current_test['steps'].append({
                    'step': row.get('Test Step'),
                    'action': row.get('Step Action', ''),
                    'expected': row.get('Step Expected', '')
                })
        
        # Parse COS from acceptance criteria
        cos_list = self.parse_cos_from_acceptance_criteria(acceptance_criteria)
        
        # Display header
        text.insert(tk.END, "═" * 80 + "\n")
        text.insert(tk.END, "CONDITIONS OF SATISFACTION (COS) COVERAGE ANALYSIS\n")
        text.insert(tk.END, "═" * 80 + "\n\n")
        
        text.insert(tk.END, f"{work_item_type}: {title}\n")
        text.insert(tk.END, f"Total Test Cases: {len(test_cases)}\n")
        text.insert(tk.END, f"Conditions of Satisfaction Found: {len(cos_list)}\n\n")
        
        if not cos_list:
            text.insert(tk.END, "⚠️ No structured Conditions of Satisfaction found.\n\n")
            text.insert(tk.END, "Acceptance Criteria (Raw):\n")
            text.insert(tk.END, "─" * 80 + "\n")
            text.insert(tk.END, acceptance_criteria or "(No acceptance criteria provided)\n")
            text.insert(tk.END, "\n" + "─" * 80 + "\n\n")
            text.insert(tk.END, "💡 TIP: For better COS analysis, structure acceptance criteria with:\n")
            text.insert(tk.END, "   - Numbered or bulleted lists\n")
            text.insert(tk.END, "   - Clear 'Given/When/Then' statements\n")
            text.insert(tk.END, "   - Separate requirements per line\n")
        else:
            # Show COS with mapped test cases
            text.insert(tk.END, "─" * 80 + "\n\n")
            
            for i, cos in enumerate(cos_list, 1):
                text.insert(tk.END, f"COS {i}: {cos}\n")
                text.insert(tk.END, "─" * 80 + "\n")
                
                # Find test cases that address this COS (by COS index)
                relevant_tests = self.find_tests_for_cos(i - 1, test_cases)  # i-1 because enumerate starts at 1
                
                if relevant_tests:
                    text.insert(tk.END, f"✓ Addressed by {len(relevant_tests)} test case(s):\n\n")
                    for test_title in relevant_tests:
                        text.insert(tk.END, f"  • {test_title}\n")
                        # Find COS reference for this test
                        test = next((tc for tc in test_cases if tc['title'] == test_title), None)
                        if test and test.get('cos_ref'):
                            reason = self.explain_test_cos_match(test['cos_ref'])
                            text.insert(tk.END, f"    Reason: {reason}\n")
                    text.insert(tk.END, "\n")
                else:
                    text.insert(tk.END, "❌ NOT ADDRESSED - Missing test coverage!\n\n")
                
                text.insert(tk.END, "\n")
        
        # Show test cases not clearly mapped to any COS
        text.insert(tk.END, "═" * 80 + "\n")
        text.insert(tk.END, "ADDITIONAL TEST CASES (Not directly mapped to COS)\n")
        text.insert(tk.END, "═" * 80 + "\n\n")
        
        mapped_tests = set()
        missing_cos = []
        for i, cos in enumerate(cos_list):
            relevant = self.find_tests_for_cos(i, test_cases)
            mapped_tests.update(relevant)
            if not relevant:
                missing_cos.append((i + 1, cos))  # Store as tuple (COS number, COS text)
        
        # Store missing COS for later use
        self.current_missing_cos = missing_cos
        self.current_csv_for_cos_coverage = csv_file
        
        # Enable button if there are missing COS
        if missing_cos and self.api_key.get().strip():
            self.add_coverage_btn.config(state=tk.NORMAL)
        
        unmapped_tests = [tc['title'] for tc in test_cases if tc['title'] not in mapped_tests]
        
        if unmapped_tests:
            text.insert(tk.END, "These test cases provide additional coverage:\n\n")
            for test_title in unmapped_tests:
                text.insert(tk.END, f"  • {test_title}\n")
        else:
            text.insert(tk.END, "All test cases are mapped to COS.\n")
        
        text.insert(tk.END, "\n" + "═" * 80 + "\n")
        text.insert(tk.END, "\n💡 RECOMMENDATIONS:\n")
        text.insert(tk.END, "   • Ensure every COS has at least one test case\n")
        text.insert(tk.END, "   • Add negative/edge case tests for critical COS\n")
        text.insert(tk.END, "   • Review unmapped tests to verify they add value\n")
        
        if missing_cos:
            text.insert(tk.END, f"\n⚠️  {len(missing_cos)} COS missing coverage - Click 'Add Missing Coverage with AI' to generate tests\n")
        
        text.config(state=tk.DISABLED)
    
    def parse_cos_from_acceptance_criteria(self, acceptance_criteria):
        """Parse Conditions of Satisfaction from acceptance criteria text"""
        if not acceptance_criteria:
            return []
        
        cos_list = []
        import re
        
        # First, try to extract list items from HTML if present
        if '<li>' in acceptance_criteria or '<LI>' in acceptance_criteria:
            # Extract text from <li> tags, but handle nested lists
            li_pattern = r'<li[^>]*>(.*?)</li>'
            li_matches = re.findall(li_pattern, acceptance_criteria, re.IGNORECASE | re.DOTALL)
            for item in li_matches:
                # Check if this item contains nested <ul> or <ol> tags
                has_nested_list = '<ul>' in item.lower() or '<ol>' in item.lower()
                
                if has_nested_list:
                    # Extract the main text before the nested list
                    main_text_pattern = r'^(.*?)(?:<ul>|<ol>)'
                    main_match = re.search(main_text_pattern, item, re.IGNORECASE | re.DOTALL)
                    if main_match:
                        clean_item = re.sub(r'<[^>]+>', '', main_match.group(1)).strip()
                        if clean_item:
                            cos_list.append(clean_item)
                else:
                    # Remove remaining HTML tags from the item
                    clean_item = re.sub(r'<[^>]+>', '', item).strip()
                    # Skip very short items that are likely sub-bullets (like "SSM" or "SSM Types")
                    # unless they contain meaningful context words
                    if clean_item and (len(clean_item) > 30 or any(word in clean_item.lower() for word in ['verify', 'ensure', 'check', 'test', 'should', 'must', 'user', 'system'])):
                        cos_list.append(clean_item)
        
        # If we found items from HTML lists, return them
        if cos_list:
            return cos_list
        
        # Otherwise, parse plain text
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', acceptance_criteria)
        
        # Split by newlines and process each line
        lines = clean_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for numbered or bulleted items
            # Patterns: 1. , 1) , - , * , • , etc.
            cos_pattern = r'^(?:\d+[\.)]|[-*•]|\[[xX\s]\])\s*(.+)$'
            match = re.match(cos_pattern, line)
            
            if match:
                cos_list.append(match.group(1).strip())
            elif len(line) > 20:  # Standalone sentence/requirement
                # Could be a COS if it's substantial
                if any(keyword in line.lower() for keyword in ['should', 'must', 'shall', 'will', 'can', 'user', 'system', 'given', 'when', 'then', 'verify']):
                    cos_list.append(line)
        
        return cos_list
    
    def find_tests_for_cos(self, cos_index, test_cases):
        """Find which test cases address this COS by reading the COS Reference column"""
        relevant_tests = []
        
        # COS index is 0-based in our list, but in CSV it's labeled as "COS 1", "COS 2", etc.
        cos_label = f"COS {cos_index + 1}"
        
        for test in test_cases:
            cos_ref = test.get('cos_ref', '').strip()
            if cos_ref:
                # Handle multiple COS references (e.g., "COS 1; COS 2")
                if cos_label in cos_ref or f"COS {cos_index + 1}" in cos_ref:
                    relevant_tests.append(test['title'])
        
        return relevant_tests
    
    def explain_test_cos_match(self, cos_ref):
        """Generate explanation showing the explicit COS reference"""
        return f"Explicitly addresses {cos_ref}"
    
    def add_missing_cos_coverage(self, csv_file):
        """Generate test cases for COS that aren't covered"""
        if not hasattr(self, 'current_missing_cos') or not self.current_missing_cos:
            messagebox.showinfo("No Missing Coverage", "All COS are already covered!")
            return
        
        if not self.api_key.get().strip():
            messagebox.showerror("API Key Required", "Please configure your AI API key to generate test cases.")
            return
        
        # Confirm with user
        missing_count = len(self.current_missing_cos)
        response = messagebox.askyesno(
            "Generate Missing Coverage",
            f"Generate test cases for {missing_count} missing COS?\n\n"
            f"This will add new test cases to your existing CSV file."
        )
        
        if not response:
            return
        
        # Disable button and show progress
        self.add_coverage_btn.config(state=tk.DISABLED, text="Generating...")
        self.update_status("Generating test cases for missing COS...")
        
        # Run in thread
        def worker():
            try:
                success = self.generate_missing_cos_tests(csv_file, self.current_missing_cos)
                
                self.add_coverage_btn.config(state=tk.NORMAL, text="🤖 Add Missing Coverage with AI")
                
                if success:
                    self.update_status("Missing COS coverage added successfully!")
                    messagebox.showinfo(
                        "Coverage Added",
                        f"Added test cases for {missing_count} missing COS!\n\n"
                        f"Check the updated test cases in the viewer."
                    )
                    # Refresh the viewer
                    self.show_test_case_viewer(csv_file)
                else:
                    self.update_status("Failed to generate missing coverage")
            except Exception as e:
                self.add_coverage_btn.config(state=tk.NORMAL, text="🤖 Add Missing Coverage with AI")
                self.log_message(f"Error: {str(e)}", "ERROR")
                self.update_status("Error generating coverage")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def generate_missing_cos_tests(self, csv_file, missing_cos):
        """Use AI to generate test cases for missing COS"""
        try:
            self.log_message("=" * 60)
            self.log_message("Generating Missing COS Coverage", "INFO")
            self.log_message("=" * 60)
            
            # Read existing CSV
            self.log_message(f"Reading existing test cases from: {csv_file}")
            with open(csv_file, 'r', encoding='utf-8') as f:
                existing_csv = f.read()
            
            # Get work item info
            fields = self.current_work_item_data.get('fields', {})
            title = fields.get('System.Title', 'Unknown')
            
            # Setup AI client
            provider = self.ai_provider.get()
            api_key = self.api_key.get().strip()
            
            self.log_message(f"Initializing {provider.upper()} AI...")
            
            try:
                from openai import OpenAI
            except ImportError:
                self.log_message("Error: openai package not installed", "ERROR")
                messagebox.showerror("Missing Package", "Please install: pip install openai")
                return False
            
            # Use appropriate model
            if provider == "github":
                client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
                model = self.selected_model
            elif provider == "openai":
                client = OpenAI(api_key=api_key)
                model = self.selected_model
            else:  # azure
                client = OpenAI(api_key=api_key)
                model = self.selected_model
            
            # Build list of missing COS with numbers
            missing_cos_text = "\n".join(f"COS {cos_num}: {cos_text}" for cos_num, cos_text in missing_cos)
            
            # Build prompt
            prompt = f"""You are a QA expert. The following Conditions of Satisfaction (COS) are NOT covered by existing test cases.

MISSING COS (need test coverage):
{missing_cos_text}

EXISTING TEST CASES (for context):
{existing_csv}

TASK:
Generate NEW test cases ONLY for the missing COS listed above. Use these guidelines:
1. Create comprehensive test cases that specifically address each missing COS
2. Use appropriate prefixes: FUNC-XX (Functional), VAL-XX (Validation), UI-XX (UI), NEG-XX (Negative)
3. Continue numbering from the existing test cases (check the CSV for the last number used)
4. Follow the EXACT CSV format: Work Item Type,Title,Test Step,Step Action,Step Expected,COS Reference
5. CRITICAL: Each test case MUST include the COS number it addresses in the "COS Reference" column (e.g., "COS 1", "COS 2", etc.)
6. Each test case structure:
   Test Case,<PREFIX>-XX: Test Title,,,,COS X
   , ,1,Step action,Expected result,
   , ,2,Next step action,Expected result,

IMPORTANT:
- Generate ONLY the new test cases (don't repeat existing ones)
- NO COMMAS inside text fields
- Start with the header row
- Make test cases specific to the missing COS
- ALWAYS include the COS Reference column

OUTPUT:
Return ONLY the CSV content for the NEW test cases."""
            
            self.log_message(f"Generating test cases for {len(missing_cos)} missing COS...")
            self.log_message("This may take 30-60 seconds...")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert QA analyst who creates targeted test cases for missing coverage."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            new_tests_csv = response.choices[0].message.content
            
            # Clean up response
            if "```" in new_tests_csv:
                parts = new_tests_csv.split("```")
                for part in parts:
                    if "Work Item Type" in part or "Title" in part:
                        new_tests_csv = part.strip()
                        if new_tests_csv.startswith("csv\n"):
                            new_tests_csv = new_tests_csv[4:]
                        break
            
            # Remove header from new tests (we'll append to existing)
            lines = new_tests_csv.split('\n')
            if lines and 'Work Item Type' in lines[0]:
                new_tests_csv = '\n'.join(lines[1:])
            
            # Backup original
            backup_file = csv_file.replace(".csv", "_before_missing_cos.csv")
            import shutil
            shutil.copy(csv_file, backup_file)
            self.log_message(f"Backup saved: {backup_file}", "INFO")
            
            # Append new tests
            with open(csv_file, 'a', encoding='utf-8', newline='') as f:
                if not existing_csv.endswith('\n'):
                    f.write('\n')
                f.write(new_tests_csv)
            
            self.log_message(f"✓ Added test cases for {len(missing_cos)} missing COS!", "SUCCESS")
            self.log_message(f"Updated file: {csv_file}", "SUCCESS")
            
            return True
            
        except Exception as e:
            self.log_message(f"Error generating missing coverage: {str(e)}", "ERROR")
            messagebox.showerror("Generation Failed", f"Error:\n{str(e)}")
            return False
    
    def create_raw_view(self, parent, csv_file):
        """Create raw CSV view"""
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text = scrolledtext.ScrolledText(text_frame, wrap=tk.NONE, font=("Consolas", 9))
        text.pack(fill=tk.BOTH, expand=True)
        
        # Read and display raw CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            text.insert(tk.END, content)
        
        text.config(state=tk.DISABLED)
    
    def open_csv_file(self, csv_file):
        """Open CSV file in default editor"""
        try:
            os.startfile(csv_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{str(e)}")
    
    def open_file_location(self, csv_file):
        """Open file location in explorer"""
        try:
            folder = os.path.dirname(csv_file)
            os.startfile(folder)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open location:\n{str(e)}")
    
    def show_screenshot_analysis_tab(self, csv_file):
        """Show tab for screenshot-based test case enhancement"""
        # Remove existing screenshot tab if present
        if self.screenshot_tab:
            try:
                self.notebook.forget(self.screenshot_tab)
            except:
                pass
        
        # Create new screenshot analysis tab
        self.screenshot_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.screenshot_tab, text="📸 Screenshot Analysis")
        
        self.current_csv_for_screenshot = csv_file
        self.pasted_screenshot = None
        
        # Title
        title_frame = ttk.Frame(self.screenshot_tab, padding="10")
        title_frame.pack(fill=tk.X)
        
        ttk.Label(
            title_frame,
            text="Enhance Test Cases with Screenshot Analysis",
            font=("Arial", 14, "bold")
        ).pack()
        
        ttk.Label(
            title_frame,
            text="AI will analyze your screenshot to identify missing test cases and enhance existing ones",
            font=("Arial", 10)
        ).pack(pady=5)
        
        # Instructions frame
        inst_frame = ttk.LabelFrame(self.screenshot_tab, text="How to Use", padding="15")
        inst_frame.pack(fill=tk.X, padx=10, pady=10)
        
        instructions = """1. Copy a screenshot to your clipboard (Win+Shift+S, PrtScn, or Snipping Tool)
2. Click 'Paste Screenshot from Clipboard' below
3. Preview your screenshot to ensure it's correct
4. Click 'Analyze & Enhance Test Cases'
5. AI will update your test cases based on what it sees"""
        
        ttk.Label(inst_frame, text=instructions, justify=tk.LEFT).pack()
        
        if not PIL_AVAILABLE:
            warning_frame = ttk.Frame(inst_frame)
            warning_frame.pack(pady=10, fill=tk.X)
            
            ttk.Label(
                warning_frame,
                text="⚠ PIL/Pillow is required for clipboard functionality",
                foreground="orange",
                font=("Arial", 10, "bold")
            ).pack()
            
            ttk.Button(
                warning_frame,
                text="📦 Install Pillow Now",
                command=self.install_pillow
            ).pack(pady=5)
            
            ttk.Label(
                warning_frame,
                text="(Or install manually with: pip install pillow)",
                foreground="gray",
                font=("Arial", 8, "italic")
            ).pack()
        
        # Screenshot area
        screenshot_frame = ttk.LabelFrame(self.screenshot_tab, text="Screenshot", padding="15")
        screenshot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Button frame
        button_frame = ttk.Frame(screenshot_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        paste_btn = ttk.Button(
            button_frame,
            text="📋 Paste Screenshot from Clipboard",
            command=self.paste_screenshot_from_clipboard
        )
        paste_btn.pack(side=tk.LEFT, padx=5)
        if not PIL_AVAILABLE:
            paste_btn.config(state=tk.DISABLED)
        
        ttk.Button(
            button_frame,
            text="🗑️ Clear Screenshot",
            command=self.clear_screenshot
        ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.screenshot_status = ttk.Label(screenshot_frame, text="No screenshot loaded", foreground="gray")
        self.screenshot_status.pack(pady=5)
        
        # Preview frame with scrollbar
        preview_container = ttk.Frame(screenshot_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for image preview
        self.screenshot_canvas = tk.Canvas(preview_container, bg="white", height=300)
        scrollbar_y = ttk.Scrollbar(preview_container, orient="vertical", command=self.screenshot_canvas.yview)
        scrollbar_x = ttk.Scrollbar(screenshot_frame, orient="horizontal", command=self.screenshot_canvas.xview)
        
        self.screenshot_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.screenshot_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(fill=tk.X)
        
        # Action buttons at bottom
        action_frame = ttk.Frame(self.screenshot_tab, padding="15")
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.analyze_btn = ttk.Button(
            action_frame,
            text="🔍 Analyze & Enhance Test Cases",
            command=self.analyze_screenshot_and_enhance,
            state=tk.DISABLED,
            style="Accent.TButton"
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.summary_btn = ttk.Button(
            action_frame,
            text="📋 View Summary",
            command=self.show_analysis_summary,
            state=tk.DISABLED
        )
        self.summary_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(
            action_frame,
            text="💡 AI will read existing test cases and update them based on screenshot",
            font=("Segoe UI", 9),
            foreground="#666"
        ).pack(side=tk.LEFT, padx=10)
    
    def show_analysis_summary(self):
        """Display the analysis summary in a new window"""
        if not self.last_analysis_summary:
            messagebox.showinfo("No Summary", "No analysis summary available yet.")
            return
        
        # Create summary window
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Screenshot Analysis Summary")
        summary_window.geometry("700x500")
        
        # Title
        title_frame = ttk.Frame(summary_window, padding="10")
        title_frame.pack(fill=tk.X)
        ttk.Label(
            title_frame,
            text="Changes Made by AI",
            font=("Arial", 14, "bold")
        ).pack()
        
        # Summary text area
        text_frame = ttk.Frame(summary_window, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        summary_text = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=("Arial", 10),
            padx=10,
            pady=10
        )
        summary_text.pack(fill=tk.BOTH, expand=True)
        summary_text.insert("1.0", self.last_analysis_summary)
        summary_text.config(state=tk.DISABLED)
        
        # Close button
        button_frame = ttk.Frame(summary_window, padding="10")
        button_frame.pack(fill=tk.X)
        ttk.Button(
            button_frame,
            text="Close",
            command=summary_window.destroy
        ).pack()
    
    def paste_screenshot_from_clipboard(self):
        """Paste screenshot from clipboard"""
        if not PIL_AVAILABLE:
            messagebox.showerror(
                "PIL Not Available",
                "PIL/Pillow is required for clipboard functionality.\n\n"
                "Install it with:\npip install pillow"
            )
            return
        
        try:
            # Get image from clipboard
            img = ImageGrab.grabclipboard()
            
            if img is None:
                messagebox.showwarning(
                    "No Image",
                    "No image found in clipboard.\n\n"
                    "Please copy a screenshot first (Win+Shift+S or PrtScn)"
                )
                return
            
            if not isinstance(img, Image.Image):
                messagebox.showwarning(
                    "Invalid Clipboard Content",
                    "Clipboard does not contain an image.\n\n"
                    "Please copy a screenshot first."
                )
                return
            
            # Store the image
            self.pasted_screenshot = img
            
            # Update UI
            self.screenshot_status.config(
                text=f"✓ Screenshot loaded ({img.width}x{img.height} pixels)",
                foreground="green"
            )
            self.analyze_btn.config(state=tk.NORMAL)
            
            # Display preview (scaled down if needed)
            self.display_screenshot_preview(img)
            
            self.log_message("✓ Screenshot pasted from clipboard", "SUCCESS")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to paste screenshot:\n{str(e)}")
            self.log_message(f"Error pasting screenshot: {e}", "ERROR")
    
    def clear_screenshot(self):
        """Clear the pasted screenshot"""
        self.pasted_screenshot = None
        self.screenshot_status.config(text="No screenshot loaded", foreground="gray")
        self.analyze_btn.config(state=tk.DISABLED)
        self.screenshot_canvas.delete("all")
        self.log_message("Screenshot cleared", "INFO")
    
    def display_screenshot_preview(self, img):
        """Display screenshot preview on canvas"""
        try:
            # Clear canvas
            self.screenshot_canvas.delete("all")
            
            # Resize if too large (max 800x600 for preview)
            max_width = 800
            max_height = 600
            
            # Calculate scaling
            scale = min(max_width / img.width, max_height / img.height, 1.0)
            new_width = int(img.width * scale)
            new_height = int(img.height * scale)
            
            # Resize image
            preview_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            from tkinter import PhotoImage as tkPhotoImage
            # PIL ImageTk
            try:
                from PIL import ImageTk
                self.photo = ImageTk.PhotoImage(preview_img)
            except ImportError:
                messagebox.showwarning("Preview Unavailable", "ImageTk not available for preview")
                return
            
            # Display on canvas
            self.screenshot_canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.screenshot_canvas.config(scrollregion=self.screenshot_canvas.bbox("all"))
            
        except Exception as e:
            self.log_message(f"Error displaying preview: {e}", "ERROR")
    
    def analyze_screenshot_and_enhance(self):
        """Analyze screenshot and enhance existing test cases"""
        if not self.pasted_screenshot:
            messagebox.showwarning("No Screenshot", "Please paste a screenshot first.")
            return
        
        if not self.api_key.get().strip():
            messagebox.showerror(
                "API Key Required",
                "Please enter your API key/token in the 'Generate Test Cases' tab first."
            )
            return
        
        # Run in thread
        def worker():
            try:
                self.progress.start()
                self.analyze_btn.config(state=tk.DISABLED)
                self.update_status("Analyzing screenshot...")
                
                success = self.enhance_test_cases_with_screenshot(
                    self.current_csv_for_screenshot,
                    self.pasted_screenshot
                )
                
                self.progress.stop()
                self.analyze_btn.config(state=tk.NORMAL)
                
                if success:
                    self.update_status("Screenshot analysis complete!")
                    # Refresh the viewer tab
                    self.show_test_case_viewer(self.current_csv_for_screenshot)
                else:
                    self.update_status("Screenshot analysis failed")
                    
            except Exception as e:
                self.progress.stop()
                self.analyze_btn.config(state=tk.NORMAL)
                self.log_message(f"Error: {str(e)}", "ERROR")
                self.update_status("Error during analysis")
        
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    
    def enhance_test_cases_with_screenshot(self, csv_file, screenshot_img):
        """Use AI to enhance existing test cases based on screenshot"""
        try:
            self.log_message("=" * 60)
            self.log_message("Screenshot Analysis", "INFO")
            self.log_message("=" * 60)
            
            # Read existing CSV
            self.log_message(f"Reading existing test cases from: {csv_file}")
            with open(csv_file, 'r', encoding='utf-8') as f:
                existing_csv = f.read()
            
            # Encode screenshot to base64
            self.log_message("Encoding screenshot...")
            buffered = io.BytesIO()
            screenshot_img.save(buffered, format="PNG")
            screenshot_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Setup AI client
            provider = self.ai_provider.get()
            api_key = self.api_key.get().strip()
            
            self.log_message(f"Initializing {provider.upper()} AI...")
            
            try:
                from openai import OpenAI
            except ImportError:
                self.log_message("Error: openai package not installed", "ERROR")
                messagebox.showerror("Missing Package", "Please install: pip install openai")
                return False
            
            # Use appropriate model
            if provider == "github":
                client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
                model = self.selected_model
            elif provider == "openai":
                client = OpenAI(api_key=api_key)
                model = self.selected_model
            else:  # azure
                client = OpenAI(api_key=api_key)
                model = self.selected_model
            
            # Build prompt for enhancement
            prompt = f"""You are a QA expert analyzing test cases and a screenshot together.

CURRENT TEST CASES (CSV format):
{existing_csv}

SCREENSHOT PROVIDED: A screenshot showing the UI/feature being tested.

YOUR TASK:
1. Analyze the screenshot carefully
2. Review the existing test cases
3. Identify what's MISSING from the test cases based on what you see in the screenshot
4. Identify test cases that could be ENHANCED with more specific details from the screenshot
5. Generate an UPDATED CSV with:
   - All original test cases (kept or enhanced)
   - New test cases for anything visible in the screenshot that isn't tested
   - Enhanced step details using exact labels, buttons, fields visible in the screenshot
   - New validation test cases based on UI elements (required fields, character limits, etc.)

IMPORTANT:
- Use the EXACT same CSV format: Work Item Type,Title,Test Step,Step Action,Step Expected
- Test cases start with "Test Case" in first column
- Steps are separate rows with step numbers
- NO COMMAS inside text fields
- Keep existing test case numbering scheme (FUNC-XX, VAL-XX, UI-XX, NEG-XX, REG-XX)
- Add new test cases with next available numbers

OUTPUT FORMAT:
First, provide a SUMMARY section explaining what you changed and why:
---SUMMARY---
[Your detailed explanation of changes made]

Then provide the complete updated CSV:
---CSV---
[Complete CSV with header row]
"""
            
            self.log_message("Calling AI with screenshot analysis...")
            self.log_message("This may take 30-60 seconds...")
            
            # Make API call with vision
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert QA analyst who enhances test cases based on screenshot analysis."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_base64}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            response_content = response.choices[0].message.content
            
            # Parse summary and CSV from response
            summary = "No summary provided"
            csv_content = response_content
            
            if "---SUMMARY---" in response_content and "---CSV---" in response_content:
                parts = response_content.split("---CSV---")
                if len(parts) == 2:
                    summary_part = parts[0].replace("---SUMMARY---", "").strip()
                    csv_content = parts[1].strip()
                    summary = summary_part
            
            # Clean up CSV response (handle code blocks)
            if "```" in csv_content:
                code_parts = csv_content.split("```")
                for part in code_parts:
                    if "Work Item Type" in part or "Title" in part:
                        csv_content = part.strip()
                        if csv_content.startswith("csv\n"):
                            csv_content = csv_content[4:]
                        break
            
            # Log the summary
            self.log_message("=" * 60)
            self.log_message("CHANGES SUMMARY:", "INFO")
            self.log_message("=" * 60)
            for line in summary.split('\n'):
                if line.strip():
                    self.log_message(line, "INFO")
            self.log_message("=" * 60)
            
            # Save updated CSV
            backup_file = csv_file.replace(".csv", "_before_screenshot.csv")
            import shutil
            shutil.copy(csv_file, backup_file)
            self.log_message(f"Backup saved: {backup_file}", "INFO")
            
            # Parse and rewrite CSV with proper quoting
            import io
            reader = csv.reader(io.StringIO(csv_content))
            rows = list(reader)
            
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
                writer.writerows(rows)
            
            self.log_message("✓ Test cases enhanced with screenshot analysis!", "SUCCESS")
            self.log_message(f"Updated file: {csv_file}", "SUCCESS")
            
            # Store summary for later viewing
            self.last_analysis_summary = summary
            self.summary_btn.config(state=tk.NORMAL)
            
            # Show simple completion message
            messagebox.showinfo(
                "Analysis Complete",
                f"Test cases have been enhanced!\n\n"
                f"Original saved as:\n{os.path.basename(backup_file)}\n\n"
                f"Click 'View Summary' to see what changed."
            )
            
            return True
            
        except Exception as e:
            self.log_message(f"Error during screenshot analysis: {str(e)}", "ERROR")
            messagebox.showerror("Analysis Failed", f"Error:\n{str(e)}")
            return False


def main():
    """Main entry point"""
    root = tk.Tk()
    app = TestCaseGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
