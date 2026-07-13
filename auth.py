"""
Intelligent Driver Behaviour Monitoring System Authentication Module
Complete login, signup, and password management system
Production-ready with Bcrypt hashing and professional Streamlit UI
"""

import streamlit as st
import bcrypt
from database import db
from datetime import datetime
import re
from typing import Tuple, List, Dict, Optional

class AuthManager:
    """Authentication manager for Intelligent Driver Behaviour Monitoring System - Complete implementation"""
    
    # ==================== PASSWORD MANAGEMENT ====================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with cost factor 12"""
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against bcrypt hash"""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False
    
    # ==================== VALIDATION ====================
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_driver_id_and_name(driver_id: str, driver_name: str) -> Dict:
        """Validate driver ID and name match against registered drivers"""
        import pandas as pd
        import os
        
        # Load driver mapping
        mapping_file = 'driver_mapping.csv'
        
        if not os.path.exists(mapping_file):
            return {
                'valid': False,
                'message': 'Driver database not found. Contact administrator.'
            }
        
        try:
            df = pd.read_csv(mapping_file)
            
            # Normalize inputs
            driver_id_upper = driver_id.upper().strip()
            driver_name_clean = driver_name.strip().title()
            
            # Check if driver ID exists
            driver_record = df[df['driver_id'].str.upper() == driver_id_upper]
            
            if driver_record.empty:
                valid_ids = ', '.join(df['driver_id'].unique())
                return {
                    'valid': False,
                    'message': f'Invalid Driver ID. Valid IDs are: {valid_ids}'
                }
            
            # Check if name matches
            registered_name = driver_record.iloc[0]['driver_name'].strip().title()
            
            if driver_name_clean != registered_name:
                return {
                    'valid': False,
                    'message': f'Name mismatch! Driver ID {driver_id_upper} is registered as "{registered_name}". Please enter the correct name.'
                }
            
            # All validations passed
            return {
                'valid': True,
                'message': 'Driver ID and name verified successfully!'
            }
        
        except Exception as e:
            return {
                'valid': False,
                'message': f'Error validating driver ID: {str(e)}'
            }
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, List[str], List[str]]:
        """Validate password meets requirements"""
        requirements = []
        passed = []
        
        # Check length
        if len(password) >= 8:
            passed.append("✓ At least 8 characters")
        else:
            requirements.append("❌ At least 8 characters")
        
        # Check uppercase
        if any(c.isupper() for c in password):
            passed.append("✓ One uppercase letter (A-Z)")
        else:
            requirements.append("❌ One uppercase letter (A-Z)")
        
        # Check number
        if any(c.isdigit() for c in password):
            passed.append("✓ One number (0-9)")
        else:
            requirements.append("❌ One number (0-9)")
        
        # Check special character
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            passed.append("✓ One special character (!@#$%^&*)")
        else:
            requirements.append("❌ One special character (!@#$%^&*)")
        
        is_valid = len(requirements) == 0
        return is_valid, passed, requirements
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        cleaned = re.sub(r'[^\d+]', '', phone)
        return len(cleaned) >= 10
    
    @staticmethod
    def validate_license(license_no: str) -> bool:
        """Validate driver license format"""
        return len(license_no) >= 5 and len(license_no) <= 20
    
    # ==================== REGISTRATION ====================
    
    @staticmethod
    def register_user(email: str, password: str, full_name: str, 
                     role: str = 'driver', phone: str = None, 
                     license_no: str = None, driver_id: str = None) -> Tuple[bool, str]:
        """Register new user with validation"""
        
        # Validate email
        if not email or not AuthManager.validate_email(email):
            return False, "Invalid email format (example: user@company.com)"
        
        # Validate password
        is_valid, _, requirements = AuthManager.validate_password_strength(password)
        if not is_valid:
            req_str = "; ".join(requirements)
            return False, f"Password requirements: {req_str}"
        
        # Validate driver-specific fields
        if role == 'driver':
            if not license_no or not AuthManager.validate_license(license_no):
                return False, "License number must be 5-20 characters"
            
            if phone and not AuthManager.validate_phone(phone):
                return False, "Invalid phone number format"
        
        # Hash password
        password_hash = AuthManager.hash_password(password)
        
        # Add user to database
        user_id = db.add_user(email, password_hash, full_name, role)
        
        if not user_id:
            return False, "Email already registered"
        
        # Create driver record if driver role
        if role == 'driver':
            db_driver_id = f"DRV{user_id:06d}"
            success = db.add_driver(
                driver_id=db_driver_id,
                user_id=user_id,
                phone=phone,
                license_no=license_no,
                license_exp=None,
                dob=None,
                address=None,
                join_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            if not success:
                return False, "Failed to create driver profile"
            
            return True, f"Registration successful! Your Driver ID: {db_driver_id}"
        else:
            return True, f"Registration successful! Admin ID: {user_id}"
    
    # ==================== LOGIN ====================
    
    @staticmethod
    def login_user(email: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """Authenticate user and return user data"""
        
        if not email or not password:
            return False, None, "❌ Please enter email and password"
        
        # Get user from database
        user = db.get_user_by_email(email)
        
        if not user:
            return False, None, "❌ Invalid email or password"
        
        # Extract user data
        user_id = user[0]
        email_db = user[1]
        password_hash = user[2]
        full_name = user[3]
        role = user[4]
        is_active = user[5]
        
        # Check if user is active
        if not is_active:
            return False, None, "❌ Account is inactive. Please contact administrator."
        
        # Verify password
        if not AuthManager.verify_password(password, password_hash):
            return False, None, "❌ Invalid email or password"
        
        # Update last login
        db.update_last_login(user_id)
        
        # Create user data dict
        user_data = {
            'user_id': user_id,
            'email': email_db,
            'full_name': full_name,
            'role': role
        }
        
        # Add driver_id if driver role
        if role == 'driver':
            driver_id = f"DRV{user_id:06d}"
            driver = db.get_driver(driver_id)
            if driver:
                user_data['driver_id'] = driver_id
        
        return True, user_data, f"✓ Welcome back, {full_name}!"
    
    # ==================== UI COMPONENTS ====================
    
    @staticmethod
    def show_login_page() -> None:
        """Render modern login/signup page"""
        
        # Modern Premium Styling - Clean Glass Edition
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700;800&display=swap');
            
            /* Global Styles */
            .stApp {
                background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 50%, #F5F3FF 100%) !important;
            }
            
            [data-testid="stAppViewContainer"] {
                background: transparent !important;
                font-family: 'Outfit', 'Inter', sans-serif !important;
            }

            /* Decorative Background Blobs */
            .stApp::before {
                content: "";
                position: fixed;
                top: -10%;
                right: -10%;
                width: 40vw;
                height: 40vw;
                background: radial-gradient(circle, rgba(14, 165, 233, 0.1) 0%, rgba(14, 165, 233, 0) 70%);
                filter: blur(80px);
                z-index: -1;
                animation: float 20s infinite alternate;
            }
            
            .stApp::after {
                content: "";
                position: fixed;
                bottom: -5%;
                left: -5%;
                width: 35vw;
                height: 35vw;
                background: radial-gradient(circle, rgba(139, 92, 246, 0.08) 0%, rgba(139, 92, 246, 0) 70%);
                filter: blur(80px);
                z-index: -1;
                animation: float 25s infinite alternate-reverse;
            }

            @keyframes float {
                0% { transform: translate(0, 0) rotate(0deg); }
                100% { transform: translate(5%, 5%) rotate(10deg); }
            }

            /* Hide default Streamlit elements for "App" feel */
            header { visibility: hidden; }
            [data-testid="stSidebar"] { display: none; }
            .stMainBlockContainer { padding-top: 2rem !important; }

            /* Glassmorphism Card Container */
            .auth-card {
                background: rgba(255, 255, 255, 0.6) !important;
                backdrop-filter: blur(16px) saturate(180%) !important;
                -webkit-backdrop-filter: blur(16px) saturate(180%) !important;
                border: 1px solid rgba(255, 255, 255, 0.3) !important;
                border-radius: 24px !important;
                padding: 3rem 2.5rem !important;
                box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07) !important;
                margin-top: 2vh;
            }

            /* Tabs Styling */
            .stTabs [data-baseweb="tab-list"] { 
                gap: 12px; 
                background: rgba(255, 255, 255, 0.3);
                padding: 6px;
                border-radius: 16px;
                margin-bottom: 2rem;
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 12px !important;
                padding: 10px 32px !important;
                font-weight: 600 !important;
                color: #64748B !important;
                border: none !important;
                transition: all 0.3s ease !important;
            }
            .stTabs [aria-selected="true"] {
                background: #FFFFFF !important;
                color: #0EA5E9 !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            }
            .stTabs [data-baseweb="tab-highlight"] { background-color: transparent !important; }

            /* Input Fields */
            .stTextInput input {
                border-radius: 14px !important;
                border: 1px solid rgba(148, 163, 184, 0.2) !important;
                background: rgba(255, 255, 255, 0.5) !important;
                color: #1E293B !important;
                padding: 0.75rem 1rem !important;
                font-size: 0.95rem !important;
                transition: all 0.25s ease !important;
            }
            .stTextInput input:focus {
                border-color: #0EA5E9 !important;
                box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1) !important;
                background: #FFFFFF !important;
            }
            label p {
                color: #475569 !important;
                font-weight: 500 !important;
                font-size: 0.9rem !important;
                margin-bottom: 4px !important;
            }

            /* Primary Button */
            .stButton > button {
                background: linear-gradient(135deg, #0EA5E9, #2563EB) !important;
                color: #FFFFFF !important;
                font-weight: 600 !important;
                border: none !important;
                border-radius: 14px !important;
                padding: 1rem 2rem !important;
                width: 100% !important;
                font-size: 1rem !important;
                letter-spacing: 0.01em !important;
                box-shadow: 0 10px 15px -3px rgba(14, 165, 233, 0.3) !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }
            .stButton > button:hover {
                transform: translateY(-2px) !important;
                box-shadow: 0 20px 25px -5px rgba(14, 165, 233, 0.4) !important;
                filter: brightness(1.05);
            }
            .stButton > button:active {
                transform: translateY(0px) !important;
            }

            /* Dividers and Info */
            .stDivider { border-color: rgba(148, 163, 184, 0.1) !important; }
            .stAlert { border-radius: 14px !important; border: none !important; }
            
            /* Custom Brand Logo Animation */
            @keyframes pulse-icon {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            .brand-icon {
                animation: pulse-icon 4s infinite ease-in-out;
                display: inline-block;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Content Container (Wrapped in our glass card)
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        
        # Brand Header
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <div class='brand-icon' style='font-size: 4rem; margin-bottom: 1rem;'>🛡️</div>
            <h1 style='color: #0F172A !important; font-size: 2.5rem; font-weight: 800; letter-spacing: -0.04em; margin-bottom: 0.5rem;'>DriveGuard</h1>
            <p style='color: #64748B !important; font-size: 1rem; font-weight: 400; letter-spacing: 0.02em;'>Premium Driver Safety Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
            
        # Tabs for login/signup
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
        
        # ==================== SIGN IN TAB ====================
        with tab1:
            st.subheader("Welcome Back", divider="blue")
            
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input(
                    "Email Address",
                    placeholder="you@company.com",
                    help="Your registered email",
                    key="login_email"
                )
                
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••",
                    help="Your password",
                    key="login_pass"
                )
                
                remember_me = st.checkbox("Remember me on this device", value=False)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    submitted = st.form_submit_button(
                        "Sign In",
                        use_container_width=True,
                        type="primary"
                    )
                
                if submitted:
                    if not email or not password:
                        st.error("❌ Please enter both email and password")
                    else:
                        with st.spinner("Signing in..."):
                            success, user_data, message = AuthManager.login_user(email, password)
                            
                            if success:
                                st.session_state.user = user_data
                                st.session_state.remember_me = remember_me
                                st.success(message)
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(message)
            
            # Password recovery
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("Forgot Password?", use_container_width=True, key="forgot_btn"):
                    st.info("📧 Contact your administrator to reset your password")
        
        # ==================== SIGN UP TAB ====================
        with tab2:
            st.subheader("Driver Registration", divider="blue")
            
            with st.form("signup_form", clear_on_submit=False):
                # Driver ID (NEW - REQUIRED)
                driver_id_input = st.text_input(
                    "Driver ID",
                    placeholder="Enter your driver ID",
                    help="Your assigned driver ID from the system",
                    key="signup_driver_id"
                ).strip()
                
                # Full Name
                full_name = st.text_input(
                    "Full Name",
                    placeholder="John Doe",
                    help="Your full name",
                    key="signup_name"
                )
                
                # Email
                email_signup = st.text_input(
                    "Email Address",
                    placeholder="driver@company.com",
                    help="Your email address",
                    key="signup_email"
                )
                
                # Password with strength indicator
                st.write("**Create Password**")
                password_signup = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••",
                    key="signup_pass",
                    help="Min 8 chars, 1 uppercase, 1 number, 1 special char"
                )
                
                # Password strength display
                if password_signup:
                    is_valid, passed, requirements = AuthManager.validate_password_strength(password_signup)
                    
                    for item in passed:
                        st.caption(f"✓ {item}")
                    for item in requirements:
                        st.caption(item)
                
                password_confirm = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="••••••••",
                    key="confirm_pass"
                )
                
                st.divider()
                
                # Driver-specific fields
                st.subheader("Contact Information", divider=False)
                
                # Phone number
                phone = st.text_input(
                    "Phone Number",
                    placeholder="+1-234-567-8900",
                    help="Your contact number",
                    key="signup_phone"
                )
                
                license_no = st.text_input(
                    "Driver License Number",
                    placeholder="DL123456",
                    help="Your driver license number",
                    key="signup_license"
                )
                
                st.divider()
                
                # Terms and conditions
                terms_agreed = st.checkbox(
                    "I agree to the Terms of Service and Privacy Policy",
                    value=False,
                    help="You must agree to continue"
                )
                
                submitted = st.form_submit_button(
                    "Create Account",
                    use_container_width=True,
                    type="primary"
                )
                
                # ==================== REGISTRATION LOGIC ====================
                if submitted:
                    # Validation
                    if not driver_id_input:
                        st.error("❌ Please enter your Driver ID")
                    elif not full_name:
                        st.error("❌ Please enter your full name")
                    elif not email_signup:
                        st.error("❌ Please enter your email")
                    elif not password_signup:
                        st.error("❌ Please enter a password")
                    elif password_signup != password_confirm:
                        st.error("❌ Passwords don't match")
                    elif not terms_agreed:
                        st.error("❌ You must agree to the terms of service")
                    elif not license_no:
                        st.error("❌ Driver license number is required")
                    else:
                        # Validate driver ID is numeric (1-18)
                        try:
                            driver_id_num = int(driver_id_input)
                            if driver_id_num < 1 or driver_id_num > 18:
                                st.error("❌ Driver ID must be between 1 and 18")
                            else:
                                # Driver registration with driver_id
                                with st.spinner("Creating account..."):
                                    success, message = AuthManager.register_user(
                                        email=email_signup,
                                        password=password_signup,
                                        full_name=full_name,
                                        role='driver',
                                        phone=phone,
                                        license_no=license_no,
                                        driver_id=driver_id_input
                                    )
                                    
                                    if success:
                                        st.success("✅ Account created successfully!")
                                        st.balloons()
                                        st.info("Please login with your Driver ID and password")
                                    else:
                                        st.error(f"❌ {message}")
                        except ValueError:
                            st.error("❌ Driver ID must be a number (1-18)")
        
        # Close the auth-card div
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("""
        <div style='text-align: center; margin-top: 2rem; padding-bottom: 2rem;'>
            <p style='color: #94A3B8; font-size: 0.85rem;'>© 2026 DriveGuard Intelligence System. All rights reserved.</p>
        </div>
        """, unsafe_allow_html=True)

    # ==================== SESSION MANAGEMENT ====================
    
    @staticmethod
    def show_logout_button() -> None:
        """Show logout button in sidebar"""
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state.user = None
            st.session_state.remember_me = False
            st.success("✓ Logged out successfully")
            st.rerun()
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    @staticmethod
    def get_current_user() -> Optional[Dict]:
        """Get current authenticated user"""
        if AuthManager.is_authenticated():
            return st.session_state.user
        return None
    
    @staticmethod
    def require_auth(required_role: str = None):
        """Decorator to require authentication"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not AuthManager.is_authenticated():
                    st.error("❌ Please log in first")
                    st.stop()
                
                user = AuthManager.get_current_user()
                
                if required_role and user['role'] != required_role:
                    st.error(f"❌ This page requires {required_role} access")
                    st.stop()
                
                return func(*args, **kwargs)
            return wrapper
        return decorator


# ==================== STREAMLIT SESSION INITIALIZATION ====================

def init_auth_session() -> None:
    """Initialize authentication session state"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'remember_me' not in st.session_state:
        st.session_state.remember_me = False
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0


# ==================== UTILITY FUNCTIONS ====================

def get_user_greeting() -> str:
    """Get personalized greeting for user"""
    if not AuthManager.is_authenticated():
        return ""
    
    user = AuthManager.get_current_user()
    hour = datetime.now().hour
    
    if hour < 12:
        greeting = "Good Morning"
    elif hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    return f"{greeting}, {user['full_name']}! 👋"


def display_user_info() -> None:
    user = AuthManager.get_current_user()
    
    st.write(f"👤 **Name:** {user['full_name']}")
    st.write(f"📧 **Email:** {user['email']}")
    st.write(f"🔐 **Role:** {user['role'].upper()}")
    
    if 'driver_id' in user:
        st.write(f"**Driver ID:** {user['driver_id']}")