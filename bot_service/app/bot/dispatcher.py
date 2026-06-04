from aiogram import Bot, Dispatcher
from app.core.config import settings
from app.bot.handlers import router as handlers_router

bot = Bot(token=settings.BOT_TOKEN)

dp = Dispatcher()

dp.include_router(handlers_router)