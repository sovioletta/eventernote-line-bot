import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/spreadsheets']


def find_url_col(header_col):
    i = 1
    for col in header_col:
        if col == 'url':
            break
        i += 1

    return i


def url_col_to_char(url_col):
    return chr(64+url_col)


def add_event_row(sheet, sheet_id, sheet_name, row_idx, url_col, date, title, url):
    try:
        range_name = "{}!A{}:{}{}".format(sheet_name, row_idx, url_col_to_char(url_col), row_idx)

        row = [date, title]
        for i in range(3, url_col):
            row.append('')
        row.append(url)

        body = {
            'values': [row]
        }
        result = sheet.values().update(
            spreadsheetId=sheet_id, range=range_name,
            valueInputOption='USER_ENTERED', body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error


def init_sheet():
    token_file = os.path.join(os.getcwd(), './token.json')
    creds = service_account.Credentials.from_service_account_file(token_file, scopes=SCOPES)

    try:
        service = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets()
    except HttpError as err:
        print(err)


def add_event(sheet, sheet_id, sheet_name, date, title, url):
    try:
        result = sheet.values().get(spreadsheetId=sheet_id,
                                    range='{}!A1:M'.format(sheet_name)).execute()
        values = result.get('values', [])

        url_col = find_url_col(values[0])
        row_idx = len(values) + 1

        add_event_row(sheet, sheet_id, sheet_name, row_idx, url_col, date, title, url)

    except HttpError as err:
        print(err)
