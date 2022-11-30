import socket
import urllib.parse
import re #find regular expressions
import os #for folder creation
import concurrent.futures
from os import path #get base name of url file
import sys #For exception handling exit code

#Global variables
FORMAT = 'utf-8'
target_port = 80
TIMEOUT = 3600

#Add http scheme to the url if missing
def addHTTP(urlInput):
    scheme = "http://"
    if urlInput.find(scheme) == -1:
        urlInput = scheme + urlInput
    return urlInput

#Name the file for download
def createFileName(urlInput):
    url = urllib.parse.urlparse(urlInput)

    target_host = url.hostname
    target_path = url.path
    target_baseName = path.basename(urlInput)

    if target_path == '' or target_path == '/':
            return str(target_host) + '_index.html'
    else:
            return str(target_host) + '_' + target_baseName 

def getLink(html):
    listLink = re.findall('"([^"]*)"', html)
    return listLink

def checkSTR(listLink):
    checkedList = []
    for i in listLink:
        if (i.find('.pdf') != -1) or (i.find('.doc') != -1) or (i.find('.txt') != -1) or (i.find('.ppt') != -1) or (i.find('.tex') != -1):
            checkedList.append(i)
    print(checkedList)
    return checkedList    

#Get all header bytes
def checkType(client):

    endHead = False
    endPart = '\r\n\r\n' #end of head
    header = bytes()
    chunk = bytes()

    while True:

        if endHead == True:
            # return header
            return header
        else:
            # if not -> read a byte until get the endPart
            buff = 1
        try:
            chunk = client.recv(buff)
        except Exception as e:
            print("Failed to reader header: %s" %e)
        header += chunk
        #Find end head
        if header.find(endPart.encode(FORMAT)) != -1:
                endHead = True

#Check url for handling modes
def checkUrl(urlInput):
    #Split space character (multi connections)
    listUrlInput = urlInput.split(' ')

    if len(listUrlInput) > 1:
        return 4 #This return option multi connections

    else:
        #Add http header if missing
        urlInput = addHTTP(urlInput)
        #Parse the link into path and host
        urlParse = urllib.parse.urlparse(urlInput)
        #Initialize path
        path = urlParse.path

        #Define html
        if path == '' or path == '/index.html' or path == '/index.htm' or path == '/':
            return 1 

        #Define folder
        elif path[-1] == '/':
            return 3 #Return folder request

        #Define extension file
        elif path.find('.'):
            return 2 #Return other extension option
    
    return 0

#Get content length
def getContentLength(header):
    endline = b'\r\n'
    partHeader = header.split(endline) #Separate each line
    
    contentLength = bytes()
    #find the content length line in each lines
    for i in partHeader:
        if i.find(b"Content-Length: ") != -1:
            contentLength = i
    #Split the content length line
    contentLength = contentLength.split(b' ')
    #return the content length
    return int(contentLength[1])



"""Handling requests"""
#Case input link is html/htm file
def processHTML(urlInput):
    # format url
    url = urllib.parse.urlparse(urlInput)

    target_host = url.hostname
    target_path = url.path
    target_scheme = url.scheme
    #print in terminal link
    print('Host:%s\nPath:%s\nScheme:%s\n' %
          (target_host, target_path, target_scheme))

    

    # create socket obj TCP
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #set time out for client
        client.settimeout(TIMEOUT)
    except socket.timeout as e:
        print("Timeout!: %s" %e)
    except socket.error as e:
        print("Failed to create socket: %s" %e)
    else:
        # connect to host server
        try:
            client.connect((target_host, target_port))
        except socket.gaierror as e:
            print("Address-related error connecting to server: %s" %e)
        except socket.error as e: 
            print ("Connection error: %s" %e) 

        # create request to host server
        request = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % (target_host)

        # send request
        client.sendall(request.encode(FORMAT)) #use sendall to avoid sending less than needed
        
        filename = createFileName(urlInput)

        # initialized file and write byte
        file = open(filename, "wb")

        # check type ( content-length or chunked )
        # return header of file
        header = checkType(client)

        #Execute if type is content length
        if header.find(b'Content-Length') != -1:
            print("Downloading file %s: " + filename)
            readContentLength(file, client, 1)
        #Execute if type is chunked
        elif header.find(b'chunked') != -1:
            print("Downloading file %s: " + filename)
            readChunked(file, client)
        else:
            print("File inst content-length or chunked")
            client.close()
            exit()
        #close connection
        client.close()

