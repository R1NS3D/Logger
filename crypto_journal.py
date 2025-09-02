import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="Crypto Logging Journal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_default_field_order():
    """Get the default field order"""
    return {
        'built_in': ['coin_symbol', 'coin_link', 'date_logged', 'market_cap', 'trading_volume', 
                     'trading_volume_timeframe', 'established_status', 'fib_levels', 'conviction_level', 
                     'risk_factors', 'sentiment_community', 'entry_strategy', 'target_exit_strategy', 
                     'notes_updates', 'trade_result'],
        'custom': []
    }

# Initialize session state for client-side storage
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
        'background_color': '#1a1a1a',
        'text_color': '#ffffff',
        'accent_color': '#00d4aa',
        'custom_background': None
    }

def load_client_data():
    """Load data from client-side storage (localStorage equivalent in Streamlit)"""
    # In Streamlit, we use session_state which persists during the session
    # For true persistence, we'd need to implement a database or file system
    # For now, we'll use session_state which is the best we can do in Streamlit
    
    # Load field toggles with defaults
    for field_key in FIELD_CONFIGS.keys():
        if field_key not in st.session_state.field_toggles:
            st.session_state.field_toggles[field_key] = True
    
    # Load custom field toggles
    for field_key in st.session_state.custom_fields.keys():
        if field_key not in st.session_state.field_toggles:
            st.session_state.field_toggles[field_key] = True
    
    # Ensure all custom fields have proper configurations
    for field_key, config in st.session_state.custom_fields.items():
        if 'type' not in config:
            config['type'] = 'text_input'  # Default fallback
        if config['type'] == 'slider' and 'min_value' not in config:
            config['min_value'] = 0
            config['max_value'] = 100
            config['value'] = 50
        elif config['type'] == 'selectbox' and 'options' not in config:
            config['options'] = ['Option 1', 'Option 2', 'Option 3']
            config['index'] = 0

def save_client_data():
    """Save data to client-side storage"""
    # In Streamlit, session_state automatically persists during the session
    # This is the closest we can get to client-side storage
    pass

def clear_all_data():
    """Clear all saved data"""
    st.session_state.log_entries = []
    st.session_state.custom_fields = {}
    st.session_state.field_order = get_default_field_order()
    st.session_state.field_toggles = {}
    st.session_state.theme_settings = {
        'background_color': '#1a1a1a',
        'text_color': '#ffffff',
        'accent_color': '#00d4aa',
        'custom_background': None
    }

def move_field_up(field_key, field_type):
    """Move a field up in the order"""
    order_list = st.session_state.field_order[field_type]
    if field_key in order_list:
        current_index = order_list.index(field_key)
        if current_index > 0:
            order_list[current_index], order_list[current_index - 1] = order_list[current_index - 1], order_list[current_index]
            save_client_data()

def move_field_down(field_key, field_type):
    """Move a field down in the order"""
    order_list = st.session_state.field_order[field_type]
    if field_key in order_list:
        current_index = order_list.index(field_key)
        if current_index < len(order_list) - 1:
            order_list[current_index], order_list[current_index + 1] = order_list[current_index + 1], order_list[current_index]
            save_client_data()

def add_field_to_order(field_key, field_type):
    """Add a new field to the order"""
    if field_type == 'custom' and field_key not in st.session_state.field_order['custom']:
        st.session_state.field_order['custom'].append(field_key)
        st.write(f"Debug: Added {field_key} to {field_type} order")
        st.write(f"Debug: Field order now: {st.session_state.field_order}")
        save_client_data()

def remove_field_from_order(field_key, field_type):
    """Remove a field from the order"""
    if field_key in st.session_state.field_order[field_type]:
        st.session_state.field_order[field_type].remove(field_key)
        save_client_data()

