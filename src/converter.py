import os
from .utils import *
from .to_anytype import to_anytype
from .custom import *
class Converter:
    def __init__(self, target_folder_path, output_folder_path = None):
        self.target_folder_path = target_folder_path
        #create output folder if it does not exist TODO: implement this
        self.output_folder_path = output_folder_path if output_folder_path else target_folder_path
        self.root_folder = os.path.abspath(self.output_folder_path)


    def obsidian_to_anytype(self):
        """
        Convert Obsidian markdown files to Anytype format.
        """
        for root, dirs, files in os.walk(self.root_folder):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    content, encoding = safe_read(file_path)
                    new_content = encode_triple_quote_blocks(content)
                    new_content = replace_spaces_in_paths(new_content)
                    new_content = replace_bracket_links(new_content)
                    if new_content != content:
                        safe_write(file_path, new_content, encoding)
        rename_files_and_folders(self.root_folder)
        for root, dirs, files in os.walk(self.root_folder):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    content, encoding = safe_read(file_path)
                    new_content = prepend_header_to_markdown(Path(file_path), content)
                    if new_content != content:
                        safe_write(file_path, new_content, encoding)
        to_anytype(self.root_folder)
        for root, dirs, files in os.walk(self.root_folder):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    content, encoding = safe_read(file_path)
                    new_content = update_links_in_markdown_newnoteflow(content, root, self.root_folder)
                    new_content = update_links_in_markdown_period(new_content,file_path,self.root_folder)
                    new_content = insert_dot_after_links(new_content)
                    new_content = decode_triple_quote_blocks(new_content)
                    if new_content != content:
                        safe_write(file_path, new_content, encoding)

