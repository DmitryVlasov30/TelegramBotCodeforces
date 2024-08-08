from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
# надо для сервера
# from aiogram.client.session.aiohttp import AiohttpSession
import asyncio
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime


token = "TOKEN"
last = []
now = []
codeforces_groups = []
flag = True
flag_work = True
del_group = []
chat_id = 'YOUR CHAT ID'
login = 'YOUR LOGIN, YOU MUST SPECIFY THE HANDLE, NOT EMAIL'
password = 'YOUR PASSWORD'
number_proxy_server = 'YOUR PROXY SERVER'
interval_requests = 'YOUR INTERVAL REQUESTS (seconds, int)'


try:
    def admin_func(func):
        async def wrapper(message: Message):
            global chat_id
            if str(message.chat.id) != chat_id:
                await message.answer('Отправлять сообщения может владелец')
                return None
            function = await func(message)
            return function
        return wrapper

    def changes_arr(otv):
        global last, now, login

        now = otv
        changes = []
        delete_changes = []
        delete_last = []
        if len(last) != 0 and now != last:
            for i in range(len(now)):
                flag_loc = False
                for j in range(len(last)):
                    if now[i][0] == last[j][0]:
                        flag_loc = True
                if not flag_loc:
                    changes.append(now[i])
        last = otv
        for i in range(len(changes)):
            if changes[i][3] == 'В очереди':
                delete_changes.append([i, changes[i][0]])

            elif changes[i][1] == login:
                delete_changes.append([i, -1])

        for i in range(len(last)):
            flag_delete = False
            for j in range(len(delete_changes)):
                if delete_changes[j][1] == last[i][0]:
                    flag_delete = True
            if last[i][3] == 'В очереди' and flag_delete:
                delete_last.append(i)

        for el in delete_last:
            del last[el]

        for el in delete_changes:
            del changes[el[0]]

        return changes


    def split_into_el(arr_total):

        prom_otv = []
        for j in range(len(arr_total)):
            index = -2
            string = arr_total[j][0]
            for i in range(1, len(string)):
                if string[i] == "Б" and string[i - 1] == "К":
                    s_prom = string[index + 2:i + 1]
                    index = i
                    prom_otv.append([s_prom, arr_total[j][1], arr_total[j][2]])

        otv_arr = []
        for i in range(len(prom_otv)):
            otv_arr.append([prom_otv[i][0].split(), prom_otv[i][1], prom_otv[i][2]])
        return otv_arr


    def total_information(otv_arr):
        index1 = 0
        index2 = 0
        language = ["JavaScript", "Node.js", "Rust", "Ruby", "Python", "Perl", "PascalABC.NET", "Delphi", "OCaml", "Go",
                    "Haskell", "Mono", "GNU", "PyPy", "C++14", "C++17", "C++20", "PHP", "Java", "Scala", "D", "C#"]
        otv = []
        for i in range(len(otv_arr)):

            name = otv_arr[i][0][3]
            problem = otv_arr[i][0][4]
            why_problem = ''
            when = otv_arr[i][0][2][:5]
            num_problem = otv_arr[i][0][0]
            contest_num = otv_arr[i][1]
            group_num = otv_arr[i][2]

            for j in range(len(otv_arr[i][0])):
                if otv_arr[i][0][j] == "-":
                    index1 = j
                if otv_arr[i][0][j] in language and otv_arr[i][0][j - 1] != "Mono":
                    index2 = j
                if otv_arr[i][0][j] == 'Попытка':
                    why_problem = otv_arr[i][0][j]
                if otv_arr[i][0][j] == "В":
                    why_problem = otv_arr[i][0][j] + " " + otv_arr[i][0][j+1]

                if otv_arr[i][0][j] == "Ошибка" or otv_arr[i][0][j] == "Неправильный":

                    if otv_arr[i][0][j] == "Ошибка" and otv_arr[i][0][j + 1] == "компиляции":
                        why_problem = otv_arr[i][0][j] + " " + otv_arr[i][0][j + 1]

                    else:
                        why_problem += (otv_arr[i][0][j] + " " + otv_arr[i][0][j + 1] + " " +
                                        otv_arr[i][0][j + 2] + " " + otv_arr[i][0][j + 3] + " " + otv_arr[i][0][j + 4])

                if otv_arr[i][0][j] == "Превышено":
                    why_problem = otv_arr[i][0][j] + " " + otv_arr[i][0][j + 1] + " " + otv_arr[i][0][j + 2] + " " + \
                                  otv_arr[i][0][
                        j + 3] + " " + otv_arr[i][0][j + 4] + " " + otv_arr[i][0][j + 5]

                if otv_arr[i][0][j] == "Полное":
                    why_problem = otv_arr[i][0][j] + " " + otv_arr[i][0][j + 1]

            for name_problem in range(index1, index2):
                problem += " " + otv_arr[i][0][name_problem]
            otv.append([num_problem, name, problem, why_problem, when, contest_num, group_num])

        return otv


    def web():
        global now, last, codeforces_groups, del_group, login, password

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get(url=f"https://codeforces.com/enter?back=%2Fprofile%2F{login}")
            driver.find_element("id", "handleOrEmail").send_keys(login)
            driver.find_element("id", "password").send_keys(password)
            driver.find_element(By.CLASS_NAME, "submit").click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="sidebar"]/div[1]/div[1]')
            ))
            driver.get(url="https://codeforces.com/groups/my")
            WebDriverWait(driver, 10).until(EC.url_to_be("https://codeforces.com/groups/my"))

            groups = []
            for name_group in range(len(codeforces_groups)):
                try:
                    cod_group = driver.find_element(By.LINK_TEXT, codeforces_groups[name_group]).get_attribute("href")
                    cod_group = cod_group.split("/")
                    groups.append([cod_group[-1], name_group])
                except:
                    del_group.append(codeforces_groups[name_group])
                    continue

            arr_total = []
            all_contest = []
            otv_gl = []

            if len(groups) == 0:
                return None

            for group in range(len(groups)):
                driver.get(f"https://codeforces.com/group/{groups[group][0]}/contests")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="pageContent"]/div[2]/div/a')
                ))
                contests = driver.find_elements(By.PARTIAL_LINK_TEXT, "Войти")
                contests_group_arr = []
                for i in range(2, len(contests) + 2):
                    name_contest_arr = driver.find_element(
                        By.XPATH, f'//*[@id="pageContent"]/div[3]/div[1]/div[6]/table/tbody/tr[{i}]/td[1]'
                    ).text
                    name_contest_arr = name_contest_arr.split(" ")

                    if "участие" in name_contest_arr:
                        del name_contest_arr[-1]
                        del name_contest_arr[-1]
                    del name_contest_arr[-1]

                    name_contest_arr[-1] = name_contest_arr[-1][:len(name_contest_arr[-1]) - 6]
                    name_contest = ''

                    for j in range(len(name_contest_arr)):
                        name_contest += name_contest_arr[j] + " "
                    num = str(driver.find_element(By.XPATH,
                                                  f'//*[@id="pageContent"]/div[3]/'
                                                  f'div[1]/div[6]/table/tbody/tr[{i}]/td[1]/a'
                                                  ).get_attribute(
                                                  "href")).split("/")
                    num_contest = num[-1]
                    contests_group_arr.append([name_contest, num_contest])

                    if not [num_contest, name_contest] in all_contest:
                        all_contest.append([num_contest, name_contest])

                all_inf = []
                for item in contests_group_arr:
                    driver.get(f'https://codeforces.com/group/{groups[group][0]}/contest/{item[1]}/status')
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="pageContent"]/div[7]/div/form/input[1]')))
                    all_inf.append(
                        [[
                            driver.find_element(By.XPATH, '//*[@id="pageContent"]/div[2]/div[6]').text
                        ], item[1], groups[group][0]]
                    )

                for el in range(len(all_inf)):
                    string = all_inf[el][0][0][49:]
                    if string == "Нет данных":
                        continue
                    arr_total.append([string, all_inf[el][1], all_inf[el][2]])
                otv_arr = split_into_el(arr_total)

                otv_gl.append(otv_arr)
            otv = total_information(otv_gl[-1])
            changes = changes_arr(otv)
            for i in range(len(changes)):
                for j in range(len(all_contest)):
                    if changes[i][5] == all_contest[j][0]:
                        changes[i].append(all_contest[j][1])

            for i in range(2, len(changes) + 2):
                url = \
                    (f'https://codeforces.com/group/{changes[i-2][6]}/contest/'
                     f'{changes[i-2][5]}/submission/{changes[i-2][0]}')
                changes[i - 2].append(url)

            changes = sorted(changes, key=lambda x: x[4])

            return changes
        except Exception as ex:
            return ex
        finally:
            driver.close()
            driver.quit()


    async def start(message: Message):
        await message.answer(
            "Здравствуйте.\n"
            "Текст с объяснением работы бота находится на GitHub -> https://github.com/DmitryVlasov30/TelegramBotParser"
        )


    async def name_changes(bot: Bot):
        global flag, codeforces_groups, flag_work, del_group, chat_id

        if len(codeforces_groups) == 0 or not flag_work:
            return None

        changes_loc = web()

        if len(del_group) != 0:
            inf_del_groups = ''
            del_groups_in_codeforces_group = []

            for i in range(len(del_group)):
                inf_del_groups += del_group[i] + "\n"
                for j in range(len(codeforces_groups)):
                    if del_group[i] == codeforces_groups[j]:
                        del_groups_in_codeforces_group.append(codeforces_groups[j])

            for i in range(len(del_groups_in_codeforces_group)):
                codeforces_groups.remove(del_groups_in_codeforces_group[i])

            del_group.clear()
            await bot.send_message(
                chat_id, f'Эти группы удалены:\n{inf_del_groups}\nпотому что их не существует'
            )
            return None

        if not isinstance(changes_loc, list) and flag:
            flag = False
            await bot.send_message(chat_id, "Что то пошло не так, информацию не удалось получить :(")
            return None

        if len(changes_loc) != 0:
            flag = True
            message_inf = ''
            time_format = '%H:%M'
            time1 = datetime.strptime(changes_loc[0][4], time_format)
            for i in range(len(changes_loc)):
                flag_time = False
                time_i = datetime.strptime(changes_loc[i][4], time_format)
                if abs(time1 - time_i).total_seconds() > 3600:
                    flag_time = True
                message_inf += f'{changes_loc[i][4]}' \
                               f'\nПользователь <b>{changes_loc[i][1]}</b> сдал задачу:\n' \
                               f'<u>{changes_loc[i][2]}</u>' \
                               f' из контеста <u>{changes_loc[i][7].strip()}</u>\n' \
                               f'Вердикт:\n' \
                               f'<b>{changes_loc[i][3]}</b>\n' \
                               f'ссылка -> {changes_loc[i][-1]}'
                if i != len(changes_loc) - 1 and not flag_time:
                    message_inf += '\n\n'

            await bot.send_message(chat_id, message_inf, parse_mode='html')


    @admin_func
    async def delete_group(message: Message):
        global codeforces_groups

        group = message.text[7:].strip()

        index_group = -1
        for i in range(len(codeforces_groups)):
            if group == codeforces_groups[i]:
                index_group = i

        if index_group == -1:
            await message.answer(f'Группа {group} не найдена')
            return None

        await message.answer(f'Группа {codeforces_groups[index_group]} удалена')
        del codeforces_groups[index_group]


    @admin_func
    async def update_groups(message: Message):
        global codeforces_groups

        group = message.text[5:].strip()
        if group == '':
            await message.answer('Нельзя добавить пустую группу')
            return None

        codeforces_groups.append(group)
        await message.answer('Группа добавлена')

    @admin_func
    async def my_groups(message: Message):
        global codeforces_groups
        inf_group = ''
        for el in codeforces_groups:
            inf_group += f'<b>{el}</b>' + '\n'
        await message.answer(f"Ваши группы:\n{inf_group}", parse_mode='html')


    @admin_func
    async def off_bot(message: Message):
        global flag_work
        flag_work = False
        await message.answer('Работа бота приостановлена')


    @admin_func
    async def on_bot(message: Message):
        global flag_work
        flag_work = True
        await message.answer("Бот работает")


    @admin_func
    async def status_bot(message: Message):
        global flag_work
        if flag_work:
            await message.answer("Бот работает")
        else:
            await message.answer("Бот приостановлен")


except Exception as all_mistake:
    print(all_mistake)


async def main():
    global token, number_proxy_server, interval_requests

    # session = AiohttpSession(proxy='http://proxy.server:{number_proxy_server}')
    bot = Bot(token=token)

    dp = Dispatcher()
    dp.message.register(start, Command(commands=["start"]))
    dp.message.register(my_groups, Command(commands=['my_groups']))
    dp.message.register(off_bot, Command(commands=["off"]))
    dp.message.register(on_bot, Command(commands=["on"]))
    dp.message.register(status_bot, Command(commands=['status']))
    dp.message.register(update_groups, Command(commands=['add']))
    dp.message.register(delete_group, Command(commands=['delete']))

    scheduler = AsyncIOScheduler(time_zone='Europe/Moscow')
    scheduler.add_job(name_changes, trigger='interval', seconds=60, kwargs={'bot': bot})
    scheduler.start()

    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()

print('bot worked')
asyncio.run(main())