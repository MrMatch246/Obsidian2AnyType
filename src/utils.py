import base64
import os, re
from pathlib import Path


def safe_read(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read(), 'utf-8'
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin1') as f:
            return f.read(), 'latin1'

def safe_write(filepath, content, encoding):
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(content)


def clone_input_to_output(input_path, output_path):
    """
    Clone the content of the input folder to the output folder.
    Creates the output folder if it does not exist.
    """
    raise NotImplementedError("This function is not implemented yet.")


def encode_triple_quote_blocks(content):
    pattern = re.compile(r'(?P<quote>```|\'\'\'|""")(?P<inner>.*?)(?P=quote)', re.DOTALL)

    def replacer(match):
        quote = match.group('quote')
        inner = match.group('inner')
        encoded = base64.b64encode(inner.encode('utf-8')).decode('utf-8')
        return f"{quote}{encoded}{quote}"

    return pattern.sub(replacer, content)

def decode_triple_quote_blocks(content):
    pattern = re.compile(r'(?P<quote>```|\'\'\'|""")(?P<inner>.*?)(?P=quote)', re.DOTALL)

    def replacer(match):
        quote = match.group('quote')
        encoded_text = match.group('inner').strip()
        try:
            decoded = base64.b64decode(encoded_text.encode('utf-8')).decode('utf-8')
            return f"{quote}{decoded}{quote}"
        except Exception as e:
            # If it's not valid base64, leave it unchanged
            print("Skipped decoding block (not valid Base64):", encoded_text[:30], "...")
            return match.group(0)

    return pattern.sub(replacer, content)

def sanitize(text):
    text = text.replace(' ', '_')
    for char in '()[]{}':
        text = text.replace(char, '_')
    return text

def replace_bracket_links(content):
    # Replace [[target]] and [[target|display]] links
    bracket_link_pattern = re.compile(r'\[\[([^\]|]+)(\|([^\]]+))?\]\]')
    def replace_bracket(match):
        target = match.group(1)
        display = match.group(3)

        new_target = sanitize(target)

        if display:
            new_display = sanitize(display)
            return f'[[{new_target}|{new_display}]]'
        else:
            return f'[[{new_target}]]'
    return bracket_link_pattern.sub(replace_bracket, content)

def replace_spaces_in_paths(content):
    md_link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    def replace_md_link(match):
        text, path = match.groups()
        if path.endswith('.md'):
            new_path = sanitize(path)
            return f'[{text}]({new_path})'
        return match.group(0)
    return md_link_pattern.sub(replace_md_link, content)


def rename_files_and_folders(root_dir):
    for path in sorted(Path(root_dir).rglob('*'), key=lambda x: -len(str(x))):
        if path.is_dir() or path.suffix == '.md':
            new_name = sanitize(path.name)
            if new_name != path.name:
                new_path = path.with_name(new_name)
                if not new_path.exists():
                    path.rename(new_path)

def prepend_header_to_markdown(file_path,content):
    file_stem = file_path.stem.replace('_', ' ')
    if not content.startswith(f'# {file_stem}'):
        content = f'# {file_stem}\n\n' + content
    return content

def find_md_file_by_title(title,root_folder):
    target_filename = f"{title.replace(' ', '_')}.md"
    for root, _, files in os.walk(root_folder):
        if target_filename in files:
            return os.path.join(root, target_filename)
    return None

def update_links_in_markdown_newnoteflow(content, file_dir,root_folder):
    # Case 1: Pipe-style links: [something|Title](...newnoteflow/...|Title.md)
    pattern_pipe_links = re.compile(
        r'\[([^\[\]]*?/)?([^|\[\]]+)\|([^\[\]]+)\]\([^\)]*newnoteflow/([^|)]+)\|[^\)]+\.md\)'
    )

    def replacer_pipe(match):
        display_text = match.group(3)
        target_filename = match.group(4) + '.md'
        abs_target_path = os.path.normpath(os.path.join(root_folder, target_filename))
        rel_path = os.path.relpath(abs_target_path, file_dir)
        return f'[{display_text}]({rel_path})'

    content = pattern_pipe_links.sub(replacer_pipe, content)

    # Case 2: Simple links: [Title](...newnoteflow/Title.md) or [Title](...newnoteflow/.../Title.md)
    pattern_simple_links = re.compile(
        r'\[([^\]]+)\]\([^\)]*newnoteflow/(?:[^/)]+/)?([^\)/]+\.md)\)'
    )

    def replacer_simple(match):
        display_text = match.group(1)
        filename = match.group(2)
        return f'[{display_text}](./{filename})'

    content = pattern_simple_links.sub(replacer_simple, content)

    return content


def update_links_in_markdown_period(content, file_dir,root_folder):
    pattern = re.compile(r'- \[[^\]]*?/([^/|\]]+)\|([^\]]+)\]\([^\)]*newnoteflow/([^|)]+)\|[^\)]+\.md\)')

    def replacer(match):
        link_path = match.group(3) + '.md'
        abs_target_path = os.path.normpath(os.path.join(root_folder, link_path))
        rel_path = os.path.relpath(abs_target_path, file_dir)
        return f'- [{match.group(2)}]({rel_path})'

    return pattern.sub(replacer, content)

def insert_dot_after_links(content):
    pattern = re.compile(r'(\- \[[^\]]+\]\([^\)]+\))(?=\s*\n)')
    return pattern.sub(r'\1.', content)

