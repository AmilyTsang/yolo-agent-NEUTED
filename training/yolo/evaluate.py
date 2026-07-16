from ultralytics import YOLO

def evaluate_yolo(model_path, data_path):
    model = YOLO(model_path)
    results = model.val(data=data_path)
    print(results)

if __name__ == '__main__':
    evaluate_yolo('models/yolo/best.pt', 'datasets/yolo/data.yaml')