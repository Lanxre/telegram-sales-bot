from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from core.infrastructure import db_manager
from core.infrastructure.services import DialogService
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from .states import DialogStates

message_router = Router()
dialog_service = DialogService(db_manager)

dialog_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📝 Завершить диалог")],
        [KeyboardButton(text="📋 Показать историю")]
    ],
    resize_keyboard=True
)

@message_router.message(Command("startdialog"))
async def start_dialog_command(message: Message, state: FSMContext) -> None:
    """Начало нового диалога с администратором"""
    admin_id = 123456789  # ID администратора (заменить на реальный)
    
    try:
        # Создаем новый диалог между пользователем и админом
        dialog = await dialog_service.create_dialog(
            dialog_id=message.chat.id,
            user1_id=message.from_user.id,
            user2_id=admin_id
        )
        
        # Сохраняем ID диалога в состоянии
        await state.update_data(dialog_id=dialog.id)
        await state.set_state(DialogStates.waiting_for_message)
        
        await message.answer(
            "💬 Вы начали диалог с поддержкой. Напишите ваше сообщение:",
            reply_markup=dialog_keyboard
        )
    except Exception:
        await message.answer("❌ Не удалось создать диалог. Попробуйте позже.")
        await state.clear()

@message_router.message(DialogStates.waiting_for_message, F.text == "📝 Завершить диалог")
async def end_dialog_handler(message: Message, state: FSMContext) -> None:
    """Завершение текущего диалога"""
    data = await state.get_data()
    dialog_id = data.get("dialog_id")
    
    if dialog_id:
        pass
    
    await message.answer(
        "✅ Диалог завершен. Спасибо за обращение!",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

@message_router.message(DialogStates.waiting_for_message, F.text == "📋 Показать историю")
async def show_history_handler(message: Message, state: FSMContext) -> None:
    """Показать историю сообщений текущего диалога"""
    data = await state.get_data()
    dialog_id = data.get("dialog_id")
    
    if not dialog_id:
        await message.answer("❌ Диалог не найден")
        return
    
    try:
        messages = await dialog_service.get_messages_for_user_in_dialog(
            dialog_id=dialog_id,
            user_id=message.from_user.id
        )
        
        if not messages:
            await message.answer("📭 В диалоге пока нет сообщений")
            return
        
        history = "\n\n".join(
            f"{'Вы' if msg.sender_id == message.from_user.id else 'Поддержка'}: {msg.content}"
            for msg in messages
        )
        
        await message.answer(
            f"📜 История сообщений:\n\n{history}",
            reply_markup=dialog_keyboard
        )
    except Exception:
        await message.answer("❌ Не удалось загрузить историю сообщений")

@message_router.message(DialogStates.waiting_for_message)
async def process_user_message(message: Message, state: FSMContext) -> None:
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
            content=message.text
        )
        
        await message.answer(
            "✅ Сообщение отправлено! Ожидайте ответа.",
            reply_markup=dialog_keyboard
        )
        
        await message.answer("Если есть, что дополнить ✍️ введите текст сообщения:")
        
        await state.set_state(DialogStates.waiting_for_message)
    except Exception:
        await message.answer("❌ Не удалось отправить сообщение. Попробуйте еще раз.")