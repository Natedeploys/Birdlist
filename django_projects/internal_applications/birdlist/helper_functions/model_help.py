
def get_no_stars(val):
    if val == 0:
        return '-'
    stars = ''
    for i in range(val):
        stars += '*'
    return stars

