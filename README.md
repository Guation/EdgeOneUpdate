# EdgeOneUpdate

已合并到 [NAT1 Traversal](https://github.com/Guation/nat1_traversal)

## 使用方法
1. 在[EdgeOne](https://console.cloud.tencent.com/edgeone/zones)控制台点击新增站点，绑定您的域名，其值与`config.json`的`domain`字段相同。

2. 在域名服务->域名管理中->添加域名，加速域名与`config.json`的`sub_domain`字段相同，回源协议根据实际需求填写，源站IP随意填写。

3. 打开[腾讯云访问管理](https://console.cloud.tencent.com/cam)

4. 新建用户->快速创建->访问方式:编程访问,用户权限:QcloudTEOFullAccess->创建用户

5. 使用`SecretId`作为`id`，使用`SecretKey`作为`token`填入`config.json`

6. 运行`edgeone_update.pyz`

7. 在[NAT1 Traversal](https://github.com/Guation/nat1_traversal)的`config.json`中将`type`字段设置为`web`，`dns`字段设置为`webhook`，`id`字段设置为`http//:127.0.0.1:8080/`

8. 运行`nat1_traversal.tgz`

9. 由于`edgeone_update`与`nat1_traversal`均使用`config.json`作为默认配置文件，请勿将他们放到一个文件夹，如果一定要放到同一个文件夹请使用`-c`指定配置文件。

10. 先运行`edgeone_update`后运行`nat1_traversal`
