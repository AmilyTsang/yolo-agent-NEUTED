from app.utils.image_utils import read_image, convert_to_rgb, normalize_image, image_to_pil
from app.core.logging import logger

class Preprocessor:
    def process(self, image_path):
        logger.info(f"开始图像预处理: {image_path}")
        
        image = read_image(image_path)
        if image is None:
            raise ValueError(f"无法读取图像: {image_path}")
        
        rgb_image = convert_to_rgb(image)
        normalized_image = normalize_image(rgb_image)
        pil_image = image_to_pil(rgb_image)
        
        logger.info("图像预处理完成")
        
        return {
            'original': image,
            'rgb': rgb_image,
            'normalized': normalized_image,
            'pil': pil_image,
            'shape': rgb_image.shape
        }