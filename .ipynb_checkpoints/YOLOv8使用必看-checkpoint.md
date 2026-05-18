## ultralytics库更新记录（官方YOLOv8、YOLO11）
- 已有8.0系列版本 左边目录文件：[ultralytics - 8.0.](https://github.com/ultralytics/ultralytics/tree/v8.0.85)

- 2024.11.06 本镜像更新为最新稳定版本YOLOv8 - [ultralytics - v8.3.27版本](https://github.com/ultralytics/ultralytics/tree/v8.3.27)

- 该镜像新增 官方YOLO11 模型 - 训练 验证 推理 改进 一体化，详情见左边目录文件：YOLO11使用必看.md

## 只需要执行两行代码，一键运行 YOLOv8 项目

YOLOv8官方项目地址：https://github.com/ultralytics/ultralytics

---

## **全网最简单上手的一键运行 **官方YOLOv8** 项目运行流程**🚀️

不需要配置环境，一键训练即可

---

### 第一步：打开控制台，命令行输入

```python
cd ultralytics-8.3.27
```

### 第二步：训练代码，命令行输入

```python
python train_v8.py --cfg ultralytics/cfg/models/v8/yolov8.yaml
```
命令输入参考如下：
![](https://picx.zhimg.com/80/v2-bc6740fd4007473714f61390dbec9e88_720w.png)
即可以开始训练了

YOLOv8 训练 显示如下：

![](https://picx.zhimg.com/80/v2-8067c1c7d679787ced4ec1dceac43ac6_720w.png)


如果想终止训练，可以使用 快捷键：Ctrl+C，终止

查看显存使用情况 输入：watch -n 1 nvidia-smi

加速访问的学术资源地址 输入: source /etc/network_turbo

runs目录输出的内容即为:训练完成的内容


### 第三步：推理代码，输入

```python
python predict.py
```

---

### 关于数据集

默认使用coco128数据集作为验证，有需要可以换成自己的数据集路径进行训练

可以根据自己使用的数据集进行修改 train_v8.py 里面的参数 ： data='coco128.yaml', 修改为对应的自己数据集的yaml文件

其他数据集可以参考ultralytics/cfg/datasets/ 该目录下

### 训练代码参数
修改数据集路径和网络模型权重路径

--cfg 后面的参数接不同的网络配置文件

--weights 后面的参数接官方权重名称 如 yolov8n.pt
