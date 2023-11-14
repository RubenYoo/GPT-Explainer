import argparse
import requests
import os
from Client import status


class PythonClient:
    """
    This class represents the python client
    """
    def __init__(self):
        self.url = 'http://127.0.0.1:5000/'

    def send_file(self, path: str, email: str = None) -> str:
        """
        This function sends a file to the server
        :param path: the path of the file
        :param email: optional email to attach to the file
        :return: the uid of the file
        """

        with open(path, 'rb') as file:
            if email:
                response = requests.post(self.url, files={'file': file}, data={'email': email})
            else:
                response = requests.post(self.url, files={'file': file})

        if response.status_code == 200:
            return response.json()['uid']
        else:
            raise Exception(response.text)

    def send_uid(self, uid: str) -> status.Status:
        """
        This function sends an uid to the server
        :param uid: the uid of the file
        :return: the status of the file
        """

        data = {
            'uid': {uid}
        }

        response = requests.get(self.url + "status", params=data)
        my_status = status.Status(response.json())
        if response.status_code == 200:
            return my_status
        elif response.status_code == 404 and my_status.is_not_found():
            raise Exception("UID not found")
        else:
            raise Exception("the request failed")

    def send_status(self, email: str, filename: str) -> status.Status:
        """
        This function sends an email and filename to the server to check the status
        :param email: the email of the file uploader
        :param filename: the filename to check the status for
        :return: the status of the file
        """

        data = {
            'email': {email},
            'filename': {filename}
        }

        response = requests.get(self.url + "status", params=data)
        my_status = status.Status(response.json())

        if response.status_code == 200:
            return my_status
        elif response.status_code == 404 and my_status.is_not_found():
            raise Exception("File not found for the provided email and filename")
        else:
            raise Exception("The request failed")


def main():
    """
    This function is the main function
    of the python client
    it sends a file or an uid to the server, and prints the response
    """

    parser = argparse.ArgumentParser(description="Upload a Powerpoint file, or send a UID")
    parser.add_argument('-upload', metavar='<file path>', help='Upload a file')
    parser.add_argument('-check', metavar='<uid>', help='Check UID')
    parser.add_argument('-email', metavar='<email>', help='Email of the file uploader')
    parser.add_argument('-filename', metavar='<filename>', help='Filename to check the status for (optional)')
    args = parser.parse_args()

    try:
        my_client = PythonClient()
        if args.upload:
            file_path = args.upload
            if not os.path.isfile(file_path):
                raise Exception("This file does not exist")
            uid = my_client.send_file(file_path, email=args.email)
            print(f"The uid is {uid}")
        elif args.check:
            uid = args.check
            response = my_client.send_uid(uid)
            print(response.get_response())
        elif args.email and args.filename:
            response = my_client.send_status(args.email, args.filename)
            print(response.get_response())
        else:
            raise Exception("Invalid parameters")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
