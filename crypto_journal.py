import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import base64
from io import BytesIO

# Local persistence paths
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
LOGS_FILE = os.path.join(DATA_DIR, 'crypto_logs.json')
CUSTOM_FIELDS_FILE = os.path.join(DATA_DIR, 'custom_fields.json')
FIELD_ORDER_FILE = os.path.join(DATA_DIR, 'field_order.json')
FIELD_TOGGLES_FILE = os.path.join(DATA_DIR, 'field_toggles.json')
THEME_FILE = os.path.join(DATA_DIR, 'theme_settings.json')

# Define all available fields with their configurations
FIELD_CONFIGS = {
    'coin_symbol': {
        'label': 'Coin Symbol/Name',
        'type': 'text_input',
        'help': 'Enter the cryptocurrency symbol or name (e.g., BTC, Ethereum)',
        'placeholder': 'BTC'
    },
    'coin_link': {
        'label': 'Coin Link (Optional)',
        'type': 'text_input',
        'help': 'Enter a link to the coin (e.g., CoinGecko, CoinMarketCap URL)',
        'placeholder': 'https://coingecko.com/en/coins/bitcoin'
    },
    'date_logged': {
        'label': 'Date Logged',
        'type': 'date_input',
        'help': 'Date when this entry was logged',
        'default': datetime.now().date()
    },
    'market_cap': {
        'label': 'Market Cap',
        'type': 'number_input',
        'help': 'Market capitalization in USD',
        'placeholder': '0',
        'value': None
    },
    'trading_volume': {
        'label': 'Trading Volume',
        'type': 'number_input',
        'help': 'Trading volume in USD',
        'placeholder': '0',
        'value': None
    },
    'trading_volume_timeframe': {
        'label': 'Volume Timeframe',
        'type': 'selectbox',
        'help': 'Timeframe for the trading volume',
        'options': ['24h', '4h', '1h', '7d', '30d']
    },
    'conviction_level': {
        'label': 'Conviction Level',
        'type': 'slider',
        'help': 'Your conviction level for this investment (1-10)',
        'min_value': 1,
        'max_value': 10,
        'value': 5,
        'step': 1
    },
    'notes': {
        'label': 'Notes',
        'type': 'text_area',
        'help': 'Additional notes or observations',
        'placeholder': 'Enter your thoughts, analysis, or any other relevant information...'
    },
    'trade_result': {
        'label': 'Trade Result',
        'type': 'selectbox',
        'help': 'Result of the trade (if completed)',
        'options': ['Pending', 'Win', 'Loss']
    }
}

# Field types for custom fields
FIELD_TYPES = {
    'text_input': 'Text Input',
    'number_input': 'Number Input',
    'selectbox': 'Dropdown',
    'slider': 'Slider',
    'text_area': 'Text Area'
}

