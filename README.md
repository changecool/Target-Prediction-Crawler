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
1. Chrome browser
   This crawler uses Chrome browser. Please download chromedriver.exe corresponding to your browser version and move it to C:\Windows folder.
2. Install dependencies
   ```python -m pip install -r requirements.txt```
3. Run
    ``` python python Targets_Prediction.py --input "__your smiles.csv path__" --output "__your output file path__" ```
    ```# Example: python targets.py --input "C:\Users\tcm\Desktop\SMILES.csv" --output "C:\Users\tcm\Desktop\targets.csv"```
4. Examples of input and output csv files
   Please use standardized column names in the csv file for easy reading by the crawler program. Sample files can be found in the "example" folder.
5. Description
   The basic code of this crawler comes from https://github.com/fmayr/DHC_TargetPrediction. Due to the passage of several years and the successive updates of various databases, the original code can no longer run properly. Therefore, we have made significant modifications based on it to meet current needs.

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
   本爬虫使用的Chrome浏览器，请自行下载浏览器版本对应的chromedriver.exe，并将其移动至C盘Windows文件夹下。
2. 安装依赖环境
    ``` python -m pip install -r requirements.txt ```
3. 运行
    ```python python Targets_Prediction.py --input "__your smiles.csv path__" --output "__your output file path__"
    #  例子：python targets.py --input "C:\Users\tcm\Desktop\SMILES.csv" --output "C:\Users\tcm\Desktop\targets.csv"```
4. 输入和输出csv文件举例
   请规范csv文件里面列名，以方便爬虫程序读取相关内容，示例文件请在“例子”文件夹查看。
5. 说明
   本爬虫基础代码来自于https://github.com/fmayr/DHC_TargetPrediction ，由于时隔数年，各大数据库相继更新，原代码已不可正常运行，故在其基础上做了大量修改已满足当前需要。
