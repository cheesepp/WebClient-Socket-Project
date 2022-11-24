import socket
import re

def getLink(html):
    listLink = re.findall('"([^"]*)"',html)
    return listLink

def checkSTR(listLink):
    checkedList = []
    for i in listLink:
        if i.find('.pdf') != -1:
            checkedList.append(i)
    print(checkedList)
    return checkedList


def readChunk(file, extName):
    
    #Đọc header thiếu (ban đầu 113) nên cộng thêm thành 357 ->đúng
    endHeader = "\r\n\r\n"

    message = bytes()
    chunk = bytes()

    while True:
        chunk = client.recv(20000)
        if extName == 'html':
            message += chunk
            print(chunk)
            break
        if not chunk:
            break
        else:
            message += chunk
            print(chunk)
            file.write(chunk)

    # TESTheader =  message.split(endHeader.encode())[0]
    # body = message.split(endHeader.encode())[1]

    # print("Header length :%d" %len(TESTheader))

    # file.write(body)
    # file.close()

def multiReq(fileList):
    
    for i in fileList:
        requestFile = "GET /class/cs224w/slides/%s HTTP/1.1\r\nHost:%s\r\nConnection: Keep-Alive\r\n\r\n" %(i,target_host)
        client.send(requestFile.encode())

        file = open(i,"wb")
        readChunk(file,'pdf')




target_host = "web.stanford.edu"
target_port = 80  # create a socket object 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  


# connect the client 
client.connect((target_host,target_port))  



# send some data 
# request = "GET /index.html/ HTTP/1.1\r\nHost:%s\r\n\r\n" % target_host

requestHTML = "GET http://web.stanford.edu/class/cs224w/slides/ HTTP/1.1\r\nHost:%s\r\n\r\n" %target_host


client.send(requestHTML.encode())

html = client.recv(20000)

f = open('index.html' , 'wb')

f.write(html)

listLink = getLink(html.decode())

print(listLink)

fileList  = checkSTR(listLink)

multiReq(fileList)



