"""
Intelligent Driver Behaviour Monitoring System Email Alert Module
Email notification system for driver events and alerts
Production-ready with SMTP support and customizable templates
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List, Dict
import os
from dotenv import load_dotenv # type: ignore

# Load environment variables
load_dotenv()


class EmailManager:
    """Email notification manager for Intelligent Driver Behaviour Monitoring System"""
    
    def __init__(self, smtp_server: str = None, smtp_port: int = None,
                 sender_email: str = None, sender_password: str = None):
        """Initialize email manager with SMTP credentials"""
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', 587))
        self.sender_email = sender_email or os.getenv('SMTP_EMAIL', 'noreply@Intelligent Driver Behaviour Monitoring System.com')
        self.sender_password = sender_password or os.getenv('SMTP_PASSWORD', '')
        self.is_configured = bool(self.sender_password)
    
    def send_alert(self, recipient_email: str, subject: str, body: str, 
                   html: bool = False) -> bool:
        """Send email alert to recipient"""
        if not self.is_configured:
            print("⚠️  Email not configured. Skipping email send.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Add body
            if html:
                message.attach(MIMEText(body, "html"))
            else:
                message.attach(MIMEText(body, "plain"))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    recipient_email,
                    message.as_string()
                )
            
            print(f"✓ Email sent to {recipient_email}")
            return True
        
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False
    
    def send_high_risk_alert(self, recipient_email: str, driver_name: str, 
                            driver_id: str, score: int, risk_level: str) -> bool:
        """Send high-risk driver alert"""
        subject = f"🚨 High-Risk Alert: {driver_name}"
        
        body = f"""
Intelligent Driver Behaviour Monitoring System - High-Risk Driver Alert
{'='*50}

Dear Administrator,

A driver has been identified as HIGH RISK and requires immediate attention.

DRIVER INFORMATION:
- Name: {driver_name}
- Driver ID: {driver_id}
- Current Score: {score}/100
- Risk Level: {risk_level}
- Alert Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ACTION REQUIRED:
1. Review driver's recent performance data
2. Schedule a safety meeting with the driver
3. Provide additional training if necessary
4. Monitor performance closely

For detailed information, please log into the Intelligent Driver Behaviour Monitoring System dashboard.

Best regards,
Intelligent Driver Behaviour Monitoring System
"""
        
        return self.send_alert(recipient_email, subject, body)
    
    def send_weekly_report(self, recipient_email: str, fleet_metrics: Dict) -> bool:
        """Send weekly fleet report"""
        subject = "📊 Weekly Fleet Safety Report - Intelligent Driver Behaviour Monitoring System"
        
        report_date = datetime.now().strftime('%Y-%m-%d')
        
        body = f"""
Intelligent Driver Behaviour Monitoring System - Weekly Fleet Safety Report
{'='*50}

Generated: {report_date}

FLEET METRICS:
- Average Fleet Score: {fleet_metrics.get('avg_score', 'N/A')}/100
- High Risk Drivers: {fleet_metrics.get('high_risk_count', 0)}
- Total Active Drivers: {fleet_metrics.get('total_drivers', 0)}
- Safety Status: {'Good ✓' if fleet_metrics.get('avg_score', 0) >= 80 else 'Fair ⚠️' if fleet_metrics.get('avg_score', 0) >= 70 else 'Needs Attention ❌'}

KEY INSIGHTS:
- Monitor drivers with scores below 70
- High-risk drivers require immediate intervention
- Continue monitoring trends for improvement

For detailed analytics and reports, please access the Intelligent Driver Behaviour Monitoring System dashboard.

Best regards,
Intelligent Driver Behaviour Monitoring System
"""
        
        return self.send_alert(recipient_email, subject, body)
    
    def send_monthly_summary(self, recipient_email: str, driver_name: str, 
                            driver_id: str, monthly_score: int, trend: str) -> bool:
        """Send monthly driver summary"""
        subject = f"📈 Monthly Summary - {driver_name}"
        
        body = f"""
Intelligent Driver Behaviour Monitoring System - Monthly Safety Summary
{'='*50}

Driver: {driver_name} ({driver_id})
Report Month: {datetime.now().strftime('%B %Y')}

PERFORMANCE:
- Monthly Score: {monthly_score}/100
- Trend: {trend}
- Status: {'Excellent ✓' if monthly_score >= 85 else 'Good ✓' if monthly_score >= 70 else 'Needs Improvement ⚠️'}

RECOMMENDATIONS:
- Continue safe driving practices
- Focus on areas of improvement
- Attend safety training sessions if needed

For detailed analysis, visit the Intelligent Driver Behaviour Monitoring System dashboard.

Best regards,
Intelligent Driver Behaviour Monitoring System
"""
        
        return self.send_alert(recipient_email, subject, body)
    
    def send_milestone_alert(self, recipient_email: str, driver_name: str, 
                            milestone: str) -> bool:
        """Send milestone achievement alert"""
        subject = f"🎉 Achievement: {driver_name} - {milestone}"
        
        body = f"""
Intelligent Driver Behaviour Monitoring System - Achievement Milestone
{'='*50}

Congratulations!

{driver_name} has achieved an important safety milestone:

MILESTONE: {milestone}

This recognition is based on consistent safe driving practices and high performance scores.

Continue maintaining these excellent standards!

Best regards,
Intelligent Driver Behaviour Monitoring System
"""
        
        return self.send_alert(recipient_email, subject, body)
    
    def send_training_reminder(self, recipient_email: str, driver_name: str, 
                              training_date: str, training_type: str) -> bool:
        """Send training reminder"""
        subject = f"📚 Training Reminder - {training_type}"
        
        body = f"""
