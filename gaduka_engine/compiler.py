import re
from copy import copy

from PIL import Image

"""
Для определения типа строки (выполнение функции, задание значения переменной, запуск цикла и т.д.)
используются регулярные выражения
"""

PASS_COMMAND = 'заглушка'
LINE_BREAK_CHARACTER = "-"
COMMENT_CHARACTER = "#"
PROHIBITION_WORDS = ('eval', "exec", "PIL", "os", "sys", "Image", 'exit', "import",
                     "ImageDraw", "ImageFont", 'compiler_data', 'ImageFilter', "del",
                     "return", "assert", "nonlocal", "global", "super", 'quit', 'raise')

TYPES = {"list": "список", "str": "строка", "int": "число", "bool": "логический",
         "dict": "список", "tuple": "неизменяемый список", "set": "множество",
         "function": "функция", "float": "число", "NoneType": 'ничего'}


class GadukaStr(str):
    def __new__(cls, *args, **kwargs):
        args = list(args)
        for index, want_to_be_string in enumerate(args):
            if isinstance(want_to_be_string, bool):
                args[index] = "Верно" if want_to_be_string else "Неверно"
            else:
                args[index] = str(want_to_be_string)
        return cls.__new__(str, " ".join(args))


class GadukaImage(Image.Image):
    '''
    Переопределённый унаследованный класс Изображений из Pillow
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getattribute__(self, item):
        custom_attrs = {"размер": "size",
                        "ширина": 'width',
                        "высота": 'height'}

        if item in custom_attrs:
            return super().__getattribute__(custom_attrs[item])
        attr = super().__getattribute__(item)
        if item not in ('__getstate__', "getpalette", 'tobytes', '__class__', "__setstate__", 'frombytes', "copy") and \
                callable(attr):
            if item in ("crop", "reduce", "_open", "load", "_new", "convert", 'rotate',
                        "copy", "paste", 'transform',
                        "filter", "transpose",
                        "__reduce_ex__", "_ensure_mutable", "_Image__transformer"):
                return attr
            else:
                raise AttributeError(item)
        else:
            return attr

    def __copy__(self):
        return super().copy()


def gaduka_type(obj):
    types_to_ru = {
        str: "Строка",
        int: "Число",
        dict: "Словарь",
        float: "Десятичная дробь",
        set: "Множество",
        list: "Список",
        tuple: "Неизменяемый список",
        enumerate: "Пронумерованный список",
        range: "Диапазон"}

    if callable(obj):
        return "Функция"
    return types_to_ru.get(type(obj), f"Объект класса {obj.__class__}")


def get_exec_funcs():
    a = {i: 'trollface' for i in ('eval', 'exit', 'super', 'quit', 'exec', 'os')}
    b = {
        "__builtins__": {"__import__": __import__},
        "диапазон": range,
        "модуль": abs,
        "все": all,
        "любой": any,
        "словарь": dict,
        "пронумеровать": enumerate,
        "десятичная_дробь": float,
        "число": int,
        "длинна": len,
        "список": list,
        "наибольшее_значение": max,
        "наименьшее_значение": min,
        "корень": pow,
        "округлить": round,
        "множество": set,
        "отсортировать": sorted,
        "строка": GadukaStr,
        "сумма": sum,
        "кортеж": tuple,
        "тип": gaduka_type,
        "изображение": GadukaImage
    }
    return a | b


class GadukaException(Exception):
    pass


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
            kwargs["соединитель"] = "' '"
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
        if "цвет" not in kwargs:
            kwargs["цвет"] = '"black"'

        return f"""
        class compiler_data: pass
        compiler_data.draw = ImageDraw.Draw({kwargs['куда']})
        compiler_data.font = ImageFont.truetype("arial.ttf", 50, encoding='UTF-8')
        compiler_data.w, compiler_data.h = compiler_data.draw.textsize({kwargs['текст']}, font=compiler_data.font)
        compiler_data.place = list({kwargs['где']})
        compiler_data.place[0] = compiler_data.place[0] * {kwargs['куда']}.width - compiler_data.w // 2
        compiler_data.place[1] = compiler_data.place[1] * {kwargs['куда']}.height - compiler_data.h // 2
        compiler_data.draw.text(compiler_data.place, {kwargs['текст']}, fill={kwargs["цвет"]}, 
        font=compiler_data.font)\n
        """

    @staticmethod
    def paste_image_to_image(kwargs):
        return f"""
        class compiler_data: pass
        compiler_data.background = {kwargs['куда']}
        compiler_data.img = {kwargs['какую']}
        compiler_data.w, compiler_data.h = compiler_data.img.size
        compiler_data.place = list({kwargs['где']})
        compiler_data.place[0] = int(compiler_data.place[0] * {kwargs['куда']}.width - compiler_data.w // 2)
        compiler_data.place[1] = int(compiler_data.place[1] * {kwargs['куда']}.height - compiler_data.h // 2)
        compiler_data.background.paste(compiler_data.img, compiler_data.place, compiler_data.img)\n
        """

    @staticmethod
    def paste_line_to_image(kwargs):
        if "цвет" not in kwargs:
            kwargs["цвет"] = '"black"'
        if "ширина" not in kwargs:
            kwargs["ширина"] = '2'

        return f"""
        class compiler_data: pass
        compiler_data.draw = ImageDraw.Draw({kwargs['куда']})
        compiler_data.li = []
        for compiler_data.i in {kwargs['точки']}:
            compiler_data.i = list(compiler_data.i)
            compiler_data.i[0] = compiler_data.i[0] * {kwargs['куда']}.width
            compiler_data.i[1] = compiler_data.i[1] * {kwargs['куда']}.height
            compiler_data.li.append(tuple(compiler_data.i))
        compiler_data.draw.line(compiler_data.li, fill={kwargs["цвет"]}, width={kwargs["ширина"]})\n
        """

    @staticmethod
    def paste_circle_to_image(kwargs):
        if "ширина_обводки" not in kwargs:
            kwargs["ширина_обводки"] = '2'
        if "цвет" not in kwargs and "обводка" not in kwargs:
            a = f'outline="black"'
        elif "цвет" not in kwargs:
            a = f'outline={kwargs["обводка"]}'
        elif "обводка" not in kwargs:
            a = f'fill={kwargs["цвет"]}'
        else:
            a = f'fill={kwargs["цвет"]}, outline={kwargs["обводка"]}'

        return f"""class compiler_data: pass
        compiler_data.draw = ImageDraw.Draw({kwargs['куда']})
        compiler_data.rad = {kwargs['радиус']}
        compiler_data.li = (({kwargs['центр']}[0] - {kwargs['радиус']}) * {kwargs['куда']}.width,
                                ({kwargs['центр']}[1] - {kwargs['радиус']}) * {kwargs['куда']}.height,
                                ({kwargs['центр']}[0] + {kwargs['радиус']}) * {kwargs['куда']}.width,
                                ({kwargs['центр']}[1] + {kwargs['радиус']}) * {kwargs['куда']}.height,)
                                
        compiler_data.draw.ellipse(compiler_data.li, {a}, width={kwargs["ширина_обводки"]})\n
        """

    @staticmethod
    def paste_shape_to_image(kwargs):
        if "ширина_обводки" not in kwargs:
            kwargs["ширина_обводки"] = '2'
        if "цвет" not in kwargs and "обводка" not in kwargs:
            a = f'outline="black"'
        elif "цвет" not in kwargs:
            a = f'outline={kwargs["обводка"]}'
        elif "обводка" not in kwargs:
            a = f'fill={kwargs["цвет"]}'
        else:
            a = f'fill={kwargs["цвет"]}, outline={kwargs["обводка"]}'

        return f"""
        class compiler_data: pass
        compiler_data.draw = ImageDraw.Draw({kwargs['куда']})
        compiler_data.li = []
        for compiler_data.i in {kwargs['углы']}:
            compiler_data.i = list(compiler_data.i)
            compiler_data.i[0] = compiler_data.i[0] * {kwargs['куда']}.width
            compiler_data.i[1] = compiler_data.i[1] * {kwargs['куда']}.height
            compiler_data.li.append(tuple(compiler_data.i))
        compiler_data.draw.polygon(compiler_data.li, {a}, width={kwargs["ширина_обводки"]})\n
        """

    @staticmethod
    def paste_rect_to_image(kwargs):
        if "ширина_обводки" not in kwargs:
            kwargs["ширина_обводки"] = '2'
        if "цвет" not in kwargs and "обводка" not in kwargs:
            a = f'outline="black"'
        elif "цвет" not in kwargs:
            a = f'outline={kwargs["обводка"]}'
        elif "обводка" not in kwargs:
            a = f'fill={kwargs["цвет"]}'
        else:
            a = f'fill={kwargs["цвет"]}, outline={kwargs["обводка"]}'

        return f"""class compiler_data: pass
        compiler_data.draw = ImageDraw.Draw({kwargs['куда']})
        compiler_data.li = ({kwargs['где']}[0] * {kwargs['куда']}.width,
                                {kwargs['где']}[1] * {kwargs['куда']}.height,
                                ({kwargs['где']}[0] + {kwargs['ширина']}) * {kwargs['куда']}.width,
                                ({kwargs['где']}[1] + {kwargs['высота']}) * {kwargs['куда']}.height,)

        compiler_data.draw.rectangle(compiler_data.li, {a}, width={kwargs["ширина_обводки"]})\n
        """

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
        if kwargs.get("по_горизонтали", False) and kwargs.get("по_вертикали", False):
            return f'{kwargs["изображение"]} = {kwargs["изображение"]}.transpose(Image.FLIP_LEFT_RIGHT)\n' \
                   f'{kwargs["изображение"]} = {kwargs["изображение"]}.transpose(Image.FLIP_TOP_BOTTOM)'

        elif kwargs.get("по_горизонтали", False):
            return f'{kwargs["изображение"]} = {kwargs["изображение"]}.transpose(Image.FLIP_LEFT_RIGHT)\n'
        elif kwargs.get("по_вертикали", False):
            return f'{kwargs["изображение"]} = {kwargs["изображение"]}.transpose(Image.FLIP_TOP_BOTTOM)\n'
        else:
            return "pass"

    @staticmethod
    def image_effects(kwargs):
        filters = {"блюр": f'{kwargs["изображение"]} = {kwargs["изображение"]}.filter(ImageFilter.BLUR)',
                   "выпуклость": f'{kwargs["изображение"]} = {kwargs["изображение"]}.filter(ImageFilter.EMBOSS)',
                   "серость": f'{kwargs["изображение"]} = {kwargs["изображение"]}.convert("L")',
                   "границы": f'''class compiler_data: pass
        {kwargs["изображение"]} = {kwargs["изображение"]}.filter(ImageFilter.BLUR)
        '''}

        a = []
        for i in kwargs.keys():
            if i in filters:
                a.append(filters[i])

        if not a:
            return "pass"
        return ";".join(a)

    """
    Функции нейросети
    отменены
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
        text = f"строка({', '.join([str(i) for i in list(kwargs.values())])})"
        return f"""итоговый_текст.append({text})"""

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
    "наложить многоугольник": ToPythonCommands.paste_shape_to_image,
    "наложить прямоугольник": ToPythonCommands.paste_rect_to_image,
    "наложить круг": ToPythonCommands.paste_circle_to_image,
    # "наложить стрелку": ToPythonCommands.paste_arrow_to_image,

    "обрезать изображение": ToPythonCommands.image_crop,
    "сжать изображение": ToPythonCommands.image_resize,
    "повернуть изображение": ToPythonCommands.image_rotate,
    "отразить изображение": ToPythonCommands.image_transpose,
    "наложить эффект": ToPythonCommands.image_effects,

    # "сгенерировать текст": ToPythonCommands.generate_text,
    # "изучить текст": ToPythonCommands.learn_text,

    "добавить текст": ToPythonCommands.add_text,
    "добавить изображение": ToPythonCommands.add_image,
}


def pre_code() -> list:
    gaduka_pre_code_vars = {'левый_верхний_угол': (0.05, 0.05),
                            'правый_верхний_угол': (0.95, 0.05),
                            'левый_нижний_угол': (0.05, 0.95),
                            'правый_нижний_угол': (0.95, 0.95),
                            'по_центру': (0.5, 0.5),

                            'Верно': True,
                            'Неверно': False,

                            "чёрный": "'black'",
                            "белый": "'white'",
                            "красный": "'red'",
                            "серый": "'gray'",
                            "оранжевый": "'orange'",
                            "жёлтый": "'yellow'",
                            "зелёный": "'green'",
                            "синий": "'blue'",
                            "розовый": "'pink'",
                            "фиолетовый": "'violet'"}

    commands = ["from PIL import Image, ImageDraw, ImageFont, ImageFilter",
                "from copy import copy as копия",]
    commands.extend([f"{var} = {value}" for var, value in gaduka_pre_code_vars.items()])
    return commands


def compile_code(code: list, pre_code_py_commands: list = ()) -> tuple[list, dict]:
    # Принимает список строк кода на Гадюке
    # Возвращает код на Питоне (потом выполняется через exec())
    full_line: str = ''
    compiled_code: list = pre_code()
    compiled_code.extend(pre_code_py_commands)
    compiled_to_not_compiled_match: dict = {}
    spaces_count = 0
    line_break_count = 0
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

        full_line += line.strip(LINE_BREAK_CHARACTER)

        if not line.endswith(LINE_BREAK_CHARACTER):
            # Строка закончена
            compil = compile_line(full_line, line_num=line_num - line_break_count)
            multistring = compil.split("\n")
            flag = True
            for mult_str in multistring:
                compiled_to_not_compiled_match[mult_str] = line_num - line_break_count
                if flag:
                    compiled_code.append(" " * spaces_count + mult_str)
                    flag = False
                else:
                    compiled_code.append(mult_str)
            line_break_count = 0
            full_line = ''
        else:
            line_break_count += 1

    if full_line:
        raise LineBreakError("Ошибка: Последняя строка вашего кода заканчивается символом переноса строки"
                             "Возможно вы случайно поставили лишний символ или незакончили свой код.")

    return compiled_code, compiled_to_not_compiled_match


def compile_line(line: str, line_num=0) -> str:
    if line == PASS_COMMAND or not (line):
        return "pass"

    # Возвращает ту же строчку, но на python
    sussy_baka = "   ".join(re.findall(r"""f".*\{.*?}.*"|f'.*\{.*?}.*'""", line))
    structure_finder = re.sub(r"""".*?"|'.*?'""", 'text', line)
    # заменяет строки в ковычках на text,
    # что бы игнорировать то что написано в ковычках

    """
    Проверка на содержание технических названий в коде
    """
    for i in PROHIBITION_WORDS:
        if re.search(f"\W{i}\W", "%" + structure_finder + "%") or re.search(f"\W{i}\W", "%" + sussy_baka + "%"):
            raise ProhibitionWordError(f"Ошибка в строке номер {line_num}: \n{line} \n"
                                       f"Некоторые названия нельзя использовать в своей программе:\n" +
                                       ", ".join(PROHIBITION_WORDS) + "\n"
                                       f"В вашей программе используется название '{i}'.")

    if re.fullmatch("повтор .+ раз:", structure_finder):
        """ 
        цикл for
        """
        count = line.removeprefix("повтор ").rstrip(" раз:")
        return f"for номер_повтора in диапазон({count}):"

    elif re.fullmatch("повтор пока .+:", structure_finder):
        """ 
        цикл while
        """
        condition = line.removeprefix("повтор пока ").rstrip(":")

        return f"while {condition}:"
    elif re.fullmatch("если .+:", structure_finder):
        """ 
        условие if 
        """
        condition = line.removeprefix("если ").rstrip(":")
        return f"if {condition}:"

    elif re.fullmatch("иначе если .+:", structure_finder):
        """ 
        условие elif 
        """
        condition = line.removeprefix("иначе если ").rstrip(":")
        return f"elif {condition}:"

    elif re.fullmatch("иначе:", structure_finder):
        """ 
        условие else 
        """
        return "else:"

    elif re.fullmatch("(?:[\w\[\].]*\.)*\w+\(.*\)", structure_finder):
        """
        вызывание функции у переменной
        например
        список.добавить(123)
        print()
        """
        return line

    elif re.fullmatch("(\w ?)+: (?:\w+ *=? *[\S ]+,? *)+", structure_finder):
        """
        выполнение команды
        например
        отправить текст: текст=123
        """
        return get_command(line, line_num)

    elif re.fullmatch("[\w\[\]]+ *[!+-/*%><]{0,2}= *.+", structure_finder):
        """
        задание / изменение переменной
        например
        переменная = 123 / 3
        переменная_12_qwert += 44
        """
        return line
    else:
        raise CompileStringError(f"Ошибка в строке номер {line_num}: \n{line} \n"
                                 f"В оформлении строки есть ошибка.")


def get_func(gaduka_command: str, line_num) -> str:
    raise CompileStringError(f"Ошибка в строке номер {line_num}: \n{gaduka_command} \n"
                             f"В гадюке нет функционала вызова функции у объекта")


def get_command(gaduka_command: str, line_num) -> str:
    if len(gaduka_command.split(":")) == 1:
        raise CompileStringError(f"Ошибка в строке номер {line_num}: \n{gaduka_command} \n"
                                 f"В оформлении строки есть ошибка.")
    command, *args = gaduka_command.split(":")
    args = ":".join(args)

    kwargs = {}
    brackets_count = 0
    open_brackets = """({["""
    closed_brackets = """)]}"""
    quote_count = None
    a = ""

    for i in args:
        if i == "," and brackets_count == 0 and not quote_count:
            if "=" in a:
                result = re.findall(r'''(["'].+?["']|[^=]+)''', a)
                kwargs[result[0].strip()] = result[1].strip()
            else:
                kwargs[a.strip()] = True
            a = ""
        else:
            a += i

        if not quote_count and i in open_brackets:
            brackets_count += 1
        elif not quote_count and i in closed_brackets:
            brackets_count -= 1
        elif i == '"' or i == "'":
            if quote_count == i:
                quote_count = None
            elif quote_count is None:
                quote_count = i
    if "=" in a:
        result = re.findall(r'''(["'].+?["']|[^=]+)''', a)
        kwargs[result[0].strip()] = result[1].strip()
    else:
        kwargs[a.strip()] = True
    # kwargs = {i.split("=")[0].strip(): i.split("=")[1].strip() for i in args.split(", ")}

    if command not in COMMANDS:
        raise FuncNotExist(f"Ошибка в строке номер {line_num}: \n{gaduka_command} \n"
                           f"Команды с именем '{command}' не существует.")
    try:
        result = COMMANDS[command](kwargs)
    except KeyError as e:
        raise ArgError(f"Ошибка в строке номер {line_num}: \n{gaduka_command} \n"
                       f"Вы не передали аргумент {e} в команду '{command}'.")
    return result