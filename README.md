# PlanetMinecraftSkinSpider
一个用于从PlanetMinecraft爬取皮肤信息的项目，计划用于皮肤原创性检查，通过爬取PlanetMinecraft海量的皮肤图片计算指纹并存入数据库，给定单个皮肤图片，可计算dhash并在库中查询是否存在记录，若有则可能为非原创。

包含：
* Scrapy爬虫项目`pm_skin`：从PlanetMinecraft爬取信息（数据库文件`scrapy.db`）
  * 皮肤标题
  * 作者
  * 发布URL
  * 下载URL
  * 重定向URL（图片所在地址）
* 数据库`scrapy.db`：Scrapy爬取时生成的SQLite数据库，储存爬取的信息
  * title：皮肤发布的名称
  * author：作者
  * date：发布日期
  * raw_url：帖子链接
  * download_url：下载链接
  * redirect_url：重定向后的下载链接
  * dhash：图片的指纹（64位数）
* 图片指纹dhash批量更新脚本`img_hash_update.py`（与`scrapy.db`置于同一目录直接运行）
* 图片dhash查询脚本`skin_hash_search.py`：直接运行，选择文件计算dhash并在数据库查询
