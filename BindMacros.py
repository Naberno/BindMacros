import keyboard
import time
import json
import os

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

# Функция для создания новой последовательности
def create_sequence():
    sequence = {}
    print("Создание новой последовательности.")
    print(HELP_TEXT)
    while True:
        trigger_key = input("Введите клавишу, которая будет запускать макрос (или 'done' для завершения): ")
        if trigger_key.lower() == 'done':
            break
        
        actions = []
        print(f"Создание макроса для клавиши '{trigger_key}'. Введите последовательность действий:")
        while True:
            keys = input("Клавиши (или 'done' для завершения макроса): ")
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
def execute_macro(sequence, trigger_key):
    if trigger_key in sequence:
        for action in sequence[trigger_key]:
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

# Главное меню программы
def main():
    while True:
        print("\n1. Создать новую последовательность")
        print("2. Запустить последовательность")
        print("3. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            name = input("Введите имя новой последовательности: ")
            sequence = create_sequence()
            save_sequence(sequence, name)
        elif choice == '2':
            sequences = get_saved_sequences()
            if not sequences:
                print("Нет доступных последовательностей!")
                continue
            
            print("Доступные последовательности:")
            for i, seq_name in enumerate(sequences, start=1):
                print(f"{i}. {seq_name}")
            
            seq_choice = int(input("Введите номер последовательности для выполнения: ")) - 1
            if 0 <= seq_choice < len(sequences):
                sequence_name = sequences[seq_choice]
                sequence = load_sequence(sequence_name)
                print(f"Запуск последовательности '{sequence_name}'. Нажмите соответствующую клавишу для выполнения макроса.")

                # Ожидание и выполнение макросов до прерывания
                while True:
                    event = keyboard.read_event()
                    if event.event_type == keyboard.KEY_DOWN:
                        trigger_key = event.name
                        if trigger_key in sequence:
                            execute_macro(sequence, trigger_key)
                        else:
                            print(f"Макрос для клавиши '{trigger_key}' не найден в текущей последовательности.")
                    
        elif choice == '3':
            break
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == "__main__":
    main()