#For handling other files (not html/htm)
def processExtFile(urlInput):
    # format url
    url = urllib.parse.urlparse(urlInput)
    
    target_host = url.hostname
    target_path = url.path

    # create socket obj
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Set time out time for socket
        client.settimeout(TIMEOUT)   
    except socket.timeout as e:
        print("Timeout!: %s" %e)
    except socket.error as e:
        print("Failed to create socket: %s" %e)
        sys.exit("Closing the program...")
    else:
        # connect to host server
        try:
            client.connect((target_host, target_port))
        except socket.gaierror as e:
            print("Address-related error connecting to server: %s" %e)
        except socket.error as e: 
            print ("Connection error: %s" %e) 
            sys.exit("Closing the program...")

        # create request to host server
        request = "GET %s HTTP/1.1\r\nHost:%s\r\n\r\n" % (urlInput, target_host)

        # send request
        client.sendall(request.encode(FORMAT))

        # initialized file name
        filename = createFileName(urlInput)

        # initialized file
        file = open(filename, "wb")

        # check type (content-length or chunked)
        # return header of file
        header = checkType(client)

        if header.find(b'Content-Length') != -1:
            print("Downloading file %s: " % filename)
            readContentLength(file, client, 2)
        elif header.find(b'chunked') != -1:
            print("Downloading file %s: " % filename)
            readChunked(file, client)
        else:
            print("File ins't content-length or chunked")
            client.close()
            exit()
        #Close connection    
        client.close()

#Download files in folder
def processFolder(urlInput):
    #process url
    url = urllib.parse.urlparse(urlInput)
    
    target_host = url.hostname
    target_path = url.path
    #Get the basename for file name
    target_baseName = path.basename(path.basename(path.normpath(target_path)))

    #get the name before the final /
    folderName = str(target_host) + '_' + target_baseName
    #create folder to save files

    os.makedirs(folderName, exist_ok = True) #Download even if folder exists
    print("Folder created")

    print("Choose a mode to donwload files: \n1. Default\n2. Multi Request")
    
    
    while True:
        try:
            temp = int(input())
        except ValueError as e:
            print("Invalid input, must be 1 or 2: %s" %e)
        else:
            if temp == 1:
                processFolder_default(target_host, urlInput, folderName)
                break
            elif temp == 2:
                processFolder_multiReq(target_host, urlInput, folderName)
                break
            else:
                print("Input out of range, try again!")

#Download files from folder using single requests
def processFolder_default(target_host, urlInput, folderName):
    # create socket obj TCP
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Set time out time for socket
        client.settimeout(TIMEOUT)
         
    except socket.timeout as e:
        print("Connection Timeout!: %s" %e)
        sys.exit("Closing the program...")
    except socket.error as e:
        print("Failed to create socket: %s" %e)
        sys.exit("Closing the program...")
    else:
        # connect to host server
        try:
            client.connect((target_host, target_port))
        except socket.gaierror as e:
            print("Address-related error connecting to server: %s" %e)
            client.close()
            sys.exit("Closing the program...")
        except socket.error as e: 
            print ("Connection error: %s" %e) 
            client.close()
            sys.exit("Closing the program...")

        # request HTML of folder
        requestHTML = "GET %s HTTP/1.1\r\nHost:%s\r\n\r\n" % (
            urlInput, target_host)

        # send request to get html
        client.sendall(requestHTML.encode(FORMAT))

        # recv html
        html = client.recv(20000)

        # return string in " " of html
        listLink = getLink(html.decode())

        # return the correct file of the listlink
        fileList = checkSTR(listLink)

        client.close()

        single_req(fileList,target_host,target_port,urlInput, folderName)