def update_existing_entries_with_new_fields():
    """Update existing entries to include any new fields that were added"""
    if not st.session_state.log_entries:
        return
    
    # Get all current field keys (built-in + custom)
    all_field_keys = set(FIELD_CONFIGS.keys())
    all_field_keys.update(st.session_state.custom_fields.keys())
    
    # Update each entry to include missing fields
    updated_count = 0
    for entry in st.session_state.log_entries:
        for field_key in all_field_keys:
            if field_key not in entry:
                # Add missing field with appropriate default value
                if field_key in FIELD_CONFIGS:
                    config = FIELD_CONFIGS[field_key]
                    if config['type'] == 'selectbox':
                        entry[field_key] = config['options'][0] if config['options'] else ''
                    elif config['type'] == 'slider':
                        entry[field_key] = config['value']
                    elif config['type'] == 'date_input':
                        entry[field_key] = config.get('default', datetime.now().date())
                    else:
                        entry[field_key] = ''
                elif field_key in st.session_state.custom_fields:
                    config = st.session_state.custom_fields[field_key]
                    if config['type'] == 'selectbox':
                        entry[field_key] = config['options'][0] if config['options'] else ''
                    elif config['type'] == 'slider':
                        entry[field_key] = config['value']
                    else:
                        entry[field_key] = ''
                updated_count += 1
    
    if updated_count > 0:
        save_client_data()
        st.info(f"🔄 Updated {updated_count} entries with new fields")

def format_number(value):
    """Format large numbers with abbreviations (K, M, B)"""
    if value is None or value == 0:
        return "0"
    
    try:
        value = float(value)
        if value >= 1_000_000_000:
            return f"{value/1_000_000_000:.1f}B"
        elif value >= 1_000_000:
            return f"{value/1_000_000:.1f}M"
        elif value >= 1_000:
            return f"{value/1_000:.1f}K"
        else:
            return f"{value:.0f}"
    except (ValueError, TypeError):
        return str(value)

def get_link_type(link):
    """Determine the type of link and return appropriate display text"""
    if not link or not isinstance(link, str):
        return None, None
    
    link_lower = link.lower()
    if 'padre' in link_lower:
        return 'Padre', 'padre'
    elif 'axiom' in link_lower:
        return 'Axiom', 'axiom'
    elif 'dexscreener' in link_lower:
        return 'DexScreener', 'dexscreener'
    elif 'coingecko' in link_lower:
        return 'CoinGecko', 'coingecko'
    elif 'coinmarketcap' in link_lower:
        return 'CoinMarketCap', 'coinmarketcap'
    else:
        return 'Link', 'generic'

def create_clickable_link(link, text):
    """Create a clickable link with appropriate styling"""
    link_type, type_class = get_link_type(link)
    if not link_type:
        return text
    
    # Create styled link based on type
    if type_class == 'padre':
        return f'<a href="{link}" target="_blank" style="color: #FF6B35; text-decoration: none; font-weight: bold;">{text} 🔗</a>'
    elif type_class == 'axiom':
        return f'<a href="{link}" target="_blank" style="color: #6366F1; text-decoration: none; font-weight: bold;">{text} 🔗</a>'
    elif type_class == 'dexscreener':
        return f'<a href="{link}" target="_blank" style="color: #10B981; text-decoration: none; font-weight: bold;">{text} 📊</a>'
    elif type_class == 'coingecko':
        return f'<a href="{link}" target="_blank" style="color: #F59E0B; text-decoration: none; font-weight: bold;">{text} 🦎</a>'
    elif type_class == 'coinmarketcap':
        return f'<a href="{link}" target="_blank" style="color: #EF4444; text-decoration: none; font-weight: bold;">{text} 📈</a>'
    else:
        return f'<a href="{link}" target="_blank" style="color: #6B7280; text-decoration: none;">{text} 🔗</a>'

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
        'help': 'Select the timeframe for trading volume',
        'options': ['5m', '1h', '24h'],
        'index': 0
    },
    'established_status': {
        'label': 'Established Status',
        'type': 'selectbox',
        'help': 'How established is this cryptocurrency in the market',
        'options': ['New', 'Emerging', 'Established']
    },
    'fib_levels': {
        'label': 'Fib Levels',
        'type': 'text_input',
        'help': 'Fibonacci retracement levels (e.g., 0.618 retracement)',
        'placeholder': '0.618 retracement'
    },
    'conviction_level': {
        'label': 'Conviction Level',
        'type': 'slider',
        'help': 'Your conviction level for this investment (1-10)',
        'min_value': 1,
        'max_value': 10,
        'value': 5
    },
    'risk_factors': {
        'label': 'Risk Factors',
        'type': 'text_area',
        'help': 'Potential risks and concerns',
        'placeholder': 'Regulatory uncertainty, competition, market volatility...'
    },
    'sentiment_community': {
        'label': 'Sentiment/Community',
        'type': 'text_input',
        'help': 'Community sentiment and social media buzz',
        'placeholder': 'Bullish on Twitter, active Discord community'
    },
    'entry_strategy': {
        'label': 'Entry Strategy',
        'type': 'text_area',
        'help': 'Your planned entry strategy and timing',
        'placeholder': 'DCA over 3 months, buy on dips below $45k...'
    },
    'target_exit_strategy': {
        'label': 'Target/Exit Strategy',
        'type': 'text_area',
        'help': 'Price targets and exit strategy',
        'placeholder': 'Take profit at $60k, stop loss at $35k...'
    },
    'notes_updates': {
        'label': 'Notes/Updates',
        'type': 'text_area',
        'help': 'Additional notes and updates',
        'placeholder': 'Any additional thoughts or observations...'
    },
    'trade_result': {
        'label': 'Trade Result',
        'type': 'selectbox',
        'help': 'Was this a winning or losing trade?',
        'options': ['Pending', 'Win', 'Loss']
    }
}

