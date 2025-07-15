from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from core.infrastructure.services import DialogService
from core.internal.models import DialogUpdate
from core.internal.enums import ButtonText, CallbackPrefixes
from filters import IsAdmin
from keyboards import get_apeals_keyboard, get_dialog_keyboard, get_message_keyboard
from logger import LoggerBuilder
from states import DialogStates

logger = LoggerBuilder("MessageRouter").add_stream_handler().build()
message_router = Router()


@message_router.message(Command("startdialog"))
async def start_dialog_command(
    message: Message, state: FSMContext, dialog_service: DialogService
) -> None:
    """Начало нового диалога с администратором"""
    try:
        admin_id = await dialog_service.get_admin_id_for_dialog()
        dialog = await dialog_service.create_dialog(
            dialog_id=message.chat.id, user1_id=message.from_user.id, user2_id=admin_id
        )

        await state.update_data(dialog_id=dialog.id)
        await state.set_state(DialogStates.waiting_for_message)

        await message.answer(
            dialog_service.formatter.start_message,
            reply_markup=get_dialog_keyboard(),
        )
    except Exception:
        await message.answer(dialog_service.formatter.start_dialog_error)
        await state.clear()


@message_router.message(
    DialogStates.waiting_for_message, F.text == ButtonText.FINISH_DIALOG.value
)
async def end_dialog_handler(
    message: Message, state: FSMContext, dialog_service: DialogService
) -> None:
    """Завершение текущего диалога"""
    data = await state.get_data()
    dialog_id = data.get("dialog_id")

    if dialog_id:
        pass

    await message.answer(
        dialog_service.formatter.end_dialog, reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@message_router.message(
    DialogStates.waiting_for_message, F.text == "📋 Показать историю"
)
async def show_history_handler(
    message: Message, state: FSMContext, dialog_service: DialogService
) -> None:
    """Показать историю сообщений текущего диалога"""
    data = await state.get_data()
    dialog_id = data.get("dialog_id")

    if not dialog_id:
        await message.answer(dialog_service.formatter.hast_dialog)
        return

    try:
        messages = await dialog_service.get_messages_for_user_in_dialog(
            dialog_id=dialog_id, user_id=message.from_user.id
        )

        if not messages:
            await message.answer(dialog_service.formatter.hast_messages)
            return

        history_messages_text = await dialog_service.get_dialogs_text(
            message.from_user.id, messages
        )

        await message.answer(history_messages_text, reply_markup=get_dialog_keyboard())
    except Exception:
        await message.answer(dialog_service.formatter.history_error)


@message_router.message(DialogStates.waiting_for_message)
async def process_user_message(
    message: Message, state: FSMContext, dialog_service: DialogService
) -> None:
    """Обработка нового сообщения от пользователя"""
    data = await state.get_data()
    dialog_id = data.get("dialog_id")

    if not dialog_id:
        await message.answer(dialog_service.formatter.hast_dialog)
        await state.clear()
        return

    try:
        await dialog_service.create_message(
            message_id=message.message_id,
            dialog_id=dialog_id,
            sender_id=message.from_user.id,
            content=message.text,
        )

        await message.answer(
            dialog_service.formatter.send_message,
            reply_markup=get_dialog_keyboard(),
        )

        await state.set_state(DialogStates.waiting_for_message)
    except Exception:
        await message.answer(dialog_service.formatter.message_send_error)


@message_router.message(Command("showapeals"), IsAdmin())
async def show_appeals(message: Message, dialog_service: DialogService):
    try:
        not_read_dialogs = await dialog_service.not_read_dialogs(message.from_user.id)

        if not_read_dialogs:
            keyboard = get_apeals_keyboard(not_read_dialogs)
            await message.answer(dialog_service.formatter.apeals, reply_markup=keyboard)

        await message.answer(dialog_service.formatter.hast_apeals)

    except Exception:
        await message.answer(dialog_service.formatter.apeals_error)


@message_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.DIALOG_APPEALS))
async def show_select_apeals(callback: CallbackQuery, dialog_service: DialogService):
    try:
        dialog_id = CallbackPrefixes.last_index_after_prefix(callback.data, CallbackPrefixes.DIALOG_APPEALS)
        dialog = await dialog_service.get_dialog(dialog_id)
        keyboard = get_message_keyboard(dialog)
        text_messages = await dialog_service.get_message_text(
            dialog.user1.username, dialog.messages
        )
        await callback.message.answer(text_messages, reply_markup=keyboard)
        await callback.answer()

    except Exception:
        await callback.message.answer(dialog_service.formatter.apeals_error)


@message_router.callback_query(lambda c: CallbackPrefixes.has_prefix(c.data, CallbackPrefixes.ANSWER_APPEALS))
async def answer_apeals_tag(callback: CallbackQuery, state: FSMContext):
    dialog_id = CallbackPrefixes.last_index_after_prefix(callback.data, CallbackPrefixes.ANSWER_APPEALS)
    await callback.message.answer("Ожидается ответ пользователю")
    await state.update_data(dialog_id=dialog_id)
    await state.set_state(DialogStates.waiting_for_answer_apeals)
    await callback.answer()


@message_router.message(DialogStates.waiting_for_answer_apeals)
async def answer_apeals(
    message: Message, state: FSMContext, dialog_service: DialogService, bot: Bot
):
    try:
        data = await state.get_data()
        dialog_id = data.get("dialog_id")
        answer = message.text.strip()

        await dialog_service.create_message(
            message_id=message.message_id,
            dialog_id=dialog_id,
            sender_id=message.from_user.id,
            content=answer,
        )

        await dialog_service.update_dialog(dialog_id, DialogUpdate(is_read=True))

        await message.answer(dialog_service.formatter.is_send)

        text = await dialog_service.get_answer_text(answer)

        await bot.send_message(
            chat_id=dialog_id,
            text=text,
        )

    except Exception:
        await message.answer(dialog_service.formatter.answer_error)

    await state.clear()
