import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="Lumberjack",
    page_icon="🪵",
    layout="wide"
)

# Initialize session state
if 'log_entries' not in st.session_state:
    st.session_state.log_entries = []

def clear_form_inputs():
    """Clear all form input fields from session state"""
    keys_to_remove = []
    for key in st.session_state.keys():
        if key.startswith('input_'):
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        del st.session_state[key]

def move_field_up(field_key, field_type):
    """Move a field up in the order"""
    order_list = st.session_state.field_order[field_type]
    if field_key in order_list:
        current_index = order_list.index(field_key)
        if current_index > 0:
            order_list[current_index], order_list[current_index - 1] = order_list[current_index - 1], order_list[current_index]
            save_client_data()
            st.success(f"✅ Moved {field_key} up")

def move_field_down(field_key, field_type):
    """Move a field down in the order"""
    order_list = st.session_state.field_order[field_type]
    if field_key in order_list:
        current_index = order_list.index(field_key)
        if current_index < len(order_list) - 1:
            order_list[current_index], order_list[current_index + 1] = order_list[current_index + 1], order_list[current_index]
            save_client_data()
            st.success(f"✅ Moved {field_key} down")

def add_field_to_order(field_key, field_type):
    """Add a new field to the order"""
    if field_type == 'custom' and field_key not in st.session_state.field_order['custom']:
        st.session_state.field_order['custom'].append(field_key)
        save_client_data()

def remove_field_from_order(field_key, field_type):
    """Remove a field from the order"""
    if field_key in st.session_state.field_order[field_type]:
        st.session_state.field_order[field_type].remove(field_key)
        save_client_data()

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
        'options': ['5m', '1h', '4h', '24h'],
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
    'sentiment_community': {
        'label': 'Sentiment/Community',
        'type': 'text_input',
        'help': 'Community sentiment and social media buzz',
        'placeholder': 'Bullish on Twitter, active Discord community'
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
    st.title("🪵 Logging Journal")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Form for new entry (NO HEADER - removed as requested)
        with st.form("log_entry_form"):
            st.markdown("### Entry Details")
            
            # Create input widgets
            coin_symbol = st.text_input("Coin Symbol", key="input_coin_symbol", placeholder="BTC")
            date_logged = st.date_input("Date Logged", key="input_date_logged", value=datetime.now().date())
            market_cap = st.number_input("Market Cap", key="input_market_cap", placeholder="0")
            conviction_level = st.slider("Conviction Level", 1, 10, 5, key="input_conviction_level")
            trade_result = st.selectbox("Trade Result", ["Pending", "Win", "Loss"], key="input_trade_result")
            notes = st.text_area("Notes", key="input_notes", placeholder="Any additional thoughts...")
            
            # Form buttons
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.form_submit_button("📝 Add Entry"):
                    if coin_symbol:
                        # Create entry
                        entry_data = {
                            'coin_symbol': coin_symbol,
                            'date_logged': date_logged,
                            'market_cap': market_cap,
                            'conviction_level': conviction_level,
                            'trade_result': trade_result,
                            'notes': notes,
                            'timestamp': datetime.now()
                        }
                        
                        # Add to log entries
                        st.session_state.log_entries.append(entry_data)
                        
                        # Success message
                        st.success(f"✅ Added {coin_symbol} to your journal!")
                        
                        # Clear all form inputs
                        clear_form_inputs()
                        
                        # Rerun to refresh the form
                        st.rerun()
                    else:
                        st.error("❌ Coin symbol is required!")
            
            with col2:
                if st.form_submit_button("🗑️ Clear Form", type="secondary"):
                    clear_form_inputs()
                    st.rerun()
    
    with col2:
        if st.session_state.log_entries:
            total_entries = len(st.session_state.log_entries)
            st.metric("Total Entries", total_entries)
            
            # Recent entries
            st.subheader("Recent Entries")
            for i, entry in enumerate(st.session_state.log_entries[-3:]):
                coin = entry.get('coin_symbol', 'Unknown')
                date = entry.get('date_logged', 'No date')
                result = entry.get('trade_result', 'Pending')
                
                if isinstance(date, str):
                    date_str = date
                else:
                    date_str = date.strftime('%Y-%m-%d') if date else 'No date'
                
                if result == 'Win':
                    result_emoji = '✅'
                elif result == 'Loss':
                    result_emoji = '❌'
                else:
                    result_emoji = '⏳'
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"• {coin} - {date_str} {result_emoji}")
                with col2:
                    if st.button(f"🗑️", key=f"delete_recent_{i}"):
                        deleted_entry = st.session_state.log_entries.pop(i)
                        st.success(f"✅ Deleted {deleted_entry.get('coin_symbol', 'Unknown')} entry")
                        st.rerun()
        else:
            st.info("No entries logged yet. Start by creating your first entry!")
    
    # Display logged entries
    if st.session_state.log_entries:
        st.header("📈 Logged Entries")
        
        # Convert to DataFrame
        df = pd.DataFrame(st.session_state.log_entries)
        
        # Create interactive table
        st.markdown("### Interactive Data Table")
        
        for i, entry in enumerate(st.session_state.log_entries):
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1.5, 1.5, 2, 1.5, 1])
            
            with col1:
                st.write(f"**{entry.get('coin_symbol', 'Unknown')}**")
            
            with col2:
                date = entry.get('date_logged', 'No date')
                if isinstance(date, str):
                    st.write(date)
                else:
                    st.write(date.strftime('%Y-%m-%d') if date else 'No date')
            
            with col3:
                market_cap = entry.get('market_cap', '')
                if market_cap:
                    st.write(f"MC: {market_cap}")
                else:
                    st.write("MC: -")
            
            with col4:
                new_result = st.selectbox(
                    "Trade Result",
                    options=['Pending', 'Win', 'Loss'],
                    index=['Pending', 'Win', 'Loss'].index(entry.get('trade_result', 'Pending')),
                    key=f"edit_result_{i}",
                    label_visibility="collapsed"
                )
                if new_result != entry.get('trade_result'):
                    entry['trade_result'] = new_result
                    st.success(f"✅ Updated {entry.get('coin_symbol', 'Unknown')} to {new_result}")
                    st.rerun()
            
            with col5:
                current_result = entry.get('trade_result', 'Pending')
                if current_result == 'Win':
                    st.write('✅ Win')
                elif current_result == 'Loss':
                    st.write('❌ Loss')
                else:
                    st.write('⏳ Pending')
            
            with col6:
                if st.button(f"🗑️", key=f"delete_inline_{i}"):
                    deleted_entry = st.session_state.log_entries.pop(i)
                    st.success(f"✅ Deleted {deleted_entry.get('coin_symbol', 'Unknown')} entry")
                    st.rerun()
        
        # Export and clear buttons
        col1, col2 = st.columns(2)
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
            if st.button("🗑️ Clear All Logs", type="secondary"):
                st.session_state.log_entries = []
                st.success("✅ All logs cleared!")
                st.rerun()

if __name__ == "__main__":
    main()
