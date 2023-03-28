import pymysql
import Admin


class CustomerModule:
    def __init__(self):
        self.con = pymysql.connect(host='localhost', user='root', password='123456', db='lego')
        self.cur = self.con.cursor()

    @staticmethod
    def menu_customer():
        print('What do you want to do?')
        print('1.Register')
        print('2.Login')
        print('3.Exit')
        return int(input())

    @staticmethod
    def menu_customer_service():
        print('What do you want to do?')
        print('1.Query Sets')
        print('2.Query Parts')
        print('3.Buy Sets')
        print('4.Buy Parts')
        print('5.Update personal info')
        print('6.Charge')
        print('7.Log out')
        print('8.Permanently Unsubscribe')
        return int(input())

    @staticmethod
    def menu_find_sets():
        print('Which filter do you want to set?')
        print('1. Search by sets name')
        print('2. Search by sets release year')
        print('3. Search by sets part number')
        print('4. Search by sets price')
        print('5. Search by sets theme')
        return int(input())

    @staticmethod
    def show_sets(sets):
        if len(sets) == 0:
            print('No sets found!')
        else:
            print('sid'.ljust(30), 'setName'.ljust(30), 'releaseYear'.ljust(30), 'partNum'.ljust(30),
                  'numLeft'.ljust(30),
                  'setPrice'.ljust(30), 'tid'.ljust(30))
            for s in sets:
                print(str(s['sid']).ljust(30), s['name'].ljust(30), str(s['releaseYear']).ljust(30),
                      str(s['partNum']).ljust(30), str(s['numLeft']).ljust(30), str(s['price']).ljust(30),
                      str(s['tid']).ljust(30))

    @staticmethod
    def menu_find_parts():
        print('Which filter do you want to set?')
        print('1. Search by parts name')
        print('2. Search by parts price')
        print('3. Search by parts color')
        print('4. Search by parts category')
        return int(input())

    @staticmethod
    def show_parts(parts):
        if len(parts) == 0:
            print('No parts found!')
        else:
            print('pid'.ljust(30), 'partName'.ljust(30), 'numLeft'.ljust(30), 'partPrice'.ljust(30),
                  'colorName'.ljust(30), 'categoryId'.ljust(30))
            for p in parts:
                print(str(p['pid']).ljust(30), p['name'].ljust(30), str(p['numLeft']).ljust(30),
                      str(p['price']).ljust(30), p['cname'].ljust(30), str(p['catId']).ljust(30))

    def customer_login(self):
        email = input('Enter your email:')
        self.cur.callproc('find_customer_by_email', (email,))
        customer = self.cur.fetchone()
        if customer is not None:
            print(f'login success! {customer[0]}')
            return customer
        else:
            print('login failed! Try again!')

    def customer_register(self):
        email = input('Enter your email:')
        name = input('Enter your name:')
        address = input('Enter your zipCode:')
        self.cur.callproc('add_customer', (email, name, 0, address))
        self.con.commit()
        info = self.cur.fetchone()
        print(info[0])

    def customer_buy_sets(self, customer):
        set_name = input('Which sets do you want to buy?')
        quantity = input('How many do you want to buy?')
        self.cur.callproc('customer_buy_sets', (5, customer[0], quantity, set_name))
        info = self.cur.fetchone()
        print(info[0])

    def customer_buy_parts(self, customer):
        part_name = input('Which parts do you want to buy?')
        quantity = input('How many do you want to buy?')
        self.cur.callproc('customer_buy_parts', (5, customer[0], quantity, part_name))
        info = self.cur.fetchone()
        print(info[0])

    def update_customer_info(self, customer):
        admin = Admin.Administrator(self.con, self.cur)
        admin.show_customer_tuple(customer)
        field = input('Which field do you want to update(name, address)?')
        value = input('What is the updated value?')
        self.cur.callproc('update_customer_info', (customer[0], field, value))
        self.con.commit()
        info = self.cur.fetchone()
        print(info[0])

    def customer_charge(self, customer):
        value = float(input('How much do you want to charge?'))
        self.cur.callproc('customer_charge', (customer[0], value))
        self.con.commit()
        info = self.cur.fetchone()
        print(info[0])

    def find_all_sets(self):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_all_sets')
        sets = cur.fetchall()
        self.show_sets(sets)

    def find_sets_by_name(self, name):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_sets_by_name', (name,))
        sets = cur.fetchall()
        self.show_sets(sets)

    def find_sets_by_release(self, lower, upper):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_sets_by_release', (lower, upper))
        sets = cur.fetchall()
        self.show_sets(sets)

    def find_sets_by_part_num(self, lower, upper):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_sets_by_part_num', (lower, upper))
        sets = cur.fetchall()
        self.show_sets(sets)

    def find_sets_by_price(self, lower, upper):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_sets_by_price', (lower, upper))
        sets = cur.fetchall()
        self.show_sets(sets)

    def find_sets_by_theme(self, name):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_sets_by_theme', (name,))
        sets = cur.fetchall()
        self.show_sets(sets)

    def find_sets_by_conditions(self, args):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_sets_by_conditions', args)
        sets = cur.fetchall()
        self.show_sets(sets)

    def query_sets(self):
        f = input('Do you want to set filters:(Y/N)')
        if f == 'N':
            self.find_all_sets()
        elif f == 'Y':
            s = input('Do you want to query by multiple conditions?(Y/N)')
            if s == 'N':
                m = self.menu_find_sets()
                if m == 1:
                    name = input('Input sets name:')
                    self.find_sets_by_name(name)
                elif m == 2:
                    lower = int(input('Input lower bound of release year:'))
                    upper = int(input('Input upper bound of release year:'))
                    self.find_sets_by_release(lower, upper)
                elif m == 3:
                    lower = int(input('Input lower bound of part number:'))
                    upper = int(input('Input upper bound of part number:'))
                    self.find_sets_by_part_num(lower, upper)
                elif m == 4:
                    lower = float(input('Input lower bound of sets price:'))
                    upper = float(input('Input upper bound of sets price:'))
                    self.find_sets_by_price(lower, upper)
                elif m == 5:
                    theme = input('Input sets theme:')
                    self.find_sets_by_theme(theme)
            elif s == 'Y':
                print('If it is null, then leave it blank')
                name = input('Input sets name:')
                lower_release = input('Input lower bound of release year:')
                if lower_release is not '':
                    lower_release = int(lower_release)
                else:
                    lower_release = 0
                upper_release = input('Input upper bound of release year:')
                if upper_release is not '':
                    upper_release = int(upper_release)
                else:
                    upper_release = 0
                lower_part_num = input('Input lower bound of part number:')
                if lower_part_num is not '':
                    lower_part_num = int(lower_part_num)
                else:
                    lower_part_num = 0
                upper_part_num = input('Input upper bound of part number:')
                if upper_part_num is not '':
                    upper_part_num = int(upper_part_num)
                else:
                    upper_part_num = 0
                lower_price = input('Input lower bound of price:')
                if lower_price is not '':
                    lower_price = float(lower_price)
                else:
                    lower_price = 0
                upper_price = input('Input upper bound of price:')
                if upper_price is not '':
                    upper_price = float(upper_price)
                else:
                    upper_price = 0
                theme = input('Input theme name:')
                self.find_sets_by_conditions(
                    (name, lower_release, upper_release, lower_part_num, upper_part_num, lower_price, upper_price,
                     theme))

    def find_all_parts(self):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_all_parts')
        parts = cur.fetchall()
        self.show_parts(parts)

    def find_parts_by_name(self, name):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_parts_by_name', (name,))
        parts = cur.fetchall()
        self.show_parts(parts)

    def find_parts_by_price(self, lower, upper):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_parts_by_price', (lower, upper))
        parts = cur.fetchall()
        self.show_parts(parts)

    def find_parts_by_color(self, name):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_parts_by_color', (name,))
        parts = cur.fetchall()
        self.show_parts(parts)

    def find_parts_by_category(self, name):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_parts_by_category', (name,))
        parts = cur.fetchall()
        self.show_parts(parts)

    def find_parts_by_conditions(self, args):
        cur = self.con.cursor(pymysql.cursors.DictCursor)
        cur.callproc('find_parts_by_conditions', args)
        parts = cur.fetchall()
        self.show_parts(parts)

    def query_parts(self):
        f = input('Do you want to set filters:(Y/N)')
        if f == 'N':
            self.find_all_parts()
        elif f == 'Y':
            s = input('Do you want to query by multiple conditions?(Y/N)')
            if s == 'N':
                m = self.menu_find_parts()
                if m == 1:
                    name = input('Input parts name:')
                    self.find_parts_by_name(name)
                elif m == 2:
                    lower = float(input('Input lower bound of parts price:'))
                    upper = float(input('Input upper bound of parts price:'))
                    self.find_parts_by_price(lower, upper)
                elif m == 3:
                    name = input('Input parts color:')
                    self.find_parts_by_color(name)
                elif m == 4:
                    name = input('Input parts category:')
                    self.find_parts_by_category(name)
            elif s == 'Y':
                print('If it is null, then leave it blank')
                name = input('Input parts name:')
                lower_price = input('Input lower bound of price:')
                if lower_price is not '':
                    lower_price = float(lower_price)
                else:
                    lower_price = 0
                upper_price = input('Input upper bound of price:')
                if upper_price is not '':
                    upper_price = float(upper_price)
                else:
                    upper_price = 0
                color = input('Input parts color name:')
                category = input('Input parts category name:')
                self.find_parts_by_conditions((name, lower_price, upper_price, color, category))

    def customer_unsubscribe(self, customer):
        self.cur.callproc('customer_unsubscribe', (customer[0],))
        self.con.commit()
        info = self.cur.fetchone()
        print(info[0])

    def customer_welcome(self):
        while True:
            m1 = self.menu_customer()
            if m1 == 1:
                self.customer_register()
            elif m1 == 2:
                customer = self.customer_login()
                if customer is not None:
                    while True:
                        m2 = self.menu_customer_service()
                        if m2 == 1:
                            self.query_sets()
                        elif m2 == 2:
                            self.query_parts()
                        elif m2 == 3:
                            self.customer_buy_sets(customer)
                        elif m2 == 4:
                            self.customer_buy_parts(customer)
                        elif m2 == 5:
                            self.update_customer_info(customer)
                        elif m2 == 6:
                            self.customer_charge(customer)
                        elif m2 == 7:
                            break
                        elif m2 == 8:
                            self.customer_unsubscribe(customer)
            elif m1 == 3:
                break
