from loguru import logger


def broadcast(message: str):
    logger.info(message)
    return "Message broadcasted!"


broadcast_def = {
    "type": "function",
    "function": {
        "name": "broadcast",
        "description": "Broadcast a message to the user",
        "parameters": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to broadcast to the user",
                },
            },
            "required": ["message"],
        },
    },
}
