import yaml, pdb, traceback, time, pause, datetime, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fit4less import Fit4LessBot
from validate_email import validate_email

def init_browser(headless):
    browser_options = Options()
    options = ['--disable-blink-features', '--no-sandbox', '--start-maximized', '--disable-extensions',
               '--ignore-certificate-errors', '--disable-blink-features=AutomationControlled']
    if headless:
        options.append(headless)

    for option in options:
        browser_options.add_argument(option)

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=browser_options)

    driver.set_window_position(0, 0)
    driver.maximize_window()

    return driver


def validate_yaml():
    with open("config.yaml", 'r') as stream:
        try:
            parameters = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc

    mandatory_params = ['email', 'password', 'bookingDay', 'bookingTimes', 'club', 'headless']

    for mandatory_param in mandatory_params:
        if mandatory_param not in parameters:
            raise Exception(mandatory_param + ' is not inside the yml file!')

    assert validate_email(parameters['email'])
    assert 0 <= parameters['bookingDay'] <= 3
    assert len(parameters['password']) > 0

    times = parameters['bookingTimes']

    for time_slot in times:
        'AM' in time_slot or 'PM' in time_slot or 'None' in time_slot

    assert isinstance(parameters['headless'], bool)

    return parameters


if __name__ == '__main__':
    parameters = validate_yaml()
    browser = None
    bot = Fit4LessBot(parameters)

    while True:
        try:

            if bot.not_booking():
                print("Skipping booking for today since the date is set to None.")
                break
            hour = int(bot.booking_time.split(' ')[0].split(':')[0])
            if 'PM' in bot.booking_time:
                hour += 12
            minute = int(bot.booking_time.split(' ')[0].split(':')[1])

            date = (datetime.datetime.now().replace(hour=hour, minute=minute, second=0) - datetime.timedelta(minutes=2))
            pause.until(date)

            browser = init_browser(parameters['headless'])
            bot.add_browser(browser)

            bot.login()

            bot.check_for_500_error()

            if bot.is_fully_booked():
                print("We are fully booked! Nothing to do today.")
                break

            bot.go_to_club()
            bot.check_for_500_error()

            while not bot.go_to_day():
                bot.check_for_500_error()

            date = (datetime.datetime.now().replace(hour=hour, minute=minute, second=0))
            pause.until(date)

            while not bot.book_slot():
                bot.check_for_500_error()
                time.sleep(random.uniform(0.8, 1.8))


            break
        except:
            traceback.print_exc()
            browser.close()
            print("There was an error! Restarting the bot.")
    if browser is not None:
        browser.close()





