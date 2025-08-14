"""Main entry point for the Google Forms integration POC."""

from gforms import GFormsClient
from gforms.config import config

# Add src to Python path for development
# sys.path.insert(0, str(Path(__file__).parent / "src"))


def main() -> None:
    """Manage Google Forms integration."""
    try:
        # Initialize the client
        client = GFormsClient()
        print(client)
        print("Google Forms client initialized successfully")
        print(f"Debug mode: {config.debug}")
        print(f"Log level: {config.log_level}")

        # Example usage (commented out to avoid API calls without valid credentials)
        # form_id = "your_form_id_here"
        # form_data = client.get_form(form_id)
        # print(f"📋 Form title: {form_data.get('info', {}).get('title', 'Unknown')}")

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Make sure to set your GOOGLE_API_KEY in .env file")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
