"""
Diagnose torch installation issues on Windows
"""

import sys
import subprocess

print("=" * 60)
print("TORCH INSTALLATION DIAGNOSTIC")
print("=" * 60)

# Check what torch package is installed
print("\n1. Checking installed 'torch' package...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "list"],
    capture_output=True,
    text=True
)

torch_lines = [line for line in result.stdout.split('\n') if 'torch' in line.lower()]
print("Found packages:")
for line in torch_lines:
    print(f"  {line}")

# Try to import torch
print("\n2. Testing torch import...")
try:
    import torch as torch_test
    print(f"✓ torch imported successfully")
    print(f"  Module location: {torch_test.__file__}")

    # Check if it has __version__
    if hasattr(torch_test, '__version__'):
        print(f"  Version: {torch_test.__version__}")
    else:
        print("  ⚠️ No __version__ attribute - this might not be PyTorch!")

    # Check if it has cuda (PyTorch specific)
    if hasattr(torch_test, 'cuda'):
        print(f"  ✓ Has CUDA support (this is PyTorch)")
    else:
        print(f"  ✗ No CUDA attribute - this is NOT PyTorch!")
        print(f"  This appears to be a different 'torch' package")

except ImportError as e:
    print(f"✗ Failed to import torch: {e}")

# Try to import the correct PyTorch
print("\n3. Attempting to import PyTorch specifically...")
try:
    import torch.nn as nn
    print("✓ PyTorch neural network module imported - PyTorch is installed!")
except Exception as e:
    print(f"✗ PyTorch not properly installed: {e}")
    print("\nRECOMMENDATION:")
    print("Uninstall the wrong 'torch' package and install PyTorch:")
    print("  pip uninstall torch")
    print("  pip install torch torchvision")

# Check EasyOCR
print("\n4. Checking EasyOCR...")
try:
    import easyocr
    print("✓ EasyOCR imported successfully")
    if hasattr(easyocr, '__version__'):
        print(f"  Version: {easyocr.__version__}")
except ImportError as e:
    print(f"✗ EasyOCR not found: {e}")

print("\n" + "=" * 60)
print("SOLUTION:")
print("=" * 60)
print("If you see 'this is NOT PyTorch' above, run:")
print("  pip uninstall torch")
print("  pip install torch==2.2.0 torchvision==0.17.0")
print("  pip install easyocr")
print("=" * 60)
