from datetime import datetime

# datetime.strptime(segment['departureDate'],"%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
tim = "2023-1-16T14:20:00"
dep = datetime.strptime(tim, "%Y-%m-%dT%H:%M:%S").strftime("%Y%m%d%H%M")
print(dep)