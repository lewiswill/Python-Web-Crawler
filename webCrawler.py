import urllib2
import pickle
import os

def buildDatabase(userURL):
    def webCrawler(seed):
        def grabPageLinks(page,crawled,toCrawl):
            crawled_URL=[]
            toCrawl_URL=[]
            for list in crawled:
                crawled_URL.append(list[0])
            for list in toCrawl:
                toCrawl_URL.append(list[0])
            response=urllib2.urlopen(page[0])
            html=response.read()
            depth=page[1]
            depth+=1
            links,pos,allFound=[],0,False
            while not allFound:
                tag=html.find("<a href=",pos)                
                if tag>-1:
                    href=html.find('"',tag+1)
                    endHref=html.find('"',href+1)
                    url=html[href+1:endHref]
                    if url[:8]=="https://":
                        if url[-1]=="/":
                            url=url[:-1]
                        if not url in links and not url in crawled_URL and not url in toCrawl_URL:
                            if depth<=MAX_DEPTH:
                                links.append([url,depth])
                    elif url[:7]=="http://":
                        if url[-1]=="/":
                            url=url[:-1]
                        if not url in links and not url in crawled_URL and not url in toCrawl_URL:
                            if depth<=MAX_DEPTH:
                                links.append([url,depth])
                    closeTag=html.find("</a>",tag)
                    pos=closeTag+1
                else:
                    allFound = True
            return links
        graph,toCrawl,crawled,urls={},[[seed,0]],[],[]
        while toCrawl:
            url=toCrawl.pop(0)
            crawled.append(url)
            print url[0]
            newLinks=grabPageLinks(url,crawled,toCrawl)
            for link in newLinks:
                toCrawl.append(link)
        for link in crawled:
            urls.append(link[0])
        print "------------------------------------------------------"
        print "\nAll the links Have been Crawled."
        print "------------------------------------------------------"
        return urls
    def urlScraper(urls):
        index={}
        for url in urls:
            response=urllib2.urlopen(url)
            html=response.read()
            pageText,pageWords="",[]
            containsScript=True
            finished=False
            while containsScript:
                startScript=html.find("<script",0)
                if startScript>-1:
                    endScript=html.find("</script>",startScript)
                    html=html[:startScript]+html[endScript+9:]
                else:
                    containsScript=False
            html=html[html.find("<body")+5:html.find("</body>")]
            while not finished:
                nextCloseTag=html.find(">")
                nextOpenTag=html.find("<")
                if nextOpenTag>-1:
                    content=" ".join(html[nextCloseTag+1:nextOpenTag].strip().split())
                    pageText=pageText+" "+content
                    html=html[nextOpenTag+1:]
                else:
                    finished=True
            for word in pageText.split():
                if word[-1]=="," or word[-1]==".":
                    word=word[:-1]
                word=word.lower()
                if word[0].isalnum() and len(word)>4:
                    if word not in pageWords:
                        pageWords.append(word)
            for word in pageWords:
                if word in index:
                    index[word].append(url)
                else:
                    index[word]=[url]
        print "Woof, All URLs are Scraped!"
        return index
    def urlGrapher(urls):
        def grabPageLinks(page):
            response=urllib2.urlopen(page)
            html=response.read()
            links=[]
            pos=0
            allFound=False
            while not allFound:
                tag=html.find("<a href=",pos)
                if tag>-1:
                    href=html.find('"',tag+1)
                    endHref=html.find('"',href+1)
                    url=html[href+1:endHref]
                    if url[:8]=="https://":
                        if url[-1]=="/":
                            url=url[:-1]
                        if not url in links:                            
                            links.append(url)
                    elif url[:7]=="http://":
                        if url[-1]=="/":
                            url=url[:-1]
                        if not url in links:
                            links.append(url)
                    closeTag=html.find("</a>",tag)
                    pos=closeTag+1
                else:
                    allFound=True
            return links
        def linksGraph(graph,link,url):
            if not links==[]:
                if url in graph:
                    graph[url].append(link)
                else:
                    graph[url]=[link]
            else:
                graph[url]=[]
        graph={}
        for i in urls:
            links=grabPageLinks(i)
            if not links==[]:
                for link in links:
                    linksGraph(graph,link,i)
            else:
                linksGraph(graph,links,i)
        print "------------------------------------------------------"
        print "URLs have been Graphed."
        return graph
    def pageRanker(graph, index):
        def computeRanks(graph):
            d=0.85
            numLoops=10
            ranks={}
            npages=len(graph)
            for page in graph:
                ranks[page]=1.0/npages
            for n in range(0,numLoops):
                newRanks={}
                for page in graph:
                    newRank=(1-d)/npages
                    for node in graph:
                        if page in graph[node]:
                            newRank=newRank+d*(ranks[node]/len(graph[node]))
                            newRanks[page]=newRank
                ranks=newRanks
            return ranks
        ranks=computeRanks(graph)
        print "------------------------------------------------------"
        print "Web Pages have been Ranked"
        return ranks
    seed=userURL.strip() #ensures whitespace is removed from start & end of the entered
    MAX_DEPTH=int(raw_input ('How deep do you want the Poodle webcrawler to search? >>> '))
    urls=webCrawler(seed)
    index=urlScraper(urls)
    graph=urlGrapher(urls)
    ranks=pageRanker(graph,index)
    print "------------------------------------------------------"
    print "\n **Database has been Created.**"
    print "------------------------------------------------------"
    return index,graph,ranks

