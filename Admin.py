import pymysql


class Administrator:
    def __init__(self, con, cur):
        self.con = con
        self.cur = cur

    @staticmethod
    def menu_tables():
        print('Welcome admin! Which table do you want to operate?')
        print('1.Staff')
        print('2.Customer')
        print('3.Branch')
        print('4.I want to log out')
        return int(input())

    @staticmethod
    def menu_branch_CRUD():
        print('What do you want to do?')
        print('1.Add branches')
        print('2.Delete branches')
        print('3.Update branches')
        print('4.Query branches')
        print('5.Exit')
        return int(input())

    @staticmethod
    def menu_staff_CRUD():
        print('What do you want to do?')
        print('1.Add staffs')
        print('2.Delete staffs')
        print('3.Update staffs')
        print('4.Query staffs')
        print('5.Exit')
        return int(input())

    @staticmethod
    def menu_find_staff():
        print('Which filter do you want to set?')
        print('1. Search by username')
        print('2. Search by salary')
        print('3. Search by branch')
        return int(input())

    @staticmethod
    def menu_find_branches():
        print('Which filter do you want to set?')
        print('1. Search by branch name')
        print('2. Search by profit')
        print('3. Search by address')
        return int(input())

    @staticmethod
    def menu_find_customers():
        print('Which filter do you want to set?')
        print('1. Search by customer name')
        print('2. Search by balance')
        print('3. Search by address')
        return int(input())

    def find_all_branches(self):
        sql = 'SELECT * FROM branches'
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def find_branch_by_id(self, name):
        sql = 'SELECT * FROM branches WHERE branchName = %s'
        self.cur.execute(sql, (name,))
        res = self.cur.fetchone()
        return res

    def find_branch_by_name(self, name):
        sql = 'SELECT * FROM branches WHERE branchName LIKE "%' + name + '%"'
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def find_branch_by_profit(self, lower, upper):
        sql = 'SELECT * FROM branches WHERE profit BETWEEN %s AND %s'
        self.cur.execute(sql, (lower, upper))
        res = self.cur.fetchall()
        return res

    def find_branch_by_address(self, address):
        sql = 'SELECT * FROM branches WHERE zipCode = %s'
        self.cur.execute(sql, (address,))
        res = self.cur.fetchall()
        return res

    def add_branch(self):
        branch_num = int(input('How many branches do you want to add?'))
        for num in range(branch_num):
            print(f'Branch {num + 1}:')
            branch_name = input('new branch name:')
            while True:
                address = self.find_all_address()
                self.show_address(address)
                branch_code = input('Where is this new branch? Enter zipcode:')
                sql1 = 'SELECT * FROM address WHERE zipcode = %s'
                self.cur.execute(sql1, (branch_code,))
                try:
                    zipcode = self.cur.fetchone()['zipCode']
                    break
                except:
                    print('No address found! Insert fail!')
            sql2 = 'INSERT INTO branches(branchName, profit, zipCode) VALUES (%s, 0, %s)'
            try:
                self.cur.execute(sql2, (branch_name, branch_code))
                self.con.commit()
            except:
                print(f'branch table has already have {branch_name}! Insert fail!')

    def delete_branch(self):
        branch_num = int(input('How many branches do you want to delete?'))
        for num in range(branch_num):
            while True:
                branches = self.find_all_branches()
                self.show_branches(branches)
                branch_id = int(input('Branch ID:'))
                sql1 = 'SELECT * FROM branches WHERE cid = %s'
                self.cur.execute(sql1, (branch_id,))
                try:
                    branch_ids = self.cur.fetchone()['cid']
                    break
                except:
                    print('Branch not found! Delete fail!')
            sql2 = 'DELETE FROM branches WHERE cid = %s'
            self.cur.execute(sql2, (branch_id,))
            self.con.commit()

    def update_branch(self):
        branch_num = int(input('How many branches do you want to update?'))
        for num in range(branch_num):
            while True:
                branches = self.find_all_branches()
                self.show_branches(branches)
                branch_id = int(input('Branch ID:'))
                sql1 = 'SELECT * FROM branches WHERE cid = %s'
                self.cur.execute(sql1, (branch_id,))
                try:
                    branch_ids = self.cur.fetchone()['cid']
                    break
                except:
                    print('Branch not found! Update fail!')
            pro = input('Which field do you want to update? (branchName, profit, zipCode)')
            try:
                if pro == 'zipCode':
                    address = self.find_all_address()
                    self.show_address(address)
                val = input('What is the updated value?')
                if pro == 'branchName':
                    sql2 = 'UPDATE branches SET branchName = %s WHERE cid = %s'
                elif pro == 'profit':
                    sql2 = 'UPDATE branches SET profit = %s WHERE cid = %s'
                elif pro == 'zipCode':
                    val = self.find_address_by_id(val)['zipCode']
                    sql2 = 'UPDATE branches SET zipCode = %s WHERE cid = %s'
                self.cur.execute(sql2, (val, branch_id))
                self.con.commit()
            except:
                print('Value or field invalid! Update fail!')

    def find_branch_by_conditions(self, *args):
        sql = 'SELECT * FROM branches WHERE 1 = 1'
        params = []
        if args[0][0] is not '':
            con = ' AND branchName LIKE "%%' + args[0][0] + '%%"'
            sql += con
        if args[0][1] is not '' or args[0][2] is not '':
            if args[0][1] and args[0][2] is not '':
                lower = int(args[0][1])
                upper = int(args[0][2])
                con = ' AND profit BETWEEN %s AND %s'
                sql += con
                params.append(lower)
                params.append(upper)
            elif args[0][1] is not '':
                lower = int(args[0][1])
                con = ' AND profit >= %s'
                sql += con
                params.append(lower)
            elif args[0][2] is not '':
                upper = int(args[0][2])
                con = ' AND profit <= %s'
                sql += con
                params.append(upper)
        if args[0][3] is not '':
            res = self.find_address_by_id(args[0][3])
            if res is not None:
                con = ' AND zipCode = %s'
                sql += con
                params.append(res['zipCode'])
            else:
                print('No address found!')
                return
        self.cur.execute(sql, tuple(params))
        branches = self.cur.fetchall()
        self.show_branches(branches)

    def query_branch(self):
        f = input('Do you want to set filters:(Y/N)')
        if f == 'N':
            branches = self.find_all_branches()
            self.show_branches(branches)
        elif f == 'Y':
            s = input('Do you want to query by multiple conditions?(Y/N)')
            if s == 'N':
                m = self.menu_find_branches()
                if m == 1:
                    name = input('Input branch name:')
                    branches = self.find_branch_by_name(name)
                    self.show_branches(branches)
                elif m == 2:
                    lower = input('Input lower bound of profit:')
                    upper = input('Input upper bound of profit:')
                    branches = self.find_branch_by_profit(lower, upper)
                    self.show_branches(branches)
                elif m == 3:
                    address = input('Input zipCode:')
                    branches = self.find_branch_by_address(address)
                    self.show_branches(branches)
            elif s == 'Y':
                print('If it is null, then leave it blank')
                name = input('Input branch name:')
                lower = input('Input lower bound of profit:')
                upper = input('Input upper bound of profit:')
                zipCode = input('Input zipCode:')
                self.find_branch_by_conditions((name, lower, upper, zipCode))

    def show_branches(self, branches):
        if len(branches) == 0:
            print('No branch found!')
        else:
            print('branchID'.ljust(30), 'branchName'.ljust(30), 'profit'.ljust(30), 'zipCode'.ljust(30))
            for b in branches:
                print(str(b['cid']).ljust(30), b['branchName'].ljust(30), str(b['profit']).ljust(30),
                      b['zipCode'].ljust(30))

    def find_all_staff(self):
        sql = 'SELECT * FROM staff'
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def find_staff_by_username(self, username):
        sql = 'SELECT * FROM staff WHERE staffName LIKE "%' + username + '%"'
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def find_staff_by_salary(self, lower, upper):
        sql = 'SELECT * FROM staff WHERE staffSalary BETWEEN %s AND %s'
        self.cur.execute(sql, (lower, upper))
        res = self.cur.fetchall()
        return res

    def find_staff_by_branch(self, name):
        sql = 'SELECT staffId, staffName, staffPassword, staffSalary, branchName FROM staff s JOIN branches b ON s.cid = b.cid WHERE branchName = %s'
        self.cur.execute(sql, (name,))
        res = self.cur.fetchall()
        return res

    def find_staff_by_conditions(self, *args):
        sql = 'SELECT * FROM staff WHERE 1 = 1'
        params = []
        if args[0][0] is not '':
            con = ' AND staffName LIKE "%%' + args[0][0] + '%%"'
            sql += con
        if args[0][1] is not '' or args[0][2] is not '':
            if args[0][1] and args[0][2] is not '':
                lower = int(args[0][1])
                upper = int(args[0][2])
                con = ' AND staffSalary BETWEEN %s AND %s'
                sql += con
                params.append(lower)
                params.append(upper)
            elif args[0][1] is not '':
                lower = int(args[0][1])
                con = ' AND staffSalary >= %s'
                sql += con
                params.append(lower)
            elif args[0][2] is not '':
                upper = int(args[0][2])
                con = ' AND staffSalary <= %s'
                sql += con
                params.append(upper)
        if args[0][3] is not '':
            res = self.find_branch_by_id(args[0][3])
            if res is not None:
                con = ' AND cid = %s'
                sql += con
                params.append(res['cid'])
            else:
                print('No branch found!')
                return
        self.cur.execute(sql, tuple(params))
        staffs = self.cur.fetchall()
        self.show_staff(staffs)

    def add_staff(self):
        staff_num = int(input('How many staffs do you want to add?'))
        for num in range(staff_num):
            print(f'staff {num + 1}:')
            username = input('new staff username:')
            password = input('new staff password:')
            salary = int(input('new staff salary:'))
            while True:
                branches = self.find_all_branches()
                self.show_branches(branches)
                branch_name = input('Which branch does this new staff work in? Enter branch name:')
                sql1 = 'SELECT * FROM branches WHERE branchName = %s'
                self.cur.execute(sql1, (branch_name,))
                try:
                    branch_id = self.cur.fetchone()['cid']
                    break
                except:
                    print('No branch found! Insert fail!')
            sql2 = 'INSERT INTO staff(staffName, staffPassword, staffSalary, cid) VALUES (%s, %s, %s, %s)'
            try:
                self.cur.execute(sql2, (username, password, salary, branch_id))
                self.con.commit()
            except:
                print(f'staff table has already have {username}! Insert fail!')

    def delete_staff(self):
        staff_num = int(input('How many staffs do you want to delete?'))
        for num in range(staff_num):
            while True:
                staffs = self.find_all_staff()
                self.show_staff(staffs)
                staff_id = int(input('Staff ID:'))
                sql1 = 'SELECT * FROM staff WHERE staffId = %s'
                self.cur.execute(sql1, (staff_id,))
                try:
                    branch_id = self.cur.fetchone()['cid']
                    break
                except:
                    print('Staff not found! Delete fail!')
            sql2 = 'DELETE FROM staff WHERE staffId = %s'
            self.cur.execute(sql2, (staff_id,))
            self.con.commit()

    def update_staff(self):
        staff_num = int(input('How many staffs do you want to update?'))
        for num in range(staff_num):
            while True:
                staffs = self.find_all_staff()
                self.show_staff(staffs)
                staff_id = int(input('Staff ID:'))
                sql1 = 'SELECT * FROM staff WHERE staffId = %s'
                self.cur.execute(sql1, (staff_id,))
                try:
                    branch_id = self.cur.fetchone()['cid']
                    break
                except:
                    print('Staff not found! Update fail!')
            pro = input('Which field do you want to update? (username, password, salary, branch)')
            try:
                if pro == 'branch':
                    branches = self.find_all_branches()
                    self.show_branches(branches)
                val = input('What is the updated value?')
                if pro == 'username':
                    sql2 = 'UPDATE staff SET staffUsername = %s WHERE staffId = %s'
                elif pro == 'password':
                    sql2 = 'UPDATE staff SET staffPassword = %s WHERE staffId = %s'
                elif pro == 'salary':
                    sql2 = 'UPDATE staff SET staffSalary = %s WHERE staffId = %s'
                elif pro == 'branch':
                    val = self.find_branch_by_id(val)['cid']
                    sql2 = 'UPDATE staff SET cid = %s WHERE staffId = %s'
                self.cur.execute(sql2, (val, staff_id))
                self.con.commit()
            except:
                print('Value or field invalid! Update fail!')

    def query_staff(self):
        f = input('Do you want to set filters:(Y/N)')
        if f == 'N':
            staffs = self.find_all_staff()
            self.show_staff(staffs)
        elif f == 'Y':
            s = input('Do you want to query by multiple conditions?(Y/N)')
            if s == 'N':
                m = self.menu_find_staff()
                if m == 1:
                    username = input('Input username:')
                    staffs = self.find_staff_by_username(username)
                    self.show_staff(staffs)
                elif m == 2:
                    lower = int(input('Input lower bound of salary:'))
                    upper = int(input('Input upper bound of salary:'))
                    staffs = self.find_staff_by_salary(lower, upper)
                    self.show_staff(staffs)
                elif m == 3:
                    branch_name = input('Input branch name:')
                    staffs = self.find_staff_by_branch(branch_name)
                    self.show_staff(staffs)
            elif s == 'Y':
                print('If it is null, then leave it blank')
                username = input('Input username:')
                lower = input('Input lower bound of salary:')
                upper = input('Input upper bound of salary:')
                branch_name = input('Input branch name:')
                self.find_staff_by_conditions((username, lower, upper, branch_name))

    def show_staff(self, staffs):
        if len(staffs) == 0:
            print('No staff found!')
        else:
            print('StaffID'.ljust(30), 'StaffName'.ljust(30), 'staffPassword'.ljust(30), 'staffSalary'.ljust(30),
                  'branchId'.ljust(30))
            for s in staffs:
                print(str(s['staffId']).ljust(30), s['staffName'].ljust(30), s['staffPassword'].ljust(30),
                      str(s['staffSalary']).ljust(30), str(s['cid']).ljust(30))

    def find_all_address(self):
        sql = 'SELECT * FROM address'
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def find_address_by_id(self, id):
        sql = 'SELECT * FROM address WHERE zipCode = %s'
        self.cur.execute(sql, (id,))
        res = self.cur.fetchone()
        return res

    def show_address(self, address):
        print('zipCode'.ljust(30), 'City'.ljust(30), 'State'.ljust(30))
        for a in address:
            print(str(a['zipCode']).ljust(30), a['city'].ljust(30), a['state'].ljust(30))

    def find_all_customers(self):
        sql = 'SELECT * FROM customer'
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def show_customer(self, customers):
        if len(customers) == 0:
            print('No customer found!')
        else:
            print('CustomerEmail'.ljust(30), 'CustomerName'.ljust(30), 'Balance'.ljust(30), 'zipCode'.ljust(30))
            for c in customers:
                print(c['customerEmail'].ljust(30), c['customerName'].ljust(30), str(c['balance']).ljust(30),
                      c['zipCode'].ljust(30))

    def show_customer_tuple(self, customers):
        if len(customers) == 0:
            print('No customer found!')
        else:
            print('CustomerEmail'.ljust(30), 'CustomerName'.ljust(30), 'Balance'.ljust(30), 'zipCode'.ljust(30))
            print(customers[0].ljust(30), customers[1].ljust(30),
                  str(customers[2]).ljust(30), customers[3].ljust(30))

    def find_customer_by_name(self, name):
        sql = 'SELECT * FROM customer WHERE customerName LIKE "%' + name + '%"'
        self.cur.execute(sql)
        res = self.cur.fetchall()
        return res

    def find_customer_by_balance(self, lower, upper):
        sql = 'SELECT * FROM customer WHERE balance BETWEEN %s AND %s'
        self.cur.execute(sql, (lower, upper))
        res = self.cur.fetchall()
        return res

    def find_customer_by_address(self, address):
        sql = 'SELECT * FROM customer WHERE zipCode = %s'
        self.cur.execute(sql, (address,))
        res = self.cur.fetchall()
        return res

    def find_customer_by_conditions(self, *args):
        sql = 'SELECT * FROM customer WHERE 1 = 1'
        params = []
        if args[0][0] is not '':
            con = ' AND customerName LIKE "%%' + args[0][0] + '%%"'
            sql += con
        if args[0][1] is not '' or args[0][2] is not '':
            if args[0][1] and args[0][2] is not '':
                lower = int(args[0][1])
                upper = int(args[0][2])
                con = ' AND balance BETWEEN %s AND %s'
                sql += con
                params.append(lower)
                params.append(upper)
            elif args[0][1] is not '':
                lower = int(args[0][1])
                con = ' AND balance >= %s'
                sql += con
                params.append(lower)
            elif args[0][2] is not '':
                upper = int(args[0][2])
                con = ' AND balance <= %s'
                sql += con
                params.append(upper)
        if args[0][3] is not '':
            res = self.find_address_by_id(args[0][3])
            if res is not None:
                con = ' AND zipCode = %s'
                sql += con
                params.append(res['zipCode'])
            else:
                print('No address found!')
                return
        self.cur.execute(sql, tuple(params))
        customers = self.cur.fetchall()
        self.show_customer(customers)

    def query_customer(self):
        f = input('Do you want to set filters:(Y/N)')
        if f == 'N':
            customers = self.find_all_customers()
            self.show_customer(customers)
        elif f == 'Y':
            s = input('Do you want to query by multiple conditions?(Y/N)')
            if s == 'N':
                m = self.menu_find_customers()
                if m == 1:
                    name = input('Input customer name:')
                    customers = self.find_customer_by_name(name)
                    self.show_customer(customers)
                elif m == 2:
                    lower = input('Input lower bound of balance:')
                    upper = input('Input upper bound of balance:')
                    customers = self.find_customer_by_balance(lower, upper)
                    self.show_customer(customers)
                elif m == 3:
                    address = input('Input zipCode:')
                    customers = self.find_customer_by_address(address)
                    self.show_customer(customers)
            elif s == 'Y':
                print('If it is null, then leave it blank')
                name = input('Input customer name:')
                lower = input('Input lower bound of balance:')
                upper = input('Input upper bound of balance:')
                zipCode = input('Input zipCode:')
                self.find_customer_by_conditions((name, lower, upper, zipCode))

    def admin_welcome(self):
        while True:
            m1 = self.menu_tables()
            if m1 == 1:
                while True:
                    m2 = self.menu_staff_CRUD()
                    if m2 == 1:
                        self.add_staff()
                    elif m2 == 2:
                        self.delete_staff()
                    elif m2 == 3:
                        self.update_staff()
                    elif m2 == 4:
                        self.query_staff()
                    elif m2 == 5:
                        break
                    else:
                        print('Invalid input! Try again!')
            elif m1 == 2:
                self.query_customer()
            elif m1 == 3:
                while True:
                    m3 = self.menu_branch_CRUD()
                    if m3 == 1:
                        self.add_branch()
                    elif m3 == 2:
                        self.delete_branch()
                    elif m3 == 3:
                        self.update_branch()
                    elif m3 == 4:
                        self.query_branch()
                    elif m3 == 5:
                        break
                    else:
                        print('Invalid input! Try again!')
            elif m1 == 4:
                break
            else:
                print('No such table! Try again!')
