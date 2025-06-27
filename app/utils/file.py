import os
import aiofiles

async def save_to_disk(file, path):
    """
        Save an uploaded file to the specified path.
    """
    # Ensure the directory exists
    os.makedirs(os.path.dirname(path), exist_ok=True)

    # Write the file content to the specified path
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)

    return True