# INSTALLATION GUIDE - PYTHON & DEPENDENCIES

## CURRENT STATUS

- [x] Project structure created successfully
- [x] Removed emoji symbols from main.py
- [ ] Python NOT FOUND on system
- [ ] Virtual environment NOT created yet
- [ ] Dependencies NOT installed yet

---

## STEP 1: INSTALL PYTHON

### Option 1: Download from Official Website (Recommended)

1. Visit: https://www.python.org/downloads/
2. Download **Python 3.10** or higher (3.10.x, 3.11.x, or 3.12.x)
3. During installation:
   - **CHECK** "Add Python to PATH" (VERY IMPORTANT!)
   - **CHECK** "Install pip"
   - Click "Install Now"

4. Verify installation:
   ```powershell
   python --version
   # Should show: Python 3.10.x or higher
   
   pip --version
   # Should show: pip 23.x.x or higher
   ```

### Option 2: Install via Windows Store

1. Open Microsoft Store
2. Search "Python 3.10" or "Python 3.11"
3. Click Install
4. Verify as above

### Option 3: Install via Chocolatey (Advanced)

```powershell
# If you have Chocolatey installed
choco install python310 -y

# Verify
python --version
```

---

## STEP 2: CREATE VIRTUAL ENVIRONMENT (After Python installed)

```powershell
# Navigate to backend directory
cd "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent\backend"

# Create virtual environment
python -m venv venv

# Activate virtual environment (PowerShell)
.\venv\Scripts\Activate.ps1

# You should see (venv) in your terminal prompt
```

**If PowerShell execution policy error:**
```powershell
# Run this first (as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activate again
.\venv\Scripts\Activate.ps1
```

**Alternative activation methods:**
```powershell
# CMD
.\venv\Scripts\activate.bat

# Git Bash
source venv/Scripts/activate
```

---

## STEP 3: INSTALL DEPENDENCIES

```powershell
# Make sure venv is activated (you see "(venv)" in prompt)
cd "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent"

# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# This will take 5-10 minutes to install 60+ packages
```

**Common Issues & Solutions:**

**Issue 1: pip SSL error**
```powershell
# Use trusted host
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

**Issue 2: Some packages fail to install**
```powershell
# Install build tools (Windows)
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Install "Desktop development with C++"

# Or install packages one by one
pip install fastapi uvicorn sqlalchemy pymysql
pip install langchain langchain-openai chromadb
```

**Issue 3: ChromaDB installation fails**
```powershell
# ChromaDB requires Microsoft C++ Build Tools
# Alternative: Use FAISS instead
pip install faiss-cpu
```

---

## STEP 4: VERIFY INSTALLATION

```powershell
# Activate venv if not already
.\venv\Scripts\Activate.ps1

# Check installed packages
pip list

# Should see:
# fastapi==0.109.0
# uvicorn==0.27.0
# langchain==0.1.6
# chromadb==0.4.22
# ... and many more

# Test imports
python -c "import fastapi; print('FastAPI OK')"
python -c "import langchain; print('LangChain OK')"
python -c "import chromadb; print('ChromaDB OK')"
```

---

## STEP 5: RUN BACKEND SERVER

```powershell
# Navigate to backend
cd "d:\Bai Luan\Nam 2025 - 2026\Hoc Ky I\CS434\CS434\CRM-AI-Agent\backend"

# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Run server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload

# Visit: http://localhost:8000/docs
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
Starting CRM-AI-Agent Backend...
INFO:     Application startup complete.
```

---

## TROUBLESHOOTING

### Python not found after installation

**Solution 1: Add to PATH manually**
1. Search "Environment Variables" in Windows
2. Edit "Path" variable
3. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python310`
4. Add: `C:\Users\YourUsername\AppData\Local\Programs\Python\Python310\Scripts`
5. Restart terminal

**Solution 2: Use full path**
```powershell
# Find Python installation
where.exe python

# Use full path
C:\Users\YourUsername\AppData\Local\Programs\Python\Python310\python.exe -m venv venv
```

### Cannot activate venv (Execution Policy)

```powershell
# Check current policy
Get-ExecutionPolicy

# Set to RemoteSigned (as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for this session only
powershell -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### Import errors after installation

```powershell
# Reinstall specific package
pip uninstall <package-name>
pip install <package-name>

# Or reinstall all
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

## NEXT STEPS AFTER SUCCESSFUL INSTALLATION

1. [ ] Create `.env` file:
   ```powershell
   cp .env.example .env
   ```

2. [ ] Edit `.env` and add your OpenAI API Key:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   MYSQL_PASSWORD=your-secure-password
   ```

3. [ ] Install MySQL 8.0 or run Docker:
   ```powershell
   docker run --name crm_mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=crm_ai_db -e MYSQL_USER=crm_user -e MYSQL_PASSWORD=password -p 3306:3306 -d mysql:8.0
   ```

4. [ ] Start working on Phase 1 tasks:
   - See `TASK_BREAKDOWN.md` for detailed checklist

---

## SUMMARY CHECKLIST

- [ ] Python 3.10+ installed
- [ ] Python added to PATH
- [ ] Virtual environment created in `backend/venv`
- [ ] Virtual environment activated
- [ ] All dependencies installed from `requirements.txt`
- [ ] Backend server runs without errors
- [ ] Swagger docs accessible at http://localhost:8000/docs
- [ ] `.env` file created with API keys
- [ ] MySQL database running

---

**Last Updated:** November 29, 2025
**Status:** Waiting for Python installation
