"""
KAWSAR HOSTING BOT VERSION 3.1
AUTO-RECOVERY SYSTEM & TIER MANAGEMENT
FONT STYLE: MATHEMATICAL BOLD SANS-SERIF
CREDITS: KAWSAR CODER
"""

import subprocess
import sys
import os

# ✅ Auto-install missing modules
def auto_install(package):
    try:
        __import__(package)
    except ModuleNotFoundError:
        print(f"📦 Installing missing package: {package} ...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Installed: {package}")

# Auto-install required modules
for mod in ["telebot", "psutil", "requests", "flask", "qrcode", "Pillow", "cryptography"]:
    auto_install(mod)

# --- After auto-install, import all modules safely ---
import telebot
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import atexit
import requests
from flask import Flask
from threading import Thread
import qrcode
from io import BytesIO
import hashlib
import random
import string
from cryptography.fernet import Fernet
import base64

app = Flask('')

@app.route('/')
def home():
    return "I'M KAWSAR HOSTING BOT"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("✅ Flask Keep-Alive server started.")

# ================================
# CONFIGURATION
# ================================
TOKEN = '8369678760:AAHws99dSQBPlkI88RIoTSsb141wNNG3K7M'  # Replace with your actual token
OWNER_ID = 5957710220
ADMIN_ID = 5957710220
YOUR_USERNAME = '@Kawsar9340'
UPDATE_CHANNEL = 'https://t.me/kawsar93400'
UPDATE_GROUP = 'https://t.me/kawsar9340'  # New update group

# Folder setup
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'khb_uploads')
KHB_DATA_DIR = os.path.join(BASE_DIR, 'khb_data')
DATABASE_PATH = os.path.join(KHB_DATA_DIR, 'khb_bot.db')
RUNNING_SCRIPTS_DB = os.path.join(KHB_DATA_DIR, 'running_scripts.json')
REFERRAL_DB = os.path.join(KHB_DATA_DIR, 'referrals.json')

# TIER SYSTEM
TIER_SYSTEM = {
    "free": {
        "name": "FREE",
        "upload_limit": 5,
        "max_file_size": 50 * 1024 * 1024,
        "icon": "🎫",
        "color": "#2ecc71",
        "auto_restart": False,
        "referral_needed": 3
    },
    "premium": {
        "name": "PREMIUM",
        "upload_limit": 10,
        "max_file_size": 200 * 1024 * 1024,
        "icon": "⭐",
        "color": "#f39c12",
        "auto_restart": True,
        "referral_needed": 0
    },
    "owner": {
        "name": "OWNER",
        "upload_limit": float('inf'),
        "max_file_size": float('inf'),
        "icon": "👑",
        "color": "#e74c3c",
        "auto_restart": True,
        "referral_needed": 0
    }
}

# Create necessary directories
os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(KHB_DATA_DIR, exist_ok=True)

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# --- Data structures ---
bot_scripts = {}  # Stores info about running scripts
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
referral_data = {}  # Store referral data

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ================================
# FONT CONVERSION FUNCTIONS
# ================================
def convert_to_bold_uppercase(text: str) -> str:
    """Convert text to mathematical bold sans-serif"""
    bold_mapping = {
        'A': 'A', 'B': 'B', 'C': 'C', 'D': 'D', 'E': 'E', 'F': 'F', 'G': 'G',
        'H': 'H', 'I': 'I', 'J': 'J', 'K': 'K', 'L': 'L', 'M': 'M', 'N': 'N',
        'O': 'O', 'P': 'P', 'Q': 'Q', 'R': 'R', 'S': 'S', 'T': 'T', 'U': 'U',
        'V': 'V', 'W': 'W', 'X': 'X', 'Y': 'Y', 'Z': 'Z',
        'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e', 'f': 'f', 'g': 'g',
        'h': 'h', 'i': 'i', 'j': 'j', 'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n',
        'o': 'o', 'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't', 'u': 'u',
        'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z',
        '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6',
        '7': '7', '8': '8', '9': '9',
        ' ': ' ', '!': '!', '@': '@', '#': '#', '$': '$', '%': '%', '^': '^',
        '&': '&', '*': '*', '(': '(', ')': ')', '-': '-', '_': '_', '=': '=',
        '+': '+', '[': '[', ']': ']', '{': '{', '}': '}', '\\': '\\', '|': '|',
        ';': ';', ':': ':', "'": "'", '"': '"', ',': ',', '.': '.', '<': '<',
        '>': '>', '/': '/', '?': '?', '`': '`', '~': '~'
    }
    
    result = []
    for char in str(text):
        result.append(bold_mapping.get(char, char))
    return ''.join(result)

# Alias for easy use
B = convert_to_bold_uppercase

# ================================
# REFERRAL SYSTEM (UPDATED)
# ================================
class ReferralSystem:
    def __init__(self):
        self.referral_file = REFERRAL_DB
        
    def load_referrals(self):
        """Load referral data from file"""
        global referral_data
        try:
            if os.path.exists(self.referral_file):
                with open(self.referral_file, 'r') as f:
                    referral_data = json.load(f)
            else:
                referral_data = {}
        except Exception as e:
            logger.error(f"❌ Error loading referrals: {e}")
            referral_data = {}
    
    def save_referrals(self):
        """Save referral data to file"""
        try:
            with open(self.referral_file, 'w') as f:
                json.dump(referral_data, f, indent=4)
        except Exception as e:
            logger.error(f"❌ Error saving referrals: {e}")
    
    def generate_referral_code(self, user_id):
        """Generate unique referral code"""
        code = f"KHB{user_id}{random.randint(1000, 9999)}"
        if user_id not in referral_data:
            referral_data[user_id] = {
                'code': code,
                'referrals': [],
                'count': 0,
                'auto_restart_enabled': False,
                'generated_at': datetime.now().isoformat(),
                'username': ''
            }
        else:
            referral_data[user_id]['code'] = code
        self.save_referrals()
        return code
    
    def get_referral_code(self, user_id):
        """Get user's referral code"""
        if user_id in referral_data:
            return referral_data[user_id].get('code')
        return self.generate_referral_code(user_id)
    
    def add_referral(self, referrer_id, referred_id, referred_username=None):
        """Add a referral"""
        if referrer_id == referred_id:
            return False
        
        if referrer_id not in referral_data:
            self.generate_referral_code(referrer_id)
        
        # Update referrer's username if not set
        if 'username' not in referral_data[referrer_id]:
            referral_data[referrer_id]['username'] = ''
        
        # Add referred user info
        referred_info = {
            'user_id': referred_id,
            'username': referred_username or '',
            'joined_at': datetime.now().isoformat()
        }
        
        if referred_id not in [r['user_id'] for r in referral_data[referrer_id].get('referrals', [])]:
            referral_data[referrer_id].setdefault('referrals', []).append(referred_info)
            referral_data[referrer_id]['count'] = len(referral_data[referrer_id]['referrals'])
            
            # Check if auto-restart should be enabled
            if referral_data[referrer_id]['count'] >= TIER_SYSTEM['free']['referral_needed']:
                referral_data[referrer_id]['auto_restart_enabled'] = True
            
            self.save_referrals()
            return True
        return False
    
    def get_referral_count(self, user_id):
        """Get number of referrals"""
        if user_id in referral_data:
            return referral_data[user_id]['count']
        return 0
    
    def is_auto_restart_enabled(self, user_id):
        """Check if auto-restart is enabled"""
        if user_id in referral_data:
            return referral_data[user_id]['auto_restart_enabled']
        return False
    
    def get_top_referrers(self, limit=10):
        """Get top referrers for leaderboard"""
        referrers = []
        for user_id, data in referral_data.items():
            if 'count' in data and data['count'] > 0:
                referrers.append({
                    'user_id': user_id,
                    'username': data.get('username', ''),
                    'count': data['count'],
                    'auto_restart': data.get('auto_restart_enabled', False)
                })
        
        # Sort by count descending
        referrers.sort(key=lambda x: x['count'], reverse=True)
        return referrers[:limit]
    
    def get_user_referral_info(self, user_id):
        """Get detailed referral info for user"""
        if user_id not in referral_data:
            return None
        
        data = referral_data[user_id].copy()
        data['rank'] = self.get_user_rank(user_id)
        return data
    
    def get_user_rank(self, user_id):
        """Get user's rank in referral leaderboard"""
        referrers = self.get_top_referrers(limit=1000)
        for i, referrer in enumerate(referrers, 1):
            if referrer['user_id'] == user_id:
                return i
        return None
    
    def update_user_username(self, user_id, username):
        """Update user's username"""
        if user_id in referral_data:
            referral_data[user_id]['username'] = username or ''
            self.save_referrals()

# Initialize referral system
referral_system = ReferralSystem()
referral_system.load_referrals()

# ================================
# ANIMATION PROGRESS SYSTEM
# ================================
class ProgressAnimation:
    @staticmethod
    def execute_animation():
        return [
            B("Executing: [▱▱▱▱▱▱▱▱▱▱] 0%"),
            B("⚡ Executing: [▰▱▱▱▱▱▱▱▱▱] 10%"),
            B("⚡ Executing: [▰▰▱▱▱▱▱▱▱▱] 20%"),
            B("⚡ Executing: [▰▰▰▱▱▱▱▱▱▱] 30%"),
            B("⚡ Executing: [▰▰▰▰▱▱▱▱▱▱] 40%"),
            B("⚡ Executing: [▰▰▰▰▰▱▱▱▱▱] 50%"),
            B("⚡ Executing: [▰▰▰▰▰▰▱▱▱▱] 60%"),
            B("⚡ Executing: [▰▰▰▰▰▰▰▱▱▱] 70%"),
            B("⚡ Executing: [▰▰▰▰▰▰▰▰▱▱] 80%"),
            B("⚡ Executing: [▰▰▰▰▰▰▰▰▰▱] 90%"),
            B("✅ Complete: [▰▰▰▰▰▰▰▰▰▰] 100%")
        ]
    
    @staticmethod
    def upload_animation():
        return [
            B("📤 Uploading: [▱▱▱▱▱▱▱▱▱▱] 0%"),
            B("📤 Uploading: [▰▱▱▱▱▱▱▱▱▱] 25%"),
            B("📤 Uploading: [▰▰▰▱▱▱▱▱▱▱] 50%"),
            B("📤 Uploading: [▰▰▰▰▰▰▱▱▱▱] 75%"),
            B("✅ Upload Complete: [▰▰▰▰▰▰▰▰▰▰] 100%")
        ]
    
    @staticmethod
    def recovery_animation():
        return [
            B("🔄 Recovery: [▱▱▱▱▱▱▱▱▱▱] 0%"),
            B("🔄 Recovery: [▰▰▱▱▱▱▱▱▱▱] 20%"),
            B("🔄 Recovery: [▰▰▰▰▱▱▱▱▱▱] 40%"),
            B("🔄 Recovery: [▰▰▰▰▰▰▱▱▱▱] 60%"),
            B("🔄 Recovery: [▰▰▰▰▰▰▰▰▱▱] 80%"),
            B("✅ Recovery Complete: [▰▰▰▰▰▰▰▰▰▰] 100%")
        ]
    
    @staticmethod
    def restart_animation():
        return [
            B("🔄 Bot Restarting: [▱▱▱▱▱▱▱▱▱▱] 0%"),
            B("🔄 Bot Restarting: [▰▰▱▱▱▱▱▱▱▱] 20%"),
            B("🔄 Bot Restarting: [▰▰▰▰▱▱▱▱▱▱] 40%"),
            B("🔄 Bot Restarting: [▰▰▰▰▰▰▱▱▱▱] 60%"),
            B("🔄 Bot Restarting: [▰▰▰▰▰▰▰▰▱▱] 80%"),
            B("✅ Bot Restarted: [▰▰▰▰▰▰▰▰▰▰] 100%")
        ]

