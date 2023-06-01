import os
import shutil
import string
import sys
# import argparse
import zipfile
# import unpack_7zarchive
# import RarFile # після pip install > Import "RarFile" could not be resolved

IMAGES = ["jpg", "png", "gif", "svg"]
MUSIC = ["mp3", "wav", "ogg", "amr"]
VIDEO = ["mp4", "avi", "mov", "mkv"]
DOCS = ["doc", "docx", "pdf", "txt", "xlsx", "pptx"]
ARCHIVES = ["zip", "rar", "7z"]

SYMB = string.punctuation
CYR_S = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
T_MAP2 = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'j',
    'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f',
    'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    'є': 'je', 'і': 'i', 'ї': 'ji', 'ґ': 'g'
}

# directory_path = r"D:\PyCoreHw\Py\Hw6\HomeTask6\Task6_exe"
directory_path = sys.argv[1]

translate = {}
for c, l in zip(CYR_S, T_MAP2):
    translate[ord(c)] = l
    translate[ord(c.upper())] = l.upper()


def create_category_directories(directory_path):
    category_directories = []
    category_directories.append(os.path.join(directory_path, "images"))
    category_directories.append(os.path.join(directory_path, "music"))
    category_directories.append(os.path.join(directory_path, "video"))
    category_directories.append(os.path.join(directory_path, "documents"))
    category_directories.append(os.path.join(directory_path, "archives"))
    category_directories.append(os.path.join(directory_path, "non_detect"))
    for category_directory in category_directories:
        os.makedirs(category_directory, exist_ok=True)
    return category_directories


ARCHIVES_DIR = os.path.join(directory_path, "archives")


def get_files_in_directory(directory_path):
    files = []
    for root, dirs, filenames in os.walk(directory_path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                files.append(file_path)
    return files


def get_category_directory(filename, category_directories):
    extension = os.path.splitext(filename)[1][1:].lower()
    if extension in IMAGES:
        return category_directories[0]
    elif extension in MUSIC:
        return category_directories[1]
    elif extension in VIDEO:
        return category_directories[2]
    elif extension in DOCS:
        return category_directories[3]
    elif extension in ARCHIVES:
        return category_directories[4]
    else:
        return category_directories[5]


def normalize(text):
    normalized_text = ""
    for char in text:
        if char.isalpha() and char.lower() in T_MAP2:
            if char.isupper():
                normalized_text += T_MAP2[char.lower()].upper()
            else:
                normalized_text += T_MAP2[char.lower()]
        elif char.isalnum():
            normalized_text += char
        elif char in SYMB:
            normalized_text += "_"
        else:
            normalized_text += char
    return normalized_text


def normalize_file_name(filename, file_path, existing_files, category_directory):
    name, extension = os.path.splitext(filename)

    new_name = name
    index = 1

    while os.path.exists(os.path.join(category_directory, new_name + extension)):
        new_name = f"{name}_{index}"
        index += 1

    normalized_new_name = normalize(new_name)  # Нормалізуємо нове ім'я файлу

    return normalized_new_name + extension


# переносимо всі архіви до відповідної категорії. "Правильні" архіви розпаковуємо.
# пошкоджені архіви залишаємо без
def extract_archive(archive_path):
    try:
        archive_name = os.path.splitext(os.path.basename(archive_path))[0]
        target_dir = os.path.join(ARCHIVES_DIR, archive_name)
        os.makedirs(target_dir, exist_ok=True)

        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(target_dir)

        # Перенесення розпакованого вмісту до відповідної підпапки без розширення
        extracted_files = get_files_in_directory(target_dir)
        for extracted_file in extracted_files:
            extracted_filename = os.path.basename(extracted_file)
            new_category_directory = get_category_directory(extracted_filename, create_category_directories(target_dir))
            new_filename = normalize_file_name(extracted_filename, extracted_file, extracted_files, new_category_directory)
            destination_path = os.path.join(new_category_directory, new_filename)
            shutil.move(extracted_file, destination_path)

        # Переміщення архіву у відповідну категорію
        archive_category_directory = get_category_directory(archive_name, create_category_directories(directory_path))
        new_archive_filename = normalize_file_name(os.path.basename(archive_path), archive_path, [], archive_category_directory)
        new_archive_path = os.path.join(archive_category_directory, new_archive_filename)
        shutil.move(archive_path, new_archive_path)

        # Видалення порожніх папок в архівній папці
        for root, dirs, filenames in os.walk(target_dir, topdown=False):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)

    except zipfile.BadZipFile:
        # Якщо архівний файл пошкоджений, просто переміщуємо його без розпакування
        new_filename = normalize_file_name(os.path.basename(archive_path), archive_path, [], ARCHIVES_DIR)
        new_file_path = os.path.join(ARCHIVES_DIR, new_filename)
        shutil.move(archive_path, new_file_path)


