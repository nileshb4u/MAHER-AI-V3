"""
Quick verification script to check OCR installation on Windows
"""

print("Checking EasyOCR installation...")
print("=" * 60)

try:
    import easyocr
    print("✓ EasyOCR is installed!")
    print(f"  Version: {easyocr.__version__}")
    EASYOCR_OK = True
except ImportError as e:
    print(f"✗ EasyOCR not found: {e}")
    EASYOCR_OK = False

try:
    import torch
    print("✓ PyTorch is installed!")
    print(f"  Version: {torch.__version__}")
    TORCH_OK = True
except ImportError as e:
    print(f"✗ PyTorch not found: {e}")
    TORCH_OK = False

try:
    import torchvision
    print("✓ TorchVision is installed!")
    print(f"  Version: {torchvision.__version__}")
    VISION_OK = True
except ImportError as e:
    print(f"✗ TorchVision not found: {e}")
    VISION_OK = False

print("\n" + "=" * 60)

if EASYOCR_OK and TORCH_OK and VISION_OK:
    print("✓✓✓ ALL DEPENDENCIES INSTALLED ✓✓✓")
    print("\nTesting OCR functionality...")

    try:
        from tools.ocr_effocr import get_ocr_info
        info = get_ocr_info()

        print("\nOCR Engine Status:")
        for engine, details in info["available_engines"].items():
            status = "✓ Ready" if details["available"] else "✗ Not available"
            print(f"  {engine}: {status}")

        if info["available_engines"]["easyocr"]["available"]:
            print("\n🎉 SUCCESS! OCR is ready to use!")
            print("\nYou can now:")
            print("  - OCR images: ocr_image_local()")
            print("  - OCR PDFs: ocr_pdf_local()")
            print("  - Extract text from scanned docs")
        else:
            print("\n⚠️ OCR engines detected but not initialized")

    except Exception as e:
        print(f"\n⚠️ Error testing OCR: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗✗✗ MISSING DEPENDENCIES ✗✗✗")
    print("\nInstall with:")
    print("  pip install easyocr torch torchvision")

print("=" * 60)
