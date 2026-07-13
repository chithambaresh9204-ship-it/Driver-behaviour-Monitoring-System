"""
Intelligent Driver Behaviour Monitoring System Database Manager
SQLite database operations for driver safety platform
"""

import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import os
from contextlib import contextmanager

class DatabaseManager:
    """SQLite database manager for Intelligent Driver Behaviour Monitoring System"""
    
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query, params=None, fetch_all=True):
        """Execute query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if 'SELECT' in query.upper():
                return cursor.fetchall() if fetch_all else cursor.fetchone()
            else:
                conn.commit()
                return cursor.lastrowid
    
    def init_database(self):
        """Create all required tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT CHECK(role IN ('driver', 'admin')) NOT NULL DEFAULT 'driver',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Drivers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS drivers (
                    driver_id TEXT PRIMARY KEY,
                    user_id INTEGER UNIQUE NOT NULL,
                    phone_number TEXT,
                    license_number TEXT UNIQUE,
                    license_expiration DATE,
                    date_of_birth DATE,
                    address TEXT,
                    join_date DATE NOT NULL,
                    status TEXT DEFAULT 'active',
                    vehicle_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                )
            ''')
            
            # Monthly scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_scores (
                    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    driver_id TEXT NOT NULL,
                    month_year TEXT NOT NULL,
                    overall_score INTEGER NOT NULL,
                    speed_control INTEGER NOT NULL,
                    focus INTEGER NOT NULL,
                    braking INTEGER NOT NULL,
                    turning INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    incidents_count INTEGER DEFAULT 0,
                    total_miles INTEGER DEFAULT 0,
                    avg_speed INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE,
                    UNIQUE(driver_id, month_year)
                )
            ''')
            
            # Incidents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    driver_id TEXT NOT NULL,
                    incident_date DATETIME NOT NULL,
                    incident_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    location TEXT,
                    description TEXT,
                    score_impact INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE
                )
            ''')
            
            # Model predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_predictions (
                    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    driver_id TEXT NOT NULL,
                    predicted_score INTEGER NOT NULL,
                    predicted_month TEXT NOT NULL,
                    model_type TEXT DEFAULT 'linear_regression',
                    model_accuracy REAL,
                    mae REAL,
                    rmse REAL,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE
                )
            ''')
            
            # Generated reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_reports (
                    report_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    driver_id TEXT NOT NULL,
                    report_type TEXT DEFAULT 'individual',
                    file_path TEXT,
                    generated_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE,
                    FOREIGN KEY(generated_by) REFERENCES users(user_id)
                )
            ''')
            
            conn.commit()
            
            # Create default admin account if it doesn't exist
            cursor.execute("SELECT user_id FROM users WHERE email = 'admin@gmail.com'")
            if not cursor.fetchone():
                import bcrypt
                admin_password_hash = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
                cursor.execute(
                    "INSERT INTO users (email, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                    ('admin@gmail.com', admin_password_hash, 'Administrator', 'admin')
                )
                conn.commit()
    
    # ==================== USER OPERATIONS ====================
    
    def add_user(self, email, password_hash, full_name, role='driver'):
        """Add new user to database"""
        try:
            query = '''
                INSERT INTO users (email, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            '''
            user_id = self.execute_query(query, (email, password_hash, full_name, role))
            return user_id
        except sqlite3.IntegrityError:
            return None
    
    def get_user_by_email(self, email):
        """Get user by email"""
        query = 'SELECT * FROM users WHERE email = ?'
        return self.execute_query(query, (email,), fetch_all=False)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        query = 'SELECT * FROM users WHERE user_id = ?'
        return self.execute_query(query, (user_id,), fetch_all=False)
    
    def update_last_login(self, user_id):
        """Update user's last login time"""
        query = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?'
        self.execute_query(query, (user_id,))
    
    def get_all_users(self):
        """Get all users"""
        query = 'SELECT * FROM users WHERE is_active = 1 ORDER BY created_at DESC'
        return self.execute_query(query)
    
    # ==================== DRIVER OPERATIONS ====================
    
    def add_driver(self, driver_id, user_id, phone=None, license_no=None, 
                   license_exp=None, dob=None, address=None, join_date=None):
        """Add new driver"""
        try:
            if join_date is None:
                join_date = datetime.now().strftime('%Y-%m-%d')
            
            query = '''
                INSERT INTO drivers 
                (driver_id, user_id, phone_number, license_number, 
                 license_expiration, date_of_birth, address, join_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.execute_query(query, (driver_id, user_id, phone, license_no, 
                                       license_exp, dob, address, join_date))
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_driver(self, driver_id):
        """Get driver by ID"""
        query = '''
            SELECT d.*, u.email, u.full_name 
            FROM drivers d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.driver_id = ?
        '''
        return self.execute_query(query, (driver_id,), fetch_all=False)
    
    def get_all_drivers(self):
        """Get all drivers"""
        query = '''
            SELECT d.*, u.email, u.full_name 
            FROM drivers d
            JOIN users u ON d.user_id = u.user_id
            WHERE d.status = 'active'
            ORDER BY d.join_date DESC
        '''
        return self.execute_query(query)
    
    def update_driver_status(self, driver_id, status):
        """Update driver status"""
        query = 'UPDATE drivers SET status = ? WHERE driver_id = ?'
        self.execute_query(query, (status, driver_id))
    
    # ==================== SCORE OPERATIONS ====================
    
    def add_monthly_score(self, driver_id, month_year, overall_score,
                         speed, focus, braking, turning, risk_level,
                         incidents=0, miles=0, avg_speed=0):
        """Add or update monthly score"""
        try:
            query = '''
                INSERT INTO monthly_scores
                (driver_id, month_year, overall_score, speed_control, 
                 focus, braking, turning, risk_level, incidents_count, 
                 total_miles, avg_speed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.execute_query(query, (driver_id, month_year, overall_score, speed, 
                                       focus, braking, turning, risk_level, 
                                       incidents, miles, avg_speed))
            return True
        except sqlite3.IntegrityError:
            # Update if exists
            query = '''
                UPDATE monthly_scores
                SET overall_score = ?, speed_control = ?, focus = ?,
                    braking = ?, turning = ?, risk_level = ?,
                    incidents_count = ?, total_miles = ?, avg_speed = ?
                WHERE driver_id = ? AND month_year = ?
            '''
            self.execute_query(query, (overall_score, speed, focus, braking, 
                                       turning, risk_level, incidents, miles, 
                                       avg_speed, driver_id, month_year))
            return True
    
    def get_monthly_scores(self, driver_id, limit=12):
        """Get monthly scores for driver"""
        query = '''
            SELECT * FROM monthly_scores
            WHERE driver_id = ?
            ORDER BY month_year DESC
            LIMIT ?
        '''
        return self.execute_query(query, (driver_id, limit))
    
    def get_current_month_score(self, driver_id):
        """Get latest month score for driver"""
        query = '''
            SELECT * FROM monthly_scores
            WHERE driver_id = ?
            ORDER BY month_year DESC
            LIMIT 1
        '''
        return self.execute_query(query, (driver_id,), fetch_all=False)
    
    def get_period_scores(self, driver_id, start_month, end_month):
        """Get scores for date range"""
        query = '''
            SELECT * FROM monthly_scores
            WHERE driver_id = ? AND month_year >= ? AND month_year <= ?
            ORDER BY month_year
        '''
        return self.execute_query(query, (driver_id, start_month, end_month))
    
    def get_all_scores(self):
        """Get all scores from all drivers"""
        query = 'SELECT * FROM monthly_scores ORDER BY month_year DESC'
        return self.execute_query(query)
    
    # ==================== PREDICTION OPERATIONS ====================
    
    def add_prediction(self, driver_id, predicted_score, predicted_month,
                      model_type='linear_regression', accuracy=0, mae=0, 
                      rmse=0, confidence=0):
        """Add model prediction"""
        query = '''
            INSERT INTO model_predictions
            (driver_id, predicted_score, predicted_month, model_type,
             model_accuracy, mae, rmse, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (driver_id, predicted_score, predicted_month, 
                                   model_type, accuracy, mae, rmse, confidence))
    
    def get_latest_prediction(self, driver_id):
        """Get latest prediction for driver"""
        query = '''
            SELECT * FROM model_predictions
            WHERE driver_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        '''
        return self.execute_query(query, (driver_id,), fetch_all=False)
    
    def get_all_predictions(self):
        """Get all predictions"""
        query = 'SELECT * FROM model_predictions ORDER BY created_at DESC'
        return self.execute_query(query)
    
    # ==================== INCIDENT OPERATIONS ====================
    
    def add_incident(self, driver_id, incident_date, incident_type,
                    severity, location='', description='', score_impact=0):
        """Add incident record"""
        query = '''
            INSERT INTO incidents
            (driver_id, incident_date, incident_type, severity, 
             location, description, score_impact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (driver_id, incident_date, incident_type, 
                                   severity, location, description, score_impact))
    
    def get_incidents(self, driver_id, months=6):
        """Get recent incidents for driver"""
        cutoff_date = datetime.now() - timedelta(days=30*months)
        query = '''
            SELECT * FROM incidents
            WHERE driver_id = ? AND incident_date >= ?
            ORDER BY incident_date DESC
        '''
        return self.execute_query(query, (driver_id, cutoff_date))
    
    def get_all_incidents(self):
        """Get all incidents"""
        query = 'SELECT * FROM incidents ORDER BY incident_date DESC'
        return self.execute_query(query)
    
    # ==================== REPORT OPERATIONS ====================
    
    def add_report(self, driver_id, report_type, file_path, generated_by):
        """Add generated report record"""
        query = '''
            INSERT INTO generated_reports
            (driver_id, report_type, file_path, generated_by)
            VALUES (?, ?, ?, ?)
        '''
        report_id = self.execute_query(query, (driver_id, report_type, file_path, generated_by))
        return report_id
    
    def get_reports(self, driver_id=None):
        """Get generated reports"""
        if driver_id:
            query = 'SELECT * FROM generated_reports WHERE driver_id = ? ORDER BY created_at DESC'
            return self.execute_query(query, (driver_id,))
        else:
            query = 'SELECT * FROM generated_reports ORDER BY created_at DESC'
            return self.execute_query(query)
    
    # ==================== ANALYTICS OPERATIONS ====================
    
    def get_fleet_metrics(self):
        """Get fleet-wide metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get latest month for all drivers
            cursor.execute('''
                SELECT AVG(overall_score) as avg_score
                FROM monthly_scores
                WHERE month_year = (SELECT MAX(month_year) FROM monthly_scores)
            ''')
            avg_score = cursor.fetchone()[0] or 0
            
            # High risk count
            cursor.execute('''
                SELECT COUNT(DISTINCT driver_id) as high_risk_count
                FROM monthly_scores
                WHERE risk_level = 'High'
                AND month_year = (SELECT MAX(month_year) FROM monthly_scores)
            ''')
            high_risk = cursor.fetchone()[0] or 0
            
            # Total active drivers
            cursor.execute('SELECT COUNT(*) FROM drivers WHERE status = "active"')
            total_drivers = cursor.fetchone()[0] or 0
            
            return {
                'avg_score': round(float(avg_score), 2),
                'high_risk_count': high_risk,
                'total_drivers': total_drivers
            }
    
    def get_risk_distribution(self):
        """Get risk level distribution"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT risk_level, COUNT(*) as count
                FROM monthly_scores
                WHERE month_year = (SELECT MAX(month_year) FROM monthly_scores)
                GROUP BY risk_level
            ''')
            
            result = cursor.fetchall()
            return {row[0]: row[1] for row in result}
    
    def get_top_drivers(self, limit=3):
        """Get top performing drivers"""
        query = '''
            SELECT d.driver_id, u.full_name, m.overall_score
            FROM drivers d
            JOIN users u ON d.user_id = u.user_id
            JOIN monthly_scores m ON d.driver_id = m.driver_id
            WHERE m.month_year = (SELECT MAX(month_year) FROM monthly_scores)
            ORDER BY m.overall_score DESC
            LIMIT ?
        '''
        return self.execute_query(query, (limit,))
    
    def get_bottom_drivers(self, limit=3):
        """Get bottom performing drivers"""
        query = '''
            SELECT d.driver_id, u.full_name, m.overall_score, m.risk_level
            FROM drivers d
            JOIN users u ON d.user_id = u.user_id
            JOIN monthly_scores m ON d.driver_id = m.driver_id
            WHERE m.month_year = (SELECT MAX(month_year) FROM monthly_scores)
            ORDER BY m.overall_score ASC
            LIMIT ?
        '''
        return self.execute_query(query, (limit,))
    
    # ==================== DATA IMPORT ====================
    
    def import_csv_data(self, csv_file):
        """Import driver scores from CSV file"""
        df = pd.read_csv(csv_file)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                # Handle missing values
                overall_score = int(row.get('overall_score', 75))
                speed = int(row.get('speed_control', 75))
                focus = int(row.get('focus', 75))
                braking = int(row.get('braking', 75))
                turning = int(row.get('turning', 75))
                risk_level = row.get('risk_level', 'Medium')
                
                cursor.execute('''
                    INSERT OR IGNORE INTO monthly_scores
                    (driver_id, month_year, overall_score, speed_control,
                     focus, braking, turning, risk_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['driver_id'], row['month_year'], overall_score,
                      speed, focus, braking, turning, risk_level))
            
            conn.commit()
    
    # ==================== DATABASE MAINTENANCE ====================
    
    def clear_all_data(self):
        """Clear all data from database (for testing)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM generated_reports')
            cursor.execute('DELETE FROM model_predictions')
            cursor.execute('DELETE FROM incidents')
            cursor.execute('DELETE FROM monthly_scores')
            cursor.execute('DELETE FROM drivers')
            cursor.execute('DELETE FROM users')
            conn.commit()
    
    def get_db_stats(self):
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Count records
            cursor.execute('SELECT COUNT(*) FROM users')
            stats['total_users'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM drivers')
            stats['total_drivers'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM monthly_scores')
            stats['total_scores'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM incidents')
            stats['total_incidents'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM model_predictions')
            stats['total_predictions'] = cursor.fetchone()[0]
            
            return stats


# Global database manager instance
db = DatabaseManager()