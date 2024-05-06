'''
try:
    contents = []
      
    while True:
        contents.append(str(input()))
          
# if the input is not-integer, just print the list
except:
    print(contents)




'''



     

import fileinput
contents = []


p=str(input("Enter file name: "))
 
with fileinput.FileInput(files=(p), mode='r') as input:
    for line in input:
        
      contents.append(line)

cx=0
d=0
x=0
y=0

for i in range(len(contents)):
  
  if contents[i]=='cx q[2], q[3];\n':
    cx=cx+1
   
  elif contents[i]=='delay(1) q[2];\n':
    d=d+1
  elif contents[i]=='x q[2];\n':   
    x=x+1
  elif contents[i]=='y q[2];\n':
    y=y+1
  else:
    i=i+1 
print(x,y,cx,d)
if d>10:
         
    a=abs(cx-d)
    b=abs(d-x) 
    c=abs(d-y) 
    k=abs(cx-x)
    e=abs(x-y) 
    
    if (cx-d==1 and cx>1) or (cx-d==-1 and cx>1) or (cx==d and cx>1):
        print("Type(1) Malicious Code")          
    elif (abs(x-d)==1 and x>1) or  (x==d and x>1):  
        print("Type(2) Malicious Code")
    elif  (abs(y-d)==1 and y>1) or  (y==d and y>1):  
        print("Type(3) Malicious Code")   
    elif a==b or (cx==k and k==x):
        print("Research Required, Possibly Malicious")
    elif a==c or (cx==k and k==y):
        print("Research Required, Possibly Malicious")
   
    elif k==e  :
        print("(1)Further investigation required.")
     
    elif k==0 or e==0  :
        print("(2)Further investigation required.")
    
    else:
        print("Maybe Secure")
       
else:        
    print ("Secure Code")