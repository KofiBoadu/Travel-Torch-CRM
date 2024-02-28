import pandas as pd
from app.models import create_databaseConnection, get_customers_information,total_customers
import os
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from flask_mail import Message
from flask import current_app
from flask_mail import Mail
# from app import create_app
from app.emails import send_email

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# app = create_app()
mail= Mail()




# def send_file_email(subject, sender, recipients, text_body, html_body=None):
# 	from app import create_app
# 	app = create_app()
#     with app.app_context():

#         msg = Message(subject, sender=sender, recipients=recipients)
#         msg.body = text_body
#         if html_body is not None:
#             msg.html = html_body  # Set the HTML content if provided
#         try:
#             mail.send(msg)
#             return True
#         except Exception as e:
#             current_app.logger.error(f'Failed to send email: {e}')
#             return False



def send_file_email(subject, sender, recipients, text_body, html_body=None):
    from app import create_app
    app = create_app()

    with app.app_context():
        mail = current_app.extensions.get('mail')
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        if html_body is not None:
            msg.html = html_body  # Set the HTML content if provided
        try:
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f'Failed to send email: {e}')
            return False




# def export_data(customers, file_format):
#     # Convert customers list to DataFrame
#     df = pd.DataFrame(customers, columns=[ 'Full_Name', 'State', 'Email', 'Mobile', 'Tour', 'Travel_Year_Start', 'Tour_Price', 'Tour_Type'])
    
#     # Choose the file format
#     file_name=""
#     if file_format.lower() == 'csv':
#         df.to_csv('CustomerTourDetails.csv', index=False)
#         file_name="CustomerTourDetails.csv"
        
#     elif file_format.lower() == 'excel':
#         df.to_excel('CustomerTourDetails.xlsx', index=False)
#         file_name= "CustomerTourDetails.xlsx"
        

#     else:
#         print('Unsupported export format specified. No export performed.')


#     return file_name




def export_data(customers, file_format):
    # Convert customers list to DataFrame
    df = pd.DataFrame(customers, columns=['Full_Name', 'State', 'Email', 'Mobile', 'Tour', 'Travel_Year_Start', 'Tour_Price', 'Tour_Type'])
    
    # Define the base path for temporary storage
    base_path = '/tmp/'
    
    # Choose the file format
    file_name = ""
    if file_format.lower() == 'csv':
        file_name = "CustomerTourDetails.csv"
        df.to_csv(os.path.join(base_path, file_name), index=False)
        
    elif file_format.lower() == 'excel':
        file_name = "CustomerTourDetails.xlsx"
        df.to_excel(os.path.join(base_path, file_name), index=False)
        
    else:
        print('Unsupported export format specified. No export performed.')

    return os.path.join(base_path, file_name)








def create_export_customer_data_procedure():
    procedure_query = """
    CREATE PROCEDURE ExportCustomerData()
    BEGIN
        SELECT
            CONCAT(c.first_name, ' ', c.last_name) AS `Full_Name`,
            c.state_address AS `State`,
            c.email_address AS `Email`,
            c.phone_number AS `Mobile`,
            t.tour_name AS `Tour`,
            YEAR(t.start_date) AS `Travel_Year_Start`,
            t.tour_price AS `Tour_Price`,
            t.tour_type AS `Tour_Type`
        FROM
            customers c
        JOIN
            tour_bookings tb ON tb.customer_id = c.customer_id
        JOIN
            tours t ON tb.tour_id = t.tour_id;
    END;
    """
    database_connection = None
    cursor = None
    try:
        database_connection = create_databaseConnection()
        cursor = database_connection.cursor()
        cursor.execute("DROP PROCEDURE IF EXISTS ExportCustomerData")
        cursor.execute(procedure_query)
        database_connection.commit()
    except Exception as e:
        raise Exception(f"An error occurred while creating procedure: {e}")
    finally:
        if cursor:
            cursor.close()
        if database_connection:
            database_connection.close()







