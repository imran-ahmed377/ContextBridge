from abc import ABC, abstractmethod
from typing import List
from models import ContentChunk
import requests
import base64
import os
from config import settings
import time
from typing import Optional


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


class GitHubConnector(BaseConnector):
    """Connector for GitHub repositories (fetches markdown/text files)."""

    def __init__(self, owner: str, repo: str, path: str = ""):
        self.owner = owner
        self.repo = repo
        self.path = path.strip('/')
        self.token = settings.github_token

    @property
    def source_name(self) -> str:
        return "github"

    def _call_api(self, api_path: str):
        url = f"https://api.github.com{api_path}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        # Retry with exponential backoff, handle rate limits
        max_retries = 5
        backoff = 1
        for attempt in range(max_retries):
            resp = requests.get(url, headers=headers, timeout=15)

            # Successful
            if resp.status_code == 200:
                remaining = int(resp.headers.get('X-RateLimit-Remaining', '1'))
                if remaining == 0:
                    # Sleep until reset time
                    reset_ts = int(resp.headers.get('X-RateLimit-Reset', '0'))
                    sleep_seconds = max(0, reset_ts - int(time.time())) + 1
                    time.sleep(sleep_seconds)
                    continue
                return resp.json()

            # Rate limited or forbidden - try to respect Retry-After or reset header
            if resp.status_code in (429, 403):
                retry_after = resp.headers.get('Retry-After')
                if retry_after and retry_after.isdigit():
                    time.sleep(int(retry_after) + 1)
                    continue
                reset_ts = resp.headers.get('X-RateLimit-Reset')
                if reset_ts and reset_ts.isdigit():
                    sleep_seconds = max(
                        0, int(reset_ts) - int(time.time())) + 1
                    time.sleep(sleep_seconds)
                    continue

            # For other transient errors, backoff
            if 500 <= resp.status_code < 600:
                time.sleep(backoff)
                backoff *= 2
                continue

            # Non-retryable error
            resp.raise_for_status()

        raise Exception(
            f"GitHub API failed after {max_retries} attempts: {url}")

    def _fetch_file_content(self, download_url: str, api_item: dict) -> str:
        # Prefer download_url if available
        try:
            if download_url:
                r = requests.get(download_url, timeout=15)
                r.raise_for_status()
                return r.text
            # Fallback to content field (base64)
            if api_item.get('content'):
                content_b64 = api_item['content']
                return base64.b64decode(content_b64).decode('utf-8')
        except Exception:
            return ""
        return ""

    def _walk_contents(self, api_path: str) -> List[dict]:
        items = []
        # Try efficient recursive tree listing first
        try:
            tree_api = f"/repos/{self.owner}/{self.repo}/git/trees/HEAD?recursive=1"
            tree_resp = self._call_api(tree_api)
            if isinstance(tree_resp, dict) and 'tree' in tree_resp:
                for entry in tree_resp['tree']:
                    if entry.get('type') != 'blob':
                        continue
                    path = entry.get('path')
                    name = os.path.basename(path)
                    items.append({
                        'path': path,
                        'name': name,
                        # Use raw.githubusercontent URL for content retrieval (fewer API calls)
                        'download_url': f"https://raw.githubusercontent.com/{self.owner}/{self.repo}/HEAD/{path}"
                    })
                return items
        except Exception as e:
            # Fallback to contents API traversal
            print(f"GitHub tree API fallback: {e}")

        try:
            resp = self._call_api(api_path)
            # If single file, GitHub returns a dict; if directory, returns a list
            if isinstance(resp, dict) and resp.get('type') == 'file':
                items.append(resp)
            elif isinstance(resp, list):
                for it in resp:
                    if it.get('type') == 'dir':
                        # it['url'] is full API URL; convert to api_path by stripping base
                        child_api_path = it.get('url', '').replace(
                            'https://api.github.com', '')
                        items.extend(self._walk_contents(child_api_path))
                    else:
                        items.append(it)
        except Exception as e:
            print(f"GitHub API error when walking {api_path}: {e}")

        return items

    def fetch_content(self) -> List[ContentChunk]:
        """Fetch markdown and text files from the repository path (recursively)."""
        try:
            base_api_path = f"/repos/{self.owner}/{self.repo}/contents"
            api_path = base_api_path + (f"/{self.path}" if self.path else "")

            items = self._walk_contents(api_path)
            chunks: List[ContentChunk] = []

            for item in items:
                name = item.get('name', '')
                # Only index text-like files for Day 2
                if not any(name.lower().endswith(ext) for ext in ('.md', '.markdown', '.txt', '.rst', '.mdown', 'README')):
                    continue

                download_url = item.get('download_url')
                content_text = self._fetch_file_content(download_url, item)
                if not content_text:
                    continue

                path = item.get('path')
                title = name
                chunk = ContentChunk(
                    source=self.source_name,
                    source_id=f"{self.owner}/{self.repo}:{path}",
                    title=title,
                    content=content_text,
                    url=f"https://github.com/{self.owner}/{self.repo}/blob/main/{path}",
                    metadata={
                        'owner': self.owner,
                        'repo': self.repo,
                        'path': path,
                        'type': 'github_file'
                    }
                )
                chunks.append(chunk)

            return chunks
        except Exception as e:
            print(f"Error fetching GitHub content: {e}")
            return []
