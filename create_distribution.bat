@echo off
echo 🌸 Creating BlossomTag Distribution Package 🌸
echo.

REM Create distribution folder
if not exist "BlossomTag_Distribution" mkdir BlossomTag_Distribution
cd BlossomTag_Distribution

REM Copy the executable
if exist "..\dist\BlossomTag.exe" (
    copy "..\dist\BlossomTag.exe" "BlossomTag.exe"
    echo ✅ Copied BlossomTag.exe
) else (
    echo ❌ BlossomTag.exe not found! Run build_blossomtag.bat first.
    pause
    exit /b 1
)

REM Create user documentation
echo Creating user documentation...

REM Create README.md for users
echo # BlossomTag - Beautiful PDF Annotation Tool 🌸 > README.md
echo. >> README.md
echo A powerful, user-friendly PDF annotation tool that makes highlighting and tagging documents a breeze! >> README.md
echo. >> README.md
echo ## ✨ Features >> README.md
echo. >> README.md
echo - 🎨 **20 Beautiful Colors** - From hot pink to gold, choose the perfect highlight color >> README.md
echo - 📝 **Smart Tagging** - Add titles, descriptions, and notes to your highlights >> README.md
echo - 🔍 **Tag Search** - Quickly find any tag by typing in the search box >> README.md
echo - 💾 **Preset System** - Save your favorite tag setups and apply them with a double-click >> README.md
echo - 🖴 **High-Quality Export** - Export annotated PDFs with beautiful annotations and highlights >> README.md
echo - 📑 **Sidebar Navigation** - See all your tags at a glance and jump to any page >> README.md
echo - 💡 **Auto-Save** - Never lose your work with automatic saving >> README.md
echo - 🚀 **No Installation Required** - Just double-click and start annotating! >> README.md
echo. >> README.md
echo ## 🚀 Quick Start >> README.md
echo. >> README.md
echo 1. **Double-click BlossomTag.exe** to launch >> README.md
echo 2. **Click "📂 Open PDF"** to load your document >> README.md
echo 3. **Select text** by dragging over it >> README.md
echo 4. **Choose a preset** or create a new tag >> README.md
echo 5. **Click "🖴 Export Final PDF"** when done >> README.md
echo. >> README.md
echo ## 🎯 Pro Tips >> README.md
echo. >> README.md
echo - **Double-click presets** for instant tagging ^(no Save button needed^) >> README.md
echo - **Use the search box** to find tags like "alex" across all pages >> README.md
echo - **Click the Tags button** to keep the sidebar open >> README.md
echo - **Create presets** for repeated annotations ^(character names, themes, etc.^) >> README.md
echo - **Right-click tags** in the sidebar for edit/delete options >> README.md
echo. >> README.md
echo ## 🛡️ Antivirus Notice >> README.md
echo. >> README.md
echo Some antivirus software may flag this as suspicious because: >> README.md
echo - It's packaged with PyInstaller ^(common for Python apps^) >> README.md
echo - It reads and writes PDF files >> README.md
echo - It's not digitally signed ^(costs money we don't have!^) >> README.md
echo. >> README.md
echo **This is a FALSE POSITIVE.** The app is completely safe and open-source. >> README.md
echo. >> README.md
echo If your antivirus blocks it: >> README.md
echo 1. Click "More info" or "Details" >> README.md
echo 2. Click "Run anyway" or "Allow" >> README.md
echo 3. Add to your antivirus whitelist if needed >> README.md
echo. >> README.md
echo You can verify safety at virustotal.com by uploading the exe file. >> README.md
echo. >> README.md
echo ## 🎨 Available Colors >> README.md
echo. >> README.md
echo Hot Pink • Lavender • Purple • Plum • Orchid • Violet • Yellow • Red >> README.md
echo Green • Blue • Teal • Orange • Mint • Slate • Coral • Lime • Sky • Rose • Gold >> README.md
echo. >> README.md
echo ## 💝 Made with Love >> README.md
echo. >> README.md
echo Created for beautiful, efficient PDF annotation. Perfect for students, researchers, >> README.md
echo book clubs, and anyone who loves to highlight and organize their reading! >> README.md
echo. >> README.md

echo ✅ Created README.md

