# Ajoutez l'import en haut
import threading

# Auto-generate Redis reports 2 seconds after startup (to give enough time for the DB to start up as well). Once done for the first time, repeat it recursively every 60s to refresh the cache.
def generate_reports_and_cache():
    threading.Timer(2.0, get_report_highest_spending_users, args=(True,)).start()
    threading.Timer(2.0, get_report_best_selling_products, args=(True,)).start()
    threading.Timer(60.0, generate_reports_and_cache).start()

# Start the first execution
generate_reports_and_cache()