# Page configuration
st.set_page_config(
    page_title="Lumberjack",
    page_icon="🪵",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_default_field_order():
    """Get the default field order"""
    return {
        'built_in': ['coin_symbol', 'coin_link', 'date_logged', 'market_cap', 'trading_volume', 'trading_volume_timeframe', 'conviction_level', 'notes', 'trade_result'],
        'custom': []
    }

# Initialize session state
if 'log_entries' not in st.session_state:
    st.session_state.log_entries = []

if 'custom_fields' not in st.session_state:
    st.session_state.custom_fields = {}

if 'field_order' not in st.session_state:
    st.session_state.field_order = get_default_field_order()

if 'field_toggles' not in st.session_state:
    st.session_state.field_toggles = {}

if 'theme_settings' not in st.session_state:
    st.session_state.theme_settings = {
        'background_color': '#0e1117',
        'text_color': '#ffffff',
        'background_image': None
    }

def _ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def _read_json(file_path):
    """Read JSON data from file"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error reading {file_path}: {e}")
    return None

def _write_json(file_path, data):
    """Write JSON data to file"""
    try:
        _ensure_data_dir()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        st.error(f"Error writing {file_path}: {e}")

def load_client_data():
    """Load data from local files"""
    # Load log entries
    logs = _read_json(LOGS_FILE)
    if logs:
        st.session_state.log_entries = logs
    
    # Load custom fields
    custom_fields = _read_json(CUSTOM_FIELDS_FILE)
    if custom_fields:
        st.session_state.custom_fields = custom_fields
    
    # Load field order
    field_order = _read_json(FIELD_ORDER_FILE)
    if field_order:
        st.session_state.field_order = field_order
    
    # Load field toggles
    field_toggles = _read_json(FIELD_TOGGLES_FILE)
    if field_toggles:
        st.session_state.field_toggles = field_toggles
    
    # Load theme settings
    theme_settings = _read_json(THEME_FILE)
    if theme_settings:
        st.session_state.theme_settings = theme_settings

def save_client_data():
    """Save data to local files"""
    _write_json(LOGS_FILE, st.session_state.log_entries)
    _write_json(CUSTOM_FIELDS_FILE, st.session_state.custom_fields)
    _write_json(FIELD_ORDER_FILE, st.session_state.field_order)
    _write_json(FIELD_TOGGLES_FILE, st.session_state.field_toggles)
    _write_json(THEME_FILE, st.session_state.theme_settings)

def clear_form_inputs():
    """Clear all form input values from session state"""
    keys_to_remove = [key for key in st.session_state.keys() if key.startswith('input_')]
    for key in keys_to_remove:
        del st.session_state[key]

def clear_all_data():
    """Clear all data and files"""
    st.session_state.log_entries = []
    st.session_state.custom_fields = {}
    st.session_state.field_order = get_default_field_order()
    st.session_state.field_toggles = {}
    st.session_state.theme_settings = {
        'background_color': '#0e1117',
        'text_color': '#ffffff',
        'background_image': None
    }
    
    # Delete files
    for file_path in [LOGS_FILE, CUSTOM_FIELDS_FILE, FIELD_ORDER_FILE, FIELD_TOGGLES_FILE, THEME_FILE]:
        if os.path.exists(file_path):
            os.remove(file_path)

def format_number(value):
    """Format large numbers with appropriate suffixes"""
    if value is None or value == '':
        return 'N/A'
    
    try:
        value = float(value)
        if value >= 1e9:
            return f"${value/1e9:.1f}B"
        elif value >= 1e6:
            return f"${value/1e6:.1f}M"
        elif value >= 1e3:
            return f"${value/1e3:.1f}K"
        else:
            return f"${value:.0f}"
    except:
        return str(value)

def get_link_type(url):
    """Determine the type of link for styling"""
    if not url or url == '':
        return 'none'
    
    url_lower = url.lower()
    if 'padre' in url_lower:
        return 'padre'
    elif 'axiom' in url_lower:
        return 'axiom'
    elif 'dexscreener' in url_lower:
        return 'dexscreener'
    elif 'coingecko' in url_lower:
        return 'coingecko'
    elif 'coinmarketcap' in url_lower:
        return 'coinmarketcap'
    else:
        return 'other'

def create_clickable_link(url, text="🔗 Open"):
    """Create a clickable link with appropriate styling"""
    if not url or url == '':
        return text
    
    link_type = get_link_type(url)
    if link_type == 'padre':
        return f'<a href="{url}" target="_blank" style="color: #ff6b6b; text-decoration: none;">🔗 Padre</a>'
    elif link_type == 'axiom':
        return f'<a href="{url}" target="_blank" style="color: #4ecdc4; text-decoration: none;">🔗 Axiom</a>'
    elif link_type == 'dexscreener':
        return f'<a href="{url}" target="_blank" style="color: #45b7d1; text-decoration: none;">🔗 DexScreener</a>'
    elif link_type == 'coingecko':
        return f'<a href="{url}" target="_blank" style="color: #96ceb4; text-decoration: none;">🔗 CoinGecko</a>'
    elif link_type == 'coinmarketcap':
        return f'<a href="{url}" target="_blank" style="color: #feca57; text-decoration: none;">🔗 CoinMarketCap</a>'
    else:
        return f'<a href="{url}" target="_blank" style="color: #a55eea; text-decoration: none;">🔗 Link</a>'

def apply_theme():
    """Apply custom theme styling"""
    theme = st.session_state.theme_settings
    
    # Base styles
    styles = f"""
    <style>
    .stApp {{
        background-color: {theme.get('background_color', '#0e1117')};
        color: {theme.get('text_color', '#ffffff')};
    }}
    
    .main .block-container {{
        background-color: {theme.get('background_color', '#0e1117')};
        color: {theme.get('text_color', '#ffffff')};
    }}
    
    .stSelectbox > div > div {{
        background-color: {theme.get('background_color', '#0e1117')};
        color: {theme.get('text_color', '#ffffff')};
    }}
    
    .stTextInput > div > div > input {{
        background-color: {theme.get('background_color', '#0e1117')};
        color: {theme.get('text_color', '#ffffff')};
        border: 1px solid #555;
    }}
    
    .stTextArea > div > div > textarea {{
        background-color: {theme.get('background_color', '#0e1117')};
        color: {theme.get('text_color', '#ffffff')};
        border: 1px solid #555;
    }}
    
    .stNumberInput > div > div > input {{
        background-color: {theme.get('background_color', '#0e1117')};
        color: {theme.get('text_color', '#ffffff')};
        border: 1px solid #555;
    }}
    
    .stSlider > div > div > div {{
        background-color: {theme.get('background_color', '#0e1117')};
    }}
    
    .stButton > button {{
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }}
    
    .stButton > button:hover {{
        background-color: #0f5a8a;
    }}
    
    .stMetric {{
        background-color: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}
    
    .stExpander {{
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }}
    
    .stDataFrame {{
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }}
    """
    
    # Add background image if set
    if theme.get('background_image'):
        styles += f"""
        .stApp {{
            background-image: url('{theme['background_image']}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        .main .block-container {{
            background-color: rgba(14, 17, 23, 0.9);
            backdrop-filter: blur(10px);
        }}
        """
    
    st.markdown(styles, unsafe_allow_html=True)

def create_input_widget(field_key, config):
    """Create an input widget based on field configuration"""
    widget_type = config.get('type', 'text_input')
    label = config.get('label', field_key)
    help_text = config.get('help', '')
    placeholder = config.get('placeholder', '')
    
    # Get current value from session state
    session_key = f"input_{field_key}"
    current_value = st.session_state.get(session_key, config.get('value', config.get('default')))
    
    if widget_type == 'text_input':
        return st.text_input(
            label,
            value=current_value,
            help=help_text,
            placeholder=placeholder,
            key=session_key
        )
    elif widget_type == 'number_input':
        return st.number_input(
            label,
            value=current_value,
            help=help_text,
            placeholder=placeholder,
            key=session_key
        )
    elif widget_type == 'selectbox':
        options = config.get('options', [])
        return st.selectbox(
            label,
            options=options,
            index=options.index(current_value) if current_value in options else 0,
            help=help_text,
            key=session_key
        )
    elif widget_type == 'slider':
        return st.slider(
            label,
            min_value=config.get('min_value', 0),
            max_value=config.get('max_value', 100),
            value=current_value if current_value is not None else config.get('value', 50),
            step=config.get('step', 1),
            help=help_text,
            key=session_key
        )
    elif widget_type == 'text_area':
        return st.text_area(
            label,
            value=current_value,
            help=help_text,
            placeholder=placeholder,
            key=session_key
        )
    elif widget_type == 'date_input':
        return st.date_input(
            label,
            value=current_value if current_value else config.get('default'),
            help=help_text,
            key=session_key
        )
    else:
        return st.text_input(
            label,
            value=current_value,
            help=help_text,
            placeholder=placeholder,
            key=session_key
        )

def add_custom_field(field_name, field_type, options=""):
    """Add a new custom field"""
    try:
        # Parse options for selectbox and slider
        parsed_options = None
        if field_type == 'selectbox' and options:
            parsed_options = [opt.strip() for opt in options.split(',')]
        elif field_type == 'slider' and options:
            try:
                min_val, max_val, step = [float(x.strip()) for x in options.split(',')]
                parsed_options = {'min_value': min_val, 'max_value': max_val, 'step': step}
            except:
                parsed_options = {'min_value': 0, 'max_value': 100, 'step': 1}
        
        # Create field configuration
        field_config = {
            'label': field_name,
            'type': field_type,
            'help': f'Custom field: {field_name}'
        }
        
        if parsed_options:
            if field_type == 'selectbox':
                field_config['options'] = parsed_options
            elif field_type == 'slider':
                field_config.update(parsed_options)
        
        # Add to custom fields
        st.session_state.custom_fields[field_name] = field_config
        
        # Add to field order
        if field_name not in st.session_state.field_order['custom']:
            st.session_state.field_order['custom'].append(field_name)
        
        # Initialize field toggle
        st.session_state.field_toggles[field_name] = True
        
        # Save data
        save_client_data()
        
    except Exception as e:
        st.error(f"Error adding custom field: {e}")

def delete_custom_field(field_name):
    """Delete a custom field"""
    try:
        # Remove from custom fields
        if field_name in st.session_state.custom_fields:
            del st.session_state.custom_fields[field_name]
        
        # Remove from field order
        if field_name in st.session_state.field_order['custom']:
            st.session_state.field_order['custom'].remove(field_name)
        
        # Remove field toggle
        if field_name in st.session_state.field_toggles:
            del st.session_state.field_toggles[field_name]
        
        # Save data
        save_client_data()
        
    except Exception as e:
        st.error(f"Error deleting custom field: {e}")

# Apply theme
apply_theme()

# Load data on startup
load_client_data()

# Main title and stats row
col1, col2 = st.columns([3, 2])

with col1:
    st.title("🪵 Logging Journal")
    st.markdown("""
    Track and analyze potential investments with this comprehensive logging tool. 
    Toggle fields on/off to customize your logging experience and focus on what matters most to you.
    **Your data is now saved client-side and will persist between sessions!**
    """)
    
    # Add some spacing to align with the stats
    st.markdown("<br>", unsafe_allow_html=True)

with col2:
    # Add spacing to align with form content
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # Quick Stats (no box, same position)
    if st.session_state.log_entries:
        st.markdown("### 📊 Quick Stats")
        
        # Calculate stats
        total_entries = len(st.session_state.log_entries)
        winning_trades = sum(1 for entry in st.session_state.log_entries if entry.get('trade_result') == 'Win')
        losing_trades = sum(1 for entry in st.session_state.log_entries if entry.get('trade_result') == 'Loss')
        win_rate = (winning_trades / (winning_trades + losing_trades) * 100) if (winning_trades + losing_trades) > 0 else 0
        
        # Clean stats display
        st.markdown(f"**Total Entries:** {total_entries}")
        st.markdown(f"**Winning Trades:** {winning_trades}")
        st.markdown(f"**Losing Trades:** {losing_trades}")
        st.markdown(f"**Win Rate:** {win_rate:.1f}%")
        
        st.markdown("---")  # Divider
        
        # Recent entries in scrollable box
        st.markdown("### 📋 Recent Entries")
        
        # Create scrollable container for recent entries
        st.markdown("""
        <div style="
            max-height: 300px;
            overflow-y: auto;
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        ">
        """, unsafe_allow_html=True)
        
        # Show all entries in scrollable box
        recent_entries = st.session_state.log_entries[::-1]  # Show newest first
        
        for i, entry in enumerate(recent_entries):
            # Create columns for entry content and trash button
            entry_col, trash_col = st.columns([4, 1])
            
            with entry_col:
                # Show abbreviated market cap
                market_cap = entry.get('market_cap', 0)
                if market_cap:
                    if market_cap >= 1e9:
                        mc_display = f"${market_cap/1e9:.1f}B"
                    elif market_cap >= 1e6:
                        mc_display = f"${market_cap/1e6:.1f}M"
                    elif market_cap >= 1e3:
                        mc_display = f"${market_cap/1e3:.1f}K"
                    else:
                        mc_display = f"${market_cap:.0f}"
                else:
                    mc_display = "N/A"
                
                # Format date without year
                date_str = str(entry.get('date_logged', 'No date'))
                if date_str != 'No date' and len(date_str) > 4:
                    # Remove year (last 4 characters if it's a date)
                    short_date = date_str[:-5] if date_str.endswith('-2024') or date_str.endswith('-2025') else date_str
                else:
                    short_date = date_str
                
                # Compact entry display on same line with hover effect
                st.markdown(f"""
                <div style="
                    padding: 8px;
                    margin: 2px 0;
                    border-radius: 5px;
                    transition: background-color 0.2s;
                " onmouseover="this.style.backgroundColor='rgba(255,255,255,0.1)'" onmouseout="this.style.backgroundColor='transparent'">
                    🪙 <strong>{entry.get('coin_symbol', 'Unknown')}</strong> - {mc_display} • {short_date}
                </div>
                """, unsafe_allow_html=True)
            
            with trash_col:
                # Trash button with no outline and hover effect
                if st.button("🗑️", key=f"delete_entry_{i}", help="Delete this entry", 
                           use_container_width=True, 
                           type="secondary"):
                    # Find the entry in the full list and remove it
                    entry_timestamp = entry.get('timestamp')
                    if entry_timestamp:
                        st.session_state.log_entries = [e for e in st.session_state.log_entries if e.get('timestamp') != entry_timestamp]
                        save_client_data()
                        st.success(f"Deleted entry for {entry.get('coin_symbol', 'Unknown')}")
                        st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("### 📊 Quick Stats")
        st.info("No entries yet")

# Field selection in sidebar
with st.sidebar:
    st.header("🔧 Field Management")
    
    # Built-in fields
    st.subheader("📋 Built-in Fields")
    for field_key in st.session_state.field_order['built_in']:
        if field_key in FIELD_CONFIGS:
            config = FIELD_CONFIGS[field_key]
            st.session_state.field_toggles[field_key] = st.checkbox(
                config['label'],
                value=st.session_state.field_toggles.get(field_key, True),
                key=f"toggle_{field_key}"
            )
    
    # Custom fields
    if st.session_state.custom_fields:
        st.subheader("🔧 Custom Fields")
        for field_name in st.session_state.field_order['custom']:
            if field_name in st.session_state.custom_fields:
                config = st.session_state.custom_fields[field_name]
                st.session_state.field_toggles[field_name] = st.checkbox(
                    config['label'],
                    value=st.session_state.field_toggles.get(field_name, True),
                    key=f"toggle_{field_name}"
                )

# Get selected fields
selected_fields = {k: v for k, v in st.session_state.field_toggles.items() if v}

# Main form - in left column
with col1:
    with st.form("entry_form"):
        entry_data = {}
        
        # Add built-in fields in custom order (only if selected)
        for field_key in st.session_state.field_order['built_in']:
            if field_key in selected_fields and selected_fields[field_key]:
                if field_key in FIELD_CONFIGS:
                    config = FIELD_CONFIGS[field_key]
                    entry_data[field_key] = create_input_widget(field_key, config)
        
        # Add custom fields in custom order (only if selected)
        for field_key in st.session_state.field_order['custom']:
            if field_key in selected_fields and selected_fields[field_key]:
                if field_key in st.session_state.custom_fields:
                    config = st.session_state.custom_fields[field_key]
                    entry_data[field_key] = create_input_widget(field_key, config)
        
        # Form buttons
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        
        with btn_col1:
            if st.form_submit_button("📝 Add Entry", type="primary", use_container_width=True):
                # Validate required fields
                if not entry_data.get('coin_symbol'):
                    st.error("❌ Coin symbol is required!")
                else:
                    # Add timestamp
                    entry_data['timestamp'] = datetime.now()
                    
                    # Add to log entries
                    st.session_state.log_entries.append(entry_data)
                    
                    # Save data
                    save_client_data()
                    
                    # Success message
                    st.success(f"✅ Added {entry_data.get('coin_symbol', 'Unknown')} to your journal!")
                    
                    # Clear form by rerunning
                    st.rerun()
        
        with btn_col2:
            if st.form_submit_button("🗑️ Clear Form", use_container_width=True):
                clear_form_inputs()
                st.rerun()
        
        with btn_col3:
            if st.form_submit_button("💾 Save Settings", use_container_width=True):
                save_client_data()
                st.success("✅ Settings saved!")



# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Theme settings
    st.subheader("🎨 Theme")
    
    # Background upload
    uploaded_bg = st.file_uploader("Upload Background", type=['png', 'jpg', 'jpeg'])
    if uploaded_bg:
        # Convert to base64
        bg_bytes = uploaded_bg.read()
        bg_b64 = base64.b64encode(bg_bytes).decode()
        st.session_state.theme_settings['background_image'] = f"data:image/{uploaded_bg.type.split('/')[-1]};base64,{bg_b64}"
        save_client_data()
        st.success("Background updated!")
    
    # Color picker
    bg_color = st.color_picker("Background Color", value=st.session_state.theme_settings.get('background_color', '#0e1117'))
    if bg_color != st.session_state.theme_settings.get('background_color'):
        st.session_state.theme_settings['background_color'] = bg_color
        save_client_data()
    
    text_color = st.color_picker("Text Color", value=st.session_state.theme_settings.get('text_color', '#ffffff'))
    if text_color != st.session_state.theme_settings.get('text_color'):
        st.session_state.theme_settings['text_color'] = text_color
        save_client_data()
    
    # Custom fields management
    st.subheader("🔧 Custom Fields")
    
    # Add new custom field
    with st.form("add_custom_field"):
        new_field_name = st.text_input("Field Name", placeholder="e.g., Risk Level")
        new_field_type = st.selectbox("Field Type", ["text_input", "number_input", "selectbox", "slider"])
        new_field_options = ""
        if new_field_type == "selectbox":
            new_field_options = st.text_input("Options (comma-separated)", placeholder="High, Medium, Low")
        elif new_field_type == "slider":
            new_field_options = st.text_input("Min, Max, Step (comma-separated)", placeholder="0, 100, 1")
        
        if st.form_submit_button("Add Field"):
            if new_field_name and new_field_name not in FIELD_CONFIGS:
                add_custom_field(new_field_name, new_field_type, new_field_options)
                st.success(f"Added field: {new_field_name}")
                st.rerun()
            elif new_field_name in FIELD_CONFIGS:
                st.error("Field already exists!")
    
    # Field management
    if st.session_state.custom_fields:
        st.write("**Manage Fields:**")
        for field_name in list(st.session_state.custom_fields.keys()):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {field_name}")
            with col2:
                if st.button("🗑️", key=f"del_{field_name}"):
                    delete_custom_field(field_name)
                    st.rerun()
    
    # Clear all data
    st.subheader("🗑️ Data Management")
    if st.button("Clear All Data", type="secondary"):
        clear_all_data()
        st.rerun()

# Full-width Interactive Data Table
if st.session_state.log_entries:
    st.subheader("📊 Interactive Data Table")
    
    # Create DataFrame
    df = pd.DataFrame(st.session_state.log_entries)
    
    if not df.empty:
        # Add trade result column for editing
        if 'trade_result' not in df.columns:
            df['trade_result'] = 'Pending'
        
        # Create column mapping to clean names
        column_mapping = {
            'coin_symbol': 'Coin',
            'coin_link': 'Link',
            'date_logged': 'Date',
            'market_cap': 'Market Cap',
            'trading_volume': 'Volume',
            'trading_volume_timeframe': 'Timeframe',
            'conviction_level': 'Conviction',
            'notes': 'Notes',
            'trade_result': 'Result',
            'timestamp': 'Added'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Create editable columns
        edited_df = st.data_editor(
            df,
            column_config={
                "Result": st.column_config.SelectboxColumn(
                    "Result",
                    help="Select the trade result",
                    options=["Pending", "Win", "Loss"],
                    required=True,
                ),
                "Link": st.column_config.LinkColumn(
                    "Link",
                    help="Click to open link",
                    display_text="🔗 Open"
                )
            },
            use_container_width=True,
            num_rows="dynamic",
            key="data_editor"
        )
        
        # Update session state with edited data
        if not edited_df.equals(df):
            # Convert back to original column names
            reverse_mapping = {v: k for k, v in column_mapping.items()}
            edited_df = edited_df.rename(columns=reverse_mapping)
            st.session_state.log_entries = edited_df.to_dict('records')
            save_client_data()
            st.rerun()
