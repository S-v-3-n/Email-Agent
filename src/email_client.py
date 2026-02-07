from imap_tools import MailBox, AND
from email.message import EmailMessage
from .config import Config
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

from .auth import get_access_token

class EmailClient:
    def __init__(self):
        self.user = Config.EMAIL_USER
        self.imap_server = Config.IMAP_SERVER
        self.mailbox = None

    def connect(self):
        """Connect to the IMAP server using OAuth2."""
        try:
            # Get Access Token
            token = get_access_token()
            
            # Connect via XOAUTH2
            # imap-tools >= 0.28 supports xoauth2 method directly
            self.mailbox = MailBox(self.imap_server)
            self.mailbox.xoauth2(self.user, token, initial_folder='INBOX')
            
            logging.info(f"Connected to {self.imap_server} as {self.user} (OAuth)")
        except Exception as e:
            logging.error(f"Failed to connect: {e}")
            raise

    def disconnect(self):
        """Disconnect from the IMAP server."""
        if self.mailbox:
            self.mailbox.logout()
            logging.info("Disconnected from IMAP server")

    def fetch_unread_emails(self, sender_filter=None):
        """Fetch unread emails from the Inbox."""
        if not self.mailbox:
            raise ConnectionError("Not connected to IMAP server")

        try:
            self.mailbox.folder.set('INBOX')
            
            # Build criteria
            criteria = AND(seen=False)
            if sender_filter:
                criteria = AND(seen=False, from_=sender_filter)
                logging.info(f"Filtering for sender: {sender_filter}")

            # Fetch unread emails
            msgs = [msg for msg in self.mailbox.fetch(criteria, mark_seen=False)]
            logging.info(f"Found {len(msgs)} unread emails matching criteria")
            return msgs
        except Exception as e:
            logging.error(f"Error fetching emails: {e}")
            return []

    def fetch_past_emails(self, sender, limit=5):
        """Fetch the last N emails from a specific sender (read or unread)."""
        if not self.mailbox:
            raise ConnectionError("Not connected")
            
        try:
            self.mailbox.folder.set('INBOX')
            criteria = AND(from_=sender)
            # reverse=True to get newest first
            msgs = [msg for msg in self.mailbox.fetch(criteria, limit=limit, reverse=True)]
            # Reverse back to chronological order
            return list(reversed(msgs))
        except Exception as e:
            logging.error(f"Error fetching history: {e}")
            return []

    def create_draft(self, to_email, subject, body):
        """Save a draft email to the Drafts folder."""
        if not self.mailbox:
            raise ConnectionError("Not connected to IMAP server")

        try:
            # Create the email message
            msg = EmailMessage()
            msg["From"] = self.user
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(body)

            # Convert to bytes
            msg_bytes = bytes(msg)

            # Append to Drafts folder
            # Note: Folder name might vary (e.g., "Drafts", "Sent Items")
            # Outlook usually uses "Drafts"
            # We can verify folder names with mailbox.folder.list() if this fails
            
            # Use flag_set to minimize issues. \Seen and \Draft are common.
            # \Seen makes it not bold (read). \Draft marks it as a draft.
            self.mailbox.append(msg_bytes, 'Drafts', flag_set=['\\Seen', '\\Draft'])
            logging.info(f"Draft saved for {to_email}: {subject}")
            return True
        except Exception as e:
            logging.error(f"Failed to create draft: {e}")
            return False

    def list_folders(self):
        """Helper to list available folders."""
        if not self.mailbox:
             raise ConnectionError("Not connected")
        return self.mailbox.folder.list()

if __name__ == "__main__":
    # Test execution
    client = EmailClient()
    try:
        client.connect()
        folders = client.list_folders()
        print("Available folders:", [f.name for f in folders])
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if client.mailbox:
            client.disconnect()
