import pymysql
import Staff
import Admin
import Customer


def menu_role():
    print('Choose your role')
    print('1.Admin')
    print('2.Staff')
    print('3.Customer')
    return int(input())


if __name__ == '__main__':
    while True:
        n = menu_role()
        if n == 1:
            while True:
                username = input('Admin username:')
                password = input('Admin password:')
                try:
                    con = pymysql.connect(host='localhost', user=username, password=password, db='lego',
                                          cursorclass=pymysql.cursors.DictCursor)
                    cur = con.cursor()
                    break
                except:
                    print('Access Denied! Try Again!')
            admin = Admin.Administrator(con, cur)
            admin.admin_welcome()
        elif n == 2:
            staff = Staff.StaffModule()
            staff.staff_welcome()
        elif n == 3:
            customer = Customer.CustomerModule()
            customer.customer_welcome()
        else:
            print('No such role! Try Again!')