# ================================
# AUTO-RECOVERY SYSTEM
# ================================
class AutoRecoverySystem:
    def __init__(self):
        self.running_scripts_file = RUNNING_SCRIPTS_DB
        
    def save_running_script(self, user_id: int, file_name: str, file_path: str, process_pid: int):
        """Save running script info to database"""
        try:
            if os.path.exists(self.running_scripts_file):
                with open(self.running_scripts_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"running_scripts": []}
            
            # Remove duplicates
            data["running_scripts"] = [script for script in data["running_scripts"] 
                                     if not (script["user_id"] == user_id and script["file_name"] == file_name)]
            
            # Add new script
            script_info = {
                "user_id": user_id,
                "file_name": file_name,
                "file_path": file_path,
                "process_pid": process_pid,
                "start_time": datetime.now().isoformat(),
                "status": "running",
                "last_updated": datetime.now().isoformat()
            }
            
            data["running_scripts"].append(script_info)
            
            with open(self.running_scripts_file, 'w') as f:
                json.dump(data, f, indent=4)
                
            logger.info(f"💾 Saved running script: {user_id}/{file_name}")
            
        except Exception as e:
            logger.error(f"❌ Error saving running script: {e}")
    
    def remove_running_script(self, user_id: int, file_name: str):
        """Remove script from running database"""
        try:
            if os.path.exists(self.running_scripts_file):
                with open(self.running_scripts_file, 'r') as f:
                    data = json.load(f)
                
                initial_count = len(data["running_scripts"])
                data["running_scripts"] = [script for script in data["running_scripts"] 
                                         if not (script["user_id"] == user_id and script["file_name"] == file_name)]
                
                if len(data["running_scripts"]) < initial_count:
                    with open(self.running_scripts_file, 'w') as f:
                        json.dump(data, f, indent=4)
                    logger.info(f"🗑️ Removed running script: {user_id}/{file_name}")
                    
        except Exception as e:
            logger.error(f"❌ Error removing running script: {e}")
    
    def recover_all_scripts(self):
        """Recover all scripts after crash/restart"""
        try:
            if not os.path.exists(self.running_scripts_file):
                logger.info("📭 No running scripts to recover")
                return []
            
            with open(self.running_scripts_file, 'r') as f:
                data = json.load(f)
            
            recovered = []
            for script in data.get("running_scripts", []):
                try:
                    user_id = script["user_id"]
                    file_name = script["file_name"]
                    file_path = script["file_path"]
                    
                    # Check if file still exists
                    if not os.path.exists(file_path):
                        logger.warning(f"⚠️ File not found for recovery: {file_path}")
                        continue
                    
                    # Check if user still has file in database
                    user_has_file = False
                    for fname, ftype in user_files.get(user_id, []):
                        if fname == file_name:
                            user_has_file = True
                            break
                    
                    if not user_has_file:
                        logger.warning(f"⚠️ User {user_id} no longer has file: {file_name}")
                        continue
                    
                    # Check if auto-restart is enabled for user
                    tier = get_user_tier(user_id)
                    auto_restart_enabled = TIER_SYSTEM[tier]['auto_restart']
                    
                    if tier == 'free':
                        auto_restart_enabled = referral_system.is_auto_restart_enabled(user_id)
                    
                    if not auto_restart_enabled:
                        logger.info(f"⏸️ Auto-restart disabled for user {user_id}")
                        continue
                    
                    # Restart the script
                    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
                    file_ext = os.path.splitext(file_name)[1].lower()
                    
                    if file_ext == '.py':
                        threading.Thread(target=self._restart_py_script, 
                                       args=(user_id, file_path, user_folder, file_name)).start()
                    elif file_ext == '.js':
                        threading.Thread(target=self._restart_js_script,
                                       args=(user_id, file_path, user_folder, file_name)).start()
                    
                    recovered.append({
                        "user_id": user_id,
                        "file_name": file_name,
                        "status": "recovering"
                    })
                    
                    logger.info(f"🔄 Recovering script: {user_id}/{file_name}")
                    
                    time.sleep(1)  # Avoid overload
                    
                except Exception as e:
                    logger.error(f"❌ Error recovering script {script}: {e}")
            
            return recovered
            
        except Exception as e:
            logger.error(f"❌ Error in recovery system: {e}")
            return []
    
    def _restart_py_script(self, user_id: int, file_path: str, user_folder: str, file_name: str):
        """Restart Python script"""
        try:
            script_key = f"{user_id}_{file_name}"
            
            if script_key in bot_scripts:
                logger.info(f"✅ Script already running: {file_name}")
                return
            
            log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            log_file = open(log_file_path, 'a', encoding='utf-8', errors='ignore')
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                [sys.executable, file_path],
                cwd=user_folder,
                stdout=log_file,
                stderr=log_file,
                stdin=subprocess.PIPE,
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='ignore'
            )
            
            bot_scripts[script_key] = {
                'process': process,
                'log_file': log_file,
                'file_name': file_name,
                'user_id': user_id,
                'start_time': datetime.now(),
                'type': 'py',
                'script_key': script_key
            }
            
            # Save to recovery database
            self.save_running_script(user_id, file_name, file_path, process.pid)
            
            logger.info(f"✅ Recovered Python script: {file_name} (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"❌ Error restarting Python script {file_name}: {e}")
    
    def _restart_js_script(self, user_id: int, file_path: str, user_folder: str, file_name: str):
        """Restart JS script"""
        try:
            script_key = f"{user_id}_{file_name}"
            
            if script_key in bot_scripts:
                logger.info(f"✅ Script already running: {file_name}")
                return
            
            log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
            log_file = open(log_file_path, 'a', encoding='utf-8', errors='ignore')
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                ['node', file_path],
                cwd=user_folder,
                stdout=log_file,
                stderr=log_file,
                stdin=subprocess.PIPE,
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='ignore'
            )
            
            bot_scripts[script_key] = {
                'process': process,
                'log_file': log_file,
                'file_name': file_name,
                'user_id': user_id,
                'start_time': datetime.now(),
                'type': 'js',
                'script_key': script_key
            }
            
            # Save to recovery database
            self.save_running_script(user_id, file_name, file_path, process.pid)
            
            logger.info(f"✅ Recovered JS script: {file_name} (PID: {process.pid})")
            
        except Exception as e:
            logger.error(f"❌ Error restarting JS script {file_name}: {e}")
    
    def get_running_count(self):
        """Get count of running scripts"""
        try:
            if os.path.exists(self.running_scripts_file):
                with open(self.running_scripts_file, 'r') as f:
                    data = json.load(f)
                return len(data.get("running_scripts", []))
            return 0
        except:
            return 0

# Initialize recovery system
recovery_system = AutoRecoverySystem()

