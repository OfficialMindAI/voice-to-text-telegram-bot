from telegram import (
    Update, 
    BotCommand, 
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackContext, 
    MessageHandler, 
    AIORateLimiter,
    filters, 
)  
import os
import traceback
 
from pathlib import Path 
from uuid import uuid4 
from pydub import AudioSegment
 


WHISPER_MODEL= None
HELP_MESSAGE = """Commands:
⚪ /start – To start the bot 

🎵 Send an audio and the bot will send you the audio converted to text
🎤 For issues, informations or advertising contact @MindAIOfficial
"""



input_path =  Path(__file__).parent.resolve() / "input_audios"
output_path =  Path(__file__).parent.resolve() / "output_audios"


def audioToText(filename, model_size="base"):
    from whisper_timestamped import load_model, transcribe_timestamped
    global WHISPER_MODEL
    if (WHISPER_MODEL == None):
        WHISPER_MODEL = load_model(model_size)
    gen = transcribe_timestamped(WHISPER_MODEL, filename, verbose=False, fp16=False)
    return gen["text"]
def create_path(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    else:
        print(f"Directory '{directory}' already exists.")
 
async def handle_voice_converter(update: Update, context: CallbackContext):   
    file_name = uuid4()
    new_file = await context.bot.get_file(update.message.voice.file_id)

    await new_file.download_to_drive(input_path / f"{file_name}.ogg") 
    # Convert OGG to WAV format
    audio = AudioSegment.from_ogg(input_path / f'{file_name}.ogg')
    audio.export(input_path / f'{file_name}.wav', format='wav')
 
    print('recognizer')
    res = audioToText(str(input_path / f'{file_name}.wav'), model_size='base')
    await  update.message.reply_text(f'Transcribed text: {res}')
 


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("/start", "Start the bot") 
     ])

 

def run_bot() -> None:
    application = (
        ApplicationBuilder()
        .token("YOUR_TOKEN")
        .concurrent_updates(True)
        .rate_limiter(AIORateLimiter(max_retries=5))
        .http_version("1.1")
        .get_updates_http_version("1.1")
        .post_init(post_init)
        .build()
    ) 
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_converter))    # application.add_handler(CommandHandler("convert", show_facts_menu, filters=user_filter))
  
 

    try:
         create_path(input_path)
    except Exception as e:
        traceback_str = ''.join(traceback.format_tb(e.__traceback__)) 
        print("Error", traceback_str, e) 
        print('*******************************************************************')
 

    application.run_polling()
 


if __name__ == "__main__":
    run_bot()

