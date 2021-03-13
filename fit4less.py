import time, random, csv, pyautogui, pdb, traceback, sys, datetime
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys


class Fit4LessBot:
    def __init__(self, parameters):
        self.email = parameters['email']
        self.password = parameters['password']
        self.booking_day = parameters['bookingDay']
        self.use_club_name = parameters['club']['useClubName']
        self.club_name = parameters['club']['clubName'].lower()
        date = datetime.datetime.now() + datetime.timedelta(days=self.booking_day)
        self.date = date.strftime('%A') + ', ' + str(date.day) + ' ' + date.strftime('%B') + ' ' + str(date.year)
        self.date_string = 'date_' + str(date.year) + '-' + '{:02d}'.format(date.month) + '-' + '{:02d}'.format(date.day)
        self.booking_time = parameters['bookingTimes'][date.strftime('%A')].strip()


    def not_booking(self):
        return 'None' in self.booking_time

    def login(self):
        try:
            self.browser.get("https://myfit4less.gymmanager.com/portal/login.asp");

            try:
                seconds_to_wait = 120
                current_time = datetime.datetime.now()
                stop_time = current_time + datetime.timedelta(seconds=seconds_to_wait)

                # Wait until it is booked, run for 40 seconds
                while current_time < stop_time:
                    self.check_for_500_error()
                    try:
                        self.browser.find_element_by_id("emailaddress").send_keys(self.email)
                        self.browser.find_element_by_id("password").send_keys(self.password)
                        self.browser.find_element_by_id("password").send_keys(Keys.ENTER)
                        return
                    except:
                        pass
                    current_time = datetime.datetime.now()

                raise Exception("Waiting for login failed")
            except TimeoutException:
                raise Exception("Could not login!")
        except TimeoutException:
            raise Exception("Could not login!")

    def book_slot(self):
        try:
            self.refresh()

            if "not possible to book for this day" in self.browser.page_source:
                self.refresh()

            if "maximum personal reservations reached" in self.browser.page_source.lower():
                return True
            elif "maximum amount of reservations allowed per day has been reached" in self.browser.page_source.lower():
                return True

            self.check_for_500_error()

            open_slots = self.browser.find_elements_by_xpath('(/html/body/div[5]/div/div/div/div/form/div[@class=\'available-slots\'])[2]/div')
            open_slots = {slot_info.get_attribute('data-slottime').strip()[3:]:(slot_info.get_attribute('id')[5:],slot_info.get_attribute('data-slotclub'),slot_info.get_attribute('data-slotdate'),slot_info.get_attribute('data-slottime')) for slot_info in open_slots}

            if self.booking_time in open_slots:
                slot_info = open_slots[self.booking_time]
                block_name = slot_info[1] + ", " + slot_info[2] + ", " + slot_info[3]
                book_script = "$(\"#action\").val(\"booking\"); " + \
                              "$(\"#block_id\").val(\"" + slot_info[0] + "\"); " + \
                              "$(\"#block_name\").val(\"" + block_name + "\"); " + \
                              "$(\"#doorPolicyForm\").submit();"
                self.browser.execute_script(book_script)

                try:
                    seconds_to_wait = 300
                    done = False
                    current_time = datetime.datetime.now()
                    stop_time = current_time + datetime.timedelta(seconds=seconds_to_wait)

                    # Wait until it is booked, run for 300 seconds
                    while current_time < stop_time and not done:
                        if '500' in self.browser.title:
                            self.refresh()
                            self.browser.execute_script(book_script)
                        elif "maximum personal reservations reached" in self.browser.page_source.lower():
                            return True
                        elif "maximum amount of reservations allowed per day has been reached." in self.browser.page_source.lower():
                            return True
                        elif self.timeslot_booked(block_name):
                            print("We are done booking!!")
                            return True
                        else:
                            print("We are not done booking yet!!")
                        current_time = datetime.datetime.now()
                except:
                    pass

            return False
        except:
            traceback.print_exc()
            print("Failed to book the times!")
            return False
            pass


    def go_to_day(self):
        try:
            script = "processClubDate(\"" + self.date_string + "\")"

            self.browser.execute_script(script)

            day_info = None
            seconds_to_wait = 30
            done = False
            current_time = datetime.datetime.now()
            stop_time = current_time + datetime.timedelta(seconds=seconds_to_wait)

            # Wait until it is booked, run for 30 seconds
            while current_time < stop_time and not done:
                self.check_for_500_error()
                try:
                    day_info = self.browser.find_element_by_xpath('//form[@id=\'doorPolicyForm\']/h2').text
                except:
                    pass
                if self.date in day_info or "not possible to book for this day" in self.browser.page_source:
                    print("We are done choosing the day!!")
                    done = True
                else:
                    print("We didn't choose the day yet!!!")
                current_time = datetime.datetime.now()
            if not done:
                self.refresh()
            return done
        except:
            self.refresh()
            return False
            pass


    def go_to_club(self):
        if not self.use_club_name:
            return

        club_list = self.browser.find_element_by_id('modal_clubs').find_elements_by_class_name('md-option')
        club_list = {club_info.get_attribute('innerText').lower().strip():club_info.get_attribute('id') for club_info in club_list}

        if self.club_name.strip() in club_list:
            club_id = club_list[self.club_name]
            club_change_script = "$(\"#action\").val(\"clubchange\"); " + \
                                 "$(\"#block_id\").val(\"" + club_id[5:] + "\"); " + \
                                 "$(\"#block_name\").val(\"" + self.club_name + "\"); " + \
                                 "$(\"#doorPolicyForm\").submit();"
            self.browser.execute_script(club_change_script)
        else:
            print("Could not find the club " + self.club_name + "! Check the spelling")

    def scroll_down(self):
        self.browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')

    def is_fully_booked(self):
        try:
            bookings = self.browser.find_elements_by_xpath('(/html/body/div[5]/div/div/div/div/form/div[@class=\'reserved-slots\'])[1]/div')

            if len(bookings) > 1:
                return True
            else:
                return False
        except:
            print("Failed to get bookings!")
            traceback.print_exc()
            return False
            pass

    def timeslot_booked(self, booking_info):
        try:
            bookings = self.browser.find_elements_by_xpath('(/html/body/div[5]/div/div/div/div/form/div[@class=\'reserved-slots\'])[1]/div')

            for booking in bookings:
                slot_club, slot_date, slot_time, block_text = "", "", "", ""

                try:
                    slot_club = booking.get_attribute('data-slotclub')
                except:
                    pass
                try:
                    slot_date = booking.get_attribute('data-slotdate')
                except:
                    pass
                try:
                    slot_time = booking.get_attribute('data-slottime')
                except:
                    pass

                block_name = ', '.join([slot_club, slot_date, slot_time])

                if booking_info.lower().strip() in block_name.lower().strip() or slot_date.lower().strip() in booking_info.lower().strip():
                    return True

            return False
        except:
            traceback.print_exc()
            return False
            pass

    def check_for_500_error(self):
        title = self.browser.title

        if '500' in title:
            raise Exception("There was a 500 error!")

    def add_browser(self, driver):
        self.browser = driver

    def refresh(self):
        self.browser.refresh()