# Available field types for custom fields
FIELD_TYPES = {
    'text_input': 'Text Input',
    'number_input': 'Number Input',
    'text_area': 'Text Area',
    'selectbox': 'Dropdown (Select Box)',
    'slider': 'Slider',
    'date_input': 'Date Input',
    'checkbox': 'Checkbox'
}

# Load data on app startup
if 'data_loaded' not in st.session_state:
    load_client_data()
    st.session_state.data_loaded = True

def create_input_widget(field_key, config):
    """Create the appropriate input widget based on field configuration"""
    if config['type'] == 'text_input':
        return st.text_input(
            config['label'],
            help=config['help'],
            placeholder=config.get('placeholder', ''),
            key=f"input_{field_key}"
        )
    
    elif config['type'] == 'date_input':
        return st.date_input(
            config['label'],
            value=config.get('default', datetime.now().date()),
            help=config['help'],
            key=f"input_{field_key}"
        )
    
    elif config['type'] == 'number_input':
        return st.number_input(
            config['label'],
            value=config.get('value'),
            help=config['help'],
            placeholder=config.get('placeholder', ''),
            key=f"input_{field_key}"
        )
    
    elif config['type'] == 'selectbox':
        return st.selectbox(
            config['label'],
            options=config['options'],
            index=config.get('index', 0),
            help=config['help'],
            key=f"input_{field_key}"
        )
    
    elif config['type'] == 'slider':
        return st.slider(
            config['label'],
            min_value=config['min_value'],
            max_value=config['max_value'],
            value=config['value'],
            help=config['help'],
            key=f"input_{field_key}"
        )
    
    elif config['type'] == 'text_area':
        return st.text_area(
            config['label'],
            help=config['help'],
            placeholder=config.get('placeholder', ''),
            height=100,
            key=f"input_{field_key}"
        )
    
    elif config['type'] == 'checkbox':
        return st.checkbox(
            config['label'],
            help=config['help'],
            key=f"input_{field_key}"
        )

def add_custom_field():
    """Add a new custom field to the session state"""
    if st.session_state.new_field_name and st.session_state.new_field_type:
        field_key = f"custom_{st.session_state.new_field_name.lower().replace(' ', '_')}"
        
        # Create basic config based on field type
        config = {
            'label': st.session_state.new_field_name,
            'type': st.session_state.new_field_type,
            'help': st.session_state.new_field_help or f"Custom field: {st.session_state.new_field_name}"
        }
        
        # Add type-specific configurations
        if st.session_state.new_field_type == 'number_input':
            config['placeholder'] = '0'
            config['value'] = 0
        elif st.session_state.new_field_type == 'selectbox':
            config['options'] = ['Option 1', 'Option 2', 'Option 3']
            config['index'] = 0
        elif st.session_state.new_field_type == 'slider':
            config['min_value'] = 0
            config['max_value'] = 100
            config['value'] = 50
        elif st.session_state.new_field_type == 'text_input':
            config['placeholder'] = f'Enter {st.session_state.new_field_name.lower()}'
        elif st.session_state.new_field_type == 'text_area':
            config['placeholder'] = f'Enter {st.session_state.new_field_name.lower()}...'
        elif st.session_state.new_field_type == 'date_input':
            config['default'] = datetime.now().date()
        elif st.session_state.new_field_type == 'checkbox':
            config['value'] = False
        
        # Add the custom field to session state
        st.session_state.custom_fields[field_key] = config
        
        # Add to field order
        add_field_to_order(field_key, 'custom')
        
        # Initialize field toggle for the new custom field
        st.session_state.field_toggles[field_key] = True
        
        # Debug: Print current state
        st.write(f"Debug: Added field {field_key} with config {config}")
        st.write(f"Debug: Custom fields now: {list(st.session_state.custom_fields.keys())}")
        st.write(f"Debug: Field order custom: {st.session_state.field_order['custom']}")
        
        # Save the data
        save_client_data()
        
        # Clear the form
        st.session_state.new_field_name = ""
        st.session_state.new_field_help = ""
        st.session_state.new_field_type = list(FIELD_TYPES.keys())[0]  # Reset to first option