# Contains Crawler, Scraper and returns values
def helpMenu():
    print "     ------------------------------------------------------------------"
    print "         **Poodle Database Help**"
    print "         Commands:"
    print "         '-build'	-Creates the POODLE database"
    print "         '-dump'	 	-Saves the POODLE database"
    print "         '-restore' 	-retrieves the previous POODLE database"
    print "         '-delete'  	-Deletes the current POODLE database"
    print "         '-print'	-Shows the POODLE database"
    print "         '-help'	  	-Shows this help information"
    print "     ------------------------------------------------------------------\n"
# Shows available Poodle Commands
def savePoodleDB(index,graph,rank):
    with open("index.txt","wb") as f:
        pickle.dump(index,f)
    with open("graph.txt","wb") as f:
        pickle.dump(graph,f)
    with open("ranks.txt","wb") as f:
        pickle.dump(rank,f)
    print "Poodle Database sucessfully Dumped!"
# Dumps the Index, Graph and Rank dictionaries as TEXT Files
def restoreDatabase():
    with open("index.txt","rb") as f:
        index=pickle.load(f)
    with open("graph.txt", "rb") as f:
        graph=pickle.load(f)
    with open("ranks.txt","rb") as f:
        rank=pickle.load(f)
    print "Database has been restored!"
    return index, graph, rank
# This function restores everything from the TEXT files
def deleteDatabase():
    indexFile="index.txt"
    graphFile="graph.txt"
    ranksFile="ranks.txt"
    if os.path.exists(indexFile):
        os.remove(indexFile)
    if os.path.exists(graphFile):
        os.remove(graphFile)
    if os.path.exists(ranksFile):
        os.path.remove(ranksFile)
    else:
        print "\nNo Stored Database to delete!\n"	
    print "\nPrevious Database has been cleared!\n"
# Delete contents of Poodle Database
def printDatabase(index,graph,rank):
	print "\n------------------------------------------------------"
	print "\nPoodle Database Index:\n"
	print index
	print "\n------------------------------------------------------"
	print "\n Poodle Database Ranks:\n"
	print ranks
	print "\n------------------------------------------------------"
	print "\n Poodle Database Graph:\n"
	print graph
	print "\n------------------------------------------------------"
# Prints the contents of index, graph and ranks dictionaries
def databaseSearch(rank,index,search):
    results={}
    for wordSearch in search.split():
        print "\n" + str(wordSearch)
        if wordSearch in index:
            for result in index[wordSearch]:
                results[result]=rank[result]
            for key in sorted(results):
                print "%s: %s" % (key, results[key])
        else:
                print "Searched Result, not found"
    print
# Searches through Poodle's stored files via else statement
def closePoodle():
    print "Woof! Poodle is now shutting down, Till Next Time!"
# Close Poodle Application
menuActive=True
while menuActive: # Menu loops until closed via -EXIT.
    option=raw_input("\n WOOF! What can POODLE fetch for you? ('-exit') to exit the application or ('-help') for poodle commands: ")
    option=option.lower()
    if option==("-build"):
        userURL=raw_input("Please provide a seed URL: ")
        if userURL[:7]=="http://":
            buildDatabase(userURL)
        else:
            userURL=raw_input("Dont forget the: http:// ")  

    elif option==("-print"):
        printDatabase(index,graph,ranks)
    elif option==("-dump"):
        savePoodleDB(index,graph,ranks)
    elif option==("-restore"):
        index,graph,ranks = restoreDatabase()
    elif option==("-delete"):
        deleteDatabase()
    elif option==("-help"):
        helpMenu()
    elif option==("-exit"):
        closePoodle()
        menuActive=False
    else:# Else serves as search function calling the databaseSearch function when not using a Menu command
        try:
            databaseSearch(ranks,index,option)
        except NameError:
            print "\nYou must Build or Restore a previous database before you can Search Poodle!\n"

