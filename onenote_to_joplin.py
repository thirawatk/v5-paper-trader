#!/usr/bin/env python3
"""
OneNote → Joplin Migration Script
===================================
Converts OneNote ZIP exports to Markdown and imports into Joplin.

Usage:
  python3 onenote_to_joplin.py <onenote_export.zip> [target_notebook]

  target_notebook: Joplin notebook to import into (default: "Imported Notes")

Steps:
  1. Export from OneNote web: right-click notebook → Download
  2. Upload ZIP to server: scp notebook.zip root@pve1:/tmp/
  3. Run: python3 onenote_to_joplin.py /tmp/notebook.zip "Library/Tech"
"""

from __future__ import annotations

import os
import re
import sys
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime

# Try markitdown first, fall back to html2text
try:
    from markitdown import MarkItDown
    CONVERTER = "markitdown"
except ImportError:
    CONVERTER = "html2text"

JOPLIN_BIN = "/root/.hermes/node/bin/joplin"


def log(msg: str, level: str = "INFO"):
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERROR": "❌"}
    print(f"{icons.get(level, '•')} {msg}")


def extract_zip(zip_path: str, extract_dir: str) -> str:
    """Extract OneNote ZIP and return the root directory."""
    log(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)

    # Find the root directory (may be nested)
    root = extract_dir
    # Check if there's a single top-level directory
    entries = os.listdir(extract_dir)
    if len(entries) == 1 and os.path.isdir(os.path.join(extract_dir, entries[0])):
        root = os.path.join(extract_dir, entries[0])

    log(f"Extracted to: {root}", "OK")
    return root


def find_html_files(root: str) -> list[tuple[str, str]]:
    """Find all HTML files and return (path, relative_path) pairs."""
    html_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if f.lower().endswith(('.html', '.htm')):
                full_path = os.path.join(dirpath, f)
                rel_path = os.path.relpath(full_path, root)
                html_files.append((full_path, rel_path))

    log(f"Found {len(html_files)} HTML files")
    return html_files


def convert_html_to_md(html_path: str) -> str:
    """Convert HTML file to Markdown."""
    if CONVERTER == "markitdown":
        md = MarkItDown()
        result = md.convert(html_path)
        return result.text_content
    else:
        # Fallback to html2text
        import html2text
        h = html2text.HTML2Text()
        h.body_width = 0  # Don't wrap
        with open(html_path, 'r', encoding='utf-8', errors='replace') as f:
            html_content = f.read()
        return h.handle(html_content)


def sanitize_filename(name: str) -> str:
    """Remove or replace characters that Joplin can't handle."""
    # Remove extension
    name = re.sub(r'\.html?$', '', name, flags=re.IGNORECASE)
    # Replace problematic characters
    name = re.sub(r'[\\/:*?"<>|]', '_', name)
    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    # Limit length
    if len(name) > 200:
        name = name[:200]
    return name


def convert_all(root: str, output_dir: str) -> list[dict]:
    """Convert all HTML files to Markdown. Returns list of note dicts."""
    html_files = find_html_files(root)
    if not html_files:
        log("No HTML files found. Checking for .one files...", "WARN")
        # Check for .one files
        one_files = []
        for dirpath, dirnames, filenames in os.walk(root):
            for f in filenames:
                if f.lower().endswith('.one'):
                    one_files.append(os.path.join(dirpath, f))
        if one_files:
            log(f"Found {len(one_files)} .one files — these need Joplin Desktop to import", "WARN")
            log("Upload this ZIP to a machine with Joplin Desktop and import there", "WARN")
        return []

    notes = []
    os.makedirs(output_dir, exist_ok=True)

    for i, (html_path, rel_path) in enumerate(html_files, 1):
        try:
            md_content = convert_html_to_md(html_path)

            # Extract title from first heading or filename
            title_match = re.search(r'^#\s+(.+)', md_content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip()
            else:
                title = sanitize_filename(os.path.basename(rel_path))

            # Create directory structure
            rel_dir = os.path.dirname(rel_path)
            note_dir = os.path.join(output_dir, rel_dir)
            os.makedirs(note_dir, exist_ok=True)

            # Save markdown file
            safe_name = sanitize_filename(os.path.basename(rel_path))
            md_path = os.path.join(note_dir, f"{safe_name}.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            notes.append({
                "title": title,
                "path": md_path,
                "rel_path": rel_path,
                "dir": rel_dir,
            })

            if i % 10 == 0:
                log(f"Converted {i}/{len(html_files)} files...")

        except Exception as e:
            log(f"Failed to convert {rel_path}: {e}", "ERROR")

    log(f"Converted {len(notes)} notes to Markdown", "OK")
    return notes


