from core.plus.ServiceRegistry import ServiceRegistry
from core.Plus import Plus

class EmployeeContract():
    @classmethod
    @ServiceRegistry.register("payroll.EmployeeContract.add_customer")
    def calculate_all_the_move_money(cls):
        pass  