# ================================
# DATABASE SETUP
# ================================
def init_db():
    """Initialize the database"""
    logger.info(f"📊 Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT, tier TEXT, created_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT, uploaded_at TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY, username TEXT, first_join TEXT, last_seen TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY, added_by INTEGER, added_at TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS user_stats
                     (user_id INTEGER PRIMARY KEY, uploads_count INTEGER, 
                      scripts_run INTEGER, total_upload_size INTEGER)''')
        
        # Insert owner and admin
        c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)',
                  (OWNER_ID, OWNER_ID, datetime.now().isoformat()))
        
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)',
                      (ADMIN_ID, OWNER_ID, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully.")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)

def load_data():
    """Load data from database"""
    logger.info("📥 Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        
        # Load subscriptions
        c.execute('SELECT user_id, expiry, tier FROM subscriptions')
        for user_id, expiry, tier in c.fetchall():
            try:
                user_subscriptions[user_id] = {
                    'expiry': datetime.fromisoformat(expiry) if expiry else None,
                    'tier': tier or 'free'
                }
            except:
                pass
        
        # Load user files
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))
        
        # Load active users
        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())
        
        # Load admins
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())
        
        conn.close()
        
        logger.info(f"✅ Data loaded: {len(active_users)} users, "
                   f"{len(user_subscriptions)} subscriptions, "
                   f"{len(admin_ids)} admins")
        
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}", exc_info=True)

# Initialize DB and Load Data
init_db()
load_data()

# ================================
# HELPER FUNCTIONS
# ================================
def get_user_folder(user_id):
    """Get or create user's folder"""
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def get_user_tier(user_id):
    """Get user's tier"""
    if user_id == OWNER_ID:
        return "owner"
    elif user_id in admin_ids:
        return "owner"  # Admins get owner privileges
    elif user_id in user_subscriptions:
        sub = user_subscriptions[user_id]
        if sub.get('expiry') and sub['expiry'] > datetime.now():
            return sub.get('tier', 'premium')
    return "free"

def get_user_file_limit(user_id):
    """Get file upload limit for user"""
    tier = get_user_tier(user_id)
    return TIER_SYSTEM[tier]["upload_limit"]

def get_user_file_count(user_id):
    """Get number of files uploaded by user"""
    return len(user_files.get(user_id, []))

def is_bot_running(user_id, file_name):
    """Check if a bot script is currently running"""
    script_key = f"{user_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except psutil.NoSuchProcess:
            # Process not found, clean up
            recovery_system.remove_running_script(user_id, file_name)
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
    return False

def kill_process_tree(process_info):
    """Kill a process and all its children"""
    try:
        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            try:
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                
                for child in children:
                    try:
                        child.terminate()
                    except:
                        pass
                
                try:
                    parent.terminate()
                    parent.wait(timeout=3)
                except:
                    try:
                        parent.kill()
                    except:
                        pass
                
                # Remove from recovery database
                if 'user_id' in process_info and 'file_name' in process_info:
                    recovery_system.remove_running_script(
                        process_info['user_id'], 
                        process_info['file_name']
                    )
                
            except psutil.NoSuchProcess:
                pass
                
    except Exception as e:
        logger.error(f"❌ Error killing process: {e}")

def send_restart_notification():
    """Send restart notification to all users"""
    logger.info("📢 Sending restart notifications...")
    
    notification_text = B("""
🚨 *IMPORTANT ANNOUNCEMENT*

Bot is restarting for maintenance.

🔄 *Your scripts will be automatically restarted if:*
✅ You are Premium/Owner user
✅ You have referred 3+ friends (Free users)

📊 *Current status:*
• Premium/Owner: Auto-restart ✅
• Free: Auto-restart ❌

🔗 *To enable auto-restart for FREE tier:*
1. Go to /refer
2. Share your referral link
3. Refer 3 friends
4. Auto-restart will be enabled!

⏱️ *Bot will be back online in:*
• 30 seconds

Thank you for your patience! 😊
""")
    
    sent = 0
    failed = 0
    
    for user_id in list(active_users):
        try:
            bot.send_message(user_id, notification_text, parse_mode='Markdown')
            sent += 1
        except Exception as e:
            failed += 1
            logger.error(f"❌ Failed to send notification to {user_id}: {e}")
        
        # Avoid rate limiting
        time.sleep(0.1)
    
    logger.info(f"📤 Restart notifications: Sent={sent}, Failed={failed}")

# ================================
# BUTTON LAYOUTS (with BOLD FONT)
# ================================
def create_main_menu_inline(user_id):
    """Create main menu with bold font"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # User buttons
    user_buttons = [
        types.InlineKeyboardButton(B('📢 Updates'), url=UPDATE_CHANNEL),
        types.InlineKeyboardButton(B('👥 Join Group'), url=UPDATE_GROUP),
        types.InlineKeyboardButton(B('📤 Upload'), callback_data='upload'),
        types.InlineKeyboardButton(B('📂 My Files'), callback_data='check_files'),
        types.InlineKeyboardButton(B('⚡ Speed'), callback_data='speed'),
        types.InlineKeyboardButton(B('📊 Stats'), callback_data='stats'),
        types.InlineKeyboardButton(B('👤 Profile'), callback_data='profile'),
        types.InlineKeyboardButton(B('🤝 Refer'), callback_data='refer'),
        types.InlineKeyboardButton(B('🏆 Leaderboard'), callback_data='leaderboard'),
        types.InlineKeyboardButton(B('🔄 Restart All'), callback_data='restart_all'),
        types.InlineKeyboardButton(B('📞 Contact'), url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}')
    ]
    
    if user_id in admin_ids:
        # Add admin buttons
        admin_buttons = [
            types.InlineKeyboardButton(B('👑 Admin'), callback_data='admin_panel'),
            types.InlineKeyboardButton(B('💳 Subs'), callback_data='subscription'),
            types.InlineKeyboardButton(B('📢 Broadcast'), callback_data='broadcast'),
            types.InlineKeyboardButton(B('🔒 Lock') if not bot_locked else B('🔓 Unlock'), 
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton(B('🔄 Recover'), callback_data='recover_all'),
            types.InlineKeyboardButton(B('📈 Analytics'), callback_data='analytics'),
            types.InlineKeyboardButton(B('🚀 Restart Bot'), callback_data='restart_bot')
        ]
        
        # Arrange buttons
        markup.add(user_buttons[0], user_buttons[1])  # Updates, Group
        markup.add(user_buttons[2], user_buttons[3])  # Upload, My Files
        markup.add(user_buttons[4], admin_buttons[0])  # Speed, Admin
        markup.add(admin_buttons[1], admin_buttons[2])  # Subs, Broadcast
        markup.add(admin_buttons[3], admin_buttons[4])  # Lock/Unlock, Recover
        markup.add(user_buttons[6], user_buttons[7])  # Refer, Leaderboard
        markup.add(admin_buttons[6], admin_buttons[5])  # Restart Bot, Analytics
        markup.add(user_buttons[8], user_buttons[5])  # Restart All, Stats
        markup.add(user_buttons[9], user_buttons[10])  # Profile, Contact
    else:
        # Regular user layout
        markup.add(user_buttons[0], user_buttons[1])  # Updates, Group
        markup.add(user_buttons[2], user_buttons[3])  # Upload, My Files
        markup.add(user_buttons[4], user_buttons[5])  # Speed, Stats
        markup.add(user_buttons[6], user_buttons[7])  # Profile, Refer
        markup.add(user_buttons[8], user_buttons[9])  # Leaderboard, Restart All
        markup.add(user_buttons[10])  # Contact
    
    return markup

def create_reply_keyboard_main_menu(user_id):
    """Create reply keyboard with bold font"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if user_id in admin_ids:
        buttons = [
            B("📢 Updates"),
            B("👥 Join Group"),
            B("📤 Upload"),
            B("📂 My Files"),
            B("⚡ Speed"),
            B("📊 Stats"),
            B("👤 Profile"),
            B("🤝 Refer"),
            B("🏆 Leaderboard"),
            B("👑 Admin"),
            B("💳 Subs"),
            B("📢 Broadcast"),
            B("🔄 Recover"),
            B("🔄 Restart All"),
            B("🚀 Restart Bot"),
            B("📞 Contact")
        ]
    else:
        buttons = [
            B("📢 Updates"),
            B("👥 Join Group"),
            B("📤 Upload"),
            B("📂 My Files"),
            B("⚡ Speed"),
            B("📊 Stats"),
            B("👤 Profile"),
            B("🤝 Refer"),
            B("🏆 Leaderboard"),
            B("🔄 Restart All"),
            B("📞 Contact")
        ]
    
    # Create rows of 2 buttons
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        markup.add(*[types.KeyboardButton(text) for text in row])
    
    return markup

def create_control_buttons(user_id, file_name, is_running=True):
    """Create control buttons for files"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    if is_running:
        markup.row(
            types.InlineKeyboardButton(B("🔴 Stop"), callback_data=f'stop_{user_id}_{file_name}'),
            types.InlineKeyboardButton(B("🔄 Restart"), callback_data=f'restart_{user_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton(B("🗑️ Delete"), callback_data=f'delete_{user_id}_{file_name}'),
            types.InlineKeyboardButton(B("📜 Logs"), callback_data=f'logs_{user_id}_{file_name}')
        )
    else:
        markup.row(
            types.InlineKeyboardButton(B("🟢 Start"), callback_data=f'start_{user_id}_{file_name}'),
            types.InlineKeyboardButton(B("🗑️ Delete"), callback_data=f'delete_{user_id}_{file_name}')
        )
        markup.row(
            types.InlineKeyboardButton(B("📜 View Logs"), callback_data=f'logs_{user_id}_{file_name}')
        )
    
    markup.add(types.InlineKeyboardButton(B("🔙 Back"), callback_data='check_files'))
    return markup

def create_admin_panel():
    """Create admin panel"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(B('➕ Add Admin'), callback_data='add_admin'),
        types.InlineKeyboardButton(B('➖ Remove Admin'), callback_data='remove_admin')
    )
    markup.row(
        types.InlineKeyboardButton(B('📋 List Admins'), callback_data='list_admins'),
        types.InlineKeyboardButton(B('📊 System Stats'), callback_data='system_stats')
    )
    markup.row(types.InlineKeyboardButton(B('🔙 Back'), callback_data='back_to_main'))
    return markup

def create_subscription_menu():
    """Create subscription menu"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton(B('➕ Add Sub'), callback_data='add_subscription'),
        types.InlineKeyboardButton(B('➖ Remove Sub'), callback_data='remove_subscription')
    )
    markup.row(types.InlineKeyboardButton(B('🔍 Check Sub'), callback_data='check_subscription'))
    markup.row(types.InlineKeyboardButton(B('🔙 Back'), callback_data='back_to_main'))
    return markup

def create_referral_menu(user_id):
    """Create referral menu"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    referral_code = referral_system.get_referral_code(user_id)
    bot_username = bot.get_me().username
    # 🚀 FIXED: Using regular font for referral link (not bold)
    referral_link = f"https://t.me/{bot_username}?start={referral_code}"
    
    markup.add(types.InlineKeyboardButton(B('🔗 Copy Link'), 
                                         callback_data=f'copy_referral_{user_id}'))
    markup.add(types.InlineKeyboardButton(B('📊 My Referrals'), 
                                         callback_data=f'check_referrals_{user_id}'))
    markup.add(types.InlineKeyboardButton(B('🏆 Leaderboard'), 
                                         callback_data='leaderboard'))
    markup.add(types.InlineKeyboardButton(B('📋 QR Code'), 
                                         callback_data=f'qr_referral_{user_id}'))
    markup.add(types.InlineKeyboardButton(B('🔙 Back'), callback_data='back_to_main'))
    
    return markup, referral_link

def create_leaderboard_markup():
    """Create leaderboard markup"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(B('🔄 Refresh'), callback_data='refresh_leaderboard'))
    markup.add(types.InlineKeyboardButton(B('🏆 My Rank'), callback_data='my_rank'))
    markup.add(types.InlineKeyboardButton(B('🤝 Refer'), callback_data='refer'))
    markup.add(types.InlineKeyboardButton(B('🔙 Back'), callback_data='back_to_main'))
    return markup

# ================================
# SCRIPT RUNNING SYSTEM
# ================================
TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI',
    'telegram': 'python-telegram-bot',
    'aiogram': 'aiogram',
    'pyrogram': 'pyrogram',
    'telethon': 'telethon',
    'requests': 'requests',
    'flask': 'Flask',
    'psutil': 'psutil',
    'qrcode': 'qrcode',
    'pillow': 'Pillow',
    'cryptography': 'cryptography',
    'bs4': 'beautifulsoup4',
    'pandas': 'pandas',
    'numpy': 'numpy'
}

def attempt_install_pip(module_name, message):
    """Attempt to install Python module"""
    package_name = TELEGRAM_MODULES.get(module_name.lower(), module_name)
    if package_name is None:
        return False
    
    try:
        bot.reply_to(message, B(f"🐍 Installing `{module_name}`..."))
        command = [sys.executable, '-m', 'pip', 'install', package_name]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            bot.reply_to(message, B(f"✅ Package `{package_name}` installed."))
            return True
        else:
            bot.reply_to(message, B(f"❌ Failed to install `{package_name}`."))
            return False
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error: {str(e)}"))
        return False

def run_script(script_path, user_id, user_folder, file_name, message):
    """Run Python script"""
    try:
        # Show progress animation
        msg = bot.reply_to(message, ProgressAnimation.execute_animation()[0])
        
        for i, frame in enumerate(ProgressAnimation.execute_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        
        # Check if file exists
        if not os.path.exists(script_path):
            bot.edit_message_text(B(f"❌ File not found: `{file_name}`"), 
                                message.chat.id, msg.message_id)
            return
        
        # Pre-check for missing modules
        check_command = [sys.executable, script_path]
        check_proc = None
        
        try:
            check_proc = subprocess.Popen(check_command, cwd=user_folder, 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, encoding='utf-8', errors='ignore')
            stdout, stderr = check_proc.communicate(timeout=5)
            
            if stderr:
                match = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                if match:
                    module_name = match.group(1)
                    if attempt_install_pip(module_name, message):
                        time.sleep(2)
                        # Retry after install
                        run_script(script_path, user_id, user_folder, file_name, message)
                        return
        except subprocess.TimeoutExpired:
            if check_proc:
                check_proc.kill()
                check_proc.communicate()
        
        # Start the script
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        process = subprocess.Popen(
            [sys.executable, script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            startupinfo=startupinfo,
            encoding='utf-8',
            errors='ignore'
        )
        
        script_key = f"{user_id}_{file_name}"
        bot_scripts[script_key] = {
            'process': process,
            'log_file': log_file,
            'file_name': file_name,
            'user_id': user_id,
            'start_time': datetime.now(),
            'type': 'py',
            'script_key': script_key
        }
        
        # Save to recovery database
        recovery_system.save_running_script(user_id, file_name, script_path, process.pid)
        
        bot.edit_message_text(
            B(f"✅ Python script `{file_name}` started!\n📊 PID: `{process.pid}`"),
            message.chat.id, msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error starting script: {str(e)}"))

def run_js_script(script_path, user_id, user_folder, file_name, message):
    """Run JavaScript script"""
    try:
        msg = bot.reply_to(message, ProgressAnimation.execute_animation()[0])
        
        for i, frame in enumerate(ProgressAnimation.execute_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        
        if not os.path.exists(script_path):
            bot.edit_message_text(B(f"❌ File not found: `{file_name}`"), 
                                message.chat.id, msg.message_id)
            return
        
        # Check for missing NPM modules
        check_command = ['node', script_path]
        check_proc = None
        
        try:
            check_proc = subprocess.Popen(check_command, cwd=user_folder,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        text=True, encoding='utf-8', errors='ignore')
            stdout, stderr = check_proc.communicate(timeout=5)
            
            if stderr and 'Cannot find module' in stderr:
                match = re.search(r"Cannot find module '(.+?)'", stderr)
                if match:
                    module_name = match.group(1)
                    bot.reply_to(message, B(f"📦 Installing `{module_name}`..."))
                    
                    try:
                        subprocess.run(['npm', 'install', module_name], cwd=user_folder,
                                     capture_output=True, text=True, check=True)
                        bot.reply_to(message, B(f"✅ NPM package `{module_name}` installed."))
                        time.sleep(2)
                        run_js_script(script_path, user_id, user_folder, file_name, message)
                        return
                    except:
                        bot.reply_to(message, B(f"❌ Failed to install `{module_name}`."))
        except subprocess.TimeoutExpired:
            if check_proc:
                check_proc.kill()
                check_proc.communicate()
        
        # Start the script
        log_file_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_file_path, 'w', encoding='utf-8', errors='ignore')
        
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        
        process = subprocess.Popen(
            ['node', script_path],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            startupinfo=startupinfo,
            encoding='utf-8',
            errors='ignore'
        )
        
        script_key = f"{user_id}_{file_name}"
        bot_scripts[script_key] = {
            'process': process,
            'log_file': log_file,
            'file_name': file_name,
            'user_id': user_id,
            'start_time': datetime.now(),
            'type': 'js',
            'script_key': script_key
        }
        
        # Save to recovery database
        recovery_system.save_running_script(user_id, file_name, script_path, process.pid)
        
        bot.edit_message_text(
            B(f"✅ JS script `{file_name}` started!\n📊 PID: `{process.pid}`"),
            message.chat.id, msg.message_id
        )
        
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error starting JS script: {str(e)}"))

# ================================
# DATABASE OPERATIONS
# ================================
DB_LOCK = threading.Lock()

def save_user_file(user_id, file_name, file_type='py'):
    """Save user file to database"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('''INSERT OR REPLACE INTO user_files 
                         (user_id, file_name, file_type, uploaded_at) 
                         VALUES (?, ?, ?, ?)''',
                      (user_id, file_name, file_type, datetime.now().isoformat()))
            conn.commit()
            
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
            
            logger.info(f"💾 Saved file '{file_name}' for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error saving file: {e}")
        finally:
            conn.close()

def remove_user_file_db(user_id, file_name):
    """Remove user file from database"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', 
                      (user_id, file_name))
            conn.commit()
            
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]:
                    del user_files[user_id]
            
            # Remove from recovery database
            recovery_system.remove_running_script(user_id, file_name)
            
            logger.info(f"🗑️ Removed file '{file_name}' for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error removing file: {e}")
        finally:
            conn.close()

def add_active_user(user_id, username=None):
    """Add active user"""
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('''INSERT OR REPLACE INTO active_users 
                         (user_id, username, first_join, last_seen) 
                         VALUES (?, ?, COALESCE((SELECT first_join FROM active_users WHERE user_id = ?), ?), ?)''',
                      (user_id, username, user_id, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            logger.info(f"👤 Added active user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error adding active user: {e}")
        finally:
            conn.close()

def save_subscription(user_id, expiry, tier='premium'):
    """Save subscription"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            expiry_str = expiry.isoformat() if expiry else None
            c.execute('''INSERT OR REPLACE INTO subscriptions 
                         (user_id, expiry, tier, created_at) 
                         VALUES (?, ?, ?, ?)''',
                      (user_id, expiry_str, tier, datetime.now().isoformat()))
            conn.commit()
            user_subscriptions[user_id] = {'expiry': expiry, 'tier': tier}
            logger.info(f"💳 Saved subscription for {user_id}")
        except Exception as e:
            logger.error(f"❌ Error saving subscription: {e}")
        finally:
            conn.close()

def remove_subscription_db(user_id):
    """Remove subscription"""
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions:
                del user_subscriptions[user_id]
            logger.info(f"🗑️ Removed subscription for {user_id}")
        except Exception as e:
            logger.error(f"❌ Error removing subscription: {e}")
        finally:
            conn.close()

# ================================
# COMMAND HANDLERS
# ================================
@bot.message_handler(commands=['start'])
def command_send_welcome(message):
    """Welcome command with referral support and profile picture"""
    user_id = message.from_user.id
    username = message.from_user.username
    add_active_user(user_id, username)
    
    # Update user's username in referral system
    referral_system.update_user_username(user_id, username)
    
    # Check for referral code
    referral_code = None
    if len(message.text.split()) > 1:
        referral_code = message.text.split()[1].strip()
    
    # Process referral
    if referral_code and referral_code.startswith('KHB'):
        try:
            referrer_id = int(referral_code[3:-4])  # Extract user ID from code
            if referrer_id != user_id:
                if referral_system.add_referral(referrer_id, user_id, username):
                    bot.reply_to(message, B(f"🎉 You were referred by user ID: `{referrer_id}`"))
        except:
            pass
    
    tier = get_user_tier(user_id)
    tier_info = TIER_SYSTEM[tier]
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    user_rank = referral_system.get_user_rank(user_id)
    
    # Try to get user's profile photo
    try:
        # Get user profile photos
        user_profile_photos = bot.get_user_profile_photos(user_id, limit=1)
        
        welcome_text = B(f"""
┏━━━━━━━━━━━━━━━━━━━━━━┓
┃   🚀 KAWSAR HOSTING   ┃
┃      VERSION 3.1     ┃
┗━━━━━━━━━━━━━━━━━━━━━━┛

👤 Welcome, {message.from_user.first_name}!
🆔 User ID: `{user_id}`
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}

📊 Referrals: {referral_count}/3
🏆 Rank: #{user_rank if user_rank else "Not ranked"}
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

📢 *Update Channel:* {UPDATE_CHANNEL}
👥 *Join Group:* {UPDATE_GROUP}

⚡ Features:
• Auto-Recovery System
• Tier-Based Hosting
• Python/JS Support
• Real-Time Monitoring
• 🏆 Referral Leaderboard

Use buttons below to navigate.
""")
        
        # If user has profile photo, send it with caption
        if user_profile_photos.total_count > 0:
            file_id = user_profile_photos.photos[0][-1].file_id
            bot.send_photo(message.chat.id, file_id, caption=welcome_text,
                          reply_markup=create_reply_keyboard_main_menu(user_id),
                          parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id, welcome_text,
                           reply_markup=create_reply_keyboard_main_menu(user_id),
                           parse_mode='Markdown')
    
    except Exception as e:
        # Fallback if can't get profile photo
        welcome_text = B(f"""
┏━━━━━━━━━━━━━━━━━━━━━━┓
┃   🚀 KAWSAR HOSTING   ┃
┃      VERSION 3.1     ┃
┗━━━━━━━━━━━━━━━━━━━━━━┛

👤 Welcome, {message.from_user.first_name}!
🆔 User ID: `{user_id}`
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}

📊 Referrals: {referral_count}/3
🏆 Rank: #{user_rank if user_rank else "Not ranked"}
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

📢 *Update Channel:* {UPDATE_CHANNEL}
👥 *Join Group:* {UPDATE_GROUP}

⚡ Features:
• Auto-Recovery System
• Tier-Based Hosting
• Python/JS Support
• Real-Time Monitoring
• 🏆 Referral Leaderboard

Use buttons below to navigate.
""")
        bot.send_message(message.chat.id, welcome_text,
                       reply_markup=create_reply_keyboard_main_menu(user_id),
                       parse_mode='Markdown')

@bot.message_handler(commands=['help'])
def command_help(message):
    """Help command"""
    help_text = B(f"""
🤖 *KAWSAR HOSTING BOT HELP*

*Basic Commands:*
/start - Start the bot
/help - Show this help message
/refer - Get your referral link
/leaderboard - Show referral leaderboard
/stats - Show bot statistics

*Uploading Files:*
• Send a .py, .js, or .zip file
• Bot will auto-install dependencies
• Your script will start automatically

*Auto-Restart System:*
• Premium/Owner: ✅ Always enabled
• Free: Enable by referring 3 friends

*Referral System:*
1. Get your referral link via /refer
2. Share with friends
3. Each referral brings you closer to auto-restart
4. After 3 referrals, auto-restart is enabled!
5. Compete on the 🏆 Leaderboard

*Support:*
📢 Updates: {UPDATE_CHANNEL}
👥 Join Group: {UPDATE_GROUP}
👤 Contact: @{YOUR_USERNAME.replace('@', '')}
""")
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['refer'])
def command_refer(message):
    """Referral command"""
    user_id = message.from_user.id
    tier = get_user_tier(user_id)
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    
    markup, referral_link = create_referral_menu(user_id)
    
    # 🚀 FIXED: Using regular font for referral link (not bold)
    refer_text = B(f"""
🤝 *REFERRAL SYSTEM*

👤 Your ID: `{user_id}`
📊 Referrals: *{referral_count}/3*
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

🔗 *Your Referral Link:*
`{referral_link}`

*How it works:*
1. Share your referral link
2. Each friend who joins via your link counts
3. After 3 referrals, auto-restart is enabled!
4. Your scripts will be automaticaly restarted on bot restart
5. Compete on the 🏆 Leaderboard!

*Benefits:*
✅ Auto-restart enabled
✅ Your scripts stay running 24/7
✅ No manual intervention needed
✅ Compete for top ranks on leaderboard
""")
    
    bot.reply_to(message, refer_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['leaderboard', 'topref'])
def command_leaderboard(message):
    """Show referral leaderboard"""
    top_referrers = referral_system.get_top_referrers(limit=10)
    
    if not top_referrers:
        bot.reply_to(message, B("🏆 No referrals yet. Be the first to refer!"))
        return
    
    leaderboard_text = B("""
🏆 *REFERRAL LEADERBOARD*
━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    for i, referrer in enumerate(top_referrers):
        username = referrer['username'] or f"User {referrer['user_id']}"
        if i < len(medals):
            leaderboard_text += B(f"\n{medals[i]} *{username}*\n")
        else:
            leaderboard_text += B(f"\n{i+1}. *{username}*\n")
        
        leaderboard_text += B(f"   👥 Referrals: `{referrer['count']}` | ")
        leaderboard_text += B("🔄 Auto-Restart: " + ("✅" if referrer['auto_restart'] else "❌") + "\n")
    
    # Add user's rank if they're in the system
    user_id = message.from_user.id
    user_rank = referral_system.get_user_rank(user_id)
    referral_count = referral_system.get_referral_count(user_id)
    
    leaderboard_text += B(f"\n━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    if user_rank:
        leaderboard_text += B(f"👤 *Your Rank:* #{user_rank}\n")
        leaderboard_text += B(f"📊 *Your Referrals:* {referral_count}/3\n")
        leaderboard_text += B(f"🔄 *Auto-Restart:* {'✅ Enabled' if referral_count >= 3 else '❌ Disabled'}\n")
    else:
        leaderboard_text += B(f"👤 *Your Rank:* Not ranked yet\n")
        leaderboard_text += B(f"📊 *Your Referrals:* {referral_count}/3\n")
        leaderboard_text += B(f"🔄 *Auto-Restart:* {'✅ Enabled' if referral_count >= 3 else '❌ Disabled'}\n")
    
    leaderboard_text += B(f"\n🏅 *Need help?* Use /refer to get your link!")
    
    bot.reply_to(message, leaderboard_text, parse_mode='Markdown', reply_markup=create_leaderboard_markup())

@bot.message_handler(commands=['recover'])
def command_recover_scripts(message):
    """Manual recovery command"""
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin permissions required."))
        return
    
    msg = bot.reply_to(message, ProgressAnimation.recovery_animation()[0])
    
    for i, frame in enumerate(ProgressAnimation.recovery_animation()):
        try:
            bot.edit_message_text(frame, message.chat.id, msg.message_id)
            time.sleep(0.3)
        except:
            pass
    
    recovered = recovery_system.recover_all_scripts()
    
    if recovered:
        bot.edit_message_text(
            B(f"✅ Recovery Complete!\n🔄 Recovered: {len(recovered)} scripts"),
            message.chat.id, msg.message_id
        )
    else:
        bot.edit_message_text(
            B("📭 No scripts to recover."),
            message.chat.id, msg.message_id
        )

@bot.message_handler(commands=['stats'])
def command_stats(message):
    """Show statistics"""
    user_id = message.from_user.id
    
    total_users = len(active_users)
    total_files = sum(len(files) for files in user_files.values())
    running_scripts = len([k for k, v in bot_scripts.items() if is_bot_running(v['user_id'], v['file_name'])])
    recovery_count = recovery_system.get_running_count()
    
    # Calculate referral stats
    referral_users = 0
    auto_restart_enabled = 0
    for uid in active_users:
        if referral_system.get_referral_count(uid) > 0:
            referral_users += 1
        if referral_system.is_auto_restart_enabled(uid):
            auto_restart_enabled += 1
    
    stats_text = B(f"""
📊 SYSTEM STATISTICS

👥 Total Users: {total_users}
📁 Total Files: {total_files}
🟢 Running Scripts: {running_scripts}
💾 Recovery Saved: {recovery_count}
🔒 Bot Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}

🎫 Tier Distribution:
• FREE: {len([uid for uid in active_users if get_user_tier(uid) == 'free'])}
• PREMIUM: {len([uid for uid in active_users if get_user_tier(uid) == 'premium'])}
• OWNER/ADMIN: {len([uid for uid in active_users if get_user_tier(uid) == 'owner'])}

🤝 Referral Stats:
• Referring Users: {referral_users}
• Auto-Restart Enabled: {auto_restart_enabled}
• 🏆 Top Referrer: {referral_system.get_top_referrers(limit=1)[0]['count'] if referral_system.get_top_referrers(limit=1) else 0} referrals
""")
    
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['restartall'])
def command_restart_all(message):
    """Restart all user scripts"""
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin permissions required."))
        return
    
    msg = bot.reply_to(message, ProgressAnimation.execute_animation()[0])
    
    restarted = 0
    for user_id, files in user_files.items():
        for file_name, file_type in files:
            if is_bot_running(user_id, file_name):
                # Stop first
                script_key = f"{user_id}_{file_name}"
                if script_key in bot_scripts:
                    kill_process_tree(bot_scripts[script_key])
                    del bot_scripts[script_key]
            
            # Restart
            user_folder = get_user_folder(user_id)
            file_path = os.path.join(user_folder, file_name)
            
            if os.path.exists(file_path):
                if file_type == 'py':
                    threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, message)).start()
                elif file_type == 'js':
                    threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, message)).start()
                
                restarted += 1
                time.sleep(0.5)
    
    bot.edit_message_text(
        B(f"✅ Restarted {restarted} scripts."),
        message.chat.id, msg.message_id
    )

# ================================
# RESTART BOT COMMAND
# ================================
@bot.message_handler(commands=['restartbot'])
def command_restart_bot(message):
    """Restart the bot with notification"""
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin permissions required."))
        return
    
    # Send restart notification to all users
    bot.reply_to(message, B("🚀 Sending restart notifications to all users..."))
    threading.Thread(target=send_restart_notification).start()
    
    # Show animation
    msg = bot.reply_to(message, ProgressAnimation.restart_animation()[0])
    
    for i, frame in enumerate(ProgressAnimation.restart_animation()):
        try:
            bot.edit_message_text(frame, message.chat.id, msg.message_id)
            time.sleep(0.5)
        except:
            pass
    
    # Wait for notifications to send
    time.sleep(5)
    
    bot.edit_message_text(
        B("✅ Restart notifications sent!\n\n🔄 Bot will now restart..."),
        message.chat.id, msg.message_id
    )
    
    # Restart the bot
    time.sleep(2)
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.message_handler(content_types=['document'])
def handle_file_upload(message):
    """Handle file uploads"""
    user_id = message.from_user.id
    
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, B("⚠️ Bot is locked."))
        return
    
    # Check file limit
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    
    if current_files >= file_limit:
        bot.reply_to(message, 
                     B(f"⚠️ File limit reached ({current_files}/{file_limit})."))
        return
    
    doc = message.document
    if not doc.file_name:
        bot.reply_to(message, B("⚠️ No file name provided."))
        return
    
    file_ext = os.path.splitext(doc.file_name)[1].lower()
    if file_ext not in ['.py', '.js', '.zip']:
        bot.reply_to(message, B("⚠️ Unsupported file type. Use .py, .js, or .zip"))
        return
    
    # Show upload animation
    msg = bot.reply_to(message, ProgressAnimation.upload_animation()[0])
    
    try:
        # Download file
        for i, frame in enumerate(ProgressAnimation.upload_animation()):
            try:
                bot.edit_message_text(frame, message.chat.id, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, doc.file_name)
        
        with open(file_path, 'wb') as f:
            f.write(downloaded_file)
        
        # Handle file based on type
        if file_ext == '.zip':
            handle_zip_file(downloaded_file, doc.file_name, user_id, user_folder, message)
        elif file_ext == '.py':
            save_user_file(user_id, doc.file_name, 'py')
            threading.Thread(target=run_script, args=(file_path, user_id, user_folder, doc.file_name, message)).start()
        elif file_ext == '.js':
            save_user_file(user_id, doc.file_name, 'js')
            threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, doc.file_name, message)).start()
        
    except Exception as e:
        bot.edit_message_text(
            B(f"❌ Error uploading file: {str(e)}"),
            message.chat.id, msg.message_id
        )

def handle_zip_file(file_content, file_name, user_id, user_folder, message):
    """Handle ZIP file upload"""
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, file_name)
        
        with open(zip_path, 'wb') as f:
            f.write(file_content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find main script
        extracted_files = os.listdir(temp_dir)
        py_files = [f for f in extracted_files if f.endswith('.py')]
        js_files = [f for f in extracted_files if f.endswith('.js')]
        
        main_script = None
        file_type = None
        
        # Check for common main file names
        for name in ['main.py', 'bot.py', 'app.py']:
            if name in py_files:
                main_script = name
                file_type = 'py'
                break
        
        if not main_script and py_files:
            main_script = py_files[0]
            file_type = 'py'
        elif not main_script and js_files:
            for name in ['index.js', 'main.js', 'bot.js']:
                if name in js_files:
                    main_script = name
                    file_type = 'js'
                    break
            if not main_script and js_files:
                main_script = js_files[0]
                file_type = 'js'
        
        if not main_script:
            bot.reply_to(message, B("❌ No .py or .js file found in ZIP."))
            return
        
        # Move files to user folder
        for item in os.listdir(temp_dir):
            src = os.path.join(temp_dir, item)
            dst = os.path.join(user_folder, item)
            
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
        
        # Save and run
        save_user_file(user_id, main_script, file_type)
        main_script_path = os.path.join(user_folder, main_script)
        
        if file_type == 'py':
            threading.Thread(target=run_script, args=(main_script_path, user_id, user_folder, main_script, message)).start()
        else:
            threading.Thread(target=run_js_script, args=(main_script_path, user_id, user_folder, main_script, message)).start()
        
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error processing ZIP: {str(e)}"))
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# ================================
# TEXT HANDLERS (Reply Keyboard)
# ================================
BUTTON_HANDLERS = {
    B("📢 Updates"): lambda m: bot.reply_to(m, f"📢 *Update Channel:* {UPDATE_CHANNEL}\n👥 *Join Group:* {UPDATE_GROUP}", parse_mode='Markdown'),
    B("👥 Join Group"): lambda m: bot.reply_to(m, f"👥 *Join our group:* {UPDATE_GROUP}", parse_mode='Markdown'),
    B("📤 Upload"): lambda m: bot.reply_to(m, B("📤 Send your .py, .js, or .zip file.")),
    B("📂 My Files"): lambda m: show_user_files(m),
    B("⚡ Speed"): lambda m: check_speed(m),
    B("📊 Stats"): lambda m: command_stats(m),
    B("👤 Profile"): lambda m: show_profile(m),
    B("🤝 Refer"): lambda m: command_refer(m),
    B("🏆 Leaderboard"): lambda m: command_leaderboard(m),
    B("🔄 Restart All"): lambda m: command_restart_all(m),
    B("👑 Admin"): lambda m: show_admin_panel(m),
    B("💳 Subs"): lambda m: show_subscription_panel(m),
    B("📢 Broadcast"): lambda m: start_broadcast(m),
    B("🔄 Recover"): lambda m: command_recover_scripts(m),
    B("🚀 Restart Bot"): lambda m: command_restart_bot(m),
    B("📞 Contact"): lambda m: bot.reply_to(m, f"📞 *Contact:* @{YOUR_USERNAME.replace('@', '')}", parse_mode='Markdown')
}

@bot.message_handler(func=lambda message: message.text in BUTTON_HANDLERS)
def handle_button_click(message):
    """Handle reply keyboard buttons"""
    handler = BUTTON_HANDLERS.get(message.text)
    if handler:
        handler(message)

def show_user_files(message):
    """Show user's files"""
    user_id = message.from_user.id
    files = user_files.get(user_id, [])
    
    if not files:
        bot.reply_to(message, B("📭 No files uploaded yet."))
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in files:
        is_running = is_bot_running(user_id, file_name)
        status = "🟢" if is_running else "🔴"
        btn_text = B(f"{status} {file_name} ({file_type})")
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    
    bot.reply_to(message, B("📂 Your Files:"), reply_markup=markup)

def check_speed(message):
    """Check bot speed"""
    start_time = time.time()
    msg = bot.reply_to(message, B("🏃 Checking speed..."))
    latency = round((time.time() - start_time) * 1000, 2)
    
    bot.edit_message_text(
        B(f"⚡ Bot Speed\n\n⏱️ Latency: {latency}ms\n🔒 Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}"),
        message.chat.id, msg.message_id
    )

def show_profile(message):
    """Show user profile"""
    user_id = message.from_user.id
    tier = get_user_tier(user_id)
    tier_info = TIER_SYSTEM[tier]
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    user_rank = referral_system.get_user_rank(user_id)
    
    profile_text = B(f"""
👤 PROFILE

🆔 User ID: `{user_id}`
👤 Name: {message.from_user.first_name}
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}
🟢 Running: {len([1 for f in user_files.get(user_id, []) if is_bot_running(user_id, f[0])])}

🤝 Referrals: {referral_count}/3
🏆 Rank: #{user_rank if user_rank else "Not ranked"}
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

*Auto-Restart Info:*
• Premium/Owner: ✅ Always enabled
• Free: Requires 3 referrals

*Referral Benefits:*
✅ Auto-restart enabled
✅ Compete on leaderboard
✅ Showcase your referring power!
""")
    
    bot.reply_to(message, profile_text, parse_mode='Markdown')

def show_admin_panel(message):
    """Show admin panel"""
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin permissions required."))
        return
    
    bot.reply_to(message, B("👑 ADMIN PANEL"), reply_markup=create_admin_panel())

def show_subscription_panel(message):
    """Show subscription panel"""
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin permissions required."))
        return
    
    bot.reply_to(message, B("💳 SUBSCRIPTION MANAGEMENT"), 
                 reply_markup=create_subscription_menu())

def start_broadcast(message):
    """Start broadcast"""
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, B("⚠️ Admin permissions required."))
        return
    
    bot.reply_to(message, B("📢 Send the message you want to broadcast."))
    bot.register_next_step_handler(message, process_broadcast_message)

def process_broadcast_message(message):
    """Process broadcast message"""
    if message.from_user.id not in admin_ids:
        return
    
    broadcast_text = message.text or message.caption
    if not broadcast_text:
        bot.reply_to(message, B("⚠️ No mesgage found."))
        return
    
    # Confirmation
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(B('✅ Confirm'), callback_data=f'broadcast_confirm_{message.message_id}'),
        types.InlineKeyboardButton(B('❌ Cancel'), callback_data='broadcast_cancel')
    )
    
    preview_text = broadcast_text[:1000].strip() if broadcast_text else "(Media message)"
    bot.reply_to(message, 
                 B(f"📢 Broadcast to {len(active_users)} users?\n\n{preview_text}"), 
                 reply_markup=markup)

# ================================
# CALLBACK QUERY HANDLERS
# ================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    """Handle all callback queries"""
    user_id = call.from_user.id
    data = call.data
    
    try:
        if data == 'upload':
            upload_callback(call)
        elif data == 'check_files':
            check_files_callback(call)
        elif data.startswith('file_'):
            file_control_callback(call)
        elif data.startswith('start_'):
            start_bot_callback(call)
        elif data.startswith('stop_'):
            stop_bot_callback(call)
        elif data.startswith('restart_'):
            restart_bot_callback(call)
        elif data.startswith('delete_'):
            delete_bot_callback(call)
        elif data.startswith('logs_'):
            logs_bot_callback(call)
        elif data == 'speed':
            speed_callback(call)
        elif data == 'stats':
            stats_callback(call)
        elif data == 'profile':
            profile_callback(call)
        elif data == 'refer':
            refer_callback(call)
        elif data == 'leaderboard':
            leaderboard_callback(call)
        elif data == 'refresh_leaderboard':
            refresh_leaderboard_callback(call)
        elif data == 'my_rank':
            my_rank_callback(call)
        elif data.startswith('copy_referral_'):
            copy_referral_callback(call)
        elif data.startswith('qr_referral_'):
            qr_referral_callback(call)
        elif data.startswith('check_referrals_'):
            check_referrals_callback(call)
        elif data == 'restart_all':
            restart_all_callback(call)
        elif data == 'admin_panel':
            admin_panel_callback(call)
        elif data == 'subscription':
            subscription_callback(call)
        elif data == 'broadcast':
            broadcast_callback(call)
        elif data == 'lock_bot':
            lock_bot_callback(call)
        elif data == 'unlock_bot':
            unlock_bot_callback(call)
        elif data == 'recover_all':
            recover_all_callback(call)
        elif data == 'analytics':
            analytics_callback(call)
        elif data == 'add_admin':
            add_admin_callback(call)
        elif data == 'remove_admin':
            remove_admin_callback(call)
        elif data == 'list_admins':
            list_admins_callback(call)
        elif data == 'system_stats':
            system_stats_callback(call)
        elif data == 'add_subscription':
            add_subscription_callback(call)
        elif data == 'remove_subscription':
            remove_subscription_callback(call)
        elif data == 'check_subscription':
            check_subscription_callback(call)
        elif data.startswith('broadcast_confirm_'):
            broadcast_confirm_callback(call)
        elif data == 'broadcast_cancel':
            broadcast_cancel_callback(call)
        elif data == 'restart_bot':
            restart_bot_callback_callback(call)
        elif data == 'back_to_main':
            back_to_main_callback(call)
        else:
            bot.answer_callback_query(call.id, "❌ Unknown command")
            
    except Exception as e:
        logger.error(f"❌ Error in callback: {e}")
        bot.answer_callback_query(call.id, "❌ Error processing request")

def upload_callback(call):
    """Handle upload callback"""
    user_id = call.from_user.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    
    if current_files >= file_limit:
        bot.answer_callback_query(call.id, 
                                 B(f"⚠️ File limit reached ({current_files}/{file_limit})"), 
                                 show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("📤 Send your .py, .js, or .zip file."))

def check_files_callback(call):
    """Handle check files callback"""
    user_id = call.from_user.id
    files = user_files.get(user_id, [])
    
    if not files:
        bot.answer_callback_query(call.id, B("📭 No files uploaded"), show_alert=True)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for file_name, file_type in files:
        is_running = is_bot_running(user_id, file_name)
        status = "🟢" if is_running else "🔴"
        btn_text = B(f"{status} {file_name} ({file_type})")
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f'file_{user_id}_{file_name}'))
    
    markup.add(types.InlineKeyboardButton(B("🔙 Back"), callback_data='back_to_main'))
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(B("📂 Your Files:"), 
                         call.message.chat.id, call.message.message_id, 
                         reply_markup=markup)

def file_control_callback(call):
    """Handle file control callback"""
    try:
        parts = call.data.split('_')
        if len(parts) < 3:
            return
        
        user_id = int(parts[1])
        file_name = '_'.join(parts[2:])
        
        # Check permission
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        files = user_files.get(user_id, [])
        file_info = None
        for fname, ftype in files:
            if fname == file_name:
                file_info = (fname, ftype)
                break
        
        if not file_info:
            bot.answer_callback_query(call.id, B("❌ File not found"), show_alert=True)
            return
        
        is_running = is_bot_running(user_id, file_name)
        
        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            B(f"⚙️ Controls for: `{file_name}`\n📁 Type: {file_info[1]}\n📊 Status: {'🟢 Running' if is_running else '🔴 Stopped'}"),
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(user_id, file_name, is_running),
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"❌ Error in file control: {e}")
        bot.answer_callback_query(call.id, B("❌ Error processing"))

def start_bot_callback(call):
    """Handle start bot callback"""
    try:
        parts = call.data.split('_')
        user_id = int(parts[1])
        file_name = '_'.join(parts[2:])
        
        # Check permission
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        if is_bot_running(user_id, file_name):
            bot.answer_callback_query(call.id, B("✅ Already running"), show_alert=True)
            return
        
        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)
        
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, B("❌ File not found"), show_alert=True)
            return
        
        # Find file type
        file_type = 'py'
        for fname, ftype in user_files.get(user_id, []):
            if fname == file_name:
                file_type = ftype
                break
        
        bot.answer_callback_query(call.id, B("🚀 Starting script..."))
        
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
        else:
            bot.answer_callback_query(call.id, B("❌ Unsupported file type"), show_alert=True)
            
    except Exception as e:
        logger.error(f"❌ Error starting script: {e}")
        bot.answer_callback_query(call.id, B("❌ Error starting script"))

def stop_bot_callback(call):
    """Handle stop bot callback"""
    try:
        parts = call.data.split('_')
        user_id = int(parts[1])
        file_name = '_'.join(parts[2:])
        
        # Check permission
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        if not is_bot_running(user_id, file_name):
            bot.answer_callback_query(call.id, B("✅ Already stopped"), show_alert=True)
            return
        
        script_key = f"{user_id}_{file_name}"
        if script_key in bot_scripts:
            kill_process_tree(bot_scripts[script_key])
            if script_key in bot_scripts:
                del bot_scripts[script_key]
        
        bot.answer_callback_query(call.id, B("🛑 Stopped script"))
        
        # Update buttons
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id,
            reply_markup=create_control_buttons(user_id, file_name, False)
        )
        
    except Exception as e:
        logger.error(f"❌ Error stopping script: {e}")
        bot.answer_callback_query(call.id, B("❌ Error stopping script"))

def restart_bot_callback(call):
    """Handle restart bot callback"""
    try:
        parts = call.data.split('_')
        user_id = int(parts[1])
        file_name = '_'.join(parts[2:])
        
        # Check permission
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        # Stop first
        if is_bot_running(user_id, file_name):
            script_key = f"{user_id}_{file_name}"
            if script_key in bot_scripts:
                kill_process_tree(bot_scripts[script_key])
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            time.sleep(1)
        
        # Start again
        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)
        
        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, B("❌ File not found"), show_alert=True)
            return
        
        # Find file type
        file_type = 'py'
        for fname, ftype in user_files.get(user_id, []):
            if fname == file_name:
                file_type = ftype
                break
        
        bot.answer_callback_query(call.id, B("🔄 Restarting script..."))
        
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
            
    except Exception as e:
        logger.error(f"❌ Error restarting script: {e}")
        bot.answer_callback_query(call.id, B("❌ Error restarting script"))

def delete_bot_callback(call):
    """Handle delete bot callback"""
    try:
        parts = call.data.split('_')
        user_id = int(parts[1])
        file_name = '_'.join(parts[2:])
        
        # Check permission
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        # Stop if running
        if is_bot_running(user_id, file_name):
            script_key = f"{user_id}_{file_name}"
            if script_key in bot_scripts:
                kill_process_tree(bot_scripts[script_key])
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
        
        # Delete files
        user_folder = get_user_folder(user_id)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(log_path):
            os.remove(log_path)
        
        # Remove from database
        remove_user_file_db(user_id, file_name)
        
        bot.answer_callback_query(call.id, B("🗑️ File deleted"))
        
        # Go back to files list
        check_files_callback(call)
        
    except Exception as e:
        logger.error(f"❌ Error deleting file: {e}")
        bot.answer_callback_query(call.id, B("❌ Error deleting file"))

def logs_bot_callback(call):
    """Handle logs bot callback"""
    try:
        parts = call.data.split('_')
        user_id = int(parts[1])
        file_name = '_'.join(parts[2:])
        
        # Check permission
        if call.from_user.id != user_id and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        user_folder = get_user_folder(user_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, B("📭 No logs found"), show_alert=True)
            return
        
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                log_content = f.read()
            
            if len(log_content) > 3000:
                log_content = log_content[-3000:]
                log_content = "...\n" + log_content
            
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, 
                           B(f"📜 Logs for `{file_name}`:\n```\n{log_content}\n```"), 
                           parse_mode='Markdown')
            
        except Exception as e:
            bot.answer_callback_query(call.id, B("❌ Error reading logs"))
            
    except Exception as e:
        logger.error(f"❌ Error getting logs: {e}")
        bot.answer_callback_query(call.id, B("❌ Error getting logs"))

def speed_callback(call):
    """Handle speed callback"""
    start_time = time.time()
    bot.answer_callback_query(call.id)
    latency = round((time.time() - start_time) * 1000, 2)
    
    bot.edit_message_text(
        B(f"⚡ Bot Speed\n\n⏱️ Latency: {latency}ms\n🔒 Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}"),
        call.message.chat.id, call.message.message_id
    )

def stats_callback(call):
    """Handle stats callback"""
    user_id = call.from_user.id
    
    total_users = len(active_users)
    total_files = sum(len(files) for files in user_files.values())
    running_scripts = len([k for k, v in bot_scripts.items() if is_bot_running(v['user_id'], v['file_name'])])
    recovery_count = recovery_system.get_running_count()
    
    # Calculate referral stats
    referral_users = 0
    auto_restart_enabled = 0
    for uid in active_users:
        if referral_system.get_referral_count(uid) > 0:
            referral_users += 1
        if referral_system.is_auto_restart_enabled(uid):
            auto_restart_enabled += 1
    
    stats_text = B(f"""
📊 SYSTEM STATISTICS

👥 Total Users: {total_users}
📁 Total Files: {total_files}
🟢 Running Scripts: {running_scripts}
💾 Recovery Saved: {recovery_count}
🔒 Bot Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}

🎫 Tier Distribution:
• FREE: {len([uid for uid in active_users if get_user_tier(uid) == 'free'])}
• PREMIUM: {len([uid for uid in active_users if get_user_tier(uid) == 'premium'])}
• OWNER/ADMIN: {len([uid for uid in active_users if get_user_tier(uid) == 'owner'])}

🤝 Referral Stats:
• Referring Users: {referral_users}
• Auto-Recovery Enabled: {auto_restart_enabled}
""")
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id, 
                         parse_mode='Markdown')

def profile_callback(call):
    """Handle profile callback"""
    user_id = call.from_user.id
    tier = get_user_tier(user_id)
    tier_info = TIER_SYSTEM[tier]
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    user_rank = referral_system.get_user_rank(user_id)
    
    profile_text = B(f"""
👤 PROFILE

🆔 User ID: `{user_id}`
👤 Name: {call.from_user.first_name}
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}
🟢 Running: {len([1 for f in user_files.get(user_id, []) if is_bot_running(user_id, f[0])])}

🤝 Referrals: {referral_count}/3
🏆 Rank: #{user_rank if user_rank else "Not ranked"}
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

*Auto-Restart Info:*
• Premium/Owner: ✅ Always enabled
• Free: Requires 3 referrals
""")
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(profile_text, call.message.chat.id, call.message.message_id, 
                         parse_mode='Markdown')

def refer_callback(call):
    """Handle referral callback"""
    user_id = call.from_user.id
    tier = get_user_tier(user_id)
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    
    markup, referral_link = create_referral_menu(user_id)
    
    # 🚀 FIXED: Using regular font for referral link (not bold)
    refer_text = B(f"""
🤝 *REFERRAL SYSTEM*

👤 Your ID: `{user_id}`
📊 Referrals: *{referral_count}/3*
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

🔗 *Your Referral Link:*
`{referral_link}`

*How it works:*
1. Share your referral link
2. Each friend who joins via your link counts
3. After 3 referrals, auto-restart is enabled!
4. Your scripts will be automaticaly restarted on bot restart
5. Compete on the 🏆 Leaderboard!

*Benefits:*
✅ Auto-restart enabled
✅ Your scripts stay running 24/7
✅ No manual intervention needed
✅ Compete for top ranks on leaderboard
""")
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(refer_text, call.message.chat.id, call.message.message_id, 
                         parse_mode='Markdown', reply_markup=markup)

def leaderboard_callback(call):
    """Handle leaderboard callback"""
    command_leaderboard(call.message)
    bot.answer_callback_query(call.id)

def refresh_leaderboard_callback(call):
    """Handle refresh leaderboard callback"""
    leaderboard_callback(call)

def my_rank_callback(call):
    """Handle my rank callback"""
    user_id = call.from_user.id
    user_rank = referral_system.get_user_rank(user_id)
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id)
    
    if user_rank:
        rank_text = B(f"""
🏆 *YOUR RANK*

📊 *Rank:* #{user_rank}
👥 *Referrals:* {referral_count}/3
🔄 *Auto-Restart:* {'✅ Enabled' if auto_restart else '❌ Disabled'}

*Needed for auto-restart:* {max(0, 3 - referral_count)} more referrals

*Status:* {'🎯 Achieved!' if auto_restart else '🏃 Keep going!'}
""")
    else:
        rank_text = B(f"""
🏆 *YOUR RANK*

📊 *Rank:* Not ranked yet
👥 *Referrals:* {referral_count}/3
🔄 *Auto-Restart:* {'✅ Enabled' if auto_restart else '❌ Disabled'}

*Needed for auto-restart:* {max(0, 3 - referral_count)} more referrals

*Status:* Start referring to join leaderboard! 🚀
""")
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, rank_text, parse_mode='Markdown')

def copy_referral_callback(call):
    """Handle copy referral link"""
    try:
        user_id = int(call.data.split('_')[2])
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        referral_code = referral_system.get_referral_code(user_id)
        bot_username = bot.get_me().username
        # 🚀 FIXED: Using regular font for referral link (not bold)
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        bot.answer_callback_query(call.id, B(f"🔗 Copied referral link!"), show_alert=True)
        
        # Send the link as a message (using regular font)
        bot.send_message(call.message.chat.id, 
                       f"🔗 *Your Referral Link:*\n\n{referral_link}\n\n*Share this link with your friends!*", 
                       parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error copying referral link: {e}")
        bot.answer_callback_query(call.id, B("❌ Error copying link"))

def qr_referral_callback(call):
    """Handle QR code for referral link"""
    try:
        user_id = int(call.data.split('_')[2])
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        referral_code = referral_system.get_referral_code(user_id)
        bot_username = bot.get_me().username
        # 🚀 FIXED: Using regular font for referral link in QR code
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(referral_link)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        
        bot.answer_callback_query(call.id, B("📱 Generating QR code..."))
        
        # Send QR code
        bot.send_photo(call.message.chat.id, photo=bio, 
                      caption=f"📱 *QR Code for your referral link*\n\n*Link:* {referral_link}\n\n*Scan this QR code to join KAWSAR Hosting!*",
                      parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error generating QR code: {e}")
        bot.answer_callback_query(call.id, B("❌ Error generating QR code"))

def check_referrals_callback(call):
    """Handle check referrals"""
    try:
        user_id = int(call.data.split('_')[2])
        if call.from_user.id != user_id:
            bot.answer_callback_query(call.id, B("⚠️ Permission denied"), show_alert=True)
            return
        
        referral_info = referral_system.get_user_referral_info(user_id)
        
        if not referral_info:
            referrals_text = B(f"""
📊 *Your Referral Stats*

👥 Total Referrals: *0/3*
🏆 Rank: Not ranked yet
🔄 Auto-Restart: ❌ Disabled

*Needed for auto-restart:* 3 more referrals

*Begin referring today and enjoy:*
✅ Auto-restart enabled
✅ 24/7 uptime for your scripts
✅ Compete on leaderboard
""")
        else:
            referrals = referral_info.get('referrals', [])
            referral_count = referral_info.get('count', 0)
            auto_restart = referral_info.get('auto_restart_enabled', False)
            rank = referral_info.get('rank', 'Not ranked')
            
            referrals_text = B(f"""
📊 *Your Referral Stats*

👥 Total Referrals: *{referral_count}/3*
🏆 Rank: #{rank if rank else "Not ranked"}
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

*Needed for auto-restart:* {max(0, 3 - referral_count)} more referrals

*Benefits of auto-restart:*
✅ Scripts auto-restart on bot reboot
✅ 24/7 uptime
✅ No manual intervention required
✅ Compete for top ranks
""")
            
            if referrals:
                referrals_text += B("\n*Your Referred Users:*\n")
                for i, ref in enumerate(referrals[:5], 1):
                    username = ref.get('username', f"User {ref.get('user_id')}")
                    referrals_text += B(f"{i}. {username}\n")
                
                if len(referrals) > 5:
                    referrals_text += B(f"... and {len(referrals) - 5} more\n")
        
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, referrals_text, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"❌ Error checking referrals: {e}")
        bot.answer_callback_query(call.id, B("❌ Error checking referrals"))

def restart_all_callback(call):
    """Handle restart all callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    msg = bot.send_message(call.message.chat.id, ProgressAnimation.execute_animation()[0])
    
    restarted = 0
    for user_id, files in user_files.items():
        for file_name, file_type in files:
            if is_bot_running(user_id, file_name):
                # Stop first
                script_key = f"{user_id}_{file_name}"
                if script_key in bot_scripts:
                    kill_process_tree(bot_scripts[script_key])
                    del bot_scripts[script_key]
            
            # Restart
            user_folder = get_user_folder(user_id)
            file_path = os.path.join(user_folder, file_name)
            
            if os.path.exists(file_path):
                if file_type == 'py':
                    threading.Thread(target=run_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
                elif file_type == 'js':
                    threading.Thread(target=run_js_script, args=(file_path, user_id, user_folder, file_name, call.message)).start()
                
                restarted += 1
                time.sleep(0.5)
    
    bot.edit_message_text(
        B(f"✅ Restarted {restarted} scripts."),
        call.message.chat.id, msg.message_id
    )
    bot.answer_callback_query(call.id)

def admin_panel_callback(call):
    """Handle admin panel callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(B("👑 ADMIN PANEL"), 
                         call.message.chat.id, call.message.message_id,
                         reply_markup=create_admin_panel())

def subscription_callback(call):
    """Handle subscription callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(B("💳 SUBSCRIPTION MANAGEMENT"), 
                         call.message.chat.id, call.message.message_id,
                         reply_markup=create_subscription_menu())

def broadcast_callback(call):
    """Handle broadcast callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("📢 Send the message you want to broadcast."))
    bot.register_next_step_handler(call.message, process_broadcast_message)

def lock_bot_callback(call):
    """Handle lock bot callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    global bot_locked
    bot_locked = True
    
    bot.answer_callback_query(call.id, B("🔒 Bot locked"))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                 reply_markup=create_main_menu_inline(call.from_user.id))

def unlock_bot_callback(call):
    """Handle unlock bot callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    global bot_locked
    bot_locked = False
    
    bot.answer_callback_query(call.id, B("🔓 Bot unlocked"))
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                 reply_markup=create_main_menu_inline(call.from_user.id))

def recover_all_callback(call):
    """Handle recover all callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    msg = bot.send_message(call.message.chat.id, ProgressAnimation.recovery_animation()[0])
    
    for i, frame in enumerate(ProgressAnimation.recovery_animation()):
        try:
            bot.edit_message_text(frame, call.message.chat.id, msg.message_id)
            time.sleep(0.3)
        except:
            pass
    
    recovered = recovery_system.recover_all_scripts()
    
    if recovered:
        bot.edit_message_text(
            B(f"✅ Recovery Complete!\n🔄 Recovered: {len(recovered)} scripts"),
            call.message.chat.id, msg.message_id
        )
    else:
        bot.edit_message_text(
            B("📭 No scripts to recover."),
            call.message.chat.id, msg.message_id
        )
    
    bot.answer_callback_query(call.id)

def analytics_callback(call):
    """Handle analytics callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    # Calculate analytics
    total_users = len(active_users)
    total_files = sum(len(files) for files in user_files.values())
    running_scripts = len([k for k, v in bot_scripts.items() if is_bot_running(v['user_id'], v['file_name'])])
    
    # Calculate referral stats
    referral_users = 0
    auto_restart_enabled = 0
    total_referrals = 0
    for uid in active_users:
        count = referral_system.get_referral_count(uid)
        if count > 0:
            referral_users += 1
            total_referrals += count
        if referral_system.is_auto_restart_enabled(uid):
            auto_restart_enabled += 1
    
    # Calculate storage usage
    total_storage = 0
    for user_id in user_files:
        user_folder = get_user_folder(user_id)
        if os.path.exists(user_folder):
            for root, dirs, files in os.walk(user_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_storage += os.path.getsize(file_path)
    
    total_storage_mb = round(total_storage / (1024 * 1024), 2)
    
    # Calculate leaderboard stats
    top_referrers = referral_system.get_top_referrers(limit=5)
    leaderboard_stats = ""
    for i, referrer in enumerate(top_referrers, 1):
        username = referrer['username'] or f"User {referrer['user_id']}"
        leaderboard_stats += B(f"{i}. {username}: {referrer['count']} referrals\n")
    
    analytics_text = B(f"""
📈 ADVANCED ANALYTICS

👥 User Metrics:
• Total Users: {total_users}
• Active Today: {len([uid for uid in active_users])}
• Referring Users: {referral_users}

📊 Referral Metrics:
• Total Referrals: {total_referrals}
• Auto-Restart Enabled: {auto_restart_enabled}
• Conversion Rate: {round(referral_users/max(total_users, 1)*100, 1)}%

🏆 Top Referrers:
{leaderboard_stats}

📁 Storage Analytics:
• Total Files: {total_files}
• Total Storage: {total_storage_mb} MB
• Avg Files per User: {round(total_files/max(total_users, 1), 1)}

🚀 Performance:
• Running Scripts: {running_scripts}
• Max Concurrent: {50}
• Success Rate: 98.5%

🎫 Revenue Metrics:
• Premium Users: {len([uid for uid in active_users if get_user_tier(uid) == 'premium'])}
• Conversion Rate: {round(len([uid for uid in active_users if get_user_tier(uid) == 'premium'])/max(total_users, 1)*100, 1)}%
""")
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(analytics_text, call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown')

def add_admin_callback(call):
    """Handle add admin callback"""
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, B("⚠️ Only owner can add admins"), show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("👑 Enter user ID to add as admin:"))
    bot.register_next_step_handler(call.message, process_add_admin)

def process_add_admin(message):
    """Process adding admin"""
    if message.from_user.id != OWNER_ID:
        return
    
    try:
        admin_id = int(message.text.strip())
        
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO admins (user_id, added_by, added_at) VALUES (?, ?, ?)',
                      (admin_id, message.from_user.id, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        
        admin_ids.add(admin_id)
        bot.reply_to(message, B(f"✅ User `{admin_id}` added as admin."))
        
    except ValueError:
        bot.reply_to(message, B("❌ Invalid user ID."))
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error: {str(e)}"))

def remove_admin_callback(call):
    """Handle remove admin callback"""
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, B("⚠️ Only owner can remove admins"), show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("👑 Enter user ID to remove admin:"))
    bot.register_next_step_handler(call.message, process_remove_admin)

def process_remove_admin(message):
    """Process removing admin"""
    if message.from_user.id != OWNER_ID:
        return
    
    try:
        admin_id = int(message.text.strip())
        
        if admin_id == OWNER_ID:
            bot.reply_to(message, B("❌ Cannot remove owner."))
            return
        
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            c = conn.cursor()
            c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
            conn.commit()
            conn.close()
        
        admin_ids.discard(admin_id)
        bot.reply_to(message, B(f"✅ User `{admin_id}` removed from admins."))
        
    except ValueError:
        bot.reply_to(message, B("❌ Invalid user ID."))
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error: {str(e)}"))

def list_admins_callback(call):
    """Handle list admins callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    admin_list = "\n".join([f"• `{admin_id}` {'👑' if admin_id == OWNER_ID else ''}" for admin_id in sorted(admin_ids)])
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(B(f"👑 Current Admins:\n\n{admin_list}"), 
                         call.message.chat.id, call.message.message_id,
                         parse_mode='Markdown')

def system_stats_callback(call):
    """Handle system stats callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    # System information
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Bot information
    total_users = len(active_users)
    total_files = sum(len(files) for files in user_files.values())
    running_scripts = len([k for k, v in bot_scripts.items() if is_bot_running(v['user_id'], v['file_name'])])
    
    stats_text = B(f"""
🖥️ SYSTEM STATUS

CPU Usage: {cpu_percent}%
Memory: {memory.percent}% ({round(memory.used/(1024**3), 1)}GB / {round(memory.total/(1024**3), 1)}GB)
Disk: {disk.percent}% ({round(disk.used/(1024**3), 1)}GB / {round(disk.total/(1024**3), 1)}GB)

🤖 BOT STATS
Users: {total_users}
Files: {total_files}
Running: {running_scripts}
Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}

📊 PERFORMANCE
Uptime: {round(time.time() - psutil.boot_time())}s
Processes: {len(psutil.pids())}
Threads: {threading.active_count()}
""")
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(stats_text, call.message.chat.id, call.message.message_id)

def add_subscription_callback(call):
    """Handle add subscription callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("💳 Enter user ID and days (e.g., 123456 30):"))
    bot.register_next_step_handler(call.message, process_add_subscription)

def process_add_subscription(message):
    """Process adding subscription"""
    if message.from_user.id not in admin_ids:
        return
    
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            bot.reply_to(message, B("❌ Invalid format. Use: user_id days"))
            return
        
        user_id = int(parts[0])
        days = int(parts[1])
        
        expiry = datetime.now() + timedelta(days=days)
        save_subscription(user_id, expiry, 'premium')
        
        bot.reply_to(message, B(f"✅ Subscription added for user `{user_id}`\n📅 Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}"))
        
    except ValueError:
        bot.reply_to(message, B("❌ Invalid user ID or days."))
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error: {str(e)}"))

def remove_subscription_callback(call):
    """Handle remove subscription callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("💳 Enter user ID to remove subscription:"))
    bot.register_next_step_handler(call.message, process_remove_subscription)

def process_remove_subscription(message):
    """Process removing subscription"""
    if message.from_user.id not in admin_ids:
        return
    
    try:
        user_id = int(message.text.strip())
        remove_subscription_db(user_id)
        
        bot.reply_to(message, B(f"✅ Subscription removed for user `{user_id}`"))
        
    except ValueError:
        bot.reply_to(message, B("❌ Invalid user ID."))
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error: {str(e)}"))

def check_subscription_callback(call):
    """Handle check subscription callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions reoquired"), show_alert=True)
        return
    
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, B("💳 Enter user ID to check subscription:"))
    bot.register_next_step_handler(call.message, process_check_subscription)

def process_check_subscription(message):
    """Process checking subscription"""
    if message.from_user.id not in admin_ids:
        return
    
    try:
        user_id = int(message.text.strip())
        
        if user_id in user_subscriptions:
            sub = user_subscriptions[user_id]
            expiry = sub.get('expiry')
            tier = sub.get('tier', 'premium')
            
            if expiry and expiry > datetime.now():
                days_left = (expiry - datetime.now()).days
                bot.reply_to(message, B(f"✅ User `{user_id}` has active subscription.\n🎫 Tier: {tier}\n📅 Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}\n⏳ Days left: {days_left}"))
            else:
                bot.reply_to(message, B(f"⚠️ User `{user_id}` has expired subscription.\n📅 Expired: {expiry.strftime('%Y-%m-%d %H:%M:%S') if expiry else 'Unknown'}"))
                remove_subscription_db(user_id)
        else:
            bot.reply_to(message, B(f"📭 User `{user_id}` has no subscription."))
        
    except ValueError:
        bot.reply_to(message, B("❌ Invalid user ID."))
    except Exception as e:
        bot.reply_to(message, B(f"❌ Error: {str(e)}"))

def broadcast_confirm_callback(call):
    """Handle broadcast confirm callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    try:
        message_id = int(call.data.split('_')[-1])
        original_message = call.message.reply_to_message
        
        if not original_message:
            bot.answer_callback_query(call.id, B("❌ Could not find original message"), show_alert=True)
            return
        
        bot.answer_callback_query(call.id, B("🚀 Starting broadcast..."))
        
        # Send to all users
        sent = 0
        failed = 0
        
        for user_id in list(active_users):
            try:
                if original_message.text:
                    bot.send_message(user_id, original_message.text)
                elif original_message.caption:
                    if original_message.photo:
                        bot.send_photo(user_id, original_message.photo[-1].file_id, caption=original_message.caption)
                    elif original_message.video:
                        bot.send_video(user_id, original_message.video.file_id, caption=original_message.caption)
                    elif original_message.document:
                        bot.send_document(user_id, original_message.document.file_id, caption=original_message.caption)
                sent += 1
            except:
                failed += 1
            
            time.sleep(0.1)  # Avoid rate limiting
        
        bot.edit_message_text(
            B(f"✅ Broadcast complete!\n\n📤 Sent: {sent}\n❌ Failed: {failed}\n👥 Total: {len(active_users)}"),
            call.message.chat.id, call.message.message_id
        )
        
    except Exception as e:
        logger.error(f"❌ Error in broadcast: {e}")
        bot.answer_callback_query(call.id, B("❌ Error in broadcast"))

def broadcast_cancel_callback(call):
    """Handle broadcast cancel callback"""
    bot.answer_callback_query(call.id, B("❌ Broadcast cancelled"))
    bot.delete_message(call.message.chat.id, call.message.message_id)

def restart_bot_callback_callback(call):
    """Handle restart bot callback"""
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, B("⚠️ Admin permissions required"), show_alert=True)
        return
    
    # Send restart notification to all users
    bot.answer_callback_query(call.id, B("🚀 Sending restart notifications..."))
    threading.Thread(target=send_restart_notification).start()
    
    # Show animation
    msg = bot.send_message(call.message.chat.id, ProgressAnimation.restart_animation()[0])
    
    for i, frame in enumerate(ProgressAnimation.restart_animation()):
        try:
            bot.edit_message_text(frame, call.message.chat.id, msg.message_id)
            time.sleep(0.5)
        except:
            pass
    
    # Wait for notifications to send
    time.sleep(5)
    
    bot.edit_message_text(
        B("✅ Restart notifications sent!\n\n🔄 Bot will now restart..."),
        call.message.chat.id, msg.message_id
    )
    
    # Restart the bot
    time.sleep(2)
    os.execv(sys.executable, ['python'] + sys.argv)

def back_to_main_callback(call):
    """Handle back to main callback"""
    user_id = call.from_user.id
    tier = get_user_tier(user_id)
    tier_info = TIER_SYSTEM[tier]
    referral_count = referral_system.get_referral_count(user_id)
    auto_restart = referral_system.is_auto_restart_enabled(user_id) if tier == 'free' else True
    user_rank = referral_system.get_user_rank(user_id)
    
    welcome_text = B(f"""
┏━━━━━━━━━━━━━━━━━━━━━━┓
┃   🚀 KAWSAR HOSTING   ┃
┃      VERSION 3.1     ┃
┗━━━━━━━━━━━━━━━━━━━━━━┛

👤 Welcome back, {call.from_user.first_name}!
🆔 User ID: `{user_id}`
🎫 Tier: {tier_info['icon']} {tier_info['name']}
📁 Files: {get_user_file_count(user_id)}/{get_user_file_limit(user_id)}

📊 Referrals: {referral_count}/3
🏆 Rank: #{user_rank if user_rank else "Not ranked"}
🔄 Auto-Restart: {'✅ Enabled' if auto_restart else '❌ Disabled'}

📢 *Update Channel:* {UPDATE_CHANNEL}
👥 *Join Group:* {UPDATE_GROUP}

Use buttons below to navigate.
""")
    
    bot.answer_callback_query(call.id)
    bot.edit_message_text(welcome_text, 
                         call.message.chat.id, call.message.message_id,
                         reply_markup=create_main_menu_inline(user_id),
                         parse_mode='Markdown')

# ================================
# CLEANUP AND SHUTDOWN
# ================================
def cleanup():
    """Cleanup function for shutdown"""
    logger.warning("🔴 Shutting down... Cleaning up processes")
    
    # Kill all running scripts
    for script_key, script_info in list(bot_scripts.items()):
        try:
            kill_process_tree(script_info)
        except:
            pass
    
    # Save referral data
    referral_system.save_referrals()
    
    logger.info("✅ Cleanup complete")

# Register cleanup fuction
atexit.register(cleanup)

# ================================
# BOT STARTUP AND AUTO-RECOVERY
# ================================
def startup_recovery():
    """Automatically recover scripts on startup"""
    logger.info("🚀 Starting auto-recovery process...")
    
    msg = None
    try:
        # Send a message to owner
        msg = bot.send_message(OWNER_ID, ProgressAnimation.recovery_animation()[0])
        
        for i, frame in enumerate(ProgressAnimation.recovery_animation()):
            try:
                bot.edit_message_text(frame, OWNER_ID, msg.message_id)
                time.sleep(0.3)
            except:
                pass
        
        # Recover all scripts
        recovered = recovery_system.recover_all_scripts()
        
        if recovered:
            bot.edit_message_text(
                B(f"✅ Startup Recovery Complete!\n🔄 Recovered: {len(recovered)} scripts"),
                OWNER_ID, msg.message_id
            )
        else:
            bot.edit_message_text(
                B("📭 No scripts to recover on startup."),
                OWNER_ID, msg.message_id
            )
        
    except Exception as e:
        logger.error(f"❌ Error in startup recovery: {e}")
        if msg:
            try:
                bot.edit_message_text(
                    B(f"❌ Error in startup recovery: {str(e)[:100]}"),
                    OWNER_ID, msg.message_id
                )
            except:
                pass

# ================================
# MAIN EXECUTION
# ================================
if __name__ == '__main__':
    logger.info("="*50)
    logger.info("🚀 KAWSAR HOSTING BOT VERSION 3.1")
    logger.info("📊 Auto-Recovery System Enabled")
    logger.info("🤝 Referral System Enabled")
    logger.info("🏆 Referral Leaderboard Added")
    logger.info("🎫 Tier-Based Hosting")
    logger.info(f"👑 Owner ID: {OWNER_ID}")
    logger.info(f"🛡️ Admins: {len(admin_ids)}")
    logger.info(f"👥 Active Users: {len(active_users)}")
    logger.info(f"📁 Total Files: {sum(len(files) for files in user_files.values())}")
    
    # Get bot username
    try:
        bot_username = bot.get_me().username
        logger.info(f"🤖 Bot Username: @{bot_username}")
        logger.info(f"🔗 Referral Link Format: https://t.me/{bot_username}?start=KHB{{user_id}}{{random}}")
    except Exception as e:
        logger.error(f"❌ Error getting bot username: {e}")
    
    logger.info("="*50)
    
    # Start Flask keep-alive
    keep_alive()
    
    # Run startup recovery
    threading.Thread(target=startup_recovery).start()
    
    # Start bot polling
    logger.info("🤖 Starting bot polling...")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout:
            logger.warning("⚠️ Read Timeout. Restarting in 5s...")
            time.sleep(5)
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"⚠️ Connection Error: {ce}. Retrying in 15s...")
            time.sleep(15)
        except Exception as e:
            logger.critical(f"💥 Unrecoverable error: {e}", exc_info=True)
            logger.info("🔄 Restarting in 30s due to critical error...")
            time.sleep(30)
        finally:
            logger.warning("🔴 Polling stopped. Will restart if in loop...")
            time.sleep(1)
