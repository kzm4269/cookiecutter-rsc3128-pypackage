Cookiecutter RSC3128 PyPackage
==============================

AIソリューションユニット向けにPythonパッケージを公開するとき用の
[cookiecutter](https://github.com/cookiecutter/cookiecutter) テンプレートです。

使用手順
--------

1. GitBucket: [空のリポジトリを作る。](http://172.31.23.128:9080/gitbucket/new)（例：`my_package`）
2. ローカルPC: Pythonパッケージを作成する。
```bash
$ pip3 install -U cookiecutter
$ cookiecutter 'http://172.31.23.128:9080/gitbucket/Ltakahara/cookiecutter-rsc3128-pypackage'
package_name [my_python_package]: my_package
...
```
3. ローカルPC: Pythonパッケージの中身を書く。（`src/my_package` にソースコードを配置する。）
4. ローカルPC: GitBucketにpushする。
```bash
$ cd ./my_package
$ git commit -m "Initial commit"
$ git tag -a 0.0.1 -m 'Release version 0.0.1'
$ git push origin master
```
