import psycopg2
import config
from datetime import datetime
import datetime as dt



def get_amount_now(tg_id):
    # print(type(date_end))
    '''

    :param user_id:
    :param date_start:
    :param date_end:
    :return:
    '''
    now = datetime.now().date()
    connection = psycopg2.connect(host=config.db_server, port=config.db_port, database=config.db_database,
                                  user=config.db_log, password=config.db_pass)
    cursor = connection.cursor()
    result = []
    # Prepare the arguments string for the SQL query
    try:

        # Execute the SQL query to insert data into the database
        cursor.execute(f"""
            SELECT bank, amount, startdate, enddate, annualrate, compoundinterest
            FROM home.Deposits
            WHERE user_id = {tg_id} AND StartDate <= '{now}' AND (EndDate >= '{now}' OR EndDate IS NULL);
            """)
        rows_ = cursor.fetchall()
        response = ''
        sum_start_period = 0
        sum_end_period = 0
        profit = 0

        if rows_:
            for row_ in rows_:
                # print(row_)
                if now >= row_[2]:
                    sum_start_period_temp, sum_end_period_temp, profit_temp = calculate_compound_interest(row_[1],
                                                                                                          row_[2],
                                                                                                          row_[3],
                                                                                                          row_[4],
                                                                                                          now,
                                                                                                          now,
                                                                                                          row_[5])
                    sum_start_period = sum_start_period + sum_start_period_temp
                    sum_end_period = sum_end_period + sum_end_period_temp
                    profit = profit + profit_temp

            result_ = f'{sum_start_period:,.2f}₽'

            return result_

        else:
            result_ = "Данные не найдены"

        return result_

    except Exception as e:
        result_ = e

    cursor.close()
    connection.close()

    return result_


def get_amount(tg_id):
    connection = psycopg2.connect(host=config.db_server, port=config.db_port, database=config.db_database,
                                  user=config.db_log, password=config.db_pass)
    cursor = connection.cursor()
    now = datetime.now().date()
    print(now)
    # Prepare the arguments string for the SQL query
    try:

        # Execute the SQL query to insert data into the database
        cursor.execute(f"""
        SELECT SUM(amount), COUNT(depositid)
        FROM home.Deposits
        WHERE user_id = {tg_id} AND StartDate <= '{now}' AND (EndDate >= '{now}' OR EndDate IS NULL);
        """)
        rows_ = cursor.fetchall()
        # result_ = []
        result_ = ''
        response = ''
        if rows_:
            response = [rows_[0][1], get_amount_now(tg_id)]

        else:
            response = ['Данные не найдены']

        return response
    except Exception as e:
        result = [e]

    cursor.close()
    connection.close()

    return result


def add_deposit(bank_, amount_, startdate_, enddate_, annualrate_, compoundinterest_, user_id_, type_):
    connection = psycopg2.connect(host=config.db_server, port=config.db_port, database=config.db_database,
                                  user=config.db_log, password=config.db_pass)
    cursor = connection.cursor()
    if type_ == 'Накопительный счет':
        enddate_ = 'NULL'
    # Prepare the arguments string for the SQL query
    try:

        # Execute the SQL query to insert data into the database
        cursor.execute(f"""
        INSERT INTO home.Deposits (Bank, user_id, Amount, StartDate, EndDate, AnnualRate, CompoundInterest)
        VALUES
        ('{bank_}', {user_id_}, {amount_}, '{startdate_}', '{enddate_}', {annualrate_}, {compoundinterest_});
        """)
        connection.commit()
        result = f'{type_} успешно добавлен'
    except Exception as e:
        result = e

    cursor.close()
    connection.close()

    return result