REM Create Quick Start Guide
echo Creating Quick Start Guide...
echo # BlossomTag Quick Start Guide 🚀 > QUICK_START.md
echo. >> QUICK_START.md
echo ## Getting Started in 2 Minutes >> QUICK_START.md
echo. >> QUICK_START.md
echo ### Step 1: Open Your PDF >> QUICK_START.md
echo 1. Double-click **BlossomTag.exe** >> QUICK_START.md
echo 2. Click the **📂 Open PDF** button >> QUICK_START.md
echo 3. Choose your PDF file >> QUICK_START.md
echo. >> QUICK_START.md
echo ### Step 2: Create Your First Highlight >> QUICK_START.md
echo 1. **Drag to select** any text on the page >> QUICK_START.md
echo 2. A dialog will appear with presets on the left >> QUICK_START.md
echo 3. **Either:** >> QUICK_START.md
echo    - Double-click a preset for instant tagging >> QUICK_START.md
echo    - Fill out the form and click "Save Tag" >> QUICK_START.md
echo. >> QUICK_START.md
echo ### Step 3: Manage Your Tags >> QUICK_START.md
echo 1. Click **📑 Tags** to open the sidebar >> QUICK_START.md
echo 2. Use the **🔍 Search** box to find specific tags >> QUICK_START.md
echo 3. Double-click any tag to jump to that page >> QUICK_START.md
echo. >> QUICK_START.md
echo ### Step 4: Create Presets >> QUICK_START.md
echo 1. Click **🎨 Preset Manager** in the toolbar >> QUICK_START.md
echo 2. Fill out the form with your preset details >> QUICK_START.md
echo 3. Click **💾 Save Preset** >> QUICK_START.md
echo 4. Now you can double-click it for instant tagging! >> QUICK_START.md
echo. >> QUICK_START.md
echo ### Step 5: Export Your Annotated PDF >> QUICK_START.md
echo 1. Click **🖴 Export Final PDF** >> QUICK_START.md
echo 2. Choose where to save your annotated PDF >> QUICK_START.md
echo 3. Your PDF will include highlights AND annotation bubbles! >> QUICK_START.md
echo. >> QUICK_START.md
echo ## 🎯 Power User Tips >> QUICK_START.md
echo. >> QUICK_START.md
echo - **Ctrl+Scroll**: Zoom in/out >> QUICK_START.md
echo - **Search tags**: Type "alex" to find all tags with "alex" in them >> QUICK_START.md
echo - **Right-click tags**: Edit or delete existing tags >> QUICK_START.md
echo - **Auto-save**: Your work saves automatically every 30 seconds >> QUICK_START.md
echo - **Color coding**: Use different colors for different types of annotations >> QUICK_START.md
echo. >> QUICK_START.md
echo **That's it! You're ready to annotate like a pro! 🌸** >> QUICK_START.md

echo ✅ Created QUICK_START.md

REM Create troubleshooting guide
echo Creating Troubleshooting Guide...
echo # BlossomTag Troubleshooting 🔧 > TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ## Common Issues and Solutions >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ### 🛡️ Antivirus Blocking the App >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Problem:** Windows Defender or antivirus software blocks BlossomTag.exe >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Solution:** >> TROUBLESHOOTING.md
echo 1. Click "More info" in the Windows warning >> TROUBLESHOOTING.md
echo 2. Click "Run anyway" >> TROUBLESHOOTING.md
echo 3. Add BlossomTag.exe to your antivirus whitelist >> TROUBLESHOOTING.md
echo 4. Verify safety at virustotal.com if concerned >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ### 📄 PDF Won't Open >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Problem:** PDF file fails to load >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Solutions:** >> TROUBLESHOOTING.md
echo - Make sure the PDF isn't password-protected >> TROUBLESHOOTING.md
echo - Try opening the PDF in another program first >> TROUBLESHOOTING.md
echo - Check if the file is corrupted >> TROUBLESHOOTING.md
echo - Make sure you have enough disk space >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ### 🎨 Highlighting Not Working >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Problem:** Can't select text or create highlights >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Solutions:** >> TROUBLESHOOTING.md
echo - Make sure you're dragging to select text ^(not just clicking^) >> TROUBLESHOOTING.md
echo - Try selecting a larger area of text >> TROUBLESHOOTING.md
echo - Some PDFs have text as images - these can't be highlighted >> TROUBLESHOOTING.md
echo - Check if the PDF has text selection restrictions >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ### 💾 Export Problems >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Problem:** Export fails or produces broken PDF >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Solutions:** >> TROUBLESHOOTING.md
echo - Choose a different save location ^(like Desktop^) >> TROUBLESHOOTING.md
echo - Make sure you have write permissions to the folder >> TROUBLESHOOTING.md
echo - Close other PDF programs that might be using the file >> TROUBLESHOOTING.md
echo - Try a shorter filename without special characters >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ### 🔍 Search Not Finding Tags >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Problem:** Tag search returns no results >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Solutions:** >> TROUBLESHOOTING.md
echo - Make sure you've created tags first >> TROUBLESHOOTING.md
echo - Search matches title and description text >> TROUBLESHOOTING.md
echo - Try searching for partial words >> TROUBLESHOOTING.md
echo - Check spelling in your search term >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ### 🖥️ App Crashes or Freezes >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Problem:** BlossomTag stops responding >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Solutions:** >> TROUBLESHOOTING.md
echo - Restart the application >> TROUBLESHOOTING.md
echo - Your work auto-saves every 30 seconds, so you shouldn't lose much >> TROUBLESHOOTING.md
echo - Try opening fewer PDFs at once >> TROUBLESHOOTING.md
echo - Make sure you have enough RAM available >> TROUBLESHOOTING.md
echo - Update your graphics drivers >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ### 📱 High DPI Display Issues >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Problem:** Text or interface looks too small/large >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Solutions:** >> TROUBLESHOOTING.md
echo - Right-click BlossomTag.exe → Properties → Compatibility >> TROUBLESHOOTING.md
echo - Check "Override high DPI scaling behavior" >> TROUBLESHOOTING.md
echo - Set scaling to "Application" >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo ## Still Having Issues? >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo If none of these solutions work: >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo 1. **Check the source code** - BlossomTag is open source >> TROUBLESHOOTING.md
echo 2. **Build from source** - Use the provided build scripts >> TROUBLESHOOTING.md
echo 3. **Check compatibility** - Works on Windows 10/11 >> TROUBLESHOOTING.md
echo. >> TROUBLESHOOTING.md
echo **Remember:** Your annotations are saved as .atnolol files alongside your PDFs, >> TROUBLESHOOTING.md
echo so your work is always safe even if the app has issues! >> TROUBLESHOOTING.md

