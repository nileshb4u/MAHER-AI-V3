"""
File Parsing Utilities for Agent Knowledge Base
Supports: PDF, DOCX, TXT files
"""

import os
import logging
from typing import Dict, List, Optional
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)

# File parsing libraries
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logger.warning("pdfplumber not installed - PDF parsing disabled")

try:
    from docx import Document
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    logger.warning("python-docx not installed - DOCX parsing disabled")


class FileParser:
    """Handles parsing of various file formats for agent knowledge"""

    # File size limits (in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
    MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB total

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {'.pdf', '.txt', '.docx'}

    # Content chunking settings
    CHUNK_SIZE = 1000  # characters per chunk
    CHUNK_OVERLAP = 100  # overlap between chunks

    @staticmethod
    def validate_file(file: FileStorage) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded file

        Returns:
            (is_valid, error_message)
        """
        if not file or not file.filename:
            return False, "No file provided"

        # Check file extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in FileParser.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file type: {ext}. Supported types: {', '.join(FileParser.SUPPORTED_EXTENSIONS)}"

        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        if size > FileParser.MAX_FILE_SIZE:
            return False, f"File too large: {size / (1024*1024):.1f}MB. Max size: {FileParser.MAX_FILE_SIZE / (1024*1024):.0f}MB"

        if size == 0:
            return False, "File is empty"

        # Check library support
        if ext == '.pdf' and not PDF_SUPPORT:
            return False, "PDF parsing not available (pdfplumber not installed)"

        if ext == '.docx' and not DOCX_SUPPORT:
            return False, "DOCX parsing not available (python-docx not installed)"

        return True, None

    @staticmethod
    def parse_txt(file: FileStorage) -> str:
        """Parse text file"""
        try:
            content = file.read().decode('utf-8', errors='ignore')
            return content.strip()
        except Exception as e:
            logger.error(f"Error parsing TXT file: {str(e)}")
            raise ValueError(f"Failed to parse text file: {str(e)}")

    @staticmethod
    def parse_pdf(file: FileStorage) -> str:
        """Parse PDF file using pdfplumber"""
        if not PDF_SUPPORT:
            raise ValueError("PDF parsing not available")

        try:
            text_content = []
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

            content = '\n\n'.join(text_content)
            return content.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF file: {str(e)}")
            raise ValueError(f"Failed to parse PDF file: {str(e)}")

    @staticmethod
    def parse_docx(file: FileStorage) -> str:
        """Parse DOCX file using python-docx"""
        if not DOCX_SUPPORT:
            raise ValueError("DOCX parsing not available")

        try:
            doc = Document(file)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            content = '\n\n'.join(paragraphs)
            return content.strip()
        except Exception as e:
            logger.error(f"Error parsing DOCX file: {str(e)}")
            raise ValueError(f"Failed to parse DOCX file: {str(e)}")

    @staticmethod
    def parse_file(file: FileStorage) -> Dict:
        """
        Parse uploaded file and extract text content

        Returns:
            {
                'filename': str,
                'extension': str,
                'size': int,
                'content': str,
                'word_count': int,
                'char_count': int,
                'summary': str
            }
        """
        # Validate file
        is_valid, error = FileParser.validate_file(file)
        if not is_valid:
            raise ValueError(error)

        # Get file metadata
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()

        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)

        # Parse based on file type
        if ext == '.txt':
            content = FileParser.parse_txt(file)
        elif ext == '.pdf':
            content = FileParser.parse_pdf(file)
        elif ext == '.docx':
            content = FileParser.parse_docx(file)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        # Generate metadata
        word_count = len(content.split())
        char_count = len(content)

        # Generate summary (first 200 characters)
        summary = content[:200] + '...' if len(content) > 200 else content

        return {
            'filename': filename,
            'extension': ext,
            'size': size,
            'content': content,
            'word_count': word_count,
            'char_count': char_count,
            'summary': summary
        }

    @staticmethod
    def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
        """
        Split text into overlapping chunks for better context preservation

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters

        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or FileParser.CHUNK_SIZE
        overlap = overlap or FileParser.CHUNK_OVERLAP

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_endings = ['. ', '.\n', '! ', '!\n', '? ', '?\n']
                best_break = -1

                for ending in sentence_endings:
                    pos = text.rfind(ending, start + chunk_size - 100, end)
                    if pos > best_break:
                        best_break = pos + len(ending)

                if best_break > start:
                    end = best_break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    @staticmethod
    def create_knowledge_context(documents: List[Dict]) -> str:
        """
        Create a formatted knowledge context from parsed documents

        Args:
            documents: List of parsed document dictionaries

        Returns:
            Formatted context string for the agent
        """
        if not documents:
            return ""

        context_parts = [
            "# Agent Knowledge Base",
            "",
            "You have access to the following knowledge documents:",
            ""
        ]

        for i, doc in enumerate(documents, 1):
            context_parts.append(f"## Document {i}: {doc['filename']}")
            context_parts.append(f"Type: {doc['extension']} | Words: {doc['word_count']} | Size: {doc['size']} bytes")
            context_parts.append("")
            context_parts.append("### Content:")
            context_parts.append(doc['content'])
            context_parts.append("")
            context_parts.append("---")
            context_parts.append("")

        context_parts.append("Use the above knowledge to inform your responses. "
                           "Reference specific documents when relevant and cite information accurately.")

        return '\n'.join(context_parts)

    @staticmethod
    def get_knowledge_summary(documents: List[Dict]) -> Dict:
        """
        Generate summary statistics for knowledge base

        Returns:
            {
                'total_files': int,
                'total_size': int,
                'total_words': int,
                'file_types': Dict[str, int],
                'files': List[Dict]
            }
        """
        if not documents:
            return {
                'total_files': 0,
                'total_size': 0,
                'total_words': 0,
                'file_types': {},
                'files': []
            }

        file_types = {}
        total_size = 0
        total_words = 0
        files = []

        for doc in documents:
            ext = doc['extension']
            file_types[ext] = file_types.get(ext, 0) + 1
            total_size += doc['size']
            total_words += doc['word_count']

            files.append({
                'filename': doc['filename'],
                'extension': doc['extension'],
                'size': doc['size'],
                'word_count': doc['word_count'],
                'summary': doc['summary']
            })

        return {
            'total_files': len(documents),
            'total_size': total_size,
            'total_words': total_words,
            'file_types': file_types,
            'files': files
        }
