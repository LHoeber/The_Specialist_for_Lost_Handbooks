@off
start cmd /k "python -m http.server 8000"
timeout /t 2 >nul
start "" "http://localhost:8000/Version_2/index.html"