echo ✅ Created TROUBLESHOOTING.md

REM Create a simple launcher script
echo Creating launcher script...
echo @echo off > START_BlossomTag.bat
echo echo 🌸 Starting BlossomTag... >> START_BlossomTag.bat
echo echo. >> START_BlossomTag.bat
echo echo If you get antivirus warnings, click "More info" then "Run anyway" >> START_BlossomTag.bat
echo echo This is a false positive - the app is completely safe! >> START_BlossomTag.bat
echo echo. >> START_BlossomTag.bat
echo start "" "BlossomTag.exe" >> START_BlossomTag.bat

echo ✅ Created START_BlossomTag.bat

REM Copy antivirus readme
if exist "..\ANTIVIRUS_README.md" (
    copy "..\ANTIVIRUS_README.md" "ANTIVIRUS_README.md"
    echo ✅ Copied ANTIVIRUS_README.md
)

REM Create a version info file
echo BlossomTag v1.0.0 > VERSION.txt
echo Build Date: %date% %time% >> VERSION.txt
echo. >> VERSION.txt
echo Features: >> VERSION.txt
echo - PDF highlighting and annotation >> VERSION.txt
echo - 20 beautiful colors >> VERSION.txt
echo - Preset system with double-click tagging >> VERSION.txt
echo - Tag search functionality >> VERSION.txt
echo - High-quality PDF export >> VERSION.txt
echo - Auto-save every 30 seconds >> VERSION.txt
echo - Sidebar with tag navigation >> VERSION.txt
echo - No installation required >> VERSION.txt

echo ✅ Created VERSION.txt

REM Calculate file sizes
echo. 
echo 📊 Distribution Package Contents:
dir /b

echo.
echo 📦 Package Size:
for %%I in (BlossomTag.exe) do echo BlossomTag.exe: %%~zI bytes

echo.
echo ✅ Distribution package created successfully!
echo.
echo 📁 Your distribution package is ready in: BlossomTag_Distribution\
echo.
echo 🚀 What's included:
echo   • BlossomTag.exe - The main application
echo   • README.md - User documentation  
echo   • QUICK_START.md - 2-minute getting started guide
echo   • TROUBLESHOOTING.md - Common issues and solutions
echo   • ANTIVIRUS_README.md - Information about false positives
echo   • START_BlossomTag.bat - Optional launcher script
echo   • VERSION.txt - Version and feature information
echo.
echo 🎯 Ready to distribute! Users just need BlossomTag.exe, but the 
echo    documentation will help them get started quickly and avoid issues.
echo.
echo 💡 For professional distribution, consider:
echo   • Creating a ZIP file of this folder
echo   • Submitting to VirusTotal.com for verification
echo   • Creating an installer with NSIS or Inno Setup
echo   • Getting a code signing certificate (eliminates antivirus warnings)
echo.
cd ..
pause