import pymysql
import Customer


class StaffModule:
    def __init__(self):
        self.con = pymysql.connect(host='localhost', user='root', password='123456', db='lego')
        self.cur = self.con.cursor()

    @staticmethod
    def menu_staff():
        print('What do you want to do?')
        print('1.Login')
        print('2.Exit')
        return int(input())

    @staticmethod
    def menu_staff_service():
        print('What do you want to do?')
        print('1.Restock sets')
        print('2.Restock parts')
        print('3.Sell sets')
        print('4.Sell parts')
        print('5.Query Sets')
        print('6.Query Parts')
        print('7.Low stock warning')
        print('8.Log out')
        return int(input())

    def staff_login(self):
        username = input('Enter your username:')
        password = input('Enter your password:')
        self.cur.callproc('staff_login', (username, password))
        staff = self.cur.fetchone()
        if staff is not None:
            print(f'login success! {staff[1]}')
            return staff
        else:
            print('login failed! Try again!')

    def staff_sell_sets(self, staff):
        sql = 'SELECT find_branch_by_staff_id(' + str(staff[0]) + ')'
        self.cur.execute(sql)
        id = self.cur.fetchone()
        email = input('Who is buying?')
        self.cur.callproc('find_customer_by_email', (email,))
        customer = self.cur.fetchone()
        if customer is not None:
            set_name = input('Which sets does the customer want to buy?')
            quantity = input('How many does the customer want to buy?')
            self.cur.callproc('customer_buy_sets', (id, email, quantity, set_name))
            info = self.cur.fetchone()
            print(info[0])
        else:
            print('This customer does not exists!')

    def staff_sell_parts(self, staff):
        sql = 'SELECT find_branch_by_staff_id(' + str(staff[0]) + ')'
        self.cur.execute(sql)
        id = self.cur.fetchone()
        email = input('Who is buying?')
        self.cur.callproc('find_customer_by_email', (email,))
        customer = self.cur.fetchone()
        if customer is not None:
            part_name = input('Which parts does the customer want to buy?')
            quantity = input('How many does the customer want to buy?')
            self.cur.callproc('customer_buy_parts', (id, email, quantity, part_name))
            info = self.cur.fetchone()
            print(info[0])
        else:
            print('This customer does not exists!')

    def low_stock_warning(self):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_sets_by_left')
        sets = cur.fetchall()
        Customer.CustomerModule.show_sets(sets)
        print()
        cur.callproc('find_parts_by_left')
        parts = cur.fetchall()
        Customer.CustomerModule.show_parts(parts)

    def restock_sets(self, staff):
        sql = 'SELECT get_restock_sets_id(' + str(staff[0]) + ')'
        self.cur.execute(sql)
        self.con.commit()
        ssid = self.cur.fetchone()
        while True:
            set_name = input('What is the set name?')
            quantity = int(input('How many sets do you restock this time?'))
            sql = 'SELECT find_sets_by_exact_name("' + set_name + '")'
            self.cur.execute(sql)
            sid = self.cur.fetchone()
            if sid[0] != -1:
                self.cur.callproc('get_restock_sets_details', (ssid, sid[0], 0, quantity, 0, 0, 0, 0))
                self.con.commit()
                info = self.cur.fetchone()
                print(info[0])
            else:
                release_year = input('Input release year:')
                part_num = input('Input part number:')
                price = input('Input price:')
                theme_name = input('Input theme name:')
                self.cur.callproc('get_restock_sets_details',
                             (ssid, -1, set_name, quantity, release_year, part_num, price, theme_name))
                self.con.commit()
                info = self.cur.fetchone()
                print(info[0])
            c = input('Do you want to add another restock record?(Y/N)')
            if c == 'N':
                break

    def restock_parts(self, staff):
        sql = 'SELECT get_restock_parts_id(' + str(staff[0]) + ')'
        self.cur.execute(sql)
        self.con.commit()
        ssid = self.cur.fetchone()
        while True:
            part_name = input('What is the part name?')
            quantity = int(input('How many parts do you restock this time?'))
            sql = 'SELECT find_parts_by_exact_name("' + part_name + '")'
            self.cur.execute(sql)
            pid = self.cur.fetchone()
            if pid[0] != -1:
                self.cur.callproc('get_restock_parts_details', (ssid, pid[0], 0, quantity, 0, 0, 0))
                self.con.commit()
                info = self.cur.fetchone()
                print(info[0])
            else:
                price = input('Input price:')
                category_name = input('Input category name:')
                color_name = input('Input color name:')
                self.cur.callproc('get_restock_parts_details', (ssid, -1, part_name, quantity, price, color_name, category_name))
                self.con.commit()
                info = self.cur.fetchone()
                print(info[0])
            c = input('Do you want to add another restock record?(Y/N)')
            if c == 'N':
                break

    def staff_welcome(self):
        while True:
            m1 = self.menu_staff()
            if m1 == 1:
                staff = self.staff_login()
                if staff is not None:
                    while True:
                        m2 = self.menu_staff_service()
                        if m2 == 1:
                            self.restock_sets(staff)
                        elif m2 == 2:
                            self.restock_parts(staff)
                        elif m2 == 3:
                            self.staff_sell_sets(staff)
                        elif m2 == 4:
                            self.staff_sell_parts(staff)
                        elif m2 == 5:
                            customer = Customer.CustomerModule()
                            customer.query_sets()
                        elif m2 == 6:
                            customer = Customer.CustomerModule()
                            customer.query_parts()
                        elif m2 == 7:
                            self.low_stock_warning()
                        elif m2 == 8:
                            break
            elif m1 == 2:
                break