def processFolder_multiReq(target_host, urlInput, folderName):
    # create socket obj
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Set time out time for socket
        client.settimeout(None)     
    except socket.timeout as e:
        print("Timeout!: %s" %e)
    except socket.error as e:
        print("Failed to create socket: %s" %e)

    else:
        # connect to host server
        try:
            client.connect((target_host, target_port))
        except socket.gaierror as e:
            print("Address-related error connecting to server: %s" %e)
            client.close()
            sys.exit("Closing the program...")
        except socket.error as e: 
            print ("Connection error: %s" %e) 
            client.close()
            sys.exit("Closing the program...")

        # request HTML of folder
        requestHTML = "GET %s HTTP/1.1\r\nHost:%s\r\n\r\n" % (
            urlInput, target_host)

        # send request to get html
        client.sendall(requestHTML.encode(FORMAT))

        # recv html
        html = client.recv(20000)

        # return string in " " of html
        listLink = getLink(html.decode())

        # return the correct file of the listlink
        fileList = checkSTR(listLink)

        multi_req(client, urlInput, fileList, target_host, folderName)


#Create new socket every iterations
def single_req(fileList ,target_host ,target_port, urlInput, folderName):
    for i in fileList:
        # initialized new socket for each file in list
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        # connect to server
        client.connect((target_host,target_port))  

        requestFile = "GET %s%s HTTP/1.1\r\nHost:%s\r\n\r\n" %(urlInput,i,target_host)
        
        client.send(requestFile.encode(FORMAT))

        #create files at correct directory
        file = open(folderName + '/' + i,'wb')
        
        # check type ( content-length or chunked )
        # return header of file
        header = checkType(client)

        if header.find(b'Content-Length') != -1:
            print("Downloading file %s: " % i)
            readContentLength(file, client, 2)
        elif header.find(b'chunked') != -1:
            print("Downloading file %s: " % i)
            readChunked(file, client)
        else:
            print("File inst content-length or chunked")
            client.close()
            sys.exit("Closing the program...")
        
        client.close()

#Create 1 socket to receive all
def multi_req(client, urlInput, fileList, target_host, folderName):
    # run the first to the end file of the list
    for i in fileList:
        # each loop send a request to the server
        requestFile = "GET %s%s HTTP/1.1\r\nHost:%s\r\nConnection: keep-alive\r\n\r\n" % (urlInput, i, target_host)
        client.sendall(requestFile.encode(FORMAT))

    # read a folder for 1 time
    readFolder_multiReq(client, fileList, folderName)


def readFolder_multiReq(client, fileList, folderName):
    chunk = bytes()
    header = bytes()
    contentLength = int()

    for i in fileList:
        #Change the space character to _
        i = i.replace('%20', '_')
        file = open(folderName + '/' + i, 'wb')

        getHeader = False
        breakOut = False
        message = bytes()
        print("Downloading file %s: " % i)
        while True:
            if breakOut == True:
                break
            if getHeader == False:        
                header = checkType(client)
                contentLength = getContentLength(header)
                getHeader = True

            while len(message) < contentLength:
                if contentLength - len(message) > 0 and contentLength - len(message) <  20000:
                    try:
                        chunk = client.recv(contentLength - len(message))
                    except socket.error as e:
                        print("Error in downloading files 1: %s" %e)
                        sys.exit("Closing the program...")
                    else:
                        file.write(chunk)
                        message += chunk
                else:
                    try:
                        chunk = client.recv(20000)
                    except socket.error as e:
                        print("Error in downloading files 2: %s" %e)
                        sys.exit("Closing the program...")
                    else:
                        file.write(chunk)
                        message += chunk

                if len(message) == contentLength:
                    print("Downloading file %s succesfully : " % i)
                    breakOut = True
                    break

