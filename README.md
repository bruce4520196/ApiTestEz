# ApiTestEz

### 介绍
让API测试变得简单。<br>
ApiTestEz（以下简称EZ）主要提供以下3方面的核心功能：<br>
1. `ez.cfg`提供多个层级的配置环境；
2. 完成对http请求的封装，测试人员只用关注*Request*参数的传递，和*Response*的断言；
3. 引入反序列化模型断言。

---
### 安装教程

    pip install ApiTestEz

---

### Quick Start

---
#### 最小测试项目

       |-- EzTestDemo
           |-- <project_name>
           |   |-- test_whatever.py
           |   |-- ez.cfg (optional: module priority)
           |-- settings
           |-- project.cfg

 `test_whatever.py`

```python
import unittest

from api_test_ez.core.case import UnitCase
  
  
class SomeTest(UnitCase):
  
   def beforeRequest(self):
       self.request.url = "http://www.baidu.com"
  
   def test_something(self):
       assert self.response.status_code == 200
  
  
if __name__ == '__main__':
   unittest.main()

```

---
#### 完整项目

    |-- EzTestDemo
      |-- <project_name>
      |   |-- <test_api_dir>
      |   |   |-- test_whatever.py
      |   |   |-- ez.cfg (optional: package priority)
      |   |   |-- model.py (optional)
      |   |-- ez.cfg (optional: module priority)
      |-- settings
      |-- project.cfg
      |-- ez.cfg (optional: project priority)
      |-- <resource> (optional)
          |-- <case_files> (optional)

 *`project.cfg`*为项目标识，它告诉EZ项目根目录和项目*`settings.py`*存放位置。<br>
 *`setting.py`*提供项目初始化设置项，如**`log`**、**`report`**配置。<br>
 *`ez.cfg`*与*`settings`*的区别在于，*`ez.cfg`*提供业务相关的配置，如*`http`*的*`headers`*、*`case_filepath`*（用例存放目录）、*`auto_request`*（自动完成请求）开关等，你还可以在里面放置业务需要的特殊变量，这些变量将会存放在*self.request.meta*中。它包含了多个层级`['case', 'package', 'module', 'project', 'command', 'default']`，优先级一次递减。<br>
 关于*`setting.py`*和*`ez.cfg`*支持的配置详情后述。<br>
 <br>
 *ez.cfg*是EZ框架的核心功能之一。下面，通过使用ez.cfg，我们来完成一个简单的请求。<br>

 `ez.cfg`

```ini
[HTTP] 
url = http://www.baidu.com
```
        
 `test_whatever.py`
        
 ```python
 import unittest

 from api_test_ez.core.case import UnitCase


 class SomeTest(UnitCase):

     def test_something(self):
         assert self.response.status_code == 200


 if __name__ == '__main__':
     unittest.main()
  ```
