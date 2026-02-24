import datetime

current_date = datetime.datetime.now()
new_date = current_date - datetime.timedelta(days = 5)
print("Current date:", current_date.strftime("%Y-%m-%d"))
print("Date after subtracting 5 days:", new_date.strftime("%Y-%m-%d"))


yesterday = current_date - datetime.timedelta(days = 1)
tomorrow = current_date + datetime.timedelta( days = 1)
print("current date: ", current_date.strftime("%Y-%m-%d"))
print("yesterday: ", yesterday.strftime("%Y-%m-%d"))
print("tomorrow ", tomorrow.strftime("%Y-%m-%d"))


#dropping microseconds from datetime
no_microseconds = current_date.replace(microsecond=0)
print("Datetime without microseconds:", no_microseconds)


#calculate two date difference in seconds
date1_str = input("Enter first date (YYYY-MM-DD HH:MM:SS): ")
date2_str = input("Enter second date (YYYY-MM-DD HH:MM:SS): ")
date1 = datetime.strptime(date1_str, "%Y-%m-%d %H:%M:%S")
date2 = datetime.strptime(date2_str, "%Y-%m-%d %H:%M:%S")
diff = date2 - date1
print("Difference in seconds:", diff.total_seconds())