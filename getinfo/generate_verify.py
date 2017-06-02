import os
import time

output_path = 'data'

def generate_code(number):
    number = number * 1000
    c1 = chr(65 + int(number*1+1)%25)
    c2 = chr(65 + int(number*2+3)%25)
    c3 = chr(65 + int(number*3+5)%25)
    c4 = chr(65 + int(number*5+7)%25)
    return c1 + c2 + c3 + c4

if __name__ == '__main__':
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    item_list = []
    # for x in range(1,10001):
    #     ts = time.time()
    #     code = generate_code(ts)
    #     tmpstr = str(ts) + '\t' + code
    #     item_list.append(tmpstr)
    #     time.sleep(0.003)
    for parent, dirnames, filenames in os.walk('images'):
        for x in filenames:
            basenames = os.path.splitext(x)
            basenames = basenames[0].split('_')
            tmpstr = basenames[1] + '\t' + basenames[0].upper()
            item_list.append(tmpstr)

    with open(os.path.join(output_path, 'code.txt'), 'w') as f:
        f.write('\n'.join(item_list))