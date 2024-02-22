fw = open('train_lunar_new_year.csv', 'w', encoding='utf-8')
with open('train_lunar_new_year.txt', 'r', encoding='utf-8') as f:
    fw.write('target|text\n')
    for l in f.readlines():
        if (l == "") or (l == None) or (l == '\n'):
            continue
        fw.write('설날111|'+l)
        
if fw != None:
    fw.close()