def delete_custom_field(field_key):
    """Delete a custom field from the session state"""
    if field_key in st.session_state.custom_fields:
        del st.session_state.custom_fields[field_key]
        remove_field_from_order(field_key, 'custom')
        save_client_data()

def apply_theme():
    """Apply the current theme settings"""
    theme = st.session_state.theme_settings
    
    # Apply custom background if set
    if theme.get('custom_background'):
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{theme['custom_background']});
            background-size: cover;
            background-attachment: fixed;
        }}
        </style>
        """, unsafe_allow_html=True)
    
    # Apply color theme with enhanced dark mode styling
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {theme['background_color']} !important;
        color: {theme['text_color']} !important;
    }}
    
    /* Main content area */
    .main .block-container {{
        background-color: {theme['background_color']} !important;
        color: {theme['text_color']} !important;
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background-color: {theme['background_color']} !important;
        color: {theme['text_color']} !important;
    }}
    
    /* Headers and text */
    h1, h2, h3, h4, h5, h6 {{
        color: {theme['text_color']} !important;
    }}
    
    /* Buttons */
    .stButton > button {{
        background-color: {theme['accent_color']} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
    }}
    
    .stButton > button:hover {{
        background-color: {theme['accent_color']}dd !important;
        transform: translateY(-1px) !important;
        transition: all 0.2s ease !important;
    }}
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {{
        background-color: #2a2a2a !important;
        color: {theme['text_color']} !important;
        border: 1px solid #444 !important;
        border-radius: 6px !important;
    }}
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > div:focus {{
        border-color: {theme['accent_color']} !important;
        box-shadow: 0 0 0 2px {theme['accent_color']}33 !important;
    }}
    
    /* Selectbox dropdown */
    .stSelectbox > div > div {{
        background-color: #2a2a2a !important;
        color: {theme['text_color']} !important;
    }}
    
    /* Date input */
    .stDateInput > div > div > input {{
        background-color: #2a2a2a !important;
        color: {theme['text_color']} !important;
        border: 1px solid #444 !important;
        border-radius: 6px !important;
    }}
    
    /* Slider */
    .stSlider > div > div > div > div {{
        background-color: #444 !important;
    }}
    
    .stSlider > div > div > div > div > div {{
        background-color: {theme['accent_color']} !important;
    }}
    
    /* Checkboxes */
    .stCheckbox > div > div > div {{
        background-color: #2a2a2a !important;
        border: 1px solid #444 !important;
        border-radius: 4px !important;
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        background-color: #2a2a2a !important;
        color: {theme['text_color']} !important;
        border: 1px solid #444 !important;
        border-radius: 6px !important;
    }}
    
    /* Metrics */
    .css-1wivap2 {{
        background-color: #2a2a2a !important;
        color: {theme['text_color']} !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
    }}
    
    /* Form containers */
    .stForm {{
        background-color: #2a2a2a !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        padding: 20px !important;
    }}
    
    /* Links */
    a {{
        color: {theme['accent_color']} !important;
    }}
    
    a:hover {{
        color: {theme['accent_color']}dd !important;
        text-decoration: underline !important;
    }}
    </style>
    """, unsafe_allow_html=True)

