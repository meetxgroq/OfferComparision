#!/usr/bin/env python3
"""
OfferCompare Pro - Local Setup Script
Helps users set up their local development environment quickly
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"🚀 {text}")
    print("="*60)

def print_step(step, text):
    """Print a formatted step."""
    print(f"\n{step}. {text}")

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"   Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"   ✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ {description} failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False

def check_prerequisites():
    """Check if required tools are installed."""
    print_step("1", "Checking Prerequisites")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 10:
        print(f"   ✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} is supported")
    else:
        print(f"   ❌ Python 3.10+ required, found {python_version.major}.{python_version.minor}")
        return False
    
    # Check for conda
    conda_available = shutil.which("conda") is not None
    if conda_available:
        print("   ✅ Conda is available")
    else:
        print("   ⚠️ Conda not found, will use pip instead")
    
    # Check for git
    git_available = shutil.which("git") is not None
    if git_available:
        print("   ✅ Git is available")
    else:
        print("   ⚠️ Git not found, some features may be limited")
    
    return True

def setup_environment():
    """Set up the Python environment."""
    print_step("2", "Setting up Python Environment")
    
    conda_available = shutil.which("conda") is not None
    
    if conda_available:
        print("   Using Conda for environment management...")
        
        # Check if environment exists
        try:
            result = subprocess.run("conda env list | grep offercompare-pro", 
                                  shell=True, capture_output=True, text=True)
            if "offercompare-pro" in result.stdout:
                print("   📦 Environment 'offercompare-pro' already exists")
                choice = input("   Do you want to recreate it? (y/n): ").lower()
                if choice == 'y':
                    run_command("conda env remove -n offercompare-pro -y", "Environment removal")
                else:
                    return True
        except:
            pass
        
        # Create environment from yml file
        if os.path.exists("environment.yml"):
            return run_command("conda env create -f environment.yml", "Conda environment creation")
        else:
            print("   ❌ environment.yml not found")
            return False
    else:
        print("   Using pip for package management...")
        
        # Create virtual environment
        if not os.path.exists("venv"):
            run_command("python -m venv venv", "Virtual environment creation")
        
        # Activate and install packages
        if os.name == 'nt':  # Windows
            activate_cmd = "venv\\Scripts\\activate && pip install -r requirements.txt"
        else:  # Unix/Linux/macOS
            activate_cmd = "source venv/bin/activate && pip install -r requirements.txt"
        
        return run_command(activate_cmd, "Package installation")

def setup_environment_file():
    """Set up the .env file."""
    print_step("3", "Setting up Environment Configuration")
    
    if os.path.exists(".env"):
        print("   📄 .env file already exists")
        choice = input("   Do you want to reconfigure it? (y/n): ").lower()
        if choice != 'y':
            return True
    
    if not os.path.exists(".env.example"):
        print("   ❌ .env.example not found")
        return False
    
    # Copy example file
    shutil.copy(".env.example", ".env")
    print("   ✅ Created .env file from .env.example")
    
    print("\n   🔑 API Key Configuration:")
    print("   Please edit the .env file and add your API keys:")
    print("   - For Google Gemini: https://aistudio.google.com/app/apikey")
    print("   - For OpenAI: https://platform.openai.com/api-keys")
    print("   - For Claude: https://console.anthropic.com/")
    
    # Interactive setup
    setup_interactive = input("\n   Do you want to set up API keys now? (y/n): ").lower()
    if setup_interactive == 'y':
        setup_api_keys_interactive()
    
    return True

def setup_api_keys_interactive():
    """Interactive API key setup."""
    print("\n   🔧 Interactive API Key Setup:")
    print("   (Press Enter to skip any provider)")
    
    env_content = []
    
    # Read existing .env
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.readlines()
    
    # API key prompts
    api_keys = {
        "GEMINI_API_KEY": "Google Gemini API Key",
        "OPENAI_API_KEY": "OpenAI API Key", 
        "ANTHROPIC_API_KEY": "Anthropic Claude API Key"
    }
    
    updated_content = []
    for line in env_content:
        key_updated = False
        for env_key, description in api_keys.items():
            if line.startswith(f"{env_key}="):
                api_key = input(f"   Enter {description}: ").strip()
                if api_key:
                    updated_content.append(f"{env_key}={api_key}\n")
                    print(f"   ✅ {env_key} configured")
                else:
                    updated_content.append(line)
                    print(f"   ⏭️ {env_key} skipped")
                key_updated = True
                break
        
        if not key_updated:
            updated_content.append(line)
    
    # Write updated .env
    with open(".env", "w") as f:
        f.writelines(updated_content)

def test_installation():
    """Test the installation."""
    print_step("4", "Testing Installation")
    
    conda_available = shutil.which("conda") is not None
    
    if conda_available:
        # Create a simple test script for conda environment
        test_script = """
