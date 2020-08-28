import gspread
from oauth2client.service_account import ServiceAccountCredentials

from util import Side

import settings

class SheetInterface:
    ''' Converts column number into letter notation '''
    NUM_TO_CHAR = [''] + [chr(i) for i in range(ord('A'), ord('Z') + 1)] + \
        ['A' + chr(i) for i in range(ord('A'), ord('Z') + 1)]

    def __init__(self, sheet_name):

        self.credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', settings.SCOPE)
        self.client = gspread.authorize(self.credentials)

        self.main_sheet = self.client.open(sheet_name).sheet1
        self.sheet1_values = self.main_sheet.get_all_values()

        self.order_books_raw = self.get_order_books_raw()
        self.accounts_raw = self.get_accounts_raw()

        self.batch = []
    
    def get_range_string(self, start_col, start_row, width, height):
        ''' Converts 2D range of cells into letter notation '''
        return '%s%d:%s%d' % (
            self.NUM_TO_CHAR[start_col], start_row,
            self.NUM_TO_CHAR[start_col + width - 1], start_row + height - 1
        )
    
    def get_order_books_raw(self):
        '''
        gets state of order book from spreadsheet
        return: list of products, where each product is described by a list of two lists
                each inner list contains tuples of each order (name, price)
                all entries are str
        '''
        ''' 0-indexed as it needs to access self.sheet1_values '''
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
    
    def get_accounts_raw(self):
        '''
        gets state of accounts from spreadsheet
        return: list of accounts, where each account is a list of [id, name, inventory...]
                all entries are str
        '''
        ''' 0-indexed '''
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
    
    def update_order_book(self, order_book):
        '''
        takes corresponding order book of a product on a particular side in list form
        appends a request body to self.batch, waiting to be updated in a batch
        '''
        product = order_book.product
        cur_row = settings.ORDER_BOOK_ROW + 5*product.product_order
        cur_col = settings.ORDER_BOOK_COL + 2

        values = [[] for i in range(4)]
        for side in Side:
            order_book_list = order_book.get_book_in_list(side)
            for account, price in order_book_list:
                values[2 * int(side)].append(account.name)
                values[2 * int(side) + 1].append(str(price))

        for i in range(4):
            values[i] += [''] * (settings.USER_LIMIT - len(values[i]))

        self.batch.append({
            'range': self.get_range_string(cur_col, cur_row, settings.USER_LIMIT, 4),
            'values': values
        })
    
    def update_account(self, account):
        '''
        takes Account object
        appends a request body to self.batch
        '''
        cur_row = settings.ACCOUNT_ROW
        cur_col = settings.ACCOUNT_COL + 1 + account.account_order

        values = [[str(account.id)], [account.name], [account.balance]] + [None] * len(account.products)
        for product in account.products:
            values[product.product_order + 3] = [account.inventory[product]]

        self.batch.append({
            'range': self.get_range_string(cur_col, cur_row, 1, len(account.products) + 3),
            'values': values
        })
    
    def batch_update(self):
        '''
        updates all requests in self.batch to the spreadsheet
        '''
        self.main_sheet.batch_update(self.batch)
        self.batch = []
