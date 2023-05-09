# Target-Prediction-Crawler
1. Supported databases:
   * Swiss Target Prediction (STP): [SwissTargetPrediction](http://www.swisstargetprediction.ch/)
   * Similarity Ensemble Approach (SEA): [SEA Search Server --- 海搜索服务器 (bkslab.org)](https://sea.bkslab.org/)
   * SuperPred: https://prediction.charite.de/index.php
   * Other databases can be added by adding corresponding crawler functions.
2. Current features:
   * Automatically crawl predicted target data.
   * Automatic target filtering based on the prediction values of each dataset, such as STP's Probability* value.
   * Automatically obtain standard names of targets from uniprot database.
# Installation and usage of the crawler
1. Chrome Browser
   * This crawler uses the Chrome browser. Please download the chromedriver.exe corresponding to your browser version and move it to the C:\Windows folder.
2. Standardize input and output CSV files
   * Please standardize the column names in the CSV file to facilitate the crawling program to read relevant content. Please refer to the two CSV sample files in the library.
3. Install dependency environment
```Python
python -m pip install -r requirements.txt
```
4. Set target screening threshold values 
   * Please set STP, SEA, and SuperPred database thresholds respectively in lines 87, 179, and 254 of Targets_Prediction.py file.
```Python
## Retain target data from SwissTargetPrediction database with "Probability*" greater than or equal to 0.6.
df = df[df['prob'] >= 0.6]

## Retain target data from SEA database with "P-value" less than 0.05.
df = df[df['prob'] < 0.05]

## Retain target data in the SuperPred database with a "Probability" greater than or equal to 60%.
df['prob'] = df['prob'].str.rstrip('%').astype('float') / 100
df = df[df['prob'] >= 0.6]
```
5.Run 
```Python
python python Targets_Prediction.py --input "__your smiles.csv path__" --output "__your output file path__"
# Example: python targets.py --input "C:\Users\tcm\Desktop\SMILES.csv" --output "C:\Users\tcm\Desktop\targets.csv"
```
6.Explanation:
   * The basic code of this crawler comes from https://github.com/fmayr/DHC_TargetPrediction . Due to updates of various databases over several years, original code cannot run properly anymore; therefore, a lot of modifications have been made based on it to meet current needs.

# Target-Prediction-Crawler
1. 支持数据库：
   * Swiss Target Prediction (STP): [SwissTargetPrediction](http://www.swisstargetprediction.ch/)
   * Similarity Ensemble Approach (SEA): [SEA Search Server --- 海搜索服务器 (bkslab.org)](https://sea.bkslab.org/)
   * SuperPred: https://prediction.charite.de/index.php
   * 其他数据库同理，可自行添加爬虫函数
2. 现有功能：
   * 自动爬取预测的靶点数据
   * 自动靶点筛选，根据各数据对应的预测值，如STP的Probability*值
   * 自动从uniprot数据库获取靶点标准名

# 爬虫的安装和使用
1. Chrome浏览器
   * 本爬虫使用的Chrome浏览器，请自行下载浏览器版本对应的chromedriver.exe，并将其移动至C盘Windows文件夹下。
2. 规范输入和输出csv文件
   * 请规范csv文件里面列名，以方便爬虫程序读取相关内容，请参看库中两个csv示例文件。
3. 安装依赖环境
```Python
python -m pip install -r requirements.txt
```
4. 靶点筛选阈值设置
   * 请在Targets_Prediction.py文件中lines87,179,254分别设置STP, SEA, SuperPred三个数据库的阈值。
```Python
## Retain target data from SwissTargetPrediction database with "Probability*" greater than or equal to 0.6.
df = df[df['prob'] >= 0.6]

## Retain target data from SEA database with "P-value" less than 0.05.
df = df[df['prob'] < 0.05]

## Retain target data in the SuperPred database with a "Probability" greater than or equal to 60%.
df['prob'] = df['prob'].str.rstrip('%').astype('float') / 100
df = df[df['prob'] >= 0.6]
```
5. 运行
```Python
python python Targets_Prediction.py --input "__your smiles.csv path__" --output "__your output file path__"
# Example: python targets.py --input "C:\Users\tcm\Desktop\SMILES.csv" --output "C:\Users\tcm\Desktop\targets.csv"
```
6. 说明
   * 本爬虫基础代码来自于https://github.com/fmayr/DHC_TargetPrediction ，由于时隔数年，各大数据库相继更新，原代码已不可正常运行，故在其基础上做了大量修改已满足当前需要。