#handle each server requests
def service(urlInput):
    choice = checkUrl(urlInput)

    urlInput = addHTTP(urlInput)
    if choice == 1:
        return processHTML(urlInput)
    elif choice == 2:
        return processExtFile(urlInput)
    elif choice == 3:
        return processFolder(urlInput)
    else:
        return "\nUnable to download file\n"

#Đang dùng mỗi socket cho 1 web
def processMultiConnection(urlInput):
    # split links into list of link
    URLS = urlInput.split(' ')

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the load operations and mark each future with its URL
        for url in URLS:
            try:
                executor.submit(service, url)
            except Exception as e:
                print("%s failed to download: %s" %(url, e))

def readContentLength(file, client, mode):
    # message : hold all data
    message = bytes()
    # chunk : hold data per recv
    chunk = bytes()

    '''
    Check lại receive đủ content length
    '''
    # print("Downloading file(s)...\n")
    while True:
        # recv data from server
        try:
            chunk = client.recv(20000)
        except socket.error as e:
            print("Error in downloading files: %s" %e)
            sys.exit("Closing the program...")
        else:
            # mode 1 : file is html
            if mode == 1:
                message += chunk
                break
            # when recv = 0 then out the while
            if not chunk:
                break

            # mode 2 : file is extension file
            else:
                message += chunk

    # write file
    file.write(message)

    print("Download file sucessfully\n")

    # close file
    file.close()


def readChunked(file, client):
    message = bytes()
    
    # print("Downloading file(s)...\n")

    while True:

        # read the len chunk in hex size
        lenChunkInHex = bytes()
        endLine = '\r\n'

        # read until \r\n in chunk
        while lenChunkInHex.find(endLine.encode(FORMAT)) == -1:
            lenChunkInHex += client.recv(1)

        # split the \r\n out of chunk
        size = len(lenChunkInHex) #size of length of chunk
        # omit r\n\
        lenChunkInHex = lenChunkInHex[:size-2].decode()

        # change the hex-len-chunk to base 10
        lenChunk = int(lenChunkInHex, 16)

        # check is end of file
        if lenChunk == 0:
            break


        chunk = client.recv(lenChunk)
        #If client failed to receive the chunk length
        #receive the missing bytes
        while len(chunk) < lenChunk:
            chunk += client.recv(lenChunk - len(chunk))

        file.write(chunk)

        message += chunk
        #Receive \r\n (not used)
        passItem = client.recv(2)

    print("Download file sucessfully\n")

    file.close()



def main():
    print("Enter host address: ")
    urlInput = input()

    choice = checkUrl(urlInput)

    # choice = 1 -> process html
    # choice = 2 -> process file extension
    # choice = 3 -> process folder
    # choice = 4 -> process mutiple links
    # choice = 0 -> link error
    urlInput = addHTTP(urlInput)

    if choice == 1:
        processHTML(urlInput)
    elif choice == 2:
        processExtFile(urlInput)
    elif choice == 3:
        processFolder(urlInput)
    elif choice == 4:
        processMultiConnection(urlInput)
    else:
        print("URL input is not valid\n Please try again") 

if __name__ == "__main__":
    main()
   
''''
test case : 
- content-length : http://web.stanford.edu/class/cs224w/slides/08-GNN-application.pdf ( done )
- chunked : http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx ( done )
- folder : http://web.stanford.edu/class/cs143/handouts/ ( done ) ( both case )
- multi connect : http://web.stanford.edu/dept/its/support/techtraining/techbriefing-media/Intro_Net_91407.ppt http://gaia.cs.umass.edu/wireshark-labs/alice.txt
'''

