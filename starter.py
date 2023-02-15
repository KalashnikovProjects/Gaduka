import os
import re

import compiler
import traceback as tr

TYPES = {"list": "список", "str": "строка", "int": "число", "bool": "логический",
         "dict": "список", "tuple": "неизменяемый список", "set": "множество",
         "function": "функция", "float": "число"}


def run_from_site(code, images, output):
    ...


def run_from_discord_bot(code, images, output):
    ...


def run_from_console(code, images=()):
    if not os.path.exists("result_files"):
        os.makedirs("result_files")

    pre_code_lines = [f"image_paths = {images}",
                      "изображения = []",
                      "for img_name in image_paths:",
                      "    img_opened = Image.open(img_name)",
                      "    img_opened.load()",
                      "    изображения.append(img_opened)", ""]
    post_code_lines = ["for num, img_opened in enumerate(итоговые_изображения):",
                       "   img_opened.save(f'result_files/result_img_{num}.png')"]

    compiled_code = None
    try:
        compiled_code = compiler.compile_code(code=code, logs=True,
                                              pre_code_py_commands=pre_code_lines,
                                              post_code_py_commands=post_code_lines)
        print("----Гадюка код----")
        print("\n".join(code))
        print("\n" * 2)

        print("----Питон код----")
        print("\n".join(compiled_code))
        print("\n" * 2)

        print("----Результат----")
        exec("\n".join(compiled_code))
    # Красиво обрабатываем все исключения
    except Exception as e:
        print(process_exception(e, compiled_code))


def process_exception(e, compiled_code=None):
    # Красивая обработка всех ошибок

    error = tr.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e).stack[-1]

    if isinstance(e, compiler.GadukaException):
        return e

    elif isinstance(e, NameError):
        a = re.search(r"'.*?'", str(e))[0]
        return f'Ошибка в строке номер {error.lineno}:\n{compiled_code[error.lineno - 1].lstrip()} ' \
               f'\nПеременной с именем {a} не сущесивует'

    elif isinstance(e, AttributeError):
        a = re.findall(r"'.*?'", str(e))

        t = TYPES.get(a[0].strip("'"), "объект")
        return f'Ошибка в строке номер {error.lineno}:\n{compiled_code[error.lineno - 1].lstrip()} ' \
               f'\nУ переменной типа {t} нет атрибута {a[1]}'
    elif isinstance(e, TypeError):
        return f'Ошибка в строке номер {error.lineno}:\n{compiled_code[error.lineno - 1].lstrip()} ' \
               f'\nНеподходящий тип объекта для этой операции.'
    elif isinstance(e, ValueError):
        return f'Ошибка в строке номер {error.lineno}:\n{compiled_code[error.lineno - 1].lstrip()} ' \
               f'\nАргумент иммет недопустимое значение: {e}'
    elif isinstance(e, IndexError):
        return f'Ошибка в строке номер {error.lineno}:\n{compiled_code[error.lineno - 1].lstrip()} ' \
               f'\nВ списке нет элемента с таким индексом.'
    elif isinstance(e, MemoryError):
        return 'Ошибка! Оперативная память переполнена.\n' \
               'Возможно в вашем коде хранится слишком много изображений.'
    elif isinstance(e, OSError) or isinstance(e, SystemError) or isinstance(e, RuntimeError):
        return f'Произошла непредвиденная системная ошибка: \n{e}'
    elif isinstance(e, SyntaxError) or isinstance(e, EOFError):
        return f'Ошибка в строке номер {error.lineno}:\n{compiled_code[error.lineno - 1].lstrip()} ' \
               f'\nВ этой строке допущена синтаксическая ошибка.'
    elif isinstance(e, ArithmeticError):
        return f'Ошибка в строке номер {error.lineno}:\n{compiled_code[error.lineno - 1].lstrip()} ' \
               f'\nОшибка в математических операциях'
    else:
        return f'Произошла непредвиденная ошибка: \n{e}'