---
#### EZ和[ddt](https://github.com/datadriventests/ddt)一起工作
   EZ支持`ddt`
   假设我们有多个接口需要测试。（这里我们使用一些fake api：https://dummyjson.com/products/<page> ）。
   我们得到10个需要测试的接口 https://dummyjson.com/products/1 ~ https://dummyjson.com/products/10 。它们将返回10种不同型号的手机信息。<br>
   显然，这10个接口在测试过程中很大程度上是相似的，我们希望编写同一个类来完成对这10个接口的测试。<br>
   首先，我们需要一份用例文件，它负责储存用例编号、接口信息、期望结果等内容。EZ支持多种格式的用例文件：*Excel*、*YAML*、*JSON*、*Pandas*、*HTML*、*Jira*等，它使用[tablib](https://tablib.readthedocs.io/en/stable/)读取用例文件。
   这里我们使用*Excel*作为存储用例文件。<br>
   <br>
`case.xlsx`<br>

   
| case_name | path         |
|-----------|--------------|
| TC0001    | /products/1  |
| TC0002    | /products/2  |
| TC0003    | /products/3  |
| TC0004    | /products/4  |
| TC0005    | /products/5  |
| TC0006    | /products/6  |
| TC0007    | /products/7  |
| TC0008    | /products/8  |
| TC0009    | /products/9  |
| TC0010    | /products/10 |


   我们将请求的域名放在`ez.cfg`中以便切换测试环境时统一管理，同时将用例路径存放在`ez.cfg`中，以便EZ发现用例。<br>

```ini
[CASE]
case_filepath = /<some path>/case.xlsx

[HTTP]
host = https://dummyjson.com
```
   > *在`ez.cfg`中，HTTP method默认为GET。*
   
在`test_whatever.py`中，现阶段不做出改变，我们将在后面的介绍中深入认识[断言](#断言)。
```python
 import unittest

 from api_test_ez.core.case import UnitCase


 class SomeTest(UnitCase):

     def test_something(self):
         assert self.response.status_code == 200


 if __name__ == '__main__':
     unittest.main()
```
   >*在test文件中，我们可以用过`__casefile__`显式指定用例路径，这在同一个文件夹下有多个.py测试代码的情况下很有用。但对项目来说不推荐这种做法。例：* 
 
```python
from api_test_ez.core.case import UnitCase


class SomeTest(UnitCase):
   __casefile__ = "/<some path>/case.xlsx"
```

---

---
### EZ中的组件

在EZ中，每个测试实例拥有两个实例变量：`self.request`和`self.response`。同时，`request`充当着上下文的作用，它存放`http`相关属性和`meta`两类属性。而`response`则提供请求响应数据断言等作用。
1. **Request**
---
   - PIPELINE

   EZ目前只支持了基于`unittest`的封装，在EZ中可以使用`unittest`的所有特性。EZ在`setUp`和`tearDown`的基础上，提供了3个额外的hook方法：`beforeRequest`、`doRequest`、`afterRequest`。<br>
   它们的执行顺序如下：
   ```
   |-- setUp
   |   |-- beforeRequest
   |   |   |-- doRequest  (if __autoRequest__ == 'on')
   |   |   |-- afterRequest  (if __autoRequest__ == 'on')
   |   |-- testMethod
   |-- tearDown
   ```

   `doRequest`和`afterRequest`仅在*自动请求*（即`__autoRequest__ == 'on'`）时被调用。而`doRequest`可以显式调用，同样的，`__autoRequest__`也可以在测试代码中显式指定。<br>

---
   - `beforeRequest`

      通常我们在`beforeRequest`中完成对请求数据的封装。<br>
       1. 显式指定url
     ```python
        def beforeRequest(self):
            self.request.url = "http://www.baidu.com"
     ```
      2. 在请求前需要通过另一个请求得到需要传递的参数
     ```python
        def beforeRequest(self):
            resp = self.request.http.get('https://somehost.com/login').json()
            self.body = {'token': resp.get('token')}
     ```
      
   - `afterRequest`
        
        在`afterRequest`中，我们完成对请求响应数据的清洗或对请求环境的还原。<br>
        1. 清除登录态
     ```python
        def afterRequest(self):
            self.request.http.get('https://somehost.com/logout')
     ```
        2. 当用户登录失败，跳过测试用例
     ```python
        def afterRequest(self):
            if self.response.bean.login_status == 0:
                self.skipTest("Login fail, skip test method.")
     ```
     > *response的bean属性将json数据转化为bean对象。*
   - `doRequest`
        
        `doRequest`完成了对请求的封装，它接受一个Request参数，并返回EzResponse对象。通常我们只需要决定**显式**或**自动**调用它。<br>
         但如果你需要重写它，请遵循`request`传递参数，并返回`EzResponse`对象的规则。这将在后续的断言中很有用。
   - `initRequest`

        `initRequest`是一个特殊的hook函数，它在测试对象初始化时被加载。<br>
        它负责找到测试用例集中每个用户的测试数据、完成对`ddt`数据的加载、并将加载完成的用例数据（包含从`ez.cfg`中加载的数据）传递给`request`完成初始化。

---
   - `request`参数。

        1. http相关属性:<br> 
        `http`: 存放`Http`实例对象。<br>
        `owner`: 标识该`request`对象属于哪个用例。<br>
        `url`: 请求的url。<br>
        `host`: 请求的host。<br>
        `path`: 请求的path。<br>
        `method`: 请求的method。<br>
        `body`: 请求的body。<br>
        2. meta:<br>
        `meta`: 除去以上http相关属性，其他来自于**用例文件**、**`ez.cfg`**的字段都将储存在`meta`中。<br>
                `meta`对象具有两个属性`bean`和`data`，`bean`属性将字典转化为bean对象；`data`将config属性按字典返回。

---
2. **Response**
    
    在测试类中，除了`request`EZ还提供了`response`，它是`EzResponse`的实例。`response`在`requests.Response`的基础上提供了3个额外的属性和方法：
    - `bean`属性: 将字典转化为bean对象。这样我们能像访问属性一样访问字典。例：
        ```python
        self.response.json()
        # {"name": "Bruce", "favorite": [{"category": "sports", "name": "basketball"}, {"category": "sports", "name": "football"}]}
        resp_bean = self.response.bean
        resp_bean.name
        # "Bruce"
        resp_bean.favorite[0].category
        # "sports"
        resp_bean.favorite[0].name
        # basketball
        ```

    - `validate`方法: `validate`接收一个`marshmallow.Schema`对象参数，并依据`Schema`模型进行校验。点击[marshmallow](https://github.com/marshmallow-code/marshmallow)了解更多信息。<br>
        关于`marshmallow`的使用我们将在下面详细阐述。
    - ~~`pair`方法（已废弃）~~: `pair`接收一个`ValidatorModel`参数，它是与`marshmallow.Schema`类似（事先未找到类似的轮子，所以重复造了一个）。引入`marshmallow`后不再维护。
---

### 断言

在EZ中，对于复杂场景的断言推荐大家使用序列化模型的方式。这种是一种更加pythonic的断言方式，它使得代码更加干净优雅，逻辑更加清晰简洁。EZ中提供 ~~`ValidatorModel`（已废弃）~~ 和`marshmallow.Schema`两种模型。

- EZ中断言的简单的使用：<br>
        <br>
    以上面的测试用例为例，`model.py`

```python
from api_test_ez.ez.serialize.fields import IntegerField, StringField, ListField
from api_test_ez.ez.serialize.models import ValidatorModel


class PhoneValidate(ValidatorModel):
    id = IntegerField(required=True)
    title = StringField(required=True)
    category = StringField(required=True, should_in=["smartphones", "laptops"])
    images = ListField(required=True, count_should_gte=1)
```

以上模型要求：
1. `id`: `required=True`表明`id`为返回结果必须字段，且它的数据类型必须是`integer`，如果不符合则会引发`ValidationError`错误；
2. `title`: 同样，`title`也是必须字段，且它的数据类型必须是`string`；
3. `category`: 除了满足以上两点，`should_be="smartphones"`表明该字段返回值必须是`"smartphones"`；
4. `images`: 这是一个列表，且它的成员个数必须大于1。
<br>
让我们接着[上面](#EZ和[ddt](https://github.com/datadriventests/ddt)一起工作)的例子，继续修改`test_whatever.py`
<br>
    
```python
import unittest

from api_test_ez.core.case import UnitCase
from tests.case.node.models import PhoneValidate


class SomeTest(UnitCase):

    def test_something(self):
        self.response.pair(PhoneValidate())


if __name__ == '__main__':
    unittest.main()
```

`pair`方法会对模型进行校验，并在产生错误时抛出`ValidationError`异常。<br>
<br>
**使用`marshmallow`翻译上述逻辑**<br>
<br>
`model.py`
    
```python
from marshmallow import Schema, fields, INCLUDE
from marshmallow import validate


class PhoneSchema(Schema):
    id = fields.Integer(required=True, strict=True)
    title = fields.String(required=True)
    category = fields.String(required=True, validate=validate.OneOf(["smartphones", "laptops"]))
    images = fields.List(fields.String(), required=True, validate=validate.Length(min=1))

    class Meta:
        unknown = INCLUDE
```
    
    >*关于`marshmallow`的更多使用方法和解释[请点击](https://github.com/marshmallow-code/marshmallow)。*

    在引入`marshmallow`后，`EzResponse`提供了新的验证方法`validate`。<br>
    <br>
    在`test_whatever.py`中验证。
    
```python
class SomeTest(UnitCase):

    def test_something(self):
        self.response.validate(PhoneValidate())
```
    
- 一个稍复杂的例子

    现在我们对`thumbnail`做校验，确保它返回的图片是我们发送请求的产品的图片。我们之前在`request.path`中储存了请求的产品信息如`/products/1`。<br>
    另外，我们对`category`重新添加校验，假如我们已知id小于等于5时是`smartphones`，大于5时是`laptops`。
    我们在模型`model.py`中添加这部分字段。
    <br>
    ```python
    # ValidatorModel
    class PhoneValidate(ValidatorModel):
        id = IntegerField(required=True)
        title = StringField(required=True)
        category = StringField(required=True)
        images = ListField(required=True, count_should_gte=1)
        thumbnail = StringField(required=True)

    # marshmallow
    class PhoneSchema(Schema):
        id = fields.Integer(required=True, strict=True)
        title = fields.String(required=True)
        category = fields.String(required=True)
        images = fields.List(fields.String(), required=True, validate=validate.Length(min=1))
        thumbnail = fields.String(required=True)

    class Meta:
        unknown = INCLUDE

    @validates("thumbnail")
    def validate_thumbnail(self, value):
        request = self.context.get("request")
        if request:
            if request.path not in value:
                raise ValidationError(f"The `thumbnail` should contain `{request.path!r}`.")
        else:
            raise ValidationError("Get `request` object fail.")

    @validates_schema
    def validate_category(self, data, **kwargs):
        if data['id'] <= 5:
            if data['category'] != "smartphones":
                raise ValidationError(f"Expect `smartphones`, but `{data['category']!r}` found.")
        else:
            if data['category'] != "laptops":
                raise ValidationError(f"Expect `smartphones`, but `{data['category']!r}` found.")
  ```
    由于涉及到了对外部变量的依赖，我们需要在断言前动态修改模型属性。<br>
    <br>
    `test_whatever.py`
    ```python
    # ValidatorModel
    class SomeTestVM(UnitCase):

        def test_something(self):
            pv = PhoneValidate()
            # thumbnail validate
            pv.thumbnail.should_cotain(self.request.path)
            # # category validate
            if self.response.bean.id <= 5:
                pv.category.should_be("smartphones")
            else:
                pv.category.should_be("laptops")
            self.response.pair(pv)
    
    # marshmallow
    class SomeTestMM(UnitCase):

        def test_something(self):
            ps = PhoneSchema()
            ps.context["request"] = self.request
            self.response.validate(ps)
    ```

---

### 测试报告

- HtmlReporter

```python
from api_test_ez.core.report import HtmlReporter, BRReporter


# HTMLTestRunner
report = HtmlReporter(case_path='<some_case_path>')
report.run()

# BeautifulReport
report = BRReporter(case_path='<some_case_path>', report_theme=)
report.run()
```
`HtmlReporter`接收3个参数:<br>
1. `case_path`: 用例脚本文件路径，如果**目录**将会遍历目录下的python文件以找到**所有**测试用例。<br>
2. `report_title`: 报告页面中的title，如果为*None*将会读取项目settings.py文件中的`REPORT_TITLE`字段。<br>
3. `report_desc`: 报告页面中的描述，如果为*None*将会读取项目settings.py文件中的`REPORT_DESC`字段。<br>

`BRReporter`除以上参数外，多出一个参数:<br>
1. `report_theme`: `BeautifulReport`报告主题，包含`theme_default`,`theme_cyan`,`theme_candy`,`theme_memories`。如果为*None*将会读取项目settings.py文件中的`BR_REPORT_THEME`字段。默认主题为`theme_default`。<br>

### Settings

| Key                | Desc                | Default                                                                           |
|--------------------|---------------------|-----------------------------------------------------------------------------------|
| CONSOLE_LOG_LEVEL  | 控制台日志等级             | INFO                                                                              |
| CONSOLE_LOG_FORMAT | 控制台日志格式             | %(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] [%(thread)d] - %(message)s  |
| FILE_LOG_LEVEL     | 日志文件等级              | DEBUG                                                                             |
| FILE_LOG_FORMAT    | 日志文件格式              | %(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] [%(thread)d] - %(message)s  |
| FILE_LOG_PATH      | 日志文件路径              | 默认为`None`，表示不输出日志文件。                                                              |
| REPORT_DIR         | 报告文件目录              | *report*，表示输出在当前运行目录./report下。                                                    |
| REPORT_FILE_NAME   | 报告文件名称              | 默认以当前时间格式命名， "%Y_%m_%d_%H_%M_%S.html"。                                            |
| REPORT_TITLE       | 报告名称                | ApiTestEz Report。                                                                 |
| REPORT_DESC        | 报告描述                | This is an api-test report generated by ApiTestEz.                                |
| BR_REPORT_THEME    | BeautifulReport报告主题 | theme_default                                                                     |


### ez.cfg

| Key            | Desc     | Default                                | Storage Location | Tag    |
|----------------|----------|----------------------------------------|------------------|--------|
| url            | 请求链接     | None                                   | request.http     | [HTTP] |
| host           | 请求host   | 当url为None时，url=host+path               | request.http     | [HTTP] |
| path           | 请求path   | 当url为None时，url=host+path               | request.http     | [HTTP] |
| method         | 请求方式     | GET                                    | request.http     | [HTTP] |
| body           | 请求body   | None                                   | request.http     | [HTTP] |
| body           | 请求body格式 | 默认为data，支持json，files，stream详见requests库 | request.http     | [HTTP] |
| *others*       | 其他任意配置项  | 如果存在将以key, value形式存储在request.meta中     | request.meta     | [META] |
| case_filepath  | 其他任意配置项  | 如果存在将以key, value形式存储在request.meta中     | __casefile__     | [CASE] |

`config`优先级：
- `default`: 0,
- `package`: 10,
- `module`: 20,
- `project`: 30,
- `case`: 40,
- `command`: 50,

>*`command`优先级最高。而对于`ez.cfg`配置文件，越靠近用例层优先级越高。*

### marshmallow之EzSchema

在`EzSchema`中，你可以动态修改字段的校验规则。

```python
from api_test_ez.ez.ez_marshmallow import EzSchema
from marshmallow import fields, validate


class PhoneSchema(EzSchema):
    id = fields.Integer(required=True, strict=True)
    title = fields.String(required=True)
    category = fields.String(required=True)
    images = fields.List(fields.String(), required=True, validate=validate.Length(min=1))


if __name__ == '__main__':
    ps = PhoneSchema()
    ps.title.validate = validate.OneOf(["smartphones", "laptops"])
```

### `ez`命令行
EZ目前仅支持`unittest`运行测试用例。它除了支持所有[`unittest`](https://docs.python.org/zh-cn/3/library/unittest.html#command-line-interface)命令行参数外，还支持以下设置内容：

**位置参数**：
- `action`: 指定`EZ`命令的行为，`run`或`dry-run`。<br>
  - `run`: 运行测试用例并生成报告。（当为设置report目录时，会以`dry-run`运行）
  - `dry-run`: 试运行测试用例。
- `cases_path`: 要运行的用例脚本路径。

**可选参数**
- `-h`, `--help`: 帮助文档
- `-version`, `--version`: 显示`ApiTestEz`版本号
- `-fk`, `--framework`: 如何运行测试。`unittest`或`pytest`(暂未支持)，默认`unittest`.
- `-cfg`, `--config`: 设置配置，优先级为`command`。例：*-cfg host=127.0.0.1*。
- `-cfgf`, `--config-file`: 设置配置文件，必须是`ez.cfg`格式的文件，优先级`command`。
- `-rs`, `--report-style`: 报告样式选择。`html`(即: HtmlReporter)或`br`(即: BRReporter)。默认`br`。
- `-rt`, `--report-theme`: BRReporter主题. 默认: `theme_default`。支持: `theme_default`, `theme_default`,`theme_default`, `theme_cyan`, `theme_candy`, `theme_memories`。
- `-rf`, `--report-file`: 报告文件路径。

>*例：ez run <path_or_dir_to_case_script_or> -cfg host=127.0.0.1 -rs html*

### TODO
1.  用例支持入参，例：f"{'X-Forwarded-For': ${province_ip} }"
2.  ~~url拆分host + path~~
3.  ~~报告~~
4.  ~~序列化断言实现~~
5.  ~~cmdline~~
6.  项目构建工具：ez create xxxx
7.  基于pytest的用例实现
8.  ~~pypi setup~~
9. 完善注释，文档
