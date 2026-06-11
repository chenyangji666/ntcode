# NTCode - PowerShell launcher (Qwen model for Bioinformatics)
Set-Location $PSScriptRoot
if (Get-Command bun -ErrorAction SilentlyContinue) {
    bun run src/entrypoints/cli.tsx @args
} elseif (Test-Path "cli") {
    wsl ./cli @args
} else {
    Write-Error "Error: Neither bun nor compiled binary found."
    exit 1
}
