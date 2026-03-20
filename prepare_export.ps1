# Prepare Export Script
# Creates a clean bundle of the codebase for sandboxed/offline deployment

$ErrorActionPreference = "Stop"

$sourceDir = Get-Location
$exportDir = Join-Path $sourceDir "export_bundle"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$zipName = "MAHER_AI_Offline_Bundle_$timestamp.zip"

Write-Host "Starting export preparation..."
Write-Host "Source: $sourceDir"
Write-Host "Destination: $exportDir"

# 1. Create Export Directory
if (Test-Path $exportDir) {
    Remove-Item -Path $exportDir -Recurse -Force
}
New-Item -ItemType Directory -Path $exportDir | Out-Null

# 2. Copy Files (exclusion list)
$exclude = @(
    ".git",
    ".gitignore",
    "node_modules",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "export_bundle",
    "*.log",
    ".DS_Store",
    ".env", # Don't export secrets
    "test_document.docx",
    "test_document.pdf"
)

Write-Host "Copying files..."

# Using Robocopy for robust copying with exclusions is often better, but for portability let's use PowerShell
# But simpler: Copy everything then delete excluded. Or iterate.
# Iterating is safer to avoid copying massive node_modules first.

Get-ChildItem -Path $sourceDir -Exclude $exclude | ForEach-Object {
    $targetPath = Join-Path $exportDir $_.Name
    if ($_.Name -in $exclude) {
        return # Skip
    }
    
    if ($_.PSIsContainer) {
        # Directory
        if (-not ($_.Name -in $exclude)) {
             Copy-Item -Path $_.FullName -Destination $targetPath -Recurse -Force
        }
    } else {
        # File
        Copy-Item -Path $_.FullName -Destination $targetPath -Force
    }
}

# 3. Clean up inside the copied directories (recursive cleanup of __pycache__ etc)
Write-Host "Cleaning up recursive artifacts in bundle..."
Get-ChildItem -Path $exportDir -Include "__pycache__", ".DS_Store", "*.pyc", "venv", "node_modules" -Recurse -Force | Remove-Item -Recurse -Force

# 4. Copy specific config examples
Copy-Item -Path ".env.example" -Destination "$exportDir\.env.example" -Force

# 5. Create Zip (Requires .NET 4.5+ or PowerShell 5+)
Write-Host "Creating Zip archive..."
$zipPath = Join-Path $sourceDir $zipName
Compress-Archive -Path "$exportDir\*" -DestinationPath $zipPath -Force

Write-Host "=========================================="
Write-Host "Export Complete!"
Write-Host "Bundle Location: $exportDir"
Write-Host "Zip File: $zipPath"
Write-Host "=========================================="
Write-Host "Next Steps for Offline Deployment:"
Write-Host "1. Validated that 'requirements.txt' is frozen."
Write-Host "2. Transfer '$zipName' to the target environment."
Write-Host "3. Follow 'SANDBOX_OFFLINE_DEPLOYMENT_GUIDE.md' inside the docs."
