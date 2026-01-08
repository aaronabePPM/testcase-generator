"""
Test Case Generator - Streamlit Web App
Generates automated test cases from Azure DevOps work items
"""

import streamlit as st
import subprocess
import json
import csv
import sys
import base64
import io
from pathlib import Path
from openai import OpenAI
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Test Case Generator",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main color scheme */
    :root {
        --primary-blue: #0078D4;
        --dark-blue: #005A9E;
        --light-blue: #E6F2FA;
        --gray-bg: #F3F2F1;
        --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Header styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100%;
    }
    
    /* Sidebar styling - reduce right padding */
    [data-testid="stSidebar"] {
        background-color: #F3F2F1;
        border-right: 1px solid #EDEBE9;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-right: 1rem;
    }
    
    [data-testid="stSidebar"] .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Title styling */
    h1 {
        color: #323130;
        font-weight: 600;
        font-size: 2rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid var(--primary-blue);
        margin-bottom: 1.5rem;
    }
    
    /* Subheader styling */
    h2 {
        color: #323130;
        font-weight: 600;
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #605E5C;
        font-weight: 600;
        font-size: 1.25rem;
    }
    
    /* Card styling for sections */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border: 1px solid #EDEBE9;
        border-radius: 4px 4px 0 0;
        padding: 12px 24px;
        font-weight: 600;
        color: #605E5C;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-blue);
        color: white;
        border-color: var(--primary-blue);
    }
    
    /* Button styling */
    .stButton button {
        background-color: var(--primary-blue);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: background-color 0.2s;
    }
    
    .stButton button:hover {
        background-color: var(--dark-blue);
    }
    
    .stDownloadButton button {
        background-color: white;
        color: var(--primary-blue);
        border: 2px solid var(--primary-blue);
        border-radius: 4px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    .stDownloadButton button:hover {
        background-color: var(--light-blue);
    }
    
    /* Sidebar header styling */
    [data-testid="stSidebar"] h2 {
        color: #323130;
        border-bottom: 2px solid var(--primary-blue);
        padding-bottom: 0.5rem;
    }
    
    /* Input field styling */
    .stTextInput input, .stSelectbox select {
        border: 1px solid #8A8886;
        border-radius: 4px;
        padding: 0.5rem;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 1px var(--primary-blue);
    }
    
    /* Info/Warning/Success boxes */
    .stAlert {
        border-radius: 4px;
        border-left: 4px solid;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: 1px solid #EDEBE9;
        border-radius: 4px;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: white;
        border: 1px solid #EDEBE9;
        border-radius: 4px;
        font-weight: 600;
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        color: var(--primary-blue);
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #EDEBE9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_file' not in st.session_state:
    st.session_state.generated_file = None
if 'work_item_data' not in st.session_state:
    st.session_state.work_item_data = None
if 'log_messages' not in st.session_state:
    st.session_state.log_messages = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0  # Track which tab to show
if 'retry_count' not in st.session_state:
    st.session_state.retry_count = 0
if 'last_work_item_id' not in st.session_state:
    st.session_state.last_work_item_id = None
if 'refinement_history' not in st.session_state:
    st.session_state.refinement_history = []  # Track refinement iterations
if 'current_csv' not in st.session_state:
    st.session_state.current_csv = None
if 'refinement_in_progress' not in st.session_state:
    st.session_state.refinement_in_progress = False
if 'last_change_summary' not in st.session_state:
    st.session_state.last_change_summary = None
if 'test_case_coverage' not in st.session_state:
    st.session_state.test_case_coverage = None  # AI-generated categorization

# Setup directories
DATA_DIR = Path("data")
JSON_DIR = DATA_DIR / "json"
TESTCASES_DIR = DATA_DIR / "testcases"
APP_DIR = Path("app")
CONFIG_DIR = Path(".config")
CONFIG_FILE = CONFIG_DIR / "user_settings.json"

JSON_DIR.mkdir(parents=True, exist_ok=True)
TESTCASES_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def log_message(message, level="INFO"):
    """Add message to log"""
    st.session_state.log_messages.append(f"[{level}] {message}")

def load_saved_api_key():
    """Load saved API key from config file"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('api_key', '')
    except Exception as e:
        log_message(f"Could not load saved API key: {str(e)}", "WARNING")
    return ''

def save_api_key(api_key):
    """Save API key to config file"""
    try:
        config = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        
        config['api_key'] = api_key
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        log_message("✓ API key saved", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"Could not save API key: {str(e)}", "ERROR")
        return False

def check_az_login():
    """Check if Azure CLI is logged in"""
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True
        )
        return result.returncode == 0
    except Exception:
        return False

def trigger_az_login():
    """Trigger Azure CLI login"""
    try:
        log_message("Triggering Azure CLI login...", "INFO")
        # Run az login - this opens a browser window
        result = subprocess.run(
            ["az", "login"],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minutes timeout for login
            shell=True
        )
        
        if result.returncode == 0:
            log_message("✓ Azure CLI login successful", "SUCCESS")
            return True
        else:
            log_message(f"Azure CLI login failed: {result.stderr}", "ERROR")
            return False
    except subprocess.TimeoutExpired:
        log_message("Azure CLI login timed out", "ERROR")
        return False
    except Exception as e:
        log_message(f"Error during Azure CLI login: {str(e)}", "ERROR")
        return False

def verify_model_access(api_key, provider, model):
    """Verify that the API key has access to the selected model"""
    try:
        if provider == "github":
            client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=api_key
            )
            # Try a minimal completion to verify access
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True, "Model is accessible"
        elif provider == "anthropic":
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                # Test with a minimal message
                response = client.messages.create(
                    model=model,
                    max_tokens=5,
                    messages=[{"role": "user", "content": "test"}]
                )
                return True, "Model is accessible"
            except ImportError:
                return False, "Anthropic package not installed"
        elif provider == "openai":
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True, "Model is accessible"
        return False, "Unknown provider"
    except Exception as e:
        return False, str(e)

def export_work_item(work_item_id, org_url):
    """Export work item from Azure DevOps"""
    output_file = JSON_DIR / f"PBI-{work_item_id}.json"
    
    try:
        cmd = [
            "az", "boards", "work-item", "show",
            "--id", str(work_item_id),
            "--organization", org_url,
            "--output", "json"
        ]
        
        log_message(f"Exporting work item {work_item_id}...")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            shell=True  # Windows requires shell=True
        )
        
        if result.returncode != 0:
            log_message(f"Export failed: {result.stderr}", "ERROR")
            return None
            
        # Save JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
            
        log_message(f"✓ Work item exported successfully", "SUCCESS")
        
        # Parse and return data
        work_item_data = json.loads(result.stdout)
        
        # Debug: Log available fields to help diagnose issues
        if 'fields' in work_item_data:
            fields = work_item_data['fields']
            log_message(f"Work item has {len(fields)} fields", "INFO")
            
            # Check for acceptance criteria variations
            ac_field = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', None)
            if ac_field:
                log_message(f"Found AcceptanceCriteria field ({len(str(ac_field))} chars)", "INFO")
            else:
                log_message("AcceptanceCriteria field is empty or missing", "WARNING")
                # Log all field names that contain 'accept', 'criteria', 'expect', or 'result'
                relevant_fields = [k for k in fields.keys() if any(term in k.lower() for term in ['accept', 'criteria', 'expect', 'result'])]
                if relevant_fields:
                    log_message(f"Related fields found: {', '.join(relevant_fields)}", "INFO")
        
        return work_item_data
        
    except subprocess.TimeoutExpired:
        log_message("Command timed out", "ERROR")
        return None
    except FileNotFoundError:
        log_message("Azure CLI not found. Please ensure 'az' is installed", "ERROR")
        return None
    except Exception as e:
        log_message(f"Error: {str(e)}", "ERROR")
        return None

def encode_image_to_base64(uploaded_file):
    """Encode uploaded image to base64"""
    return base64.b64encode(uploaded_file.read()).decode('utf-8')

def generate_change_summary(old_csv, new_csv, api_key, provider, model):
    """Generate a summary of changes between old and new test cases"""
    try:
        log_message("Generating change summary...")
        
        # Parse CSVs to count test cases
        import csv
        import io
        
        old_reader = csv.reader(io.StringIO(old_csv))
        old_rows = list(old_reader)
        old_test_cases = [row for row in old_rows if row and row[0] == "Test Case"]
        
        new_reader = csv.reader(io.StringIO(new_csv))
        new_rows = list(new_reader)
        new_test_cases = [row for row in new_rows if row and row[0] == "Test Case"]
        
        # Extract test case titles for comparison
        old_titles = set([tc[1] if len(tc) > 1 else "" for tc in old_test_cases])
        new_titles = set([tc[1] if len(tc) > 1 else "" for tc in new_test_cases])
        
        added_titles = new_titles - old_titles
        removed_titles = old_titles - new_titles
        kept_titles = old_titles & new_titles
        
        system_prompt = "You are a QA analyst that concisely summarizes changes in test cases. Be specific about what was added, modified, or removed."
        
        user_prompt = f"""Analyze these test case changes and provide a clear, concise summary.

STATISTICS:
- Original: {len(old_test_cases)} test cases
- Refined: {len(new_test_cases)} test cases
- Added: {len(added_titles)} new test cases
- Removed: {len(removed_titles)} test cases
- Kept/Modified: {len(kept_titles)} test cases

NEW TEST CASES ADDED:
{chr(10).join(['- ' + title for title in list(added_titles)[:10]]) if added_titles else "None"}

REMOVED TEST CASES:
{chr(10).join(['- ' + title for title in list(removed_titles)[:10]]) if removed_titles else "None"}

ORIGINAL CSV SAMPLE:
{old_csv[:2000]}

REFINED CSV SAMPLE:
{new_csv[:2000]}

Provide a brief summary (3-5 bullet points) highlighting:
- What new test cases were added and why they're valuable
- What test cases were removed or modified
- Key improvements in test coverage or quality
- Any patterns in the changes (e.g., added negative tests, improved steps, etc.)

Keep it concise, user-friendly, and focus on the most important changes."""
        
        # Use simple completion for summary
        if provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model=model,
                max_tokens=500,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            summary = response.content[0].text.strip()
        else:
            if provider == "github":
                client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
            else:
                client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            summary = response.choices[0].message.content.strip()
        
        return summary
    except Exception as e:
        log_message(f"Could not generate change summary: {str(e)}", "WARNING")
        return "Changes applied successfully. Review the updated test cases in the Preview tab."

def categorize_test_cases_with_ai(csv_content, work_item_data, api_key, provider, model):
    """Ask AI to categorize which test cases directly address COS/Expected Results vs additional considerations"""
    try:
        log_message("Analyzing test case coverage with AI...")
        
        fields = work_item_data.get('fields', {})
        work_item_type = fields.get('System.WorkItemType', 'Product Backlog Item')
        acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
        
        if not acceptance_criteria:
            acceptance_criteria = fields.get('Custom.ExpectedResults', '')
        
        criteria_label = "Expected Results" if work_item_type == "Bug" else "Conditions of Satisfaction (COS)"
        
        system_prompt = "You are a QA expert that analyzes test case coverage against acceptance criteria."
        
        user_prompt = f"""Analyze these test cases and categorize them based on whether they DIRECTLY address the specified {criteria_label} or are ADDITIONAL considerations.

{criteria_label.upper()}:
{acceptance_criteria if acceptance_criteria else 'None specified'}

GENERATED TEST CASES (CSV):
{csv_content}

For each test case in the CSV, determine:
1. Does it DIRECTLY test one of the {criteria_label}? 
2. Or is it an ADDITIONAL consideration (edge cases, negative tests, extra validation, etc.)?

Return a JSON object with this structure:
{{
  "direct_coverage": [
    {{
      "test_title": "FUNC-01: Test Name",
      "addresses": "Brief explanation of which {criteria_label.lower()} it addresses"
    }}
  ],
  "additional_considerations": [
    {{
      "test_title": "NEG-01: Test Name",
      "purpose": "Brief explanation of what additional coverage it provides"
    }}
  ]
}}

IMPORTANT: Be strict - only categorize as "direct_coverage" if it clearly tests a stated {criteria_label.lower()}. Everything else goes in "additional_considerations".

Return ONLY the JSON object, no other text."""
        
        # Use AI to categorize
        if provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            
            result = response.content[0].text.strip()
        else:
            if provider == "github":
                client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
            else:
                client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content.strip()
        
        # Clean JSON response
        if result.startswith("```json"):
            result = result[7:]
        if result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()
        
        # Parse JSON
        categorization = json.loads(result)
        log_message(f"✓ Coverage analysis complete: {len(categorization.get('direct_coverage', []))} direct, {len(categorization.get('additional_considerations', []))} additional", "SUCCESS")
        return categorization
        
    except Exception as e:
        log_message(f"Could not analyze coverage with AI: {str(e)}", "WARNING")
        return None

def generate_with_refinement(current_csv, refinement_prompt, api_key, provider, model, screenshots=None):
    """Generate refined test cases based on current CSV and additional instructions"""
    try:
        log_message(f"Refining test cases with {model}...")
        
        # Build refinement prompt
        system_prompt = "You are a QA expert that refines and improves manual test cases based on feedback. Always maintain the CSV format and structure."
        
        user_prompt = f"""CURRENT TEST CASES (CSV format):
{current_csv}

REFINEMENT INSTRUCTIONS:
{refinement_prompt}

IMPORTANT RULES:
1. Maintain the exact CSV format with the same header row
2. Keep all existing test cases unless specifically asked to remove them
3. Apply the refinement instructions to improve/add/modify test cases
4. NEVER use commas in text fields - use semicolons instead
5. Each Test Case is ONE row, each Step is a separate row
6. Return ONLY the complete CSV - NO explanatory text
"""
        
        # Handle different providers with vision support for screenshots
        if provider == "anthropic":
            try:
                import anthropic
            except ImportError:
                log_message("Installing anthropic package...", "INFO")
                subprocess.run([sys.executable, "-m", "pip", "install", "anthropic"], check=True)
                import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Build message content with screenshots if provided
            message_content = [{"type": "text", "text": user_prompt}]
            
            if screenshots:
                for screenshot in screenshots:
                    image_data = encode_image_to_base64(screenshot)
                    message_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": screenshot.type,
                            "data": image_data
                        }
                    })
                    log_message(f"✓ Attached screenshot: {screenshot.name}", "INFO")
            
            response = client.messages.create(
                model=model,
                max_tokens=4000,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": message_content}]
            )
            
            csv_content = response.content[0].text.strip()
            
        else:
            # OpenAI-compatible APIs (GitHub Models and OpenAI) with vision support
            if provider == "github":
                client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
            else:  # openai
                client = OpenAI(api_key=api_key)
            
            # Build message content with screenshots if provided
            message_content = [{"type": "text", "text": user_prompt}]
            
            if screenshots:
                for screenshot in screenshots:
                    image_data = encode_image_to_base64(screenshot)
                    message_content.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{screenshot.type};base64,{image_data}"
                        }
                    })
                    log_message(f"✓ Attached screenshot: {screenshot.name}", "INFO")
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_content}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            csv_content = response.choices[0].message.content.strip()
        
        # Clean up response
        if csv_content.startswith("```csv"):
            csv_content = csv_content[6:]
        if csv_content.startswith("```"):
            csv_content = csv_content[3:]
        if csv_content.endswith("```"):
            csv_content = csv_content[:-3]
        
        csv_content = csv_content.strip()
        
        # Sanitize CSV content
        csv_content = sanitize_csv_content(csv_content)
        
        log_message("✓ Test cases refined successfully", "SUCCESS")
        return csv_content
        
    except Exception as e:
        error_msg = str(e)
        log_message(f"AI refinement failed: {error_msg}", "ERROR")
        
        # Return error details for display
        return {'error': True, 'message': error_msg}

def generate_with_ai(work_item_data, api_key, provider, model, retry_feedback=None):
    """Generate test cases using AI"""
    try:
        # Read template
        template_file = APP_DIR / "testcase_template.csv"
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Build prompt
        prompt = build_prompt(work_item_data, template_content)
        
        # If this is a retry, add specific feedback
        if retry_feedback:
            prompt += f"\n\n⚠️ PREVIOUS ATTEMPT HAD ERRORS - PLEASE FIX:\n{retry_feedback}\n\nGenerate the CSV again with these issues corrected."
        
        log_message(f"Generating test cases with {model}...")
        
        # Handle different providers
        if provider == "anthropic":
            # Use Anthropic API directly
            try:
                import anthropic
            except ImportError:
                log_message("Installing anthropic package...", "INFO")
                import subprocess
                subprocess.run([sys.executable, "-m", "pip", "install", "anthropic"], check=True)
                import anthropic
            
            client = anthropic.Anthropic(api_key=api_key)
            
            response = client.messages.create(
                model=model,
                max_tokens=4000,
                temperature=0.7,
                system="You are a QA expert that generates comprehensive manual test cases in CSV format. ALWAYS use commas as delimiters and properly escape any commas within text fields.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            csv_content = response.content[0].text.strip()
            
        else:
            # Use OpenAI-compatible API (GitHub Models and OpenAI)
            if provider == "github":
                client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=api_key
                )
            else:  # openai
                client = OpenAI(api_key=api_key)
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a QA expert that generates comprehensive manual test cases in CSV format. ALWAYS use commas as delimiters and properly escape any commas within text fields."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            csv_content = response.choices[0].message.content.strip()
        
        # Clean up response
        if csv_content.startswith("```csv"):
            csv_content = csv_content[6:]
        if csv_content.startswith("```"):
            csv_content = csv_content[3:]
        if csv_content.endswith("```"):
            csv_content = csv_content[:-3]
        
        csv_content = csv_content.strip()
        
        # Validate and auto-fix CSV structure before sanitizing
        is_valid, validation_messages, csv_content = validate_and_fix_csv_structure(csv_content)
        
        # Store validation warnings to show later, but don't block file generation
        validation_warnings = []
        if not is_valid:
            # Log validation errors but continue - let user see and fix the CSV
            critical_errors = [err for err in validation_messages if 'CRITICAL' in err or 'Too many rows' in err]
            
            if critical_errors:
                error_summary = "\n".join(f"- {err}" for err in critical_errors)
                log_message(f"CSV validation failed: {error_summary}", "ERROR")
                validation_warnings = critical_errors
                # Continue anyway - don't return error, let the file be saved
        
        # Log any non-critical fixes that were applied
        if validation_messages:
            for msg in validation_messages:
                if 'Auto-fixed' in msg:
                    log_message(msg, "INFO")
        
        # Sanitize CSV content to remove problematic commas
        csv_content = sanitize_csv_content(csv_content)
        
        log_message("✓ Test cases generated successfully", "SUCCESS")
        
        # Return CSV content with validation warnings if any
        if validation_warnings:
            return {'csv_content': csv_content, 'validation_warnings': validation_warnings}
        return csv_content
        
    except Exception as e:
        error_msg = str(e)
        log_message(f"AI generation failed: {error_msg}", "ERROR")
        
        # Return error details for display
        return {'error': True, 'message': error_msg}

def sanitize_csv_content(csv_content):
    """Clean and properly escape CSV content to handle commas and special characters"""
    import csv
    import io
    
    try:
        # Parse the CSV content using csv reader to properly handle quoted fields
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        
        log_message(f"CSV parsing: {len(rows)} total rows (including header)", "INFO")
        
        # Rebuild with proper escaping
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        for row_num, row in enumerate(rows, 1):
            # Replace commas with semicolons in text fields (except when properly quoted)
            cleaned_row = []
            for cell in row:
                # Remove any stray commas that aren't part of numbers
                if cell and not cell.replace('.', '').replace('-', '').isdigit():
                    # Replace commas with semicolons
                    cell = cell.replace(',', ';')
                cleaned_row.append(cell)
            writer.writerow(cleaned_row)
        
        result = output.getvalue()
        log_message(f"✓ CSV content sanitized - {len(rows)} rows preserved", "SUCCESS")
        return result
        
    except Exception as e:
        log_message(f"Warning: CSV sanitization error: {str(e)} - returning original content", "WARNING")
        # If sanitization completely fails, return original to avoid data loss
        return csv_content

def validate_and_fix_csv_structure(csv_content):
    """Validate CSV structure and attempt to fix common issues automatically"""
    import csv
    import io
    
    errors = []
    fixed = False
    
    try:
        # First, remove trailing commas from each line to prevent extra columns
        lines = csv_content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Count trailing commas and remove if more than expected
            stripped = line.rstrip(',')
            # Count commas in cleaned line
            comma_count = stripped.count(',')
            # If we had 6+ commas (creating 7+ fields), the line likely had trailing commas
            if line.count(',') > comma_count:
                log_message(f"Removed {line.count(',') - comma_count} trailing comma(s) from line", "INFO")
                cleaned_lines.append(stripped)
                fixed = True
            else:
                cleaned_lines.append(line)
        
        csv_content = '\n'.join(cleaned_lines)
        
        # Try to parse as CSV
        reader = csv.reader(io.StringIO(csv_content))
        rows = list(reader)
        
        if not rows:
            errors.append("CSV is empty")
            return False, errors, csv_content
        
        # Check header
        header = rows[0]
        expected_cols = 6  # Should have 6 columns
        
        if len(header) != expected_cols:
            errors.append(f"CRITICAL: Header has {len(header)} columns, expected {expected_cols}")
            return False, errors, csv_content
        
        # Validate the header structure (flexible for PBI vs Bug)
        expected_first_five = ["Work Item Type", "Title", "Test Step", "Step Action", "Step Expected"]
        valid_last_columns = ["COS Reference", "Expected Results", "COS Reference/Expected Results"]
        
        # Check first 5 columns match expected (case-insensitive and trimmed)
        header_lower = [col.strip().lower() for col in header]
        expected_lower = [col.strip().lower() for col in expected_first_five]
        
        for idx, (actual, expected) in enumerate(zip(header_lower[:5], expected_lower)):
            if actual != expected:
                errors.append(f"CRITICAL: Column {idx + 1} is '{header[idx]}', expected '{expected_first_five[idx]}'")
        
        # Check 6th column is one of the valid options
        sixth_col = header[5].strip()
        if sixth_col not in valid_last_columns:
            # Check case-insensitive match
            sixth_col_lower = sixth_col.lower()
            valid_lower = [col.lower() for col in valid_last_columns]
            if sixth_col_lower not in valid_lower:
                log_message(f"Warning: 6th column is '{sixth_col}', expected 'COS Reference' or 'Expected Results'", "WARNING")
        
        # If we found critical header errors, return failure
        critical_header_errors = [err for err in errors if 'CRITICAL' in err]
        if critical_header_errors:
            return False, errors, csv_content
        
        # Count rows with wrong column count
        wrong_col_count = 0
        rows_to_fix = []
        
        for idx, row in enumerate(rows[1:], start=1):
            if len(row) != expected_cols:
                wrong_col_count += 1
                rows_to_fix.append((idx, len(row)))
                if wrong_col_count <= 3:  # Only report first 3
                    errors.append(f"Row {idx + 1} has {len(row)} columns")
        
        # If more than 30% of rows have wrong column count, it's unfixable
        total_data_rows = len(rows) - 1
        if total_data_rows > 0 and (wrong_col_count / total_data_rows) > 0.3:
            errors.append(f"Too many rows with wrong column count: {wrong_col_count}/{total_data_rows}")
            return False, errors, csv_content
        
        # If only some rows have wrong column count, try to auto-fix
        if wrong_col_count > 0 and wrong_col_count <= total_data_rows * 0.3:
            log_message(f"Auto-fixing {wrong_col_count} rows with incorrect column count...", "INFO")
            
            # Rebuild CSV with fixed rows
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(header)
            
            # Fix data rows
            for row in rows[1:]:
                if len(row) < expected_cols:
                    # Pad with empty strings
                    row = row + [''] * (expected_cols - len(row))
                elif len(row) > expected_cols:
                    # Truncate extra columns
                    row = row[:expected_cols]
                writer.writerow(row)
            
            csv_content = output.getvalue()
            fixed = True
            log_message(f"✓ Auto-fixed {wrong_col_count} rows", "SUCCESS")
        
        # Check for unescaped quotes (warning only, not blocking)
        if '"""' in csv_content:
            log_message("Warning: Detected triple quotes in CSV", "WARNING")
        
        # If we fixed issues, return success with fixed content
        if fixed:
            return True, [f"Auto-fixed {wrong_col_count} rows with wrong column count"], csv_content
        
        # If no errors, validation passed
        if not errors:
            return True, [], csv_content
        
        # Minor issues that were noted but not blocking
        return True, errors, csv_content
        
    except csv.Error as e:
        errors.append(f"CSV parsing error: {str(e)}")
        return False, errors, csv_content
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
        return False, errors, csv_content

# Default prompt template
DEFAULT_PROMPT_TEMPLATE = """Generate comprehensive manual test cases for this Azure DevOps work item:

WORK ITEM DETAILS:
Type: {work_item_type}
Title: {title}
Description: {description}
Acceptance Criteria: {acceptance_criteria}
Repro Steps: {repro_steps}

TEMPLATE FORMAT:
{template_content}

CRITICAL REQUIREMENTS:

1. TEST CASE COVERAGE:
   - Create manual test cases covering Functional, Validation, UI, Negative, and Regression scenarios as applicable
   - Pay special attention to any DeveloperNotes field in the work item - this outlines the developer's work and must be covered
   - Map each test case to relevant features/requirements from Title, Description, Acceptance Criteria, and DeveloperNotes
   - Create a reasonable number of test steps — enough to reproduce the scenario and verify success/failure

2. TEST CASE TITLES:
   - Must start with a type prefix: FUNC-XX, VAL-XX, UI-XX, NEG-XX, or REG-XX (pick the right prefix per test)
   - Must NOT contain the PBI/Bug number
   - Example: "FUNC-01: User Login Validation" not "PBI-5105699: User Login Validation"

3. CSV FORMAT RULES (⚠️ CRITICAL):
   - DELIMITER: Use COMMAS (,) as the delimiter between columns
   - EXACTLY 6 COLUMNS: Work Item Type,Title,Test Step,Step Action,Step Expected,{last_column}
   - Header row MUST be: Work Item Type,Title,Test Step,Step Action,Step Expected,{last_column}
   - Each Test Case is ONE row with: "Test Case","full title","","","","{last_column_lower} reference"
   - Each Step is a SEPARATE row with: "","","step number","action","expected result",""
   - NEVER mix Test Case-level and Test Step values on the same row
   - ALL rows must have EXACTLY 6 columns

4. QUOTE HANDLING (⚠️ CRITICAL):
   - Simple text: No quotes needed
   - Text with commas: MUST be enclosed in double quotes
   - Text with quotes: Escape internal quotes by doubling them (use two quote marks not one)
   - Example: "Click button, wait, verify" should become "Click button; wait; verify" OR place in quotes
   - DO NOT use triple or unmatched quotes
   - DO NOT mix quote styles

5. COMMA HANDLING (⚠️ CRITICAL):
   - Commas are ONLY used as column separators
   - If text contains commas, you have TWO options:
     a) Replace commas with semicolons: "Item1; Item2; Item3"
     b) Enclose entire cell in double quotes
   - Option (a) is STRONGLY PREFERRED for simplicity
   - Use semicolons for lists and dashes for pauses

6. CONTENT GUIDELINES:
   - {last_column_description}
   - Include clear preconditions, steps, and expected results for each step
   - Keep steps concise and avoid unnecessary commas
   - Use plain text only (no markup, no HTML)

OUTPUT FORMAT:
⚠️ Return ONLY the CSV data - NO explanatory text, NO markdown formatting.
Start directly with the header row.
⚠️ FINAL CHECKLIST BEFORE RESPONDING:
  ☑ All rows have exactly 6 columns
  ☑ Commas in text are either replaced with semicolons OR the cell is quoted
  ☑ No improperly escaped quotes
  ☑ Each test case is on its own row, separate from test steps
  ☑ Quotes within quoted text are properly escaped
"""

def load_custom_prompt():
    """Load custom prompt from config file"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get('custom_prompt', None)
    except Exception as e:
        log_message(f"Could not load custom prompt: {str(e)}", "WARNING")
    return None

def save_custom_prompt(prompt):
    """Save custom prompt to config file"""
    try:
        config = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        
        config['custom_prompt'] = prompt
        
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        log_message("✓ Custom prompt saved", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"Could not save custom prompt: {str(e)}", "ERROR")
        return False

def reset_to_default_prompt():
    """Remove custom prompt from config file"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
            
            if 'custom_prompt' in config:
                del config['custom_prompt']
                
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=2)
                
                log_message("✓ Reset to default prompt", "SUCCESS")
        return True
    except Exception as e:
        log_message(f"Could not reset prompt: {str(e)}", "ERROR")
        return False

def build_prompt(work_item_data, template_content):
    """Build AI prompt"""
    fields = work_item_data.get('fields', {})
    
    title = fields.get('System.Title', 'N/A')
    description = fields.get('System.Description', 'N/A')
    acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', 'N/A')
    repro_steps = fields.get('Microsoft.VSTS.TCM.ReproSteps', 'N/A')
    work_item_type = fields.get('System.WorkItemType', 'Product Backlog Item')
    
    # Determine the last column header based on work item type
    last_column = "Expected Results" if work_item_type == "Bug" else "COS Reference"
    last_column_description = (
        "Expected Results: The expected behavior when the bug is fixed" if work_item_type == "Bug"
        else "COS Reference: Which Condition of Satisfaction (COS) this test case addresses"
    )
    
    # Use custom prompt if available, otherwise use default
    custom_prompt = load_custom_prompt()
    prompt_template = custom_prompt if custom_prompt else DEFAULT_PROMPT_TEMPLATE
    
    prompt = prompt_template.format(
        work_item_type=work_item_type,
        title=title,
        description=description,
        acceptance_criteria=acceptance_criteria,
        repro_steps=repro_steps,
        template_content=template_content,
        last_column=last_column,
        last_column_lower=last_column.lower(),
        last_column_description=last_column_description
    )
    
    return prompt

def save_test_cases(work_item_id, csv_content):
    """Save test cases to file"""
    output_file = TESTCASES_DIR / f"Testcases_PBI_{work_item_id}.csv"
    
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write(csv_content)
        
        log_message(f"✓ Test cases saved to {output_file}", "SUCCESS")
        return output_file
        
    except Exception as e:
        log_message(f"Error saving file: {str(e)}", "ERROR")
        return None

# Main App Layout
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
    }
