from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from core.infrastructure.services import DialogService
from core.internal.models import DialogUpdate
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
async def show_appeals(message: Message, dialog_service: DialogService):
    try:
        not_read_dialogs = await dialog_service.not_read_dialogs(message.from_user.id)
        keyboard = get_apeals_keyboard(not_read_dialogs)
        await message.answer("Все поступившие обращения", reply_markup=keyboard)

    except Exception:
        await message.answer("❌ Не удалось загрузить сообщения.")


@message_router.callback_query(lambda c: c.data.startswith("dialog_apeals_"))
async def show_select_apeals(callback: CallbackQuery, dialog_service: DialogService):
    try:
        dialog_id = int(callback.data.split("_")[-1])
        dialog = await dialog_service.get_dialog(dialog_id)
        keyboard = get_message_keyboard(dialog)
        await callback.message.answer(
            f"{dialog.user1.username}: {'\n'.join(map(lambda x: x.content, dialog.messages))}",
            reply_markup=keyboard,
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await callback.message.answer("❌ Не удалось загрузить обращение.")


@message_router.callback_query(lambda c: c.data.startswith("answer_apeals_"))
async def answer_apeals_tag(callback: CallbackQuery, state: FSMContext):
    dialog_id = int(callback.data.split("_")[-1])
    await callback.message.answer("Ожидается ответ пользователю")
    await state.set_data(data={"dialog_id": dialog_id})
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

        await message.answer("✅ Ответ отправлен!")

        await bot.send_message(
            chat_id=dialog_id,
            text="Вы получили ответ на ваше обращение. Для деталей /startdialog '📋 Показать историю'\n"
            + f"{answer if len(answer) < 20 else f'{answer[:20]}...'}",
        )

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        await message.answer("❌ Не удалось отправить ответ.")

    await state.clear()
