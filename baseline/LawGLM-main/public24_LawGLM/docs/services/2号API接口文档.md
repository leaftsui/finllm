## 2 号API接口函数 根据公司代码，获得该公司对应的基本信息

``` 
def get_company_info_service_by_code(company_code:  Annotated[str, "公司代码", True],need_fields: Annotated[str, "需要返回的字段列表 例如 [公司名称, 公司代码, 主营业务]", True]):
    """
   	根据公司代码, 公司股票代码，获得该公司对应的基本信息。
    """

``` 

### 例子： 
### 1
##### 输入
``` 
company_code="688579",need_fields=[]
``` 
#### 输出 
``` 
{"公司名称": "山大地纬软件股份有限公司", "公司简称": "山大地纬", "英文名称": "Dareway Software Co., Ltd.", "关联证券": "", "公司代码": "688579", "曾用简称": "", "所属市场": "上交所科创板", "所属行业": "软件和信息技术服务业", "成立日期": "1992-11-19", "上市日期": "2020-07-17", "法人代表": "郑永清", "总经理": "史玉良", "董秘": "张建军", "邮政编码": "250200", "注册地址": "山东省济南市章丘区文博路1579号", "办公地址": "山东省济南市章丘区文博路1579号", "联系电话": "0531-58215506", "传真": "0531-58215555", "官方网址": "www.dareway.com.cn", "电子邮箱": "ir@dareway.com.cn", "入选指数": "", "主营业务": "XXX", "机构简介": "XXXX", "每股面值": "1.0", "首发价格": "8.12", "首发募资净额": "28001.446", "首发主承销商": "民生证券股份有限公司"}

```
### 2
#### 输入

company_code="301012",need_fields=['公司名称']
``` 
输出
{"公司名称": "江苏扬电科技股份有限公司"}
``` 


### 3
#### 输入
``` 
company_code="688579",need_fields=['公司名称']
``` 

#### 输出
``` 
{"公司名称": "山大地纬软件股份有限公司"}
``` 
