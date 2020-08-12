import gspread
from oauth2client.service_account import ServiceAccountCredentials

import settings

class SheetInterface:
    def __init__(self, sheet_name):
        self.NUM_TO_CHAR = [''] + [chr(i) for i in range(ord('A'), ord('Z') + 1)] + \
            ['A' + chr(i) for i in range(ord('A'), ord('Z') + 1)]

        self.credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', settings.SCOPE)
        self.client = gspread.authorize(self.credentials)

        self.main_sheet = self.client.open(sheet_name).sheet1
        self.sheet1_values = self.main_sheet.get_all_values()

        self.order_books_raw = self.get_order_books_raw()
        self.accounts_raw = self.get_accounts_raw()

        self.batch = []
    
    def get_range_string(self, start_col, start_row, width, height):
        return '%s%d:%s%d' % (
            self.NUM_TO_CHAR[start_col], start_row,
            self.NUM_TO_CHAR[start_col + width - 1], start_row + height
        )
    
    # formats order books from sheet1 as a list of pairs of two lists (both sides of one product)
    # each side stores a list of tuples (name: str, price: str)
    def get_order_books_raw(self):
        # 0-indexed as it needs to access self.sheet1_values
        table_row = settings.ORDER_BOOK_ROW - 1
        table_col = settings.ORDER_BOOK_COL - 1

        raw_data = []

        while table_row < len(self.sheet1_values) and self.sheet1_values[table_row + 1][table_col][:5] == 'Event':
            cur_product = [[], []]
            cur_row = table_row
            cur_col = table_col + 2

            for i in range(2):
                while cur_col < len(self.sheet1_values[cur_row]) and self.sheet1_values[cur_row][cur_col] != '':
                    cur_product[i].append((self.sheet1_values[cur_row][cur_col], self.sheet1_values[cur_row+1][cur_col]))
                    cur_col += 1
                
                cur_row += 2
                cur_col = table_col + 2

            raw_data.append(cur_product)
            table_row += 5
        
        return raw_data
    
    # formats accounts table from sheet 1 as a list of lists
    # each inner list is a column from the table [account_id, name, inventory...]
    # every entry is a str
    def get_accounts_raw(self):
        # 0-indexed
        table_row = settings.ACCOUNT_ROW - 1
        table_col = settings.ACCOUNT_COL

        raw_data = []

        while table_col < len(self.sheet1_values[table_row]) and self.sheet1_values[table_row][table_col] != '':
            cur_account = []
            cur_row = table_row

            while cur_row < len(self.sheet1_values) and self.sheet1_values[cur_row][table_col] != '':
                cur_account.append(self.sheet1_values[cur_row][table_col])

                cur_row += 1
            
            raw_data.append(cur_account)
            table_col += 1
        
        return raw_data
    
    def update_order_book(self, product, side, order_book_list):
        cur_row = settings.ORDER_BOOK_ROW + 5*product.product_order + 2*int(side)
        cur_col = settings.ORDER_BOOK_COL + 2

        values = [[], []]
        for account, price in order_book_list:
            values[0].append(account.name)
            values[1].append(str(price))
        for i in range(2):
            values[i] += [''] * (settings.USER_LIMIT - len(values[i]))

        self.batch.append({
            'range': self.get_range_string(cur_col, cur_row, settings.USER_LIMIT, 2),
            'values': values
        })
    
    def update_account(self, account):
        cur_row = settings.ACCOUNT_ROW + 2
        cur_col = settings.ACCOUNT_COL + 1 + account.account_order

        values = [[account.balance]]
        temp = []
        for product, position in account.inventory.items():
            temp.append((product.product_order, position))
        temp.sort()
        for _, y in temp:
            values.append([y])

        self.batch.append({
            'range': self.get_range_string(cur_col, cur_row, 1, len(account.inventory) + 1),
            'values': values
        })

    def add_account(self, account):
        cur_row = settings.ACCOUNT_ROW
        cur_col = settings.ACCOUNT_COL + 1 + account.account_order

        self.batch.append({
            'range': self.get_range_string(cur_col, cur_row, 1, 2),
            'values': [[str(account.account_id)], [account.name]]
        })

        self.update_account(account)
    
    def batch_update(self):
        self.main_sheet.batch_update(self.batch)
        self.batch = []
