import base64
import json
import platform
import queue
import shutil
import os
import re
import time
import traceback as tr
from io import BytesIO
from multiprocessing import Process, Queue
TIMEOUT_RUN_GADUKA = 10

from . import compiler
from PIL import Image


def run_from_api(code, images_json):
    # Возвращает текст, и изображения в формате json
    imgs = []
    for json_data in images_json:
        if json_data:
            imgs.append(Image.open(BytesIO(base64.b64decode(json_data))))

    return_queue = Queue()
    procc = Process(target=compile_and_run_and_get_result,
                    args=(code, imgs, return_queue))
    procc.start()
    start = time.time()
    while time.time() - start <= TIMEOUT_RUN_GADUKA:
        try:
            ms = return_queue.get(timeout=0.1)
            if ms:
                break
        except queue.Empty as e:
            pass

        time.sleep(.1)
    else:
        procc.kill()
        procc.join()
        return_queue.close()

        return "Ошибка! Похоже ваш код выполняется очень долго.\nВозможно проблема в цикле 'повтор пока'. \n Также такое может произойти при большом количестве изображений.", []

    result_imgs, result_text, compiled_code = ms
    for i in result_imgs:
        i.__class__ = Image.Image

    procc.join()
    return_queue.close()

    imgs_json = []
    for img in result_imgs:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        a = base64.b64encode(buffered.getvalue()).decode("utf-8")
        imgs_json.append(json.dumps(a))
    return result_text, imgs_json


def mem_limit_only_for_linux(coef):
    import resource
    def memory_limit():
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        resource.setrlimit(resource.RLIMIT_AS, (get_memory() * 1024 * coef, hard))

    def get_memory():
        with open('/proc/meminfo', 'r') as mem:
            free_memory = 0
            for i in mem:
                sline = i.split()
                if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
                    free_memory += int(sline[1])
        return free_memory

    memory_limit()


def compile_and_run_and_get_result(code, imgs, process_connect):
    if platform.system() == "Linux":
        mem_limit_only_for_linux(0.7)

    pilimage = Image.Image
    Image.Image = compiler.GadukaImage

    compiled_code, match_not_compile, result_imgs, result_text = "", {}, [], []

    try:
        compiled_code, match_not_compile = compiler.compile_code(code=code)

        print(compiled_code)
        # print("\n".join(compiled_code))
        result_imgs, result_text = [], []
        exec("\n".join(compiled_code), {"итоговые_изображения": result_imgs, "итоговый_текст": result_text,
                                        "изображения": imgs},
             compiler.get_exec_funcs())
        result_text = "\n".join(result_text)
        a = []
        for i in result_imgs:
            i.__class__ = pilimage
            a.append(i.copy())
        result_imgs = a
        process_connect.put((result_imgs, result_text, compiled_code))
        return result_imgs, result_text, compiled_code
    except Exception as e:
        a = ([], process_exception(e, compiled_code, match_not_compile, code), compiled_code)
        process_connect.put(a)
        return a


def run_from_console(code, images=()):
    if os.path.exists("gaduka_engine/result_files"):
        shutil.rmtree("gaduka_engine/result_files")
    os.makedirs("gaduka_engine/result_files")

    return_queue = Queue()
    imgs = []
    for img_name in images:
        img_opened = Image.open(img_name)
        img_opened.load()
        imgs.append(img_opened)

    procc = Process(target=compile_and_run_and_get_result,
                    args=(code, imgs, return_queue))
    procc.start()
    start = time.time()
    while time.time() - start <= TIMEOUT_RUN_GADUKA:
        try:
            ms = return_queue.get(timeout=0.1)
            if ms:
                break
        except queue.Empty as e:
            pass

        time.sleep(.1)
    else:
        procc.kill()
        procc.join()
        return_queue.close()

        print("\nОшибка! Похоже ваш код выполняется очень долго.\nВозможно проблема в цикле 'повтор пока'. \n Также такое может произойти при большом количестве изображений.")
        return
    result_imgs, result_text, compiled_code = ms
    for i in result_imgs:
        i.__class__ = Image.Image

    procc.join()
    return_queue.close()

    for num, img in enumerate(result_imgs):
        img.save(f'gaduka_engine/result_files/result_img_{num}.png')

    print("----Гадюка код----")
    print("\n".join(code))
    print("\n" * 2)

    print("----Питон код----")
    print("\n".join(compiled_code))
    print("\n" * 2)

    print("----Результат----")
    print(result_text)
    print("------------------")

    print("Итоговые изображения сохранены в папку result_files")
    if result_imgs:
        print(result_imgs)