Intelligent Driver Behaviour Monitoring System - Training Reminder
{'='*50}

Dear {driver_name},

This is a reminder about your upcoming safety training:

TRAINING DETAILS:
- Type: {training_type}
- Scheduled Date: {training_date}
- Duration: 1-2 hours
- Location: Contact your dispatcher for details

Please confirm your attendance and ensure you complete the training.

For more information, contact the safety department.

Best regards,
Intelligent Driver Behaviour Monitoring System
"""
        
        return self.send_alert(recipient_email, subject, body)
    
    def send_score_improvement_notification(self, recipient_email: str, 
                                           driver_name: str, driver_id: str,
                                           previous_score: int, current_score: int) -> bool:
        """Send score improvement notification"""
        improvement = current_score - previous_score
        subject = f"✓ Score Improvement - {driver_name}"
        
        body = f"""
Intelligent Driver Behaviour Monitoring System - Score Improvement Notification
{'='*50}

Good News, {driver_name}!

Your driving safety score has improved:

SCORE COMPARISON:
- Previous Score: {previous_score}/100
- Current Score: {current_score}/100
- Improvement: +{improvement} points

Keep up the excellent work! Consistent safe driving practices lead to lower insurance rates 
and better fleet performance.

For detailed metrics, visit the Intelligent Driver Behaviour Monitoring System dashboard.

Best regards,
Intelligent Driver Behaviour Monitoring System
"""
        
        return self.send_alert(recipient_email, subject, body)
    
    def send_incident_report(self, recipient_email: str, driver_name: str, 
                            incident_type: str, severity: str, 
                            incident_date: str, description: str) -> bool:
        """Send incident report notification"""
        subject = f"⚠️ Incident Report - {driver_name}"
        
        body = f"""
Intelligent Driver Behaviour Monitoring System - Incident Report
{'='*50}

An incident has been recorded for your review:

INCIDENT DETAILS:
- Driver: {driver_name}
- Type: {incident_type}
- Severity: {severity}
- Date: {incident_date}
- Description: {description}

RECOMMENDED ACTIONS:
1. Review the incident with the driver
2. Provide coaching if necessary
3. Monitor for patterns
4. Update driver's training records if needed

For detailed information, access the Intelligent Driver Behaviour Monitoring System dashboard.

Best regards,
Intelligent Driver Behaviour Monitoring System
"""
        
        return self.send_alert(recipient_email, subject, body)
    
    def send_license_expiration_warning(self, recipient_email: str, driver_name: str, 
                                       expiration_date: str, days_remaining: int) -> bool:
        """Send license expiration warning"""
        subject = f"⏰ License Renewal Reminder - {driver_name}"
        
        body = f"""
Intelligent Driver Behaviour Monitoring System - License Renewal Reminder
{'='*50}

Dear {driver_name},

Your driver's license is expiring soon:

LICENSE DETAILS:
- Expiration Date: {expiration_date}
- Days Remaining: {days_remaining}

ACTION REQUIRED:
Please renew your license before the expiration date to maintain your active driver status.

Contact your local DMV or licensing authority to schedule your renewal appointment.

Best regards,
Intelligent Driver Behaviour Monitoring System
"""
        
        return self.send_alert(recipient_email, subject, body)
    
    def send_batch_alerts(self, alert_list: List[Dict]) -> int:
        """Send multiple alerts in batch"""
        sent_count = 0
        
        for alert in alert_list:
            try:
                if alert['type'] == 'high_risk':
                    result = self.send_high_risk_alert(
                        alert['email'],
                        alert['driver_name'],
                        alert['driver_id'],
                        alert['score'],
                        alert['risk_level']
                    )
                elif alert['type'] == 'weekly_report':
                    result = self.send_weekly_report(
                        alert['email'],
                        alert['metrics']
                    )
                elif alert['type'] == 'incident':
                    result = self.send_incident_report(
                        alert['email'],
                        alert['driver_name'],
                        alert['incident_type'],
                        alert['severity'],
                        alert['incident_date'],
                        alert['description']
                    )
                
                if result:
                    sent_count += 1
            
            except Exception as e:
                print(f"❌ Error sending alert: {str(e)}")
        
        return sent_count
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            print("✓ SMTP connection successful")
            return True
        except Exception as e:
            print(f"❌ SMTP connection failed: {str(e)}")
            return False


# Global email manager instance
email_manager = EmailManager()


# Convenience functions

def send_high_risk_alert(email: str, driver_name: str, driver_id: str, 
                        score: int, risk_level: str) -> bool:
    """Convenience function to send high-risk alert"""
    return email_manager.send_high_risk_alert(email, driver_name, driver_id, score, risk_level)


def send_weekly_report(email: str, metrics: Dict) -> bool:
    """Convenience function to send weekly report"""
    return email_manager.send_weekly_report(email, metrics)


def send_incident_notification(email: str, driver_name: str, incident_type: str, 
                               severity: str, incident_date: str, description: str) -> bool:
    """Convenience function to send incident notification"""
    return email_manager.send_incident_report(email, driver_name, incident_type, 
                                             severity, incident_date, description)


def send_milestone_notification(email: str, driver_name: str, milestone: str) -> bool:
    """Convenience function to send milestone notification"""
    return email_manager.send_milestone_alert(email, driver_name, milestone)


# Example usage
if __name__ == "__main__":
    # Test email configuration
    print("Testing email configuration...")
    
    # Create email manager
    em = EmailManager()
    
    # Test connection
    if em.test_connection():
        print("✓ Email system ready")
        
        # Send test alert
        em.send_high_risk_alert(
            "admin@example.com",
            "John Doe",
            "DRV000001",
            65,
            "High"
        )
    else:
        print("⚠️  Email not configured - alerts will be skipped")