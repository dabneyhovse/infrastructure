import logging
import json
import html
import traceback
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.error("Exception while handling an update:", exc_info=context.error)
    if not (msg := getattr(update, "message", None)) or not (err := context.error):
        return

    tb_list = traceback.format_exception(None, context.error, err.__traceback__)
    tb_string = "".join(tb_list)

    await msg.reply_text(
        "Sorry, I ran into an error! ;-;\n"
        f"<pre>{html.escape(tb_string)}</pre>",
        parse_mode=ParseMode.HTML
    )