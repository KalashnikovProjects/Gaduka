import re

"""
Для определения типа строки (выполнение функции, задание значения переменной, запуск цикла и т.д.)
используются регулярные выражения
"""

PASS_COMMAND = 'заглушка'
LINE_BREAK_CHARACTER = "-"
COMMENT_CHARACTER = "#"
PROHIBITION_WORDS = ('eval', "exec", "pillow", "os", "sys", "Image", 'exit')
print_logs = False


class GadukaException(Exception):
    ...


class ProhibitionWordError(GadukaException):
    pass


class LineBreakError(GadukaException):
    pass


class CompileStringError(GadukaException):
    pass


class FuncNotExist(GadukaException):
    pass


class ArgError(GadukaException):
    pass


class ToPythonCommands:
    """
    Базовые функции
    """

    @staticmethod
    def list_append(kwargs):
        return f'{kwargs["список"]}.append({kwargs["элемент"]})'

    @staticmethod
    def list_remove(kwargs):
        return f'{kwargs["список"]}.remove({kwargs["элемент"]})'

    @staticmethod
    def list_delete(kwargs):
        return f'{kwargs["список"]}.pop({kwargs["номер"]})'

    @staticmethod
    def list_extend(kwargs):
        return f'{kwargs["список"]}.extend({kwargs["элементы"]})'

    @staticmethod
    def list_join(kwargs):
        if "соединитель" not in kwargs:
            kwargs["соединитель"] = " "
        if "переменная" not in kwargs:
            kwargs["переменная"] = kwargs["список"]
        return f'{kwargs["переменная"]} = {kwargs["соединитель"]}.join({kwargs["список"]})'

    @staticmethod
    def str_split(kwargs):
        if "переменная" not in kwargs:
            kwargs["переменная"] = kwargs["строка"]

        if "разделитель" not in kwargs:
            return f'{kwargs["переменная"]} = {kwargs["строка"]}.split()'

        return f'{kwargs["переменная"]} = {kwargs["строка"]}.split({kwargs["разделитель"]})'

    @staticmethod
    def dict_remove(kwargs):
        return f'{kwargs["список"]}.pop({kwargs["номер"]})'

    """
    Функции вставки объектов на изображение
    """

    @staticmethod
    def paste_text_to_image(kwargs):
        ...

    @staticmethod
    def paste_image_to_image(kwargs):
        ...

    @staticmethod
    def paste_line_to_image(kwargs):
        ...

    @staticmethod
    def paste_arrow_to_image(kwargs):
        ...

    @staticmethod
    def paste_shape_to_image(kwargs):
        ...

    """
    Функции обработки изображений
    """

    @staticmethod
    def image_crop(kwargs):
        return f'{kwargs["изображение"]} = {kwargs["изображение"]}.crop((' \
                    f'{kwargs["левая_граница"]}, {kwargs["верхняя_граница"]},' \
                    f'{kwargs["правая_граница"]}, {kwargs["нижняя_граница"]}))'

    @staticmethod
    def image_resize(kwargs):
        return f'{kwargs["изображение"]} = {kwargs["изображение"]}.reduce({kwargs["коэффициент"]})'

    @staticmethod
    def image_rotate(kwargs):
        return f'{kwargs["изображение"]} = {kwargs["изображение"]}.rotate({kwargs["поворот"]}, expand=True)'

    @staticmethod
    def image_transpose(kwargs):
        ...

    @staticmethod
    def image_effect(kwargs):
        ...

    """
    Функции нейросети
    """

    @staticmethod
    def generate_text(kwargs):
        ...

    @staticmethod
    def learn_text(kwargs):
        ...

    """
    Другие функции
    """

    @staticmethod
    def add_text(kwargs):
        if print_logs:
            return f"""print({', '.join([str(i) for i in list(kwargs.values())])})"""
        else:
            return ...

    @staticmethod
    def add_image(kwargs):
        # Добавить картинку к результату
        return f"итоговые_изображения.append({kwargs['изображение']})"


COMMANDS = {
    "добавить элемент": ToPythonCommands.list_append,
    "убрать элемент": ToPythonCommands.list_remove,
    "удалить элемент": ToPythonCommands.list_delete,
    "расширить список": ToPythonCommands.list_extend,
    "все элементы": ToPythonCommands.list_join,
    "разделить строку": ToPythonCommands.str_split,
    "удалить ключ": ToPythonCommands.dict_remove,

    "наложить текст": ToPythonCommands.paste_text_to_image,
    "наложить картинку": ToPythonCommands.paste_image_to_image,
    "наложить линию": ToPythonCommands.paste_line_to_image,
    "наложить стрелку": ToPythonCommands.paste_arrow_to_image,
    "наложить многоугольник": ToPythonCommands.paste_shape_to_image,

    "обрезать изображение": ToPythonCommands.image_crop,
    "сжать изображение": ToPythonCommands.image_resize,
    "повернуть изображение": ToPythonCommands.image_rotate,
    "отразить изображение": ToPythonCommands.image_transpose,
    "наложить эффект": ToPythonCommands.image_effect,

    "сгенерировать текст": ToPythonCommands.generate_text,
    "изучить текст": ToPythonCommands.learn_text,

    "добавить текст": ToPythonCommands.add_text,
    "добавить изображение": ToPythonCommands.add_image,
}


