from apps.dashboard.services.DashboardService import DashboardService
def get_information_dashboard(request, plugin_name=None):
    #here we will to get the information of a plugin that need the dashboard
    answer=DashboardService.get_information_of_a_plugin(request, plugin_name)
    return answer