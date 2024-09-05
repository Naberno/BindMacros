import keyboard
import time
import json
import os
import threading

# Подсказка для пользователя
HELP_TEXT = """
Поддерживаемые клавиши:
- Буквы и цифры (например, w, q, 1)
- Специальные клавиши: (alt), (-alt), (space), (esc), (tab), (caps), (shift), (ctrl), (win)
- Для помощи введите: _help
Примеры использования:
- wwqr(alt)d(-alt)
- (space)(shift)a
"""

# Функция для синхронизации с английской раскладкой
def sync_with_english_layout(key):
    # Маппинг клавиш с русской на английскую раскладку
    ru_to_en = {
        "й": "q", "ц": "w", "у": "e", "к": "r", "е": "t", "н": "y", "г": "u", "ш": "i", "щ": "o", "з": "p",
        "х": "[", "ъ": "]", "ф": "a", "ы": "s", "в": "d", "а": "f", "п": "g", "р": "h", "о": "j", "л": "k",
        "д": "l", "ж": ";", "э": "'", "я": "z", "ч": "x", "с": "c", "м": "v", "и": "b", "т": "n", "ь": "m",
        "б": ",", "ю": ".", ".": "/", ",": "`"
    }
    # Если клавиша русская, преобразуем её
    return ru_to_en.get(key, key)

# Функция для создания новой последовательности
def create_sequence():
    sequence = {}
    print("Создание новой последовательности.")
    print(HELP_TEXT)
    while True:
        trigger_key = input("Введите клавишу, которая будет запускать макрос (или 'done' для завершения): ")
        trigger_key = sync_with_english_layout(trigger_key)  # Синхронизация с английской раскладкой
        if trigger_key.lower() == 'done':
            break

        actions = []
        print(f"Создание макроса для клавиши '{trigger_key}'. Введите последовательность действий:")
        while True:
            keys = input("Клавиши (или 'done' для завершения макроса): ")
            keys = sync_with_english_layout(keys)  # Синхронизация с английской раскладкой
            if keys.lower() == 'done':
                break
            elif keys.lower() == '_help':
                print(HELP_TEXT)
                continue
            delay = float(input(f"Задержка перед нажатием клавиш '{keys}' (в секундах): "))
            actions.append({"key": keys, "delay": delay})

        sequence[trigger_key] = actions
        print(f"Макрос для клавиши '{trigger_key}' добавлен.")

    return sequence

# Функция для выполнения макроса
def execute_macro(sequence, trigger_key, stop_key):
    global stop_macro
    if trigger_key in sequence:
        stop_macro = False  # Сброс флага остановки
        for action in sequence[trigger_key]:
            # Проверяем, если задана клавиша остановки
            if stop_macro:
                print(f"Макрос остановлен, так как была нажата клавиша '{stop_key}'.")
                break  # Прерываем выполнение макроса

            time.sleep(action["delay"])
            keys = parse_keys(action["key"])
            for key in keys:
                keyboard.press_and_release(key)
    else:
        print(f"Макрос для клавиши '{trigger_key}' не найден.")

# Функция для разбора строки с клавишами
def parse_keys(keys):
    parsed_keys = []
    buffer = ""
    special_key = False

    for char in keys:
        if char == '(':
            if buffer:
                parsed_keys.append(buffer)
                buffer = ""
            special_key = True
            buffer += char
        elif char == ')':
            buffer += char
            if special_key:
                parsed_keys.append(buffer)
                buffer = ""
                special_key = False
        else:
            if special_key:
                buffer += char
            else:
                parsed_keys.append(char)

    if buffer:
        parsed_keys.append(buffer)

    # Преобразование специальных ключей
    for i, key in enumerate(parsed_keys):
        if key == "(alt)":
            keyboard.press("alt")
        elif key == "(-alt)":
            keyboard.release("alt")
        elif key == "(space)":
            parsed_keys[i] = "space"
        elif key == "(esc)":
            parsed_keys[i] = "esc"
        elif key == "(tab)":
            parsed_keys[i] = "tab"
        elif key == "(caps)":
            parsed_keys[i] = "caps lock"
        elif key == "(shift)":
            keyboard.press("shift")
        elif key == "(-shift)":
            keyboard.release("shift")
        elif key == "(ctrl)":
            keyboard.press("ctrl")
        elif key == "(-ctrl)":
            keyboard.release("ctrl")
        elif key == "(win)":
            keyboard.press("windows")
        elif key == "(-win)":
            keyboard.release("windows")
        elif key.startswith("(") and key.endswith(")"):
            print(f"Неизвестная специальная клавиша: {key}")

    return [key for key in parsed_keys if not key.startswith("(")]

