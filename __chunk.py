import socket

def endHeaderDetect(response,endHead):
    while True:
        endPart = '\r\n\r\n'
    # check end of header 
        if endHead == True:
            return response
        else :
            # if not -> read a byte until get the endPart 
            buff = 1
    
        chunk = client.recv(buff)
    
        response += chunk

        if response.find(endPart.encode()) != -1:
            endHead = True

def readBody(response,f):
    while True:
        # read the len chunk in hex size
        lenChunkInHex = bytes()
        endLine = '\r\n'

        while lenChunkInHex.find(endLine.encode()) == -1:
            lenChunkInHex += client.recv(1)

        size = len(lenChunkInHex) 

        lenChunkInHex = lenChunkInHex[:size-2].decode()

        # change the hex-len-chunk to base 10
        lenChunk = int(lenChunkInHex , 16)

        if lenChunk == 0:
            break
        print("Chunk length : %d" %lenChunk)


        chunk = client.recv(lenChunk)

        f.write(chunk)

        response += chunk

        passItem = client.recv(2)



target_host = "www.httpwatch.com"
target_port = 80  # create a socket object 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  


# connect the client 
client.connect((target_host,target_port))  


# send some data 
# request = "GET /index.html/ HTTP/1.1\r\nHost:%s\r\n\r\n" % target_host

request = "GET http://www.httpwatch.com/httpgallery/chunked/chunkedimage.aspx HTTP/1.1\r\nHost:%s\r\n\r\n" %target_host


client.send(request.encode())

header = bytes()
body = bytes()

f = open('hihi.aspx' , "wb")

response = endHeaderDetect(header,False)
print("Header :%s" %(response))

readBody(body,f)

client.close()