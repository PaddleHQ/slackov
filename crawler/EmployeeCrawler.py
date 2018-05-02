from app.Employees import Employees
from crawler.SlackCrawler import SlackCrawler


class EmployeeCrawler(SlackCrawler):
    employee = None

    def __init__(self):
        SlackCrawler.__init__(self)
        self.employee = Employees()

    def run(self):
        employees = self.get_slack_response(
            self.get_user_list
        )
        for employee in employees['members']:
            if self.employee.exists_by_id(employee['id']) is False:
                print ("Inserting '%s'" % (employee['name']))
                self.employee.create(employee)
            else:
                print ("Skipping '%s'" % (employee['name']))

    def get_user_list(self):
        return self.slack_client.api_call(
            "users.list",
        )