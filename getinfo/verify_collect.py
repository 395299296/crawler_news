from urllib.request import urlopen
import os, time

output_path = 'images'
url = 'http://mp.weixin.qq.com/mp/verifycode?cert=%s'

if __name__ == '__main__':
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for x in range(0,28):
        print('save verify code img:', x)
        ts = time.time()
        data = urlopen(url % ts).read()
        with open(os.path.join(output_path, '_%s.jpg'%ts), 'wb') as f:
            f.write(data)
        time.sleep(1.1)