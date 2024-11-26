import os
import time
import uuid
from typing import Any, Dict, Optional, List
from config import get_settings
import httpx


settings = get_settings()


def remove_none(dict: Dict[str, Any]):
    return {key: value for key, value in dict.items() if value is not None}


def generate_unique_filename(prefix="", length=8):
    # Generate a UUID
    unique_id = uuid.uuid4()

    # Convert the UUID to a hexadecimal string and remove hyphens
    unique_string = unique_id.hex

    # Add an optional prefix to the unique string
    if prefix:
        unique_string = f"{prefix}_{unique_string}"
    # Return the first 'length' characters of the unique string
    return unique_string[:length]


def delete_file(file_path: str, seconds: Optional[float] = 300):
    time.sleep(seconds)
    if os.path.exists(file_path):
        # Attempt to delete the file
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error deleting file '{file_path}': {e}")
    else:
        print(f"File '{file_path}' does not exist.")


async def send_sms(phone_numbers: List[str], message: str = "", sender_id: str = "GSC24"):
    payloadMessage = """
    Thank you for registering for a once in a lifetime opportunity,Good Shepherd Conference 2024. We're excited to experience God's presence with you. 

Here are the event details: 
Date: December 14th, 2024 
Time: 10am GMT 
Venue: Perez chapel international - Youth Auditorium 

Share this link to invite a friend
https://gsc.szfamily.org/events/638dd663-90fe-4fa5-8021-50f7d66cd9b1

See you there!
    """
    payload = {
        "sender": "GSC24",  # Replace with your sender ID
        "message": payloadMessage,
        "recipients": phone_numbers,
    }
    headers = {
        "api-key": settings.arkesel_api_key,
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(settings.arkesel_url, json=payload, headers=headers)
        if response.status_code == 200:
            return {"status": "success", "data": response.json()}
        else:
            return {"status": "error", "details": response.json()}
    except Exception as e:
        print(f"Unable to send message to {phone_numbers}")