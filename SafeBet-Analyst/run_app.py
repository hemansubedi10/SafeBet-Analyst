# SafeBet Analyst - Quick Start Script
import subprocess
import sys
import os

def main():
    print("🚀 Starting SafeBet Analyst Application...")
    print("\nMake sure you have set your API keys in the .env file or environment variables.")
    print("To set up your API keys, copy .env.example to .env and fill in your values.\n")
    
    try:
        # Run the Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running the application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()