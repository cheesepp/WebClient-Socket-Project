import socket
import urllib.parse
import re


def checkUrl(urlInput):

    listUrlInput = urlInput.split(' ')

    if len(listUrlInput) > 1:
        return 4
    else:

        scheme = 'http://'

        if urlInput.find(scheme) == -1:
            urlInput = scheme + urlInput

        urlParse = urllib.parse.urlparse(urlInput)

        path = urlParse.path

        # define html
        if path == '' or path == '/index.html' or path == '/':
            return 1

        # define folder
        elif path[-1] == '/':
            return 3

        # define extension file
        elif path.find('.'):
            return 2

        return 0

def getLink(html):
    listLink = re.findall('"([^"]*)"', html)
    return listLink

def checkSTR(listLink):
    checkedList = []
    for i in listLink:
        if (i.find('.pdf') != -1) or (i.find('.doc') != -1) or (i.find('.txt') != -1) or (i.find('.ppt') != -1):
            checkedList.append(i)
    print(checkedList)
    return checkedList

def processHTML(urlInput):

    # format url
    url = urllib.parse.urlparse(urlInput)
    target_host = url.hostname
    target_path = url.path
    target_scheme = url.scheme
    print('Host:%s\nPath:%s\nScheme:%s\n' %
          (target_host, target_path, target_scheme))

    # initialize port
    target_port = 80

    # create socket obj
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to host server
    client.connect((target_host, target_port))

    # create request to host server
    request = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % (target_host)

    # send request
    client.sendall(request.encode())

    # initialized file name
    filename = str(target_host)
    listPart = filename.split('.')
    if listPart[0] == 'www':
        filename = listPart[1] + '.html'
    else:
        filename = listPart[0] + '.html'

    # initialized file
    file = open(filename, "wb")

    # check type ( content-length or chunked )
    # return header of file
    header = checkType(client)

    if header.find(b'Content-Length') != -1:
        readContentLength(file, client, 1)
    elif header.find(b'chunked') != -1:
        readChunked(file, client)

    client.close()

def processEXTFILE(urlInput):
    # format url
    url = urllib.parse.urlparse(urlInput)
    target_host = url.hostname
    target_path = url.path
    target_scheme = url.scheme
    print('Host:%s\nPath:%s\nScheme:%s\n' %
          (target_host, target_path, target_scheme))

    # initialize port
    target_port = 80

    # create socket obj
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to host server
    client.connect((target_host, target_port))

    # create request to host server
    request = "GET %s HTTP/1.1\r\nHost:%s\r\n\r\n" % (urlInput, target_host)

    # send request
    client.sendall(request.encode())

    # initialized file name
    filename = target_path.replace('/', '_')

    # initialized file
    file = open(filename, "wb")

    # check type ( content-length or chunked )
    # return header of file
    header = checkType(client)

    if header.find(b'Content-Length') != -1:
        readContentLength(file, client, 2)
    elif header.find(b'chunked') != -1:
        readChunked(file, client)
    else:
        print("File inst content-length or chunked")

def processFOLDER(urlInput):
    url = urllib.parse.urlparse(urlInput)
    target_host = url.hostname
    target_path = url.path
    target_scheme = url.scheme
    print('Host:%s\nPath:%s\nScheme:%s\n' %
          (target_host, target_path, target_scheme))

    print("Choos system to donwload folder : \n1. Default\n2. Multi Request")
    temp = int(input())
    if temp == 1:
        processFOLDER_default(target_host, urlInput)
    elif temp == 2:
        processFOLDER_multireq(target_host, urlInput)
    else:
        print("Syntax error")

def processFOLDER_default(target_host, urlInput):
    # initialize port
    target_port = 80

    # create socket obj
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to host server
    client.connect((target_host, target_port))

    # request HTML of folder
    requestHTML = "GET %s HTTP/1.1\r\nHost:%s\r\n\r\n" % (
        urlInput, target_host)

    # send request to get html
    client.sendall(requestHTML.encode())

    # recv html
    html = client.recv(20000)

    # return string in " " of html
    listLink = getLink(html.decode())

    # return the correct file of the listlink
    fileList = checkSTR(listLink)

    client.close()

    single_req(fileList,target_host,target_port,urlInput)

def processFOLDER_multireq(target_host, urlInput):
    # initialize port
    target_port = 80

    # create socket obj
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to host server
    client.connect((target_host, target_port))

    # request HTML of folder
    requestHTML = "GET %s HTTP/1.1\r\nHost:%s\r\n\r\n" % (
        urlInput, target_host)

    # send request to get html
    client.sendall(requestHTML.encode())

    # recv html
    html = client.recv(20000)

    # return string in " " of html
    listLink = getLink(html.decode())

    # return the correct file of the listlink
    fileList = checkSTR(listLink)

    multi_req(client, urlInput, fileList, target_host)