def get_deposits(tg_id):
    connection = psycopg2.connect(host=config.db_server, port=config.db_port, database=config.db_database,
                                  user=config.db_log, password=config.db_pass)
    cursor = connection.cursor()

    # Prepare the arguments string for the SQL query
    try:

        # Execute the SQL query to insert data into the database
        cursor.execute(f"""
        SELECT bank, amount, startdate, enddate, annualrate, compoundinterest
        FROM home.Deposits
        WHERE user_id = {tg_id};
        """)
        rows_ = cursor.fetchall()
        # result_ = []
        result_ = ''
        response = ''
        if rows_:
            for row_ in rows_:
                # row_as_dict_ = dict(row_)  # Преобразование объекта sqlite3.Row в словарь

                bank, amount, start_date, end_date, rate, compound = row_
                bank = f"Банк: {bank}"
                amount = f"Сумма вклада: {amount:,.2f} руб."  # Форматирование суммы с разделителями тысяч и двумя знаками после запятой
                start_date = f"Дата начала вклада: {datetime.strftime(start_date, '%d.%m.%Y')}"
                end_date = f"Дата окончания вклада: {datetime.strftime(end_date, '%d.%m.%Y')}"
                rate = f"Годовая процентная ставка: {rate:.2%}"  # Преобразование в проценты и форматирование
                compound = f"Использование сложного процента: {'Да' if compound else 'Нет'}"
                tire = "-------------"  # Разделитель для читаемости при выводе нескольких вкладов
                list_response = [bank, amount, start_date, end_date, rate, compound, tire]
                response = '\n'.join(list_response)
                result_ = result_ + '\n' + response
                # print(f"Банк: {bank}")
                # print(f"Сумма вклада: {amount:,.2f} руб.")  # Форматирование суммы с разделителями тысяч и двумя знаками после запятой
                # print(f"Дата начала вклада: {datetime.strftime(start_date, '%d.%m.%Y')}")
                # print(f"Дата окончания вклада: {datetime.strftime(end_date, '%d.%m.%Y')}")
                # print(f"Годовая процентная ставка: {rate:.2%}")  # Преобразование в проценты и форматирование
                # print(f"Использование сложного процента: {'Да' if compound else 'Нет'}")
                # print("-" * 30)  # Разделитель для читаемости при выводе нескольких вкладов
                # print(result_)
            return result_
        else:
            result_ = "Данные не найдены"

        return result_
    except Exception as e:
        result = e

    cursor.close()
    connection.close()

    return result


def get_profit(user_id, date_start, date_end, details):
    # print(type(date_end))
    '''

    :param user_id:
    :param date_start:
    :param date_end:
    :return:
    '''
    date_start = datetime.strptime(date_start, '%d.%m.%Y').date()
    date_end = datetime.strptime(date_end, '%d.%m.%Y').date()


    connection = psycopg2.connect(host=config.db_server, port=config.db_port, database=config.db_database,
                                  user=config.db_log, password=config.db_pass)
    cursor = connection.cursor()
    result = []
    # Prepare the arguments string for the SQL query
    try:

        # Execute the SQL query to insert data into the database
        cursor.execute(f"""
        SELECT bank, amount, startdate, enddate, annualrate, compoundinterest
        FROM home.Deposits
        WHERE user_id = {user_id};
        """)
        rows_ = cursor.fetchall()
        response = ''
        sum_start_period = 0
        sum_end_period = 0
        profit = 0

        if rows_:
            for row_ in rows_:
                # print(row_)
                if date_end > row_[2]:
                    sum_start_period_temp, sum_end_period_temp, profit_temp = calculate_compound_interest(row_[1],
                                                                                                          row_[2],
                                                                                                          row_[3],
                                                                                                          row_[4],
                                                                                                          date_start,
                                                                                                          date_end,
                                                                                                          row_[5])
                    sum_start_period = sum_start_period + sum_start_period_temp
                    sum_end_period = sum_end_period + sum_end_period_temp
                    profit = profit + profit_temp
                    if details:
                        bank, amount, start_date, end_date, rate, compound = row_
                        bank = f"Банк: {bank}"
                        amount = f"Сумма вклада: {amount:,.2f} руб."  # Форматирование суммы с разделителями тысяч и двумя знаками после запятой
                        start_date_temp = f"Дата начала вклада: {datetime.strftime(start_date, '%d.%m.%Y')}"
                        end_date_temp = f"Дата окончания вклада: {datetime.strftime(end_date, '%d.%m.%Y')}"
                        rate = f"Годовая процентная ставка: {rate:.2%}"  # Преобразование в проценты и форматирование
                        compound = f"Использование сложного процента: {'Да' if compound else 'Нет'}"
                        sum_start_period_temp = f"Сумма на начало периода: {sum_start_period_temp:,.2f} ₽"
                        sum_end_period_temp = f"Сумма на конец периода: {sum_end_period_temp:,.2f} ₽"
                        profit_temp = f"Доход за период: {profit_temp:,.2f} ₽"
                        tire = "-------------"  # Разделитель для читаемости при выводе нескольких вкладов
                        if end_date < date_end:
                            warning_status = 'ВНИМАНИЕ! Вклад истекает в указанном периоде'
                            list_response = [bank, amount, start_date_temp, end_date_temp, rate, compound,
                                             sum_start_period_temp, sum_end_period_temp, profit_temp, warning_status, tire]
                        else:
                            list_response = [bank, amount, start_date_temp, end_date_temp, rate, compound,
                                             sum_start_period_temp, sum_end_period_temp, profit_temp, tire]

                        response = '\n'.join(list_response)
                        result.append(response)

            result_ = f'''Сумма на начало периода: {sum_start_period:,.2f} ₽
Сумма на конец периода: {sum_end_period:,.2f} ₽
Доход за период: {profit:,.2f} ₽'''
            result = '\n'.join(result)
            result = result + '\n\n' + result_
            return result
        else:
            result_ = "Данные не найдены"

        return result_

    except Exception as e:
        result_ = e

    cursor.close()
    connection.close()

    return result_


