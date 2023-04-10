## Canvas下载器演示

| ![](./showcase/showcase-1.jpg) | ![](./showcase/showcase-2.jpg) |
|--------------------------------|--------------------------------|

## 以下是面向用户文档

### 下载链接
1. [Window 下载链接](https://github.com/LeeTeng2001/SJTU-Canvas-Downloader/releases/download/v1.2/SJTU.Canvas.exe)
2. [Mac 下载链接](https://github.com/LeeTeng2001/SJTU-Canvas-Downloader/releases/download/v1.2/SJTU.Canvas.dmg)

### 教程
1. 首先去[Canvas设置](https://oc.sjtu.edu.cn/profile/settings)，滑倒下方，设置**允许外部软件的融入**，并创建访问许可证。访问许可证可以随意填写用途，过期日期可以留空。
2. 生成后，将Canvas令牌保存在一旁（非常重要）
3. 找到要下载的课程页面，抄下网址中的**课程号码**。如网址为：https://oc.sjtu.edu.cn/courses/93214 ，那么课程号码就是**93214**
4. 运行exe程序（应该需要权限），点击**设置**填写Canvas令牌。填写课程号码。
5. **同步模式** : 推荐使用On模式（只下载新的文件）。程序会先检查目标文件夹下有没有重名的文件（也会检查子文件夹）
6. **Canvas文件结构**: 是否按照Canvas上的文件夹结构进行下载。
7. 最后点击保存并运行即可
8. 注意，Canvas令牌只需要创建一次，以后下载其他课程只需要换课程号码参数即可。


## 以下是面向开发者文档

### How to build and run this project locally

```bash
# Create new virtual environment and install dependencies
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirement.txt
 
# Run 
$ python canvas_downloader.py
 
# Build executable and disk (mac)
$ pyinstaller -n "SJTU Canvas下载器" -w --icon=resources/canvas.icns canvas_downloader.py
$ mkdir -p dist/dmg
$ cp -r dist/SJTU\ Canvas下载器.app dist/dmg
$ create-dmg \
  --volname "SJTU Canvas下载器" \
  --volicon "resources/canvas.icns" \
  --window-pos 200 120 \
  --window-size 600 300 \
  --icon-size 100 \
  --icon "SJTU Canvas下载器.app" 175 120 \
  --hide-extension "SJTU Canvas下载器.app" \
  --app-drop-link 425 120 \
  "dist/SJTU Canvas下载器.dmg" \
  "dist/dmg/"
 
# Build executable (window)
$ pyinstaller -n "SJTU Canvas下载器" --onefile -w --icon=resources/canvas.ico canvas_downloader.py
```

### Change Log
- v1.0 
  - Initial build
- v1.1 
  - Added sync & ability to choose download structure
- v1.2 (Current release) 
  - Update to QT6
  - restructure project for maintainability
  - Add docs and code refactoring
  - Remove dependency for `configuration.json` file
  - Use pathlib for path manipulation instead of os
  - Unit testing
  - 更改应用语言为中文
- v1.3 (In Progress)
  - Automate build process
