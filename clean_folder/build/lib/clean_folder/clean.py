# from sort_folder15.py
import os
import sys
import shutil

def sort_folder(folder_path):
    category_mapping = {
        '1.Текстові файли': ['txt'],
        '4.Зображення': ['jpg', 'jpeg', 'png', 'svg'],
        '2.Документи': ['docx', 'doc', 'pdf', 'xlsx', 'pptx'],
        '5.Відео файли': ['avi', 'mp4', 'mov', 'mkv'],
        '6.Музика': ['mp3', 'ogg', 'wav', 'amr'],
        '3.Архіви': ['zip', 'gz', 'rar']
    }
    if not os.path.isdir(folder_path):
        print(f"Директорії '{folder_path}' не існує.")
        return

    successfully_moved_files = [] # локальна для сортування. передати, як аргумент
    failed_to_move_files = []
    skipped_files = []

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                extension = filename.split('.')[-1].lower()
                for category, extensions in category_mapping.items():
                    if extension in extensions:
                        category_folder = category
                        category_path = os.path.join(folder_path, category_folder)
                        if not os.path.exists(category_path):
                            os.makedirs(category_path)
                        new_file_path = os.path.join(category_path, filename)
                        try:
                            shutil.move(file_path, new_file_path)
                            successfully_moved_files.append(filename)
                            print(f"Файл '{filename}' переміщено до категорії '{category_folder}'")
                        except Exception:
                            failed_to_move_files.append(filename)
                            print(f"Не вдалося перемістити файл '{filename}'")
                        break
                else:
                    skipped_files.append(filename)
                    print(f"Файл '{filename}' пропущено - немає відповідної категорії")

    print(f"Кількість переміщених файлів: {len(successfully_moved_files)}")
    print(f"Кількість файлів, які не вдалось перемістити: {len(failed_to_move_files)}")
    print(f"Кількість файлів, які залишились без змін: {len(skipped_files)}")
    skipped_files_str = ', '.join(skipped_files)
    print(skipped_files_str)
    
    remove_empty_directories(folder_path, successfully_moved_files) # доступний для функції видалення
def remove_empty_directories(folder_path, successfully_moved_files):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for directory in dirs:
            directory_path = os.path.join(root, directory)
            if not os.listdir(directory_path) and directory not in successfully_moved_files:
                os.rmdir(directory_path)
                print(f"Порожню папку '{directory}' видалено")

if __name__ == '__main__':
    # folder_path = os.path.dirname(sys.argv[0])
    folder_path = os.path.abspath(os.path.dirname(sys.argv[0]))
    sort_folder(folder_path)