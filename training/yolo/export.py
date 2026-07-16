from ultralytics import YOLO

def export_yolo(model_path, format='onnx'):
    model = YOLO(model_path)
    model.export(format=format)

if __name__ == '__main__':
    export_yolo('models/yolo/best.pt')