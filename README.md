# theol-downloader
theol平台文件探测、批量获取信息、批量下载
# 文件id/文件名加密逻辑
GB2312编码的hex加密，再把其中数字字母按以下逻辑替换：0->A , 1->B , 2->C ......
# form_fast1.py
生成信息表格，包含文件名大小、url
# analysis_2.py
探测文件id分布范围，以便提高检测效率
# fanal.py
集合以上功能，并有一个根据字典批量下载的模块
