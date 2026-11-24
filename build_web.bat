@echo off
setlocal
cd /d "%~dp0"

python -m pygbag --build --archive ^
  --ume_block 1 ^
  --width 768 ^
  --height 624 ^
  --app_name cosmonian ^
  --package com.insertcoinstudio.cosmonian ^
  --title "COSMONIAN" ^
  .

if errorlevel 1 (
  echo.
  echo Error: no se pudo crear el paquete web.
  exit /b 1
)

python web_postprocess.py
if errorlevel 1 (
  echo.
  echo Error: no se pudo ajustar el escalado del HTML.
  exit /b 1
)

echo.
echo Paquete listo: %~dp0build\web.zip
