from core.plus.ServiceRegistry import ServiceRegistry
from core.Plus import Plus

class EmployeeContract():
    @classmethod
    def calculate_all_the_move_money(cls):
        pass  



ServiceRegistry["payroll.EmployeeContract.add_customer"] = EmployeeContract.calculate_all_the_move_money