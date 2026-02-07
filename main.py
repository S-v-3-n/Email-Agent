import os
import sys
import logging
from src.email_client import EmailClient
from src.ai_engine import AIEngine
from src.config import Config

from src.context_loader import load_context

# Configure logging to stdout
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    print("=== Outlook Email Response Agent ===")
    
    # 1. Initialize logic
    if not Config.EMAIL_USER or not Config.EMAIL_PASSWORD:
        print("Error: EMAIL_USER or EMAIL_PASSWORD not set in .env")
        return

    try:
        client = EmailClient()
        ai = AIEngine()
        
        # Load Context Resources
        print("Loading resources...")
        context_data = load_context()
        if context_data:
            print("Loaded context resources.")
        else:
            print("No context resources found in 'resources/' folder.")

        print(f"Connecting to Outlook as {Config.EMAIL_USER}...")
        client.connect()
        
        # 2. Fetch Unread
        if Config.TARGET_SENDER:
            print(f"Fetching unread emails from: {Config.TARGET_SENDER}...")
        else:
            print("Fetching all unread emails...")
            
        emails = client.fetch_unread_emails(sender_filter=Config.TARGET_SENDER)
        
        if not emails:
            print("No unread emails found.")
            return

        print(f"Found {len(emails)} unread emails.")

        # --- DEDUPLICATION LOGIC ---
        # Group by normalized subject (remove Re:, Fwd:, etc.)        
        email_groups = {}
        for email in emails:
            # Simple normalization: remove "Re: ", "Fwd: ", "RE: ", "FW: "
            # And strip whitespace
            subject = email.subject.strip()
            norm_subject = subject
            for prefix in ["Re:", "Fwd:", "RE:", "FW:", "re:", "fwd:"]:
                if norm_subject.startswith(prefix):
                    norm_subject = norm_subject[len(prefix):].strip()
            
            # Keep the LATEST email for this subject
            # (emails should already be in order, but we confirm by date)
            if norm_subject not in email_groups:
                email_groups[norm_subject] = email
            else:
                if email.date > email_groups[norm_subject].date:
                    email_groups[norm_subject] = email
        
        sorted_emails = sorted(email_groups.values(), key=lambda x: x.date, reverse=True)
        print(f"Filtered down to {len(sorted_emails)} unique conversations (showing latest only).\n")
        # ---------------------------

        # 3. Interactive Processing
        for i, email in enumerate(sorted_emails, 1):
            print(f"[{i}] From: {email.from_} | Subject: {email.subject}")
            print(f"    Date: {email.date}")
            print(f"    Preview: {email.text[:100]}...")
            
            # Fetch History if sender is known
            history = []
            if Config.TARGET_SENDER and email.from_ == Config.TARGET_SENDER:
                 print("    Fetching conversation history...")
                 history = client.fetch_past_emails(email.from_, limit=5)
                 # Remove current email from history if present (by ID or subject/date)
                 history = [msg for msg in history if msg.date < email.date]

            choice = input("    Generate draft reply? (y/n/q): ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'y':
                print("    Generating draft with AI...")
                reply_body = ai.generate_reply(email.from_, email.subject, email.text, history=history, context=context_data)
                
                if reply_body:
                    if reply_body.strip() == "IGNORE":
                        print("    AI suggested ignoring this email.")
                    else:
                        # Create Draft
                        success = client.create_draft(email.from_, f"Re: {email.subject}", reply_body)
                        if success:
                            print("    [Success] Draft saved to 'Drafts' folder.")
                        else:
                            print("    [Error] Failed to save draft.")
                else:
                    print("    [Error] AI failed to generate reply.")
            
            print("-" * 40)

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        # cleanup
        if 'client' in locals():
            client.disconnect()
        print("=== Done ===")

if __name__ == "__main__":
    main()
