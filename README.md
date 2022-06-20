# ApiTestEz

### 介绍
让API测试变得简单.


### 安装教程

    pip install ApiTestEz

### Quick Start

### 项目目录 
   1. 一个简单项目

          |-- EzTestDemo
              |-- <project_name>
              |   |-- test_whatever.py
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
   2. 一个完整项目

           |-- EzTestDemo
             |-- <project_name>
             |   |-- <test_api_dir>
             |   |   |-- testwhatever.py
             |   |   |-- ez.cfg (optional: package priority)
             |   |   |-- model.py (optional)
             |   |-- ez.cfg (optional: module priority)
             |-- settings
             |-- project.cfg
             |-- ez.cfg (optional: project priority)
             |-- <resource> (optional)
                 |-- <case_files> (optional)

        *project.cfg*为项目标识，它告诉EZ项目根目录和项目*settings.py*存放位置。<br>
        *setting.py*提供项目初始化设置项，如**log**、**report**配置。<br>
        *ez.cfg*与*settings*的区别在于，*ez.cfg*提供业务相关的配置，如**http**的*headers*、*case_filepath*（用例存放目录）、*auto_request*（自动完成请求）开关等，你还可以在里面放置业务需要的特殊变量，这些变量将会存放在*self.request.meta*中。它包含了多个层级**['case', 'package', 'module', 'project', 'command', 'default']**，优先级一次递减。<br>
        关于*setting.py*和*ez.cfg*支持的配置详情后述。<br>
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
                print(self.response.text)
                assert self.response.status_code == 200


        if __name__ == '__main__':
            unittest.main()
         ```
---
   3. EZ和[ddt](https://github.com/datadriventests/ddt)一起工作

      假设我们现在有3个域名需要访问
      
      
---
### TODO
1.  用例支持入参，例：f"{'X-Forwarded-For': ${province_ip} }"
2.  url拆分host + path
3.  ~~报告~~
4.  ~~ORM响应断言实现~~
5.  cmdline
6.  项目构建工具：ez create xxxx
7.  基于pytest的用例实现
8.  ~~pypi setup~~
9. 完善注释，文档