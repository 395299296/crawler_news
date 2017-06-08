import tensorflow as tf
from PIL import Image
import numpy
import random
import os

x_data = []
y_data = []
train_data_x = []
train_data_y = []
test_data_x = []
test_data_y = []

IMAGE_HEIGHT = 53
IMAGE_WIDTH = 130  
CAPTCHA_LEN = 4
alphabet = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
ALPHABET = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
char_set = ALPHABET + alphabet
CHAR_SET_LEN = len(char_set)
input_path = 'verifies'

# 把彩色图像转为灰度图像（色彩对识别验证码没有什么用）  
def convert2gray(img):  
    if len(img.shape) > 2:  
        gray = numpy.mean(img, -1)  
        # 上面的转法较快，正规转法如下  
        # r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]  
        # gray = 0.2989 * r + 0.5870 * g + 0.1140 * b  
        return gray  
    else:  
        return img

def text2vec(text):  
    text_len = len(text)  
    if text_len != CAPTCHA_LEN:  
        raise ValueError('验证码长度4个字符')  
   
    vector = numpy.zeros(CAPTCHA_LEN*CHAR_SET_LEN)  
    for i, c in enumerate(text):
        k = ord(c)-ord('a')
        if k >= 0:
            k += len(ALPHABET)
        else:
            k = ord(c)-ord('A')
        idx = i * CHAR_SET_LEN + k
        vector[idx] = 1
    return vector

# 生成一个训练batch  
def get_next_batch(batch_size=128):
    global train_data_x
    global train_data_y
    perm = numpy.arange(len(train_data_x))
    numpy.random.shuffle(perm)
    train_data_x = train_data_x[perm]
    train_data_y = train_data_y[perm]
    batch_x = train_data_x[0:batch_size]
    batch_y = train_data_y[0:batch_size]
   
    return batch_x, batch_y

for parent, dirnames, filenames in os.walk(input_path):
    for x in filenames:
        basenames = os.path.splitext(x)
        basenames = basenames[0].split('_')
        captcha_image = Image.open(os.path.join(parent, x))
        captcha_image = numpy.array(captcha_image)
        captcha_image = convert2gray(captcha_image)
        captcha_image = captcha_image.flatten() / 255 # (image.flatten()-128)/128  mean为0
        x_data.append(captcha_image)
        y_data.append(text2vec(basenames[0].upper()))

train_data_x = numpy.array(x_data[0:900])
train_data_y = numpy.array(y_data[0:900])
test_data_x = numpy.array(x_data[900:1000])
test_data_y = numpy.array(y_data[900:1000])

####################################################################
# 申请占位符 按照图片
X = tf.placeholder(tf.float32, [None, IMAGE_HEIGHT*IMAGE_WIDTH])
Y = tf.placeholder(tf.float32, [None, CAPTCHA_LEN*CHAR_SET_LEN])
keep_prob = tf.placeholder(tf.float32) # dropout

# 定义CNN
def crack_captcha_cnn(w_alpha=0.01, b_alpha=0.1):
    # 将占位符 转换为 按照图片给的新样式
    x = tf.reshape(X, shape=[-1, IMAGE_HEIGHT, IMAGE_WIDTH, 1])

    #w_c1_alpha = np.sqrt(2.0/(IMAGE_HEIGHT*IMAGE_WIDTH)) #
    #w_c2_alpha = np.sqrt(2.0/(3*3*32))
    #w_c3_alpha = np.sqrt(2.0/(3*3*64))
    #w_d1_alpha = np.sqrt(2.0/(8*32*64))
    #out_alpha = np.sqrt(2.0/1024)

    # 3 conv layer
    w_c1 = tf.Variable(w_alpha*tf.random_normal([3, 3, 1, 32])) # 从正太分布输出随机值
    b_c1 = tf.Variable(b_alpha*tf.random_normal([32]))
    conv1 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(x, w_c1, strides=[1, 1, 1, 1], padding='SAME'), b_c1))
    conv1 = tf.nn.max_pool(conv1, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv1 = tf.nn.dropout(conv1, keep_prob)

    w_c2 = tf.Variable(w_alpha*tf.random_normal([3, 3, 32, 64]))
    b_c2 = tf.Variable(b_alpha*tf.random_normal([64]))
    conv2 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv1, w_c2, strides=[1, 1, 1, 1], padding='SAME'), b_c2))
    conv2 = tf.nn.max_pool(conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv2 = tf.nn.dropout(conv2, keep_prob)

    w_c3 = tf.Variable(w_alpha*tf.random_normal([3, 3, 64, 64]))
    b_c3 = tf.Variable(b_alpha*tf.random_normal([64]))
    conv3 = tf.nn.relu(tf.nn.bias_add(tf.nn.conv2d(conv2, w_c3, strides=[1, 1, 1, 1], padding='SAME'), b_c3))
    conv3 = tf.nn.max_pool(conv3, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')
    conv3 = tf.nn.dropout(conv3, keep_prob)

    # Fully connected layer
    w_d = tf.Variable(w_alpha*tf.random_normal([7*17*64, 1024]))
    b_d = tf.Variable(b_alpha*tf.random_normal([1024]))
    dense = tf.reshape(conv3, [-1, w_d.get_shape().as_list()[0]])
    dense = tf.nn.relu(tf.add(tf.matmul(dense, w_d), b_d))
    dense = tf.nn.dropout(dense, keep_prob)

    w_out = tf.Variable(w_alpha*tf.random_normal([1024, CAPTCHA_LEN*CHAR_SET_LEN]))
    b_out = tf.Variable(b_alpha*tf.random_normal([CAPTCHA_LEN*CHAR_SET_LEN]))
    out = tf.add(tf.matmul(dense, w_out), b_out)
    #out = tf.nn.softmax(out)
    return out

# 训练
def train_crack_captcha_cnn():
    output = crack_captcha_cnn()
    #loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(output, Y))
    loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(logits=output, labels=Y))
    # 最后一层用来分类的softmax和sigmoid有什么不同？
    # optimizer 为了加快训练 learning_rate应该开始大，然后慢慢衰
    optimizer = tf.train.AdamOptimizer(learning_rate=0.001).minimize(loss)

    predict = tf.reshape(output, [-1, CAPTCHA_LEN, CHAR_SET_LEN])
    max_idx_p = tf.argmax(predict, 2)
    max_idx_l = tf.argmax(tf.reshape(Y, [-1, CAPTCHA_LEN, CHAR_SET_LEN]), 2)
    correct_pred = tf.equal(max_idx_p, max_idx_l)
    accuracy = tf.reduce_mean(tf.cast(correct_pred, tf.float32))

    saver = tf.train.Saver()
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        step = 0
        while True:
            batch_x, batch_y = get_next_batch(64)
            _, loss_ = sess.run([optimizer, loss], feed_dict={X: batch_x, Y: batch_y, keep_prob: 0.75})
            print(step, loss_)

            # 每100 step计算一次准确率
            if step % 100 == 0:
                batch_x_test, batch_y_test = get_next_batch(100)
                acc = sess.run(accuracy, feed_dict={X: batch_x_test, Y: batch_y_test, keep_prob: 1.})
                print(step, acc)
                # 如果准确率大于50%,保存模型,完成训练
                if acc > 0.8:
                    saver.save(sess, "./model/model", global_step=step)
                    break
            step += 1

train_crack_captcha_cnn()