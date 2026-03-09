import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

        /* TYPOGRAPHY */
        html, body, [class*="css"], .stApp, p, div, span, h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
        }

        /* PAGE BACKGROUND */
        .stApp {
            background: linear-gradient(to bottom, #514648, #41353a, #30262c, #201720, #0f0314);     
        }

        /* Styling the st.container visually */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px;
            background: rgba(31, 40, 51, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(0, 242, 254, 0.2);
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
            padding: 10px;
        }
        
        [data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 242, 254, 0.15);
            border: 1px solid rgba(0, 242, 254, 0.5);
        }

        /* Sleek Button Styling */
        .stButton > button {
            background: linear-gradient(45deg, #FF512F 0%, #F09819 100%);
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px 0 rgba(252, 104, 110, 0.75);
        }
        
        .stButton > button:hover {
            background: linear-gradient(45deg, #F09819 0%, #FF512F 100%);
            box-shadow: 0 6px 20px 0 rgba(252, 104, 110, 0.9);
            transform: scale(1.02);
            color: white !important;
        }

        /* Primary Button (e.g., Logout) */
        .stButton > button[kind="primary"] {
             background: linear-gradient(45deg, #ec008c 0%, #fc6767 100%);
             box-shadow: 0 4px 15px 0 rgba(236, 0, 140, 0.75);
             transition: all 0.3s ease;
        }
        
        .stButton > button[kind="primary"]:hover {
             background: linear-gradient(45deg, #fc6767 0%, #ec008c 100%);
             box-shadow: 0 6px 20px 0 rgba(236, 0, 140, 0.9);
             transition: all 0.3s ease;
        }

        /* Input fields glowing focus */
        .stTextInput input, .stNumberInput input {
            border-radius: 6px;
            border: 1px solid #4facfe;
            background-color: rgba(11, 12, 16, 0.8) !important;
            color: white !important;
        }
        
        .stTextInput input:focus, .stNumberInput input:focus {
            box-shadow: 0 0 8px rgba(0, 242, 254, 0.6);
            border-color: #00f2fe;
        }
        
        /* Metric Styling */
        [data-testid="stMetricValue"] {
            color: #00f2fe;
            font-weight: 700;
        }

        /* Alerts & Notifications */
        [data-testid="stAlert"] {
            border-radius: 10px;
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            border-left: 4px solid #00f2fe !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            color: white;
            transition: all 0.3s ease;
        }
        [data-testid="stAlert"] p {
            color: #f8f9fa;
        }

        /* Tab Styling */
        [data-baseweb="tab-list"] {
            gap: 16px;
            background-color: transparent;
        }
        [data-baseweb="tab"] {
            background-color: transparent !important;
            border: none !important;
            color: #b0c4de !important;
            padding: 10px 16px;
            font-weight: 600;
            border-bottom: 3px solid transparent !important;
            transition: all 0.3s ease;
        }
        [data-baseweb="tab"][aria-selected="true"] {
            color: #00f2fe !important;
            border-bottom: 3px solid #00f2fe !important;
            text-shadow: 0 0 8px rgba(0, 242, 254, 0.5);
        }
        [data-baseweb="tab"]:hover {
            color: white !important;
            background-color: rgba(255,255,255,0.05) !important;
            border-radius: 6px 6px 0 0;
        }

        /* Divider Styling */
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(0, 242, 254, 0.5), transparent);
            margin: 2rem 0;
        }

        /* Dataframe Wrapper/Container */
        [data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(0, 242, 254, 0.15);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            transition: box-shadow 0.3s ease;
        }
        [data-testid="stDataFrame"]:hover {
            box-shadow: 0 6px 20px rgba(0, 242, 254, 0.25);
            border: 1px solid rgba(0, 242, 254, 0.35);
        }
        
        /* Expander Styling */
        [data-testid="stExpander"] {
            background: rgba(31, 40, 51, 0.4);
            border-radius: 10px;
            border: 1px solid rgba(0, 242, 254, 0.1);
            backdrop-filter: blur(5px);
            margin-bottom: 10px;
        }
        [data-testid="stExpander"] summary {
            font-weight: 600;
            color: #00f2fe;
        }
        </style>
    """, unsafe_allow_html=True)
