import logging

import telegram.constants
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters


class ChatGPT3TelegramBot:
    def __init__(self, config, gpt3_bot):
        self.config = config
        self.gpt3_bot = gpt3_bot

    # Help menu
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("/start - Start the bot\n/reset - Reset conversation\n/help - Help menu")

    # Start the bot
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.message.from_user.id) not in self.config['allowed_chats']:
            logging.info(f'User {update.message.from_user.name} is not allowed to start the bot')
            return

        logging.info('Bot started')
        await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a Chat-GPT3 Bot, please talk to me!")

    # Reset the conversation
    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.message.from_user.id) not in self.config['allowed_chats']:
            logging.info(f'User {update.message.from_user.name} is not allowed to reset the bot')
            return

        logging.info('Resetting the conversation...')
        self.gpt3_bot.reset_chat()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Done!")

    # React to messages
    async def prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if str(update.message.from_user.id) not in self.config['allowed_chats']:
            logging.info(f'User {update.message.from_user.name} is not allowed to use the bot')
            return

        logging.info(f'New message received from user {update.message.from_user.name}')
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.constants.ChatAction.TYPING)
        response = self.get_chatgpt_response(update.message.text)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            reply_to_message_id=update.message.message_id,
            text=response["message"],
            parse_mode=telegram.constants.ParseMode.MARKDOWN
        )

    def get_chatgpt_response(self, message) -> dict:
        try:
            response = self.gpt3_bot.get_chat_response(message)
            return response
        except:
            return {"message": "I'm having some trouble talking to you, please try again later."}

    def run(self):
        application = ApplicationBuilder().token(self.config['telegram_bot_token']).build()

        application.add_handler(CommandHandler('start', self.start))
        application.add_handler(CommandHandler('reset', self.reset))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.prompt))

        application.run_polling()
