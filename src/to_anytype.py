import os
import re
import argparse

newfiles_folder = 'newnoteflow'
log = open("log.txt", "a")

def safe_read(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read(), 'utf-8'
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin1') as f:
            return f.read(), 'latin1'

def safe_write(file_path, content, encoding):
    with open(file_path, 'w', encoding=encoding) as f:
        f.write(content)

def preprocess_md_links(file_path):
    try:
        contents, encoding = safe_read(file_path)
        contents = re.sub(r'%20', ' ', contents)

        def remove_relative_path(match):
            name, path = match.groups()
            if path.startswith(("http:", "https:", "onenote:")):
                log.write(f"[{name}]({path}) unchanged\n")
                return f"[{name}]({path})"
            filename = os.path.basename(path)
            log.write(f"[{name}]({path}) -> [{name}]({filename})\n")
            return f"[{name}]({filename})"

        contents = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', remove_relative_path, contents)
        safe_write(file_path, contents, encoding)
    except Exception as e:
        print(f"Error preprocessing Markdown links in file {file_path}: {e}")

def replace_wiki_links(file_path):
    try:
        contents, encoding = safe_read(file_path)

        def replace_function(match):
            link_content = match.group(1)
            if link_content.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.md')):
                log.write(f"[[{link_content}]] -> [{link_content}]({link_content})\n")
                return f"[{link_content}]({link_content})"
            else:
                log.write(f"[[{link_content}]] -> [{link_content}]({link_content}.md)\n")
                return f"[{link_content}]({link_content}.md)"

        updated_contents = re.sub(r'\[\[(.*?)\]\]', replace_function, contents)
        safe_write(file_path, updated_contents, encoding)
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

def find_file(name, search_path):
    for root, dirs, files in os.walk(search_path):
        if name in files:
            return os.path.join(root, name)
    return None

def create_if_not_exists(file_path):
    try:
        if not os.path.exists(file_path):
            log.write(f"Creating file: {file_path}\n")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('')
        else:
            log.write("File exists, updating link\n")
    except Exception as e:
        print(f"Error creating file {file_path}: {e}")

def update_links_and_create_directory_index(file_path, base_path):
    try:
        log.write(f"FILE: {file_path}\n")
        contents, encoding = safe_read(file_path)

        def replace_link(match):
            is_image, name, link = match.groups()
            if link.startswith(("http:", "https:", "onenote:")):
                log.write(f"External link: {link}, skipped\n")
                return match.group(0)

            found_path = find_file(link, base_path)
            if found_path:
                relative_path = os.path.relpath(found_path, os.path.dirname(file_path))
                log.write(f"Resolved: {link} -> {relative_path}\n")
            else:
                if is_image == '':
                    newfiles_path = os.path.join(base_path, newfiles_folder, link)
                    create_if_not_exists(newfiles_path)
                    relative_path = os.path.relpath(newfiles_path, os.path.dirname(file_path))
                else:
                    relative_path = link
            return f"{is_image}[{name}]({relative_path})"

        updated_contents = re.sub(r'(!?)\[([^\]]+)\]\(([^)]+)\)', replace_link, contents)
        safe_write(file_path, updated_contents, encoding)
        print(f"Processed: {file_path}")
    except Exception as e:
        print(f"Error updating links in {file_path}: {e}")

def create_directory_index(dir_path):
    try:
        index_file_path = os.path.join(dir_path, os.path.basename(dir_path) + '.md')
        if not os.path.exists(index_file_path):
            links = []
            for item in os.listdir(dir_path):
                item_path = os.path.join(dir_path, item)
                if os.path.isdir(item_path):
                    links.append(f"- [{item}]({os.path.abspath(os.path.join(item_path, item + '.md'))})")
                elif item.endswith('.md') and item != os.path.basename(dir_path) + '.md':
                    links.append(f"- [{os.path.splitext(item)[0]}]({os.path.abspath(item_path)})")
            safe_write(index_file_path, '\n'.join(links), 'utf-8')
    except Exception as e:
        print(f"Error creating index for {dir_path}: {e}")

def update_md_links(file_path):
    try:
        contents, encoding = safe_read(file_path)
        contents = re.sub(r'\[([^\]]+)\]\(([^)]+)\)',
                          lambda m: f'[{m.group(1)}]({m.group(2).replace(" ", "%20")})',
                          contents)
        safe_write(file_path, contents, encoding)
    except Exception as e:
        print(f"Error updating Markdown links in {file_path}: {e}")

def metategs_to_text(file_path):
    try:
        contents, encoding = safe_read(file_path)
        lines = contents.splitlines()
        modified_lines = [line for i, line in enumerate(lines) if i >= 9 or line.strip() != '---']
        safe_write(file_path, '\n'.join(modified_lines) + '\n', encoding)
    except Exception as e:
        print(f"Error cleaning metatags in {file_path}: {e}")

def confirm_execution(part):
    response = input(f"Do you want to execute the script part '{part}'? (yes/no): ").strip().lower()
    return response in ['yes', 'y']

def main(base_path, auto=False):
    if auto or confirm_execution("1. Preprocess markdown links"):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.md'):
                    preprocess_md_links(os.path.join(root, file))
        print("Preprocessing completed.")

    if auto or confirm_execution("2. Replace wiki-links"):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.md'):
                    replace_wiki_links(os.path.join(root, file))
        print("Wiki-link replacement completed.")

    if auto or confirm_execution("3. Resolve links + index creation"):
        for root, dirs, files in os.walk(base_path):
            for dir in dirs:
                create_directory_index(os.path.join(root, dir))
            for file in files:
                if file.endswith('.md'):
                    update_links_and_create_directory_index(os.path.join(root, file), base_path)
        print("Links and indexes updated.")

    if (not auto) and confirm_execution("4. Encode links (%20)"):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.md'):
                    update_md_links(os.path.join(root, file))
        print("Markdown links encoded.")

    if auto or confirm_execution("5. Remove YAML metatags"):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('.md'):
                    metategs_to_text(os.path.join(root, file))
        print("Metatag cleanup done.")

    log.close()

def to_anytype(file_path):
    main(file_path,auto=True)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process Markdown files in a directory.')
    parser.add_argument('path', help='Base path to start processing')
    args = parser.parse_args()
    main(args.path)