import sys
print('   Testing utility imports...')
try:
    from utils.call_llm import get_provider_info
    from utils.col_calculator import get_cost_index
    from utils.market_data import get_market_salary_range
    from utils.company_db import get_company_data
    
    provider_info = get_provider_info()
    available_providers = provider_info.get('available_providers', [])
    
    if available_providers:
        providers_str = ', '.join(available_providers)
        print(f'   ✅ Available AI providers: {providers_str}')
        default_provider = provider_info.get('default_provider', 'None')
        print(f'   ✅ Default provider: {default_provider}')
    else:
        print('   ⚠️ No AI providers configured. Please add API keys to .env file.')
    
    print('   ✅ All core utilities imported successfully')
except Exception as e:
    print(f'   ❌ Error: {e}')
    sys.exit(1)
"""
        
        # Write test script to file
        with open("test_setup.py", "w") as f:
            f.write(test_script)
        
        try:
            print("   Testing in conda environment...")
            result = subprocess.run("conda run -n offercompare-pro python test_setup.py", 
                                  shell=True, check=True, capture_output=True, text=True)
            print(result.stdout)
            
            # Clean up test script
            os.remove("test_setup.py")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Test failed: {e}")
            print(f"   Error output: {e.stderr}")
            # Clean up test script
            if os.path.exists("test_setup.py"):
                os.remove("test_setup.py")
            return False
    else:
        # Test in virtual environment
        try:
            # Test utility imports
            print("   Testing utility imports...")
            from utils.call_llm import get_provider_info
            
            provider_info = get_provider_info()
            available_providers = provider_info.get("available_providers", [])
            
            if available_providers:
                print(f"   ✅ Available AI providers: {', '.join(available_providers)}")
                print(f"   ✅ Default provider: {provider_info.get('default_provider', 'None')}")
            else:
                print("   ⚠️ No AI providers configured. Please add API keys to .env file.")
            
            # Test basic functionality
            print("   Testing core utilities...")
            from utils.col_calculator import get_cost_index
            from utils.market_data import get_market_salary_range
            from utils.company_db import get_company_data
            
            print("   ✅ All core utilities imported successfully")
            
            return True
            
        except ImportError as e:
            print(f"   ❌ Import error: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Test error: {e}")
            return False

def print_next_steps():
    """Print next steps for the user."""
    print_step("5", "Next Steps")
    
    conda_available = shutil.which("conda") is not None
    
    if conda_available:
        print("   To activate the environment:")
        print("   conda activate offercompare-pro")
        print("\n   Or run directly without activation:")
        print("   conda run -n offercompare-pro python main.py")
    else:
        if os.name == 'nt':  # Windows
            print("   To activate the environment:")
            print("   venv\\Scripts\\activate")
        else:  # Unix/Linux/macOS
            print("   To activate the environment:")
            print("   source venv/bin/activate")
    
    print("\n   To run OfferCompare Pro:")
    print("   python main.py")
    
    print("\n   To test individual components:")
    print("   python main.py  # Select option 4: Test Utilities")
    
    print("\n   For help and documentation:")
    print("   python main.py  # Select option 3: Help & Documentation")

def main():
    """Main setup function."""
    print_header("OFFERCOMPARE PRO - LOCAL SETUP")
    print("Welcome! This script will help you set up OfferCompare Pro locally.")
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("❌ Please run this script from the OfferCompare project directory.")
        sys.exit(1)
    
    try:
        # Run setup steps
        if not check_prerequisites():
            print("❌ Prerequisites check failed. Please install required tools.")
            sys.exit(1)
        
        if not setup_environment():
            print("❌ Environment setup failed.")
            sys.exit(1)
        
        if not setup_environment_file():
            print("❌ Environment file setup failed.")
            sys.exit(1)
        
        if not test_installation():
            print("❌ Installation test failed.")
            sys.exit(1)
        
        print_next_steps()
        
        print_header("SETUP COMPLETE! 🎉")
        print("OfferCompare Pro is ready to use!")
        print("Run 'python main.py' to get started.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 