def calculate_compound_interest(initial_amount, start_date, end_date, annual_rate, control_start_date,
                                control_end_date, capitalisation):
    # Переводим процентную ставку из процентов в десятичную форму
    # annual_rate

    # Расчёт количества месяцев от начала вклада до начала и конца контрольного периода
    if capitalisation:
        if control_start_date >= start_date:
            months_start = (control_start_date.year - start_date.year) * 12 + (control_start_date.month - start_date.month)
            # print(months_start)
            amount_at_control_start = round(initial_amount * pow((1 + annual_rate / 12), months_start), 2)
        elif control_start_date < start_date:
            months_start = 0
            amount_at_control_start = 0
            # print(months_start)
        if control_end_date <= end_date:
            months_end = (control_end_date.year - start_date.year) * 12 + (control_end_date.month - start_date.month)
            amount_at_control_end = round(initial_amount * pow((1 + annual_rate / 12), months_end), 2)
            # print(months_end)
        elif control_end_date > end_date:
            months_end = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            amount_at_control_end = round(initial_amount * pow((1 + annual_rate / 12), months_end), 2)
            # print(months_end)

        if amount_at_control_start > 0:
            interest_earned = round(amount_at_control_end - amount_at_control_start, 2)
        else:
            interest_earned = round(amount_at_control_end - initial_amount, 2)

        return amount_at_control_start, amount_at_control_end, interest_earned

    else:

        if control_start_date >= start_date:
            months_start = (control_start_date.year - start_date.year) * 12 + (
                        control_start_date.month - start_date.month)
            # print(months_start)
            amount_at_control_start = round(initial_amount + initial_amount * (annual_rate / 12) * months_start, 2)
        elif control_start_date < start_date:
            months_start = 0
            amount_at_control_start = 0
            # print(months_start)
        if control_end_date <= end_date:
            months_end = (control_end_date.year - start_date.year) * 12 + (control_end_date.month - start_date.month)
            amount_at_control_end = round(initial_amount + initial_amount * (annual_rate / 12) * months_end, 2)
            # print(months_end)
        elif control_end_date > end_date:
            months_end = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
            amount_at_control_end = round(initial_amount + initial_amount * (annual_rate / 12) * months_end, 2)
            # print(months_end)

        if amount_at_control_start > 0:
            interest_earned = round(amount_at_control_end - amount_at_control_start, 2)
        else:
            interest_earned = round(amount_at_control_end - initial_amount, 2)

        return amount_at_control_start, amount_at_control_end, interest_earned

if __name__ == '__main__':
    bank = 'ТестБанк1'
    amount = 10000.0
    startdate = '2024-06-23'
    enddate = '2025-01-23'
    annualrate = 0.20
    compoundinterest = 'False'
    user_id = 260399228
    type_ = 'Вклад'
    #
    # print(get_deposits(user_id))
    print(get_profit(user_id, '01.03.2024', '01.07.2024', True))
    # print(get_amount(260399228))
    # Пример данных входа
    # initial_amount = 1000000  # руб.
    # start_date = datetime(2024, 1, 1)
    # end_date = datetime(2025, 1, 1)
    # annual_rate = 0.12  # процентов годовых
    # control_start_date = datetime(2023, 3, 1)
    # control_end_date = datetime(2025, 7, 1)

    # Вызов функции
    # result = calculate_compound_interest(initial_amount, start_date, end_date, annual_rate, control_start_date,
    #                                      control_end_date, False)
    # print("Сумма на начало периода:", result[0])
    # print("Сумма на конец периода:", result[1])
    # print("Начисленные проценты за период:", result[2])
    # print(add_deposit(bank, amount, startdate, enddate, annualrate, compoundinterest, user_id, type_))
