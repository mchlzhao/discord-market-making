from util import Product

#
# Spreadsheet
#

# coordinates 1-indexed
ORDER_BOOK_ROW = 2
ORDER_BOOK_COL = 2

ACCOUNT_ROW = 2
ACCOUNT_COL = 15



#
# Game constants
#

USER_LIMIT = 10
POSITION_LIMIT = 5

PRODUCTS = [
    Product(1, 0, 'E1'),
    Product(2, 1, 'E2'),
    Product(3, 2, 'E3'),
    Product(4, 3, 'E4'),
    Product(5, 4, 'E5'),
    Product(6, 5, 'E6'),
    Product(7, 6, 'E7'),
    Product(8, 7, 'E8'),
    Product(9, 8, 'E9'),
    Product(10, 9, 'E10'),
    Product(11, 10, 'E11'),
]



#
# Google authentication
#

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