def process_exception(e, compiled_code=None, match_compile=None, code=()):
    #raise e
    print(tr.format_exc())
    def get_line(lineno=None, text=None):
        try:
            if text:
                try:
                    l_num = match_compile[text.lstrip()]
                except KeyError:
                    if not lineno:
                        l_num = match_compile[text]
            else:
                try:
                    if not lineno:
                        l_num = match_compile[compiled_code[error.lineno - 1].lstrip()]
                    else:
                        l_num = match_compile[compiled_code[int(lineno) - 1].lstrip()]
                except KeyError:
                    if not lineno:
                        l_num = match_compile[compiled_code[error.lineno - 1]]
                    else:
                        l_num = match_compile[compiled_code[int(lineno) - 1]]
        except Exception:
            return "Неизвестно", "???"
        line = code[l_num]
        return l_num + 1, line

    # Красивая обработка всех ошибок

    err = tr.TracebackException(exc_type=type(e), exc_traceback=e.__traceback__, exc_value=e)
    error = err.stack[-1]

    if isinstance(e, compiler.GadukaException):
        return e.__str__()

    if isinstance(e, NameError):
        a = re.search(r"'.*?'", str(e))[0]
        l_num, line = get_line()
        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nПеременной с именем {a} не существует'

    elif isinstance(e, AttributeError):
        a = re.findall(r"'.*?'", str(e))
        l_num, line = get_line()
        if a:
            a = a[0].strip("'")
            t = compiler.TYPES.get(a, f"объект класса {a}")
            return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
                   f'\nУ переменной типа {t} нет атрибута {a[1]}'
        else:
            return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
                   f'\nАттрибута {e} не существует.'
    elif isinstance(e, TypeError):
        l_num, line = get_line()

        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nНеподходящий тип объекта для этой операции.'
    elif isinstance(e, ValueError):
        l_num, line = get_line()
        if str(e) == "bad transparency mask":
            return "Произошла ошибка при наложении изображений.\n Возможно, то изображение, которое вы хотите наложить меньше изображения, на которое вы хотите его наложить."
        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nАргумент имеет недопустимое значение: {e}'
    elif isinstance(e, IndexError):
        l_num, line = get_line()
        if l_num == "Неизвестно":
            return f'Ошибка! \nПохоже вы прикрепили недостаточно изображений для запуска этого кода.'
        return f'Ошибка в строке номер {l_num}:\n  {line.lstrip()} ' \
               f'\nВ списке нет элемента с таким индексом.'
    elif isinstance(e, MemoryError):
        return 'Ошибка! Оперативная память переполнена.\n' \
               'Возможно в вашем коде хранится слишком много изображений.'
    elif isinstance(e, OSError) or isinstance(e, SystemError) or isinstance(e, RuntimeError):
        return f'Произошла непредвиденная системная ошибка: \n{e}'

    elif isinstance(e, SyntaxError) or isinstance(e, EOFError):
        l_num, line = get_line(text=err.text.rstrip('\n'))
        msg = err.msg
        if msg == "unexpected indent" or msg == "expected an indented block":
            msg = 'неправильный отступ'
        return f'Ошибка в строке номер {l_num}:\n  {line} ' \
               f'\nВ этой строке допущена синтаксическая ошибка.' + (f'\nПодробнее: {msg}' if msg != "invalid syntax" else "")
    elif isinstance(e, ArithmeticError):
        l_num, line = get_line()

        return f'Ошибка в строке номер {l_num}:\n{line} ' \
               f'\nОшибка в математических операциях'
    else:
        return f'Произошла непредвиденная ошибка: \n{e}'
