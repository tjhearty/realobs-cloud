import pdb

def find_months(dt_array,month_numbers):
    """
    Find the indices for a particular month in an array of datetimes
    """

    idts = []

    if type(month_numbers) == int: # It's only 1 month
        month_number = month_numbers
        
        for idt,dt in enumerate(dt_array):
            if dt.month == month_number:
                idts.append(idt)

    else:
        for month_number in month_numbers: # It's a list of month numbers
            idts.extend(find_months(dt_array,month_number))


    return idts