</style>
<div style='background: linear-gradient(90deg, #0078D4 0%, #005A9E 100%); padding: 30px 50px; margin: -2rem -2rem 2rem -2rem; border-radius: 0;'>
    <h1 style='color: white; margin: 0; font-weight: 600; font-size: 2.5em;'>Azure DevOps Test Case Generator</h1>
    <p style='color: white; margin: 10px 0 0 0; opacity: 0.95; font-size: 1.2em;'>Generate comprehensive test cases from Azure DevOps work items using AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    
    # Azure DevOps Settings
    st.subheader("Azure DevOps")
    
    # Check Azure CLI status
    az_logged_in = check_az_login()
    if az_logged_in:
        st.success("✓ Azure CLI: Authenticated")
    else:
        st.warning("⚠️ Azure CLI: Not logged in")
        st.caption("The app will prompt for login when needed")
    
    org_url = st.text_input(
        "Organization URL",
        value="https://dev.azure.com/hexagonPPMCOL",
        help="Your Azure DevOps organization URL"
    )
    
    # AI Settings
    st.subheader("AI Configuration")
    
    ai_provider = st.selectbox(
        "AI Provider",
        options=["github", "openai", "anthropic"],
        format_func=lambda x: {"github": "GitHub Models", "openai": "OpenAI", "anthropic": "Anthropic (Claude)"}[x]
    )
    
    # Load saved API key if available
    saved_key = load_saved_api_key()
    
    api_key = st.text_input(
        "API Key",
        value=saved_key,
        type="password",
        help="Your GitHub token, OpenAI API key, or Anthropic API key"
    )
    
    # Option to save API key
    if api_key and api_key != saved_key:
        if st.checkbox("Save API key for future sessions", value=False):
            save_api_key(api_key)
    
    if ai_provider == "github":
        model = st.selectbox(
            "Model",
            options=[
                "Mistral-large-2411",
                "Mistral-Nemo",
                "Mistral-small",
                "Meta-Llama-3.1-405B-Instruct",
                "Meta-Llama-3.1-70B-Instruct",
                "Meta-Llama-3.1-8B-Instruct",
                "Cohere-command-r-plus",
                "Cohere-command-r",
                "AI21-Jamba-1.5-Large",
                "AI21-Jamba-1.5-Mini",
                "Phi-3.5-MoE-instruct",
                "Phi-3.5-mini-instruct",
                "gpt-4o",
                "gpt-4o-mini"
            ],
            index=0,
            help="Mistral-large-2411 is recommended for test case generation. Note: Claude is only available via Anthropic provider.",
            key="model_selector"
        )
    elif ai_provider == "anthropic":
        model = st.selectbox(
            "Model",
            options=[
                "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-20240620",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ],
            index=0,
            help="Claude models excel at structured output generation",
            key="model_selector"
        )
    else:  # openai
        model = st.selectbox(
            "Model",
            options=["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
            index=0,
            key="model_selector"
        )
    
    # Store in session state for access across tabs
    st.session_state.model = model
    st.session_state.ai_provider = ai_provider
    st.session_state.api_key = api_key
    
    # Test Connection Button
    if api_key:
        if st.button("🔍 Test Model Connection", width="stretch"):
            with st.spinner("Testing connection..."):
                success, message = verify_model_access(api_key, ai_provider, model)
                if success:
                    st.success(f"✓ Connected! {message}")
                else:
                    st.error(f"✗ Connection failed: {message}")
    
    st.divider()
    
    # Prompt Customization Section
    st.subheader("Prompt Editor")
    
    with st.expander("Customize AI Prompt", expanded=False):
        st.markdown("**Edit the prompt template used for test case generation**")
        st.caption("Use {placeholders} for dynamic values: {work_item_type}, {title}, {description}, {acceptance_criteria}, {repro_steps}, {template_content}, {last_column}, {last_column_lower}, {last_column_description}")
        
        # Load current prompt (custom or default)
        current_prompt = load_custom_prompt()
        using_custom = current_prompt is not None
        
        if using_custom:
            st.info("✏️ Using custom prompt")
        else:
            st.info("📄 Using default prompt")
            current_prompt = DEFAULT_PROMPT_TEMPLATE
        
        # Text area for editing
        edited_prompt = st.text_area(
            "Prompt Template",
            value=current_prompt,
            height=400,
            help="Edit the prompt template. Variables in {curly braces} will be replaced with work item data.",
            label_visibility="collapsed"
        )
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Save Custom Prompt", width="stretch"):
                if save_custom_prompt(edited_prompt):
                    st.success("✓ Custom prompt saved!")
                    st.rerun()
                else:
                    st.error("Failed to save prompt")
        
        with col2:
            if st.button("🔄 Reset to Default", width="stretch", disabled=not using_custom):
                if reset_to_default_prompt():
                    st.success("✓ Reset to default prompt!")
                    st.rerun()
                else:
                    st.error("Failed to reset prompt")
    
    st.divider()
    
    # Help Section
    with st.expander("ℹ️ Help & Prerequisites"):
        st.markdown("""
        **Prerequisites:**
        - Azure CLI installed and configured
        - Run `az login` before using this app
        - Valid API key for your chosen provider
        
        **Available Models:**
        - **GitHub Models:** Mistral, Llama, Cohere, Phi (Recommended: Mistral Large)
        - **Anthropic:** Claude 3.5 Sonnet, Opus, Haiku (Claude NOT on GitHub Models)
        - **OpenAI:** GPT-4, GPT-3.5
        
        **⚠️ Important:** Claude models are ONLY available via Anthropic provider, not GitHub Models!
        
        **How to get API keys:**
        - GitHub: [github.com/settings/tokens](https://github.com/settings/tokens)
        - Anthropic: [console.anthropic.com](https://console.anthropic.com)
        - OpenAI: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
        
        **How to use:**
        1. Configure Azure DevOps URL (left)
        2. Select AI provider and model (left)
        3. Enter your API key (left)
        4. Click "🔍 Test Model Connection" to verify (left)
        5. Enter Work Item ID (right)
        6. Click "Generate Test Cases" (right)
        7. Review and download results
        """)

# Main Content Area

# Work Item Input Section (moved from sidebar)
st.subheader("Work Item ID #")
col1, col2 = st.columns([1.5, 3.5])

with col1:
    work_item_id = st.text_input(
        "Work Item ID",
        help="Enter the PBI or Bug number",
        placeholder="e.g., 5105699",
        label_visibility="collapsed",
        disabled=st.session_state.refinement_in_progress,
        key="work_item_input"
    )

with col2:
    generate_btn = st.button(
        "Generate Test Cases", 
        type="primary",
        disabled=st.session_state.refinement_in_progress,
        key="generate_button"
    )

st.divider()

# Handle generation
if generate_btn:
    if not work_item_id:
        st.error("⚠️ Please enter a Work Item ID")
    elif not work_item_id.isdigit():
        st.error("⚠️ Work Item ID must be a number")
    elif not api_key:
        st.error("⚠️ Please enter an API key in the configuration sidebar")
    else:
        # Store settings in session state for potential retries
        st.session_state.api_key = api_key
        st.session_state.ai_provider = ai_provider
        st.session_state.model = model
        st.session_state.last_work_item_id = work_item_id
        st.session_state.retry_count = 0  # Reset retry count for new generation
        
        # Check Azure CLI authentication
        if not check_az_login():
            st.warning("⚠️ Azure CLI is not logged in. Opening login window...")
            
            with st.spinner("Waiting for Azure CLI login (a browser window will open)..."):
                if trigger_az_login():
                    st.success("✓ Azure CLI authentication successful!")
                else:
                    st.error("❌ Azure CLI login failed. Please run 'az login' manually in a terminal and try again.")
                    st.stop()
        
        # Proceed with work item export
        # Clear previous logs
        st.session_state.log_messages = []
        
        with st.spinner("Exporting work item from Azure DevOps..."):
            work_item_data = export_work_item(work_item_id, org_url)
        
        if work_item_data:
            st.session_state.work_item_data = work_item_data
            
            # Store work item details for COS tab
            fields = work_item_data.get('fields', {})
            st.session_state.work_item_title = fields.get('System.Title', 'N/A')
            st.session_state.work_item_type = fields.get('System.WorkItemType', 'Product Backlog Item')
            
            # For Bugs, check both Acceptance Criteria and Repro Steps for expected results
            acceptance_criteria = fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
            
            # Also check custom field (some Azure DevOps instances use custom fields)
            if not acceptance_criteria:
                acceptance_criteria = fields.get('Custom.ExpectedResults', '')
            
            repro_steps = fields.get('Microsoft.VSTS.TCM.ReproSteps', '')
            
            # If bug has no acceptance criteria but has repro steps, use those as the criteria
            if st.session_state.work_item_type == "Bug" and not acceptance_criteria and repro_steps:
                st.session_state.acceptance_criteria = repro_steps
                log_message("Using Repro Steps as acceptance criteria for Bug", "INFO")
            else:
                st.session_state.acceptance_criteria = acceptance_criteria if acceptance_criteria else 'N/A'
            
            # Log what we found
            if st.session_state.acceptance_criteria and st.session_state.acceptance_criteria != 'N/A':
                log_message(f"Found acceptance criteria/expected results ({len(st.session_state.acceptance_criteria)} chars)", "INFO")
            else:
                log_message("No acceptance criteria or expected results found in work item", "WARNING")
            
            # Display work item info
            st.success(f"✓ Exported: {fields.get('System.Title', 'N/A')}")
            
            with st.spinner("Generating test cases with AI..."):
                csv_content = generate_with_ai(work_item_data, api_key, ai_provider, model)
            
            # Check for validation errors and retry with feedback
            if isinstance(csv_content, dict) and csv_content.get('validation_errors'):
                validation_errors = csv_content.get('validation_errors', [])
                error_feedback = "\n".join(f"- {err}" for err in validation_errors)
                
                st.warning(f"⚠️ CSV validation issues detected. Auto-retrying with specific feedback...")
                log_message(f"Critical validation errors: {error_feedback}", "WARNING")
                log_message("Retrying generation with validation feedback...", "INFO")
                
                # Retry with specific feedback about what went wrong
                with st.spinner("Regenerating with corrections..."):
                    csv_content = generate_with_ai(work_item_data, api_key, ai_provider, model, retry_feedback=error_feedback)
                
                # If retry also failed, show clearer message
                if isinstance(csv_content, dict) and csv_content.get('validation_errors'):
                    st.error(f"❌ **CSV Generation Failed After Retry**")
                    st.warning(f"The AI model ({model}) is having difficulty generating a properly formatted CSV file.")
                    st.info("💡 **Suggestions:**\n- Try a different AI model (Mistral-large-2411 or gpt-4o recommended)\n- Check the Activity Log for specific formatting issues")
                    csv_content = None
            
            # Check for other errors
            if isinstance(csv_content, dict) and csv_content.get('error'):
                error_msg = csv_content.get('message', 'Unknown error')
                
                # Check if it's a rate limit error
                if 'RateLimitReached' in error_msg or '429' in error_msg or 'Rate limit' in error_msg:
                    # Extract wait time if available
                    import re
                    wait_match = re.search(r'wait (\d+) seconds', error_msg)
                    if wait_match:
                        wait_seconds = int(wait_match.group(1))
                        wait_hours = wait_seconds // 3600
                        wait_minutes = (wait_seconds % 3600) // 60
                        wait_time_str = f"{wait_hours}h {wait_minutes}m" if wait_hours > 0 else f"{wait_minutes}m"
                        st.error(f"⏱️ **Rate Limit Reached**: You've exceeded the API rate limit. Please wait approximately **{wait_time_str}** before trying again.")
                    else:
                        st.error("⏱️ **Rate Limit Reached**: You've exceeded the API rate limit. Please wait before trying again.")
                    
                    st.info("💡 **Tip**: Consider switching to a different AI provider or model if available.")
                else:
                    st.error(f"❌ **AI Generation Failed**: {error_msg}")
                
                log_message(f"Generation failed with error displayed to user", "INFO")
                csv_content = None
            
            # Handle validation warnings if CSV was generated with issues
            validation_warnings = None
            if csv_content and isinstance(csv_content, dict) and 'csv_content' in csv_content:
                validation_warnings = csv_content.get('validation_warnings', [])
                csv_content = csv_content['csv_content']
            
            if csv_content:
                output_file = save_test_cases(work_item_id, csv_content)
                
                if output_file:
                    st.session_state.generated_file = output_file
                    st.session_state.current_csv = csv_content  # Store for refinement
                    st.session_state.refinement_history = []  # Reset history
                    
                    # Show validation warnings if any
                    if validation_warnings:
                        st.warning("⚠️ **CSV Generated with Issues**")
                        st.markdown("The CSV has been saved, but there are formatting issues:")
                        for warning in validation_warnings:
                            st.markdown(f"- {warning}")
                        st.info("💡 **You can still view and edit the CSV in the Preview tab.** Use the Save button to fix issues manually, or click 'Generate Test Cases' again to retry with AI.")
                    
                    # Analyze test case coverage with AI
                    with st.spinner("Analyzing test case coverage..."):
                        coverage = categorize_test_cases_with_ai(
                            csv_content,
                            work_item_data,
                            api_key,
                            ai_provider,
                            model
                        )
                        st.session_state.test_case_coverage = coverage
                    
                    if not validation_warnings:
                        st.success("✓ Test cases generated successfully!")
                        st.balloons()
                    else:
                        st.success("✓ CSV file generated (with warnings - see above)")
                    # Switch to preview tab after successful generation
                    st.session_state.active_tab = 1
                    st.rerun()

# Tabs for results
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Generated Test Cases", "Preview", "COS/Expected Results", "Refine Test Cases", "Activity Log"])

with tab1:
    # Block tab if refinement is in progress
    if st.session_state.refinement_in_progress:
        st.warning("🔒 Page Locked: Refinement in progress...")
        st.info("Please wait while test cases are being refined. This tab will be available again once refinement completes.")
    elif st.session_state.generated_file and st.session_state.generated_file.exists():
        file_path = st.session_state.generated_file
        
        # First, validate CSV format
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                csv_data = f.read()
            
            # Try to parse CSV to validate format
            df_test = pd.read_csv(file_path)
            
            # CSV is valid - show content
            st.subheader(f"{file_path.name}")
            
            # Download buttons
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="Download CSV File",
                    data=csv_data,
                    file_name=file_path.name,
                    mime="text/csv",
                    width="stretch"
                )
            
            with col2:
                # JSON Download (if available)
                if st.session_state.work_item_data:
                    json_data = json.dumps(st.session_state.work_item_data, indent=2)
                    work_item_id = file_path.name.split('_')[-1].replace('.csv', '')
                    
                    st.download_button(
                        label="Download Work Item JSON",
                        data=json_data,
                        file_name=f"PBI-{work_item_id}.json",
                        mime="application/json",
                        width="stretch"
                    )
            
            # Display content
            st.text_area(
                "CSV Content",
                value=csv_data,
                height=400,
                help="Copy or edit this content before downloading"
            )
            
        except Exception as e:
            # CSV format error detected
            log_message(f"CSV format error in Generated Test Cases tab: {str(e)}", "ERROR")
            
            # Check if we should retry
            if st.session_state.retry_count < 2:  # Max 2 retries
                st.session_state.retry_count += 1
                st.warning(f"⚠️ CSV format error detected. Automatically regenerating test cases (Attempt {st.session_state.retry_count}/2)...")
                log_message(f"Automatic retry {st.session_state.retry_count} due to CSV error", "WARNING")
                
                # Get the work item ID from the filename
                work_item_id = st.session_state.generated_file.name.split('_')[-1].replace('.csv', '')
                
                # Check if we have the necessary data to regenerate
                if st.session_state.work_item_data and 'api_key' in st.session_state:
                    with st.spinner("Regenerating test cases..."):
                        # Get current settings from session state
                        api_key = st.session_state.get('api_key', '')
                        ai_provider = st.session_state.get('ai_provider', 'github')
                        model = st.session_state.get('model', 'Mistral-large-2411')
                        
                        csv_content = generate_with_ai(st.session_state.work_item_data, api_key, ai_provider, model)
                        
                        if csv_content:
                            output_file = save_test_cases(work_item_id, csv_content)
                            if output_file:
                                st.session_state.generated_file = output_file
                                st.session_state.current_csv = csv_content
                                
                                # Re-analyze coverage
                                coverage = categorize_test_cases_with_ai(
                                    csv_content,
                                    st.session_state.work_item_data,
                                    api_key,
                                    ai_provider,
                                    model
                                )
                                st.session_state.test_case_coverage = coverage
                                
                                st.success("Test cases regenerated successfully!")
                                st.rerun()
                        else:
                            st.error("Failed to regenerate test cases. Please try manual regeneration.")
                else:
                    st.error("Cannot auto-regenerate: Missing work item data or API key.")
            else:
                st.error(f"❌ Unable to generate valid CSV after {st.session_state.retry_count} attempts.")
                st.error("The AI-generated content has formatting issues. Please try:")
                st.markdown("""
                - Regenerating with a different AI model
                - Checking the Activity Log for details
                - Manually reviewing the CSV format in the Preview tab
                """)
                
                # Show the raw error for debugging
                with st.expander("View Error Details"):
                    st.code(str(e))
                    st.text("Check the Activity Log tab for more information.")
    else:
        st.info("👆 Enter a Work Item ID above and click 'Generate Test Cases' to get started")

