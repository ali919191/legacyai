"""
Media Memory Service for Legacy AI Platform

This service enables users to upload and manage media memories (photos, audio, video)
that are associated with memory entries. The service provides a foundation for
multimodal memory storage that can be extended to cloud storage solutions.

The service integrates with the MemoryCaptureService to ensure media files are
properly linked to existing memory entries, maintaining data consistency and
enabling rich, multimedia memory experiences.
"""

from typing import List, Dict, Any, Optional, BinaryIO
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import uuid
import os
import mimetypes


class MediaType(Enum):
    """Enumeration of supported media types."""
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass
class MediaFile:
    """Represents a media file associated with a memory."""
    id: str
    memory_id: str
    user_id: str
    filename: str
    file_type: MediaType
    mime_type: str
    file_size: int
    upload_timestamp: datetime
    description: str
    local_path: Optional[str] = None  # Local file path for development
    cloud_url: Optional[str] = None   # Cloud storage URL for production
    metadata: Optional[Dict[str, Any]] = None


class MediaMemoryService:
    """
    Media Memory Service for the Legacy AI platform.

    This service handles the upload, storage, and retrieval of media memories
    including photos, audio recordings, and videos. It provides a foundation
    for multimodal memory experiences while maintaining links to structured
    memory entries.

    Key Features:
    - Support for images, audio, and video files
    - Automatic file type detection and validation
    - Metadata tracking (upload time, file info, descriptions)
    - Integration with MemoryCaptureService for data consistency
    - Designed for future cloud storage migration
    - Access control integration ready

    The service currently uses local file storage but is designed to easily
    migrate to cloud storage solutions like AWS S3, Google Cloud Storage,
    or Azure Blob Storage.
    """

    # Supported file extensions by media type
    SUPPORTED_EXTENSIONS = {
        MediaType.IMAGE: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
        MediaType.AUDIO: ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        MediaType.VIDEO: ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    }

    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        MediaType.IMAGE: 10 * 1024 * 1024,  # 10MB
        MediaType.AUDIO: 50 * 1024 * 1024,  # 50MB
        MediaType.VIDEO: 100 * 1024 * 1024  # 100MB
    }

    def __init__(self, memory_service, storage_directory: str = "media_uploads"):
        """
        Initialize the Media Memory Service.

        Args:
            memory_service: Instance of MemoryCaptureService for memory validation
            storage_directory: Directory for local file storage (relative to project root)
        """
        self.memory_service = memory_service
        self.storage_directory = storage_directory
        self.media_files: Dict[str, MediaFile] = {}

        # Create storage directory if it doesn't exist
        self._ensure_storage_directory()

    def _ensure_storage_directory(self):
        """Ensure the storage directory exists."""
        if not os.path.exists(self.storage_directory):
            os.makedirs(self.storage_directory)

    def _get_media_type_from_filename(self, filename: str) -> Optional[MediaType]:
        """
        Determine media type from file extension.

        Args:
            filename: The filename to analyze

        Returns:
            MediaType if supported, None otherwise
        """
        _, ext = os.path.splitext(filename.lower())

        for media_type, extensions in self.SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                return media_type

        return None

    def _validate_file(self, file: BinaryIO, filename: str) -> tuple[MediaType, str]:
        """
        Validate file type and size.

        Args:
            file: File-like object to validate
            filename: Original filename

        Returns:
            Tuple of (MediaType, mime_type)

        Raises:
            ValueError: If file is invalid or unsupported
        """
        # Determine media type from filename
        media_type = self._get_media_type_from_filename(filename)
        if not media_type:
            raise ValueError(f"Unsupported file type: {filename}")

        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning

        max_size = self.MAX_FILE_SIZES[media_type]
        if file_size > max_size:
            raise ValueError(f"File too large: {file_size} bytes (max: {max_size} bytes)")

        # Get MIME type
        mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            mime_type = "application/octet-stream"

        return media_type, mime_type

    def _generate_local_path(self, media_id: str, filename: str) -> str:
        """
        Generate local file path for storage.

        Args:
            media_id: Unique media identifier
            filename: Original filename

        Returns:
            Local file path
        """
        _, ext = os.path.splitext(filename)
        return os.path.join(self.storage_directory, f"{media_id}{ext}")

    def upload_media(
        self,
        user_id: str,
        memory_id: str,
        file: BinaryIO,
        filename: str,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a media file and associate it with a memory.

        This method validates the file, stores it locally, and creates a media
        record linked to the specified memory. The memory must exist before
        media can be uploaded.

        Args:
            user_id: ID of the user uploading the media
            memory_id: ID of the memory to associate with the media
            file: File-like object containing the media data
            filename: Original filename of the uploaded file
            description: Optional description of the media
            metadata: Optional additional metadata

        Returns:
            The ID of the uploaded media file

        Raises:
            ValueError: If file is invalid, memory doesn't exist, or other validation fails
        """
        # Validate that memory exists
        memory = self.memory_service.retrieve_memory(memory_id)
        if not memory:
            raise ValueError(f"Memory with ID {memory_id} does not exist")

        # Validate file
        media_type, mime_type = self._validate_file(file, filename)

        # Generate unique ID and local path
        media_id = str(uuid.uuid4())
        local_path = self._generate_local_path(media_id, filename)

        # Get file size
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        # Save file locally
        with open(local_path, 'wb') as f:
            f.write(file.read())

        # Create media record
        media_file = MediaFile(
            id=media_id,
            memory_id=memory_id,
            user_id=user_id,
            filename=filename,
            file_type=media_type,
            mime_type=mime_type,
            file_size=file_size,
            upload_timestamp=datetime.now(),
            description=description,
            local_path=local_path,
            cloud_url=None,  # Will be set when migrated to cloud storage
            metadata=metadata or {}
        )

        # Store media record
        self.media_files[media_id] = media_file

        return media_id

    def retrieve_media(self, media_id: str) -> Optional[MediaFile]:
        """
        Retrieve media file metadata by ID.

        Args:
            media_id: The ID of the media file to retrieve

        Returns:
            MediaFile object if found, None otherwise
        """
        return self.media_files.get(media_id)

    def list_media_for_memory(self, memory_id: str) -> List[MediaFile]:
        """
        List all media files associated with a specific memory.

        Args:
            memory_id: The ID of the memory

        Returns:
            List of MediaFile objects associated with the memory
        """
        return [
            media for media in self.media_files.values()
            if media.memory_id == memory_id
        ]

    def get_media_file_path(self, media_id: str) -> Optional[str]:
        """
        Get the local file path for a media file.

        This method returns the local path for serving files. In production,
        this would be replaced with cloud storage URLs.

        Args:
            media_id: The ID of the media file

        Returns:
            Local file path if media exists and file is available, None otherwise
        """
        media = self.retrieve_media(media_id)
        if media and media.local_path and os.path.exists(media.local_path):
            return media.local_path
        return None

    def delete_media(self, media_id: str, user_id: str) -> bool:
        """
        Delete a media file.

        This method removes both the file record and the physical file.
        Access control should be checked before calling this method.

        Args:
            media_id: The ID of the media file to delete
            user_id: The ID of the user requesting deletion (for future access control)

        Returns:
            True if successfully deleted, False otherwise
        """
        media = self.retrieve_media(media_id)
        if not media:
            return False

        # Remove physical file if it exists
        if media.local_path and os.path.exists(media.local_path):
            try:
                os.remove(media.local_path)
            except OSError:
                pass  # File may already be deleted

        # Remove from storage
        del self.media_files[media_id]
        return True

    def get_media_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored media files.

        Returns:
            Dictionary with media statistics
        """
        total_files = len(self.media_files)
        total_size = sum(media.file_size for media in self.media_files.values())

        type_counts = {}
        for media in self.media_files.values():
            media_type = media.file_type.value
            type_counts[media_type] = type_counts.get(media_type, 0) + 1

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "files_by_type": type_counts
        }

    def migrate_to_cloud_storage(self, cloud_storage_service) -> int:
        """
        Migrate local files to cloud storage.

        This method would be implemented when integrating with cloud storage
        services like AWS S3, Google Cloud Storage, etc.

        Args:
            cloud_storage_service: Cloud storage service instance

        Returns:
            Number of files migrated
        """
        # Placeholder for future cloud migration implementation
        migrated_count = 0

        for media in self.media_files.values():
            if media.local_path and not media.cloud_url:
                # Upload to cloud and update cloud_url
                # cloud_url = cloud_storage_service.upload_file(media.local_path)
                # media.cloud_url = cloud_url
                # Optionally remove local file after successful upload
                migrated_count += 1

        return migrated_count