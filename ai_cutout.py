import sys
import os
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw
import onnxruntime as ort
from skimage import io

# 添加库的路径
sys.path.append("/home/aistudio/external-libraries")


# ONNX模型处理类
class BriaRMBG_ONNX:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(model_path)

    def __call__(self, input_tensor):
        input_name = self.session.get_inputs()[0].name
        output = self.session.run(None, {input_name: input_tensor})
        return output


# 图片预处理函数
def preprocess_image(im: np.ndarray, model_input_size: list) -> np.ndarray:
    # 确保图像为三通道
    if im.shape[2] == 4:  # 如果是四通道图片，转为三通道
        im = cv2.cvtColor(im, cv2.COLOR_BGRA2BGR)
    elif len(im.shape) < 3:  # 如果是单通道图片，转为三通道
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)

    # 调整图像大小
    im = cv2.resize(im, (model_input_size[0], model_input_size[1]), interpolation=cv2.INTER_LINEAR)
    # 转换数据类型和归一化
    im = im.astype(np.float32) / 255.0
    # 平均值和标准差调整
    mean = [0.5, 0.5, 0.5]
    std = [10.0, 1.0, 1.0]
    im -= mean
    im /= std
    # 扩展维度以符合模型输入要求
    return im[np.newaxis, :, :, :]


# 图片后处理函数
def postprocess_image(result: np.ndarray, im_size: list) -> np.ndarray:
    result = result[0]
    ma = np.max(result)
    mi = np.min(result)
    result = (result - mi) / (ma - mi) * 255
    result = result.astype(np.uint8)
    result = cv2.resize(result, (im_size[1], im_size[0]), interpolation=cv2.INTER_LINEAR)
    return result


# 添加背景色函数
def add_background_to_image(input_image_path, output_image_path, background_color, out_size=None):
    image = Image.open(input_image_path)
    image = image.convert('RGBA')  # 转换为RGBA以保持透明度处理
    if out_size is None:
        out_size = image.size
    out_image = Image.new('RGB', out_size, background_color)
    out_image.paste(image, (0, 0), image)
    out_image.save(output_image_path)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')  # 移除前面的'#'字符
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))  # 转换为整数的RGB元组


# 主函数

def rmbg(input_image_path, background_color, out_size_w, out_size_h, size_opt):
    # 对输入路径和文件进行处理，得到输出路径等信息
    match = re.search(r'^(.*\/)([^.]+)(\..+)$', input_image_path)
    path, filename, ext = match.groups()
    output_image_path = os.path.join(path, filename + "_final.png")  # 直接指定为PNG格式

    # 读取并处理图片
    image = Image.open(input_image_path)
    image.convert('RGBA').save(output_image_path, 'PNG')  # 保存为PNG格式

    # 加载和使用ONNX模型
    net = BriaRMBG_ONNX("/home/aistudio/rmbg/onnx/model.onnx")
    orig_im = np.array(image)
    orig_im_size = orig_im.shape[:2]
    processed_image = preprocess_image(orig_im, [1024, 1024])
    processed_image = np.transpose(processed_image, (0, 3, 1, 2))  # 转换为ONNX格式

    result = net(processed_image)
    result_image = postprocess_image(result[0][0], orig_im_size)

    # 结合去除背景和添加新背景的步骤
    pil_im = Image.fromarray(result_image)
    no_bg_image = Image.new("RGBA", pil_im.size, (0, 0, 0, 0))
    no_bg_image.paste(image, mask=pil_im)
    background_color_rgb = hex_to_rgb(background_color)  # 将十六进制颜色代码转换为RGB元组
    final_image = Image.new('RGB', pil_im.size, background_color_rgb)
    final_image.paste(no_bg_image, (0, 0), no_bg_image)
    final_image.save(output_image_path, 'PNG')  # 保存最终图片为PNG格式

    return output_image_path