def pre_code() -> list:
    constants = {'левый_верхний_угол': (0.05, 0.05),
                 'правый_верхний_угол': (0.95, 0.05),
                 'левый_нижний_угол': (0.05, 0.95),
                 'правый_нижний_угол': (0.95, 0.95),
                 'Верно': True,
                 'Неверно': False,
                 "итоговые_изображения": []}

    commands = [f"{var} = {value}" for var, value in constants.items()]
    commands.append("from PIL import Image")
    commands.append("")
    return commands


def compile_code(code: list, pre_code_py_commands: list = (), post_code_py_commands: list = (),
                 logs=False) -> list:
    global print_logs
    print_logs = logs

    # Принимает список строк кода на Гадюке
    # Возвращает код на Питоне (потом выполняется через exec())
    full_line: str = ''
    compiled_code: list = pre_code()
    compiled_code.extend(pre_code_py_commands)
    spaces_count = 0

    for line_num, line in enumerate(code):
        # Обрабатываем пробелы в строке
        line = line.replace("\t", "    ")
        if not full_line:
            spaces_count = len(line) - len(line.lstrip())
        line = line.strip()
        if line.startswith(COMMENT_CHARACTER):
            continue

        if not full_line and line.startswith(LINE_BREAK_CHARACTER):
            raise LineBreakError(f"Ошибка в строке номер {line_num}: {line} \n"
                                 f"Строка номер {line_num - 1} не заканчивается символом переноса строки\n"
                                 f"Но следующая строка, строка номер {line_num}, начинается с него.")
        elif full_line and not line.startswith("-"):
            raise LineBreakError(f"Ошибка в строке номер {line_num}: {line} \n"
                                 f"Строка номер {line_num - 1} заканчивается на символ переноса строки\n"
                                 f"Но следующая строка, строка номер {line_num}, не начинается с него.")

        full_line += line.strip(LINE_BREAK_CHARACTER) + " "

        if not line.endswith(LINE_BREAK_CHARACTER):
            # Строка закончена,
            compiled_code.append(" " * spaces_count + compile_line(line, line_num=line_num))
            full_line = ''

    if full_line:
        raise LineBreakError("Ошибка: Последняя строка вашего кода заканчивается символом переноса строки"
                             "Возможно вы случайно поставили лишний символ или незакончили свой код.")

    compiled_code.extend(post_code_py_commands)
    return compiled_code


def compile_line(line: str, line_num=0) -> str:
    # Возвращает ту же строчку, но на python
    structure_finder = re.sub(r"""".*?"|'.*?'""", 'text', line)
    # заменяет строки в ковычках на text,
    # что бы игнорировать то что написано в ковычках

    if line == PASS_COMMAND or not (line):
        return "pass"

    for i in PROHIBITION_WORDS:
        if re.search(f"\W{i}\W", "%" + structure_finder + "%"):
            raise ProhibitionWordError(f"Ошибка в строке номер {line_num}: {line} \n"
                                       f"Некоторые названия нельзя использовать в своей программе:\n" +
                                       ", ".join(PROHIBITION_WORDS) + "\n"
                                                                      f"В вашей программе используется название '{i}'.")

    if re.fullmatch("повтор .+ раз:", structure_finder):
        """ 
        цикл for
        """
        count = line.lstrip("повтор ").rstrip(" раз:")
        return f"for номер_повтора in range({count}):"

    elif re.fullmatch("повтор пока .+:", structure_finder):
        """ 
        цикл while
        """
        condition = line.lstrip("повтор пока ").rstrip(":")

        return f"while {condition}:"
    elif re.fullmatch("если .+:", structure_finder):
        """ 
        условие if 
        """
        condition = line.lstrip("если ").rstrip(":")
        return f"if {condition}:"

    elif re.fullmatch("иначе если .+:", structure_finder):
        """ 
        условие elif 
        """
        condition = line.lstrip("иначе если ").rstrip(":")
        return f"elif {condition}:"

    elif re.fullmatch("иначе:", structure_finder):
        """ 
        условие else 
        """
        return "else:"

    elif re.fullmatch("[\w\[\].]+.\w+(\(.*\))?", structure_finder):
        """
        вызывание функции у переменной
        например
        список.добавить(123)
        """
        return get_func(line, line_num)

    elif re.fullmatch("(\w ?)+: (\w+ *= *[\S ]+,? *)+", structure_finder):
        """
        выполнение команды
        например
        отправить текст: текст=123
        """
        return get_command(line, line_num)

    elif re.fullmatch("[\w\[\]]+ *[!+-/*%><]{1,2}= *.+", structure_finder):
        """
        задание / изменение переменной
        например
        переменная = 123 / 3
        переменная_12_qwert += 44
        """
        return line
    else:
        raise CompileStringError(f"Ошибка в строке номер {line_num}: {line} \n"
                                 f"В оформлении строки есть ошибка.")


def get_func(gaduka_command: str, line_num) -> str:
    return "аргумент или функция"


def get_command(gaduka_command: str, line_num) -> str:
    if len(gaduka_command.split(":")) != 2:
        raise CompileStringError(f"Ошибка в строке номер {line_num}: {gaduka_command} \n"
                                 f"В оформлении строки есть ошибка.")
    command, args = gaduka_command.split(":")
    kwargs = {i.split("=")[0].strip(): i.split("=")[1].strip() for i in args.split(",")}
    if command not in COMMANDS:
        raise FuncNotExist(f"Ошибка в строке номер {line_num}: {gaduka_command} \n"
                           f"Команды с именем '{command}' не существует.")
    try:
        result = COMMANDS[command](kwargs)
    except KeyError as e:
        raise ArgError(f"Ошибка в строке номер {line_num}: {gaduka_command} \n"
                       f"Вы не передали аргумент {e} в команду '{command}'.")
    return result
