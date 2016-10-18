from subprocess import Popen, PIPE
import sys, re, locale


def main():
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    inp = ""
    for i in range(1,len(sys.argv)):
        p = Popen(['pdftotext', '-layout', sys.argv[i], '-'], stdout=PIPE)
        out, _ = p.communicate(None)
        if not 'date' in locals():
            date = getDate(out.split('\n'))
        if date and date == getDate(out.split('\n')):
            inp += out
        else:
            if date:
                print "The reports don't have the same date! Error on file",'"{0}"'.format(sys.argv[i])
                return

    lines = inp.split('\n')


    card, cash = getPayments(lines)
    categorys = getProducts(lines)
    if sum(categorys.values()) == (card+cash):
        print "Date:", getDate(lines)
        print "Card:", card, "  Cash:",cash
        print "Refunds:", getNettoTotal(lines)-(card+cash), "  Total:", getNettoTotal(lines)
        print ""
        for k,v in categorys.items():
            print '{0:8.2f} kr - {1}'.format(v, k)
        if getNettoTotal(lines)-(card+cash) != 0:
            print "ALERT!!! Report has refunds!!! Check report for more details"
    else:
        print "There seems to be some problem with the parsing of the file"

def getPayments(lines):
    paymentsregex = re.compile("\s*Card\s+\(\d+\)\s+([\d,]+\.\d\d)\s+Cash\s+\(\d+\)\s+([\d,]+\.\d\d)\s*")
    card = 0
    cash = 0
    for l in lines:
        match = paymentsregex.match(l)
        if match:
            card += locale.atof(match.group(1))
            cash += locale.atof(match.group(2))
    return (card, cash)

def getDate(lines):
    dateregex = re.compile("\s*.+?\s+([A-Z][a-z]{2} \d\d?, \d{4}) \d\d:\d\d\s*")
    for l in lines:
        match = dateregex.match(l)
        if match:
            return match.group(1)

def getNettoTotal(lines):
    nettoregex = re.compile("\s*Net amount\s+([\d,]+\.\d\d)\s+[\d,]+\.\d\d\s+[\d,]+\.\d\d\s*")
    tot = 0
    for l in lines:
        match = nettoregex.match(l)
        if match:
            tot += locale.atof(match.group(1))
    return tot

def getProducts(lines):
    productregex = re.compile("(.+?)(,\s(.*?))?\s+([\d,]+)\s+([\d,]+\.\d\d)\s+[\d,]+\.\d\d\s+([\d,]+\.\d\d)")
    categorys = {}

    sumSold  = 0
    for l in lines:
        match = productregex.match(l)
        if match and match.group(5) == match.group(6):
            sumSold += locale.atof(match.group(5))
            category = match.group(1).strip()
            if category in categorys.keys():
                categorys[category] += locale.atof(match.group(5))
                #print match.group(1), match.group(3),match.group(4),match.group(5),(locale.atof(match.group(5))/locale.atoi(match.group(4)))
            else:
                categorys[category] = locale.atof(match.group(5))

    return categorys

main()