with tab2:
    # Block tab if refinement is in progress
    if st.session_state.refinement_in_progress:
        st.warning("🔒 Page Locked: Refinement in progress...")
        st.info("Please wait while test cases are being refined. This tab will be available again once refinement completes.")
    elif st.session_state.generated_file and st.session_state.generated_file.exists():
        st.subheader("Test Cases Preview")
        
        # Separate CSV parsing from rendering to properly isolate errors
        df = None
        try:
            df = pd.read_csv(st.session_state.generated_file)
            
            # Reset retry count on successful parse
            if st.session_state.retry_count > 0:
                st.session_state.retry_count = 0
                
        except Exception as e:
            log_message(f"CSV parsing error: {str(e)}", "ERROR")
            
            # Check if we should retry
            if st.session_state.retry_count < 2:  # Max 2 retries
                st.session_state.retry_count += 1
                st.warning(f"CSV format error detected. Automatically regenerating test cases (Attempt {st.session_state.retry_count}/2)...")
                log_message(f"Automatic retry {st.session_state.retry_count} due to CSV error", "WARNING")
                
                # Get the work item ID from the filename
                work_item_id = st.session_state.generated_file.name.split('_')[-1].replace('.csv', '')
                
                # Check if we have the necessary data to regenerate
                if st.session_state.work_item_data and 'api_key' in st.session_state:
                    with st.spinner("Regenerating test cases..."):
                        # Get current settings from session state
                        api_key = st.session_state.get('api_key', '')
                        ai_provider = st.session_state.get('ai_provider', 'github')
                        model = st.session_state.get('model', 'Mistral-large-2411')
                        
                        csv_content = generate_with_ai(st.session_state.work_item_data, api_key, ai_provider, model)
                        
                        if csv_content:
                            output_file = save_test_cases(work_item_id, csv_content)
                            if output_file:
                                st.session_state.generated_file = output_file
                                st.success("Test cases regenerated successfully!")
                                st.rerun()
                        else:
                            st.error("Failed to regenerate test cases. Please try manual regeneration.")
                else:
                    st.error("Cannot auto-regenerate: Missing work item data or API key.")
            else:
                st.error(f"Unable to parse CSV after {st.session_state.retry_count} attempts: {str(e)}")
                st.error("Please regenerate test cases manually or check the CSV format in the 'Generated Test Cases' tab.")
                
                # Show the raw error for debugging
                with st.expander("View Error Details"):
                    st.code(str(e))
        
        # If CSV was parsed successfully, display it
        if df is not None:
            try:
                # Display statistics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    test_cases = len(df[df.iloc[:, 0] == "Test Case"])
                    st.metric("Test Cases", test_cases)
                
                with col2:
                    steps = len(df[df.iloc[:, 2].notna()])
                    st.metric("Test Steps", steps)
                
                with col3:
                    # Use AI-generated coverage data if available
                    if st.session_state.test_case_coverage:
                        direct_coverage = len(st.session_state.test_case_coverage.get('direct_coverage', []))
                        st.metric("COS Covered", direct_coverage)
                    else:
                        st.metric("COS Covered", "N/A")
                
                st.divider()
                
                # Add CSS to enable horizontal scrolling and proper column sizing
                st.markdown("""
                    <style>
                        /* Enable horizontal scrolling and auto-size columns based on content */
                        div[data-testid="stDataFrame"] {
                            overflow-x: auto !important;
                            overflow-y: auto !important;
                        }
                        div[data-testid="stDataFrame"] > div {
                            overflow-x: auto !important;
                        }
                        div[data-testid="stDataFrame"] table {
                            width: auto !important;
                            table-layout: auto !important;
                            display: table !important;
                        }
                        div[data-testid="stDataFrame"] th,
                        div[data-testid="stDataFrame"] td {
                            white-space: nowrap !important;
                            min-width: 100px !important;
                            max-width: 400px !important;
                        }
                    </style>
                """, unsafe_allow_html=True)
                
                # Configure columns to size based on content with error handling
                column_config = {}
                for col in df.columns:
                    try:
                        # Check column data type and configure appropriately
                        col_dtype = df[col].dtype
                        
                        # Calculate max content width for each column
                        if not df[col].isna().all():
                            max_length = max(
                                df[col].astype(str).str.len().max(),
                                len(col)
                            )
                        else:
                            max_length = len(col)
                        
                        # Set width based on content (roughly 8 pixels per character)
                        # Convert to Python int to avoid JSON serialization issues with numpy int64
                        # Cap at 400px to ensure scrolling is needed for wide content
                        width_px = int(min(max_length * 8, 400))
                        
                        # Use appropriate column type based on data type
                        if col_dtype in ['float64', 'int64', 'float32', 'int32']:
                            # Numeric column - use NumberColumn
                            column_config[col] = st.column_config.NumberColumn(
                                col,
                                width=width_px
                            )
                        else:
                            # Text column
                            column_config[col] = st.column_config.TextColumn(
                                col,
                                width=width_px
                            )
                    except Exception as col_error:
                        # If column config fails, skip it and use default
                        log_message(f"Column config error for '{col}': {str(col_error)}", "WARNING")
                        pass
                
            except Exception as render_error:
                # If statistics or column config fails, log but continue
                log_message(f"Error preparing display: {str(render_error)}", "WARNING")
                column_config = {}
            
            # Display editable dataframe (outside the try/except to avoid fallback)
            st.caption("✏️ You can edit cells directly in the table below. Click Save Changes to update the CSV file.")
            
            try:
                edited_df = st.data_editor(
                    df,
                    width='content',  # Don't force fit to container - allow horizontal scroll
                    height=500,
                    hide_index=True,
                    column_config=column_config if column_config else None,
                    num_rows="dynamic",  # Allow adding/deleting rows
                    key="preview_editor"
                )
                
                # Add save button and check if data was edited
                has_changes = not edited_df.equals(df)
                
                col1, col2 = st.columns([1, 4])
                with col1:
                    save_button = st.button("💾 Save Changes", disabled=not has_changes, type="primary")
                with col2:
                    if has_changes:
                        st.warning("⚠️ You have unsaved changes")
                
                # Save changes when button is clicked
                if save_button and has_changes:
                    try:
                        # Save the edited data back to CSV
                        edited_df.to_csv(st.session_state.generated_file, index=False)
                        st.session_state.current_csv = edited_df.to_csv(index=False)
                        log_message("✓ Changes saved to CSV", "SUCCESS")
                        st.success("✅ Changes saved successfully!")
                        st.rerun()  # Rerun to clear the "has changes" state
                    except Exception as save_error:
                        log_message(f"Error saving edited CSV: {str(save_error)}", "ERROR")
                        st.error(f"Failed to save changes: {str(save_error)}")
                        
            except Exception as editor_error:
                # If data_editor fails, fall back to simple non-editable display
                log_message(f"Data editor error (using read-only fallback): {str(editor_error)}", "WARNING")
                st.warning("⚠️ Editor unavailable. Displaying in read-only mode.")
                st.dataframe(df, height=500)
    else:
        st.info("Generate test cases to see preview")