def main():
    # Apply theme
    apply_theme()
    
    # Header with settings gear
    col1, col2 = st.columns([6, 1])
    
    with col1:
        st.title("📊 Crypto Logging Journal")
        st.markdown("""
        Track and analyze potential cryptocurrency investments with this comprehensive logging tool. 
        Toggle fields on/off to customize your logging experience and focus on what matters most to you.
        **Your data is now saved client-side and will persist between sessions!**
        """)
    
    with col2:
        st.markdown("### ⚙️")
        if st.button("⚙️ Settings", key="settings_btn"):
            st.session_state.show_settings = not st.session_state.get('show_settings', False)
    
    # Settings panel
    if st.session_state.get('show_settings', False):
        with st.expander("⚙️ Theme & Customization Settings", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("🎨 Colors")
                
                # Quick theme presets
                col1a, col1b = st.columns(2)
                with col1a:
                    if st.button("🌙 Dark Mode", type="secondary"):
                        st.session_state.theme_settings['background_color'] = '#1a1a1a'
                        st.session_state.theme_settings['text_color'] = '#ffffff'
                        st.session_state.theme_settings['accent_color'] = '#00d4aa'
                        apply_theme()
                        st.success("✅ Dark mode applied!")
                
                with col1b:
                    if st.button("☀️ Light Mode", type="secondary"):
                        st.session_state.theme_settings['background_color'] = '#ffffff'
                        st.session_state.theme_settings['text_color'] = '#000000'
                        st.session_state.theme_settings['accent_color'] = '#1f77b4'
                        apply_theme()
                        st.success("✅ Light mode applied!")
                
                st.markdown("---")
                
                # Custom color pickers
                st.session_state.theme_settings['background_color'] = st.color_picker(
                    "Background Color", 
                    st.session_state.theme_settings['background_color']
                )
                st.session_state.theme_settings['text_color'] = st.color_picker(
                    "Text Color", 
                    st.session_state.theme_settings['text_color']
                )
                st.session_state.theme_settings['accent_color'] = st.color_picker(
                    "Accent Color", 
                    st.session_state.theme_settings['accent_color']
                )
            
            with col2:
                st.subheader("🖼️ Background")
                uploaded_file = st.file_uploader(
                    "Upload Custom Background", 
                    type=['png', 'jpg', 'jpeg'],
                    help="Upload an image to use as background"
                )
                if uploaded_file is not None:
                    # Convert to base64
                    image_bytes = uploaded_file.read()
                    image_base64 = base64.b64encode(image_bytes).decode()
                    st.session_state.theme_settings['custom_background'] = image_base64
                    st.success("✅ Background image uploaded!")
                
                if st.button("🗑️ Remove Background"):
                    st.session_state.theme_settings['custom_background'] = None
                    st.success("✅ Background image removed!")
            
            with col3:
                st.subheader("💾 Data Management")
                if st.button("🗑️ Clear All Data", type="secondary"):
                    clear_all_data()
                    st.success("✅ All data cleared!")
                    st.rerun()
                
                if st.button("📥 Export Data", type="secondary"):
                    # Export functionality would go here
                    st.info("Export functionality coming soon!")
            
            # Apply theme changes
            if st.button("🎨 Apply Theme Changes"):
                apply_theme()
                st.success("✅ Theme applied!")
    
    # Sidebar for field toggles and custom field management
    st.sidebar.header("📝 Field Selection")
    st.sidebar.markdown("Select which fields to include in your log entries:")
    
    # Field reordering section
    with st.sidebar.expander("🔄 Reorder Fields", expanded=False):
        st.markdown("**Built-in Fields:**")
        for i, field_key in enumerate(st.session_state.field_order['built_in']):
            if field_key in FIELD_CONFIGS:
                config = FIELD_CONFIGS[field_key]
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📋 {config['label']}")
                with col2:
                    if st.button("⬆️", key=f"up_built_{field_key}", help="Move up"):
                        move_field_up(field_key, 'built_in')
                        st.rerun()
                with col3:
                    if st.button("⬇️", key=f"down_built_{field_key}", help="Move down"):
                        move_field_down(field_key, 'built_in')
                        st.rerun()
        
        if st.session_state.field_order['custom']:
            st.markdown("**Custom Fields:**")
            for i, field_key in enumerate(st.session_state.field_order['custom']):
                if field_key in st.session_state.custom_fields:
                    config = st.session_state.custom_fields[field_key]
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"🔧 {config['label']}")
                    with col2:
                        if st.button("⬆️", key=f"up_custom_{field_key}", help="Move up"):
                            move_field_up(field_key, 'custom')
                            st.rerun()
                    with col3:
                        if st.button("⬇️", key=f"down_custom_{field_key}", help="Move down"):
                            move_field_down(field_key, 'custom')
                            st.rerun()
    
    # Create checkboxes for built-in field toggles (in custom order)
    selected_fields = {}
    for field_key in st.session_state.field_order['built_in']:
        if field_key in FIELD_CONFIGS:
            config = FIELD_CONFIGS[field_key]
            with st.sidebar.expander(config['label'], expanded=False):
                st.markdown(f"**{config['help']}**")
                selected_fields[field_key] = st.checkbox(
                    f"Enable {config['label']}",
                    value=st.session_state.field_toggles.get(field_key, True),
                    key=f"toggle_{field_key}"
                )
                st.session_state.field_toggles[field_key] = selected_fields[field_key]
    
    # Custom Fields Management Section
    st.sidebar.markdown("---")
    st.sidebar.header("🔧 Custom Fields")
    
    # Add new custom field form
    with st.sidebar.expander("➕ Add Custom Field", expanded=False):
        st.text_input("Field Name", key="new_field_name", placeholder="e.g., Team Size")
        st.selectbox("Field Type", options=list(FIELD_TYPES.keys()), format_func=lambda x: FIELD_TYPES[x], key="new_field_type")
        st.text_area("Help Text (Optional)", key="new_field_help", placeholder="Description of this field...")
        
        if st.button("Add Field", key="add_custom_field_btn"):
            if st.session_state.new_field_name and st.session_state.new_field_name.strip():
                try:
                    add_custom_field()
                    st.success(f"✅ Added custom field: {st.session_state.new_field_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error adding custom field: {str(e)}")
                    st.error("Please try again or check the field configuration.")
            else:
                st.error("❌ Field name is required!")
    
    # Display and manage existing custom fields (in custom order)
    if st.session_state.custom_fields:
        st.sidebar.markdown("**Your Custom Fields:**")
        st.sidebar.write(f"Debug: Found {len(st.session_state.custom_fields)} custom fields")
        st.sidebar.write(f"Debug: Field order custom: {st.session_state.field_order['custom']}")
        
        for field_key in st.session_state.field_order['custom']:
            if field_key in st.session_state.custom_fields:
                config = st.session_state.custom_fields[field_key]
                with st.sidebar.expander(config['label'], expanded=False):
                    st.markdown(f"**{config['help']}**")
                    st.markdown(f"*Type: {FIELD_TYPES[config['type']]}*")
                    
                    # Toggle for custom field
                    selected_fields[field_key] = st.checkbox(
                        f"Enable {config['label']}",
                        value=st.session_state.field_toggles.get(field_key, True),
                        key=f"toggle_{field_key}"
                    )
                    st.session_state.field_toggles[field_key] = selected_fields[field_key]
                    
                    # Delete button
                    if st.button(f"🗑️ Delete {config['label']}", key=f"delete_{field_key}"):
                        delete_custom_field(field_key)
                        st.success(f"✅ Deleted custom field: {config['label']}")
                        st.rerun()
        else:
            st.sidebar.write("No custom fields in field order")
    else:
        st.sidebar.write("No custom fields found")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📋 New Log Entry")
        
        # Check if any fields are selected
        if not any(selected_fields.values()):
            st.warning("⚠️ Please select at least one field to enable logging.")
            return
        
        # Create form for selected fields
        with st.form("log_entry_form"):
            st.markdown("### Entry Details")
            
            # Create input widgets for selected fields (in custom order)
            entry_data = {}
            
            # Add built-in fields in custom order (only if selected)
            for field_key in st.session_state.field_order['built_in']:
                if field_key in selected_fields and selected_fields[field_key]:
                    if field_key in FIELD_CONFIGS:
                        config = FIELD_CONFIGS[field_key]
                        value = create_input_widget(field_key, config)
                        entry_data[field_key] = value
            
            # Add custom fields in custom order (only if selected)
            for field_key in st.session_state.field_order['custom']:
                if field_key in selected_fields and selected_fields[field_key]:
                    if field_key in st.session_state.custom_fields:
                        config = st.session_state.custom_fields[field_key]
                        value = create_input_widget(field_key, config)
                        entry_data[field_key] = value
            
            # Submit button
            submitted = st.form_submit_button("📝 Log Entry", type="primary")
            
            if submitted:
                # Validate that at least coin symbol is provided
                if 'coin_symbol' in entry_data and entry_data['coin_symbol'].strip():
                    # Add timestamp for sorting
                    entry_data['timestamp'] = datetime.now().isoformat()
                    
                    # Add to session state
                    st.session_state.log_entries.append(entry_data)
                    
                    # Save data immediately
                    save_client_data()
                    
                    st.success(f"✅ Logged entry for {entry_data['coin_symbol']} (Saved automatically)")
                    
                    # Clear form inputs
                    for field_key in selected_fields.keys():
                        if f"input_{field_key}" in st.session_state:
                            del st.session_state[f"input_{field_key}"]
                else:
                    st.error("❌ Coin Symbol/Name is required!")
    
    with col2:
        st.header("📊 Quick Stats")
        
        if st.session_state.log_entries:
            total_entries = len(st.session_state.log_entries)
            unique_coins = len(set(entry.get('coin_symbol', 'Unknown') for entry in st.session_state.log_entries))
            
            # Calculate win rate
            completed_trades = [entry for entry in st.session_state.log_entries if entry.get('trade_result') in ['Win', 'Loss']]
            if completed_trades:
                wins = len([entry for entry in completed_trades if entry.get('trade_result') == 'Win'])
                win_rate = (wins / len(completed_trades)) * 100
            else:
                win_rate = 0
            
            st.metric("Total Entries", total_entries)
            st.metric("Unique Coins", unique_coins)
            st.metric("Win Rate", f"{win_rate:.1f}%")
            
            # Show breakdown of trade results
            pending_count = len([entry for entry in st.session_state.log_entries if entry.get('trade_result') == 'Pending'])
            win_count = len([entry for entry in st.session_state.log_entries if entry.get('trade_result') == 'Win'])
            loss_count = len([entry for entry in st.session_state.log_entries if entry.get('trade_result') == 'Loss'])
            
            st.markdown("**Trade Results Breakdown:**")
            st.write(f"⏳ Pending: {pending_count}")
            st.write(f"✅ Wins: {win_count}")
            st.write(f"❌ Losses: {loss_count}")
            
            # Recent entries preview with delete buttons and market cap
            st.subheader("Recent Entries")
            for i, entry in enumerate(st.session_state.log_entries[-3:]):
                coin = entry.get('coin_symbol', 'Unknown')
                date = entry.get('date_logged', 'No date')
                result = entry.get('trade_result', 'Pending')
                market_cap = entry.get('market_cap', '')
                
                # Format date
                if isinstance(date, str):
                    date_str = date
                else:
                    date_str = date.strftime('%Y-%m-%d') if date else 'No date'
                
                # Format market cap
                mc_display = ""
                if market_cap:
                    mc_display = f"MC: {format_number(market_cap)} | "
                
                # Add emoji for trade result
                if result == 'Win':
                    result_emoji = '✅'
                elif result == 'Loss':
                    result_emoji = '❌'
                else:
                    result_emoji = '⏳'
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {coin} - {mc_display}{date_str} {result_emoji}")
                with col2:
                    if st.button(f"🗑️", key=f"delete_recent_{i}", help=f"Delete {coin} entry"):
                        # Find the actual index in the full list
                        actual_index = st.session_state.log_entries.index(entry)
                        deleted_entry = st.session_state.log_entries.pop(actual_index)
                        save_client_data()
                        st.success(f"✅ Deleted {deleted_entry.get('coin_symbol', 'Unknown')} entry")
                        st.rerun()
        else:
            st.info("No entries logged yet. Start by creating your first entry!")
    
    # Display logged entries
    if st.session_state.log_entries:
        st.header("📈 Logged Entries")
        
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.log_entries)
        
        # Reorder columns to put important ones first
        important_cols = ['coin_symbol', 'date_logged', 'market_cap', 'conviction_level', 'trade_result']
        other_cols = [col for col in df.columns if col not in important_cols + ['timestamp']]
        
        # Reorder columns
        display_cols = [col for col in important_cols if col in df.columns] + other_cols
        df_display = df[display_cols].copy()
        
        # Clean up column names for display
        def clean_column_name(col_name):
            """Convert column names to clean, readable format"""
            # Remove underscores and capitalize
            clean_name = col_name.replace('_', ' ').title()
            
            # Special cases for better readability
            replacements = {
                'Coin Symbol': 'Coin',
                'Date Logged': 'Date',
                'Market Cap': 'Market Cap',
                'Trading Volume': 'Volume',
                'Trading Volume Timeframe': 'Volume Timeframe',
                'Established Status': 'Status',
                'Fib Levels': 'Fib Levels',
                'Conviction Level': 'Conviction',
                'Risk Factors': 'Risk Factors',
                'Sentiment Community': 'Sentiment',
                'Entry Strategy': 'Entry Strategy',
                'Target Exit Strategy': 'Exit Strategy',
                'Notes Updates': 'Notes',
                'Trade Result': 'Result',
                'Coin Link': 'Link'
            }
            
            return replacements.get(clean_name, clean_name)
        
        # Rename columns for cleaner display
        df_display.columns = [clean_column_name(col) for col in df_display.columns]
        
        # Format date columns
        if 'Date' in df_display.columns:
            df_display['Date'] = pd.to_datetime(df_display['Date']).dt.strftime('%Y-%m-%d')
        
        # Format market cap with abbreviations
        if 'Market Cap' in df_display.columns:
            df_display['Market Cap'] = df_display['Market Cap'].apply(format_number)
        
        # Format trading volume with abbreviations
        if 'Volume' in df_display.columns:
            df_display['Volume'] = df_display['Volume'].apply(format_number)
        
        # Create an interactive table with editable trade result dropdowns
        st.markdown("### Interactive Data Table")
        st.markdown("Edit trade results directly in the table below:")
        
        # Create a custom table with editable dropdowns
        for i, entry in enumerate(st.session_state.log_entries):
            # Create columns for the table row
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2, 1.5, 1.5, 1.5, 2, 1.5, 1])
            
            with col1:
                # Coin symbol (clickable if link exists)
                coin_symbol = entry.get('coin_symbol', 'Unknown')
                coin_link = entry.get('coin_link', '')
                if coin_link and coin_link.strip():
                    st.markdown(create_clickable_link(coin_link, coin_symbol), unsafe_allow_html=True)
                else:
                    st.write(f"**{coin_symbol}**")
            
            with col2:
                # Date
                date = entry.get('date_logged', 'No date')
                if isinstance(date, str):
                    st.write(date)
                else:
                    st.write(date.strftime('%Y-%m-%d') if date else 'No date')
            
            with col3:
                # Market cap
                market_cap = entry.get('market_cap', '')
                if market_cap:
                    st.write(f"MC: {format_number(market_cap)}")
                else:
                    st.write("MC: -")
            
            with col4:
                # Conviction level
                conviction = entry.get('conviction_level', '')
                if conviction:
                    st.write(f"Conv: {conviction}")
                else:
                    st.write("Conv: -")
            
            with col5:
                # Trade result dropdown
                new_result = st.selectbox(
                    "Trade Result",
                    options=['Pending', 'Win', 'Loss'],
                    index=['Pending', 'Win', 'Loss'].index(entry.get('trade_result', 'Pending')),
                    key=f"edit_result_{i}",
                    label_visibility="collapsed"
                )
                # Update the entry if result changed
                if new_result != entry.get('trade_result'):
                    entry['trade_result'] = new_result
                    save_client_data()
                    st.success(f"✅ Updated {entry.get('coin_symbol', 'Unknown')} to {new_result}")
            
            with col6:
                # Show current result with emoji
                current_result = entry.get('trade_result', 'Pending')
                if current_result == 'Win':
                    st.write('✅ Win')
                elif current_result == 'Loss':
                    st.write('❌ Loss')
                else:
                    st.write('⏳ Pending')
            
            with col7:
                # Delete button
                if st.button(f"🗑️", key=f"delete_inline_{i}", help=f"Delete {entry.get('coin_symbol', 'Unknown')} entry"):
                    deleted_entry = st.session_state.log_entries.pop(i)
                    save_client_data()
                    st.success(f"✅ Deleted {deleted_entry.get('coin_symbol', 'Unknown')} entry")
                    st.rerun()
        
        st.markdown("---")
        
        # Export functionality
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"crypto_journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📥 Export to JSON"):
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"crypto_journal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col3:
            if st.button("🗑️ Clear All Logs", type="secondary"):
                st.session_state.log_entries = []
                save_client_data()
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💡 <strong>Tips:</strong> Your data is now saved client-side and will persist between sessions! 
        Use the settings gear (⚙️) to customize themes and backgrounds. 
        Use the "Reorder Fields" section to arrange fields in your preferred order.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
