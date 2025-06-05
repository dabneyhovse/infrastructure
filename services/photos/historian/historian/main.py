import logging
import os
import io
import httpx
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, constants
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


load_dotenv()

BOT_TOKEN = str(os.getenv("TG_TOKEN"))
CHANNEL_ID = str(os.getenv("TG_CHANNEL_ID"))
BASE_URL = str(os.getenv("IM_BASE_URL"))
API_KEY = str(os.getenv("IM_API_KEY"))


# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )


async def upload(
    user: str | None, name: str | None, contents: httpx._types.FileContent
):
    headers = {"Accept": "application/json", "x-api-key": API_KEY}

    data = {
        "deviceAssetId": f"{name or "UNK"}-{datetime.now().timestamp()}",
        "deviceId": f"{user or "UNK"}-python",
        "fileCreatedAt": datetime.now().isoformat(),
        "fileModifiedAt": datetime.now().isoformat(),
        "isFavorite": "false",
    }

    files = {"assetData": (name, contents, "application/octet-stream")}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/api/assets", headers=headers, data=data, files=files
        )
        return response.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (msg := update.message):
        return

    await msg.reply_text(
        "Hello! If you're sending images, please send them as uncompressed files (Document). "
        "If you send a compressed photo, I'll delete it and ask you to resend as a file.",
        reply_to_message_id=msg.message_id,
    )


async def handle_compressed_photo(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not (msg := update.message):
        return

    await msg.reply_text(
        "Please resend your image as a document, not a photo. This is for compression reasons.",
        reply_to_message_id=msg.message_id,
    )

    try:
        await msg.delete()
    except Exception as e:
        logging.warning(f"Could not delete the message: {e}")


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not (msg := update.message) or not (document := msg.document):
        return

    try:
        file_io = io.BytesIO()

        new_file = await context.bot.get_file(document.file_id)
        await new_file.download_to_memory(file_io)
        file_io.seek(0)

        logging.info(f"recieved file: {document.file_id}")

        upload_res = await upload(msg.from_user.username, document.file_name, file_io)

        file_io.seek(0)
        await msg.reply_photo(
            file_io,
            reply_to_message_id=msg.message_id,
            parse_mode=constants.ParseMode.MARKDOWN_V2,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        await msg.reply_text(
            f"An error occurred while downloading the file: {e}",
            reply_to_message_id=msg.message_id,
        )


def main() -> None:

    channel_filter = filters.ALL

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.PHOTO & channel_filter, handle_compressed_photo)
    )
    app.add_handler(
        MessageHandler(filters.Document.IMAGE & channel_filter, handle_document)
    )
    app.run_polling()


if __name__ == "__main__":
    main()