with tab3:
    # Block tab if refinement is in progress
    if st.session_state.refinement_in_progress:
        st.warning("🔒 Page Locked: Refinement in progress...")
        st.info("Please wait while test cases are being refined. Coverage analysis will be updated once refinement completes.")
    elif st.session_state.generated_file and st.session_state.generated_file.exists():
        st.subheader("COS/Expected Results Coverage")
        
        try:
            # Get work item type from session state
            work_item_type = st.session_state.get('work_item_type', 'Product Backlog Item')
            work_item_title = st.session_state.get('work_item_title', 'N/A')
            acceptance_criteria = st.session_state.get('acceptance_criteria', 'N/A')
            
            # Determine header based on work item type
            criteria_header = "Expected Results" if work_item_type == "Bug" else "Conditions of Satisfaction (COS)"
            
            st.markdown(f"**Work Item:** {work_item_title}")
            st.markdown(f"**Type:** {work_item_type}")
            
            st.divider()
            
            # Display acceptance criteria/expected results
            st.subheader(f"{criteria_header}")
            
            if acceptance_criteria and acceptance_criteria != 'N/A':
                # Parse COS/Expected Results from HTML
                import re
                from html import unescape
                
                # First, unescape HTML entities
                text = unescape(acceptance_criteria)
                
                # Replace HTML list items and breaks with newlines BEFORE removing tags
                text = re.sub(r'<li[^>]*>', '\n• ', text)  # Replace <li> with bullet
                text = re.sub(r'</li>', '', text)
                text = re.sub(r'<br\s*/?>', '\n', text)  # Replace <br> with newline
                text = re.sub(r'</p>\s*<p>', '\n\n', text)  # Replace paragraph breaks
                text = re.sub(r'<div[^>]*>', '\n', text)  # Replace div starts with newline
                text = re.sub(r'</div>', '', text)
                
                # Now remove remaining HTML tags
                text = re.sub(r'<[^<]+?>', '', text)
                
                # Clean up whitespace but preserve line breaks
                lines = text.split('\n')
                cos_list = []
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 3:  # Skip empty or very short lines
                        cos_list.append(line)
                
                if cos_list:
                    for cos in cos_list:
                        st.markdown(cos)
                else:
                    # Fallback to text area if parsing fails
                    clean_text = re.sub(r'\s+', ' ', text).strip()
                    st.text_area("Details", clean_text, height=200, disabled=True)
            else:
                if work_item_type == "Bug":
                    st.info(f"The 'Acceptance Criteria' field is empty in Azure DevOps. Expected results may be documented in 'Repro Steps' or generated by AI based on the bug description.")
                else:
                    st.info(f"The 'Acceptance Criteria' field is empty in Azure DevOps. Test cases were generated based on the work item description.")
            
            st.divider()
            
            # Show AI-generated coverage analysis
            st.subheader("Test Case Coverage Analysis")
            st.caption("🤖 Analyzed by AI - categorized based on whether tests directly address the criteria above")
            
            coverage = st.session_state.test_case_coverage
            
            if coverage:
                direct = coverage.get('direct_coverage', [])
                additional = coverage.get('additional_considerations', [])
                
                # Filter out any entries with None or empty test_title
                direct = [test for test in direct if test.get('test_title') and test.get('test_title') not in ['None', 'none', '']]
                additional = [test for test in additional if test.get('test_title') and test.get('test_title') not in ['None', 'none', '']]
                
                total_tests = len(direct) + len(additional)
                st.markdown(f"**Total Test Cases Generated:** {total_tests}")
                st.markdown(f"**Direct Coverage:** {len(direct)} test case(s)")
                st.markdown(f"**Additional Considerations:** {len(additional)} test case(s)")
                
                st.divider()
                
                # Display direct coverage
                if direct:
                    st.markdown(f"### ✅ {criteria_header} Directly Addressed ({len(direct)} test cases)")
                    st.caption("These test cases directly validate the specified criteria")
                    
                    for test in direct:
                        with st.expander(f"📌 {test['test_title']}", expanded=False):
                            st.markdown(f"**Addresses:** {test['addresses']}")
                else:
                    st.markdown(f"### ✅ {criteria_header} Directly Addressed")
                    st.info("No test cases were identified as directly addressing the specified criteria. All tests are additional considerations.")
                
                st.markdown("")
                
                # Display additional considerations
                if additional:
                    st.markdown(f"### 📋 Additional Considerations ({len(additional)} test cases)")
                    st.caption("These test cases provide extra coverage beyond the specified criteria")
                    
                    with st.expander("View Additional Test Cases", expanded=False):
                        for test in additional:
                            st.markdown(f"• **{test['test_title']}**")
                            st.caption(f"   _{test['purpose']}_")
                            st.markdown("")
            else:
                st.warning("⚠️ Coverage analysis not available. This may happen if there was an issue during generation.")
                st.info("💡 Try regenerating test cases or use the Refine tab to trigger a new analysis.")
                
        except Exception as e:
            st.error(f"Error displaying coverage: {str(e)}")
    else:
        st.info("Generate test cases to see coverage analysis")

