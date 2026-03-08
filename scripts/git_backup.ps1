param(
  [string]$RepoDir = ".",
  [string]$Message = ""
)

Set-Location $RepoDir

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Host "git not found. Install Git for Windows first."
  exit 1
}

if (-not (Test-Path ".git")) {
  git init | Out-Null
}

if ([string]::IsNullOrWhiteSpace($Message)) {
  $Message = "backup " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}

git add -A
git commit -m $Message

Write-Host "Committed."
