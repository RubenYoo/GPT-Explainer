import subprocess
import unittest
import time
import os
import Client.python_client
import Client.status


class MyTestCase(unittest.TestCase):
    def test_system(self):
        """
        This function tests the system
        """

        self.file_path = "../asyncio-intro.pptx"

        self.scripts = ['../Web_api/app.py', '../Gpt_explainer/main.py']

        self.processes = []

        for script in self.scripts:
            process = subprocess.Popen(['python', script])
            self.processes.append(process)

        my_client = Client.python_client.PythonClient()

        try:
            uid = my_client.send_file(os.path.abspath(self.file_path))
            print(uid)

            my_status = Client.status.Status(my_client.send_uid(uid))
            while not my_status.is_done():
                time.sleep(5)
                my_status = Client.status.Status(my_client.send_uid(uid))

            print(my_status.get_explanation())

        except Exception as e:
            print(e)

        for process in self.processes:
            process.terminate()


def main():
    system_test = MyTestCase()
    system_test.test_system()


if __name__ == '__main__':
    unittest.main()
