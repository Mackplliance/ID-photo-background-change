from ai_cutout import rmbg

if __name__ == '__main__':
    # 输入图片的路径
    input_img = '/home/aistudio/rmbg/photo/dong.jpg'

    # 证件照的背景颜色
    # color = "#FFFFFF" # 白色 (用于护照、签证、身份证等)
    color = "#438EDB" # 蓝色 (用于毕业证、工作证等)
    # color = "#FF0000" # 红色 (用于一些特殊的证件照)

    # 证件照的大小
    width = 295        # 一寸 (295像素 x 413像素)
    height = 413       # 一寸 (295像素 x 413像素)

    # 是否保持原图大小
    # size_opt = "不保持原图大小"
    size_opt = "保持原图大小"  # 如果选了这个会保持输入图片的大小，忽略上面的证件照的大小参数

    # color, width, height 这三个参数不影响框图，只会影响证件照的结果
    out_path, output_image_path = rmbg(input_img, color, width, height, size_opt)

    print('抠图后的图片: ', out_path)
    print('证件照: ', output_image_path)

    from PIL import Image
    import matplotlib.pyplot as plt

    # print('原图')
    image_input = Image.open(input_img)

    # print('抠图后的图片')
    image_rmbg = Image.open(out_path)

    # print('证件照')
    image_bg = Image.open(output_image_path)

    # 设定图片显示的大小
    fig, axs = plt.subplots(3, 1, figsize=(5, 15))

    # 在每个子图上显示一张图片
    axs[0].imshow(image_input)
    axs[0].axis('off')  # 不显示坐标轴
    axs[0].set_title(' original')

    axs[1].imshow(image_rmbg)
    axs[1].axis('off')  # 不显示坐标轴
    axs[1].set_title(' remove background')

    axs[2].imshow(image_bg)
    axs[2].axis('off')  # 不显示坐标轴
    axs[2].set_title('with background')

    # 调整子图之间的间距
    plt.tight_layout()

    # 显示画布
    plt.show()