def export_customer_data():
    database_connection = None
    cursor = None
    customers = []

    try:
        database_connection = create_databaseConnection()
        cursor = database_connection.cursor()
        cursor.callproc('ExportCustomerData')
        for result in cursor.stored_results():
            customers.extend(result.fetchall())
    except Exception as e:
        raise Exception(f"An error occurred while fetching customer data: {e}")
    finally:
        if cursor:
            cursor.close()
        if database_connection:
            database_connection.close()

    return customers







# def upload_file(filename, filepath, mimetype):
#     """Shows basic usage of the Google Drive API.
#     Uploads a file to Google Drive.
#     """
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'), SCOPES)
#             creds = flow.run_local_server(port=0)
        
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())

#     service = build('drive', 'v3', credentials=creds)

#     #Call the Drive v3 API to upload the file
#     file_metadata = {'name': filename}
#     media = MediaFileUpload(filepath, mimetype=mimetype)
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

#     return file.get('id')


# import os
# import json
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

def upload_file(filename, filepath, mimetype, SCOPES=SCOPES):
    """Uploads a file to Google Drive."""
    creds = None
    token_str = os.environ.get('GOOGLE_OAUTH_TOKEN')
    
    # If the token environment variable exists, use it to create credentials
    if token_str:
        token_info = json.loads(token_str)
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    
    # Check if credentials are valid, otherwise refresh or log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Assuming client secrets are also stored in an environment variable
            client_secrets_info = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
            flow = InstalledAppFlow.from_client_config(client_secrets_info, SCOPES)
            creds = flow.run_local_server(port=0)
            # Here, you would need to update the environment variable or use a more persistent storage
            # since changes to environment variables in runtime are not persistent across deploys/restarts in Heroku
            
    service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API to upload the file
    file_metadata = {'name': filename}
    media = MediaFileUpload(filepath, mimetype=mimetype)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return file.get('id')



# def get_google_drive_service():
#     creds = None
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 os.environ['GOOGLE_APPLICATION_CREDENTIALS'], SCOPES)
#             creds = flow.run_local_server(port=0)
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
    
#     service = build('drive', 'v3', credentials=creds)
#     return service

# import os
# import json
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build

def get_google_drive_service():
    """Returns a service object connected to the Google Drive API."""
    creds = None
    # Try to load the token from an environment variable
    token_str = os.environ.get('GOOGLE_OAUTH_TOKEN')
    
    if token_str:
        # If the token was found in the environment variable, load it
        token_info = json.loads(token_str)
        creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    
    # Check if the credentials are not valid or do not exist
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load client secrets from an environment variable
            client_secrets_info = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
            flow = InstalledAppFlow.from_client_config(client_secrets_info, SCOPES)
            creds = flow.run_local_server(port=0)
            # Note: In a production environment, especially in platforms like Heroku,
            # you should consider a more persistent solution for storing refreshed tokens

    # Build the service object for the Google Drive API
    service = build('drive', 'v3', credentials=creds)
    return service






def generate_shareable_link(file_id):
    service = get_google_drive_service()
    request = service.files().get(fileId=file_id, fields='webViewLink')
    response = request.execute()
    print(f"WebViewLink: {response.get('webViewLink')}")
    return response.get('webViewLink')







def make_file_public(file_id):
    service = get_google_drive_service()
    # Make the file public
    permission = {
        'type': 'anyone',
        'role': 'reader',
    }
    service.permissions().create(
        fileId=file_id,
        body=permission,
        fields='id',
    ).execute()








def get_download_link(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"
    




# customers= export_customer_data()
# filename= export_data(customers, 'csv')

# filepath='/Users/danielkofiboadu/Desktop/Travel-Torch-CRM/'+filename


# file=upload_file(filename, filepath, 'text/'+'csv')

# make_file_public(file)


# download=get_download_link(file)

# print(download)


# subject = "Your Subject Here"
# sender = "bookings@africatravellers.com"
# recipients = ["mrboadu3@gmail.com"]
# text_body = "This is the text body of the email."
# html_body = f"""
# <h1>This is the HTML Body of the Email</h1>
# <p>This part is in <strong>bold</strong>.</p>
# <p>Visit <a href='{download}'</a> for more information.</p>
# """




# print(send_file_email(subject, sender, recipients, text_body, html_body))


# '/Users/danielkofiboadu/Desktop/Travel-Torch-CRM/app/credentials.json'
