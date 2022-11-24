import socket
import urllib.parse




def readChunk(response, f, extName):
    
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

    TESTheader =  message.split(endHeader.encode())[0]
    body = message.split(endHeader.encode())[1]

    print("Header length :%d" %len(TESTheader))

    f.write(body)
    f.close()

# input website name
#### code here
# http://www-net.cs.umass.edu/wireshark-labs/Wireshark_Intro_v8.1.docx
print("Enter host address (eg. www.example.com)\n")
urlInput = input('')
print("Enter extension name  (eg. html, pdf, doc...))\n")
extName = input('')
# url = http://www.example.com/index.html
url = urllib.parse.urlparse(urlInput)

# host : www.example.com
target_host = url.hostname

# path : /index.html
target_path = url.path

#scheme : http
target_scheme = url.scheme


print("Enter host address (eg. www.example.com)\n")
urlInput2 = input('')
print("Enter extension name  (eg. html, pdf, doc...))\n")
extName2 = input('')
# url = http://www.example.com/index.html
url2 = urllib.parse.urlparse(urlInput2)

# host : www.example.com
target_host2 = url2.hostname

# path : /index.html
target_path2 = url2.path

#scheme : http
target_scheme2 = url2.scheme



print('Host:%s\nPath:%s\nScheme:%s\n'% (target_host,target_path,target_scheme))

target_port = 80  # create a socket object 
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
client.setblocking(False)
# connect the client 
client.connect_ex((target_host,target_port))  

client.connect_ex((target_host2,target_port))
# send some data 
# request = "GET /index.html/ HTTP/1.1\r\nHost:%s\r\n\r\n" % target_host

request1 = "GET %s HTTP/1.1\r\nHost:%s\r\n\r\n" %(target_path,target_host)

request2 = "GET %s HTTP/1.1\r\nHost:%s\r\n\r\n" %(target_path2,target_host2)

# request = "GET / HTTP/1.1\r\nHost:%s\r\n\r\n" %target_host
# header = "HEAD / HTTP/1.1\r\nHost:%s\r\n\r\n" %target_host



client.sendall(request1.encode())  

# receive some data 
# tim so byte can receive trong nay content-length chunk transfer
# response = client.recv(4096)  



if target_path == '':
    filename = 'index.html'
else :
    filename = target_path.replace('/','_') + '.' + extName

f = open(filename , "wb")

response = b''
readChunk(response, f, extName)

client.sendall(request2.encode())  

# receive some data 
# tim so byte can receive trong nay content-length chunk transfer
# response = client.recv(4096)  



if target_path == '':
    filename = 'index.html'
else :
    filename = target_path.replace('/','_') + '.' + extName

f = open(filename , "wb")

response = b''
readChunk(response, f, extName)


client.close()