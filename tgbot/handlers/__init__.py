from aiogram import Router
from aiogram.filters import CommandStart 

from tgbot.handlers.commands import start_command_handler


from aiogram import Router, F
from tgbot.handlers.basic import handle_message,save_to_db_handler,clear_db_handler,process_token,process_db_id,Form
from aiogram.fsm.context import FSMContext


def setup() -> Router:
    router = Router()

    router.message.register(start_command_handler, CommandStart())
    router.message.register(save_to_db_handler,lambda message: message.text == "Сохранить в БД")
    router.message.register(process_token,Form.token)
    router.message.register(process_db_id,Form.db_id)
    router.message.register(clear_db_handler,lambda message: message.text == "Очистить БД")
    router.message.register(handle_message,Form.links)

    return router
