# MAHER AI - Branding Images

This folder contains placeholder images for MAHER AI branding. Replace these with your actual photos to complete the branding.

## 📸 Images to Replace

### 1. **MAHER Logo (Face Shot)**
**File:** `maher-logo-placeholder.svg`
**Replace with:** Your actual MAHER AI face/head photo

**Requirements:**
- **Format:** PNG, JPG, or SVG (PNG recommended for photos)
- **Size:** 200x200 pixels minimum (square/circular crop works best)
- **Background:** Transparent background preferred (PNG with alpha channel)
- **Naming:** Replace the file with same name: `maher-logo.png` or `maher-logo.jpg`

**Where it's used:**
- Landing page header (circular logo above "MAHER AI" title)
- Shows as a 96x96px circular image with orange border and glow effect

**How to replace:**
1. Prepare your MAHER face photo (square crop, transparent background ideal)
2. Name it: `maher-logo.png` or `maher-logo.jpg`
3. Place it in this folder: `public/images/`
4. Update Landing.tsx line 72-73:
   ```tsx
   src="/images/maher-logo.png"  // or .jpg
   ```

---

### 2. **MAHER Robot (Knee-Up)**
**File:** `maher-robot-placeholder.svg`
**Replace with:** Your actual MAHER AI humanoid robot photo (knee-up shot)

**Requirements:**
- **Format:** PNG with transparent background (recommended) or JPG
- **Size:** 400px width minimum, height proportional to knee-up shot
- **Background:** Transparent preferred for floating effect
- **Orientation:** Vertical/portrait (robot standing, visible from knees up)
- **Naming:** Replace the file: `maher-robot.png` or `maher-robot.jpg`

**Where it's used:**
- Landing page background (floating on right side on desktop)
- Shows at ~600px height with subtle opacity and glow effect
- Mobile: Smaller version shown centered at 192px height

**How to replace:**
1. Prepare your MAHER robot photo (knee-up, transparent background ideal)
2. Name it: `maher-robot.png` or `maher-robot.jpg`
3. Place it in this folder: `public/images/`
4. Update Landing.tsx lines 58, 85:
   ```tsx
   src="/images/maher-robot.png"  // or .jpg
   ```

---

## 🎨 Visual Effects Applied

Both images have CSS effects applied for brand consistency:

### Logo Effects:
- Circular crop with 4px orange border
- Glow effect (shadow) in brand orange color
- Hover effect: Brighter border and stronger glow
- Subtle blur glow background

### Robot Effects:
- Drop shadow with orange tint
- Low opacity (20%) for subtle background presence
- Hover effect: Increased opacity (40%)
- Desktop: Floating on right side, full height (600px)
- Mobile: Centered, smaller (192px height)

---

## 📁 Folder Structure

```
public/
└── images/
    ├── README.md (this file)
    ├── maher-logo-placeholder.svg (REPLACE ME)
    ├── maher-robot-placeholder.svg (REPLACE ME)
    ├── maher-logo.png (YOUR FILE - add this)
    └── maher-robot.png (YOUR FILE - add this)
```

---

## ✅ Quick Replacement Checklist

- [ ] 1. Prepare MAHER face photo (square, transparent background)
- [ ] 2. Save as `maher-logo.png` in `public/images/`
- [ ] 3. Update `components/Landing.tsx` line 72 to use new filename
- [ ] 4. Prepare MAHER robot photo (knee-up, transparent background)
- [ ] 5. Save as `maher-robot.png` in `public/images/`
- [ ] 6. Update `components/Landing.tsx` lines 58 and 85 to use new filename
- [ ] 7. Rebuild frontend: `npm run build`
- [ ] 8. Restart server and refresh browser
- [ ] 9. Delete placeholder SVG files (optional)

---

## 🖼️ Image Preparation Tips

### For Logo (Face):
- Use Photoshop/GIMP to remove background
- Crop to square (1:1 aspect ratio)
- Save as PNG with transparency
- Recommended size: 300x300px or larger

### For Robot:
- Ensure good lighting and contrast
- Remove background if possible (PNG with alpha)
- Crop to show knees and above
- Keep proportions natural (not stretched)
- Recommended width: 600px or larger

### Tools for Background Removal:
- **Photoshop:** Magic Wand + Layer Mask
- **GIMP:** Free alternative to Photoshop
- **remove.bg:** Online tool (https://www.remove.bg/)
- **Canva:** Free online editor with background removal
- **Photopea:** Free online Photoshop alternative

---

## 🚀 After Replacement

Once you've replaced the images:

1. **Rebuild Frontend:**
   ```bash
   npm run build
   ```

2. **Restart Server:**
   ```bash
   # Windows
   start_server.bat

   # Linux/Mac
   ./start_server.sh
   ```

3. **Clear Browser Cache:**
   - Press Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or clear cache manually in browser settings

4. **Verify:**
   - Navigate to landing page (http://localhost:8080)
   - Check logo appears correctly in circular frame
   - Check robot appears on right side (desktop) or centered (mobile)
   - Test hover effects

---

## 🎨 Brand Colors Reference

If you need to match colors when editing images:

- **Brand Orange:** `#F97316` (RGB: 249, 115, 22)
- **Deep Blue:** `#0F172A` (RGB: 15, 23, 42)
- **Brand Blue:** `#1E3A5F` (RGB: 30, 58, 95)
- **Light Blue:** `#60A5FA` (RGB: 96, 165, 250)

---

## 📞 Need Help?

If images don't display correctly:
1. Check file paths match exactly in Landing.tsx
2. Ensure files are in `public/images/` folder
3. Verify file extensions (.png, .jpg, .svg)
4. Check browser console (F12) for errors
5. Rebuild frontend and hard refresh browser

---

**Last Updated:** 2025-11-12
