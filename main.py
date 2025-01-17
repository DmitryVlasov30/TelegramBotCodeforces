from telebot import TeleBot
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.by import By

from datetime import datetime
from threading import Timer
import sqlite3




token = "TOKEN"
bot = TeleBot(token=token)
last = now = []
codeforces_groups = []
flag = True
flag_work = True
del_group = []
chat_id = 'YOUR CHAT ID'
login = 'YOUR LOGIN, YOU MUST SPECIFY THE HANDLE, NOT EMAIL'
password = 'YOUR PASSWORD'
interval_requests = 'YOUR INTERVAL REQUESTS (seconds, int)'
global_flag_stop = ''


try:
    def admin_func(func):
        def wrapper(message):
            global chat_id
            if str(message.chat.id) != chat_id:
                message.answer('Отправлять сообщения может владелец')
                return
            function = func(message)
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
                return

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

    @bot.message_handler(commands=["start"])
    def start(message):
        message.answer(
            "Здравствуйте.\n"
            "Текст с объяснением работы бота находится на GitHub -> https://github.com/DmitryVlasov30/TelegramBotParser"
        )
        start_timer(message)


    def name_changes(message):
        global flag, codeforces_groups, flag_work, del_group, chat_id
        try:
            if len(codeforces_groups) == 0 or not flag_work:
                return

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
                bot.send_message(
                    chat_id, f'Эти группы удалены:\n{inf_del_groups}\nпотому что их не существует'
                )
                return

            if not isinstance(changes_loc, list) and flag:
                flag = False
                bot.send_message(chat_id, "Что то пошло не так, информацию не удалось получить :(")
                return

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

                bot.send_message(chat_id, message_inf, parse_mode='html')
        except Exception as ex:
            bot.send_message(chat_id, f"Произошла ошибка {ex}")
        finally:
            start_timer(bot)


    @bot.message_handler(commands=["del"])
    @admin_func
    def delete_group(message):
        global codeforces_groups

        group = message.text[7:].strip()

        index_group = -1
        for i in range(len(codeforces_groups)):
            if group == codeforces_groups[i]:
                index_group = i

        if index_group == -1:
            bot.send_message(message.chat.id, f'Группа {group} не найдена')
            return

        bot.send_message(message.chat.id, f'Группа {codeforces_groups[index_group]} удалена')
        del codeforces_groups[index_group]


    @bot.message_handler(commands=["add"])
    @admin_func
    def update_groups(message):
        global codeforces_groups

        group = message.text[5:].strip()
        if group == '':
            bot.send_message(message.chat.id, 'Нельзя добавить пустую группу')
            return

        codeforces_groups.append(group)
        bot.send_message(message.chat.id, 'Группа добавлена')


    @bot.message_handler(comands=["groups"])
    @admin_func
    def my_groups(message):
        global codeforces_groups
        inf_group = ''
        for el in codeforces_groups:
            inf_group += f'<b>{el}</b>' + '\n'
        bot.send_message(message.chat.id, f"Ваши группы:\n{inf_group}", parse_mode='html')


    @bot.message_handler(commands=["off"])
    @admin_func
    def off_bot(message):
        global flag_work
        flag_work = False
        message.answer('Работа бота приостановлена')


    @bot.message_handler(commands=["on"])
    @admin_func
    def on_bot(message):
        global flag_work
        flag_work = True
        bot.send_message(message.chat.id, "Бот работает")


    @bot.message_handler(commands=["status"])
    @admin_func
    def status_bot(message):
        global flag_work
        if flag_work:
            bot.send_message(message.chat.id, "Бот работает")
        else:
            bot.send_message(message.chat.id, "Бот приостановлен")


    def start_timer(message):
        global interval_requests
        Timer(int(interval_requests), name_changes, args=(message,)),start()


    @bot.message_handler(commands=["stop"])
    def stop_bot(message):
        bot.send_message("работа бота завершена")
        bot.stop_bot()



except Exception as all_mistake:
    bot.send_message(chat_id, f"Произошла ошибка: {all_mistake}")


print('bot worked')
bot.infinity_polling(timeout=10, long_polling_timeout=150)