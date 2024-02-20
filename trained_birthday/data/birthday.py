from weather import weather 

fw = open('train_birthday.csv', 'w', encoding='utf-8')

with open('train_birthday.txt', 'r', encoding='utf-8') as f:
    fw.write('target|text\n')

    for l in f.readlines():
        if l.strip(): 
            fw.write('생일111_base|' + l)

            current_weather = weather()

            if current_weather == '맑음':
                with open('train_birthday_sunny.txt', 'r', encoding='utf-8') as sunny_file:
                    sunny_data = sunny_file.read()
                    fw.write('생일111_sunny|' + sunny_data)
            
            elif current_weather == '눈':
                with open('train_birthday_snow.txt', 'r', encoding='utf-8') as sunny_file:
                    sunny_data = sunny_file.read()
                    fw.write('생일111_snow|' + sunny_data)
            
if fw:
    fw.close()