def import_to_joplin(notes: list[dict], target_notebook: str):
    """Import converted Markdown notes into Joplin."""
    if not notes:
        log("No notes to import", "WARN")
        return

    # Group notes by directory (for sub-notebook structure)
    dir_groups: dict[str, list[dict]] = {}
    for note in notes:
        d = note.get("dir", "")
        if d not in dir_groups:
            dir_groups[d] = []
        dir_groups[d].append(note)

    log(f"Importing {len(notes)} notes into '{target_notebook}'...")
    log(f"Found {len(dir_groups)} subdirectories")

    imported = 0
    skipped = 0

    for dir_name, dir_notes in dir_groups.items():
        # Determine notebook name
        if dir_name:
            # Use the directory name as sub-notebook
            notebook = f"{target_notebook}/{dir_name}" if target_notebook else dir_name
        else:
            notebook = target_notebook or "Imported Notes"

        for note in dir_notes:
            try:
                # Import via CLI
                result = subprocess.run(
                    [JOPLIN_BIN, "import", note["path"], notebook, "--format", "md", "-f"],
                    capture_output=True, text=True, timeout=30,
                    env={**os.environ, "PATH": f"/root/.hermes/node/bin:{os.environ.get('PATH', '')}"}
                )

                if result.returncode == 0:
                    imported += 1
                else:
                    if "already exists" in result.stdout.lower() or "already exists" in result.stderr.lower():
                        skipped += 1
                    else:
                        log(f"Import error for {note['title']}: {result.stderr}", "ERROR")
                        skipped += 1

            except subprocess.TimeoutExpired:
                log(f"Timeout importing {note['title']}", "ERROR")
                skipped += 1
            except Exception as e:
                log(f"Error importing {note['title']}: {e}", "ERROR")
                skipped += 1

    log(f"Imported: {imported} | Skipped: {skipped}", "OK")

    # Sync
    log("Syncing to server...")
    subprocess.run(
        [JOPLIN_BIN, "sync"],
        capture_output=True, timeout=60,
        env={**os.environ, "PATH": f"/root/.hermes/node/bin:{os.environ.get('PATH', '')}"}
    )
    log("Sync complete", "OK")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    zip_path = sys.argv[1]
    target_notebook = sys.argv[2] if len(sys.argv) > 2 else "Imported Notes"

    if not os.path.exists(zip_path):
        log(f"File not found: {zip_path}", "ERROR")
        sys.exit(1)

    # Create temp directory
    with tempfile.TemporaryDirectory(prefix="onenote_") as tmp_dir:
        # Extract
        root = extract_zip(zip_path, tmp_dir)

        # Convert
        output_dir = os.path.join(tmp_dir, "converted")
        notes = convert_all(root, output_dir)

        if notes:
            # Show preview
            print(f"\n{'='*50}")
            print(f"Preview of converted notes:")
            print(f"{'='*50}")
            for n in notes[:10]:
                print(f"  📄 {n['title'][:60]}")
                print(f"     → {n['rel_path']}")
            if len(notes) > 10:
                print(f"  ... and {len(notes) - 10} more")
            print(f"{'='*50}\n")

            # Import
            import_to_joplin(notes, target_notebook)
        else:
            log("No notes were converted", "ERROR")
            sys.exit(1)

    log("Migration complete!", "OK")
    print(f"\nCheck your Joplin app for the imported notes in '{target_notebook}'")


if __name__ == "__main__":
    main()
