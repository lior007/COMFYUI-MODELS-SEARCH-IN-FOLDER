import os
import pathlib
import hashlib
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DirectoryState:
    """Department for managing and monitoring the status of the folder"""
    MODEL_EXTENSIONS = {'.ckpt', '.safetensors', '.pt', '.bin', '.yaml', '.vae', '.sft', '.gguf'}

    def __init__(self, path: str):
        self.path = path
        self.files_hash = self._calculate_directory_hash()
        self.timestamp = datetime.now()

    def _calculate_directory_hash(self) -> str:
        """Computes a digital signature of the folder state"""
        hash_content = []
        try:
            for root, _, files in os.walk(self.path):
                for filename in files:
                    if pathlib.Path(filename).suffix.lower() in self.MODEL_EXTENSIONS:
                        full_path = os.path.join(root, filename)
                        try:
                            stats = os.stat(full_path)
                            file_info = f"{full_path}|{stats.st_size}|{stats.st_mtime}"
                            hash_content.append(file_info)
                        except (FileNotFoundError, PermissionError) as e:
                            logger.warning(f"Error accessing file {full_path}: {e}")
                            continue

            hash_content.sort()
            content_str = "|".join(hash_content)
            return hashlib.md5(content_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating directory hash: {e}")
            return ""

    def is_valid(self) -> bool:
        """Checks if the folder state has changed"""
        current_hash = self._calculate_directory_hash()
        return current_hash == self.files_hash and current_hash != ""
