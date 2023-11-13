from pprint import pprint


code = []
with open("test.txt", "r") as f:
    code = f.readlines()

for i in range(len(code)):
    code[i] = code[i].replace("\n", "")



index = 0
tab_count = code[0].count("   ")
pprint(tab_count)

while index < len(code):
    line = code[index]
    if "REPEAT" in line:
        tmp_index = index+1
        while True:
            if code[tmp_index] == str(str("   "*tab_count) + "END"):
                break
            else:
                pprint(code[tmp_index])
            tmp_index += 1
    
    index += 1