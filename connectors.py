from abc import ABC, abstractmethod
from typing import List
from models import ContentChunk


class BaseConnector(ABC):
    """Abstract base class for data source connectors."""

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Name of the data source (e.g., 'github', 'notion')."""
        pass

    @abstractmethod
    def fetch_content(self) -> List[ContentChunk]:
        """
        Fetch content from the data source.

        Returns:
            List of ContentChunk objects
        """
        pass


class FileConnector(BaseConnector):
    """Connector for local files (Markdown, text)."""

    def __init__(self, file_path: str):
        """
        Initialize file connector.

        Args:
            file_path: Path to the file to index
        """
        self.file_path = file_path

    @property
    def source_name(self) -> str:
        return "file"

    def fetch_content(self) -> List[ContentChunk]:
        """Read and parse a file into content chunks."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # For now, treat entire file as one chunk
            # In production, this would split by sections/headers
            filename = self.file_path.split('/')[-1]

            chunk = ContentChunk(
                source=self.source_name,
                source_id=self.file_path,
                title=filename,
                content=content,
                url=f"file://{self.file_path}",
                metadata={
                    "file_path": self.file_path,
                    "type": "file"
                }
            )

            return [chunk]
        except Exception as e:
            print(f"Error reading file {self.file_path}: {e}")
            return []


class MarkdownConnector(BaseConnector):
    """Connector for Markdown files with section-based chunking."""

    def __init__(self, file_path: str):
        """
        Initialize Markdown connector.

        Args:
            file_path: Path to the Markdown file
        """
        self.file_path = file_path

    @property
    def source_name(self) -> str:
        return "markdown"

    def fetch_content(self) -> List[ContentChunk]:
        """Parse Markdown file and create chunks by sections."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            filename = self.file_path.split('/')[-1]
            chunks = []

            # Split by headers (# , ## , ### )
            lines = content.split('\n')
            current_section = ""
            current_title = filename

            for line in lines:
                if line.startswith('#'):
                    # Save previous section if it has content
                    if current_section.strip():
                        chunk = ContentChunk(
                            source=self.source_name,
                            source_id=f"{self.file_path}#{current_title}",
                            title=current_title,
                            content=current_section.strip(),
                            url=f"file://{self.file_path}",
                            metadata={
                                "file_path": self.file_path,
                                "type": "markdown_section",
                                "section": current_title
                            }
                        )
                        chunks.append(chunk)

                    # Start new section
                    current_title = line.lstrip('#').strip()
                    current_section = ""
                else:
                    current_section += line + "\n"

            # Add last section
            if current_section.strip():
                chunk = ContentChunk(
                    source=self.source_name,
                    source_id=f"{self.file_path}#{current_title}",
                    title=current_title,
                    content=current_section.strip(),
                    url=f"file://{self.file_path}",
                    metadata={
                        "file_path": self.file_path,
                        "type": "markdown_section",
                        "section": current_title
                    }
                )
                chunks.append(chunk)

            return chunks if chunks else []
        except Exception as e:
            print(f"Error reading Markdown file {self.file_path}: {e}")
            return []
