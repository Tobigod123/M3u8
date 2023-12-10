import os
import logging
import subprocess
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

TOKEN = '6528532477:AAHCLp8krmcep32fwhpo_UDiaQepzOYtB78'
ffmpeg_process = None

RECORDING_DIRECTORY = 'Recordings'

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! You can use the /record command to start recording a live stream.")

def record(update: Update, context: CallbackContext):
    try:
        url = context.args[0]
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter the name for the recorded video file:")
        context.user_data['waiting_for_name'] = True
        context.user_data['url'] = url
    except IndexError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid URL.")

def handle_video_name(update: Update, context: CallbackContext):
    if 'waiting_for_name' in context.user_data and context.user_data['waiting_for_name']:
        try:
            video_file_name = update.message.text.strip()
            url = context.user_data['url']
            os.makedirs(RECORDING_DIRECTORY, exist_ok=True)
            video_file_path = os.path.join(RECORDING_DIRECTORY, video_file_name)
            command = ['ffmpeg', '-i', url, '-c', 'copy', video_file_path]
            global ffmpeg_process
            ffmpeg_process = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Recording the live stream.")
            context.user_data['waiting_for_name'] = False
            context.user_data['url'] = None
        except Exception as e:
            logger.error(f"An error occurred while handling the video name: {e}")
            context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Please try again.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Not expecting a file name.")

def stop(update: Update, context: CallbackContext):
    global ffmpeg_process
    if ffmpeg_process:
        try:
            ffmpeg_process.terminate()
            ffmpeg_process = None
            context.bot.send_message(chat_id=update.effective_chat.id, text="Recording stopped.")
        except Exception as e:
            logger.error(f"An error occurred while stopping recording: {e}")
            context.bot.send_message(chat_id=update.effective_chat.id, text="An error occurred. Recording could not be stopped.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No recording process is active.")

def main():
    bot = Bot(token=TOKEN)
    updater = Updater(bot=bot)

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    record_handler = CommandHandler('record', record)
    stop_handler = CommandHandler('stop', stop)
    video_name_handler = MessageHandler(Filters.text & ~Filters.command, handle_video_name)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(record_handler)
    dispatcher.add_handler(stop_handler)
    dispatcher.add_handler(video_name_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
