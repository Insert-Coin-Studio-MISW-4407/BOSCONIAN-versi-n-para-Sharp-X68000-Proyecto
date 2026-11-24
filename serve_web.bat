@echo off
setlocal
cd /d "%~dp0"

python -m pygbag ^
  --ume_block 1 ^
  --width 768 ^
  --height 624 ^
  --app_name cosmonian ^
  --package com.insertcoinstudio.cosmonian ^
  --title "COSMONIAN" ^
  .
