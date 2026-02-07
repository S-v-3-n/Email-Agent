from imap_tools import MailBox
import getpass

def test_connection():
    email = input("Enter your email: ").strip()
    password = getpass.getpass("Enter your App Password: ").strip()
    
    server = "outlook.office365.com"
    print(f"\nAttempting to connect to {server}...")
    
    try:
        with MailBox(server).login(email, password) as mailbox:
            print("SUCCESS! Connected successfully.")
            print(f"Inbox has {mailbox.folder.get()['total']} messages.")
    except Exception as e:
        print(f"\nFAILURE: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure you are using an APP PASSWORD, not your login password.")
        print("2. Ensure IMAP is enabled in Outlook Settings > Mail > Sync email.")

if __name__ == "__main__":
    test_connection()