# Функция для сохранения последовательности
def save_sequence(sequence, name):
    with open(f"{name}.json", "w") as f:
        json.dump(sequence, f)
    print(f"Последовательность '{name}' сохранена.")

# Функция для загрузки последовательности
def load_sequence(name):
    with open(f"{name}.json", "r") as f:
        return json.load(f)

# Функция для получения списка всех сохранённых последовательностей
def get_saved_sequences():
    return [f.replace(".json", "") for f in os.listdir() if f.endswith(".json")]

# Функция для выполнения макроса в отдельном потоке
def start_macro_thread(sequence, trigger_key, stop_key):
    macro_thread = threading.Thread(target=execute_macro, args=(sequence, trigger_key, stop_key))
    macro_thread.start()

# Функция для проверки нажатых клавиш
def check_pressed_key():
    print("Нажимайте клавиши для проверки. Для выхода нажмите 'q'.")
    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            pressed_key = event.name
            english_key = sync_with_english_layout(pressed_key)
            if english_key == 'q':
                print("Выход из режима проверки клавиш.")
                break
            else:
                print(f"Нажата клавиша: {english_key}")

# Главное меню программы
def main():
    global stop_macro
    while True:
        print("\n1. Создать новый макрос")
        print("2. Запустить макрос")
        print("3. Проверить нажатие клавиш")
        print("4. Выход")

        choice = input("Выберите действие: ")

        if choice == '1':
            name = input("Введите имя нового макроса: ")
            sequence = create_sequence()
            save_sequence(sequence, name)
        elif choice == '2':
            sequences = get_saved_sequences()
            if not sequences:
                print("Нет доступных макросов!")
                continue

            print("Доступные макросы:")
            for i, seq_name in enumerate(sequences, start=1):
                print(f"{i}. {seq_name}")

            seq_choice = int(input("Введите номер макроса для запуска: ")) - 1
            if 0 <= seq_choice < len(sequences):
                sequence_name = sequences[seq_choice]
                sequence = load_sequence(sequence_name)
                print(f"Запуск макроса '{sequence_name}'.")

                # Настройка клавиши остановки
                set_stop_key = input("Хотите установить клавишу для остановки макроса? (yes/no): ").lower()
                if set_stop_key == 'yes':
                    print(f"Выберите кнопку нажав на нее")
                    time.sleep(1)
                    event = keyboard.read_event()
                    pressed_key = event.name
                    stop_key = sync_with_english_layout(pressed_key)

                else:
                    stop_key = None  # Клавиша остановки не задается

                if stop_key:
                    print(f"Клавиша для остановки макроса: '{stop_key}'.")
                else:
                    print("Клавиша для остановки макроса не задана.")

                # Ожидание и выполнение макросов до прерывания
                while True:
                    if stop_key and keyboard.is_pressed(stop_key):
                        stop_macro = True

                    event = keyboard.read_event()
                    if event.event_type == keyboard.KEY_DOWN:
                        trigger_key = event.name
                        trigger_key = sync_with_english_layout(trigger_key)  # Синхронизация с английской раскладкой
                        if trigger_key in sequence:
                            start_macro_thread(sequence, trigger_key, stop_key)

        elif choice == '3':
            check_pressed_key()
        elif choice == '4':
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()

