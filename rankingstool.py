#!/usr/bin/python

import argparse
import re
import operator

# old ranking and new ranking
parser = argparse.ArgumentParser(description='Args to specify old and new rankings files and which comparisons to run')
parser.add_argument('-o','--old-rankings', help="Path to previous quarter's ranking info file", required=True)
parser.add_argument('-n','--new-rankings', help="Path to current quarter's ranking info file", required=True)
parser.add_argument('-p','--print-html', action='store_true', help="Flag to output the current rankings in a pretty HTML table", required=False)
parser.add_argument('-s','--sort-by', default='change', choices=['rank','change'], help="'rank': sorts by ranking, 'change': sorts by biggest change (default)", required=False)

def make_dict(rankingfile):
    """takes the raw data and munges it into a rank number:name dict"""
    rankingdict = {}
    count = 0
    with open (rankingfile) as raw:
        for line in raw:
            leaguename = re.search("[A-Za-z]{3,}", line)
            if leaguename:
                count = count + 1
                rankingdict[line[:-1]] = count
    return rankingdict

def get_new(oldrankdict,newrankdict,quiet=False):
    newteams = set(newrankdict.keys()) - set(oldrankdict.keys())
    if quiet == False:
        if len(newteams) == 0:
            print "\nNo new entries"
        else:
            print "\nNew entries:"
            while newteams:
                team = newteams.pop()
                print "{0}: {1}".format(newrankdict[team], team)
    else:
        newentries = []
        while newteams:
            newentries.append(newteams.pop())
        return newentries

def get_dropouts(oldrankdict,newrankdict):
    dropouts = set(oldrankdict.keys()) - set(newrankdict.keys())
    if len(dropouts) == 0:
        print "\nNo dropouts"
    else:
        print "\nTeams dropping out:"
        while dropouts:
            team = dropouts.pop()
            print team

def get_changes(oldrankdict,newrankdict,sort='change', html=False):
    """compares the dicts and prints a nice report"""
    changes = {}
    print "\nRanking changes:"
    sorted_kv = sorted(newrankdict.iteritems(), key=operator.itemgetter(1))
    for k,v in sorted_kv:
        if k in oldrankdict and v != oldrankdict[k]:
            lastq = oldrankdict[k]
            thisq = v
            changes[k] = lastq-thisq
    if sort == 'rank' and not html:
        for k,v in sorted_kv:
            if k in changes:
                print "{0}: {1} was {2} ({3})".format(v, k, oldrankdict[k], changes[k])
    if sort == 'change' and not html:
        sorted_changes = sorted(changes.iteritems(), key=operator.itemgetter(1), reverse=True)
        for k,v in sorted_changes:
            print "{0}: {1} was {2} ({3})".format(newrankdict[k], k, oldrankdict[k], v)
    if html:
        newentries = get_new(oldrankdict, newrankdict, quiet=True)
        print "<table>"
        print "<tr class=header><th class=rank>Rank</th><th class=team>League</th><th class=change>+/-</th></tr>"
        for k,v in sorted_kv:
            if v < 41:
                rank = 'rank d1'
            elif v < 61:
                rank = 'rank d2'
            else:
                rank = 'rank'
            if k in changes:
                if changes[k] > 9:
                    print """<tr class="bigrise"><td class="{0}">{1}</td><td class="team">{2}</td><td class="change">+{3}</td></tr>""".format(rank,v,k,changes[k])
                elif changes[k] > 4:
                    print """<tr class="smallrise"><td class="{0}">{1}</td><td class="team">{2}</td><td class="change">+{3}</td></tr>""".format(rank,v,k,changes[k])
                elif changes[k] > 0:
                    print """<tr class="tinyrise"><td class="{0}">{1}</td><td class="team">{2}</td><td class="change">+{3}</td></tr>""".format(rank,v,k,changes[k])
                elif changes[k] < -9:
                    print """<tr class="bigdrop"><td class="{0}">{1}</td><td class="team">{2}</td><td class="change">{3}</td></tr>""".format(rank,v,k,changes[k])
                elif changes[k] < -4:
                    print """<tr class="smalldrop"><td class="{0}">{1}</td><td class="team">{2}</td><td class="change">{3}</td></tr>""".format(rank,v,k,changes[k])
                elif changes[k] < 0:
                    print """<tr class="tinydrop"><td class="{0}">{1}</td><td class="team">{2}</td><td class="change">{3}</td></tr>""".format(rank,v,k,changes[k])
            elif k in newentries:
                    print """<tr class="newentry"><td class="{0}">{1}</td><td class="team">{2}</td><td class="change">*</td></tr>""".format(rank,v,k)
            else:
                print """<tr><td class="{0}">{1}</td><td class="team">{2}</td><td class="change">=</td></tr>""".format(rank,v,k)
        print "</table>"
        get_dropouts(oldrankdict, newrankdict)
 

     
if __name__ == "__main__":
    args = parser.parse_args()
    old = make_dict(args.old_rankings)
    new = make_dict(args.new_rankings)
    if args.print_html:
        get_changes(old,new,html=args.print_html)
    else:
        get_new(old,new)
        get_dropouts(old,new)
        get_changes(old,new,args.sort_by)