def sort_files_in_directory(directory_path):
    category_directories = create_category_directories(directory_path)
    files = get_files_in_directory(directory_path)

    for file_path in files:
        filename = os.path.basename(file_path)
        extension = os.path.splitext(filename)[1][1:].lower()

        if extension in ARCHIVES:
            try:
                extract_archive(file_path)
            except Exception:
                # Якщо сталася помилка під час розпакування, перемістимо архів без розпакування
                new_filename = normalize_file_name(filename, file_path, files, ARCHIVES_DIR)
                destination_path = os.path.join(ARCHIVES_DIR, new_filename)
                shutil.move(file_path, destination_path)
            continue

        category_directory = get_category_directory(filename, category_directories)
        new_filename = normalize_file_name(filename, file_path, files, category_directory)
        destination_path = os.path.join(category_directory, new_filename)
        shutil.move(file_path, destination_path)

    # Видалення порожніх папок
    for root, dirs, filenames in os.walk(directory_path, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)


def find_files(directory_path, extensions):
    files = []
    for extension in extensions:
        for root, dirs, filenames in os.walk(directory_path):
            for file in filenames:
                if file.lower().endswith("." + extension):
                    files.append(os.path.join(root, file))
    return files


def find_unknown_extensions(directory_path):
    known_extensions = IMAGES + MUSIC + VIDEO + DOCS + ARCHIVES
    extensions = set()
    for root, dirs, filenames in os.walk(directory_path):
        for file in filenames:
            extension = os.path.splitext(file)[1][1:].lower()
            if extension not in known_extensions:
                extensions.add(extension)
    return list(extensions)


def list_files_in_directory(directory_path):
    files = []
    file_count = 0
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path):
            file_count += 1
            file_name = os.path.basename(item_path)
            files.append(file_name)
    return files, file_count


def generate_report(directory_path):
    report = ""
    report += "Список файлів в категорії Images:\n" + "\n".join(
        os.path.basename(file) for file in find_files(directory_path, IMAGES)) + "\n\n"
    report += "Список файлів в категорії Music:\n" + "\n".join(
        os.path.basename(file) for file in find_files(directory_path, MUSIC)) + "\n\n"
    report += "Список файлів в категорії Video:\n" + "\n".join(
        os.path.basename(file) for file in find_files(directory_path, VIDEO)) + "\n\n"
    report += "Список файлів в категорії Documents:\n" + "\n".join(
        os.path.basename(file) for file in find_files(directory_path, DOCS)) + "\n\n"
    report += "Список файлів в категорії Archives:\n" + "\n".join(
        os.path.basename(file) for file in find_files(directory_path, ARCHIVES)) + "\n\n"

    non_detect_files, non_detect_count = list_files_in_directory(os.path.join(directory_path, "non_detect"))
    report += f"Кількість файлів в категорії Non Detect ({non_detect_count} файлів):\n"
    report += "Список файлів в категорії Non Detect:\n" + "\n".join(non_detect_files) + "\n\n"

    known_extensions = IMAGES + MUSIC + VIDEO + DOCS + ARCHIVES
    report += "Перелік усіх відомих розширень:\n" + ", ".join(known_extensions) + "\n\n"

    unknown_extensions = find_unknown_extensions(directory_path)
    report += f"Кількість невідомих розширень ({len(unknown_extensions)} розширень):\n"
    report += "Список невідомих розширень:\n" + ", ".join(unknown_extensions) + "\n"

    return report


# Запуск сортування файлів в заданій директорії
sort_files_in_directory(directory_path)

# Згенерувати звіт про сортування
report = generate_report(directory_path)
print(report)

 # інші функції та операції, для наданого шляху
def main():
    normalize()
    normalize_file_name()
    extract_archive()
    sort_files_in_directory(directory_path)
    find_files(directory_path)
    list_files_in_directory(directory_path)
    generate_report(directory_path)

if __name__ == "__main__":
    main()
    # directory_path = r"D:\PyCoreHw\Py\Hw6\HomeTask6\Task6_exe"
