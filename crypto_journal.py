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
