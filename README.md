# Image Background Transformer 🎨

A powerful Python tool for automatically removing backgrounds from images and replacing them with professional backgrounds while maintaining image quality and dimensions.

Perfect for e-commerce product photography, automotive listings, or any scenario where you need consistent, professional backgrounds.

## ✨ Features

- 🤖 **AI-Powered Background Removal** - Uses state-of-the-art U-2-Net deep learning model
- 🖼️ **Custom Background Replacement** - Replace with your own backgrounds or use default studio background
- 📏 **Quality Preservation** - Maintains original image dimensions and quality
- ⚡ **Batch Processing** - Process multiple images at once with progress tracking
- 🎯 **Multiple AI Models** - Choose from different models optimized for various subjects
- 🎨 **Flexible Output** - Supports JPEG, PNG, and WEBP formats
- 📊 **Detailed Logging** - Track processing with colorful console output and log files
- ⚙️ **Highly Configurable** - YAML-based configuration with CLI overrides

## 📋 Requirements

- Python 3.8 or higher
- ~200 MB disk space for AI models (downloaded automatically on first run)
- Sufficient RAM based on image sizes (recommended: 4GB+ for 4K images)

## 🚀 Installation

### Step 1: Clone or Download the Project

```bash
cd /path/to/Image-transformer
```

### Step 2: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The first run will automatically download the AI model (~176 MB). This is a one-time process.

## 📁 Project Structure

```
Image-transformer/
├── main.py                     # Main entry point
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── PRD.md                      # Product requirements document
├── src/
│   ├── __init__.py
│   ├── background_remover.py  # AI background removal
│   ├── background_replacer.py # Background replacement logic
│   ├── image_processor.py     # Main processing pipeline
│   └── utils.py               # Utility functions
├── input/                     # Place your images here
├── output/                    # Processed images go here
├── backgrounds/               # Background images
│   └── default_bg.jpeg        # Default background
├── images/                    # Example images
│   ├── raw.jpeg              # Example input
│   ├── output.jpeg           # Example output
│   └── sample_bg.jpeg        # Sample background
└── logs/                      # Processing logs
    └── processing.log
```

## 💡 Quick Start

### 1. Prepare Your Images

```bash
# Copy your images to the input folder
cp /path/to/your/images/*.jpg input/
```

### 2. (Optional) Add Custom Background

```bash
# Copy your custom background to backgrounds folder
cp /path/to/background.jpg backgrounds/
```

Edit `config.yaml` to use your background:
```yaml
default_background: "./backgrounds/your_background.jpg"
```

### 3. Run the Tool

**Ensure virtual environment is activated:**
```bash
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

**Run with default settings:**
```bash
python main.py
```

**That's it!** Check the `output/` folder for your processed images.

## 🎯 Usage Examples

### Basic Usage

```bash
# Process all images in input/ folder with default settings
python main.py
```

### Custom Configuration

```bash
# Use a different config file
python main.py --config my_config.yaml

# Override input/output folders
python main.py --input ./my_photos --output ./processed

# Use a specific background image
python main.py --background ./backgrounds/studio_white.jpg

# Use a different AI model (faster but less accurate)
python main.py --model u2netp

# Set output quality
python main.py --quality 85

# Enable verbose logging
python main.py --verbose
```

### Combining Options

```bash
python main.py \
  --input ./car_photos \
  --output ./processed_cars \
  --background ./backgrounds/garage.jpg \
  --quality 95 \
  --verbose
```

## ⚙️ Configuration

Edit `config.yaml` to customize behavior:

```yaml
# Input/Output
input_folder: "./input"
output_folder: "./output"
default_background: "./backgrounds/default_bg.jpeg"

# Output Settings
output_format: "JPEG"           # JPEG, PNG, or WEBP
output_quality: 95              # 1-100 (higher = better quality)
preserve_original_format: false # Keep original format

# AI Model Selection
model: "u2net"                  # Options:
                                # - u2net: Most accurate (slower)
                                # - u2netp: Faster, less accurate
                                # - u2net_human_seg: For people
                                # - u2net_cloth_seg: For clothing

