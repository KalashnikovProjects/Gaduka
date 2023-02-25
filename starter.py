import shutil
import os
import re

import compiler
import traceback as tr


def run_from_api(code, images, output):
    ...


def compile_and_run_and_get_result(code, pre_code, post_code):
    compiled_code, match_not_compile, result_imgs, result_text = "", {}, [], []

    try:
        compiled_code, match_not_compile = compiler.compile_code(code=code,
                                                                 pre_code_py_commands=pre_code,
                                                                 post_code_py_commands=post_code)

        result_imgs, result_text = [], []
        exec("\n".join(compiled_code), {"итоговые_изображения": result_imgs, "итоговый_текст": result_text},
             compiler.get_exec_funcs())
        result_text = "\n".join(result_text)
        return result_imgs, result_text, compiled_code
    except Exception as e:
        return result_imgs, process_exception(e, compiled_code, match_not_compile, code), compiled_code


def run_from_console(code, images=()):
    if os.path.exists("result_files"):
        shutil.rmtree("result_files")
    os.makedirs("result_files")

    pre_code_lines = [f"image_paths = {images}",
                      "изображения = []",
                      "for img_name in image_paths:",
                      "    img_opened = Image.open(img_name)",
                      "    img_opened.load()",
                      "    изображения.append(img_opened)",
                      "del img_opened, image_paths, img_name", "", ]
    post_code_lines = ["",
                       "for num, img_opened in пронумеровать(итоговые_изображения):",
                       "   img_opened.save(f'result_files/result_img_{num}.png')"]

    result_imgs, result_text, compiled_code = \
        compile_and_run_and_get_result(code, pre_code_lines, post_code_lines)

    print("----Гадюка код----")
    print("\n".join(code))
    print("\n" * 2)

    print("----Питон код----")
    print("\n".join(compiled_code))
    print("\n" * 2)

    print("----Результат----")
    print(result_text)
    if result_imgs:
        print(result_imgs)


def process_exception(e, compiled_code=None, match_compile=None, code=()):
    def get_line(lineno=None):
        if not lineno:
            l_num = match_compile[compiled_code[error.lineno - 1].lstrip()]
        else:
            l_num = match_compile[compiled_code[int(lineno) - 1].lstrip()]

        line = code[l_num]
        return l_num + 1, line

    # Красивая обработка всех ошибок

    err = tr.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e)
    error = err.stack[-1]

    if isinstance(e, compiler.GadukaException):
        return e

    if isinstance(e, NameError):
        a = re.search(r"'.*?'", str(e))[0]
        l_num, line = get_line()
        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nПеременной с именем {a} не существует'

    elif isinstance(e, AttributeError):
        a = re.findall(r"'.*?'", str(e))
        l_num, line = get_line()

        t = compiler.TYPES.get(a[0].strip("'"), "объект")
        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nУ переменной типа {t} нет атрибута {a[1]}'
    elif isinstance(e, TypeError):
        l_num, line = get_line()

        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nНеподходящий тип объекта для этой операции.'
    elif isinstance(e, ValueError):
        l_num, line = get_line()

        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nАргумент иммет недопустимое значение: {e}'
    elif isinstance(e, IndexError):
        l_num, line = get_line()

        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nВ списке нет элемента с таким индексом.'
    elif isinstance(e, MemoryError):
        return 'Ошибка! Оперативная память переполнена.\n' \
               'Возможно в вашем коде хранится слишком много изображений.'
    elif isinstance(e, OSError) or isinstance(e, SystemError) or isinstance(e, RuntimeError):
        return f'Произошла непредвиденная системная ошибка: \n{e}'

    elif isinstance(e, SyntaxError) or isinstance(e, EOFError):
        l_num, line = get_line(lineno=err.lineno)

        return f'Ошибка в строке номер {l_num}:\n  {line} ' \
               f'\nВ этой строке допущена синтаксическая ошибка.'
    elif isinstance(e, ArithmeticError):
        l_num, line = get_line()

        return f'Ошибка в строке номер {l_num}:\n{line} ' \
               f'\nОшибка в математических операциях'
    else:
        return f'Произошла непредвиденная ошибка: \n{e}'
