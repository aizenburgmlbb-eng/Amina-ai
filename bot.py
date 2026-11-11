import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Загружаем секреты
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
FOLDER_ID = os.getenv("YANDEX_FOLDER_ID")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключение к Yandex AI Studio (используем OpenAI-совместимый протокол)
client = AsyncOpenAI(
    api_key=YANDEX_API_KEY,
    base_url="https://ai.api.cloud.yandex.net/v1",
    default_headers={"x-folder-id": FOLDER_ID} # Передаем ID каталога
)

# ВАЖНО: Указываем точное имя модели из вашего интерфейса
# На скриншоте она называется "DeepSeek V4.1 Flash 1017", 
# но в API она может называться иначе (например, deepseek-v4-flash).
# Если бот выдаст ошибку модели, проверьте точное имя в документации AI Studio.
MODEL_NAME = "deepseek-v4-flash" 

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Я бот на базе DeepSeek. Напиши мне что-нибудь, и я отвечу.")

@dp.message()
async def handle_message(message: types.Message):
    # Показываем статус "печатает..."
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Отправляем запрос к нейросети
        response = await client.chat.completions.create(
            model=f"gpt://{FOLDER_ID}/{MODEL_NAME}/latest", # Формат URI для Yandex Cloud
            messages=[
                {"role": "system", "content": "Ты — дружелюбный и умный ассистент."},
                {"role": "user", "content": message.text}
            ],
            temperature=0.6,
            max_tokens=1500
        )
        
        # Получаем ответ и отправляем пользователю
        answer = response.choices[0].message.content
        await message.answer(answer)
        
    except Exception as e:
        logging.error(f"Ошибка API: {e}")
        await message.answer("Упс, произошла ошибка при обращении к нейросети. Попробуйте позже.")

async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())