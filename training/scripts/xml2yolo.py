import os
import xml.etree.ElementTree as ET

def convert_xml_to_yolo(xml_dir, output_dir, class_names):
    os.makedirs(output_dir, exist_ok=True)
    
    for xml_file in os.listdir(xml_dir):
        if not xml_file.endswith('.xml'):
            continue
        
        tree = ET.parse(os.path.join(xml_dir, xml_file))
        root = tree.getroot()
        
        img_width = int(root.find('size/width').text)
        img_height = int(root.find('size/height').text)
        
        yolo_lines = []
        for obj in root.findall('object'):
            class_name = obj.find('name').text
            if class_name not in class_names:
                continue
            
            class_id = class_names.index(class_name)
            
            bbox = obj.find('bndbox')
            xmin = int(bbox.find('xmin').text)
            ymin = int(bbox.find('ymin').text)
            xmax = int(bbox.find('xmax').text)
            ymax = int(bbox.find('ymax').text)
            
            x_center = (xmin + xmax) / 2 / img_width
            y_center = (ymin + ymax) / 2 / img_height
            width = (xmax - xmin) / img_width
            height = (ymax - ymin) / img_height
            
            yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
        
        txt_file = os.path.join(output_dir, xml_file.replace('.xml', '.txt'))
        with open(txt_file, 'w') as f:
            f.write('\n'.join(yolo_lines))

if __name__ == '__main__':
    class_names = ['crazing', 'inclusion', 'patches', 'pitted_surface', 'rolled-in_scale', 'scratches']
    convert_xml_to_yolo('datasets/neu_det/Annotations', 'datasets/yolo/labels/train', class_names)