import math
import random
import re

from PIL import Image, ImageDraw, ImageFont, ImageFilter, PngImagePlugin
from PIL.PngImagePlugin import PngImageFile

"""
Для определения типа строки (выполнение функции, задание значения переменной, запуск цикла и т.д.)
используются регулярные выражения

У некоторых функций аргументы названы на русском, эти функции можно вызывать напрямую из языка
"""

PASS_COMMANDS = ('заглушка', "...")
LINE_BREAK_CHARACTER = "-"
COMMENT_CHARACTER = "#"
PROHIBITION_WORDS = ('eval', "exec", "PIL", "os", "sys", "Image", 'exit', "import", "lambda",
                     "ImageDraw", "ImageFont", 'compiler_data', 'ImageFilter', "del",
                     "return", "assert", "nonlocal", "global", "super", 'quit', 'raise')

TYPES = {"list": "список", "str": "строка", "int": "число", "bool": "логический тип",
         "frozenset": "Неизменяемое множество",
         "dict": "словарь", "tuple": "неизменяемый список", "set": "множество",
         "function": "функция", "float": "Десятичная дробь", "NoneType": 'ничего'}

WORDS_FOR_REPLACE = {
    "или": "or",
    "и": "and",
    "в": "in",
    "не": "not"
}
result_imgs, result_text = [], []


def super_replace(text, before, after):
    result = re.finditer(fr'''".*?"|'.*?'|(\b{before}\b)''', text, re.MULTILINE)
    res = list(text)
    for match in list(result)[::-1]:
        if match.group(1):
            del res[match.start(1): match.end(1)]
            res.insert(match.start(1), after)
    return "".join(res)


def removeprefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


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
    """
    Переопределённый унаследованный класс Изображений из Pillow
    """

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
        range: "Диапазон",
        frozenset: "Неизменяемое множество",
        type(None): "Ничего"}

    if callable(obj):
        return "Функция"
    return types_to_ru.get(type(obj), f"Объект класса {obj.__class__}")


def all_elements(список, соединитель=" "):
    return соединитель.join([str(i) for i in список])


def split_string(строка, разделитель=None):
    if разделитель:
        return строка.split(разделитель)
    else:
        return строка.split()


def get_exec_funcs():
    a = {i: 'trollface' for i in ('eval', 'exit', 'super', 'quit', 'exec', 'os')}
    b = {
        "__builtins__": {"__import__": __import__},
        "ничего": None,
        "печать": ToPythonFunctions.print_any,
        "добавить": ToPythonFunctions.list_append,
        "убрать": ToPythonFunctions.list_remove,
        "удалить": ToPythonFunctions.delete,
        "объединить": ToPythonFunctions.list_extend,
        "диапазон": range,
        "модуль": abs,
        "все": all,
        "любой": any,
        "словарь": dict,
        "пронумеровать": enumerate,
        "десятичная_дробь": float,
        "число": int,
        "длина": len,
        "список": list,
        "наибольшее": max,
        "наименьшее": min,
        "случайное_число": random.randint,
        "случайный_элемент": random.choice,
        "корень": math.sqrt,
        "округлить": round,
        "множество": set,
        "отсортировать": sorted,
        "строка": GadukaStr,
        "сумма": sum,
        "кортеж": tuple,
        "тип": gaduka_type,
        "изображение": GadukaImage,
        "разделить_строку": split_string,
        "все_элементы": all_elements,
        "добавить_текст": ToPythonFunctions.paste_text_to_image,
        "добавить_картинку": ToPythonFunctions.paste_image_to_image,
        "добавить_линию": ToPythonFunctions.paste_line_to_image,
        "добавить_многоугольник": ToPythonFunctions.paste_shape_to_image,
        "добавить_прямоугольник": ToPythonFunctions.paste_rect_to_image,
        "добавить_круг": ToPythonFunctions.paste_circle_to_image,
        "обрезать": ToPythonFunctions.image_crop,
        "сжать": ToPythonFunctions.image_resize,
        "повернуть": ToPythonFunctions.image_rotate,
        "отразить": ToPythonFunctions.image_transpose,
        "эффекты": ToPythonFunctions.image_effects
    }
    return {**a, **b}


