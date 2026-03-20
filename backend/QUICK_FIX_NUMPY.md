# 🔥 QUICK FIX: NumPy Version Issue

## The Problem

If you see this error:
```
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6...
Failed to initialize NumPy: _ARRAY_API not found
```

## The Solution (30 seconds)

Run this ONE command:

```bash
pip install "numpy<2.0"
```

That's it! This will downgrade NumPy from 2.x to 1.x.

## Verify It Worked

```bash
python check_ocr.py
```

Should now show:
```
✅✅✅ ALL DEPENDENCIES INSTALLED ✅✅✅
🎉 SUCCESS! OCR is ready to use!
```

## Why This Happens

- PyTorch 2.2.0 was compiled with NumPy 1.x
- NumPy 2.0+ changed internal APIs and broke compatibility
- EasyOCR uses PyTorch, so it also needs NumPy < 2.0

## Alternative: Full Reinstall

If the quick fix doesn't work:

```bash
# Remove all related packages
pip uninstall numpy torch torchvision easyocr -y

# Install in correct order
pip install "numpy<2.0,>=1.24.0"
pip install torch==2.2.0 torchvision==0.17.0
pip install easyocr==1.7.1
```

## Confirmation

After fixing, run:

```bash
python -c "import numpy, torch, easyocr; print(f'NumPy: {numpy.__version__} | PyTorch: {torch.__version__} | EasyOCR: {easyocr.__version__}')"
```

Should show:
```
NumPy: 1.26.x | PyTorch: 2.2.0+cpu | EasyOCR: 1.7.1
```

✅ **All set! Your document tools are ready to use!**