with tab4:
    st.subheader("Refine Test Cases")
    st.markdown("Make iterative improvements to your test cases with additional context, screenshots, or instructions.")
    st.caption("💡 Uses the same AI provider and model configured in the sidebar")
    
    if st.session_state.generated_file and st.session_state.generated_file.exists():
        
        # Show loading overlay if refinement is in progress
        if st.session_state.refinement_in_progress:
            st.warning("🔒 Page Locked: Refinement in progress...")
            st.info("The entire page is locked while test cases are being refined. Please wait - this may take 30-60 seconds. The page will update automatically when complete.")
            st.divider()
        
        # Show last change summary if available
        if st.session_state.last_change_summary:
            st.success("✅ Refinement Complete!")
            with st.expander("📋 What Changed?", expanded=True):
                st.markdown(st.session_state.last_change_summary)
            st.divider()
        
        # Show refinement history
        if st.session_state.refinement_history:
            with st.expander(f"📝 Refinement History ({len(st.session_state.refinement_history)} iterations)", expanded=False):
                for i, entry in enumerate(st.session_state.refinement_history, 1):
                    st.markdown(f"**Iteration {i}:** {entry['prompt'][:100]}...")
                    if entry.get('screenshots'):
                        st.caption(f"   • {len(entry['screenshots'])} screenshot(s) attached")
                    if entry.get('summary'):
                        with st.expander(f"View changes", expanded=False):
                            st.markdown(entry['summary'])
        
        st.divider()
        
        # Refinement input
        st.markdown("### ✏️ Refinement Instructions")
        
        is_refining = st.session_state.refinement_in_progress
        
        refinement_prompt = st.text_area(
            "What would you like to change or improve?",
            height=150,
            placeholder="Examples:\n• Add test cases for error handling scenarios\n• Include more detailed validation steps\n• Add edge cases for user input\n• Update test case titles to be more specific\n• Add security testing scenarios",
            help="Describe what you want to add, modify, or improve in the test cases",
            disabled=is_refining
        )
        
        # Screenshot upload
        st.markdown("### 📸 Screenshots (Optional)")
        
        # Check if current model supports vision
        current_model = st.session_state.get('model', 'Mistral-large-2411')
        vision_models = ['gpt-4-vision', 'gpt-4o', 'gpt-4-turbo', 'claude-3', 'claude-3-opus', 'claude-3-sonnet', 'claude-3-5-sonnet']
        model_supports_vision = any(vm in current_model.lower() for vm in vision_models)
        
        if model_supports_vision:
            st.markdown("✅ **Vision Supported** - Your selected model can analyze screenshots")
            st.caption("Vision-capable models: Claude 3.5 Sonnet, Claude 3 Opus, GPT-4 Vision, GPT-4o, GPT-4 Turbo")
        else:
            st.markdown(f"<div style='color: #d32f2f; font-weight: 500;'>❌ Screenshots Not Supported</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #d32f2f;'>Your current model (<strong>{current_model}</strong>) cannot analyze images. Screenshots will be <strong>ignored</strong> during refinement.</div>", unsafe_allow_html=True)
            st.caption("To use screenshots, switch to a vision-capable model in the sidebar: Claude 3.5 Sonnet, Claude 3 Opus, GPT-4 Vision, GPT-4o, or GPT-4 Turbo")
        
        is_refining = st.session_state.refinement_in_progress
        
        uploaded_screenshots = st.file_uploader(
            "Attach screenshots to provide visual context",
            type=["png", "jpg", "jpeg", "gif"],
            accept_multiple_files=True,
            help="Upload UI screenshots, mockups, or diagrams to help the AI understand visual requirements",
            disabled=(not model_supports_vision) or is_refining
        )
        
        if uploaded_screenshots:
            cols = st.columns(min(len(uploaded_screenshots), 4))
            for idx, screenshot in enumerate(uploaded_screenshots):
                with cols[idx % 4]:
                    st.image(screenshot, caption=screenshot.name, width="stretch")
        
        st.divider()
        
        # Refinement button
        col1, col2 = st.columns([3, 1])
        
        is_refining = st.session_state.refinement_in_progress
        
        with col1:
            if st.button("🔄 Refine Test Cases", type="primary", disabled=is_refining, width="stretch"):
                # Validate prompt is not empty
                if not refinement_prompt or refinement_prompt.strip() == "":
                    st.error("⚠️ Please enter refinement instructions before clicking Refine Test Cases")
                else:
                    # Get current settings from sidebar configuration
                    api_key = st.session_state.get('api_key', '')
                    ai_provider = st.session_state.get('ai_provider', 'github')
                    model = st.session_state.get('model', 'Mistral-large-2411')
                    
                    if not api_key:
                        st.error("Please configure your API key in the sidebar")
                    else:
                        # Log refinement start
                        log_message(f"Starting test case refinement with {model}...", "INFO")
                        log_message(f"Refinement request: {refinement_prompt[:100]}...", "INFO")
                        
                        # Set refinement flag
                        st.session_state.refinement_in_progress = True
                        st.session_state.last_change_summary = None
                        st.rerun()
        
        with col2:
            if st.button("↺ Reset", help="Clear refinement form", disabled=is_refining, width="stretch"):
                st.session_state.last_change_summary = None
                st.rerun()
        
        # Execute refinement if flag is set
        if st.session_state.refinement_in_progress:
            api_key = st.session_state.get('api_key', '')
            ai_provider = st.session_state.get('ai_provider', 'github')
            model = st.session_state.get('model', 'Mistral-large-2411')
            
            log_message("Executing test case refinement...", "INFO")
            
            # Get current CSV content
            current_csv = st.session_state.current_csv
            if not current_csv:
                with open(st.session_state.generated_file, 'r', encoding='utf-8') as f:
                    current_csv = f.read()
            
            # Generate refined version
            refined_csv = generate_with_refinement(
                current_csv,
                refinement_prompt,
                api_key,
                ai_provider,
                model,
                screenshots=uploaded_screenshots
            )
            
            # Check for errors
            if isinstance(refined_csv, dict) and refined_csv.get('error'):
                error_msg = refined_csv.get('message', 'Unknown error')
                
                # Check if it's a rate limit error
                if 'RateLimitReached' in error_msg or '429' in error_msg or 'Rate limit' in error_msg:
                    # Extract wait time if available
                    import re
                    wait_match = re.search(r'wait (\d+) seconds', error_msg)
                    if wait_match:
                        wait_seconds = int(wait_match.group(1))
                        wait_hours = wait_seconds // 3600
                        wait_minutes = (wait_seconds % 3600) // 60
                        wait_time_str = f"{wait_hours}h {wait_minutes}m" if wait_hours > 0 else f"{wait_minutes}m"
                        st.error(f"⏱️ **Rate Limit Reached**: You've exceeded the API rate limit. Please wait approximately **{wait_time_str}** before trying again.")
                    else:
                        st.error("⏱️ **Rate Limit Reached**: You've exceeded the API rate limit. Please wait before trying again.")
                    
                    st.info("💡 **Tip**: Consider switching to a different AI provider or model if available.")
                else:
                    st.error(f"❌ **Refinement Failed**: {error_msg}")
                
                log_message(f"Refinement failed with error displayed to user", "INFO")
                refined_csv = None
            
            if refined_csv:
                log_message("✓ Test case refinement successful", "SUCCESS")
                
                # Generate change summary
                change_summary = generate_change_summary(
                    current_csv,
                    refined_csv,
                    api_key,
                    ai_provider,
                    model
                )
                
                # Save refined version
                work_item_id = st.session_state.last_work_item_id or st.session_state.generated_file.name.split('_')[-1].replace('.csv', '')
                output_file = save_test_cases(work_item_id, refined_csv)
                
                if output_file:
                    st.session_state.generated_file = output_file
                    st.session_state.current_csv = refined_csv
                    st.session_state.last_change_summary = change_summary
                    
                    log_message(f"✓ Refined test cases saved to {output_file.name}", "SUCCESS")
                    
                    # Re-analyze coverage after refinement
                    if st.session_state.work_item_data:
                        log_message("Re-analyzing test case coverage...", "INFO")
                        coverage = categorize_test_cases_with_ai(
                            refined_csv,
                            st.session_state.work_item_data,
                            api_key,
                            ai_provider,
                            model
                        )
                        st.session_state.test_case_coverage = coverage
                        log_message("✓ Coverage analysis updated", "SUCCESS")
                    
                    # Track refinement with summary
                    st.session_state.refinement_history.append({
                        'prompt': refinement_prompt,
                        'screenshots': [s.name for s in uploaded_screenshots] if uploaded_screenshots else None,
                        'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'summary': change_summary
                    })
                    
                    log_message(f"✓ Refinement complete - iteration {len(st.session_state.refinement_history)}", "SUCCESS")
                    st.balloons()
            elif not isinstance(refined_csv, dict):  # Only show if not already shown above
                st.error("❌ Test case refinement failed. Please check the Activity Log for details.")
                log_message("✗ Test case refinement failed", "ERROR")
            
            # Clear refinement flag and rerun
            st.session_state.refinement_in_progress = False
            st.rerun()
        
        st.divider()
        
        # Tips
        with st.expander("💡 Refinement Tips", expanded=False):
            st.markdown("""
            **Effective Refinement Strategies:**
            
            - **Be Specific**: Instead of "add more tests", say "add negative test cases for invalid email formats"
            - **Reference Existing Tests**: "Expand FUNC-01 to include multiple user roles"
            - **Use Screenshots**: Attach UI mockups to explain visual requirements
            - **Iterate Gradually**: Make small, focused changes rather than large rewrites
            - **Validate Logic**: "Add validation for date ranges - start date must be before end date"
            
            **Example Prompts:**
            - "Add 3 negative test cases for the login form: empty username, invalid password, SQL injection attempts"
            - "Include accessibility testing: keyboard navigation, screen reader support, WCAG compliance"
            - "Add performance test cases: load time under 2 seconds, handles 1000 concurrent users"
            - "Update all test case titles to follow the format: [Module]-[Action]-[Expected Result]"
            """)
    else:
        st.info("Generate test cases first to use the refinement feature")

with tab5:
    # Show notice if refinement is in progress
    if st.session_state.refinement_in_progress:
        st.warning("🔒 Page Locked: Refinement in progress...")
        st.info("Activity log updates will appear once refinement completes.")
        st.divider()
    
    st.subheader("Activity Log")
    st.caption("📋 Newest entries appear at the top")
    
    if st.session_state.log_messages:
        # Reverse the list to show newest messages first
        for msg in reversed(st.session_state.log_messages):
            if "[ERROR]" in msg:
                st.error(msg)
            elif "[SUCCESS]" in msg:
                st.success(msg)
            elif "[WARNING]" in msg:
                st.warning(msg)
            else:
                st.info(msg)
    else:
        st.info("No activity yet. Generate or refine test cases to see logs.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
    Test Case Generator v2.0 | Powered by Azure DevOps + AI
</div>
""", unsafe_allow_html=True)