def processMULTI_CONNECT(urlInput):
    # split links into list of link
    listurl = urlInput.split(' ')
    
    for url in listurl:
        choice = checkUrl(url)
        if choice == 1:
            processHTML(url)
        elif choice == 2:
            processEXTFILE(url)
        elif choice == 3:
            processFOLDER(url)



def single_req(fileList,target_host,target_port,urlInput):
    for i in fileList:
        # initialized new socket for each file in list
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        
        #  connect to server
        client.connect((target_host,target_port))  

        requestFile = "GET %s%s HTTP/1.1\r\nHost:%s\r\n\r\n" %(urlInput,i,target_host)
        
        client.send(requestFile.encode())

        file = open(i,'wb')
        
        # check type ( content-length or chunked )
        # return header of file
        header = checkType(client)

        if header.find(b'Content-Length') != -1:
            readContentLength(file, client, 2)
        elif header.find(b'chunked') != -1:
            readChunked(file, client)
        else:
            print("File inst content-length or chunked")

def multi_req(client, urlInput, fileList, target_host):
    # run the first to the end file of the list
    for i in fileList:
        # each loop send a request to the server
        requestFile = "GET %s%s HTTP/1.1\r\nHost:%s\r\nConnection: keep-alive\r\n\r\n" % (
            urlInput, i, target_host)
        client.sendall(requestFile.encode())

    # read a folder for 1 time
    readFolder_multireq(client, fileList)

def readFolder_multireq(client, fileList):
    message = bytes()
    chunk = bytes()

    while True:
        chunk = client.recv(20000)
        print("Dowloading file...")
        message += chunk

        # print(chunk)
        if not chunk:
            break

    part = message.split(b"HTTP")

    index = 0
    for i in part:
        if i == b'':
            continue
        i = b'HTTP' + i
        f = open(fileList[index], 'wb')
        f.write(i)
        print("Download file %d success" % (index+1))
        index += 1

def readContentLength(file, client, mode):
    # message : hold all data
    message = bytes()

    # chunk : hold data per recv
    chunk = bytes()

    while True:
        # recv data from server
        chunk = client.recv(20000)

        # mode 1 : file is html
        if mode == 1:
            print("Dowloanding file...")
            message += chunk
            # print(chunk)
            break

        # when recv = 0 then out the while
        if not chunk:
            break

        # mode 2 : file is extension file
        else:
            print("Dowloanding file...")
            message += chunk
            # print(chunk)

    # write file
    file.write(message)
    print("Downfile sucess\n")

    # close file
    file.close()

def readChunked(file, client):
    message = bytes()
    while True:

        # read the len chunk in hex size
        lenChunkInHex = bytes()
        endLine = '\r\n'

        # read until \r\n in chunk
        while lenChunkInHex.find(endLine.encode()) == -1:
            lenChunkInHex += client.recv(1)

        # split the \r\n out of chunk
        size = len(lenChunkInHex)
        lenChunkInHex = lenChunkInHex[:size-2].decode()

        # change the hex-len-chunk to base 10
        lenChunk = int(lenChunkInHex, 16)

        # check is end of file
        if lenChunk == 0:
            break

        print("Chunk length receive : %d" % lenChunk)

        chunk = client.recv(lenChunk)

        while len(chunk) < lenChunk:
            chunk += client.recv(lenChunk-len(chunk))

        file.write(chunk)

        message += chunk

        passItem = client.recv(2)

def checkType(client):
    endHead = False
    endPart = '\r\n\r\n'
    header = bytes()
    while True:

        if endHead == True:
            return header
        else:
            # if not -> read a byte until get the endPart
            buff = 1

        chunk = client.recv(buff)

        header += chunk

        if header.find(endPart.encode()) != -1:
            endHead = True



if __name__ == '__main__':
    print('Enter host address :')
    urlInput = input()

    choice = checkUrl(urlInput)

    # choice = 1 -> process html
    # choice = 2 -> process file extension
    # choice = 3 -> process folder
    # choice = 4 -> process mutiple links
    # choice = 0 -> link error

    if choice == 1:
        processHTML(urlInput)
    elif choice == 2:
        processEXTFILE(urlInput)
    elif choice == 3:
        processFOLDER(urlInput)
    elif choice == 4:
        processMULTI_CONNECT(urlInput)
    else:
        print("URL input isnt legal")
