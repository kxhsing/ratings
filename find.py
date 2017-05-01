def findInfo(filename):

    f = open(filename)

    ids = [1, 4]
    longest_length = 0
    for line in f:
        line = line.rstrip()
        items = line.split("|")
        title, url = (items[i] for i in ids)
        if len(url) > longest_length:
            longest_length = len(url)
    return longest_length
    
    # , title, date, video_date, url, g01, g02, g03, g04, g05, g06, g07, g08, g09, g10, g11, g12, g13, g14 = 