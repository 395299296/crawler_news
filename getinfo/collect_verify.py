from urllib.request import urlopen
import os, time

output_path = 'images'
url = 'http://mp.weixin.qq.com/mp/verifycode?cert=%s'

if __name__ == '__main__':
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for x in range(1,10001):
        print('save verify code img:', x)
        data = urlopen(url % time.time()).read()
        with open(os.path.join(output_path, '%d.jpg'%x), 'wb') as f:
            f.write(data)
        time.sleep(0.05)