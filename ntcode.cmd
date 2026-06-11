@echo off
REM NTCode - Windows launcher (Qwen model for Bioinformatics)
cd /d "C:\Users\12860\Desktop\ntcode"
bun run src/entrypoints/cli.tsx %*