# Processing Options
add_shadow: false               # Add shadow effect (experimental)
center_subject: true            # Center subject on background
skip_existing: true             # Skip already processed files
continue_on_error: true         # Keep going if one file fails

# Logging
log_level: "INFO"               # DEBUG, INFO, WARNING, ERROR
log_file: "./logs/processing.log"
```

## 🎨 AI Models

Choose the right model for your use case:

| Model | Best For | Speed | Accuracy |
|-------|----------|-------|----------|
| `u2net` | General purpose, vehicles, products | Slower | Highest |
| `u2netp` | When speed matters | Faster | Good |
| `u2net_human_seg` | People, portraits | Medium | High for humans |
| `u2net_cloth_seg` | Clothing, fashion items | Medium | High for clothing |

## 📊 Sample Output

```
==================================================
Image Background Transformer
==================================================

Input folder:  ./input
Output folder: ./output
Found 3 image(s) to process

Processing: 100%|████████████| 3/3 [00:12<00:00,  4.2s/image]
[1/3] ✓ car_001.jpg (3.2s)
[2/3] ✓ car_002.jpg (4.5s)
[3/3] ✓ car_003.jpg (3.8s)

==================================================
Processing Complete!
==================================================

Total images:  3
Successful:    3
Failed:        0
Total time:    11.5s
Average time:  3.8s per image

Output saved to: ./output
```

## 🐛 Troubleshooting

### "No module named 'rembg'"

**Solution:** Make sure virtual environment is activated:
```bash
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### "No images found in input folder"

**Solution:** 
1. Ensure images are in the `input/` folder
2. Check supported formats: JPEG, PNG, WEBP, BMP
3. Verify file extensions are lowercase or uppercase (both work)

### Model Download Fails

**Solution:**
1. Check internet connection
2. Models are downloaded from GitHub - ensure access
3. Try manually downloading from: https://github.com/danielgatis/rembg

### Memory Error with Large Images

**Solution:**
1. Resize images before processing
2. Use `u2netp` model (lighter weight)
3. Process fewer images at once
4. Increase system RAM if possible

### Poor Background Removal Quality

**Solution:**
1. Try different models (`u2net` is most accurate)
2. Ensure input images have clear subject/background separation
3. Check that images are well-lit and in focus
4. For specific subjects, use specialized models (human_seg, cloth_seg)

## 🔧 Advanced Usage

### Processing Specific File Types

Edit `config.yaml` or modify `src/utils.py::get_image_files()` to support additional formats.

### Custom Background Gradient

The tool creates a default gray gradient background if none is specified. Customize in `src/image_processor.py::_create_default_background()`.

### Adding Shadow Effects

Enable in config:
```yaml
add_shadow: true
```

Note: This is experimental and may need tuning for your specific images.

## 📝 Example Workflow

**E-commerce Product Photography:**

1. Take photos of products with any background
2. Place all images in `input/` folder
3. Add your brand's background to `backgrounds/`
4. Configure `config.yaml` with your brand settings
5. Run: `python main.py`
6. Upload processed images from `output/` to your store

**Automotive Listings:**

The example images show a car with open boot being transformed from a garage setting to a professional studio background - perfect for dealership listings.

## 🤝 Contributing

This is a standalone tool. Feel free to fork and customize for your needs.

## 📄 License

This project uses open-source libraries:
- `rembg` - Licensed under MIT
- `Pillow` - Licensed under HPND
- `OpenCV` - Licensed under Apache 2.0

## 🙏 Acknowledgments

- Background removal powered by [rembg](https://github.com/danielgatis/rembg)
- U-2-Net model by Xuebin Qin et al.

## 📮 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `logs/processing.log` for detailed error messages
3. Ensure all dependencies are correctly installed
4. Verify Python version (3.8+)

## 🎉 Tips for Best Results

1. **Good Lighting**: Well-lit images with clear subject/background separation
2. **High Resolution**: Higher quality inputs = better outputs
3. **Clean Edges**: Avoid motion blur or out-of-focus edges
4. **Consistent Backgrounds**: Use the same background image for all products in a set
5. **Test Settings**: Try different models and quality settings to find what works best

---

**Happy Processing!** 🚀

When done, remember to deactivate your virtual environment:
```bash
deactivate
```
