#!/usr/bin/env python3
"""
Setup script for EDC Voice Agent
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_env_file():
    """Create .env file with user input"""
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists")
        overwrite = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Skipping .env file creation")
            return True
    
    print("\n🔧 Setting up environment variables...")
    
    env_content = []
    
    # Twilio Configuration
    print("\n--- Twilio Configuration ---")
    account_sid = input("Enter your Twilio Account SID: ").strip()
    auth_token = input("Enter your Twilio Auth Token: ").strip()
    phone_number = input("Enter your Twilio Phone Number (with +): ").strip()
    
    env_content.extend([
        f"TWILIO_ACCOUNT_SID={account_sid}",
        f"TWILIO_AUTH_TOKEN={auth_token}",
        f"TWILIO_NUMBER={phone_number}"
    ])
    
    # ElevenLabs Configuration
    print("\n--- ElevenLabs Configuration ---")
    elevenlabs_key = input("Enter your ElevenLabs API Key: ").strip()
    env_content.append(f"ELEVENLABS_API_KEY={elevenlabs_key}")
    
    # Base URL
    print("\n--- Application Configuration ---")
    print("Note: You'll need to update this after starting ngrok")
    base_url = input("Enter your base URL (or press Enter for localhost): ").strip()
    if not base_url:
        base_url = "http://localhost:5000"
    env_content.append(f"BASE_URL={base_url}")
    
    # Write .env file
    try:
        with open(".env", "w") as f:
            f.write("\n".join(env_content))
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def create_static_directory():
    """Create static directory if it doesn't exist"""
    static_dir = Path("static")
    if not static_dir.exists():
        try:
            static_dir.mkdir()
            print("✅ Created static directory")
        except Exception as e:
            print(f"❌ Failed to create static directory: {e}")
            return False
    else:
        print("✅ Static directory already exists")
    return True

def test_environment():
    """Test if environment variables are set correctly"""
    print("\n🧪 Testing environment configuration...")
    
    required_vars = [
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN', 
        'TWILIO_NUMBER',
        'ELEVENLABS_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def main():
    """Main setup function"""
    print("🚀 EDC Voice Agent Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create static directory
    if not create_static_directory():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️  python-dotenv not available, skipping environment test")
    else:
        if not test_environment():
            print("\n⚠️  Environment test failed. Please check your .env file.")
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Start your application: python app.py")
    print("2. In another terminal, start ngrok: ngrok http 5000")
    print("3. Update BASE_URL in .env with your ngrok URL")
    print("4. Configure your Twilio webhook URLs")
    print("5. Test with: python test_outbound_call.py")
    
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()

