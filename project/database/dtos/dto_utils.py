# I chose to give the full datetime object to the frontend to be able to sort by it.
# Therefore the formatting has to be done there as well
def sql_server_datetime_to_human_readable(date):
    return date.strftime("%d/%m/%Y, %H:%M:%S")
