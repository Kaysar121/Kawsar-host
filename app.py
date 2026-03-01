
import logging
import asyncio
import subprocess
import os
import psutil
import sys
import re
import time
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from flask import Flask
from threading import Thread

# ================== FLASK SERVER FOR RENDER ==================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# ================== BOT CONFIG ==================

TOKEN = "8369678760:AAF0Qcz5XPyp_b2o6e6V8YGgrT9OncUoXgQ"
ADMIN_ID = 5957710220

bot = Bot(token=TOKEN)
dp = Dispatcher()

running_processes = {}
STORAGE_DIR = "user_files"
os.makedirs(STORAGE_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)

# ================== BASIC COMMANDS ==================

def menu(is_admin=False):
    buttons = [
        [KeyboardButton(text="🏓 Ping")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer("Bot Started Successfully ✅", reply_markup=menu())

@dp.message(Command("ping"))
async def ping_cmd(message: types.Message):
    await message.answer("🏓 Pong!", reply_markup=menu())

# ================== SAFE POLLING START ==================

async def main():
    print("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()  # Start Flask for Render port binding
    asyncio.run(main())