class GadukaException(Exception):
    pass


class ProhibitionWordError(GadukaException):
    pass


class LineBreakError(GadukaException):
    pass


class CompileStringError(GadukaException):
    pass


class ArgError(GadukaException):
    pass


class ToPythonFunctions:
    """
    Базовые функции
    """

    @staticmethod
    def print_any(*данные):
        res_t = []
        for i in данные:
            if "image" in i.__class__.__name__.lower():
                result_imgs.append(i)
            else:
                res_t.append(str(i))
        result_text.append(' '.join(res_t))

    @staticmethod
    def list_append(список, элемент):
        список.append(элемент)

    @staticmethod
    def list_remove(список, элемент):
        список.remove(элемент)

    @staticmethod
    def delete(объект, номер):
        объект.pop(номер)

    @staticmethod
    def list_extend(список, элементы):
        список.extend(элементы)

    """
    Функции вставки объектов на изображение
    """

    @staticmethod
    def paste_text_to_image(куда, где, текст, размер=50, цвет="black"):
        draw = ImageDraw.Draw(куда)
        font = ImageFont.truetype("Pillow/Tests/fonts/DejaVuSans.ttf", size=размер)
        w, h = draw.textsize(текст, font=font)
        place = [int(где[0] * куда.width - w // 2), int(где[1] * куда.height - h // 2)]
        draw.text(place, текст, fill=цвет, font=font)

    @staticmethod
    def paste_image_to_image(куда, где, какую):
        background = куда
        img = какую
        w, h = img.size
        place = [int(где[0] * куда.width - w // 2), int(где[1] * куда.height - h // 2)]
        background.paste(img, place, img)

    @staticmethod
    def paste_line_to_image(куда, точки, цвет="black", ширина=2):
        draw = ImageDraw.Draw(куда)
        li = [(int(i[0] * куда.width), int(i[1] * куда.height)) for i in точки]
        draw.line(li, fill=цвет, width=ширина)

    @staticmethod
    def paste_circle_to_image(куда, центр, радиус, ширина_обводки=2, обводка=None, цвет=None):
        draw = ImageDraw.Draw(куда)
        li = (int((центр[0] - радиус) * куда.width),
              int((центр[1] - радиус) * куда.height),
              int((центр[0] + радиус) * куда.width),
              int((центр[1] + радиус) * куда.height))
        if not цвет and not обводка:
            обводка = "black"
        draw.ellipse(li, width=ширина_обводки, fill=цвет, outline=обводка)

    @staticmethod
    def paste_shape_to_image(куда, углы, ширина_обводки=2, обводка=None, цвет=None):
        draw = ImageDraw.Draw(куда)
        li = [(int(i[0] * куда.width), int(i[1] * куда.height)) for i in углы]
        if not цвет and not обводка:
            обводка = "black"
        draw.polygon(li, fill=цвет, outline=обводка, width=ширина_обводки)

    @staticmethod
    def paste_rect_to_image(куда, где, высота, ширина, ширина_обводки=2, обводка=None, цвет=None):
        draw = ImageDraw.Draw(куда)
        li = (int(где[0] * куда.width),
              int(где[1] * куда.height),
              int((где[0] + ширина) * куда.width),
              int((где[1] + высота) * куда.height))
        if not цвет and not обводка:
            обводка = "black"
        draw.rectangle(li, width=int(ширина_обводки), outline=обводка, fill=цвет)

    """
    Функции обработки изображений
    """

    @staticmethod
    def image_crop(изображение, углы):
        # изображение = обрезать(изображение, углы)
        if len(углы) != 4:
            raise ArgError("Нужно указать 4 угла для обрезки изображения")
        return изображение.crop(углы)

    @staticmethod
    def image_resize(изображение, коэффициент):
        # изображение = сжать(изображение, коэффициент)
        return изображение.reduce(коэффициент)

    @staticmethod
    def image_rotate(изображение, поворот):
        # изображение = повернуть(изображение, поворот)
        return изображение.rotate(поворот, expand=True)

    @staticmethod
    def image_transpose(изображение, по_вертикали=False, по_горизонтали=False):
        # изображение = отразить(изображение)

        if not(по_вертикали or по_горизонтали):
            по_горизонтали = True

        if по_горизонтали:
            изображение = изображение.transpose(Image.FLIP_LEFT_RIGHT)
        if по_вертикали:
            изображение = изображение.transpose(Image.FLIP_TOP_BOTTOM)

        return изображение

    @staticmethod
    def image_effects(изображение, *эффекты):
        # изображение = эффекты(изображение, [])

        filters = {"блюр": ImageFilter.BLUR,
                   "выпуклость": ImageFilter.EMBOSS,
                   "границы": ImageFilter.CONTOUR}

        for i in эффекты:
            if i in filters:
                изображение = изображение.filter(filters[i])
            if i == "серость":
                изображение = изображение.convert("L")

        return изображение


def pre_code():
    gaduka_pre_code_vars = {'левый_верхний_угол': (0.05, 0.05),
                            'правый_верхний_угол': (0.95, 0.05),
                            'левый_нижний_угол': (0.05, 0.95),
                            'правый_нижний_угол': (0.95, 0.95),
                            'по_центру': (0.5, 0.5),

                            'Верно': True,
                            'Неверно': False,

                            'блюр': "'блюр'",
                            'выпуклость': "'выпуклость'",
                            'серость': "'серость'",
                            'границы': "'границы'",

                            "чёрный": "'black'", "черный": "'black'",
                            "белый": "'white'",
                            "красный": "'red'",
                            "серый": "'gray'",
                            "оранжевый": "'orange'",
                            "жёлтый": "'yellow'", "желтый": "'yellow'",
                            "зелёный": "'green'", "зеленый": "'green'",
                            "синий": "'blue'",
                            "розовый": "'pink'",
                            "фиолетовый": "'violet'"}

    commands = ["from PIL import Image, ImageDraw, ImageFont, ImageFilter",
                "from copy import copy as копия"]
    commands.extend([f"{var} = {value}" for var, value in gaduka_pre_code_vars.items()])
    return commands


def compile_code(code, pre_code_py_commands=()):
    # Принимает список строк кода на Гадюке.
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
                             "Возможно вы случайно поставили лишний символ или не закончили свой код.")

    return compiled_code, compiled_to_not_compiled_match


def compile_line(line, line_num=0):
    if line in PASS_COMMANDS:
        return "pass"

    if not line:
        return ""

    if "#" in line:
        br_count = 0
        for n, i in enumerate(line):
            if i == "#" and br_count % 2 == 0:
                line = line[:n]
                break
            elif i in ("'", '"'):
                br_count += 1

    if line.endswith(";"):
        raise CompileStringError(f"Ошибка в строке номер {line_num}: \n{line} \n"
                                 f"В Гадюке, в отличии от многих других языков, не нужно ставить ';' в конце строки.")

    for i in WORDS_FOR_REPLACE.items():
        line = super_replace(line, i[0], i[1])

    # Возвращает ту же строчку, но на python
    sussy_baka = "   ".join(re.findall(r"""f".*\{.*?}.*"|f'.*\{.*?}.*'""", line))  # Проверка с f строками
    structure_finder = re.sub(r"""".*?"|'.*?'""", 'text', line)

    # заменяет строки в кавычках на text,
    # что бы игнорировать то что написано в кавычках

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
        count = removeprefix(line, "повтор ").rstrip(" раз:")
        return f"for номер_повтора in диапазон({count}):"

    elif re.fullmatch("повтор пока .+:", structure_finder):
        """ 
        цикл while
        """
        condition = removeprefix(line, "повтор пока ").rstrip(":")

        return f"while {condition}:"
    elif re.fullmatch("если .+:", structure_finder):
        """ 
        условие if 
        """
        condition = removeprefix(line, "если ").rstrip(":")
        return f"if {condition}:"

    elif re.fullmatch("иначе если .+:", structure_finder):
        """ 
        условие elif 
        """
        condition = removeprefix(line, "иначе если ").rstrip(":")
        return f"elif {condition}:"

    elif re.fullmatch("иначе:", structure_finder):
        """ 
        условие else 
        """
        return "else:"
    else:
        return line
