# PowerShell script - run_and_extract.ps1

# Définir les chemins
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectDir = Join-Path $ScriptDir "app\services"
$DataDir = "C:\Users\saghi\Downloads"
$DestDir = Join-Path $ScriptDir "data\datalake"
$ArchiveDir = Join-Path $ScriptDir "data\archives"

# Créer les dossiers de destination et d'archive s'ils n'existent pas
If (-Not (Test-Path -Path $DestDir)) {
    New-Item -ItemType Directory -Path $DestDir | Out-Null
}
If (-Not (Test-Path -Path $ArchiveDir)) {
    New-Item -ItemType Directory -Path $ArchiveDir | Out-Null
}

# Étape 1 : Exécuter le script Python
Write-Host "Exécution du script Python..."
python "$ProjectDir\data_loader.py"

# Étape 2 : Vérifier et déplacer le fichier téléchargé
$ZipFile = Join-Path $DataDir "IDFM-gtfs.zip"
$DestZip = Join-Path $DestDir "IDFM-gtfs.zip"

If (Test-Path -Path $ZipFile) {
    Write-Host "Fichier IDFM-gtfs.zip trouve. Deplacement vers $DestDir"
    Move-Item -Path $ZipFile -Destination $DestZip -Force
} else {
    Write-Host "Le fichier IDFM-gtfs.zip n'a pas ete trouve dans $DataDir"
    exit 1
}

# Étape 3 : Décompresser le fichier
Write-Host "Decompression de IDFM-gtfs.zip..."
Expand-Archive -Path $DestZip -DestinationPath $DestDir -Force

# Étape 4 : Archiver le fichier avec date
$DateStamp = Get-Date -Format "yyyy-MM-dd"
$ArchiveFile = Join-Path $ArchiveDir "IDFM-gtfs_$DateStamp.zip"
Move-Item -Path $DestZip -Destination $ArchiveFile -Force

Write-Host "Archive enregistree dans : $ArchiveFile" -ForegroundColor DarkGray
