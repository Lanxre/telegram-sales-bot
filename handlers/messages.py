from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from core.infrastructure.services import DialogService

from aiogram.fsm.context import FSMContext
from .states import DialogStates
from keyboards import get_dialog_keyboard, get_apeals_keyboard

from filters import IsAdmin

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
            "💬 Вы начали диалог с поддержкой. Напишите ваше сообщение:",
            reply_markup=get_dialog_keyboard(),
        )
    except Exception:
        await message.answer("❌ Не удалось создать диалог. Попробуйте позже.")
        await state.clear()


@message_router.message(
    DialogStates.waiting_for_message, F.text == "📝 Завершить диалог"
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
        "✅ Диалог завершен. Спасибо за обращение!", reply_markup=ReplyKeyboardRemove()
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
        await message.answer("❌ Диалог не найден")
        return

    try:
        messages = await dialog_service.get_messages_for_user_in_dialog(
            dialog_id=dialog_id, user_id=message.from_user.id
        )

        if not messages:
            await message.answer("📭 В диалоге пока нет сообщений")
            return

        history = "\n\n".join(
            f"{'Вы' if msg.sender_id == message.from_user.id else 'Поддержка'}: {msg.content}"
            for msg in messages
        )

        await message.answer(
            f"📜 История сообщений:\n\n{history}", reply_markup=get_dialog_keyboard()
        )
    except Exception:
        await message.answer("❌ Не удалось загрузить историю сообщений")


@message_router.message(DialogStates.waiting_for_message)
async def process_user_message(
    message: Message, state: FSMContext, dialog_service: DialogService
) -> None:
    """Обработка нового сообщения от пользователя"""
    data = await state.get_data()
    dialog_id = data.get("dialog_id")

    if not dialog_id:
        await message.answer("❌ Диалог не найден")
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
            "✅ Сообщение отправлено! Ожидайте ответа.\n"
            + "Если есть, что дополнить ✍️ введите текст сообщения:",
            reply_markup=get_dialog_keyboard(),
        )

        await state.set_state(DialogStates.waiting_for_message)
    except Exception:
        await message.answer("❌ Не удалось отправить сообщение. Попробуйте еще раз.")

@message_router.message(Command("showapeals"), IsAdmin())
async def show_appeals(message: Message, state: FSMContext, dialog_service: DialogService):
    try:
        not_read_dialogs = await dialog_service.not_read_dialogs(message.from_user.id)
        keyboard = get_apeals_keyboard(not_read_dialogs)
        await message.answer("Все поступившие обращения", reply_markup=keyboard)

    except Exception:
        await message.answer("❌ Не удалось загрузить сообщения.")