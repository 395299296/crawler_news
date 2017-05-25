from PIL import Image

im = Image.open("images/1.jpg")
#(将图片转换为8位像素模式)
im.convert("P")

#颜色直方图
his = im.histogram()
values = {}

for i in range(256):
    values[i] = his[i]

for j,k in sorted(values.items(),key=lambda x:x[1],reverse = True)[:30]:
    print(j,k)

im2 = Image.new("P",im.size,255)

for x in range(im.size[0]):
    for y in range(im.size[1]):
        pix = im.getpixel((x,y))
        if values[pix[0]] > 20 and values[pix[0]] < 100:
            im2.putpixel((x,y),pix[0])

im2.show()